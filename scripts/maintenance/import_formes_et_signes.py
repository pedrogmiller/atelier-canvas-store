import sys
import json
import shutil
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from PIL import Image, ImageDraw, ImageOps, ImageFilter
from agents.mockup_agent import MockupAgent

# Load metadata
meta_file = Path("data/production/collection_01_formes_et_signes/collection_01_metadata.json")
with open(meta_file, "r", encoding="utf-8-sig") as f:
    meta = json.load(f)

collection_info = meta["collection"]
products_info = meta["products"]
bundles_info = meta["bundles"]

static_dir = Path("storefront/static/products")
static_dir.mkdir(parents=True, exist_ok=True)

mockup_agent = MockupAgent()

FRAME_MAP = [
    {"type": "unframed_poster", "label": "Museum-Grade Matte Fine Art Print (Unframed)", "suffix": "UNF"},
    {"type": "natural_oak", "label": "Solid Natural Oak Wood Frame", "suffix": "OAK"},
    {"type": "black_wood", "label": "Matte Black Solid Wood Frame", "suffix": "BLK"},
    {"type": "white_wood", "label": "Crisp White Solid Wood Frame", "suffix": "WHT"}
]

SIZES = [
    {
        "size": "30x40_cm",
        "size_label": "30x40 cm (12x16 in)",
        "sku_code": "30X40",
        "gelato_dim": "30x40-cm",
        "price_unframed": 35.0,
        "price_framed": 85.0,
        "base_cost_unframed": 6.5,
        "base_cost_framed": 18.5,
        "ship_est": 5.5
    },
    {
        "size": "50x70_cm",
        "size_label": "50x70 cm (20x28 in)",
        "sku_code": "50X70",
        "gelato_dim": "50x70-cm",
        "price_unframed": 55.0,
        "price_framed": 135.0,
        "base_cost_unframed": 11.5,
        "base_cost_framed": 28.5,
        "ship_est": 7.5
    },
    {
        "size": "70x100_cm",
        "size_label": "70x100 cm (28x40 in)",
        "sku_code": "70X100",
        "gelato_dim": "70x100-cm",
        "price_unframed": 85.0,
        "price_framed": 210.0,
        "base_cost_unframed": 18.5,
        "base_cost_framed": 45.0,
        "ship_est": 10.5
    }
]

def build_variants(base_sku, discount=0.0, is_bundle=False, bundle_count=1):
    variants = []
    for s_idx, s in enumerate(SIZES):
        for f in FRAME_MAP:
            f_type = f["type"]
            f_label = f["label"]
            f_suffix = f["suffix"]
            
            is_unframed = (f_type == "unframed_poster")
            raw_unit_price = s["price_unframed"] if is_unframed else s["price_framed"]
            raw_price = raw_unit_price * bundle_count
            retail_price = round(raw_price * (1.0 - discount), 2)
            
            base_cost = (s["base_cost_unframed"] if is_unframed else s["base_cost_framed"]) * bundle_count
            ship_cost = s["ship_est"] * (1.2 if bundle_count > 1 else 1.0)
            net_profit = round(retail_price - base_cost - ship_cost, 2)
            margin_pct = round((net_profit / retail_price) * 100, 1) if retail_price > 0 else 0
            
            if is_unframed:
                g_sku = f"poster_matte_{s['gelato_dim']}_250-gsm"
            elif f_type == "natural_oak":
                g_sku = f"framed-poster_flat_wood_natural_{s['gelato_dim']}_200-gsm"
            elif f_type == "black_wood":
                g_sku = f"framed-poster_flat_wood_black_{s['gelato_dim']}_200-gsm"
            else:
                g_sku = f"framed-poster_flat_wood_white_{s['gelato_dim']}_200-gsm"
            
            var_id = f"{f_type}_{s['size']}"
            is_hero = (s["size"] == "50x70_cm" and f_type == "natural_oak")
            
            variants.append({
                "variant_id": var_id,
                "size": s["size"],
                "size_label": s["size_label"],
                "frame_type": f_type,
                "frame_label": f_label,
                "gelato_sku": g_sku,
                "base_production_cost": base_cost,
                "shipping_cost_est": ship_cost,
                "retail_price": retail_price,
                "net_profit": net_profit,
                "profit_margin_pct": margin_pct,
                "is_hero_recommendation": is_hero
            })
    return variants

new_catalog_entries = []

