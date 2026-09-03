import socket

candidates = [
    # Oak-based Abstract / Editorial (.com)
    "oakhouse.com", "oakliving.com", "oakstudio.com", "oakform.com", "oakhaven.com",
    "oakline.com", "oakhome.com", "oakmaison.com", "oakatelier.com", "oakluxe.com",
    "oakpure.com", "oaknordic.com", "oakverve.com", "oakminimal.com", "oakserene.com",
    "casaandpure.com", "casaandform.com", "casaoak.com", "studiocasa.com",
    
    # Modern Design House Names with "Oak"
    "oakformstudio.com", "oaklivingstudio.com", "oakmaisonstudio.com",
    "oaknordicstudio.com", "oakhausstudio.com", "oakandcasa.com",
    "oakpurestudio.com", "oakserenestudio.com",
    
    # Short Coined / Editorial Lifestyle Names (No category word)
    "varahaus.com", "varaliving.com", "varastudio.com", "varamaison.com",
    "formahaus.com", "formaliving.com", "formamaison.com",
    "kanso living.com", "kansohaus.com", "kansostudio.com",
    "lumenhaus.com", "lumenliving.com", "lumenmaison.com",
    "serenahaus.com", "serenaliving.com", "serenamaison.com",
    "terrahaus.com", "terraliving.com", "terramaison.com",
    "havenaura.com", "havenliving.com", "havenhaus.com"
]

print("=== AUDITING ABSTRACT / EDITORIAL .COM DOMAINS ===")
available = []
taken = []

for d in candidates:
    d_clean = d.replace(" ", "")
    try:
        ip = socket.gethostbyname(d_clean)
        taken.append((d_clean, ip))
    except socket.gaierror:
        available.append(d_clean)

print("\n--- AVAILABLE .COM (ABSTRACT / NO PRODUCT WORD) ---")
for d in sorted(available):
    print(f"  [AVAILABLE] {d}")
