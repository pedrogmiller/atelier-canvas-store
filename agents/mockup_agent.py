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

def _draw_rounded_rect(draw: ImageDraw.ImageDraw, box: List[int], radius: int, fill: Any):
    """Draws rounded rectangle if supported by Pillow, else falls back to standard rectangle."""
    if hasattr(draw, "rounded_rectangle"):
        draw.rounded_rectangle(box, radius=radius, fill=fill)
    else:
        draw.rectangle(box, fill=fill)

class MockupAgent(BaseAgent):
    """Virtual Interior Staging & Dynamic Multi-Frame Customizer Artist."""

    FRAME_CONFIGS = {
        "natural_oak": {"color": (198, 155, 112), "mat": 38, "frame_w": 18, "label": "Solid Natural Oak"},
        "black_wood": {"color": (28, 28, 30), "mat": 38, "frame_w": 18, "label": "Matte Black Solid Wood"},
        "white_wood": {"color": (242, 240, 236), "mat": 38, "frame_w": 18, "label": "Nordic White Wood"},
        "canvas_wrap": {"color": (230, 225, 215), "mat": 0, "frame_w": 0, "label": "Stretched Canvas Wrap"},
        "unframed_poster": {"color": (248, 246, 240), "mat": 0, "frame_w": 0, "label": "Unframed Matte Print"}
    }

    def __init__(self):
        super().__init__(
            name="MockupAgent",
            role_description="Virtual Interior Staging & Dynamic Multi-Frame Customizer Artist"
        )

    def generate_mockups(self, art_image_path: Path, output_dir: Path, title: str) -> Dict[str, Any]:
        """Generates real-time frame variations for living room and detail shots + bedroom & studio."""
        output_dir.mkdir(parents=True, exist_ok=True)
        art_img = Image.open(art_image_path).convert("RGB")

        mockup_files = {
            "living_room_frames": {},
            "framed_detail_frames": {}
        }

        # 1. Generate Living Room Staged Views for ALL 5 Frame Styles
        for f_key, cfg in self.FRAME_CONFIGS.items():
            lr_path = output_dir / f"mockup_living_room_{f_key}.jpg"
            lr_img = self._create_living_room_mockup(art_img, frame_type=f_key, cfg=cfg)
            lr_img.save(lr_path, "JPEG", quality=93)
            mockup_files["living_room_frames"][f_key] = str(lr_path)

        # 2. Generate Framed Detail Views for ALL 5 Frame Styles
        for f_key, cfg in self.FRAME_CONFIGS.items():
            fd_path = output_dir / f"mockup_framed_{f_key}.jpg"
            fd_img = self._create_clean_framed_shot(art_img, frame_type=f_key, cfg=cfg)
            fd_img.save(fd_path, "JPEG", quality=93)
            mockup_files["framed_detail_frames"][f_key] = str(fd_path)

        # 3. Master Bedroom Scene (Matte Black Frame)
        m2_path = output_dir / "mockup_bedroom_black.jpg"
        m2_img = self._create_bedroom_mockup(art_img, frame_color=(28, 28, 30), mat_border=30)
        m2_img.save(m2_path, "JPEG", quality=92)
        mockup_files["bedroom_black"] = str(m2_path)

        # 4. Nordic Minimalist Studio (White Wood Frame)
        m3_path = output_dir / "mockup_studio_white.jpg"
        m3_img = self._create_studio_mockup(art_img, frame_color=(242, 240, 236), mat_border=40)
        m3_img.save(m3_path, "JPEG", quality=92)
        mockup_files["studio_white"] = str(m3_path)

        # Defaults for backward compatibility
        mockup_files["living_room_oak"] = str(output_dir / "mockup_living_room_natural_oak.jpg")
        mockup_files["framed_product"] = str(output_dir / "mockup_framed_natural_oak.jpg")

        logger.info(f"[{self.name}] Generated multi-frame living room and detail mockups in {output_dir}")
        return mockup_files

    def _apply_frame(self, art: Image.Image, frame_type: str, cfg: Dict[str, Any], scale_ratio: float = 1.0) -> Image.Image:
        """Applies matting, frame moulding, or canvas wrap depth."""
        frame_color = cfg["color"]
        mat_w = int(cfg["mat"] * scale_ratio)
        frame_w = int(cfg["frame_w"] * scale_ratio)

        if frame_type == "canvas_wrap":
            # Frameless 3D canvas wrap with side bevel depth
            w, h = art.size
            canvas = ImageOps.expand(art, border=4, fill=(210, 205, 195))
            c_draw = ImageDraw.Draw(canvas)
            cw, ch = canvas.size
            # Bevel highlights
            c_draw.line([(0, 0), (cw, 0)], fill=(255, 255, 255, 90), width=2)
            c_draw.line([(0, ch - 1), (cw, ch - 1)], fill=(0, 0, 0, 90), width=2)
            c_draw.line([(cw - 1, 0), (cw - 1, ch)], fill=(0, 0, 0, 90), width=2)
            return canvas

        if frame_type == "unframed_poster":
            # Unframed pure matte paper
            w, h = art.size
            poster = ImageOps.expand(art, border=1, fill=(210, 205, 200))
            return poster

        # Framed with Matting
        if mat_w > 0:
            matted = ImageOps.expand(art, border=mat_w, fill=(248, 247, 242))
            m_draw = ImageDraw.Draw(matted)
            mw, mh = matted.size
            m_draw.rectangle([mat_w - 1, mat_w - 1, mw - mat_w, mh - mat_w], outline=(215, 210, 200), width=1)
        else:
            matted = art

        framed = ImageOps.expand(matted, border=frame_w, fill=frame_color)
        fw, fh = framed.size
        f_draw = ImageDraw.Draw(framed)

        # 3D Frame bevel
        f_draw.line([(0, 0), (fw, 0)], fill=(255, 255, 255, 75), width=1)
        f_draw.line([(0, 0), (0, fh)], fill=(255, 255, 255, 75), width=1)
        f_draw.line([(0, fh - 1), (fw, fh - 1)], fill=(0, 0, 0, 85), width=1)
        f_draw.line([(fw - 1, 0), (fw - 1, fh)], fill=(0, 0, 0, 85), width=1)
        f_draw.rectangle([frame_w - 1, frame_w - 1, fw - frame_w, fh - frame_w], outline=(0, 0, 0, 100), width=2)

        return framed

    def _create_living_room_mockup(self, art: Image.Image, frame_type: str, cfg: Dict[str, Any]) -> Image.Image:
        """Renders the Living Room scene with the specific frame style on the wall."""
        canvas_w, canvas_h = 1600, 1200
        scene = Image.new("RGB", (canvas_w, canvas_h), (236, 230, 220)) # Warm limewash wall
        draw = ImageDraw.Draw(scene)

        # Floor: Warm European oak planks
        floor_y = 900
        draw.rectangle([0, floor_y, canvas_w, canvas_h], fill=(175, 142, 110))
        draw.rectangle([0, floor_y - 25, canvas_w, floor_y], fill=(245, 242, 236))

        # Modern Minimalist Bouclé Sofa
        sofa_top = 820
        sofa_left = 220
        sofa_right = 1380
        _draw_rounded_rect(draw, [sofa_left, sofa_top, sofa_right, floor_y + 100], radius=35, fill=(225, 220, 210))
        _draw_rounded_rect(draw, [sofa_left + 40, sofa_top + 40, sofa_right - 40, floor_y + 60], radius=20, fill=(215, 208, 198))
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
        framed = self._apply_frame(resized_art, frame_type=frame_type, cfg=cfg, scale_ratio=0.7)

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

    def _create_clean_framed_shot(self, art: Image.Image, frame_type: str, cfg: Dict[str, Any]) -> Image.Image:
        """High-resolution gallery studio product shot for the specific frame."""
        canvas_w, canvas_h = 1600, 1600
        scene = Image.new("RGB", (canvas_w, canvas_h), (246, 244, 240))

        target_art_h = 980
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        framed = self._apply_frame(resized_art, frame_type=frame_type, cfg=cfg, scale_ratio=1.5)

        fw, fh = framed.size
        fx = (canvas_w - fw) // 2
        fy = (canvas_h - fh) // 2

        # Floating shadow
        shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([fx + 16, fy + 24, fx + fw + 24, fy + fh + 32], fill=(20, 20, 25, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(24))
        scene.paste(shadow, (0, 0), shadow)

        scene.paste(framed, (fx, fy))
        return scene

    def _create_bedroom_mockup(self, art: Image.Image, frame_color: Tuple[int, int, int], mat_border: int) -> Image.Image:
        """Composites framed art above a peaceful linen headboard."""
        canvas_w, canvas_h = 1600, 1200
        scene = Image.new("RGB", (canvas_w, canvas_h), (228, 226, 222))
        draw = ImageDraw.Draw(scene)

        hb_top = 720
        _draw_rounded_rect(draw, [250, hb_top, 1350, 1200], radius=25, fill=(78, 85, 92))
        _draw_rounded_rect(draw, [320, hb_top - 60, 750, hb_top + 100], radius=20, fill=(240, 238, 232))
        _draw_rounded_rect(draw, [850, hb_top - 60, 1280, hb_top + 100], radius=20, fill=(240, 238, 232))
        draw.rectangle([200, hb_top + 60, 1400, 1200], fill=(235, 230, 222))

        target_art_h = 420
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        
        cfg = {"color": frame_color, "mat": mat_border, "frame_w": 16}
        framed = self._apply_frame(resized_art, frame_type="black_wood", cfg=cfg, scale_ratio=0.7)

        fw, fh = framed.size
        fx = (canvas_w - fw) // 2
        fy = 180

        shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([fx + 8, fy + 12, fx + fw + 14, fy + fh + 16], fill=(20, 20, 25, 100))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        scene.paste(shadow, (0, 0), shadow)

        scene.paste(framed, (fx, fy))
        return scene

    def _create_studio_mockup(self, art: Image.Image, frame_color: Tuple[int, int, int], mat_border: int) -> Image.Image:
        """Composites framed art in a clean architectural design studio."""
        canvas_w, canvas_h = 1600, 1200
        scene = Image.new("RGB", (canvas_w, canvas_h), (242, 240, 236))
        draw = ImageDraw.Draw(scene)

        draw.rectangle([0, 950, canvas_w, canvas_h], fill=(210, 208, 204))
        draw.rectangle([280, 820, 1320, 950], fill=(160, 130, 100))
        draw.line([(320, 950), (320, 1020)], fill=(40, 40, 40), width=6)
        draw.line([(1280, 950), (1280, 1020)], fill=(40, 40, 40), width=6)

        draw.ellipse([380, 750, 450, 830], fill=(245, 240, 235))
        draw.rectangle([405, 710, 425, 755], fill=(245, 240, 235))

        target_art_h = 440
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)
        resized_art = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)

        cfg = {"color": frame_color, "mat": mat_border, "frame_w": 18}
        framed = self._apply_frame(resized_art, frame_type="white_wood", cfg=cfg, scale_ratio=0.7)

        fw, fh = framed.size
        fx = (canvas_w - fw) // 2
        fy = 220

        shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([fx + 10, fy + 14, fx + fw + 16, fy + fh + 18], fill=(30, 30, 35, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        scene.paste(shadow, (0, 0), shadow)

        scene.paste(framed, (fx, fy))
        return scene

mockup_agent = MockupAgent()