# 1. Process 4 Single Products
for p in products_info:
    sku = p["sku"]
    title = p["title"]
    subtitle = p["subtitle"]
    desc = p["description"]
    palette = p["palette"]
    tags = p["tags"]
    raw_rel_path = Path(p["relative_path"])
    
    slug_name = title.lower().replace("'", "").replace(" ", "-").replace("é", "e").replace("è", "e")
    p_id = f"formes-et-signes-{slug_name}-{sku.lower().replace('_', '-')}"
    
    prod_static_dir = static_dir / p_id
    prod_static_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy master art
    master_art_dest = prod_static_dir / "master_art.jpg"
    shutil.copy(raw_rel_path, master_art_dest)
    
    # Generate mockups
    art_img = Image.open(master_art_dest).convert("RGB")
    
    # Living room frames
    for f_key, cfg in MockupAgent.FRAME_CONFIGS.items():
        lr_img = mockup_agent._create_living_room_mockup(art_img, frame_type=f_key, cfg=cfg)
        lr_img.save(prod_static_dir / f"living_room_{f_key}.jpg", "JPEG", quality=92)
        
        fd_img = mockup_agent._create_clean_framed_shot(art_img, frame_type=f_key, cfg=cfg)
        fd_img.save(prod_static_dir / f"framed_{f_key}.jpg", "JPEG", quality=92)
    
    # Legacy fallbacks
    shutil.copy(prod_static_dir / "living_room_natural_oak.jpg", prod_static_dir / "living_room_oak.jpg")
    shutil.copy(prod_static_dir / "framed_natural_oak.jpg", prod_static_dir / "framed_product.jpg")
    
    # Bedroom & Studio
    bed_img = mockup_agent._create_bedroom_mockup(art_img, frame_color=(28, 28, 30), mat_border=30)
    bed_img.save(prod_static_dir / "bedroom_black.jpg", "JPEG", quality=92)
    
    stu_img = mockup_agent._create_studio_mockup(art_img, frame_color=(242, 240, 236), mat_border=40)
    stu_img.save(prod_static_dir / "studio_white.jpg", "JPEG", quality=92)
    
    variants = build_variants(sku, discount=0.0)
    
    entry = {
        "id": p_id,
        "sku": sku,
        "title": f"Formes & Signes - {title} ({subtitle})",
        "seo_title": f"Formes & Signes: {title} | Scandinavian Modernist Wall Art, Archival Fine Art Print",
        "aesthetic_id": "formes-et-signes",
        "aesthetic_name": "Formes & Signes Collection",
        "collection_title": "Formes & Signes",
        "collection_subtitle": collection_info["subtitle"],
        "short_summary": f"Formes & Signes: {title} ({subtitle}). {desc}",
        "story_and_concept": f"{collection_info['curatorial_statement']} Rendered in {', '.join(palette)}.",
        "styling_tips": "A refined focal statement for mid-century modern, Scandinavian, and minimalist interiors. Pairs effortlessly with solid natural oak frames above a credenza or sofa.",
        "specifications": {
            "paper": collection_info["paper_spec"],
            "framing": "Sustainably sourced FSC-certified solid natural oak, black wood, or white wood with crystal-clear gallery acrylic",
            "printing": "12-color archival Giclée pigment printing with 100+ year fade-resistant guarantee",
            "fulfillment": "Locally printed and hand-framed across 32 regional global hubs for 48–72h fast delivery"
        },
        "color_palette": palette,
        "seo_tags": tags + ["formes & signes", "scandinavian art", "mid century print", "oak framed poster", "fine art giclee"],
        "social_ad_caption": f"Discover 'Formes & Signes: {title}'. Printed on 250 gsm archival museum matte paper in solid FSC-certified wood frames. 🚚 Fast localized shipping.",
        "starting_price": 35.0,
        "max_price": 210.0,
        "hero_price": 135.0,
        "hero_variant_id": "natural_oak_50x70_cm",
        "images": {
            "hero": f"/static/products/{p_id}/living_room_oak.jpg",
            "framed_product": f"/static/products/{p_id}/framed_product.jpg",
            "living_room": f"/static/products/{p_id}/living_room_oak.jpg",
            "bedroom": f"/static/products/{p_id}/bedroom_black.jpg",
            "studio": f"/static/products/{p_id}/studio_white.jpg",
            "master_art": f"/static/products/{p_id}/master_art.jpg",
            "living_room_frames": {
                "natural_oak": f"/static/products/{p_id}/living_room_natural_oak.jpg",
                "black_wood": f"/static/products/{p_id}/living_room_black_wood.jpg",
                "white_wood": f"/static/products/{p_id}/living_room_white_wood.jpg",
                "canvas_wrap": f"/static/products/{p_id}/living_room_canvas_wrap.jpg",
                "unframed_poster": f"/static/products/{p_id}/living_room_unframed_poster.jpg"
            },
            "framed_detail_frames": {
                "natural_oak": f"/static/products/{p_id}/framed_natural_oak.jpg",
                "black_wood": f"/static/products/{p_id}/framed_black_wood.jpg",
                "white_wood": f"/static/products/{p_id}/framed_white_wood.jpg",
                "canvas_wrap": f"/static/products/{p_id}/framed_canvas_wrap.jpg",
                "unframed_poster": f"/static/products/{p_id}/framed_unframed_poster.jpg"
            }
        },
        "variants": variants
    }
    new_catalog_entries.append(entry)
    print(f"Created product: {p_id}")

