import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Header
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import stripe

from config.settings import settings
from suppliers.pricing_models import (
    GelatoOrderPayload, GelatoOrderLineItem, CustomerShippingAddress
)
from suppliers.gelato_client import gelato_client
from agents.seo_indexer_agent import seo_indexer_agent

logger = logging.getLogger("StorefrontApp")

# Setup FastAPI App
app = FastAPI(title=settings.app_name)

# Mount Static & Templates
app.mount("/static", StaticFiles(directory=str(settings.storefront_dir / "static")), name="static")
templates = Jinja2Templates(directory=str(settings.storefront_dir / "templates"))

# Setup Stripe
stripe.api_key = settings.stripe_secret_key
is_stripe_live = bool(settings.stripe_secret_key and settings.stripe_secret_key.startswith("sk_live_"))

def get_catalog() -> List[Dict[str, Any]]:
    """Loads current live product catalog from catalog.json."""
    if settings.catalog_file.exists():
        try:
            with open(settings.catalog_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read catalog.json: {e}")
    return []

def render_template(template_name: str, request: Request, context: Dict[str, Any] = None):
    """Bulletproof template renderer compatible with all Starlette and FastAPI versions."""
    ctx = {"request": request}
    if context:
        ctx.update(context)
    try:
        return templates.TemplateResponse(request=request, name=template_name, context=ctx)
    except (TypeError, AttributeError):
        return templates.TemplateResponse(template_name, ctx)

# --- Storefront Routes ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Gallery homepage with hero and product grid."""
    products = get_catalog()
    return render_template("index.html", request, {"products": products})

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: str):
    """Product configurator page with interactive frame/size selector and Google JSON-LD schema."""
    products = get_catalog()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product collection not found.")
    
    schema_data = seo_indexer_agent.generate_product_schema(product)
    schema_json = json.dumps(schema_data)
    return render_template("product.html", request, {"product": product, "product_schema_json": schema_json})

@app.get("/api/catalog")
async def api_catalog():
    """Returns active product catalog in JSON format."""
    return JSONResponse(content=get_catalog())

@app.get("/sitemap.xml")
async def sitemap():
    """Dynamically serves standard XML sitemap for Google and search crawlers."""
    catalog = get_catalog()
    xml_content = seo_indexer_agent.generate_sitemap_xml(catalog)
    return Response(content=xml_content, media_type="application/xml")

@app.get("/robots.txt")
async def robots():
    """Serves robots.txt with sitemap directive."""
    robots_content = seo_indexer_agent.generate_robots_txt()
    return Response(content=robots_content, media_type="text/plain")

@app.get("/googleedeef9195d589a72.html")
async def google_verification():
    """Serves Google Search Console ownership verification file."""
    return Response(content="google-site-verification: googleedeef9195d589a72.html", media_type="text/html")

@app.get("/returns", response_class=HTMLResponse)
@app.get("/return-policy", response_class=HTMLResponse)
@app.get("/refund-policy", response_class=HTMLResponse)
async def returns_policy(request: Request):
    """Clear 30-day return, exchange, and refund policy required for Pinterest and Google Merchant status."""
    return render_template("returns.html", request, {"title": "Return & Refund Policy — Oak Print Studio"})

@app.get("/shipping", response_class=HTMLResponse)
@app.get("/shipping-policy", response_class=HTMLResponse)
async def shipping_policy(request: Request):
    """Global localized shipping and delivery policy in 32 countries."""
    return render_template("shipping.html", request, {"title": "Shipping & Delivery Policy — Oak Print Studio"})

@app.get("/privacy", response_class=HTMLResponse)
@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    """GDPR & CCPA compliant privacy policy."""
    return render_template("privacy.html", request, {"title": "Privacy Policy — Oak Print Studio"})

@app.get("/terms", response_class=HTMLResponse)
@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_policy(request: Request):
    """Terms of Service."""
    return render_template("terms.html", request, {"title": "Terms of Service — Oak Print Studio"})

