import json
import logging
from typing import Optional, Any, Dict
from config.settings import settings

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger("BaseAgent")

class BaseAgent:
    """Base class for all specialized AI agents."""
    
    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description
        self.api_key = settings.gemini_api_key
        self.client = None
        
        if GENAI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"[{self.name}] Initialized with Gemini API.")
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to initialize Gemini Client: {e}")
        else:
            logger.info(f"[{self.name}] Operating in Local Fallback mode (No GEMINI_API_KEY).")

    def generate_json(self, prompt: str, system_instruction: str, schema_example: Dict[str, Any]) -> Dict[str, Any]:
        """Calls Gemini with JSON mode or returns structured heuristic fallback."""
        if self.client:
            try:
                full_prompt = (
                    f"{prompt}\n\n"
                    f"You MUST return ONLY valid JSON matching this schema:\n"
                    f"{json.dumps(schema_example, indent=2)}\n"
                    f"Do not include markdown codeblocks or extra text."
                )
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        response_mime_type="application/json"
                    )
                )
                # Clean and parse JSON
                cleaned_text = response.text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                return json.loads(cleaned_text.strip())
            except Exception as e:
                logger.warning(f"[{self.name}] Gemini JSON generation failed: {e}. Falling back.")
        
        return {}
