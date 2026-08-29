import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    # App & Environment
    app_name: str = "Atelier & Canvas - Autonomous Art Store"
    base_dir: Path = BASE_DIR
    output_dir: Path = BASE_DIR / "output"
    storefront_dir: Path = BASE_DIR / "storefront"
    catalog_file: Path = BASE_DIR / "storefront" / "catalog.json"
    
    # API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gelato_api_key: str = os.getenv("GELATO_API_KEY", "")
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_secret_key")
    stripe_publishable_key: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_mock_pub_key")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock")
    
    # Currency & Business Margins
    currency: str = "USD"
    min_profit_margin_pct: float = 50.0  # Enforce at least 50% net profit margin
    default_markup_multiplier: float = 2.4  # Retail Price = Landed Cost * 2.4
    
    # Server configuration (Dynamic for Render / Railway / Local)
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    store_url: str = os.getenv("STORE_URL", f"http://localhost:{os.getenv('PORT', '8000')}")

settings = Settings()


# Ensure required directories exist
settings.output_dir.mkdir(parents=True, exist_ok=True)
(settings.storefront_dir / "static" / "products").mkdir(parents=True, exist_ok=True)
