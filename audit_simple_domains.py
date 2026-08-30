import socket

candidates = [
    # Single Word / Compound Studio Names (No "and")
    "formaframing.com", "formaprint.com", "formaprints.com", "formastudioart.com",
    "terraframing.com", "terraframes.com", "terraprint.com", "terraprints.com", "terragallery.com",
    "auraframing.com", "auraprints.com", "auragallery.com",
    "lumenoak.com", "lumenframes.com", "lumenprints.com", "lumenartstudio.com",
    "calmframing.com", "calmprints.com", "calmgallery.com", "calmstudioart.com",
    "maisonframed.com", "maisonprints.com", "maisongallery.com",
    "archframed.com", "archframing.com", "archprints.com", "archgallery.com",
    "zenframe.com", "zenframed.com", "zenframing.com", "zenprints.com",
    "nordicframed.com", "nordicframing.com", "nordicprints.com",
    "pureframed.com", "pureframing.com", "pureprints.com",
    "havenframed.com", "havenprints.com",
    "solarframed.com", "solarprints.com",
    "plasterframed.com", "plasterprints.com",
    "oakandart.com", "oakprints.com", "oakframing.com", "oakstudioart.com"
]

print("=== AUDITING SINGLE / NO-AND .COM DOMAINS ===")
available = []
taken = []

for d in candidates:
    try:
        ip = socket.gethostbyname(d)
        taken.append((d, ip))
    except socket.gaierror:
        available.append(d)

print("\n--- AVAILABLE .COM (NO 'AND') ---")
for d in sorted(available):
    print(f"  [AVAILABLE] {d}")
