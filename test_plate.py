import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance

def generate_photorealistic_living_room_plate(width=1600, height=1200) -> Image.Image:
    """Renders a rich, highly detailed architectural living room interior with warm sunlight and textures."""
    # 1. Warm limewash plaster wall with gradient
    base = Image.new("RGB", (width, height), (243, 239, 232))
    draw = ImageDraw.Draw(base)

    # Vertical subtle wall gradient (lighter near ceiling, warm near floor)
    for y in range(850):
        t = y / 850.0
        r = int(246 - t * 8)
        g = int(242 - t * 8)
        b = int(236 - t * 8)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Add subtle wall plaster texture
    noise = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    n_draw = ImageDraw.Draw(noise)
    for _ in range(25000):
        nx = random.randint(0, width)
        ny = random.randint(0, 850)
        alpha = random.randint(4, 18)
        tone = random.choice([255, 220, 180])
        n_draw.point((nx, ny), fill=(tone, tone, tone, alpha))
    base.paste(noise, (0, 0), noise)

    # 3. Floor: Warm European Herringbone Natural Oak Wood Planks
    floor_y = 820
    # Base wood tone
    draw.rectangle([0, floor_y, width, height], fill=(188, 156, 126))
    
    # Draw herringbone / plank lines with natural tone variations
    for py in range(floor_y, height, 22):
        shade_offset = random.randint(-12, 12)
        r = min(255, max(0, 188 + shade_offset))
        g = min(255, max(0, 156 + shade_offset))
        b = min(255, max(0, 126 + shade_offset))
        draw.rectangle([0, py, width, py + 22], fill=(r, g, b))
        draw.line([(0, py), (width, py)], fill=(145, 115, 88), width=1)
        
        # Staggered vertical plank joints
        for px in range(0, width, 180):
            stagger = 90 if (py // 22) % 2 == 0 else 0
            draw.line([(px + stagger, py), (px + stagger, py + 22)], fill=(140, 110, 85), width=1)

    # 4. Solid Wood Baseboard / Skirting
    draw.rectangle([0, floor_y - 28, width, floor_y], fill=(248, 246, 240))
    draw.line([(0, floor_y - 28), (width, floor_y - 28)], fill=(210, 205, 195), width=1)
    draw.line([(0, floor_y), (width, floor_y)], fill=(130, 100, 75), width=2) # Floor contact shadow

    # 5. Modern Organic Bouclé Sofa (Curved, tactile, layered cushions)
    # Sofa Base Depth Shadow
    sofa_l, sofa_r = 180, 1420
    sofa_t = 730
    sofa_shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(sofa_shadow)
    s_draw.ellipse([sofa_l - 40, floor_y - 30, sofa_r + 40, floor_y + 80], fill=(40, 30, 20, 140))
    sofa_shadow = sofa_shadow.filter(ImageFilter.GaussianBlur(25))
    base.paste(sofa_shadow, (0, 0), sofa_shadow)

    # Sofa Main Body (Warm Cream Bouclé)
    if hasattr(draw, "rounded_rectangle"):
        draw.rounded_rectangle([sofa_l, sofa_t, sofa_r, floor_y + 120], radius=45, fill=(232, 226, 216))
        # Seat Cushion
        draw.rounded_rectangle([sofa_l + 20, sofa_t + 50, sofa_r - 20, floor_y + 60], radius=30, fill=(238, 233, 224))
        # Left Back Cushion
        draw.rounded_rectangle([sofa_l + 40, sofa_t - 20, 760, floor_y - 10], radius=35, fill=(225, 218, 208))
        # Right Back Cushion
        draw.rounded_rectangle([780, sofa_t - 20, sofa_r - 40, floor_y - 10], radius=35, fill=(225, 218, 208))
        # Linen Throw Cushion (Terracotta / Ochre accent)
        draw.rounded_rectangle([sofa_l + 80, sofa_t + 10, sofa_l + 250, sofa_t + 170], radius=22, fill=(195, 115, 82))
        draw.rounded_rectangle([sofa_r - 260, sofa_t + 10, sofa_r - 90, sofa_t + 170], radius=22, fill=(120, 135, 118))
    else:
        draw.rectangle([sofa_l, sofa_t, sofa_r, floor_y + 80], fill=(232, 226, 216))

    # 6. Natural Sunlight Window Cast Shadow (Warm morning sun angle)
    sunlight = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sun_draw = ImageDraw.Draw(sunlight)
    # Angled architectural sunbeam polygon
    sun_draw.polygon([
        (0, 0), (700, 0), (1200, floor_y + 200), (0, floor_y + 200)
    ], fill=(255, 250, 235, 38))
    sunlight = sunlight.filter(ImageFilter.GaussianBlur(15))
    base.paste(sunlight, (0, 0), sunlight)

    # 7. Organic Indoor Fiddle-Leaf Fig / Olive Tree Silhouette in Corner
    plant = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(plant)
    # Terracotta Planter Pot
    pot_x, pot_y = 120, 720
    p_draw.polygon([(pot_x - 35, pot_y + 160), (pot_x + 35, pot_y + 160), (pot_x + 48, pot_y), (pot_x - 48, pot_y)], fill=(185, 105, 75, 240))
    # Plant branches & lush leaves
    p_draw.line([(pot_x, pot_y), (pot_x - 40, pot_y - 260)], fill=(75, 60, 45, 240), width=6)
    p_draw.line([(pot_x, pot_y - 80), (pot_x + 60, pot_y - 220)], fill=(75, 60, 45, 240), width=5)
    
    # Leaves
    for lx, ly, w_rad, h_rad, angle in [
        (pot_x - 60, pot_y - 280, 45, 25, -20),
        (pot_x - 20, pot_y - 320, 50, 28, 15),
        (pot_x + 70, pot_y - 240, 48, 26, 30),
        (pot_x + 30, pot_y - 180, 42, 24, -10),
        (pot_x - 50, pot_y - 160, 40, 22, -35),
    ]:
        p_draw.ellipse([lx - w_rad, ly - h_rad, lx + w_rad, ly + h_rad], fill=(55, 78, 58, 230))
    
    plant = plant.filter(ImageFilter.GaussianBlur(1))
    base.paste(plant, (0, 0), plant)

    return base

if __name__ == "__main__":
    t = generate_photorealistic_living_room_plate()
    t.save("test_living_room_plate.jpg", "JPEG", quality=95)
    print("Photorealistic Living Room Plate Generated!")
