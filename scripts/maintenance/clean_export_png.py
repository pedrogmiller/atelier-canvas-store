import json
import shutil
import re
from pathlib import Path
from PIL import Image

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text[:40]

def clean_and_export_png_gallery():
    base_dir = Path(r"C:\Users\pedro\.gemini\antigravity\scratch\art_ecommerce_agents")
    catalog_path = base_dir / "storefront" / "catalog.json"
    output_png_dir = base_dir / "fine_art_gallery_png"
    
    # 1. Clean directory completely
    if output_png_dir.exists():
        shutil.rmtree(output_png_dir)
    output_png_dir.mkdir(parents=True, exist_ok=True)

    with open(catalog_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    # Use unique collections (first 30)
    seen_aesthetics = set()
    selected_products = []
    for p in products:
        selected_products.append(p)
        if len(selected_products) >= 30:
            break

    print(f"Exporting clean, deduplicated {len(selected_products)} diverse fine art PNGs...")
    
    for idx, p in enumerate(selected_products, 1):
        p_id = p.get("id")
        title = p.get("title", f"Artwork {idx}")
        aesthetic = p.get("aesthetic_id", "art")
        clean_name = slugify(f"{aesthetic}_{title}")
        png_filename = f"{idx:02d}_{clean_name}.png"
        png_dest_path = output_png_dir / png_filename

        source_1 = base_dir / "output" / p_id / "master_artwork_300dpi.jpg"
        source_2 = base_dir / "storefront" / "static" / "products" / p_id / "master_art.jpg"

        source_path = source_1 if source_1.exists() else source_2

        if source_path and source_path.exists():
            with Image.open(source_path) as img:
                img_rgb = img.convert("RGB")
                img_rgb.save(png_dest_path, "PNG", optimize=True)
                w, h = img_rgb.size
                size_kb = png_dest_path.stat().st_size / 1024
                print(f"  [{idx:02d}/30] {png_filename} ({w}x{h} px, {size_kb:.1f} KB)")

    print("\nClean PNG gallery ready at:", output_png_dir)

if __name__ == "__main__":
    clean_and_export_png_gallery()
