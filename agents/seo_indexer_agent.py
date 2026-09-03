import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET

from config.settings import settings
from agents.base_agent import BaseAgent

logger = logging.getLogger("SEOIndexerAgent")

class SEOIndexerAgent(BaseAgent):
    """
    Autonomous SEO & Indexing Agent.
    Generates sitemap.xml, robots.txt, and Google Rich Snippet JSON-LD Product Schemas
    to maximize search visibility across Google, Bing, and Pinterest search crawlers.
    """
    
    def __init__(self):
        super().__init__(
            name="SEOIndexerAgent",
            role_description="Autonomous search visibility, XML sitemaps, and Google Rich Snippets generator"
        )
        self.default_base_url = "https://www.oakprintstudio.com"

    def get_base_url(self, override_url: Optional[str] = None) -> str:
        """Determines the canonical live base URL."""
        if override_url:
            return override_url.rstrip("/")
        if settings.store_url and "localhost" not in settings.store_url:
            return settings.store_url.rstrip("/")
        return self.default_base_url

    def generate_sitemap_xml(self, catalog: List[Dict[str, Any]], base_url: Optional[str] = None) -> str:
        """
        Generates standard sitemaps.org compliant XML sitemap covering homepage and all catalog products.
        """
        domain = self.get_base_url(base_url)
        today = datetime.utcnow().strftime("%Y-%m-%d")

        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        # 1. Homepage
        home_url = ET.SubElement(urlset, "url")
        ET.SubElement(home_url, "loc").text = f"{domain}/"
        ET.SubElement(home_url, "lastmod").text = today
        ET.SubElement(home_url, "changefreq").text = "daily"
        ET.SubElement(home_url, "priority").text = "1.0"

        # 2. Key Policy & Guarantee Pages (Required for Merchant Verification)
        policy_routes = [
            ("/returns", "0.9"),
            ("/shipping", "0.8"),
            ("/privacy", "0.5"),
            ("/terms", "0.5"),
        ]
        for route, prio in policy_routes:
            pol_url = ET.SubElement(urlset, "url")
            ET.SubElement(pol_url, "loc").text = f"{domain}{route}"
            ET.SubElement(pol_url, "lastmod").text = today
            ET.SubElement(pol_url, "changefreq").text = "monthly"
            ET.SubElement(pol_url, "priority").text = prio

        # 3. Product Pages
        for item in catalog:
            p_id = item.get("id")
            if not p_id:
                continue
            
            p_url = ET.SubElement(urlset, "url")
            ET.SubElement(p_url, "loc").text = f"{domain}/product/{p_id}"
            ET.SubElement(p_url, "lastmod").text = today
            ET.SubElement(p_url, "changefreq").text = "weekly"
            ET.SubElement(p_url, "priority").text = "0.8"

        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_string = ET.tostring(urlset, encoding="utf-8", method="xml").decode("utf-8")
        return xml_declaration + xml_string

    def generate_robots_txt(self, base_url: Optional[str] = None) -> str:
        """
        Generates crawler instructions directing Googlebot, Bingbot, and Pinterestbot to sitemap.xml.
        """
        domain = self.get_base_url(base_url)
        return (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /api/checkout\n"
            "Disallow: /api/webhook\n"
            "\n"
            f"Sitemap: {domain}/sitemap.xml\n"
        )

    def generate_product_schema(self, product: Dict[str, Any], base_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates Google-compliant JSON-LD Product & Offer Schema for rich search results.
        """
        domain = self.get_base_url(base_url)
        p_id = product.get("id", "")
        title = product.get("title", "Archival Fine Art Print")
        description = product.get("description", "Museum-grade fine art print in handcrafted solid natural oak frame.")
        
        # Calculate pricing range
        starting_price = float(product.get("starting_price", 42.0))
        pricing_matrix = product.get("pricing_matrix", [])
        
        prices = [float(p.get("retail_price", starting_price)) for p in pricing_matrix if "retail_price" in p]
        high_price = max(prices) if prices else starting_price * 2.5
        
        # Image URL
        image_obj = product.get("images", {})
        hero_img = image_obj.get("hero", "")
        if hero_img and not hero_img.startswith("http"):
            hero_img = f"{domain}{hero_img}"

        return {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": title,
            "image": [hero_img] if hero_img else [],
            "description": description,
            "sku": p_id,
            "mpn": f"OPS-{p_id[:8].upper()}",
            "brand": {
                "@type": "Brand",
                "name": "OAK PRINT STUDIO"
            },
            "category": "Home & Garden > Decor > Artwork > Posters, Prints, & Visual Artwork",
            "material": "FSC-Certified Solid Natural Oak Wood & 250 gsm Museum Archival Paper",
            "offers": {
                "@type": "AggregateOffer",
                "url": f"{domain}/product/{p_id}",
                "priceCurrency": "USD",
                "lowPrice": f"{starting_price:.2f}",
                "highPrice": f"{high_price:.2f}",
                "offerCount": len(pricing_matrix) if pricing_matrix else 17,
                "priceValidUntil": "2027-12-31",
                "itemCondition": "https://schema.org/NewCondition",
                "availability": "https://schema.org/InStock",
                "seller": {
                    "@type": "Organization",
                    "name": "OAK PRINT STUDIO",
                    "url": domain
                }
            }
        }

    def save_static_files(self, catalog: List[Dict[str, Any]], target_dir: Optional[Path] = None):
        """Saves physical sitemap.xml and robots.txt files for static serving."""
        out_dir = target_dir or (settings.storefront_dir / "static")
        out_dir.mkdir(parents=True, exist_ok=True)
        
        sitemap_content = self.generate_sitemap_xml(catalog)
        with open(out_dir / "sitemap.xml", "w", encoding="utf-8") as f:
            f.write(sitemap_content)
            
        robots_content = self.generate_robots_txt()
        with open(out_dir / "robots.txt", "w", encoding="utf-8") as f:
            f.write(robots_content)
            
        logger.info(f"Generated static sitemap.xml ({len(catalog)} products) and robots.txt in {out_dir}")

seo_indexer_agent = SEOIndexerAgent()
