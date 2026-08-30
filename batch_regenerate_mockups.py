import json
import shutil
from pathlib import Path
from agents.mockup_agent import mockup_agent

def batch_update_all_mockups():
    base_dir = Path(r"C:\Users\pedro\.gemini\antigravity\scratch\art_ecommerce_agents")
    catalog_path = base_dir / "storefront" / "catalog.json"

    with open(catalog_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"Re-rendering photorealistic room scenes for {len(products)} collections...")

    for idx, p in enumerate(products, 1):
        p_id = p.get("id")
        title = p.get("title")
        
        # Locate artwork
        art_path = base_dir / "output" / p_id / "master_artwork_300dpi.jpg"
        if not art_path.exists():
            art_path = base_dir / "storefront" / "static" / "products" / p_id / "master_art.jpg"
        
        if not art_path.exists():
            print(f"  [SKIP] No master art found for {p_id}")
            continue

        output_dir = base_dir / "output" / p_id
        mockups = mockup_agent.generate_mockups(art_path, output_dir, title)
        
        # Copy to storefront
        static_dir = base_dir / "storefront" / "static" / "products" / p_id
        static_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(mockups["living_room_oak"], static_dir / "living_room_oak.jpg")
        shutil.copy(mockups["bedroom_black"], static_dir / "bedroom_black.jpg")
        shutil.copy(mockups["studio_white"], static_dir / "studio_white.jpg")
        shutil.copy(mockups["framed_product"], static_dir / "framed_product.jpg")
        
        print(f"  [{idx:02d}/{len(products)}] Photorealistic mockups rendered: {title[:40]}...")

    print("\nAll 30+ collections upgraded with photorealistic living rooms!")

if __name__ == "__main__":
    batch_update_all_mockups()
