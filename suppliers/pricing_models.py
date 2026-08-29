from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class FrameType(str, Enum):
    NATURAL_OAK = "natural_oak"
    BLACK_WOOD = "black_wood"
    WHITE_WOOD = "white_wood"
    CANVAS_WRAP = "canvas_wrap"
    UNFRAMED_POSTER = "unframed_poster"

class ProductSize(str, Enum):
    SIZE_12X18 = "12x18_in"  # 30x45 cm
    SIZE_18X24 = "18x24_in"  # 45x60 cm
    SIZE_24X36 = "24x36_in"  # 60x90 cm
    SIZE_30X40 = "30x40_in"  # 75x100 cm

class ProductVariant(BaseModel):
    variant_id: str
    size: ProductSize
    size_label: str             # e.g., "24x36 in (60x90 cm)"
    frame_type: FrameType
    frame_label: str            # e.g., "Solid Natural Oak Frame"
    gelato_sku: str
    base_production_cost: float # What Gelato charges for manufacturing
    shipping_cost_est: float    # Domestic average shipping
    retail_price: float         # Customer pays this
    net_profit: float           # Pure profit after manufacturing + shipping + 3% payment fee
    profit_margin_pct: float    # (net_profit / retail_price) * 100
    is_hero_recommendation: bool = False

class GelatoOrderLineItem(BaseModel):
    item_reference_id: str
    product_uid: str
    files: List[Dict[str, str]] # e.g. [{"type": "default", "url": "..."}]
    quantity: int = 1

class CustomerShippingAddress(BaseModel):
    first_name: str
    last_name: str
    address_line_1: str
    address_line_2: Optional[str] = ""
    city: str
    state_province: str
    postal_code: str
    country_code: str          # e.g., "US", "GB", "DE", "FR"
    email: str
    phone: Optional[str] = ""

class GelatoOrderPayload(BaseModel):
    order_type: str = "order"
    order_reference_id: str
    customer_reference_id: str
    currency: str = "USD"
    items: List[GelatoOrderLineItem]
    shipping_address: CustomerShippingAddress