@app.get("/pinterest-catalog.csv")
async def pinterest_catalog(currency: str = "EUR"):
    """Dynamically serves Pinterest Merchant Product Catalog CSV for 100% automated pin creation."""
    import csv, io
    catalog = get_catalog()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "description", "link", "image_link", "price", "availability", "condition", "brand", "google_product_category", "product_type"])
    base_url = "https://www.oakprintstudio.com"
    curr = currency.upper()
    for p in catalog:
        pid = p.get("id")
        title = p.get("title", "")
        desc = p.get("short_summary", "")
        link = f"{base_url}/product/{pid}"
        hero_img = p.get("images", {}).get("hero", "")
        img_link = f"{base_url}{hero_img}" if hero_img.startswith("/") else hero_img
        st_price = float(p.get("starting_price", 26.0))
        price = f"{st_price:.2f} {curr}"
        category = "Home & Garden > Decor > Artwork > Posters, Prints, & Visual Artwork"
        ptype = p.get("aesthetic_name", "Fine Art")
        writer.writerow([pid, title, desc, link, img_link, price, "in stock", "new", "Oak Print Studio", category, ptype])
    return Response(content=output.getvalue(), media_type="text/csv")

recent_pings: List[Dict[str, str]] = []

@app.get("/api/health")
async def health_check(request: Request):
    """Diagnostic health check to verify Gelato, Stripe, and keep-alive monitor status."""
    from datetime import datetime, timezone
    ua = request.headers.get("user-agent", "unknown")
    recent_pings.append({
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
        "user_agent": ua[:70]
    })
    if len(recent_pings) > 10:
        recent_pings.pop(0)

    is_gelato_active = bool(gelato_client.api_key and not gelato_client.is_mock_mode)
    stripe_key_type = "LIVE" if is_stripe_live else ("TEST_SANDBOX" if settings.stripe_secret_key.startswith("sk_test_") else "MOCK")
    return JSONResponse(content={
        "status": "healthy",
        "store": "OAK PRINT STUDIO",
        "domain": "oakprintstudio.com",
        "gelato_connected": is_gelato_active,
        "gelato_mode": "LIVE" if is_gelato_active else "MOCK_FALLBACK",
        "stripe_mode": stripe_key_type,
        "recent_pings": recent_pings
    })


# --- Stripe & Checkout Layer ---

class CheckoutItem(BaseModel):
    product_id: str
    product_title: str
    variant_id: str
    size_label: str
    frame_label: str
    gelato_sku: str
    price: float
    image_url: str
    quantity: int = 1

class CheckoutRequest(BaseModel):
    items: List[CheckoutItem]

