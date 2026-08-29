import os
import requests
from dotenv import load_dotenv
from suppliers.gelato_client import gelato_client
from config.settings import settings

load_dotenv()

def test_gelato():
    print("Testing Gelato API connection...")
    key = settings.gelato_api_key
    print(f"Key loaded: {key[:12]}... (length: {len(key)})")
    
    headers = {"X-API-KEY": key}
    res = requests.get("https://order.gelatoapis.com/v4/orders", headers=headers, params={"limit": 1})
    print("Gelato API Response Status:", res.status_code)
    if res.status_code in [200, 201]:
        print(" Gelato API Authentication: SUCCESS!")
        print("Active Gelato Account verified.")
    else:
        print("Response:", res.text)

if __name__ == "__main__":
    test_gelato()
