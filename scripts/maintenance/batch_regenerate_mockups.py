import json
import shutil
from pathlib import Path
from agents.mockup_agent import mockup_agent

def batch_update_all_mockups():
    base_dir = Path(r"C:\Users\pedro\.gemini\antigravity\scratch\art_ecommerce_agents")
    catalog_path = base_dir / "storefront" / "catalog.json"

    with open(catalog_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"Generating multi-frame living room and detail mockups for {len(products)} collections...")

    for idx, p in enumerate(products, 1):
        p_id = p.get("id")
        title = p.get("title")
        
        art_path = base_dir / "output" / p_id / "master_artwork_300dpi.jpg"
        if not art_path.exists():
            art_path = base_dir / "storefront" / "static" / "products" / p_id / "master_art.jpg"
        
        if not art_path.exists():
            continue

        output_dir = base_dir / "output" / p_id
        mockups = mockup_agent.generate_mockups(art_path, output_dir, title)
        
        static_dir = base_dir / "storefront" / "static" / "products" / p_id
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy Living Room frame variations
        for f_key, src in mockups["living_room_frames"].items():
            shutil.copy(src, static_dir / f"living_room_{f_key}.jpg")

        # Copy Framed Detail variations
        for f_key, src in mockups["framed_detail_frames"].items():
            shutil.copy(src, static_dir / f"framed_{f_key}.jpg")

        # Standard bedroom, studio, and defaults
        shutil.copy(mockups["bedroom_black"], static_dir / "bedroom_black.jpg")
        shutil.copy(mockups["studio_white"], static_dir / "studio_white.jpg")
        shutil.copy(mockups["living_room_oak"], static_dir / "living_room_oak.jpg")
        shutil.copy(mockups["framed_product"], static_dir / "framed_product.jpg")
        
        # Update product.images in catalog object
        p["images"]["living_room_frames"] = {
            f_key: f"/static/products/{p_id}/living_room_{f_key}.jpg"
            for f_key in mockups["living_room_frames"]
        }
        p["images"]["framed_detail_frames"] = {
            f_key: f"/static/products/{p_id}/framed_{f_key}.jpg"
            for f_key in mockups["framed_detail_frames"]
        }
        
        print(f"  [{idx:02d}/{len(products)}] Multi-frame variants generated: {title[:40]}...")

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)

    print("\nAll collections successfully upgraded with real-time frame color switching!")

if __name__ == "__main__":
    batch_update_all_mockups()
