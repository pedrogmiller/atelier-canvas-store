from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = getattr(Image, "LANCZOS", getattr(Image, "ANTIALIAS", 1))

def composite_art_on_real_photo():
    base_dir = Path(r"C:\Users\pedro\.gemini\antigravity\scratch\art_ecommerce_agents")
    photo_path = base_dir / "assets" / "room_templates" / "living_room_real.jpg"
    art_path = base_dir / "output" / "amalfi-lemon-groves-terracotta-heirloom-amalfi-lemon-branch-with-leaves-no-5-3927d3" / "master_artwork_300dpi.jpg"
    if not art_path.exists():
        art_path = base_dir / "storefront" / "static" / "products" / "amalfi-lemon-groves-terracotta-heirloom-amalfi-lemon-branch-with-leaves-no-5-3927d3" / "master_art.jpg"

    if not photo_path.exists() or not art_path.exists():
        print("Paths not found!")
        return

    # Load real photo and art
    scene = Image.open(photo_path).convert("RGB")
    art = Image.open(art_path).convert("RGB")

    # Resize photo to standard 1600x1200
    scene = scene.resize((1600, 1200), RESAMPLE_FILTER)
    sw, sh = scene.size

    # Frame art with natural oak wood frame & archival mat
    mat_w = 36
    frame_w = 18
    frame_color = (198, 155, 112) # Natural Oak

    # 1. Matting
    matted = ImageOps.expand(art, border=mat_w, fill=(248, 246, 240))
    # 2. Wooden Frame
    framed = ImageOps.expand(matted, border=frame_w, fill=frame_color)
    
    # 3. Frame 3D bevel highlights
    fw, fh = framed.size
    f_draw = ImageDraw.Draw(framed)
    f_draw.line([(0, 0), (fw, 0)], fill=(255, 255, 255, 75), width=1)
    f_draw.line([(0, 0), (0, fh)], fill=(255, 255, 255, 75), width=1)
    f_draw.line([(0, fh - 1), (fw, fh - 1)], fill=(0, 0, 0, 85), width=1)
    f_draw.line([(fw - 1, 0), (fw - 1, fh)], fill=(0, 0, 0, 85), width=1)
    f_draw.rectangle([frame_w - 1, frame_w - 1, fw - frame_w, fh - frame_w], outline=(0, 0, 0, 100), width=2)

    # Resize framed art to fit wall proportionally (e.g. 440px high)
    target_h = 440
    aspect = fw / fh
    target_w = int(target_h * aspect)
    framed_scaled = framed.resize((target_w, target_h), RESAMPLE_FILTER)
    
    # Wall placement coordinates in the real living room photo (upper wall centered above sofa)
    fw_s, fh_s = framed_scaled.size
    fx = (sw - fw_s) // 2
    fy = 170

    # Photorealistic 2-layer wall drop shadow
    shadow = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    # Contact shadow
    s_draw.rectangle([fx + 4, fy + 8, fx + fw_s + 8, fy + fh_s + 12], fill=(15, 12, 10, 140))
    # Diffuse ambient shadow
    s_draw.rectangle([fx + 10, fy + 18, fx + fw_s + 20, fy + fh_s + 28], fill=(25, 20, 15, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    
    # Composite
    scene.paste(shadow, (0, 0), shadow)
    scene.paste(framed_scaled, (fx, fy))

    out_test = base_dir / "test_real_photo_mockup.jpg"
    scene.save(out_test, "JPEG", quality=95)
    print("Saved test real photo mockup to:", out_test)


if __name__ == "__main__":
    composite_art_on_real_photo()
