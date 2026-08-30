import math
import random
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("MockupAgent")

try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = getattr(Image, "LANCZOS", getattr(Image, "ANTIALIAS", 1))

class MockupAgent(BaseAgent):
    """Virtual Interior Staging & Mockup Artist that composites art onto real photographic room backgrounds."""

    def __init__(self):
        super().__init__(
            name="MockupAgent",
            role_description="Virtual Interior Staging & Real Photo Mockup Artist"
        )
        self.template_dir = settings.base_dir / "assets" / "room_templates"

    def generate_mockups(self, art_image_path: Path, output_dir: Path, title: str) -> Dict[str, str]:
        """Generates 4 distinct mockups using authentic real photographic room backgrounds."""
        output_dir.mkdir(parents=True, exist_ok=True)
        art_img = Image.open(art_image_path).convert("RGB")

        mockup_files = {}

        # 1. Living Room Hero Scene on REAL Photography Background (Natural Oak Frame)
        m1_path = output_dir / "mockup_living_room_oak.jpg"
        m1_img = self._composite_on_real_room(
            art=art_img,
            template_filename="living_room_real.jpg",
            frame_color=(198, 155, 112), # Natural Oak
            target_h=450,
            pos_y=165,
            mat_border=36,
            frame_w=18
        )
        m1_img.save(m1_path, "JPEG", quality=94)
        mockup_files["living_room_oak"] = str(m1_path)

        # 2. Master Bedroom on REAL Photography Background (Matte Black Frame)
        m2_path = output_dir / "mockup_bedroom_black.jpg"
        m2_img = self._composite_on_real_room(
            art=art_img,
            template_filename="bedroom_real.jpg",
            frame_color=(28, 28, 30), # Matte Black
            target_h=430,
            pos_y=160,
            mat_border=30,
            frame_w=16
        )
        m2_img.save(m2_path, "JPEG", quality=94)
        mockup_files["bedroom_black"] = str(m2_path)

        # 3. Nordic Minimalist Studio on REAL Photography Background (White Wood Frame)
        m3_path = output_dir / "mockup_studio_white.jpg"
        m3_img = self._composite_on_real_room(
            art=art_img,
            template_filename="studio_real.jpg",
            frame_color=(244, 242, 238), # Nordic White
            target_h=440,
            pos_y=180,
            mat_border=38,
            frame_w=18
        )
        m3_img.save(m3_path, "JPEG", quality=94)
        mockup_files["studio_white"] = str(m3_path)

        # 4. Pure Gallery Studio Framed Shot
        m4_path = output_dir / "mockup_framed_product.jpg"
        m4_img = self._create_gallery_framed_shot(art_img, frame_color=(198, 155, 112))
        m4_img.save(m4_path, "JPEG", quality=94)
        mockup_files["framed_product"] = str(m4_path)

        logger.info(f"[{self.name}] Generated 4 real photo room mockups in {output_dir}")
        return mockup_files

    def _apply_realistic_frame(self, art: Image.Image, frame_color: Tuple[int, int, int], frame_width: int = 18, mat_width: int = 36) -> Image.Image:
        """Adds archival museum matting, wood grain bevel highlights, and glass sheen."""
        # 1. Archival Matting
        if mat_width > 0:
            matted = ImageOps.expand(art, border=mat_width, fill=(248, 246, 240))
            m_draw = ImageDraw.Draw(matted)
            mw, mh = matted.size
            m_draw.rectangle([mat_width - 1, mat_width - 1, mw - mat_width, mh - mat_width], outline=(220, 215, 205), width=1)
        else:
            matted = art

        # 2. Wooden Frame Moulding
        framed = ImageOps.expand(matted, border=frame_width, fill=frame_color)
        fw, fh = framed.size
        f_draw = ImageDraw.Draw(framed)

        # 3. 3D Frame Bevel Highlights
        f_draw.line([(0, 0), (fw, 0)], fill=(255, 255, 255, 75), width=1)
        f_draw.line([(0, 0), (0, fh)], fill=(255, 255, 255, 75), width=1)
        f_draw.line([(0, fh - 1), (fw, fh - 1)], fill=(0, 0, 0, 85), width=1)
        f_draw.line([(fw - 1, 0), (fw - 1, fh)], fill=(0, 0, 0, 85), width=1)
        f_draw.rectangle([frame_width - 1, frame_width - 1, fw - frame_width, fh - frame_width], outline=(0, 0, 0, 100), width=2)

        # 4. Subtle Anti-glare Glass Reflection
        glass = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glass)
        g_draw.polygon([(frame_width, frame_width), (int(fw * 0.40), frame_width), (frame_width, int(fh * 0.50))], fill=(255, 255, 255, 16))
        glass = glass.filter(ImageFilter.GaussianBlur(10))
        framed.paste(glass, (0, 0), glass)

        return framed

    def _composite_on_real_room(
        self,
        art: Image.Image,
        template_filename: str,
        frame_color: Tuple[int, int, int],
        target_h: int = 440,
        pos_y: int = 170,
        mat_border: int = 36,
        frame_w: int = 18
    ) -> Image.Image:
        """Composites framed art with dual-layer wall drop shadows onto a real photographic room background."""
        template_path = self.template_dir / template_filename
        
        if template_path.exists():
            scene = Image.open(template_path).convert("RGB")
            scene = scene.resize((1600, 1200), RESAMPLE_FILTER)
        else:
            # Fallback warm studio wall if template is missing
            scene = Image.new("RGB", (1600, 1200), (242, 238, 232))

        sw, sh = scene.size

        # 1. Frame the art
        framed = self._apply_realistic_frame(art, frame_color, frame_width=frame_w, mat_width=mat_border)
        fw, fh = framed.size
        
        # 2. Scale framed art to fit wall
        aspect = fw / fh
        target_w = int(target_h * aspect)
        framed_scaled = framed.resize((target_w, target_h), RESAMPLE_FILTER)
        fw_s, fh_s = framed_scaled.size

        # 3. Position (Centered horizontally above furniture)
        fx = (sw - fw_s) // 2
        fy = pos_y

        # 4. Dual-layer Realistic Wall Drop Shadow
        shadow = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        # Sharp Contact Shadow
        s_draw.rectangle([fx + 4, fy + 8, fx + fw_s + 8, fy + fh_s + 12], fill=(15, 12, 10, 140))
        # Soft Ambient Diffuse Shadow
        s_draw.rectangle([fx + 10, fy + 18, fx + fw_s + 20, fy + fh_s + 28], fill=(25, 20, 15, 90))
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))

        # 5. Composite Shadow + Artwork onto Real Room Photo
        scene.paste(shadow, (0, 0), shadow)
        scene.paste(framed_scaled, (fx, fy))

        return scene

    def _create_gallery_framed_shot(self, art: Image.Image, frame_color: Tuple[int, int, int]) -> Image.Image:
        """High-resolution neutral gallery product shot."""
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

        # Soft floating shadow
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([fx + 18, fy + 26, fx + fw + 28, fy + fh + 36], fill=(20, 20, 25, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(26))
        scene.paste(shadow, (0, 0), shadow)

        scene.paste(framed, (fx, fy))
        return scene

mockup_agent = MockupAgent()
