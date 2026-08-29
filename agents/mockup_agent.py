import math
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("MockupAgent")

# Safe Pillow Resampling Filter for all Pillow versions
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
    """Agent that creates high-converting interior room mockups and framed product previews."""

    def __init__(self):
        super().__init__(
            name="MockupAgent",
            role_description="Virtual Interior Staging & 3D Mockup Artist"
        )


    def generate_mockups(self, art_image_path: Path, output_dir: Path, title: str) -> Dict[str, str]:
        """Generates 4 distinct lifestyle and framed product mockup images."""
        output_dir.mkdir(parents=True, exist_ok=True)
        art_img = Image.open(art_image_path).convert("RGB")

        mockup_files = {}

        # 1. Living Room Hero Scene (Natural Oak Frame)
        m1_path = output_dir / "mockup_living_room_oak.jpg"
        m1_img = self._create_living_room_mockup(art_img, frame_color=(198, 155, 112), mat_border=40)
        m1_img.save(m1_path, "JPEG", quality=92)
        mockup_files["living_room_oak"] = str(m1_path)

        # 2. Master Bedroom Scene (Matte Black Frame)
        m2_path = output_dir / "mockup_bedroom_black.jpg"
        m2_img = self._create_bedroom_mockup(art_img, frame_color=(28, 28, 30), mat_border=30)
        m2_img.save(m2_path, "JPEG", quality=92)
        mockup_files["bedroom_black"] = str(m2_path)

        # 3. Nordic Minimalist Studio (White Frame)
        m3_path = output_dir / "mockup_studio_white.jpg"
        m3_img = self._create_studio_mockup(art_img, frame_color=(240, 240, 242), mat_border=50)
        m3_img.save(m3_path, "JPEG", quality=92)
        mockup_files["studio_white"] = str(m3_path)

        # 4. Pure Framed Product Shot (Gallery Quality on Neutral Studio Wall)
        m4_path = output_dir / "mockup_framed_product.jpg"
        m4_img = self._create_clean_framed_shot(art_img, frame_color=(198, 155, 112))
        m4_img.save(m4_path, "JPEG", quality=92)
        mockup_files["framed_product"] = str(m4_path)

        logger.info(f"[{self.name}] Generated 4 lifestyle room mockups in {output_dir}")
        return mockup_files

    def _apply_frame(self, art: Image.Image, frame_color: Tuple[int, int, int], frame_width: int = 24, mat_width: int = 40) -> Image.Image:
        """Adds fine art matting, inner bevel, and solid wood frame with shadow."""
        # 1. Add white archival matting
        if mat_width > 0:
            matted = ImageOps.expand(art, border=mat_width, fill=(248, 247, 242))
        else:
            matted = art

        # 2. Add outer wooden frame border
        framed = ImageOps.expand(matted, border=frame_width, fill=frame_color)
        
        # 3. Add subtle bevel highlight on frame
        draw = ImageDraw.Draw(framed)
        w, h = framed.size
        # Outer light highlight
        draw.rectangle([0, 0, w - 1, h - 1], outline=(255, 255, 255, 60), width=1)
        # Inner depth shadow
        draw.rectangle([frame_width - 1, frame_width - 1, w - frame_width, h - frame_width], outline=(0, 0, 0, 80), width=2)
        return framed

    def _create_living_room_mockup(self, art: Image.Image, frame_color: Tuple[int, int, int], mat_border: int) -> Image.Image:
        """Composites framed art above a warm limewash wall with modern sofa."""
        canvas_w, canvas_h = 1600, 1200
        scene = Image.new("RGB", (canvas_w, canvas_h), (236, 230, 220)) # Warm limewash wall
        draw = ImageDraw.Draw(scene)

        # Floor: Warm European oak planks
        floor_y = 900
        draw.rectangle([0, floor_y, canvas_w, canvas_h], fill=(175, 142, 110))
        # Skirting board
        draw.rectangle([0, floor_y - 25, canvas_w, floor_y], fill=(245, 242, 236))

        # Modern Minimalist Bouclé Sofa
        sofa_top = 820
        sofa_left = 220
        sofa_right = 1380
        # Sofa back cushions
        _draw_rounded_rect(draw, [sofa_left, sofa_top, sofa_right, floor_y + 100], radius=35, fill=(225, 220, 210))
        _draw_rounded_rect(draw, [sofa_left + 40, sofa_top + 40, sofa_right - 40, floor_y + 60], radius=20, fill=(215, 208, 198))
        # Decorative cushion
        _draw_rounded_rect(draw, [sofa_left + 80, sofa_top + 20, sofa_left + 220, sofa_top + 160], radius=15, fill=(188, 110, 80))

        # Ambient window light beam
        light = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        light_draw = ImageDraw.Draw(light)
        light_draw.polygon([(0, 0), (900, 0), (1400, floor_y), (0, floor_y)], fill=(255, 252, 240, 25))
        scene.paste(light, (0, 0), light)

        # Frame and place the artwork above the sofa
        target_art_h = 460
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        framed = self._apply_frame(resized_art, frame_color, frame_width=18, mat_width=mat_border)

        # Frame Position (Centered above sofa)
        fw, fh = framed.size
        fx = (canvas_w - fw) // 2
        fy = 240

        # Drop shadow on wall
        shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([fx + 10, fy + 15, fx + fw + 18, fy + fh + 20], fill=(40, 35, 30, 95))
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        scene.paste(shadow, (0, 0), shadow)

        # Paste artwork
        scene.paste(framed, (fx, fy))
        return scene

    def _create_bedroom_mockup(self, art: Image.Image, frame_color: Tuple[int, int, int], mat_border: int) -> Image.Image:
        """Composites framed art above a peaceful linen headboard."""
        canvas_w, canvas_h = 1600, 1200
        scene = Image.new("RGB", (canvas_w, canvas_h), (228, 226, 222))
        draw = ImageDraw.Draw(scene)

        # Headboard (Minimalist upholstered)
        hb_top = 720
        _draw_rounded_rect(draw, [250, hb_top, 1350, 1200], radius=25, fill=(78, 85, 92))
        # Layered pillows
        _draw_rounded_rect(draw, [320, hb_top - 60, 750, hb_top + 100], radius=20, fill=(240, 238, 232))
        _draw_rounded_rect(draw, [850, hb_top - 60, 1280, hb_top + 100], radius=20, fill=(240, 238, 232))
        # Bed duvet
        draw.rectangle([200, hb_top + 60, 1400, 1200], fill=(235, 230, 222))

        # Artwork
        target_art_h = 420
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        framed = self._apply_frame(resized_art, frame_color, frame_width=16, mat_width=mat_border)

        fw, fh = framed.size
        fx = (canvas_w - fw) // 2
        fy = 180

        # Drop shadow
        shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([fx + 8, fy + 12, fx + fw + 14, fy + fh + 16], fill=(20, 20, 25, 100))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        scene.paste(shadow, (0, 0), shadow)

        scene.paste(framed, (fx, fy))
        return scene

    def _create_studio_mockup(self, art: Image.Image, frame_color: Tuple[int, int, int], mat_border: int) -> Image.Image:
        """Composites framed art in a clean architectural design studio with indoor plant."""
        canvas_w, canvas_h = 1600, 1200
        scene = Image.new("RGB", (canvas_w, canvas_h), (242, 240, 236))
        draw = ImageDraw.Draw(scene)

        # Floor: Polished concrete
        draw.rectangle([0, 950, canvas_w, canvas_h], fill=(210, 208, 204))

        # Modern Credenza / Console Table
        draw.rectangle([280, 820, 1320, 950], fill=(160, 130, 100))
        draw.line([(320, 950), (320, 1020)], fill=(40, 40, 40), width=6)
        draw.line([(1280, 950), (1280, 1020)], fill=(40, 40, 40), width=6)

        # Decorative ceramic vase on credenza
        draw.ellipse([380, 750, 450, 830], fill=(245, 240, 235))
        draw.rectangle([405, 710, 425, 755], fill=(245, 240, 235))

        # Frame art
        target_art_h = 440
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        framed = self._apply_frame(resized_art, frame_color, frame_width=18, mat_width=mat_border)

        fw, fh = framed.size
        fx = (canvas_w - fw) // 2
        fy = 220

        # Drop shadow
        shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([fx + 10, fy + 14, fx + fw + 16, fy + fh + 18], fill=(30, 30, 35, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        scene.paste(shadow, (0, 0), shadow)

        scene.paste(framed, (fx, fy))
        return scene

    def _create_clean_framed_shot(self, art: Image.Image, frame_color: Tuple[int, int, int]) -> Image.Image:
        """High-resolution neutral studio studio shot for product main thumbnail."""
        canvas_w, canvas_h = 1600, 1600
        scene = Image.new("RGB", (canvas_w, canvas_h), (246, 244, 240))

        target_art_h = 1000
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        framed = self._apply_frame(resized_art, frame_color, frame_width=32, mat_width=60)

        fw, fh = framed.size
        fx = (canvas_w - fw) // 2
        fy = (canvas_h - fh) // 2

        # Soft realistic floating shadow
        shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([fx + 16, fy + 24, fx + fw + 24, fy + fh + 32], fill=(20, 20, 25, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(24))
        scene.paste(shadow, (0, 0), shadow)

        scene.paste(framed, (fx, fy))
        return scene

