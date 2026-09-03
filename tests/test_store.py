import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from storefront.app import app

def test_storefront():
    client = TestClient(app)
    
    # 1. Test Homepage
    home = client.get("/")
    print("1. Homepage GET:", home.status_code)
    assert home.status_code == 200
    assert "OAK PRINT STUDIO" in home.text



    # 2. Test Catalog API
    cat = client.get("/api/catalog")
    print("2. Catalog API GET:", cat.status_code, f"({len(cat.json())} products found)")
    assert cat.status_code == 200
    products = cat.json()
    assert len(products) >= 5

    # 3. Test Single Product Page
    import html
    p_id = products[0]["id"]
    prod_page = client.get(f"/product/{p_id}")
    print(f"3. Product Page GET (/product/{p_id}):", prod_page.status_code)
    assert prod_page.status_code == 200
    assert products[0]["title"] in html.unescape(prod_page.text)


    # 4. Test Stripe Checkout API with Bundle Discount
    # Single Item
    single_res = client.post("/api/checkout", json={
        "items": [{
            "product_id": p_id,
            "product_title": products[0]["title"],
            "variant_id": "natural_oak_24x36_in",
            "size_label": "24x36 in (60x90 cm)",
            "frame_label": "Solid Natural Oak Wood Frame",
            "gelato_sku": "framed-poster_flat_wood_natural_24x36-in_200-gsm",
            "price": 110.0,
            "image_url": "/static/test.jpg",
            "quantity": 1
        }]
    })
    print("4a. Checkout Single Item POST:", single_res.status_code, single_res.json().get("bundle_discount_applied"))
    assert single_res.status_code == 200

    # 3-Piece Gallery Triptych Bundle (20% Off)
    bundle_res = client.post("/api/checkout", json={
        "items": [
            {
                "product_id": p_id,
                "product_title": products[0]["title"],
                "variant_id": "natural_oak_24x36_in",
                "size_label": "24x36 in",
                "frame_label": "Natural Oak",
                "gelato_sku": "framed-poster_flat_wood_natural_24x36-in",
                "price": 110.0,
                "image_url": "/static/test1.jpg",
                "quantity": 1
            },
            {
                "product_id": p_id,
                "product_title": "Matching Abstract Duo",
                "variant_id": "natural_oak_24x36_in",
                "size_label": "24x36 in",
                "frame_label": "Natural Oak",
                "gelato_sku": "framed-poster_flat_wood_natural_24x36-in",
                "price": 110.0,
                "image_url": "/static/test2.jpg",
                "quantity": 1
            },
            {
                "product_id": p_id,
                "product_title": "Complementary Botanical Print",
                "variant_id": "natural_oak_24x36_in",
                "size_label": "24x36 in",
                "frame_label": "Natural Oak",
                "gelato_sku": "framed-poster_flat_wood_natural_24x36-in",
                "price": 110.0,
                "image_url": "/static/test3.jpg",
                "quantity": 1
            }
        ]
    })
    print("4b. Checkout 3-Piece Triptych Bundle POST:", bundle_res.status_code, bundle_res.json().get("bundle_discount_applied"))
    assert bundle_res.status_code == 200
    assert "20% Off" in bundle_res.json().get("bundle_discount_applied", "")

    # 5. Test Success Page & Automated Gelato Routing
    success_page = client.get(f"/success?order_ref={bundle_res.json()['order_ref']}")
    print("5. Order Success & Gelato Dispatch GET:", success_page.status_code)
    assert success_page.status_code == 200
    assert "Your Fine Art Print is in Production" in success_page.text

    print("\n All Automated Storefront, Bundle & Checkout Tests PASSED Successfully!")


if __name__ == "__main__":
    test_storefront()
