import logging
from typing import List, Dict, Any
from config.settings import settings
from agents.base_agent import BaseAgent
from suppliers.pricing_models import (
    FrameType, ProductSize, ProductVariant
)
from suppliers.gelato_client import gelato_client

logger = logging.getLogger("SupplierSourcingAgent")

class SupplierSourcingAgent(BaseAgent):
    """Agent that analyzes POD supplier SKUs, calculates landed costs, and enforces profit margins."""

    def __init__(self):
        super().__init__(
            name="SupplierSourcingAgent",
            role_description="Chief Sourcing & Pricing Optimization Officer"
        )
        self.min_margin = settings.min_profit_margin_pct
        self.markup_multiplier = settings.default_markup_multiplier

    def build_product_variants(self, art_title: str) -> List[ProductVariant]:
        """Generates all profitable product variants mapped to Gelato SKUs."""
        variants: List[ProductVariant] = []

        size_configs = [
            (ProductSize.SIZE_12X18, "12x18 in (30x45 cm)"),
            (ProductSize.SIZE_18X24, "18x24 in (45x60 cm)"),
            (ProductSize.SIZE_24X36, "24x36 in (60x90 cm)"),
            (ProductSize.SIZE_30X40, "30x40 in (75x100 cm)"),
        ]

        frame_configs = [
            (FrameType.NATURAL_OAK, "Solid Natural Oak Wood Frame"),
            (FrameType.BLACK_WOOD, "Matte Black Solid Wood Frame"),
            (FrameType.WHITE_WOOD, "Nordic White Wood Frame"),
            (FrameType.CANVAS_WRAP, "Gallery Stretched Fine Art Canvas"),
            (FrameType.UNFRAMED_POSTER, "Museum-Grade Matte Fine Art Print (Unframed)"),
        ]

        for size, size_label in size_configs:
            for frame_type, frame_label in frame_configs:
                # White wood and Canvas wrap are offered on popular sizes 18x24 and 24x36
                if frame_type == FrameType.WHITE_WOOD and size not in [ProductSize.SIZE_18X24, ProductSize.SIZE_24X36]:
                    continue
                if frame_type == FrameType.CANVAS_WRAP and size == ProductSize.SIZE_12X18:
                    continue

                specs = gelato_client.get_catalog_specs(size, frame_type)
                base_cost = specs["base_cost"]
                shipping_est = specs["shipping"]
                sku = specs["sku"]

                # Landed Cost = Base Manufacturing + Domestic Shipping
                landed_cost = base_cost + shipping_est

                # Compute Smart Retail Price with charm rounding
                raw_retail = landed_cost * self.markup_multiplier
                # Round to clean .00 or .95
                retail_price = round(raw_retail)

                # Payment gateway fee estimate (Stripe: 2.9% + $0.30)
                stripe_fee = (retail_price * 0.029) + 0.30
                total_cost = landed_cost + stripe_fee
                net_profit = round(retail_price - total_cost, 2)
                margin_pct = round((net_profit / retail_price) * 100, 1)

                # Enforce profitability threshold
                if margin_pct < self.min_margin:
                    retail_price = round((total_cost / (1 - (self.min_margin / 100))) + 1)
                    stripe_fee = (retail_price * 0.029) + 0.30
                    net_profit = round(retail_price - (landed_cost + stripe_fee), 2)
                    margin_pct = round((net_profit / retail_price) * 100, 1)

                is_hero = (size == ProductSize.SIZE_24X36 and frame_type == FrameType.NATURAL_OAK)

                variant = ProductVariant(
                    variant_id=f"{frame_type.value}_{size.value}",
                    size=size,
                    size_label=size_label,
                    frame_type=frame_type,
                    frame_label=frame_label,
                    gelato_sku=sku,
                    base_production_cost=base_cost,
                    shipping_cost_est=shipping_est,
                    retail_price=float(retail_price),
                    net_profit=net_profit,
                    profit_margin_pct=margin_pct,
                    is_hero_recommendation=is_hero
                )
                variants.append(variant)

        logger.info(f"[{self.name}] Configured {len(variants)} profitable variants (Margins: {min(v.profit_margin_pct for v in variants)}% - {max(v.profit_margin_pct for v in variants)}%).")
        return variants
