import socket

def check_domains():
    candidates = [
        "lumenoak.com", "lumenandoak.com", "lumenoakstudio.com", "lumenoakart.com",
        "auraandframe.com", "auraframed.com", "auraframestudio.com",
        "varaprints.com", "varaframed.com", "varastudioart.com",
        "calmandframe.com", "calmframed.com", "calmframestudio.com",
        "atelierandcanvas.com", "ateliercanvasstudio.com", "ateliercanvasart.com",
        "maisonandframe.com", "maisoncadreart.com", "maisonframestudio.com",
        "serenaandframe.com", "serenaframestudio.com",
        "havenandcanvas.com", "havenframeart.com", "havenframestudio.com",
        "terraandframe.com", "terraframed.com", "terraframestudio.com"
    ]
    
    print("Checking domain DNS resolution...")
    for d in candidates:
        try:
            ip = socket.gethostbyname(d)
            print(f"  [TAKEN / HAS IP] {d} -> {ip}")
        except socket.gaierror:
            print(f"  [POTENTIALLY AVAILABLE - NO IP] {d}")

if __name__ == "__main__":
    check_domains()
