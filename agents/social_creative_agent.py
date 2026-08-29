import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("SocialCreativeAgent")

class SocialCreativeAgent(BaseAgent):
    """
    Agent that automatically generates high-converting Pinterest Pins,
    TikTok/Instagram Reel scripts, audio hooks, and hashtag bundles for organic traffic.
    """

    def __init__(self):
        super().__init__(
            name="SocialCreativeAgent",
            role_description="Lead Social Growth & Viral Ad Creative Director"
        )

    def generate_social_package(
        self,
        product_id: str,
        art_brief: Dict[str, Any],
        mockup_path: str,
        output_dir: Path
    ) -> Dict[str, Any]:
        """Generates ready-to-post Pinterest Pin graphics and TikTok/Reels marketing scripts."""
        marketing_dir = output_dir / "social_marketing"
        marketing_dir.mkdir(parents=True, exist_ok=True)

        title = art_brief.get("collection_title", "Gallery Wall Art")
        aesthetic = art_brief.get("aesthetic_name", "Modern Minimalist")

        # 1. Create Vertical Pinterest Pin Image (1000x1500 px, 2:3 ratio)
        pin_image_path = marketing_dir / "pinterest_pin_1000x1500.jpg"
        self._render_pinterest_pin(mockup_path, title, aesthetic, pin_image_path)

        # 2. Generate Viral TikTok/Reels Scripts and Pinterest SEO Copy
        system_instruction = (
            "You are a viral social media director specializing in luxury home decor, interior styling, and Pinterest/TikTok ads. "
            "Write high-converting, aesthetic marketing scripts and SEO tags."
        )

        prompt = (
            f"Generate a social media marketing launch package for:\n"
            f"Piece: '{title}'\n"
            f"Aesthetic: '{aesthetic}'\n"
            f"Key selling points: Solid Natural Oak frame, 250 gsm archival matte paper, 72h local printing in 32 countries.\n"
        )

        schema_example = {
            "pinterest_pin": {
                "title": f"How to Style a {aesthetic} Living Room | Atelier & Canvas",
                "description": f"Anchor your living space with this museum-grade {aesthetic} statement framed art. Handcrafted in solid natural oak with archival pigment printing. ✨ 72h local worldwide delivery. Shop the gallery now.",
                "destination_link": f"{settings.store_url}/product/{product_id}",
                "search_keywords": ["living room wall art", "aesthetic home decor", "japandi interior", "framed canvas ideas", "large wall decor"]
            },
            "tiktok_reels_scripts": [
                {
                    "concept": "POV: Aesthetic Room Transformation",
                    "hook": "POV: You replaced generic IKEA posters with a museum-grade solid oak canvas.",
                    "visual_flow": "Start with empty wall → quick cut to unboxing textured oak frame → final reveal above linen sofa in golden hour sunlight.",
                    "on_screen_text": "The single easiest way to make your apartment look like a $5,000/night Airbnb ✨",
                    "suggested_audio": "Lofi Chill / Acoustic Warm Ambient"
                },
                {
                    "concept": "Interior Designer Styling Secret",
                    "hook": "The #1 mistake people make when buying living room art? Buying too small.",
                    "visual_flow": "Show difference between a tiny 8x10 print vs a bold 24x36 statement hero piece.",
                    "on_screen_text": "Go big or go home: 24x36 is the magic designer ratio.",
                    "suggested_audio": "Trending Aesthetic Voiceover"
                }
            ],
            "hashtag_bundle": [
                "#homedecor", "#wallart", "#interiordesign", "#gallerywall",
                "#japandi", "#apartmentdecor", "#aestheticlivingroom", "#neutralhome"
            ]
        }

        social_copy = self.generate_json(prompt, system_instruction, schema_example)
        if not social_copy or "pinterest_pin" not in social_copy:
            # Fallback
            social_copy = {
                "pinterest_pin": {
                    "title": f"The Art of {aesthetic} | Handcrafted Statement Wall Art",
                    "description": f"Elevate your home with '{title}'. Printed on museum-grade archival paper and framed in solid oak. 🚚 72h fast delivery.",
                    "destination_link": f"{settings.store_url}/product/{product_id}",
                    "search_keywords": ["wall art aesthetic", "framed prints", "living room ideas"]
                },
                "tiktok_reels_scripts": [
                    {
                        "concept": "Aesthetic Living Room Reveal",
                        "hook": f"The secret to a peaceful living room is anchoring it with {aesthetic} statement art.",
                        "visual_flow": "Close-up of oak grain frame texture → pan out to whole room.",
                        "on_screen_text": f"Found the perfect {aesthetic} statement piece ✨",
                        "suggested_audio": "Warm Acoustic Ambient"
                    }
                ],
                "hashtag_bundle": ["#homedecor", "#wallart", "#interiordesign", "#aesthetic"]
            }

        # Save marketing brief JSON
        social_copy["pin_image_path"] = str(pin_image_path)
        with open(marketing_dir / "social_marketing_brief.json", "w", encoding="utf-8") as f:
            json.dump(social_copy, f, indent=2)

        logger.info(f"[{self.name}] Generated Pinterest Pin & TikTok scripts in {marketing_dir}")
        return social_copy

    def _render_pinterest_pin(self, mockup_path: str, title: str, aesthetic: str, out_path: Path):
        """Composites an eye-catching 1000x1500 px vertical Pinterest Pin image."""
        pin_w, pin_h = 1000, 1500
        pin = Image.new("RGB", (pin_w, pin_h), (245, 240, 232))

        try:
            # Load mockup and place in center-top
            mockup = Image.open(mockup_path).convert("RGB")
            # Crop/fit into 1000x1050 viewport
            mock_w, mock_h = mockup.size
            scale = max(pin_w / mock_w, 1050 / mock_h)
            new_w, new_h = int(mock_w * scale), int(mock_h * scale)
            resized_mockup = mockup.resize((new_w, new_h), Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else getattr(Image, "LANCZOS", 1))
            
            # Crop to exactly 1000x1050
            crop_x = (new_w - pin_w) // 2
            crop_y = (new_h - 1050) // 2
            cropped = resized_mockup.crop((crop_x, crop_y, crop_x + pin_w, crop_y + 1050))
            pin.paste(cropped, (0, 0))
        except Exception as e:
            logger.warning(f"Could not load mockup for pin: {e}")

        draw = ImageDraw.Draw(pin)

        # Brand header badge on mockup
        draw.rectangle([0, 0, pin_w, 60], fill=(28, 28, 30))
        draw.text((pin_w // 2 - 130, 20), "ATELIER & CANVAS - 2026 CURATION", fill=(250, 248, 245))

        # Bottom Graphic Banner (1050 to 1500)
        draw.rectangle([0, 1050, pin_w, pin_h], fill=(250, 248, 245))
        draw.line([(0, 1050), (pin_w, 1050)], fill=(232, 227, 218), width=3)

        # Aesthetic Label
        draw.rectangle([pin_w // 2 - 140, 1080, pin_w // 2 + 140, 1115], fill=(232, 220, 205), outline=(198, 107, 77), width=1)
        draw.text((pin_w // 2 - 115, 1090), aesthetic.upper()[:28], fill=(112, 88, 68))

        # Title / Hook
        draw.text((pin_w // 2 - 240, 1140), "THE ART OF SERENE LIVING", fill=(28, 28, 30))
        draw.text((pin_w // 2 - 280, 1180), "Museum Archival Paper & Solid Oak", fill=(104, 99, 91))
        draw.text((pin_w // 2 - 190, 1220), "* 72-Hour Local Delivery in 32 Countries", fill=(59, 122, 87))

        # Big CTA Button
        btn_top = 1280
        draw.rectangle([pin_w // 2 - 220, btn_top, pin_w // 2 + 220, btn_top + 70], fill=(28, 28, 30))
        draw.text((pin_w // 2 - 120, btn_top + 22), "SHOP STATEMENT ART ->", fill=(255, 255, 255))

        # Footer Guarantee
        draw.text((pin_w // 2 - 160, 1420), "100% Satisfaction & 100-Year Fade Guarantee", fill=(150, 145, 138))

        pin.save(out_path, "JPEG", quality=94)