# 2. Process Curated Bundles
# Diptych (01 + 02)
art1 = Image.open("data/production/collection_01_formes_et_signes/01_lenvol_indigo.jpg").convert("RGB")
art2 = Image.open("data/production/collection_01_formes_et_signes/02_bleu_lunaire.jpg").convert("RGB")
art3 = Image.open("data/production/collection_01_formes_et_signes/03_ocre_cosmique.jpg").convert("RGB")

w, h = art1.size
gap = int(w * 0.08)
diptych_master = Image.new("RGB", (w * 2 + gap, h), (248, 246, 240))
diptych_master.paste(art1, (0, 0))
diptych_master.paste(art2, (w + gap, 0))

diptych_id = "formes-et-signes-signature-diptych-set-of-2"
diptych_dir = static_dir / diptych_id
diptych_dir.mkdir(parents=True, exist_ok=True)
diptych_master_path = diptych_dir / "master_art.jpg"
diptych_master.save(diptych_master_path, "JPEG", quality=92)

# Generate Diptych mockups
for f_key, cfg in MockupAgent.FRAME_CONFIGS.items():
    lr_img = mockup_agent._create_living_room_mockup(diptych_master, frame_type=f_key, cfg=cfg)
    lr_img.save(diptych_dir / f"living_room_{f_key}.jpg", "JPEG", quality=92)
    fd_img = mockup_agent._create_clean_framed_shot(diptych_master, frame_type=f_key, cfg=cfg)
    fd_img.save(diptych_dir / f"framed_{f_key}.jpg", "JPEG", quality=92)

shutil.copy(diptych_dir / "living_room_natural_oak.jpg", diptych_dir / "living_room_oak.jpg")
shutil.copy(diptych_dir / "framed_natural_oak.jpg", diptych_dir / "framed_product.jpg")
bed_img = mockup_agent._create_bedroom_mockup(diptych_master, frame_color=(28, 28, 30), mat_border=30)
bed_img.save(diptych_dir / "bedroom_black.jpg", "JPEG", quality=92)
stu_img = mockup_agent._create_studio_mockup(diptych_master, frame_color=(242, 240, 236), mat_border=40)
stu_img.save(diptych_dir / "studio_white.jpg", "JPEG", quality=92)

diptych_variants = build_variants("OPS-BUNDLE-FS-DIPTYCH", discount=0.15, is_bundle=True, bundle_count=2)

