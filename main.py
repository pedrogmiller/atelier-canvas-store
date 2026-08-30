import sys
import argparse

# Set UTF-8 encoding for Windows terminal compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import settings
from pipeline.orchestrator import ArtPipelineOrchestrator
from storefront.app import get_catalog

console = Console(highlight=False, soft_wrap=True)


def run_generate(theme: str = None, custom_prompt: str = None):
    """Executes the multi-agent art creation & publishing pipeline."""
    orchestrator = ArtPipelineOrchestrator()
    orchestrator.run(theme_id=theme, custom_instruction=custom_prompt)

def run_generate_all():
    """Populates the catalog with high-ticket collections across all 5 seed aesthetics."""
    orchestrator = ArtPipelineOrchestrator()
    themes = [
        "japandi-minimalism",
        "bauhaus-geometric",
        "vintage-botanical",
        "mediterranean-coastal",
        "dark-academia-moody"
    ]
    for idx, t in enumerate(themes, 1):
        console.print(f"\n[bold gold1]=== Generating Collection {idx}/{len(themes)}: {t} ===[/bold gold1]")
        orchestrator.run(theme_id=t)

def display_catalog():
    """Prints active store inventory, retail prices, and profit margins."""
    catalog = get_catalog()
    if not catalog:
        console.print("[yellow]Catalog is currently empty. Run 'python main.py --generate' to create collections.[/yellow]")
        return

    table = Table(title="🏛️ Active Live Storefront Catalog", border_style="gold1")
    table.add_column("Collection Title", style="cyan bold")
    table.add_column("Aesthetic", style="magenta")
    table.add_column("Price Range", style="green")
    table.add_column("Variants", style="dim")
    table.add_column("Live URL", style="blue underline")

    for p in catalog:
        table.add_row(
            p["title"],
            p["aesthetic_name"],
            f"${p['starting_price']} - ${p['max_price']}",
            f"{len(p.get('variants', []))} frame/size options",
            f"{settings.store_url}/product/{p['id']}"
        )

    console.print(table)

def start_server():
    """Starts the FastAPI Web Storefront server."""
    console.print(Panel.fit(
        f"[bold gold1]🚀 Starting Atelier & Canvas Live D2C Web Storefront...[/bold gold1]\n\n"
        f"• [bold]Store URL:[/bold] [underline cyan]{settings.store_url}[/underline cyan]\n"
        f"• [bold]Stripe Checkout:[/bold] [green]Active[/green]\n"
        f"• [bold]Gelato Automated Fulfillment:[/bold] [green]Active (32 Country Hubs)[/green]\n"
        f"• Press [bold red]Ctrl+C[/bold red] to stop the server.",
        border_style="gold1"
    ))
    uvicorn.run(
        "storefront.app:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )

def run_batch_expansion(target: int = 28):
    """Scales the store to 28+ audited collections, master Etsy CSV, and 30-day marketing playbook."""
    from pipeline.batch_expander import BatchCatalogExpander
    expander = BatchCatalogExpander()
    expander.run_expansion(target_count=target)

def main():
    parser = argparse.ArgumentParser(description="Autonomous Wall Art Multi-Agent E-Commerce Engine & Storefront")
    parser.add_argument("--generate", action="store_true", help="Generate a new fine art collection with agents")
    parser.add_argument("--generate-all", action="store_true", help="Generate collections for all 5 core aesthetics")
    parser.add_argument("--expand", action="store_true", help="Expand store to 28+ audited art collections, master Etsy CSV, and 30-day marketing playbook")
    parser.add_argument("--theme", type=str, default=None, help="Specific aesthetic theme ID")
    parser.add_argument("--prompt", type=str, default=None, help="Custom prompt or interior brief instructions")
    parser.add_argument("--serve", action="store_true", help="Launch the live D2C web storefront server")
    parser.add_argument("--catalog", action="store_true", help="Display all live products and profit margins")

    args = parser.parse_args()

    if args.expand:
        run_batch_expansion()
    elif args.generate:
        run_generate(theme=args.theme, custom_prompt=args.prompt)
    elif args.generate_all:
        run_generate_all()
    elif args.catalog:
        display_catalog()
    elif args.serve:
        start_server()
    else:
        # Default: Show help and launch menu
        console.print(Panel.fit(
            "[bold gold1]ATELIER & CANVAS - Autonomous Wall Art Multi-Agent Engine[/bold gold1]\n\n"
            "Commands:\n"
            "  [cyan]python main.py --expand[/cyan]             Scale to 28+ audited collections + Master Etsy CSV + 30-Day Marketing Playbook\n"
            "  [cyan]python main.py --generate[/cyan]           Run agents to curate, frame, and publish a piece\n"
            "  [cyan]python main.py --serve[/cyan]              Launch live D2C web storefront with Stripe & Gelato\n"
            "  [cyan]python main.py --catalog[/cyan]            View live inventory, pricing, and profit breakdown\n",
            border_style="gold1"
        ))


if __name__ == "__main__":
    main()
