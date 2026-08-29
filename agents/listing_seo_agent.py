import json
import logging
from typing import Dict, Any, List
from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("ListingSEOAgent")

class ListingSEOAgent(BaseAgent):
    """Agent that writes high-converting SEO titles, descriptions, Etsy/Shopify tags, and styling guides."""

    def __init__(self):
        super().__init__(
            name="ListingSEOAgent",
            role_description="Lead E-Commerce Copywriter & Search Optimization Strategist"
        )

    def generate_listing_content(self, art_brief: Dict[str, Any], variants: List[Any]) -> Dict[str, Any]:
        """Generates comprehensive listing copy, SEO metadata, and product specifications."""
        hero_title = art_brief.get("collection_title", "Minimalist Fine Art Print")
        aesthetic = art_brief.get("aesthetic_name", "Modern Minimalist")
        palette = ", ".join(art_brief.get("color_palette", ["Neutral", "Terracotta"]))
        
        system_instruction = (
            "You are an expert luxury home decor copywriter and Etsy/Shopify SEO master. "
            "Write engaging, emotionally resonant product descriptions and high-search-volume keywords "
            "for a high-end framed art print."
        )

        prompt = (
            f"Write an e-commerce listing for a fine art print collection.\n"
            f"Title: {hero_title}\n"
            f"Aesthetic: {aesthetic}\n"
            f"Colors: {palette}\n"
            f"Target Rooms: {', '.join(art_brief.get('target_interior_rooms', ['Living Room']))}\n"
        )

        schema_example = {
            "seo_title": f"{hero_title} | Large Framed Wall Art, Minimalist Living Room Decor, Japandi Canvas Print",
            "short_summary": "Elevate your sanctuary with this museum-grade textured artwork, crafted with sustainable solid wood frames and archival pigment inks.",
            "story_and_concept": "Inspired by the organic harmony of natural pigments and wabi-sabi philosophy, this piece brings quiet luxury and grounded tranquility to your space.",
            "styling_tips": "Pairs effortlessly above a linen sofa, credenza, or as the grounding anchor in a modern bedroom gallery wall. Combine with warm ceramics and textured textiles.",
            "specifications": {
                "paper": "Museum-grade 200–250 gsm heavyweight archival matte paper",
                "framing": "Sustainably sourced FSC-certified solid natural oak and pine",
                "printing": "12-color Giclée pigment printing with 100+ year anti-fade warranty",
                "fulfillment": "Locally printed and hand-framed across 32 regional global hubs for 48–72h fast delivery"
            },
            "seo_tags": [
                "large framed wall art", "minimalist canvas print", "japandi living room decor",
                "neutral abstract art", "horizontal wall art", "bedroom wall decor", "gallery wall set",
                "aesthetic room decor", "wabi sabi poster", "modern home decor", "sustainable art print"
            ],
            "social_ad_caption": "Bring gallery-grade serenity into your living room. Handcrafted with sustainably sourced oak frames and museum-grade archival paper. ✨ 72h local worldwide shipping."
        }

        result = self.generate_json(prompt, system_instruction, schema_example)
        if result and "seo_title" in result:
            logger.info(f"[{self.name}] Generated SEO Listing via Gemini: '{result.get('seo_title')[:50]}...'")
            return result

        # High quality fallback copy
        logger.info(f"[{self.name}] Generated SEO Listing via High-Converting Template.")
        return {
            "seo_title": f"{hero_title} | Framed Wall Art, {aesthetic} Canvas Print, Living Room Decor",
            "short_summary": f"Transform your living space with {hero_title}. Printed on museum-grade heavyweight matte paper and encased in premium solid wood frames.",
            "story_and_concept": f"Created to reflect the calming balance of {aesthetic}, combining {palette} tones to anchor modern interiors with refined elegance.",
            "styling_tips": "Ideal as a statement hero piece above a sofa or headboard. Harmonizes beautifully with neutral boucle fabrics, natural wood accents, and warm ambient lighting.",
            "specifications": {
                "paper": "Museum-grade 200–250 gsm heavyweight archival matte paper",
                "framing": "Sustainably sourced FSC-certified solid natural oak and pine",
                "printing": "12-color Giclée pigment printing with 100+ year anti-fade warranty",
                "fulfillment": "Locally printed and hand-framed across 32 regional global hubs for 48–72h fast delivery"
            },
            "seo_tags": [
                f"{aesthetic.lower()} wall art", "framed canvas print", "modern living room art",
                "large statement art", "neutral home decor", "gallery wall art", "bedroom wall decor",
                "minimalist poster", "terracotta art print", "fine art giclee", "sustainable wall art"
            ],
            "social_ad_caption": f"Elevate your sanctuary with '{hero_title}'. Museum-grade archival paper and handcrafted solid oak frames. 🚚 Fast 72-hour domestic shipping."
        }
