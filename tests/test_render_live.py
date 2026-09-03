import requests

base_url = "https://atelier-canvas-store.onrender.com"

# 1. Homepage
r = requests.get(base_url, timeout=15)
print("1. Live Homepage Status:", r.status_code)
assert r.status_code == 200

# 2. Catalog API
cat = requests.get(f"{base_url}/api/catalog", timeout=15)
print("2. Live Catalog Count:", len(cat.json()))
assert cat.status_code == 200
products = cat.json()

# 3. Product Page
p_id = products[0]["id"]
prod = requests.get(f"{base_url}/product/{p_id}", timeout=15)
print(f"3. Live Product Page Status (/product/{p_id[:25]}...):", prod.status_code)
assert prod.status_code == 200

print("\n🎉 ALL LIVE STORE ENDPOINTS ARE WORKING PERFECTLY ON RENDER!")