diptych_entry = {
    "id": diptych_id,
    "sku": "OPS-BUNDLE-FS-DIPTYCH",
    "title": "Formes & Signes - The Signature Diptych (Set of 2)",
    "seo_title": "The Signature Diptych (Set of 2) | Formes & Signes Curated Fine Art Set (15% Off)",
    "aesthetic_id": "formes-et-signes",
    "aesthetic_name": "Formes & Signes Collection",
    "collection_title": "Formes & Signes",
    "is_bundle": True,
    "bundle_items": ["OPS-FS-01", "OPS-FS-02"],
    "bundle_discount_pct": 15,
    "short_summary": "The Signature Diptych (Set of 2). The perfect dialogue of blues: pair L'Envol Indigo and Bleu Lunaire side-by-side with an automatic 15% bundle savings.",
    "story_and_concept": "Curated pairing of L'Envol Indigo and Bleu Lunaire. A harmonious study in smoked indigo, ultramarine cobalt, and Tuscan ochre on archival cotton rag paper.",
    "styling_tips": "Hang side-by-side with 10–15 cm spacing above a master bed, living room sectional, or dining sideboard.",
    "specifications": {
        "paper": collection_info["paper_spec"],
        "framing": "Includes 2 matched solid wood frames or unframed archival prints",
        "printing": "12-color archival Giclée pigment printing",
        "fulfillment": "Locally printed and packaged together across 32 regional global hubs"
    },
    "color_palette": ["Smoked Midnight Indigo", "Ultramarine Cobalt", "Tuscan Ochre", "Cadmium Accent", "Archival Ivory"],
    "seo_tags": ["diptych set of 2", "formes & signes", "paired prints", "gallery wall set", "blue wall art set"],
    "social_ad_caption": "Transform your space with The Signature Diptych (Set of 2). Enjoy 15% bundle savings on matched fine art prints. 🚚 Fast worldwide shipping.",
    "starting_price": 59.50,
    "max_price": 357.00,
    "hero_price": 229.50,
    "hero_variant_id": "natural_oak_50x70_cm",
    "images": {
        "hero": f"/static/products/{diptych_id}/living_room_oak.jpg",
        "framed_product": f"/static/products/{diptych_id}/framed_product.jpg",
        "living_room": f"/static/products/{diptych_id}/living_room_oak.jpg",
        "bedroom": f"/static/products/{diptych_id}/bedroom_black.jpg",
        "studio": f"/static/products/{diptych_id}/studio_white.jpg",
        "master_art": f"/static/products/{diptych_id}/master_art.jpg",
        "living_room_frames": {
            "natural_oak": f"/static/products/{diptych_id}/living_room_natural_oak.jpg",
            "black_wood": f"/static/products/{diptych_id}/living_room_black_wood.jpg",
            "white_wood": f"/static/products/{diptych_id}/living_room_white_wood.jpg",
            "canvas_wrap": f"/static/products/{diptych_id}/living_room_canvas_wrap.jpg",
            "unframed_poster": f"/static/products/{diptych_id}/living_room_unframed_poster.jpg"
        },
        "framed_detail_frames": {
            "natural_oak": f"/static/products/{diptych_id}/framed_natural_oak.jpg",
            "black_wood": f"/static/products/{diptych_id}/framed_black_wood.jpg",
            "white_wood": f"/static/products/{diptych_id}/framed_white_wood.jpg",
            "canvas_wrap": f"/static/products/{diptych_id}/framed_canvas_wrap.jpg",
            "unframed_poster": f"/static/products/{diptych_id}/framed_unframed_poster.jpg"
        }
    },
    "variants": diptych_variants
}
new_catalog_entries.append(diptych_entry)
print(f"Created bundle: {diptych_id}")

# Composite Triptych master art
triptych_master = Image.new("RGB", (w * 3 + gap * 2, h), (248, 246, 240))
triptych_master.paste(art1, (0, 0))
triptych_master.paste(art2, (w + gap, 0))
triptych_master.paste(art3, ((w + gap) * 2, 0))

triptych_id = "formes-et-signes-collectors-triptych-set-of-3"
triptych_dir = static_dir / triptych_id
triptych_dir.mkdir(parents=True, exist_ok=True)
triptych_master_path = triptych_dir / "master_art.jpg"
triptych_master.save(triptych_master_path, "JPEG", quality=92)

# Generate Triptych mockups
for f_key, cfg in MockupAgent.FRAME_CONFIGS.items():
    lr_img = mockup_agent._create_living_room_mockup(triptych_master, frame_type=f_key, cfg=cfg)
    lr_img.save(triptych_dir / f"living_room_{f_key}.jpg", "JPEG", quality=92)
    fd_img = mockup_agent._create_clean_framed_shot(triptych_master, frame_type=f_key, cfg=cfg)
    fd_img.save(triptych_dir / f"framed_{f_key}.jpg", "JPEG", quality=92)

shutil.copy(triptych_dir / "living_room_natural_oak.jpg", triptych_dir / "living_room_oak.jpg")
shutil.copy(triptych_dir / "framed_natural_oak.jpg", triptych_dir / "framed_product.jpg")
bed_img = mockup_agent._create_bedroom_mockup(triptych_master, frame_color=(28, 28, 30), mat_border=30)
bed_img.save(triptych_dir / "bedroom_black.jpg", "JPEG", quality=92)
stu_img = mockup_agent._create_studio_mockup(triptych_master, frame_color=(242, 240, 236), mat_border=40)
stu_img.save(triptych_dir / "studio_white.jpg", "JPEG", quality=92)

triptych_variants = build_variants("OPS-BUNDLE-FS-TRIPTYCH", discount=0.20, is_bundle=True, bundle_count=3)

