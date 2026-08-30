import os
import io
import math
import random
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, List
from PIL import Image, ImageDraw, ImageFilter
from config.settings import settings
from agents.base_agent import BaseAgent

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger("ArtGeneratorAgent")

class ArtGeneratorAgent(BaseAgent):
    """Fine art generator capable of creating unique compositions tailored to specific aesthetics."""

    def __init__(self):
        super().__init__(
            name="ArtGeneratorAgent",
            role_description="Fine Art Print Director & Generative Illustrator"
        )

    def generate_artwork(self, art_brief: Dict[str, Any], output_path: Path) -> Path:
        """Generates a master high-resolution artwork unique to its aesthetic."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        prompt = art_brief.get("hero_art_prompt", "Fine art abstract painting")
        
        # 1. Attempt generation via Gemini / Imagen API if available
        if self.client and GENAI_AVAILABLE:
            try:
                logger.info(f"[{self.name}] Calling Imagen Image Generation API...")
                result = self.client.models.generate_images(
                    model="imagen-3.0-generate-002",
                    prompt=prompt,
                    config=dict(
                        number_of_images=1,
                        aspect_ratio="3:4",
                        output_mime_type="image/jpeg",
                        person_generation="ALLOW_ADULT"
                    )
                )
                for generated_image in result.generated_images:
                    image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                    image.save(output_path, "JPEG", quality=95)
                    logger.info(f"[{self.name}] Saved master artwork via API: {output_path}")
                    return output_path
            except Exception as e:
                logger.warning(f"[{self.name}] Imagen API call failed or not enabled: {e}. Generating procedural fine art master.")

        # 2. Specialized Procedural Fine Art Engine based on Aesthetic
        image = self._render_aesthetic_specific_art(art_brief)
        image.save(output_path, "JPEG", quality=95)
        logger.info(f"[{self.name}] Rendered unique aesthetic artwork: {output_path}")
        return output_path

    def _render_aesthetic_specific_art(self, art_brief: Dict[str, Any], width: int = 2400, height: int = 3200) -> Image.Image:
        """Dispatches composition rendering based on aesthetic ID to ensure diverse visual styles."""
        aesthetic_id = art_brief.get("aesthetic_id", "japandi-minimalism")
        palette = self._get_palette_rgb(art_brief.get("color_palette", []))
        seed_val = abs(hash(art_brief.get("title", aesthetic_id))) % 100000
        rng = random.Random(seed_val)

        # Base Canvas Background
        bg_color = palette[0]
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Dispatch to specialized genre rendering
        if "botanical" in aesthetic_id or "herbarium" in aesthetic_id or "lemon" in aesthetic_id:
            self._render_botanical_composition(draw, width, height, palette, rng)
        elif "bauhaus" in aesthetic_id or "deco" in aesthetic_id:
            self._render_bauhaus_constructivist_composition(draw, width, height, palette, rng)
        elif "architectural" in aesthetic_id or "palm-springs" in aesthetic_id or "retro-futuristic" in aesthetic_id:
            self._render_architectural_schematic(draw, width, height, palette, rng)
        elif "celestial" in aesthetic_id:
            self._render_celestial_astronomy(draw, width, height, palette, rng)
        elif "ukiyo" in aesthetic_id or "sumi" in aesthetic_id:
            self._render_zen_woodblock_composition(draw, width, height, palette, rng)
        elif "watercolor" in aesthetic_id or "alpine" in aesthetic_id or "riviera" in aesthetic_id:
            self._render_landscape_horizons(draw, width, height, palette, rng)
        elif "line-art" in aesthetic_id:
            self._render_continuous_line_art(draw, width, height, palette, rng)
        elif "moroccan" in aesthetic_id or "terracotta" in aesthetic_id:
            self._render_moroccan_terracotta_arches(draw, width, height, palette, rng)
        elif "expressionist" in aesthetic_id or "plaster" in aesthetic_id:
            self._render_textured_impasto_composition(draw, width, height, palette, rng)
        else:
            self._render_japandi_stone_composition(draw, width, height, palette, rng)

        # Add rich linen archival texture
        self._apply_linen_texture(img, width, height, rng)
        return img

    def _render_botanical_composition(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws delicate botanical specimens, branching foliage, and leaf silhouettes."""
        stem_color = palette[4] if len(palette) > 4 else (58, 80, 61)
        leaf_color_1 = palette[1] if len(palette) > 1 else (118, 142, 126)
        leaf_color_2 = palette[2] if len(palette) > 2 else (204, 114, 82)
        accent_orb = palette[3] if len(palette) > 3 else (217, 163, 85)

        # Soft background sunburst / halo
        draw.ellipse([w//2 - 400, h//2 - 600, w//2 + 400, h//2 + 200], fill=accent_orb)

        # Main central branching stem
        cx = w // 2
        start_y = int(h * 0.85)
        end_y = int(h * 0.22)
        
        # Stem curve points
        points = []
        for i in range(10):
            t = i / 9.0
            cur_y = int(start_y - t * (start_y - end_y))
            cur_x = int(cx + math.sin(t * math.pi * 1.5) * 80)
            points.append((cur_x, cur_y))
        
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=stem_color, width=12)

        # Foliage Leaves
        num_leaves = 14
        for idx in range(num_leaves):
            t = (idx + 1) / (num_leaves + 2)
            cur_y = int(start_y - t * (start_y - end_y))
            cur_x = int(cx + math.sin(t * math.pi * 1.5) * 80)
            
            side = 1 if idx % 2 == 0 else -1
            leaf_w = rng.randint(220, 360)
            leaf_h = rng.randint(90, 140)
            leaf_x = cur_x + (side * (leaf_w // 2 + 20))
            color = leaf_color_1 if idx % 3 != 0 else leaf_color_2

            # Draw almond-shaped organic leaf
            draw.ellipse(
                [leaf_x - leaf_w//2, cur_y - leaf_h//2, leaf_x + leaf_w//2, cur_y + leaf_h//2],
                fill=color
            )
            # Branch connection
            draw.line([(cur_x, cur_y), (leaf_x, cur_y)], fill=stem_color, width=6)

    def _render_bauhaus_constructivist_composition(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws constructivist geometric color blocks, intersecting quadrants, and kinetic balance beams."""
        c1, c2, c3, c4 = palette[1], palette[2], palette[3], palette[4]

        # 1. Asymmetrical Large Color Field Quadrant
        draw.rectangle([int(w * 0.15), int(h * 0.15), int(w * 0.65), int(h * 0.60)], fill=c1)

        # 2. Bold Half-Circle Constructivist Arch
        draw.pieslice([int(w * 0.35), int(h * 0.40), int(w * 0.85), int(h * 0.90)], start=0, end=180, fill=c2)

        # 3. Floating Kinetic Balance Disc
        orb_r = int(w * 0.16)
        draw.ellipse([int(w * 0.68) - orb_r, int(h * 0.28) - orb_r, int(w * 0.68) + orb_r, int(h * 0.28) + orb_r], fill=c3)

        # 4. Diagonal Architectural Grid Beams
        draw.line([(int(w * 0.10), int(h * 0.75)), (int(w * 0.90), int(h * 0.30))], fill=c4, width=14)
        draw.line([(int(w * 0.25), int(h * 0.85)), (int(w * 0.75), int(h * 0.85))], fill=c1, width=8)

        # Small anchor square
        draw.rectangle([int(w * 0.18), int(h * 0.70), int(w * 0.28), int(h * 0.78)], fill=c3)

    def _render_architectural_schematic(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws cantilever architectural structures, isometric grids, and structural elevations."""
        c_slate = palette[1]
        c_warm = palette[2]
        c_accent = palette[3]
        line_color = palette[4]

        # Structural Terraces
        draw.rectangle([int(w * 0.20), int(h * 0.50), int(w * 0.80), int(h * 0.62)], fill=c_warm)
        draw.rectangle([int(w * 0.35), int(h * 0.35), int(w * 0.75), int(h * 0.50)], fill=c_slate)
        draw.rectangle([int(w * 0.15), int(h * 0.62), int(w * 0.85), int(h * 0.82)], fill=c_accent)

        # Cantilever Pillars
        for x_step in [0.25, 0.45, 0.65, 0.78]:
            px = int(w * x_step)
            draw.line([(px, int(h * 0.35)), (px, int(h * 0.82))], fill=line_color, width=6)

        # Horizon drafting gridlines
        for y_step in range(12, 90, 8):
            py = int(h * (y_step / 100.0))
            draw.line([(int(w * 0.10), py), (int(w * 0.90), py)], fill=(200, 190, 180), width=1)

        # Golden Ratio Arch
        draw.arc([int(w * 0.45), int(h * 0.15), int(w * 0.85), int(h * 0.55)], start=180, end=360, fill=line_color, width=5)

    def _render_celestial_astronomy(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws historical astronomical engravings, lunar phases, and orbital rings."""
        c_night, c_gold, c_star, c_line = palette[1], palette[2], palette[3], palette[4]
        cx, cy = w // 2, h // 2

        # Concentric Celestial Orbit Rings
        for r_ratio in [0.15, 0.26, 0.35, 0.42]:
            rad = int(w * r_ratio)
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=c_line, width=2)

        # Main Celestial Moon / Sun disc
        m_rad = int(w * 0.20)
        draw.ellipse([cx - m_rad, cy - m_rad, cx + m_rad, cy + m_rad], fill=c_night)

        # Crescent overlay in gold
        draw.pieslice([cx - m_rad, cy - m_rad, cx + m_rad, cy + m_rad], start=45, end=225, fill=c_gold)

        # Constellation Stars & Axes
        draw.line([(cx, int(h * 0.08)), (cx, int(h * 0.92))], fill=c_line, width=1)
        draw.line([(int(w * 0.08), cy), (int(w * 0.92), cy)], fill=c_line, width=1)

        # Random scatter star cluster
        for _ in range(40):
            sx = rng.randint(int(w * 0.15), int(w * 0.85))
            sy = rng.randint(int(h * 0.12), int(h * 0.88))
            sr = rng.randint(2, 6)
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=c_gold)

    def _render_zen_woodblock_composition(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws Japanese Zen Enso circle, tranquil misty mountain ridges, and moon silhouettes."""
        c_ink, c_mist, c_sun = palette[1], palette[3], palette[2]
        cx, cy = w // 2, int(h * 0.45)

        # Rising Red/Ochre Sun
        sun_r = int(w * 0.22)
        draw.ellipse([cx - sun_r, cy - int(h * 0.15) - sun_r, cx + sun_r, cy - int(h * 0.15) + sun_r], fill=c_sun)

        # Large Calligraphic Enso Circle
        enso_r = int(w * 0.32)
        draw.arc([cx - enso_r, cy - enso_r, cx + enso_r, cy + enso_r], start=20, end=330, fill=c_ink, width=42)

        # Layered mountain passes at bottom
        for idx, y_base in enumerate([0.72, 0.78, 0.85]):
            y_pos = int(h * y_base)
            points = [(0, h), (0, y_pos)]
            for step in range(1, 10):
                x_val = int(w * (step / 9.0))
                y_val = int(y_pos + math.sin(step + idx) * 90)
                points.append((x_val, y_val))
            points.append((w, h))
            draw.polygon(points, fill=c_mist if idx < 2 else c_ink)

    def _render_landscape_horizons(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws abstract flowing watercolor mountain strata and coastal horizons."""
        c_sky = palette[0]
        c_sun = palette[2]
        colors = [palette[1], palette[3], palette[4], palette[2]]

        # Radiant Sun on Horizon
        draw.ellipse([w//2 - 250, int(h * 0.28) - 250, w//2 + 250, int(h * 0.28) + 250], fill=c_sun)

        # 4 Layered Wave/Mountain Horizon Bands
        for i, c in enumerate(colors):
            y_start = int(h * (0.42 + i * 0.12))
            pts = [(0, h), (0, y_start)]
            for x_pct in range(0, 105, 10):
                px = int(w * (x_pct / 100.0))
                py = int(y_start + math.sin((x_pct / 15.0) + i) * (80 - i * 15))
                pts.append((px, py))
            pts.append((w, h))
            draw.polygon(pts, fill=c)

    def _render_continuous_line_art(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws fluid single-line abstract Matisse-style contour figures and organic vases."""
        c_bg_shape = palette[1]
        c_sub_shape = palette[2]
        line_color = palette[4]

        # Background abstract organic cutout shapes
        draw.ellipse([int(w * 0.20), int(h * 0.25), int(w * 0.70), int(h * 0.65)], fill=c_bg_shape)
        draw.ellipse([int(w * 0.45), int(h * 0.45), int(w * 0.85), int(h * 0.80)], fill=c_sub_shape)

        # Continuous fluid contour line
        cx, cy = w // 2, h // 2
        line_pts = [
            (cx - 180, int(h * 0.20)),
            (cx + 80, int(h * 0.25)),
            (cx + 160, int(h * 0.38)),
            (cx + 60, int(h * 0.48)),
            (cx - 120, int(h * 0.52)),
            (cx - 160, int(h * 0.65)),
            (cx + 40, int(h * 0.75)),
            (cx + 180, int(h * 0.82))
        ]
        for i in range(len(line_pts) - 1):
            draw.line([line_pts[i], line_pts[i+1]], fill=line_color, width=16)

    def _render_moroccan_terracotta_arches(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws concentric keyhole arches and terracotta courtyard perspectives."""
        c_terra, c_cobalt, c_stucco, c_dark = palette[1], palette[2], palette[3], palette[4]
        cx = w // 2

        # Outer Grand Arch
        draw.pieslice([int(w * 0.15), int(h * 0.15), int(w * 0.85), int(h * 0.70)], start=180, end=360, fill=c_terra)
        draw.rectangle([int(w * 0.15), int(h * 0.42), int(w * 0.85), int(h * 0.90)], fill=c_terra)

        # Inner Keyhole Recess
        draw.pieslice([int(w * 0.28), int(h * 0.26), int(w * 0.72), int(h * 0.68)], start=180, end=360, fill=c_stucco)
        draw.rectangle([int(w * 0.28), int(h * 0.47), int(w * 0.72), int(h * 0.90)], fill=c_stucco)

        # Courtyard Core Focal Point (Deep Ultramarine/Terracotta)
        draw.pieslice([int(w * 0.38), int(h * 0.36), int(w * 0.62), int(h * 0.60)], start=180, end=360, fill=c_cobalt)
        draw.rectangle([int(w * 0.38), int(h * 0.48), int(w * 0.62), int(h * 0.90)], fill=c_cobalt)

    def _render_textured_impasto_composition(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws dynamic palette knife horizontal impasto blocks and textural strokes."""
        c1, c2, c3, c4 = palette[1], palette[2], palette[3], palette[4]

        # 5 Layered Bold Horizontal Palette Knife Strokes
        strokes = [
            (0.18, 0.15, 0.82, 0.32, c1),
            (0.12, 0.35, 0.75, 0.50, c2),
            (0.25, 0.52, 0.88, 0.68, c3),
            (0.15, 0.70, 0.80, 0.84, c4)
        ]
        for x1_r, y1_r, x2_r, y2_r, col in strokes:
            draw.rectangle([int(w * x1_r), int(h * y1_r), int(w * x2_r), int(h * y2_r)], fill=col)

    def _render_japandi_stone_composition(self, draw: ImageDraw.ImageDraw, w: int, h: int, palette: list, rng: random.Random):
        """Draws balanced asymmetrical river stones and minimalist wabi-sabi balance."""
        c_stone1 = palette[1]
        c_stone2 = palette[2]
        c_stone3 = palette[3]
        line_color = palette[4]

        # 3 Stacked Organic Balancing River Stones
        cx = w // 2
        # Bottom Stone (Wide)
        draw.ellipse([cx - 380, int(h * 0.62), cx + 380, int(h * 0.80)], fill=c_stone1)
        # Middle Stone
        draw.ellipse([cx - 280, int(h * 0.44), cx + 260, int(h * 0.60)], fill=c_stone2)
        # Top Stone (Balanced)
        draw.ellipse([cx - 180, int(h * 0.28), cx + 180, int(h * 0.42)], fill=c_stone3)

        # Vertical Zen plum line
        draw.line([(cx + 220, int(h * 0.15)), (cx + 220, int(h * 0.85))], fill=line_color, width=4)

    def _apply_linen_texture(self, img: Image.Image, w: int, h: int, rng: random.Random):
        """Applies subtle fine art linen / cotton paper texture to the canvas."""
        grain = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        grain_draw = ImageDraw.Draw(grain)
        for _ in range(12000):
            gx = rng.randint(0, w)
            gy = rng.randint(0, h)
            alpha = rng.randint(6, 22)
            tone = rng.choice([255, 0])
            grain_draw.point((gx, gy), fill=(tone, tone, tone, alpha))
        img.paste(grain, (0, 0), grain)

    def _get_palette_rgb(self, palette_names: list) -> list:
        """Converts color names to harmonious RGB triplets."""
        color_map = {
            "Terracotta": (204, 114, 82),
            "Warm Ochre": (217, 163, 85),
            "Charcoal Slate": (54, 60, 68),
            "Muted Sage": (148, 161, 144),
            "Raw Linen": (244, 240, 232),
            "Sandstone": (230, 221, 207),
            "Deep Cobalt": (28, 62, 118),
            "Burnt Vermilion": (212, 63, 44),
            "Mustard Yellow": (224, 172, 42),
            "Matte Black": (32, 32, 34),
            "Warm Parchment": (246, 241, 230),
            "Forest Moss": (58, 80, 61),
            "Eucalyptus Green": (118, 142, 126),
            "Antique Sepia": (112, 84, 62),
            "Old Ivory": (247, 243, 233),
            "Dried Rose": (184, 125, 128),
            "Amalfi Ultramarine": (36, 75, 138),
            "Terracotta Clay": (195, 102, 73),
            "Sunlit Limewash": (248, 244, 234),
            "Deep Obsidian": (24, 25, 29),
            "Burnished Gold": (198, 153, 62),
            "Burgundy Wine": (108, 38, 48),
            "Espresso Umber": (60, 44, 37)
        }
        rgb_list = []
        for name in palette_names:
            if name in color_map:
                rgb_list.append(color_map[name])
        
        if len(rgb_list) < 5:
            rgb_list.extend([(244, 240, 232), (204, 114, 82), (54, 60, 68), (148, 161, 144), (45, 45, 45)])
        return rgb_list

art_generator_agent = ArtGeneratorAgent()
