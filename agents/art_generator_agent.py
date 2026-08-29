import os
import io
import math
import random
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFilter
from config.settings import settings
from agents.base_agent import BaseAgent

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger("ArtGeneratorAgent")

class ArtGeneratorAgent(BaseAgent):
    """Agent that creates high-resolution print-ready artwork matching the art brief."""

    def __init__(self):
        super().__init__(
            name="ArtGeneratorAgent",
            role_description="Fine Art Print Director & Generative Illustrator"
        )

    def generate_artwork(self, art_brief: Dict[str, Any], output_path: Path) -> Path:
        """Generates the master high-resolution artwork."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        prompt = art_brief.get("hero_art_prompt", "Fine art abstract painting")
        
        # 1. Attempt generation via Gemini / Imagen API if available
        if self.client and GENAI_AVAILABLE:
            try:
                logger.info(f"[{self.name}] Calling Gemini/Imagen Image Generation API...")
                result = self.client.models.generate_images(
                    model="imagen-3.0-generate-002",
                    prompt=prompt,
                    config=dict(
                        number_of_images=1,
                        aspect_ratio="3:4",
                        output_mime_type="image/jpeg",
                        person_generation="ALLOW_ADULT"
                    )
                )
                for generated_image in result.generated_images:
                    image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                    image.save(output_path, "JPEG", quality=95)
                    logger.info(f"[{self.name}] Saved master artwork via API: {output_path}")
                    return output_path
            except Exception as e:
                logger.warning(f"[{self.name}] Imagen API call failed or not enabled: {e}. Generating procedural fine art master.")

        # 2. Procedural High-Res Fine Art Master Generator (Fallback / Offline)
        image = self._render_procedural_fine_art(art_brief)
        image.save(output_path, "JPEG", quality=95)
        logger.info(f"[{self.name}] Rendered procedural high-res fine art: {output_path}")
        return output_path

    def _render_procedural_fine_art(self, art_brief: Dict[str, Any], width: int = 2400, height: int = 3200) -> Image.Image:
        """Renders an elegant, textured minimalist fine art canvas (3:4 ratio)."""
        palette_hex = self._get_palette_rgb(art_brief.get("color_palette", []))
        
        # Background: Rich warm textured plaster / linen
        bg_color = palette_hex[0] if len(palette_hex) > 0 else (242, 237, 228)
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw subtle linen / paper grain texture
        grain = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        grain_draw = ImageDraw.Draw(grain)
        for _ in range(8000):
            gx = random.randint(0, width)
            gy = random.randint(0, height)
            alpha = random.randint(5, 20)
            tone = random.choice([255, 0])
            grain_draw.point((gx, gy), fill=(tone, tone, tone, alpha))
        
        # Draw aesthetic geometric & organic abstract composition
        cx, cy = width // 2, height // 2

        # 1. Large Textured Organic Arch / Semicircle
        accent_1 = palette_hex[1] if len(palette_hex) > 1 else (198, 107, 77)
        arch_w, arch_h = int(width * 0.65), int(height * 0.55)
        arch_top = cy - int(height * 0.22)
        arch_left = cx - arch_w // 2
        draw.pieslice(
            [arch_left, arch_top, arch_left + arch_w, arch_top + arch_h],
            start=180, end=360,
            fill=accent_1
        )
        draw.rectangle(
            [arch_left, arch_top + arch_h // 2, arch_left + arch_w, arch_top + arch_h],
            fill=accent_1
        )

        # 2. Balanced Minimalist Sphere / Celestial Orb
        accent_2 = palette_hex[2] if len(palette_hex) > 2 else (62, 70, 78)
        orb_radius = int(width * 0.18)
        orb_cx = cx + int(width * 0.15)
        orb_cy = cy - int(height * 0.18)
        draw.ellipse(
            [orb_cx - orb_radius, orb_cy - orb_radius, orb_cx + orb_radius, orb_cy + orb_radius],
            fill=accent_2
        )

        # 3. Soft Zen Horizontal Grounding Bar
        accent_3 = palette_hex[3] if len(palette_hex) > 3 else (142, 154, 137)
        bar_w = int(width * 0.75)
        bar_h = int(height * 0.08)
        bar_left = cx - bar_w // 2
        bar_top = cy + int(height * 0.20)
        if hasattr(draw, "rounded_rectangle"):
            draw.rounded_rectangle(
                [bar_left, bar_top, bar_left + bar_w, bar_top + bar_h],
                radius=12,
                fill=accent_3
            )
        else:
            draw.rectangle(
                [bar_left, bar_top, bar_left + bar_w, bar_top + bar_h],
                fill=accent_3
            )


        # 4. Delicate Zen Brushstroke Line
        accent_4 = palette_hex[4] if len(palette_hex) > 4 else (45, 45, 45)
        line_top = int(height * 0.12)
        line_bottom = int(height * 0.88)
        draw.line(
            [(cx - int(width * 0.28), line_top), (cx - int(width * 0.28), line_bottom)],
            fill=accent_4,
            width=6
        )

        # Blend grain & soften edges
        img.paste(grain, (0, 0), grain)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        return img

    def _get_palette_rgb(self, palette_names: list) -> list:
        """Converts color names to harmonious RGB triplets."""
        color_map = {
            "Terracotta": (204, 114, 82),
            "Warm Ochre": (217, 163, 85),
            "Charcoal Slate": (54, 60, 68),
            "Muted Sage": (148, 161, 144),
            "Raw Linen": (244, 240, 232),
            "Sandstone": (230, 221, 207),
            "Deep Cobalt": (28, 62, 118),
            "Burnt Vermilion": (212, 63, 44),
            "Mustard Yellow": (224, 172, 42),
            "Matte Black": (32, 32, 34),
            "Warm Parchment": (246, 241, 230),
            "Forest Moss": (58, 80, 61),
            "Eucalyptus Green": (118, 142, 126),
            "Antique Sepia": (112, 84, 62),
            "Old Ivory": (247, 243, 233),
            "Dried Rose": (184, 125, 128),
            "Amalfi Ultramarine": (36, 75, 138),
            "Terracotta Clay": (195, 102, 73),
            "Sunlit Limewash": (248, 244, 234),
            "Deep Obsidian": (24, 25, 29),
            "Burnished Gold": (198, 153, 62),
            "Burgundy Wine": (108, 38, 48),
            "Espresso Umber": (60, 44, 37)
        }
        rgb_list = []
        for name in palette_names:
            if name in color_map:
                rgb_list.append(color_map[name])
        
        # Ensure at least 5 colors
        if len(rgb_list) < 5:
            rgb_list.extend([(244, 240, 232), (204, 114, 82), (54, 60, 68), (148, 161, 144), (45, 45, 45)])
        return rgb_list
