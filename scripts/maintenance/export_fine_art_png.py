import json
import os
import re
from pathlib import Path
from PIL import Image

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text[:45]

def export_all_art_to_png():
    base_dir = Path(r"C:\Users\pedro\.gemini\antigravity\scratch\art_ecommerce_agents")
    catalog_path = base_dir / "storefront" / "catalog.json"
    output_png_dir = base_dir / "fine_art_gallery_png"
    output_png_dir.mkdir(parents=True, exist_ok=True)

    if not catalog_path.exists():
        print("catalog.json not found!")
        return

    with open(catalog_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"Exporting {len(products)} fine art master prints to PNG format...")
    exported_count = 0

    for idx, p in enumerate(products, 1):
        p_id = p.get("id")
        title = p.get("title", f"Artwork {idx}")
        clean_name = slugify(title)
        png_filename = f"{idx:02d}_{clean_name}.png"
        png_dest_path = output_png_dir / png_filename

        # Source paths
        source_1 = base_dir / "output" / p_id / "master_artwork_300dpi.jpg"
        source_2 = base_dir / "storefront" / "static" / "products" / p_id / "master_art.jpg"

        source_path = None
        if source_1.exists():
            source_path = source_1
        elif source_2.exists():
            source_path = source_2

        if source_path:
            with Image.open(source_path) as img:
                img_rgb = img.convert("RGB")
                img_rgb.save(png_dest_path, "PNG", optimize=True)
                w, h = img_rgb.size
                size_mb = png_dest_path.stat().st_size / (1024 * 1024)
                print(f"  [{idx:02d}/{len(products)}] Exported: {png_filename} ({w}x{h} px, {size_mb:.2f} MB)")
                exported_count += 1
        else:
            print(f"  [MISSING] Source art not found for {p_id}")

    print(f"\nSuccessfully exported {exported_count} fine art pieces in PNG format to:")
    print(f"{output_png_dir}")

if __name__ == "__main__":
    export_all_art_to_png()