triptych_entry = {
    "id": triptych_id,
    "sku": "OPS-BUNDLE-FS-TRIPTYCH",
    "title": "Formes & Signes - The Collector's Triptych (Set of 3)",
    "seo_title": "The Collector's Triptych (Set of 3) | Formes & Signes Complete Gallery Set (20% Off)",
    "aesthetic_id": "formes-et-signes",
    "aesthetic_name": "Formes & Signes Collection",
    "collection_title": "Formes & Signes",
    "is_bundle": True,
    "bundle_items": ["OPS-FS-01", "OPS-FS-02", "OPS-FS-03"],
    "bundle_discount_pct": 20,
    "short_summary": "The Collector's Triptych (Set of 3). The complete 3-piece gallery wall balance spanning midnight indigo, vibrant cobalt, and warm Tuscan ochre with 20% bundle savings.",
    "story_and_concept": "Curated 3-piece triptych combining L'Envol Indigo, Bleu Lunaire, and Ocre Cosmique for a full-room statement wall.",
    "styling_tips": "Mount as a linear triptych over large sofas, living room walls, or office reception spaces with 10–12 cm spacing.",
    "specifications": {
        "paper": collection_info["paper_spec"],
        "framing": "Includes 3 matched solid wood frames or unframed archival prints",
        "printing": "12-color archival Giclée pigment printing",
        "fulfillment": "Locally printed and packaged together across 32 regional global hubs"
    },
    "color_palette": ["Smoked Midnight Indigo", "Ultramarine Cobalt", "Tuscan Ochre", "Terracotta", "Archival Ivory"],
    "seo_tags": ["triptych set of 3", "formes & signes", "gallery wall set of 3", "large statement art", "modernist art set"],
    "social_ad_caption": "Complete your space with The Collector's Triptych (Set of 3). Unlock 20% gallery savings on museum-grade matched wall art. 🚚 Fast worldwide shipping.",
    "starting_price": 84.00,
    "max_price": 504.00,
    "hero_price": 324.00,
    "hero_variant_id": "natural_oak_50x70_cm",
    "images": {
        "hero": f"/static/products/{triptych_id}/living_room_oak.jpg",
        "framed_product": f"/static/products/{triptych_id}/framed_product.jpg",
        "living_room": f"/static/products/{triptych_id}/living_room_oak.jpg",
        "bedroom": f"/static/products/{triptych_id}/bedroom_black.jpg",
        "studio": f"/static/products/{triptych_id}/studio_white.jpg",
        "master_art": f"/static/products/{triptych_id}/master_art.jpg",
        "living_room_frames": {
            "natural_oak": f"/static/products/{triptych_id}/living_room_natural_oak.jpg",
            "black_wood": f"/static/products/{triptych_id}/living_room_black_wood.jpg",
            "white_wood": f"/static/products/{triptych_id}/living_room_white_wood.jpg",
            "canvas_wrap": f"/static/products/{triptych_id}/living_room_canvas_wrap.jpg",
            "unframed_poster": f"/static/products/{triptych_id}/living_room_unframed_poster.jpg"
        },
        "framed_detail_frames": {
            "natural_oak": f"/static/products/{triptych_id}/framed_natural_oak.jpg",
            "black_wood": f"/static/products/{triptych_id}/framed_black_wood.jpg",
            "white_wood": f"/static/products/{triptych_id}/framed_white_wood.jpg",
            "canvas_wrap": f"/static/products/{triptych_id}/framed_canvas_wrap.jpg",
            "unframed_poster": f"/static/products/{triptych_id}/framed_unframed_poster.jpg"
        }
    },
    "variants": triptych_variants
}
new_catalog_entries.append(triptych_entry)
print(f"Created bundle: {triptych_id}")

# 3. Update master storefront/catalog.json
catalog_file = Path("storefront/catalog.json")
with open(catalog_file, "r", encoding="utf-8") as f:
    existing_catalog = json.load(f)

# Filter out any old entries with same ids if present
new_ids = {e["id"] for e in new_catalog_entries}
filtered_catalog = [item for item in existing_catalog if item["id"] not in new_ids]

# Prepend new entries at the top
updated_catalog = new_catalog_entries + filtered_catalog

with open(catalog_file, "w", encoding="utf-8") as f:
    json.dump(updated_catalog, f, indent=2, ensure_ascii=False)

print(f"Catalog successfully updated! Total products now: {len(updated_catalog)} (Added {len(new_catalog_entries)} Formes & Signes products/bundles)")
