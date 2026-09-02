import os
import base64
from pathlib import Path
from PIL import Image
import numpy as np

def generate_brand_suite():
    brain_img = Path(r"C:\Users\pedro\.gemini\antigravity\brain\637c8188-56ca-4933-abf6-ce7af7f9ad8d\oak_brand_emblem_1788383015013.jpg")
    if not brain_img.exists():
        raise FileNotFoundError(f"Source illustration not found: {brain_img}")

    orig = Image.open(brain_img).convert("RGB")
    arr = np.array(orig, dtype=np.float32)

    # Calculate lightness to extract dark linework from paper
    lightness = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    ink_threshold = 230.0
    solid_threshold = 90.0

    alpha = np.clip((ink_threshold - lightness) / (ink_threshold - solid_threshold) * 255.0, 0, 255).astype(np.uint8)

    # Warm charcoal ink lines (#1C1C1E)
    r_ch = np.full_like(alpha, 28)
    g_ch = np.full_like(alpha, 28)
    b_ch = np.full_like(alpha, 30)

    rgba = np.dstack([r_ch, g_ch, b_ch, alpha])
    transparent_img = Image.fromarray(rgba, mode="RGBA")

    # Crop to content
    bbox = transparent_img.getbbox()
    cropped = transparent_img.crop(bbox)

    # Pad into a square
    w, h = cropped.size
    max_dim = max(w, h)
    pad = int(max_dim * 0.08)
    target_dim = max_dim + 2 * pad

    square_emblem = Image.new("RGBA", (target_dim, target_dim), (0, 0, 0, 0))
    offset_x = (target_dim - w) // 2
    offset_y = (target_dim - h) // 2
    square_emblem.paste(cropped, (offset_x, offset_y), cropped)

    # Directories
    brand_dir = Path("brand_identity")
    brand_dir.mkdir(parents=True, exist_ok=True)
    images_dir = Path("storefront/static/images")
    images_dir.mkdir(parents=True, exist_ok=True)
    static_dir = Path("storefront/static")

    # 1. Save High-Res PNG Emblem (1024x1024)
    emblem_1024 = square_emblem.resize((1024, 1024), Image.Resampling.LANCZOS)
    emblem_1024.save(brand_dir / "logo_emblem.png")
    emblem_1024.save(images_dir / "logo_emblem.png")

    # 2. Save Favicons
    fav_512 = square_emblem.resize((512, 512), Image.Resampling.LANCZOS)
    fav_512.save(brand_dir / "favicon_512x512.png")
    fav_512.save(images_dir / "favicon_512x512.png")
    fav_512.save(static_dir / "favicon.png")

    fav_64 = square_emblem.resize((64, 64), Image.Resampling.LANCZOS)
    fav_64.save(static_dir / "favicon.ico", format="ICO")

    # Encode emblem for SVGs
    with open(brand_dir / "logo_emblem.png", "rb") as f:
        emblem_b64 = base64.b64encode(f.read()).decode("utf-8")

    # 3. Standalone Emblem SVG
    emblem_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="100%" height="100%">
  <image href="data:image/png;base64,{emblem_b64}" x="0" y="0" width="500" height="500" />
</svg>"""
    with open(brand_dir / "logo_emblem.svg", "w", encoding="utf-8") as f:
        f.write(emblem_svg)
    with open(images_dir / "logo_emblem.svg", "w", encoding="utf-8") as f:
        f.write(emblem_svg)

    # 4. Primary Horizontal Wordmark SVG
    wordmark_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 140" width="100%" height="100%">
  <style>
    .brand-title {{ font-family: 'Cormorant Garamond', 'Georgia', serif; font-size: 40px; font-weight: 700; letter-spacing: 0.16em; fill: #1C1C1E; }}
    .brand-sub {{ font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; font-size: 11px; font-weight: 600; letter-spacing: 0.26em; fill: #B8834E; }}
    .brand-line {{ stroke: #E8E3DA; stroke-width: 1.5; }}
  </style>
  <g transform="translate(10, 5)">
    <image href="data:image/png;base64,{emblem_b64}" x="0" y="0" width="130" height="130" />
  </g>
  <text x="165" y="62" class="brand-title">OAK PRINT STUDIO</text>
  <line x1="165" y1="84" x2="680" y2="84" class="brand-line" />
  <text x="165" y="106" class="brand-sub">MUSEUM ART &amp; SOLID WOOD FRAMING</text>
</svg>"""
    with open(brand_dir / "logo_primary_wordmark.svg", "w", encoding="utf-8") as f:
        f.write(wordmark_svg)
    with open(images_dir / "logo_primary_wordmark.svg", "w", encoding="utf-8") as f:
        f.write(wordmark_svg)

    # 5. Circular Atelier Seal SVG
    seal_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
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
      OAK PRINT STUDIO
    </textPath>
  </text>
  <text class="seal-text-bot">
    <textPath href="#circlePathBottom" startOffset="50%" text-anchor="middle">
      • ARCHIVAL FINE ART &amp; FRAMING •
    </textPath>
  </text>
  <image href="data:image/png;base64,{emblem_b64}" x="105" y="105" width="190" height="190" />
</svg>"""
    with open(brand_dir / "logo_monogram_seal.svg", "w", encoding="utf-8") as f:
        f.write(seal_svg)
    with open(images_dir / "logo_seal.svg", "w", encoding="utf-8") as f:
        f.write(seal_svg)

    print("All master brand assets generated successfully!")

if __name__ == "__main__":
    generate_brand_suite()
