import socket

candidates = [
    # Clean & Architectural
    "lumenframe.com", "lumenandframe.com", "lumenoakstudio.com", "lumenoakart.com",
    "auraandframe.com", "auraframestudio.com",
    "formaandframe.com", "formaframed.com", "formaframestudio.com", "formaartstudio.com",
    
    # Earth, Stone & Texture
    "terraandframe.com", "terraframeart.com", "terraframeshop.com",
    "stoneandframe.com", "stoneandcanvas.com", "stoneframeart.com", "stoneframestudio.com",
    "clayandcanvas.com", "clayandframe.com", "clayframeart.com",
    
    # Serene & Sanctuary
    "calmandframe.com", "calmframed.com", "calmframestudio.com", "calmcanvasart.com",
    "havenandframe.com", "havenframeart.com", "havenandcanvas.com",
    "serenaandframe.com", "serenaframestudio.com",
    
    # Nordic & Minimalist
    "nordicandframe.com", "nordicframestudio.com", "nordiccanvasart.com",
    "varaartstudio.com", "varaframed.com",
    
    # European Studio & Atelier
    "atelierandcanvas.com", "ateliercanvasstudio.com", "ateliercanvasart.com",
    "maisonandframe.com", "maisoncadreart.com", "maisonframestudio.com",
    "atelierandframe.com", "atelierframestudio.com", "atelierframeart.com"
]

print("=== DOMAIN AVAILABILITY AUDIT (.COM ONLY) ===")
available = []
taken = []

for d in candidates:
    try:
        ip = socket.gethostbyname(d)
        taken.append((d, ip))
    except socket.gaierror:
        available.append(d)

print("\n--- AVAILABLE .COM DOMAINS ---")
for d in available:
    print(f"  [AVAILABLE] {d}")

print("\n--- TAKEN DOMAINS ---")
for d, ip in taken:
    print(f"  [TAKEN] {d} -> {ip}")

