import json
import shutil
import csv
import logging
from pathlib import Path
from typing import Dict, Any, List
from config.settings import settings
from agents.base_agent import BaseAgent
from suppliers.pricing_models import ProductVariant

logger = logging.getLogger("StorefrontSyncAgent")

class StorefrontSyncAgent(BaseAgent):
    """Agent that synchronizes generated art collections into the live storefront catalog and exports CSVs."""

    def __init__(self):
        super().__init__(
            name="StorefrontSyncAgent",
            role_description="Catalog Systems Architect & E-Commerce Integration Manager"
        )
        self.catalog_file = settings.catalog_file
        self.static_products_dir = settings.storefront_dir / "static" / "products"
        self.static_products_dir.mkdir(parents=True, exist_ok=True)

    def publish_to_storefront(
        self,
        product_id: str,
        art_brief: Dict[str, Any],
        variants: List[ProductVariant],
        mockup_paths: Dict[str, str],
        master_art_path: Path,
        seo_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploys the product package into the live storefront web catalog."""
        # 1. Copy images into web static directory
        dest_product_dir = self.static_products_dir / product_id
        dest_product_dir.mkdir(parents=True, exist_ok=True)

        web_image_urls = {}
        # Copy master art
        dest_art = dest_product_dir / "master_art.jpg"
        shutil.copyfile(master_art_path, dest_art)
        web_image_urls["master_art"] = f"/static/products/{product_id}/master_art.jpg"

        # Copy mockups
        for key, val in mockup_paths.items():
            if isinstance(val, dict):
                web_image_urls[key] = {}
                for f_key, src_path in val.items():
                    dest_mockup = dest_product_dir / f"{key.replace('_frames', '')}_{f_key}.jpg"
                    shutil.copyfile(src_path, dest_mockup)
                    web_image_urls[key][f_key] = f"/static/products/{product_id}/{dest_mockup.name}"
            elif isinstance(val, (str, Path)):
                dest_mockup = dest_product_dir / f"{key}.jpg"
                shutil.copyfile(val, dest_mockup)
                web_image_urls[key] = f"/static/products/{product_id}/{key}.jpg"

        # 2. Build product document for web store
        hero_variant = next((v for v in variants if v.is_hero_recommendation), variants[0])
        min_price = min(v.retail_price for v in variants)
        max_price = max(v.retail_price for v in variants)

        # Build images dictionary
        images_dict = {
            "hero": web_image_urls.get("living_room_oak", web_image_urls.get("framed_product", f"/static/products/{product_id}/living_room_natural_oak.jpg")),
            "living_room": web_image_urls.get("living_room_oak", f"/static/products/{product_id}/living_room_natural_oak.jpg"),
            "corner": web_image_urls.get("corner_detail", f"/static/products/{product_id}/corner_natural_oak.jpg"),
            "corner_detail": web_image_urls.get("corner_detail", f"/static/products/{product_id}/corner_natural_oak.jpg"),
            "gallery_wall": web_image_urls.get("gallery_wall", f"/static/products/{product_id}/gallery_wall_natural_oak.jpg"),
            "framed_product": web_image_urls.get("framed_product", f"/static/products/{product_id}/framed_natural_oak.jpg"),
            "bedroom": web_image_urls.get("bedroom_black", f"/static/products/{product_id}/bedroom_black.jpg"),
            "studio": web_image_urls.get("studio_white", f"/static/products/{product_id}/studio_white.jpg"),
            "master_art": web_image_urls.get("master_art", f"/static/products/{product_id}/master_art.jpg")
        }
        if "living_room_frames" in web_image_urls:
            images_dict["living_room_frames"] = web_image_urls["living_room_frames"]
        if "corner_detail_frames" in web_image_urls:
            images_dict["corner_detail_frames"] = web_image_urls["corner_detail_frames"]
        if "gallery_wall_frames" in web_image_urls:
            images_dict["gallery_wall_frames"] = web_image_urls["gallery_wall_frames"]
        if "framed_detail_frames" in web_image_urls:
            images_dict["framed_detail_frames"] = web_image_urls["framed_detail_frames"]

        product_record = {
            "id": product_id,
            "title": art_brief.get("collection_title", "Gallery Fine Art Print"),
            "seo_title": seo_content.get("seo_title", ""),
            "aesthetic_id": art_brief.get("aesthetic_id", "contemporary"),
            "aesthetic_name": art_brief.get("aesthetic_name", "Contemporary Art"),
            "short_summary": seo_content.get("short_summary", ""),
            "story_and_concept": seo_content.get("story_and_concept", ""),
            "styling_tips": seo_content.get("styling_tips", ""),
            "specifications": seo_content.get("specifications", {}),
            "color_palette": art_brief.get("color_palette", []),
            "seo_tags": seo_content.get("seo_tags", []),
            "social_ad_caption": seo_content.get("social_ad_caption", ""),
            "starting_price": min_price,
            "max_price": max_price,
            "hero_price": hero_variant.retail_price,
            "hero_variant_id": hero_variant.variant_id,
            "images": images_dict,
            "variants": [v.model_dump() for v in variants]
        }

        # 3. Update live catalog JSON
        catalog_data = []
        if self.catalog_file.exists():
            try:
                with open(self.catalog_file, "r", encoding="utf-8") as f:
                    catalog_data = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read existing catalog, creating fresh one: {e}")
                catalog_data = []

        # Remove existing if same ID
        catalog_data = [p for p in catalog_data if p["id"] != product_id]
        catalog_data.insert(0, product_record)

        with open(self.catalog_file, "w", encoding="utf-8") as f:
            json.dump(catalog_data, f, indent=2)

        # 4. Generate Shopify & Etsy compatible CSV
        self._export_csv(product_record, variants)

        logger.info(f"[{self.name}] Successfully published '{product_record['title']}' to Web Storefront Catalog.")
        return product_record

    def _export_csv(self, product_record: Dict[str, Any], variants: List[ProductVariant]):
        """Generates Shopify and Etsy standard import CSV files."""
        prod_out_dir = settings.output_dir / product_record["id"]
        prod_out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Shopify Import CSV
        shopify_csv = prod_out_dir / "shopify_import.csv"
        with open(shopify_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags",
                "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
                "Variant SKU", "Variant Price", "Variant Requires Shipping"
            ])
            handle = product_record["id"]
            title = product_record["title"]
            body = f"<p>{product_record['short_summary']}</p><p>{product_record['story_and_concept']}</p>"
            tags = ", ".join(product_record["seo_tags"])

            for v in variants:
                writer.writerow([
                    handle, title, body, "Atelier & Canvas", "Wall Art", tags,
                    "Size", v.size_label, "Frame Style", v.frame_label,
                    v.gelato_sku, v.retail_price, "TRUE"
                ])

        # 2. Etsy Multi-Listing Import CSV
        etsy_csv = prod_out_dir / "etsy_import.csv"
        with open(etsy_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Title", "Description", "Price", "Quantity", "Tags", "Materials",
                "Shop Section", "Image 1 URL", "Image 2 URL", "Image 3 URL"
            ])
            hero_var = next((v for v in variants if v.is_hero_recommendation), variants[0])
            etsy_desc = (
                f"{product_record['seo_title']}\n\n"
                f"{product_record['short_summary']}\n\n"
                f"SPECIFICATIONS & CRAFTSMANSHIP:\n"
                f"• Paper: 250 gsm museum-grade archival matte paper\n"
                f"• Framing: Handcrafted FSC-certified solid natural oak wood\n"
                f"• Printing: 12-color fade-resistant Giclée pigment inks\n"
                f"• 72-Hour Delivery: Printed and framed locally in 32 global hubs\n\n"
                f"STYLING ADVICE:\n{product_record['styling_tips']}\n"
            )
            writer.writerow([
                product_record["seo_title"][:140],
                etsy_desc,
                hero_var.retail_price,
                999,
                ", ".join(product_record["seo_tags"][:13]),
                "Solid Natural Oak, Museum Archival Matte Paper 250 gsm, Giclee Pigment Inks",
                product_record["aesthetic_name"],
                f"{settings.store_url}{product_record['images'].get('living_room', '')}",
                f"{settings.store_url}{product_record['images'].get('bedroom', '')}",
                f"{settings.store_url}{product_record['images'].get('framed_product', '')}"
            ])

