import sys
import json
import csv
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any

# Set UTF-8 encoding for Windows terminal compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import settings
from pipeline.orchestrator import ArtPipelineOrchestrator
from storefront.app import get_catalog

logger = logging.getLogger("BatchExpander")
console = Console(highlight=False, soft_wrap=True)

class BatchCatalogExpander:
    """Orchestrates scaling the store to 25+ audited art collections, master Etsy/Shopify exports, and 30-day marketing playbook."""

    def __init__(self):
        self.orchestrator = ArtPipelineOrchestrator()
        self.marketing_dir = settings.base_dir / "marketing_playbook"
        self.pins_dir = self.marketing_dir / "pins"
        self.marketing_dir.mkdir(parents=True, exist_ok=True)
        self.pins_dir.mkdir(parents=True, exist_ok=True)

    def run_expansion(self, target_count: int = 28):
        """Runs batch generation across all styles until catalog reaches target count."""
        styles = self.orchestrator.trend_agent.catalog
        console.print(Panel.fit(
            f"[bold gold1]🚀 Starting Full Catalog Expansion to {target_count}+ Audited Art Collections...[/bold gold1]\n"
            f"[dim]Iterating across {len(styles)} interior design aesthetics with 6-point commercial audits & social kits[/dim]",
            border_style="gold1"
        ))

        generated_records = []
        current_catalog = get_catalog()
        existing_ids = {p["id"] for p in current_catalog}

        # 1. Generate across all styles
        for idx, style in enumerate(styles, 1):
            console.print(f"\n[bold cyan]=== [Collection {idx}/{len(styles)}] Aesthetic: {style['name']} ===[/bold cyan]")
            record = self.orchestrator.run(theme_id=style["id"])
            if record and record.get("status") != "rejected":
                generated_records.append(record)

        # 2. If needed, generate variations to exceed 25+
        iteration = 1
        while len(get_catalog()) < target_count and iteration <= 8:
            style = styles[iteration % len(styles)]
            console.print(f"\n[bold magenta]=== [Bonus Variation {iteration}] Curating Gallery Series: {style['name']} ===[/bold magenta]")
            record = self.orchestrator.run(theme_id=style["id"], custom_instruction="Gallery wall statement series with high-contrast minimalist balance.")
            if record and record.get("status") != "rejected":
                generated_records.append(record)
            iteration += 1

        total_products = get_catalog()
        console.print(f"\n[bold green]✅ Catalog Expansion Complete! Total active store collections: {len(total_products)}[/bold green]")

        # 3. Build Master Multi-Channel Exports (Etsy & Shopify)
        self.generate_master_channel_exports(total_products)

        # 4. Build 30-Day Social Marketing Playbook & Ready-to-Post Pins
        self.build_30_day_marketing_playbook(total_products)

        return total_products

    def generate_master_channel_exports(self, products: List[Dict[str, Any]]):
        """Builds master bulk import CSVs for Etsy and Shopify containing all products and variants."""
        console.print("\n[bold gold1]📦 Generating Master Multi-Channel Marketplace Exports...[/bold gold1]")

        # Master Etsy CSV
        master_etsy_path = settings.output_dir / "master_etsy_catalog_import.csv"
        with open(master_etsy_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Title", "Description", "Price", "Quantity", "Tags", "Materials",
                "Shop Section", "Image 1 URL", "Image 2 URL", "Image 3 URL", "SKU"
            ])
            for p in products:
                hero_var = next((v for v in p.get("variants", []) if v.get("is_hero_recommendation")), p.get("variants", [{}])[0])
                desc = (
                    f"{p.get('seo_title', p.get('title'))}\n\n"
                    f"{p.get('short_summary', '')}\n\n"
                    f"ABOUT THE COLLECTION:\n{p.get('story_and_concept', '')}\n\n"
                    f"MUSEUM CRAFTSMANSHIP & MATERIALS:\n"
                    f"• Paper: 250 gsm heavyweight museum-grade archival matte paper\n"
                    f"• Framing: Handcrafted FSC-certified solid natural oak and pine wood\n"
                    f"• Inks: 12-color Giclée pigment printing (100+ year anti-fade warranty)\n"
                    f"• Fast Delivery: Printed and framed locally in 32 global hubs for 48–72h fast delivery\n\n"
                    f"STYLING ADVICE:\n{p.get('styling_tips', '')}\n"
                )
                writer.writerow([
                    p.get("seo_title", p.get("title"))[:140],
                    desc,
                    hero_var.get("retail_price", 110.0),
                    999,
                    ", ".join(p.get("seo_tags", [])[:13]),
                    "Solid Natural Oak, Museum Archival Matte Paper 250 gsm, Giclee Pigment Inks",
                    p.get("aesthetic_name", "Wall Art"),
                    f"{settings.store_url}{p['images'].get('living_room', '')}",
                    f"{settings.store_url}{p['images'].get('bedroom', '')}",
                    f"{settings.store_url}{p['images'].get('framed_product', '')}",
                    hero_var.get("gelato_sku", "")
                ])

        # Master Shopify CSV
        master_shopify_path = settings.output_dir / "master_shopify_catalog_import.csv"
        with open(master_shopify_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags",
                "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
                "Variant SKU", "Variant Price", "Variant Requires Shipping"
            ])
            for p in products:
                handle = p.get("id")
                title = p.get("title")
                body = f"<p>{p.get('short_summary', '')}</p><p>{p.get('story_and_concept', '')}</p>"
                tags = ", ".join(p.get("seo_tags", []))
                for v in p.get("variants", []):
                    writer.writerow([
                        handle, title, body, "Atelier & Canvas", "Wall Art", tags,
                        "Size", v.get("size_label", ""), "Frame Style", v.get("frame_label", ""),
                        v.get("gelato_sku", ""), v.get("retail_price", ""), "TRUE"
                    ])

        console.print(f"  [green]✓[/green] Master Etsy Bulk CSV: [dim]{master_etsy_path}[/dim]")
        console.print(f"  [green]✓[/green] Master Shopify Bulk CSV: [dim]{master_shopify_path}[/dim]")

    def build_30_day_marketing_playbook(self, products: List[Dict[str, Any]]):
        """Creates the complete 30-Day Pinterest & TikTok Marketing Playbook with scheduled pins."""
        console.print("\n[bold pink1]📅 Generating 30-Day Pinterest & TikTok Marketing Playbook...[/bold pink1]")

        calendar_md_path = self.marketing_dir / "30_DAY_MARKETING_PLAYBOOK.md"
        bulk_pins_csv_path = self.marketing_dir / "pinterest_bulk_upload_schedule.csv"

        schedule_entries = []
        csv_rows = [["Title", "Description", "Media URL", "Link", "Publish Date", "Board"]]

        # Build 30 Days of Scheduled Content
        days_content = []
        for day in range(1, 31):
            product = products[(day - 1) % len(products)]
            social_info = product.get("social_marketing", {}).get("pinterest_pin", {})
            reels_script = product.get("social_marketing", {}).get("tiktok_reels_scripts", [{}])[0]
            hashtags = " ".join(product.get("social_marketing", {}).get("hashtag_bundle", ["#homedecor", "#wallart", "#interiordesign"]))

            pin_title = social_info.get("title", f"How to Style {product.get('aesthetic_name')} | Atelier & Canvas")
            pin_desc = social_info.get("description", f"Elevate your sanctuary with '{product.get('title')}'. Museum-grade archival paper and handcrafted solid oak frames. 🚚 72h local worldwide shipping.")
            dest_url = f"{settings.store_url}/product/{product.get('id')}"

            # Copy pin image to marketing_playbook/pins/day_XX_pin.jpg
            source_pin = settings.output_dir / product.get("id") / "social_marketing" / "pinterest_pin_1000x1500.jpg"
            dest_pin_filename = f"day_{day:02d}_{product.get('aesthetic_id', 'art')}.jpg"
            dest_pin_path = self.pins_dir / dest_pin_filename

            if source_pin.exists():
                shutil.copyfile(source_pin, dest_pin_path)
            elif (settings.storefront_dir / "static" / "products" / product.get("id") / "living_room_oak.jpg").exists():
                shutil.copyfile(settings.storefront_dir / "static" / "products" / product.get("id") / "living_room_oak.jpg", dest_pin_path)

            csv_rows.append([
                pin_title,
                f"{pin_desc}\n\n{hashtags}",
                f"{settings.store_url}/static/products/{product.get('id')}/living_room_oak.jpg",
                dest_url,
                f"Day {day} - 09:00 AM (Peak Pinterest Hours)",
                f"{product.get('aesthetic_name')} Home Decor"
            ])

            pin_link_url = str(dest_pin_path).replace("\\", "/")
            days_content.append(f"""### 📌 Day {day:02d}: {product.get('title')}
* **Category / Board**: `{product.get('aesthetic_name')} Decor`
* **Scheduled Posting Time**: `09:00 AM EST` or `07:30 PM EST` (Peak home decor browsing)
* **Target Piece**: [{product.get('title')}]({dest_url})
* **Saved Pin Image**: [`pins/{dest_pin_filename}`](file:///{pin_link_url})

#### 🖼️ Pinterest Pin Details
* **Pin Headline**: **{pin_title}**
* **Pin Caption**: {pin_desc}
* **Destination Link**: `{dest_url}`
* **Hashtags**: `{hashtags}`

#### 📱 TikTok / Instagram Reel Script Angle
* **Concept**: *{reels_script.get('concept', 'Aesthetic Room Transformation')}*
* **Video Hook (First 3s)**: *"{reels_script.get('hook', 'POV: You found the perfect statement wall art.')}"*
* **Visual Action**: *{reels_script.get('visual_flow', 'Close-up of solid oak wood grain texture, then pan out to styled living room wall in golden hour lighting.')}*
* **On-Screen Text**: `"{reels_script.get('on_screen_text', 'How to make your living room feel like a $5,000 designer sanctuary ✨')}"`
* **Suggested Sound**: `{reels_script.get('suggested_audio', 'Warm Acoustic Ambient / Lofi Home Aesthetic')}`

---
""")

        pins_dir_url = str(self.pins_dir).replace("\\", "/")
        # Write Markdown Playbook
        with open(calendar_md_path, "w", encoding="utf-8") as f:
            f.write(f"""# 📅 30-Day Pinterest & TikTok Organic Launch Playbook
**Brand**: Atelier & Canvas | Curated Fine Art & Gallery Frames
**Total Active Store Collections**: {len(products)} Fine Art Pieces
**Storefront URL**: [{settings.store_url}]({settings.store_url})

---

## 🎯 How to Use This Playbook (No Password Access Needed)

1. **All Ready-to-Post Pin Graphics (1000x1500 px)** are pre-generated in:
   [`C:/Users/pedro/.gemini/antigravity/scratch/art_ecommerce_agents/marketing_playbook/pins`](file:///{pins_dir_url})
2. **Posting takes 1 minute per day**:
   - Go to your free Pinterest account $\\to$ click **Create Pin**.
   - Drag & drop the corresponding `day_XX.jpg` pin image from the `pins/` folder.
   - Copy & paste the pre-written Title, Description, and Destination Link from below.
   - Alternatively, use Pinterest's built-in **"Schedule for later"** feature to schedule 7–14 days in advance in 10 minutes!

---

## 🗓️ 30-Day Daily Posting Schedule

{''.join(days_content)}
""")


        # Write Pinterest Bulk Upload CSV
        with open(bulk_pins_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(csv_rows)

        console.print(f"  [green]✓[/green] 30-Day Marketing Playbook: [dim]{calendar_md_path}[/dim]")
        console.print(f"  [green]✓[/green] 30 Ready-to-Post Pins saved in: [dim]{self.pins_dir}[/dim]")
        console.print(f"  [green]✓[/green] Pinterest Bulk Schedule CSV: [dim]{bulk_pins_csv_path}[/dim]")

if __name__ == "__main__":
    expander = BatchCatalogExpander()
    expander.run_expansion(target_count=28)
