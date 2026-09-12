import math
import random
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance

from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("MockupAgent")

try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = getattr(Image, "LANCZOS", getattr(Image, "ANTIALIAS", 1))

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "assets" / "mockup_templates"

def _draw_rounded_rect(draw: ImageDraw.ImageDraw, box: List[int], radius: int, fill: Any):
    """Draws rounded rectangle if supported by Pillow, else falls back to standard rectangle."""
    if hasattr(draw, "rounded_rectangle"):
        draw.rounded_rectangle(box, radius=radius, fill=fill)
    else:
        draw.rectangle(box, fill=fill)


class MockupAgent(BaseAgent):
    """Virtual Interior Staging & 3D Architectural Mockup Director for Scandinavian Wall Art."""

    FRAME_CONFIGS = {
        "natural_oak": {
            "color": (218, 182, 142),
            "mat": 38,
            "frame_w": 18,
            "label": "Solid Natural Oak Wood",
            "corner_tpl": "corner_natural_oak_base.jpg"
        },
        "black_wood": {
            "color": (28, 28, 30),
            "mat": 38,
            "frame_w": 18,
            "label": "Matte Black Solid Wood",
            "corner_tpl": "corner_black_wood_base.jpg"
        },
        "white_wood": {
            "color": (242, 240, 236),
            "mat": 38,
            "frame_w": 18,
            "label": "Nordic White Wood",
            "corner_tpl": "corner_white_wood_base.jpg"
        },
        "canvas_wrap": {
            "color": (230, 225, 215),
            "mat": 0,
            "frame_w": 0,
            "label": "Stretched Canvas Wrap",
            "corner_tpl": "corner_natural_oak_base.jpg"
        },
        "unframed_poster": {
            "color": (248, 246, 240),
            "mat": 0,
            "frame_w": 0,
            "label": "Unframed Museum Matte Print",
            "corner_tpl": "corner_natural_oak_base.jpg"
        }
    }

    def __init__(self):
        super().__init__(
            name="MockupAgent",
            role_description="Virtual Interior Staging & 3D Architectural Mockup Director"
        )
        self.templates_dir = TEMPLATES_DIR

    def generate_mockups(self, art_image_path: Path, output_dir: Path, title: str) -> Dict[str, Any]:
        """Generates all 3 Minted gallery-grade staged views + studio detail shots across all frame styles."""
        output_dir.mkdir(parents=True, exist_ok=True)
        art_img = Image.open(art_image_path).convert("RGB")

        mockup_files = {
            "living_room_frames": {},
            "corner_detail_frames": {},
            "gallery_wall_frames": {},
            "framed_detail_frames": {}
        }

        # 1. SHOT 1: The Modernist Living Room / Credenza Scene (Wide Staged View)
        # Features: Painted cream credenza top, vinyl turntable on left, clay presepio in center, spacious right
        for f_key, cfg in self.FRAME_CONFIGS.items():
            lr_path = output_dir / f"mockup_living_room_{f_key}.jpg"
            lr_img = self._create_credenza_living_room_mockup(art_img, frame_type=f_key, cfg=cfg)
            lr_img.save(lr_path, "JPEG", quality=94)
            mockup_files["living_room_frames"][f_key] = str(lr_path)

        # 2. SHOT 2: The 45° Angled Corner & Frame Material Detail (Close-Up Shot)
        # Features: 4-point OpenCV perspective homography, authentic wood grain pores, 45° miter joint & floating recess
        for f_key, cfg in self.FRAME_CONFIGS.items():
            cd_path = output_dir / f"mockup_corner_{f_key}.jpg"
            cd_img = self._create_corner_detail_mockup(art_img, frame_type=f_key, cfg=cfg)
            cd_img.save(cd_path, "JPEG", quality=94)
            mockup_files["corner_detail_frames"][f_key] = str(cd_path)

        # 3. SHOT 3: Multi-Piece Gallery Wall Staging (Diptychs & Triptychs)
        # Features: Cohesive 2-piece side-by-side gallery wall staging with uniform 11 cm spacing
        for f_key, cfg in self.FRAME_CONFIGS.items():
            gw_path = output_dir / f"mockup_gallery_wall_{f_key}.jpg"
            gw_img = self._create_gallery_wall_mockup(art_img, frame_type=f_key, cfg=cfg)
            gw_img.save(gw_path, "JPEG", quality=94)
            mockup_files["gallery_wall_frames"][f_key] = str(gw_path)

        # 4. Clean Studio Framed Product Detail Shots for all 5 styles
        for f_key, cfg in self.FRAME_CONFIGS.items():
            fd_path = output_dir / f"mockup_framed_{f_key}.jpg"
            fd_img = self._create_clean_framed_shot(art_img, frame_type=f_key, cfg=cfg)
            fd_img.save(fd_path, "JPEG", quality=94)
            mockup_files["framed_detail_frames"][f_key] = str(fd_path)

        # 5. Master Bedroom Scene (Matte Black Frame)
        m2_path = output_dir / "mockup_bedroom_black.jpg"
        m2_img = self._create_bedroom_mockup(art_img, frame_color=(28, 28, 30), mat_border=30)
        m2_img.save(m2_path, "JPEG", quality=92)
        mockup_files["bedroom_black"] = str(m2_path)

        # 6. Nordic Minimalist Studio (White Wood Frame)
        m3_path = output_dir / "mockup_studio_white.jpg"
        m3_img = self._create_studio_mockup(art_img, frame_color=(242, 240, 236), mat_border=40)
        m3_img.save(m3_path, "JPEG", quality=92)
        mockup_files["studio_white"] = str(m3_path)

        # Defaults for backward compatibility
        mockup_files["living_room_oak"] = str(output_dir / "mockup_living_room_natural_oak.jpg")
        mockup_files["framed_product"] = str(output_dir / "mockup_framed_natural_oak.jpg")
        mockup_files["corner_detail"] = str(output_dir / "mockup_corner_natural_oak.jpg")
        mockup_files["gallery_wall"] = str(output_dir / "mockup_gallery_wall_natural_oak.jpg")

        logger.info(f"[{self.name}] Generated Minted-grade 3-shot gallery staging suite in {output_dir}")
        return mockup_files

    # -------------------------------------------------------------
    # SHOT 1: THE MODERNIST CREDENZA LIVING ROOM SCENE
    # -------------------------------------------------------------
    def _create_credenza_living_room_mockup(self, art: Image.Image, frame_type: str, cfg: Dict[str, Any]) -> Image.Image:
        """Composites framed artwork into the custom photographic Scandinavian credenza living room scene."""
        bg_template = self.templates_dir / "custom_credenza_living_room_base.jpg"
        if not bg_template.exists():
            return self._create_clean_framed_shot(art, frame_type, cfg)

        scene = Image.open(bg_template).convert("RGB")
        sw, sh = scene.size

        scale = sw / 1024.0
        x1 = int(499 * scale)
        y1 = int(114 * scale)
        x2 = int(733 * scale)
        y2 = int(472 * scale)
        pw = x2 - x1
        ph = y2 - y1

        resized_art = art.resize((pw, ph), RESAMPLE_FILTER)
        scene.paste(resized_art, (x1, y1))

        # Soft inner frame lip shadow & window light sheen
        shadow_overlay = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        s_np = np.zeros((sh, sw, 4), dtype=np.uint8)
        
        cv2.line(s_np, (x1, y1), (x2, y1), (0, 0, 0, 160), max(2, int(2 * scale)))
        cv2.line(s_np, (x1, y1), (x1, y2), (0, 0, 0, 160), max(2, int(2 * scale)))
        cv2.line(s_np, (x1, y2), (x2, y2), (255, 255, 255, 70), max(1, int(1 * scale)))
        cv2.line(s_np, (x2, y1), (x2, y2), (255, 255, 255, 70), max(1, int(1 * scale)))
        
        cv2.line(s_np, (x1 + int(20 * scale), y1), (x1 + int(pw * 0.45), y2), (255, 255, 255, 12), int(24 * scale))
        
        s_img = Image.fromarray(s_np).filter(ImageFilter.GaussianBlur(1.2 * scale))
        scene.paste(s_img, (0, 0), s_img)

        return scene.resize((1600, 1600), RESAMPLE_FILTER)

    # -------------------------------------------------------------
    # SHOT 2: THE 45° ANGLED CORNER MACRO DETAIL
    # -------------------------------------------------------------
    def _create_corner_detail_mockup(self, art: Image.Image, frame_type: str, cfg: Dict[str, Any]) -> Image.Image:
        """Warps art with OpenCV 4-point homography into the macro photographic 45° corner template."""
        tpl_name = cfg.get("corner_tpl", "corner_natural_oak_base.jpg")
        bg_template = self.templates_dir / tpl_name
        if not bg_template.exists():
            bg_template = self.templates_dir / "corner_natural_oak_base.jpg"

        if not bg_template.exists():
            return self._create_clean_framed_shot(art, frame_type, cfg)

        scene = Image.open(bg_template).convert("RGB")
        sw, sh = scene.size

        aw, ah = art.size
        crop_w = int(aw * 0.82)
        crop_h = int(ah * 0.82)
        art_crop = art.crop((0, 0, crop_w, crop_h)).resize((1800, 1800), RESAMPLE_FILTER)

        scale = sw / 2400.0
        dst_quad = np.float32([
            [-60 * scale, 365 * scale],
            [1654 * scale, 872 * scale],
            [1634 * scale, 2460 * scale],
            [-60 * scale, 2460 * scale]
        ])

        src_pts = np.float32([[0, 0], [1800, 0], [1800, 1800], [0, 1800]])
        H = cv2.getPerspectiveTransform(src_pts, dst_quad)

        art_np = np.array(art_crop)
        warped_art = cv2.warpPerspective(art_np, H, (sw, sh), flags=cv2.INTER_LANCZOS4)

        mask = np.zeros((sh, sw), dtype=np.uint8)
        cv2.fillConvexPoly(mask, dst_quad.astype(np.int32), 255)
        mask_pil = Image.fromarray(mask).filter(ImageFilter.GaussianBlur(1.0 * scale))

        scene.paste(Image.fromarray(warped_art), (0, 0), mask_pil)

        # Floating canvas recess shadow trench
        trench_np = np.zeros((sh, sw, 4), dtype=np.uint8)
        cv2.line(trench_np, (int(-60 * scale), int(365 * scale)), (int(1654 * scale), int(872 * scale)), (8, 6, 4, 185), max(4, int(6 * scale)))
        cv2.line(trench_np, (int(1654 * scale), int(872 * scale)), (int(1634 * scale), int(2460 * scale)), (8, 6, 4, 185), max(4, int(6 * scale)))
        trench_img = Image.fromarray(trench_np).filter(ImageFilter.GaussianBlur(2.5 * scale))
        scene.paste(trench_img, (0, 0), trench_img)

        return scene.resize((1600, 1600), RESAMPLE_FILTER)

    # -------------------------------------------------------------
    # SHOT 3: MULTI-PIECE GALLERY WALL STAGING (DIPTYCHS)
    # -------------------------------------------------------------
    def _create_gallery_wall_mockup(self, art: Image.Image, frame_type: str, cfg: Dict[str, Any]) -> Image.Image:
        """Composites a cohesive multi-piece gallery wall diptych above the credenza with uniform 11 cm spacing."""
        canvas_w, canvas_h = 1600, 1200
        scene = Image.new("RGB", (canvas_w, canvas_h), (239, 235, 227))

        draw = ImageDraw.Draw(scene)
        floor_y = 1000
        draw.rectangle([0, floor_y, canvas_w, canvas_h], fill=(185, 150, 115))
        draw.rectangle([0, floor_y - 20, canvas_w, floor_y], fill=(245, 242, 236))
        draw.line([(0, floor_y - 20), (canvas_w, floor_y - 20)], fill=(215, 210, 202), width=1)

        bench_w = 1260
        bench_h = 42
        bench_x = (canvas_w - bench_w) // 2
        bench_y = 865
        
        b_shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        bs_draw = ImageDraw.Draw(b_shadow)
        bs_draw.rectangle([bench_x + 8, bench_y + 16, bench_x + bench_w + 8, bench_y + bench_h + 16], fill=(20, 18, 15, 85))
        b_shadow = b_shadow.filter(ImageFilter.GaussianBlur(16))
        scene.paste(b_shadow, (0, 0), b_shadow)

        draw.rectangle([bench_x, bench_y, bench_x + bench_w, bench_y + bench_h], fill=(215, 180, 140))
        for blx in [bench_x + 90, bench_x + bench_w - 105]:
            draw.rectangle([blx, bench_y + bench_h, blx + 16, floor_y], fill=(30, 28, 26))

        vx = bench_x + bench_w - 190
        vy = bench_y - 85
        draw.ellipse([vx, vy, vx + 75, vy + 90], fill=(188, 112, 85))
        draw.rectangle([vx + 24, vy - 16, vx + 52, vy + 12], fill=(188, 112, 85))

        target_art_h = 490
        aspect = art.width / art.height
        target_art_w = int(target_art_h * aspect)

        p1 = art.resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        p2 = art.transpose(Image.Transpose.FLIP_LEFT_RIGHT).resize((target_art_w, target_art_h), RESAMPLE_FILTER)
        p2 = ImageEnhance.Color(p2).enhance(0.92)

        framed1 = self._apply_frame(p1, frame_type=frame_type, cfg=cfg, scale_ratio=0.8)
        framed2 = self._apply_frame(p2, frame_type=frame_type, cfg=cfg, scale_ratio=0.8)

        fw1, fh1 = framed1.size
        fw2, fh2 = framed2.size

        wall_gap = 68
        total_pair_w = fw1 + wall_gap + fw2
        start_x = (canvas_w - total_pair_w) // 2
        art_y = 220

        shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([start_x + 14, art_y + 18, start_x + fw1 + 14, art_y + fh1 + 18], fill=(20, 18, 15, 95))
        s_draw.rectangle([start_x + fw1 + wall_gap + 14, art_y + 18, start_x + total_pair_w + 14, art_y + fh2 + 18], fill=(20, 18, 15, 95))
        shadow = shadow.filter(ImageFilter.GaussianBlur(20))
        scene.paste(shadow, (0, 0), shadow)

        scene.paste(framed1, (start_x, art_y))
        scene.paste(framed2, (start_x + fw1 + wall_gap, art_y))

        sunlight = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        sl_draw = ImageDraw.Draw(sunlight)
        sl_draw.polygon([(0, 0), (1000, 0), (1600, floor_y), (0, floor_y)], fill=(255, 252, 240, 20))
        scene.paste(sunlight, (0, 0), sunlight)

        return scene

    # -------------------------------------------------------------
    # CLEAN STUDIO & ARCHITECTURAL ROOM RENDERS
    # -------------------------------------------------------------
    def _apply_frame(self, art: Image.Image, frame_type: str, cfg: Dict[str, Any], scale_ratio: float = 1.0) -> Image.Image:
        """Applies solid wood moulding, archival matting, or canvas wrap depth."""
        frame_color = cfg["color"]
        mat_w = int(cfg["mat"] * scale_ratio)
        frame_w = int(cfg["frame_w"] * scale_ratio)

        if frame_type == "canvas_wrap":
            w, h = art.size
            canvas = ImageOps.expand(art, border=4, fill=(210, 205, 195))
            c_draw = ImageDraw.Draw(canvas)
            cw, ch = canvas.size
            c_draw.line([(0, 0), (cw, 0)], fill=(255, 255, 255, 90), width=2)
            c_draw.line([(0, ch - 1), (cw, ch - 1)], fill=(0, 0, 0, 90), width=2)
            c_draw.line([(cw - 1, 0), (cw - 1, ch)], fill=(0, 0, 0, 90), width=2)
            return canvas

        if frame_type == "unframed_poster":
            poster = ImageOps.expand(art, border=1, fill=(210, 205, 200))
            return poster

        # Framed with Matting
        if mat_w > 0:
            matted = ImageOps.expand(art, border=mat_w, fill=(248, 246, 240))
            m_draw = ImageDraw.Draw(matted)
            mw, mh = matted.size
            m_draw.rectangle([mat_w - 1, mat_w - 1, mw - mat_w, mh - mat_w], outline=(220, 215, 206), width=1)
        else:
            matted = art

        framed = ImageOps.expand(matted, border=frame_w, fill=frame_color)
        fw, fh = framed.size
        f_draw = ImageDraw.Draw(framed)

        # 3D Frame bevel
        f_draw.line([(0, 0), (fw, 0)], fill=(255, 255, 255, 110), width=1)
        f_draw.line([(0, 0), (0, fh)], fill=(255, 255, 255, 100), width=1)
        f_draw.line([(0, fh - 1), (fw, fh - 1)], fill=(0, 0, 0, 85), width=1)
        f_draw.line([(fw - 1, 0), (fw - 1, fh)], fill=(0, 0, 0, 85), width=1)
        f_draw.rectangle([frame_w - 1, frame_w - 1, fw - frame_w, fh - frame_w], outline=(0, 0, 0, 95), width=2)

        return framed

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

