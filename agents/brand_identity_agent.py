import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageFont

from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("BrandIdentityAgent")

class BrandConcept(BaseModel):
    name: str = Field(description="The core brand name")
    tagline: str = Field(description="Clean luxury positioning tagline")
    domains: List[str] = Field(description="Target .com domain name options")
    brand_story: str = Field(description="1-paragraph narrative positioning the brand")
    simplicity_credibility_rationale: str = Field(description="Why this name commands buyer trust and high perceived luxury value")
    aesthetic_focus: str = Field(description="Interior aesthetics this name naturally resonates with")
    recommended_social_handles: Dict[str, str] = Field(description="Handles for Gmail, Pinterest, TikTok, IG")
    palette: List[str] = Field(description="Signature color palette hex codes")

class BrandIdentityAgent(BaseAgent):
    """Specialized agent in charge of luxury brand naming, logo creation, domain strategy, and visual identity."""

    def __init__(self):
        super().__init__(
            name="BrandIdentityAgent",
            role_description="Brand Director & Luxury Visual Identity Designer"
        )
        self.brand_dir = settings.base_dir / "brand_identity"
        self.brand_dir.mkdir(parents=True, exist_ok=True)


    def propose_brand_names(self) -> List[BrandConcept]:
        """Proposes 5 carefully curated, simple, high-credibility fine art brand concepts with strong .com domain availability."""
        return [
            BrandConcept(
                name="Atelier & Canvas",
                tagline="Curated Fine Art & Archival Frames",
                domains=["atelierandcanvas.com", "ateliercanvasstudio.com", "ateliercanvasart.com"],
                brand_story="Rooted in European gallery heritage, Atelier & Canvas pairs museum-grade paper with sustainably crafted solid oak frames. It conveys craftsmanship, bespoke artistry, and intentional home curation.",
                simplicity_credibility_rationale="The word 'Atelier' immediately anchors the brand in high-end European artisanal workshops, while 'Canvas' clarifies the core product instantly. Simple, authoritative, and timeless.",
                aesthetic_focus="Japandi, French Heritage, Minimalist Plaster, Bauhaus",
                recommended_social_handles={
                    "gmail": "ateliercanvas.art@gmail.com",
                    "pinterest": "@atelierandcanvas",
                    "tiktok": "@ateliercanvas",
                    "instagram": "@ateliercanvas.art"
                },
                palette=["#1C1C1E", "#FAF8F5", "#C66B4D", "#E8E3DA", "#3B7A57"]
            ),
            BrandConcept(
                name="Lumen & Oak",
                tagline="Light, Form & Solid Wood Frames",
                domains=["lumenoakstudio.com", "lumenoakart.com", "lumenandoak.com"],
                brand_story="Named for the interplay of natural light ('Lumen') and handcrafted solid oak framing ('Oak'). Designed for modern homeowners seeking architectural balance, calm aesthetics, and organic luxury.",
                simplicity_credibility_rationale="Two punchy, sensory words. 'Lumen' speaks to the visual clarity of fine art printing; 'Oak' guarantees solid, premium physical craftsmanship before the customer even clicks.",
                aesthetic_focus="Scandinavian Modern, Japandi, Architectural Schematics, Desert Modernism",
                recommended_social_handles={
                    "gmail": "lumenoak.art@gmail.com",
                    "pinterest": "@lumenoakstudio",
                    "tiktok": "@lumenoak",
                    "instagram": "@lumenoak.art"
                },
                palette=["#24211D", "#F4F1EA", "#C49A6C", "#7A8274", "#D8D0C5"]
            ),
            BrandConcept(
                name="Calm & Frame",
                tagline="Statement Art for Peaceful Living",
                domains=["calmandframe.com", "calmframed.com", "calmframestudio.com"],
                brand_story="Built on the psychology of sanctuary-first home design. Calm & Frame creates tranquil, gallery-quality art designed to reduce visual noise and bring quiet sophistication to living spaces.",
                simplicity_credibility_rationale="Extreme clarity. Modern buyers crave calm in their homes, and 'Frame' tells them exactly what they receive—ready-to-hang, framed statement pieces.",
                aesthetic_focus="Neutral Textured Plaster, Wabi-Sabi, Zen Sumi-e, Ethereal Horizons",
                recommended_social_handles={
                    "gmail": "calmframe.art@gmail.com",
                    "pinterest": "@calmandframe",
                    "tiktok": "@calmframe",
                    "instagram": "@calm.and.frame"
                },
                palette=["#2B2D2F", "#F7F5F0", "#D0A98B", "#8C9B90", "#E3DFD7"]
            ),
            BrandConcept(
                name="Maison & Frame",
                tagline="French Modern Fine Art & Framing",
                domains=["maisonandframe.com", "maisonframestudio.com", "maisoncadreart.com"],
                brand_story="Inspired by Parisian residential architecture and Côte d'Azur villas. Maison & Frame brings gallery-level curation into everyday homes with solid wood craftsmanship and archival inks.",
                simplicity_credibility_rationale="'Maison' (House/Home) carries immense perceived luxury value worldwide. Combined with 'Frame', it creates the impression of an established, century-old design house.",
                aesthetic_focus="French Riviera, Antique Botanical, Dark Academia, Art Deco Gilt",
                recommended_social_handles={
                    "gmail": "maisonframe.art@gmail.com",
                    "pinterest": "@maisonandframe",
                    "tiktok": "@maisonframe",
                    "instagram": "@maison.and.frame"
                },
                palette=["#1E1B18", "#F9F6F0", "#9E6B55", "#4A5D4E", "#D5CEBF"]
            ),
            BrandConcept(
                name="Terra & Frame",
                tagline="Earth-Toned Art & Natural Wood",
                domains=["terraandframe.com", "terraframed.com", "terraframestudio.com"],
                brand_story="Celebrates the raw pigment of the earth—terracotta, sandstone, olive, and ochre. Sourced locally across 32 countries with FSC-certified natural oak wood frames.",
                simplicity_credibility_rationale="'Terra' connects directly to the #1 home decor trend of 2024–2026: warm terracotta, clay, and Mediterranean limewash. It feels organic, premium, and sustainable.",
                aesthetic_focus="Mediterranean Terracotta, Desert Modernism, Pressed Botanicals, Amalfi Coast",
                recommended_social_handles={
                    "gmail": "terraframe.art@gmail.com",
                    "pinterest": "@terraandframe",
                    "tiktok": "@terraframe",
                    "instagram": "@terra.and.frame"
                },
                palette=["#231F20", "#FAF6EE", "#BD6B4D", "#6F7D67", "#E4DCD0"]
            )
        ]

    def generate_complete_brand_suite(self, brand: BrandConcept) -> Dict[str, Path]:
        """Generates high-res SVG & PNG logos, social headers, and email templates for the chosen brand."""
        logger.info(f"Generating full brand creative suite for: {brand.name}")
        out_paths = {}

        # 1. Vector SVG Logos & Botanical Hand-Drawn Emblem
        svg_logo_path = self.brand_dir / "logo_primary_wordmark.svg"
        svg_seal_path = self.brand_dir / "logo_monogram_seal.svg"
        svg_emblem_path = self.brand_dir / "logo_emblem.svg"
        
        # Check if master hand-drawn emblem exists
        emblem_png_path = self.brand_dir / "logo_emblem.png"
        emblem_b64 = ""
        if emblem_png_path.exists():
            import base64
            with open(emblem_png_path, "rb") as f:
                emblem_b64 = base64.b64encode(f.read()).decode("utf-8")

        if emblem_b64:
            svg_wordmark_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 140" width="100%" height="100%">
  <style>
    .brand-title {{ font-family: 'Cormorant Garamond', 'Georgia', serif; font-size: 40px; font-weight: 700; letter-spacing: 0.16em; fill: #1C1C1E; }}
    .brand-sub {{ font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; font-size: 11px; font-weight: 600; letter-spacing: 0.26em; fill: #B8834E; }}
    .brand-line {{ stroke: #E8E3DA; stroke-width: 1.5; }}
  </style>
  <g transform="translate(10, 5)">
    <image href="data:image/png;base64,{emblem_b64}" x="0" y="0" width="130" height="130" />
  </g>
  <text x="165" y="62" class="brand-title">{brand.name.upper()}</text>
  <line x1="165" y1="84" x2="680" y2="84" class="brand-line" />
  <text x="165" y="106" class="brand-sub">{brand.tagline.upper()}</text>
</svg>"""
            svg_seal_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
  <style>
    .seal-text-top {{ font-family: 'Cormorant Garamond', serif; font-size: 14.5px; font-weight: 700; letter-spacing: 0.24em; fill: #1C1C1E; text-transform: uppercase; }}
    .seal-text-bot {{ font-family: 'Plus Jakarta Sans', sans-serif; font-size: 9.5px; font-weight: 600; letter-spacing: 0.26em; fill: #B8834E; text-transform: uppercase; }}
  </style>
  <defs>
    <path id="circlePathTop" d="M 60,200 A 140,140 0 0,1 340,200" fill="none" />
    <path id="circlePathBottom" d="M 340,200 A 140,140 0 0,1 60,200" fill="none" />
  </defs>
  <circle cx="200" cy="200" r="186" fill="#FAF8F5" stroke="#1C1C1E" stroke-width="2.5" />
  <circle cx="200" cy="200" r="172" fill="none" stroke="#B8834E" stroke-width="1.2" stroke-dasharray="4,3" />
  <circle cx="200" cy="200" r="126" fill="none" stroke="#E8E3DA" stroke-width="1.2" />
  <text class="seal-text-top">
    <textPath href="#circlePathTop" startOffset="50%" text-anchor="middle">
      {brand.name.upper()}
    </textPath>
  </text>
  <text class="seal-text-bot">
    <textPath href="#circlePathBottom" startOffset="50%" text-anchor="middle">
      • ARCHIVAL FINE ART &amp; FRAMING •
    </textPath>
  </text>
  <image href="data:image/png;base64,{emblem_b64}" x="105" y="105" width="190" height="190" />
</svg>"""
        else:
            svg_wordmark_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 120" width="100%" height="100%">
  <style>
    .brand-title {{ font-family: 'Cormorant Garamond', 'Georgia', serif; font-size: 42px; font-weight: 600; letter-spacing: 0.18em; fill: {brand.palette[0]}; text-anchor: middle; }}
    .brand-sub {{ font-family: 'Inter', 'Helvetica Neue', sans-serif; font-size: 11px; font-weight: 500; letter-spacing: 0.32em; fill: {brand.palette[2]}; text-anchor: middle; }}
    .brand-line {{ stroke: {brand.palette[3]}; stroke-width: 1; }}
  </style>
  <text x="300" y="55" class="brand-title">{brand.name.upper()}</text>
  <line x1="180" y1="75" x2="420" y2="75" class="brand-line" />
  <text x="300" y="96" class="brand-sub">{brand.tagline.upper()}</text>
</svg>"""
            initials = "".join([w[0] for w in brand.name.split() if w[0].isalpha() and w != "&"])[:3]
            svg_seal_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="100%">
  <circle cx="150" cy="150" r="140" fill="{brand.palette[1]}" stroke="{brand.palette[0]}" stroke-width="3" />
  <circle cx="150" cy="150" r="128" fill="none" stroke="{brand.palette[3]}" stroke-width="1" stroke-dasharray="4,4" />
  <text x="150" y="145" font-family="'Cormorant Garamond', serif" font-size="54px" font-weight="700" letter-spacing="0.1em" fill="{brand.palette[0]}" text-anchor="middle">{initials}</text>
  <text x="150" y="180" font-family="'Inter', sans-serif" font-size="10px" font-weight="600" letter-spacing="0.25em" fill="{brand.palette[2]}" text-anchor="middle">ARCHIVAL FINE ART</text>
</svg>"""

        with open(svg_logo_path, "w", encoding="utf-8") as f:
            f.write(svg_wordmark_content)
        out_paths["svg_wordmark"] = svg_logo_path

        with open(svg_seal_path, "w", encoding="utf-8") as f:
            f.write(svg_seal_content)
        out_paths["svg_seal"] = svg_seal_path
        if svg_emblem_path.exists():
            out_paths["svg_emblem"] = svg_emblem_path

        # 2. Raster PNG High-Res Logos & Favicons
        png_logo_path = self.brand_dir / "logo_primary_1200x400.png"
        img = Image.new("RGB", (1200, 400), color=(250, 248, 245))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 1200, 400], fill=(250, 248, 245))
        draw.text((380, 140), brand.name.upper(), fill=(28, 28, 30))
        draw.line([(320, 210), (880, 210)], fill=(200, 190, 180), width=2)
        draw.text((400, 230), brand.tagline.upper(), fill=(198, 107, 77))
        img.save(png_logo_path, "PNG")
        out_paths["png_wordmark"] = png_logo_path

        # Favicon (512x512)
        favicon_path = self.brand_dir / "favicon_512x512.png"
        fav = Image.new("RGB", (512, 512), color=(28, 28, 30))
        d_fav = ImageDraw.Draw(fav)
        d_fav.rectangle([20, 20, 492, 492], outline=(218, 180, 145), width=4)
        d_fav.text((180, 200), initials, fill=(250, 248, 245))
        d_fav.text((140, 290), "ARCHIVAL", fill=(198, 107, 77))
        fav.save(favicon_path, "PNG")
        out_paths["favicon"] = favicon_path

        # 3. Social Media Banners
        # Pinterest Banner (1200x675)
        pin_banner_path = self.brand_dir / "pinterest_header_banner_1200x675.jpg"
        pin_banner = Image.new("RGB", (1200, 675), color=(28, 28, 30))
        pb_draw = ImageDraw.Draw(pin_banner)
        pb_draw.rectangle([40, 40, 1160, 635], outline=(80, 75, 70), width=1)
        pb_draw.text((420, 260), brand.name.upper(), fill=(250, 248, 245))
        pb_draw.line([(400, 320), (800, 320)], fill=(198, 107, 77), width=2)
        pb_draw.text((360, 345), brand.tagline.upper(), fill=(210, 205, 198))
        pb_draw.text((410, 410), "Printed & Framed Locally in 32 Countries", fill=(100, 160, 120))
        pin_banner.save(pin_banner_path, "JPEG", quality=95)
        out_paths["pinterest_banner"] = pin_banner_path

        # 4. Master Brand Book (Markdown)
        brand_book_path = self.brand_dir / "BRAND_IDENTITY_GUIDELINES.md"
        with open(brand_book_path, "w", encoding="utf-8") as f:
            f.write(f"""# 🏛️ {brand.name} | Master Brand Identity & Style Guide
**Positioning**: {brand.tagline}
**Primary Domain Strategy**: `{brand.domains[0]}` (Alternates: `{', '.join(brand.domains[1:])}`)

---

## 💎 Brand Archetype & Story
{brand.brand_story}

### Simplicity & Trust Factor
{brand.simplicity_credibility_rationale}


---

## 🎨 Signature Color Palette
| Swatch | Color Name | Hex Code | Purpose |
| :--- | :--- | :--- | :--- |
| ⬛ | Deep Obsidian | `{brand.palette[0]}` | Primary Text, Hero Framing, Luxury Contrast |
| ⬜ | Limewash Ivory | `{brand.palette[1]}` | Canvas Backgrounds, Archival Mats, Page Base |
| 🟫 | Warm Terracotta | `{brand.palette[2]}` | Accent Badges, Call to Actions, Price Accents |
| 🔘 | Raw Linen Sand | `{brand.palette[3]}` | Borders, Dividers, Card Backgrounds |
| 🟩 | Forest Sage | `{brand.palette[4]}` | Trust Guarantees, 72h Delivery Badges |

---

## 🔤 Typography Pairing
* **Primary Header & Logo**: `Cormorant Garamond` (Serif, Elegant, Archival Authority)
* **Body & UI**: `Inter` or `Plus Jakarta Sans` (Clean, Modern, High Legibility on Mobile)

---

## 📱 Social Media Setup Kit
* **Gmail Account**: `{brand.recommended_social_handles['gmail']}`
* **Pinterest Handle**: `{brand.recommended_social_handles['pinterest']}`
* **TikTok Handle**: `{brand.recommended_social_handles['tiktok']}`
* **Instagram Handle**: `{brand.recommended_social_handles['instagram']}`

### Master Social Bio Template (Paste into Pinterest/TikTok/IG):
> 🏛️ **{brand.name}** | {brand.tagline}  
> 🖼️ Museum-grade archival paper & handcrafted solid oak frames.  
> 🚚 72-Hour local delivery across 32 countries.  
> 🔗 **{brand.domains[0]}**
""")
        out_paths["brand_book"] = brand_book_path

        return out_paths

brand_identity_agent = BrandIdentityAgent()