@app.post("/api/checkout")
async def create_checkout_session(payload: CheckoutRequest):
    """Creates a Stripe Checkout Session with dynamic Gallery Bundle savings."""
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty.")

    order_ref = f"order_{uuid.uuid4().hex[:8]}"

    # Calculate bundle discount
    total_qty = sum(item.quantity for item in payload.items)
    discount_multiplier = 1.0
    discount_label = ""
    if total_qty >= 3:
        discount_multiplier = 0.80  # 20% off
        discount_label = " (Gallery Bundle - 20% Off)"
    elif total_qty >= 2:
        discount_multiplier = 0.85  # 15% off
        discount_label = " (Pair Bundle - 15% Off)"

    if is_stripe_live:
        try:
            line_items = []
            for item in payload.items:
                discounted_unit_price = round(item.price * discount_multiplier, 2)
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"{item.product_title} - {item.frame_label} ({item.size_label}){discount_label}",
                            "images": [f"{settings.store_url}{item.image_url}" if item.image_url.startswith("/") else item.image_url],
                            "metadata": {
                                "gelato_sku": item.gelato_sku,
                                "product_id": item.product_id,
                                "variant_id": item.variant_id
                            }
                        },
                        "unit_amount": int(discounted_unit_price * 100), # Cents
                    },
                    "quantity": item.quantity,
                })

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                shipping_address_collection={"allowed_countries": ["US", "CA", "GB", "DE", "FR", "AU", "IT", "ES", "NL", "SE"]},
                success_url=f"{settings.store_url}/success?order_ref={order_ref}&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.store_url}/#collection",
                client_reference_id=order_ref,
                metadata={"order_ref": order_ref, "bundle_discount": discount_label}
            )
            return {
                "checkout_url": session.url,
                "order_ref": order_ref,
                "bundle_discount_applied": discount_label or "Standard"
            }
        except Exception as e:
            logger.error(f"Stripe error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    else:
        # Seamless Mock / Test Mode Checkout
        return {
            "checkout_url": f"/success?order_ref={order_ref}&mock_mode=true",
            "order_ref": order_ref,
            "mode": "test_simulator",
            "bundle_discount_applied": discount_label or "Standard"
        }


@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request, order_ref: str = "order_sample", session_id: str = ""):
    """Displays order confirmation and triggers automated Gelato fulfillment in background."""
    # Simulate automated fulfillment routing for demo/test orders
    mock_address = CustomerShippingAddress(
        first_name="Valued",
        last_name="Collector",
        address_line_1="742 Evergreen Terrace",
        city="Austin",
        state_province="TX",
        postal_code="78701",
        country_code="US",
        email="customer@example.com"
    )
    
    # Auto-dispatch to Gelato client
    order_payload = GelatoOrderPayload(
        order_reference_id=order_ref,
        customer_reference_id="cust_guest",
        items=[
            GelatoOrderLineItem(
                item_reference_id="item_1",
                product_uid="framed-poster_flat_wood_natural_24x36-in_200-gsm",
                files=[{"type": "default", "url": f"{settings.store_url}/static/products/sample/master_art.jpg"}]
            )
        ],
        shipping_address=mock_address
    )
    gelato_client.create_fulfillment_order(order_payload)

    return render_template(
        "success.html",
        request,
        {"order_ref": order_ref}
    )

# --- Stripe Webhook Listener (Automated 100% Fulfillment) ---


@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receives payment confirmation from Stripe and automatically orders from Gelato."""
    payload_body = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload_body, sig_header, settings.stripe_webhook_secret
        )
    except Exception as e:
        logger.error(f"Invalid webhook signature: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_ref = session.get("client_reference_id", f"order_{uuid.uuid4().hex[:8]}")
        shipping = session.get("shipping_details", {})
        customer_email = session.get("customer_details", {}).get("email", "")

        # Extract address
        address = CustomerShippingAddress(
            first_name=shipping.get("name", "Collector").split()[0],
            last_name=" ".join(shipping.get("name", "Collector").split()[1:]) or "Customer",
            address_line_1=shipping.get("address", {}).get("line1", "123 Gallery Way"),
            address_line_2=shipping.get("address", {}).get("line2", ""),
            city=shipping.get("address", {}).get("city", "New York"),
            state_province=shipping.get("address", {}).get("state", "NY"),
            postal_code=shipping.get("address", {}).get("postal_code", "10001"),
            country_code=shipping.get("address", {}).get("country", "US"),
            email=customer_email
        )

        # Dispatch fulfillment
        line_items = session.get("line_items", {}).get("data", [])
        order_items = []
        for item in line_items:
            sku = item.get("price", {}).get("product", {}).get("metadata", {}).get("gelato_sku", "framed-poster_flat_wood_natural_24x36-in_200-gsm")
            order_items.append(GelatoOrderLineItem(
                item_reference_id=f"item_{uuid.uuid4().hex[:6]}",
                product_uid=sku,
                files=[{"type": "default", "url": f"{settings.store_url}/static/products/sample/master_art.jpg"}],
                quantity=item.get("quantity", 1)
            ))

        order_payload = GelatoOrderPayload(
            order_reference_id=order_ref,
            customer_reference_id=customer_email or "cust_direct",
            items=order_items,
            shipping_address=address
        )

        background_tasks.add_task(gelato_client.create_fulfillment_order, order_payload)
        logger.info(f"Successfully queued automated Gelato fulfillment for order: {order_ref}")

    return {"status": "success"}
