import socket

domains = [
    "terraframe.com",
    "terraandframe.com",
    "terraframed.com",
    "terraframestudio.com",
    "terraframeart.com",
    "terraframeshop.com"
]

print("Checking Terra Frame domain resolutions:")
for d in domains:
    try:
        ip = socket.gethostbyname(d)
        print(f"  [REGISTERED / HAS IP] {d} -> {ip}")
    except socket.gaierror:
        print(f"  [POTENTIALLY AVAILABLE] {d}")
