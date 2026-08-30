import os
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

def setup_real_photography_templates():
    template_dir = Path(r"C:\Users\pedro\.gemini\antigravity\scratch\art_ecommerce_agents\assets\room_templates")
    template_dir.mkdir(parents=True, exist_ok=True)

    # Real architectural & interior photography sources (Royalty-free Unsplash high-res)
    photo_urls = {
        "living_room_real.jpg": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1600&q=85",
        "scandi_living_real.jpg": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1600&q=85",
        "bedroom_real.jpg": "https://images.unsplash.com/photo-1616046229478-9901c5536a45?auto=format&fit=crop&w=1600&q=85",
        "studio_real.jpg": "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&w=1600&q=85"
    }

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for name, url in photo_urls.items():
        dest = template_dir / name
        if not dest.exists():
            print(f"Downloading real photography room background: {name}...")
            try:
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code == 200:
                    with open(dest, "wb") as f:
                        f.write(r.content)
                    print(f"  [OK] Saved: {name}")
                else:
                    print(f"  [FAIL] ({r.status_code}) for {name}")
            except Exception as e:
                print(f"  [ERROR] downloading {name}: {e}")
        else:
            print(f"  [EXISTS] Template already exists: {name}")

if __name__ == "__main__":
    setup_real_photography_templates()

