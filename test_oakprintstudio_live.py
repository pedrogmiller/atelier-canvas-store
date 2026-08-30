import requests

base_url = "https://www.oakprintstudio.com"

# 1. Homepage
r = requests.get(base_url, timeout=10)
print("1. Homepage Status:", r.status_code)
assert r.status_code == 200

# 2. Catalog
cat = requests.get(f"{base_url}/api/catalog", timeout=10)
print(f"2. Catalog API ({len(cat.json())} products):", cat.status_code)
assert cat.status_code == 200

# 3. Product Page
p = cat.json()[0]
prod = requests.get(f"{base_url}/product/{p['id']}", timeout=10)
print(f"3. Live Product Page ({p['title'][:30]}...):", prod.status_code)
assert prod.status_code == 200

print("\nSUCCESS: https://www.oakprintstudio.com IS 100% LIVE AND OPERATIONAL!")
