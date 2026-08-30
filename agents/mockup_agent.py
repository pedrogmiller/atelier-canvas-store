import math
import random
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance

from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("MockupAgent")

try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = getattr(Image, "LANCZOS", getattr(Image, "ANTIALIAS", 1))

def _draw_rounded_rect(draw: ImageDraw.ImageDraw, box: List[int], radius: int, fill: Any):
    """Draws rounded rectangle if supported by Pillow, else falls back to standard rectangle."""
    if hasattr(draw, "rounded_rectangle"):
        draw.rounded_rectangle(box, radius=radius, fill=fill)
    else:
        draw.rectangle(box, fill=fill)

class MockupAgent(BaseAgent):
    """Virtual Interior Staging & 3D Mockup Artist creating photorealistic interior room scenes."""

    def __init__(self):
        super().__init__(
            name="MockupAgent",
            role_description="Virtual Interior Staging & Photorealistic Mockup Artist"
        )

    def generate_mockups(self, art_image_path: Path, output_dir: Path, title: str) -> Dict[str, str]:
        """Generates 4 distinct, photorealistic lifestyle room mockups and framed product previews."""
        output_dir.mkdir(parents=True, exist_ok=True)
        art_img = Image.open(art_image_path).convert("RGB")

        mockup_files = {}

        # 1. Living Room Hero Scene (Solid Natural Oak Frame above Bouclé Sofa)
        m1_path = output_dir / "mockup_living_room_oak.jpg"
        m1_img = self._create_photorealistic_living_room(art_img, frame_color=(198, 155, 112), mat_border=38)
        m1_img.save(m1_path, "JPEG", quality=94)
        mockup_files["living_room_oak"] = str(m1_path)

        # 2. Master Bedroom Scene (Matte Black Frame above Linen Headboard)
        m2_path = output_dir / "mockup_bedroom_black.jpg"
        m2_img = self._create_photorealistic_bedroom(art_img, frame_color=(28, 28, 30), mat_border=32)
        m2_img.save(m2_path, "JPEG", quality=94)
        mockup_files["bedroom_black"] = str(m2_path)

        # 3. Nordic Minimalist Studio (Nordic White Wood Frame above Travertine Console)
        m3_path = output_dir / "mockup_studio_white.jpg"
        m3_img = self._create_photorealistic_studio(art_img, frame_color=(242, 240, 236), mat_border=42)
        m3_img.save(m3_path, "JPEG", quality=94)
        mockup_files["studio_white"] = str(m3_path)

        # 4. Pure Gallery Studio Framed Shot (High-Resolution Detail View)
        m4_path = output_dir / "mockup_framed_product.jpg"
        m4_img = self._create_gallery_framed_shot(art_img, frame_color=(198, 155, 112))
        m4_img.save(m4_path, "JPEG", quality=94)
        mockup_files["framed_product"] = str(m4_path)

        logger.info(f"[{self.name}] Generated 4 photorealistic room mockups in {output_dir}")
        return mockup_files

    def _apply_realistic_frame(self, art: Image.Image, frame_color: Tuple[int, int, int], frame_width: int = 22, mat_width: int = 38) -> Image.Image:
        """Adds archival museum matting, wood grain texture, bevel core, and glass reflections."""
        # 1. White Archival Cotton Matting with warm tone
        if mat_width > 0:
            matted = ImageOps.expand(art, border=mat_width, fill=(247, 245, 239))
            # Draw inner core bevel line
            m_draw = ImageDraw.Draw(matted)
            mw, mh = matted.size
            m_draw.rectangle([mat_width - 1, mat_width - 1, mw - mat_width, mh - mat_width], outline=(215, 210, 200), width=1)
        else:
            matted = art

        # 2. Solid Wood Frame Moulding
        framed = ImageOps.expand(matted, border=frame_width, fill=frame_color)
        fw, fh = framed.size
        f_draw = ImageDraw.Draw(framed)

        # 3. Realistic 3D Bevel & Lighting Highlights on Frame
        # Outer light highlight on top & left
        f_draw.line([(0, 0), (fw, 0)], fill=(255, 255, 255, 80), width=1)
        f_draw.line([(0, 0), (0, fh)], fill=(255, 255, 255, 80), width=1)
        # Outer shadow on bottom & right
        f_draw.line([(0, fh - 1), (fw, fh - 1)], fill=(0, 0, 0, 90), width=1)
        f_draw.line([(fw - 1, 0), (fw - 1, fh)], fill=(0, 0, 0, 90), width=1)
        
        # Inner frame recess shadow
        f_draw.rectangle([frame_width - 1, frame_width - 1, fw - frame_width, fh - frame_width], outline=(0, 0, 0, 110), width=2)

        # 4. Subtle Diagonal Museum Glass Reflection (Anti-glare sheen)
        glass = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glass)
        g_draw.polygon([
            (frame_width, frame_width), 
            (int(fw * 0.45), frame_width), 
            (frame_width, int(fh * 0.55))
        ], fill=(255, 255, 255, 18))
        glass = glass.filter(ImageFilter.GaussianBlur(12))
        framed.paste(glass, (0, 0), glass)

        return framed

    def _create_photorealistic_living_room(self, art: Image.Image, frame_color: Tuple[int, int, int], mat_border: int) -> Image.Image:
        """Renders a warm, sunlit Scandinavian living room with natural oak herringbone floor & bouclé sofa."""
        w, h = 1600, 1200
        scene = Image.new("RGB", (w, h), (243, 239, 232))
        draw = ImageDraw.Draw(scene)

        # 1. Warm limewash plaster wall
        for y in range(840):
            t = y / 840.0
            r = int(246 - t * 8)
            g = int(242 - t * 8)
            b = int(236 - t * 8)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        # Plaster grain
        noise = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        n_draw = ImageDraw.Draw(noise)
        for _ in range(20000):
            nx = random.randint(0, w)
            ny = random.randint(0, 840)
            tone = random.choice([255, 210, 180])
            n_draw.point((nx, ny), fill=(tone, tone, tone, random.randint(4, 16)))
        scene.paste(noise, (0, 0), noise)

        # 2. European Herringbone Natural Oak Wood Planks
        floor_y = 810
        draw.rectangle([0, floor_y, w, h], fill=(188, 156, 126))
        for py in range(floor_y, h, 20):
            shade = random.randint(-10, 10)
            r = min(255, max(0, 188 + shade))
            g = min(255, max(0, 156 + shade))
            b = min(255, max(0, 126 + shade))
            draw.rectangle([0, py, w, py + 20], fill=(r, g, b))
            draw.line([(0, py), (w, py)], fill=(140, 110, 85), width=1)
            for px in range(0, w, 160):
                stagger = 80 if (py // 20) % 2 == 0 else 0
                draw.line([(px + stagger, py), (px + stagger, py + 20)], fill=(135, 105, 80), width=1)

        # Baseboard
        draw.rectangle([0, floor_y - 26, w, floor_y], fill=(248, 246, 240))
        draw.line([(0, floor_y - 26), (w, floor_y - 26)], fill=(210, 205, 195), width=1)
        draw.line([(0, floor_y), (w, floor_y)], fill=(120, 95, 70), width=2)

        # 3. Modern Bouclé Sofa
        sofa_l, sofa_r = 180, 1420
        sofa_t = 710
        # Floor contact shadow
        sofa_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(sofa_shadow)
        s_draw.ellipse([sofa_l - 40, floor_y - 20, sofa_r + 40, floor_y + 90], fill=(30, 25, 20, 140))
        sofa_shadow = sofa_shadow.filter(ImageFilter.GaussianBlur(25))
        scene.paste(sofa_shadow, (0, 0), sofa_shadow)

        # Sofa structure
        _draw_rounded_rect(draw, [sofa_l, sofa_t, sofa_r, floor_y + 120], radius=45, fill=(232, 226, 216))
        _draw_rounded_rect(draw, [sofa_l + 25, sofa_t + 45, sofa_r - 25, floor_y + 60], radius=28, fill=(238, 233, 224))
        _draw_rounded_rect(draw, [sofa_l + 45, sofa_t - 20, 770, floor_y - 10], radius=35, fill=(225, 218, 208))
        _draw_rounded_rect(draw, [790, sofa_t - 20, sofa_r - 45, floor_y - 10], radius=35, fill=(225, 218, 208))
        # Throw pillows
        _draw_rounded_rect(draw, [sofa_l + 80, sofa_t + 10, sofa_l + 240, sofa_t + 160], radius=20, fill=(195, 115, 82))
        _draw_rounded_rect(draw, [sofa_r - 250, sofa_t + 10, sofa_r - 90, sofa_t + 160], radius=20, fill=(120, 135, 118))

        # 4. Sunlit window beam
        sunlight = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sun_draw = ImageDraw.Draw(sunlight)
        sun_draw.polygon([(0, 0), (700, 0), (1200, floor_y + 200), (0, floor_y + 200)], fill=(255, 250, 235, 36))
        sunlight = sunlight.filter(ImageFilter.GaussianBlur(15))
        scene.paste(sunlight, (0, 0), sunlight)

        # 5. Potted Olive Tree in Corner
        plant = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(plant)
        pot_x, pot_y = 110, 710
        p_draw.polygon([(pot_x - 35, pot_y + 150), (pot_x + 35, pot_y + 150), (pot_x + 48, pot_y), (pot_x - 48, pot_y)], fill=(185, 105, 75, 240))
        p_draw.line([(pot_x, pot_y), (pot_x - 35, pot_y - 260)], fill=(75, 60, 45, 240), width=6)
        p_draw.line([(pot_x, pot_y - 80), (pot_x + 55, pot_y - 210)], fill=(75, 60, 45, 240), width=5)
        for lx, ly, wr, hr in [(pot_x - 55, pot_y - 270, 42, 24), (pot_x - 15, pot_y - 310, 48, 26), (pot_x + 65, pot_y - 230, 45, 25), (pot_x + 25, pot_y - 170, 40, 22)]:
            p_draw.ellipse([lx - wr, ly - hr, lx + wr, ly + hr], fill=(55, 78, 58, 230))
        plant = plant.filter(ImageFilter.GaussianBlur(1))
        scene.paste(plant, (0, 0), plant)

        # 6. Composite Framed Artwork above Sofa
        target_art_h = 430
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        framed = self._apply_realistic_frame(resized_art, frame_color, frame_width=18, mat_width=mat_border)

        fw, fh = framed.size
        fx = (w - fw) // 2
        fy = 210

        # Photorealistic dual-layer wall drop shadow
        wall_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ws_draw = ImageDraw.Draw(wall_shadow)
        # Deep contact shadow
        ws_draw.rectangle([fx + 4, fy + 8, fx + fw + 8, fy + fh + 12], fill=(20, 15, 10, 120))
        # Soft ambient diffuse shadow
        ws_draw.rectangle([fx + 12, fy + 20, fx + fw + 24, fy + fh + 32], fill=(30, 25, 20, 80))
        wall_shadow = wall_shadow.filter(ImageFilter.GaussianBlur(16))
        scene.paste(wall_shadow, (0, 0), wall_shadow)

        scene.paste(framed, (fx, fy))
        return scene

    def _create_photorealistic_bedroom(self, art: Image.Image, frame_color: Tuple[int, int, int], mat_border: int) -> Image.Image:
        """Renders a serene, cozy master bedroom with upholstered headboard & linen bedding."""
        w, h = 1600, 1200
        scene = Image.new("RGB", (w, h), (232, 230, 226))
        draw = ImageDraw.Draw(scene)

        # Darkened moody wall top gradient
        for y in range(750):
            t = y / 750.0
            r = int(225 - t * 10)
            g = int(223 - t * 10)
            b = int(218 - t * 10)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        # Architectural Upholstered Headboard
        hb_top = 700
        _draw_rounded_rect(draw, [220, hb_top, 1380, 1200], radius=30, fill=(65, 72, 78))
        # Down Pillows
        _draw_rounded_rect(draw, [300, hb_top - 65, 760, hb_top + 90], radius=22, fill=(245, 243, 238))
        _draw_rounded_rect(draw, [840, hb_top - 65, 1300, hb_top + 90], radius=22, fill=(245, 243, 238))
        # Linen Duvet with soft folds
        _draw_rounded_rect(draw, [180, hb_top + 50, 1420, 1200], radius=20, fill=(238, 234, 226))
        draw.rectangle([180, hb_top + 160, 1420, 1200], fill=(230, 225, 215))

        # Artwork
        target_art_h = 410
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        framed = self._apply_realistic_frame(resized_art, frame_color, frame_width=16, mat_width=mat_border)

        fw, fh = framed.size
        fx = (w - fw) // 2
        fy = 175

        # Drop shadow
        wall_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ws_draw = ImageDraw.Draw(wall_shadow)
        ws_draw.rectangle([fx + 8, fy + 14, fx + fw + 16, fy + fh + 22], fill=(15, 15, 20, 120))
        wall_shadow = wall_shadow.filter(ImageFilter.GaussianBlur(14))
        scene.paste(wall_shadow, (0, 0), wall_shadow)

        scene.paste(framed, (fx, fy))
        return scene

    def _create_photorealistic_studio(self, art: Image.Image, frame_color: Tuple[int, int, int], mat_border: int) -> Image.Image:
        """Renders an airy architectural studio with polished concrete and travertine console."""
        w, h = 1600, 1200
        scene = Image.new("RGB", (w, h), (244, 242, 238))
        draw = ImageDraw.Draw(scene)

        # Polished Concrete Floor
        floor_y = 900
        draw.rectangle([0, floor_y, w, h], fill=(215, 212, 208))
        draw.line([(0, floor_y), (w, floor_y)], fill=(185, 180, 175), width=2)

        # Minimalist Travertine Console Table
        _draw_rounded_rect(draw, [260, 780, 1340, 900], radius=8, fill=(228, 222, 212))
        # Fluted Legs
        draw.rectangle([340, 900, 420, 1080], fill=(218, 210, 200))
        draw.rectangle([1180, 900, 1260, 1080], fill=(218, 210, 200))

        # Stoneware Ceramic Vase with Dried Botanical Fronds
        vase_x, vase_y = 380, 710
        draw.ellipse([vase_x - 30, vase_y, vase_x + 30, vase_y + 80], fill=(245, 242, 235))
        draw.rectangle([vase_x - 12, vase_y - 25, vase_x + 12, vase_y], fill=(245, 242, 235))
        # Dried Frond
        draw.line([(vase_x, vase_y - 25), (vase_x - 40, vase_y - 180)], fill=(160, 140, 115), width=3)
        draw.line([(vase_x, vase_y - 25), (vase_x + 30, vase_y - 150)], fill=(160, 140, 115), width=3)

        # Artwork
        target_art_h = 440
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        framed = self._apply_realistic_frame(resized_art, frame_color, frame_width=18, mat_width=mat_border)

        fw, fh = framed.size
        fx = (w - fw) // 2
        fy = 190

        # Drop shadow
        wall_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ws_draw = ImageDraw.Draw(wall_shadow)
        ws_draw.rectangle([fx + 10, fy + 18, fx + fw + 20, fy + fh + 28], fill=(25, 25, 30, 95))
        wall_shadow = wall_shadow.filter(ImageFilter.GaussianBlur(15))
        scene.paste(wall_shadow, (0, 0), wall_shadow)

        scene.paste(framed, (fx, fy))
        return scene

    def _create_gallery_framed_shot(self, art: Image.Image, frame_color: Tuple[int, int, int]) -> Image.Image:
        """High-resolution neutral museum gallery wall shot."""
        w, h = 1600, 1600
        scene = Image.new("RGB", (w, h), (246, 244, 240))

        target_art_h = 980
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        framed = self._apply_realistic_frame(resized_art, frame_color, frame_width=32, mat_width=60)

        fw, fh = framed.size
        fx = (w - fw) // 2
        fy = (h - fh) // 2

        # Soft realistic floating shadow
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([fx + 18, fy + 26, fx + fw + 28, fy + fh + 36], fill=(20, 20, 25, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(26))
        scene.paste(shadow, (0, 0), shadow)

        scene.paste(framed, (fx, fy))
        return scene

mockup_agent = MockupAgent()
