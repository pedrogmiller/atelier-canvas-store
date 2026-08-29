import sys
import json
import uuid
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

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
from agents.trend_scout_agent import TrendScoutAgent
from agents.trend_auditor_agent import TrendAuditorAgent
from agents.art_generator_agent import ArtGeneratorAgent
from agents.supplier_sourcing_agent import SupplierSourcingAgent
from agents.mockup_agent import MockupAgent
from agents.listing_seo_agent import ListingSEOAgent
from agents.social_creative_agent import SocialCreativeAgent
from agents.storefront_sync_agent import StorefrontSyncAgent

logger = logging.getLogger("PipelineOrchestrator")
console = Console(highlight=False, soft_wrap=True)

class ArtPipelineOrchestrator:
    """Master orchestrator that coordinates the 8-agent multi-agent pipeline."""

    def __init__(self):
        self.trend_agent = TrendScoutAgent()
        self.auditor_agent = TrendAuditorAgent()
        self.art_agent = ArtGeneratorAgent()
        self.supplier_agent = SupplierSourcingAgent()
        self.mockup_agent = MockupAgent()
        self.seo_agent = ListingSEOAgent()
        self.social_agent = SocialCreativeAgent()
        self.storefront_agent = StorefrontSyncAgent()

    def run(self, theme_id: Optional[str] = None, custom_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Runs the entire multi-agent creation, auditing, marketing, and deployment pipeline."""
        console.print(Panel.fit(
            "[bold gold1]🎨 Launching Autonomous Wall Art Multi-Agent Pipeline...[/bold gold1]\n"
            f"[dim]Goal: Social Signals → Audit (>=8/10) → Art Gen → Supplier SKUs → Mockups → Social Ads → Live Store[/dim]",
            border_style="gold1"
        ))

        # 1. Trend & Interior Scout (Pinterest, TikTok, Etsy Signals)
        with console.status("[bold cyan]Step 1/8: TrendScoutAgent ingesting Pinterest & TikTok demand signals...[/bold cyan]"):
            art_brief = self.trend_agent.create_art_brief(theme_id, custom_instruction)
            title = art_brief.get("collection_title", "Gallery Artwork")
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
            product_id = f"{slug}-{uuid.uuid4().hex[:6]}"
            product_out_dir = settings.output_dir / product_id
            product_out_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"  [green]✓[/green] Art Concept Formulated: [bold]{title}[/bold] ([dim]{art_brief.get('aesthetic_name')}[/dim])")

        # 2. Commercial Demand & Viability Audit Gatekeeper
        with console.status("[bold yellow]Step 2/8: TrendAuditorAgent evaluating 6-point commercial scorecard...[/bold yellow]"):
            audit_report = self.auditor_agent.audit_art_brief(art_brief)
            score = audit_report.get("commercial_score", 0.0)
            is_approved = audit_report.get("is_approved", False)

            self._render_audit_scorecard(title, audit_report)

            if not is_approved:
                console.print(f"  [bold red]✗ REJECTED by TrendAuditorAgent[/bold red] (Score {score}/10 < Threshold {self.auditor_agent.PASS_THRESHOLD}/10). Halting production.")
                return {"status": "rejected", "audit_report": audit_report}
            
            console.print(f"  [bold green]✓ APPROVED by TrendAuditorAgent[/bold green] (Score [bold]{score}/10[/bold] - High Monetization Viability)")

        # 3. High-Res Artwork Generation
        with console.status("[bold magenta]Step 3/8: ArtGeneratorAgent rendering 300 DPI master print...[/bold magenta]"):
            master_art_path = product_out_dir / "master_artwork_300dpi.jpg"
            self.art_agent.generate_artwork(art_brief, master_art_path)
            console.print(f"  [green]✓[/green] Print-Ready Master Generated: [dim]{master_art_path.name}[/dim]")

        # 4. Supplier Sourcing & Margin Calculation (Gelato SKUs)
        with console.status("[bold yellow]Step 4/8: SupplierSourcingAgent evaluating Gelato SKUs & optimizing margins...[/bold yellow]"):
            variants = self.supplier_agent.build_product_variants(title)
            hero_var = next((v for v in variants if v.is_hero_recommendation), variants[0])
            console.print(
                f"  [green]✓[/green] Configured {len(variants)} Variants mapped to Gelato SKUs. "
                f"Hero (24x36 Oak): [bold green]${hero_var.retail_price}[/bold green] ([bold]${hero_var.net_profit} Profit / {hero_var.profit_margin_pct}% Margin[/bold])"
            )

        # 5. Room Mockup Compositing
        with console.status("[bold blue]Step 5/8: MockupAgent compositing framed artwork into luxury rooms...[/bold blue]"):
            mockup_dir = product_out_dir / "mockups"
            mockup_paths = self.mockup_agent.generate_mockups(master_art_path, mockup_dir, title)
            console.print(f"  [green]✓[/green] Rendered 4 Room Mockups (Living Room, Bedroom, Studio, Framed Product)")

        # 6. Listing Copy & SEO Tags
        with console.status("[bold green]Step 6/8: ListingSEOAgent drafting high-converting SEO copy and tags...[/bold green]"):
            seo_content = self.seo_agent.generate_listing_content(art_brief, variants)
            console.print(f"  [green]✓[/green] SEO Copy & {len(seo_content.get('seo_tags', []))} Keyword Tags Crafted")

        # 7. Social Creative & Pinterest/TikTok Ad Generation
        with console.status("[bold pink1]Step 7/8: SocialCreativeAgent rendering Pinterest Pin & TikTok scripts...[/bold pink1]"):
            social_package = self.social_agent.generate_social_package(
                product_id=product_id,
                art_brief=art_brief,
                mockup_path=mockup_paths.get("living_room_oak", master_art_path),
                output_dir=product_out_dir
            )
            console.print(f"  [green]✓[/green] Generated Vertical Pinterest Pin (1000x1500) & TikTok/Reels Launch Scripts")

        # 8. Web Storefront Sync & CSV Export
        with console.status("[bold gold1]Step 8/8: StorefrontSyncAgent publishing to live web store catalog...[/bold gold1]"):
            product_record = self.storefront_agent.publish_to_storefront(
                product_id=product_id,
                art_brief=art_brief,
                variants=variants,
                mockup_paths=mockup_paths,
                master_art_path=master_art_path,
                seo_content=seo_content
            )
            product_record["commercial_audit"] = audit_report
            product_record["social_marketing"] = social_package
            console.print(f"  [green]✓[/green] Published live to Web Storefront: [bold underline]{settings.store_url}/product/{product_id}[/bold underline]")

        # 9. Save Master Manifest
        manifest_path = product_out_dir / "product_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(product_record, f, indent=2)

        # Render Summary Table
        self._render_summary_table(product_record)

        return product_record

    def _render_audit_scorecard(self, title: str, audit: Dict[str, Any]):
        """Renders the 6-Point Commercial Viability Scorecard table."""
        scorecard = audit.get("scorecard", {})
        table = Table(title=f"📊 Commercial Viability Audit: {title}", border_style="yellow")
        table.add_column("Monetization Criterion", style="cyan")
        table.add_column("Score (0-10)", style="bold green")
        table.add_column("Benchmark Target", style="dim")

        benchmarks = {
            "buyer_purchase_intent": ">= 8.0 (Sanctuary / Living room decor)",
            "perceived_luxury_value": ">= 8.5 ($100+ framed perception)",
            "market_undersaturation": ">= 7.5 (Undersaturated demand)",
            "multi_cart_potential": ">= 8.0 (Gallery wall triptych pairing)",
            "trend_longevity": ">= 8.0 (6-12 month macro trend)",
            "ip_cleanliness": "10.0 (Zero trademark infringement)"
        }

        for metric, score in scorecard.items():
            readable_name = metric.replace("_", " ").title()
            benchmark = benchmarks.get(metric, ">= 8.0")
            table.add_row(readable_name, f"{score}/10", benchmark)

        table.add_section()
        table.add_row(
            "[bold]Overall Commercial Score[/bold]",
            f"[bold gold1]{audit.get('commercial_score')}/10[/bold gold1]",
            f"[bold]Pass Threshold: {self.auditor_agent.PASS_THRESHOLD}/10[/bold]"
        )
        console.print(table)

    def _render_summary_table(self, product: Dict[str, Any]):
        table = Table(title=f"🚀 Product Release Summary: {product['title']}", border_style="gold1")
        table.add_column("Size / Frame", style="cyan")
        table.add_column("Gelato SKU", style="dim")
        table.add_column("Landed Cost", style="red")
        table.add_column("Retail Price", style="green bold")
        table.add_column("Net Profit", style="gold1 bold")
        table.add_column("Margin %", style="magenta")

        for v in product["variants"][:6]:
            highlight = "⭐ " if v["is_hero_recommendation"] else "  "
            table.add_row(
                f"{highlight}{v['size_label']} - {v['frame_label']}",
                v["gelato_sku"][:25] + "...",
                f"${v['base_production_cost'] + v['shipping_cost_est']:.2f}",
                f"${v['retail_price']:.2f}",
                f"${v['net_profit']:.2f}",
                f"{v['profit_margin_pct']}%"
            )

        console.print(table)
        console.print(
            f"\n[bold green]✅ Ready for Sales![/bold green] Open your web storefront at: "
            f"[bold underline cyan]{settings.store_url}/product/{product['id']}[/bold underline cyan]\n"
        )
