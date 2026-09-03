import requests

try:
    print("Pinging https://atelier-canvas-store.onrender.com...")
    res = requests.get("https://atelier-canvas-store.onrender.com", timeout=30)
    print("Status:", res.status_code)
    print("Title in HTML:", "ATELIER & CANVAS" in res.text)
except Exception as e:
    print("Wait notice:", e)
