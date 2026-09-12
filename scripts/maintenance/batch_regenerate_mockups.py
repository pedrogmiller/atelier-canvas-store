import json
import shutil
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.mockup_agent import mockup_agent

def batch_update_all_mockups():
    catalog_path = BASE_DIR / "storefront" / "catalog.json"

    with open(catalog_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"Generating 3-shot Minted staging formula mockups for {len(products)} collections...")

    for idx, p in enumerate(products, 1):
        p_id = p.get("id")
        title = p.get("title")
        
        art_path = BASE_DIR / "output" / p_id / "master_artwork_300dpi.jpg"
        if not art_path.exists():
            art_path = BASE_DIR / "storefront" / "static" / "products" / p_id / "master_art.jpg"
        
        if not art_path.exists():
            print(f"  [{idx:02d}/{len(products)}] Warning: Master art not found for {p_id}, skipping.")
            continue

        output_dir = BASE_DIR / "output" / p_id
        mockups = mockup_agent.generate_mockups(art_path, output_dir, title)
        
        static_dir = BASE_DIR / "storefront" / "static" / "products" / p_id
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Copy Living Room frame variations
        for f_key, src in mockups["living_room_frames"].items():
            shutil.copy(src, static_dir / f"living_room_{f_key}.jpg")

        # 2. Copy 45-deg Corner Detail variations
        for f_key, src in mockups["corner_detail_frames"].items():
            shutil.copy(src, static_dir / f"corner_{f_key}.jpg")

        # 3. Copy Gallery Wall variations
        for f_key, src in mockups["gallery_wall_frames"].items():
            shutil.copy(src, static_dir / f"gallery_wall_{f_key}.jpg")

        # 4. Copy Framed Detail variations
        for f_key, src in mockups["framed_detail_frames"].items():
            shutil.copy(src, static_dir / f"framed_{f_key}.jpg")

        # 5. Standard bedroom, studio, and defaults
        shutil.copy(mockups["bedroom_black"], static_dir / "bedroom_black.jpg")
        shutil.copy(mockups["studio_white"], static_dir / "studio_white.jpg")
        shutil.copy(mockups["living_room_oak"], static_dir / "living_room_oak.jpg")
        shutil.copy(mockups["framed_product"], static_dir / "framed_product.jpg")
        
        # Update product.images in catalog object
        p["images"]["hero"] = f"/static/products/{p_id}/living_room_natural_oak.jpg"
        p["images"]["living_room"] = f"/static/products/{p_id}/living_room_natural_oak.jpg"
        p["images"]["corner"] = f"/static/products/{p_id}/corner_natural_oak.jpg"
        p["images"]["corner_detail"] = f"/static/products/{p_id}/corner_natural_oak.jpg"
        p["images"]["gallery_wall"] = f"/static/products/{p_id}/gallery_wall_natural_oak.jpg"
        p["images"]["framed_product"] = f"/static/products/{p_id}/framed_natural_oak.jpg"

        p["images"]["living_room_frames"] = {
            f_key: f"/static/products/{p_id}/living_room_{f_key}.jpg"
            for f_key in mockups["living_room_frames"]
        }
        p["images"]["corner_detail_frames"] = {
            f_key: f"/static/products/{p_id}/corner_{f_key}.jpg"
            for f_key in mockups["corner_detail_frames"]
        }
        p["images"]["gallery_wall_frames"] = {
            f_key: f"/static/products/{p_id}/gallery_wall_{f_key}.jpg"
            for f_key in mockups["gallery_wall_frames"]
        }
        p["images"]["framed_detail_frames"] = {
            f_key: f"/static/products/{p_id}/framed_{f_key}.jpg"
            for f_key in mockups["framed_detail_frames"]
        }
        
        print(f"  [{idx:02d}/{len(products)}] 3-shot staged mockups generated: {title[:40]}...")

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)

    print("\nAll collections successfully upgraded with the 3-shot Minted staging formula!")

if __name__ == "__main__":
    batch_update_all_mockups()
