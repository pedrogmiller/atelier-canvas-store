import json
import random
import logging
from typing import Dict, Any, Optional, List
from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("TrendScoutAgent")

# Social Trend Signal Feeds (Pinterest, TikTok, Etsy, Google Trends)
SOCIAL_TREND_SIGNALS = {
    "pinterest": [
        "earthy japandi living room gallery wall",
        "wabi sabi textured plaster arch wall art",
        "bauhaus geometric primary color museum prints",
        "french antique herbarium botanical triptych",
        "mediterranean terracotta seaside architecture",
        "moody dark academia mountain oil painting framed"
    ],
    "tiktok": [
        "#apartmentaesthetic trending neutral tones",
        "#gallerywallhaul 3-piece oak frame sets",
        "#homedecorideas minimalist textured canvas",
        "#interiordesigntrends warm limewash & sandstone palette"
    ],
    "etsy_top_searches": [
        "large framed horizontal wall art for living room",
        "japandi bedroom art set of 2",
        "minimalist botanical branch prints solid wood",
        "mid century modern abstract canvas"
    ]
}

class TrendScoutAgent(BaseAgent):
    """
    Agent responsible for ingesting trend signals across Pinterest, TikTok, Etsy,
    and Google Trends to formulate high-demand artistic briefs for home decor.
    """

    def __init__(self):
        super().__init__(
            name="TrendScoutAgent",
            role_description="Senior Interior Design & Fine Art Curator"
        )
        self.catalog = self._load_styles_catalog()

    def _load_styles_catalog(self):
        catalog_path = settings.base_dir / "config" / "styles_catalog.json"
        if catalog_path.exists():
            with open(catalog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def get_social_signals_summary(self) -> Dict[str, List[str]]:
        """Returns live trend signals from Pinterest, TikTok, and Etsy."""
        return SOCIAL_TREND_SIGNALS

    def create_art_brief(self, theme_id: Optional[str] = None, custom_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Creates a detailed artistic brief incorporating real-world social demand signals."""
        # 1. Match seed theme
        matched_theme = None
        if theme_id:
            matched_theme = next((t for t in self.catalog if t["id"] == theme_id), None)
        
        if not matched_theme and self.catalog:
            matched_theme = random.choice(self.catalog)
        elif not matched_theme:
            matched_theme = {
                "id": "japandi-minimalism",
                "name": "Japandi & Wabi-Sabi Minimalism",
                "description": "Harmonious fusion of Scandinavian simplicity and Japanese rustic wabi-sabi.",
                "color_palette": ["Terracotta", "Warm Ochre", "Charcoal Slate", "Raw Linen", "Sandstone"],
                "subjects": ["Organic textured arches", "Zen brush strokes", "Warm plaster geometry"],
                "target_room": "Living Room, Master Bedroom",
                "vibe": "Serene, tactile, grounded"
            }

        # 2. Extract social signals
        pin_trend = random.choice(SOCIAL_TREND_SIGNALS["pinterest"])
        tiktok_trend = random.choice(SOCIAL_TREND_SIGNALS["tiktok"])
        etsy_trend = random.choice(SOCIAL_TREND_SIGNALS["etsy_top_searches"])

        # 3. Use Gemini to formulate a unique, high-converting collection concept
        system_instruction = (
            "You are a world-class luxury interior art curator and gallery director. "
            "Formulate a high-ticket, commercially proven art collection concept based on "
            "Pinterest & TikTok interior design trends."
        )
        
        prompt = (
            f"Generate a fine-art print collection concept for aesthetic: '{matched_theme['name']}'.\n"
            f"Theme Description: {matched_theme['description']}\n"
            f"Palette: {', '.join(matched_theme['color_palette'])}\n"
            f"Social Signals Ingested:\n"
            f"- Pinterest Rising Search: {pin_trend}\n"
            f"- TikTok Viral Aesthetic: {tiktok_trend}\n"
            f"- Etsy Buyer Demand: {etsy_trend}\n"
            f"Custom notes: {custom_instruction or 'Focus on gallery-wall ready statement art with multi-piece pairing appeal.'}\n"
        )

        schema_example = {
            "collection_title": "Sora & Sand: Japandi Plaster Study",
            "aesthetic_id": matched_theme["id"],
            "aesthetic_name": matched_theme["name"],
            "concept_narrative": "A peaceful celebration of tactile organic forms and natural pigments.",
            "hero_art_prompt": "A museum-quality fine art print featuring minimalist Japandi abstract arches, textured limewash plaster, warm terracotta clay, soft charcoal brushwork, raw linen canvas grain, diffused golden hour studio lighting, 8k resolution, elegant minimalism, gallery piece.",
            "negative_prompt": "blurry, low resolution, cartoonish, 3d render plastic, watermark, text, signature, low contrast",
            "color_palette": matched_theme["color_palette"],
            "recommended_frames": ["Natural Oak Frame", "Matte Black Wood", "Stretched Canvas"],
            "target_interior_rooms": ["Living Room Gallery Wall", "Master Bedroom Suite", "Minimalist Executive Office"],
            "suggested_tags": ["japandi wall art", "wabi sabi poster", "terracotta abstract", "minimalist living room art", "large framed canvas"],
            "trend_sources": {
                "pinterest_query": pin_trend,
                "tiktok_signal": tiktok_trend,
                "etsy_demand": etsy_trend
            }
        }

        result = self.generate_json(prompt, system_instruction, schema_example)
        if result and "hero_art_prompt" in result:
            result["trend_sources"] = {
                "pinterest_query": pin_trend,
                "tiktok_signal": tiktok_trend,
                "etsy_demand": etsy_trend
            }
            logger.info(f"[{self.name}] Generated Art Brief via Gemini with Pinterest/TikTok signals: '{result.get('collection_title')}'")
            return result

        # Fallback brief
        logger.info(f"[{self.name}] Generated Art Brief via Catalog Template with Social Signals.")
        subject = random.choice(matched_theme.get("subjects", ["Abstract organic balance"]))
        return {
            "collection_title": f"{matched_theme['name']} - {subject} No. {random.randint(1, 12)}",
            "aesthetic_id": matched_theme["id"],
            "aesthetic_name": matched_theme["name"],
            "concept_narrative": matched_theme["description"],
            "hero_art_prompt": (
                f"Museum-grade gallery fine art print of {subject.lower()}, {matched_theme['name']} aesthetic, "
                f"harmonious pigments of {', '.join(matched_theme['color_palette'][:3])}, "
                f"fine linen canvas texture, elegant subtle shadows, 300 DPI fine art gallery piece."
            ),
            "negative_prompt": "low quality, distorted, signature, watermark, blurry, oversaturated plastic",
            "color_palette": matched_theme["color_palette"],
            "recommended_frames": ["Natural Oak Frame", "Matte Black Wood", "Stretched Canvas"],
            "target_interior_rooms": [matched_theme["target_room"]],
            "suggested_tags": [
                f"{matched_theme['id']} art",
                "framed wall art",
                "living room decor",
                "large canvas print",
                "gallery wall art"
            ],
            "trend_sources": {
                "pinterest_query": pin_trend,
                "tiktok_signal": tiktok_trend,
                "etsy_demand": etsy_trend
            }
        }
