import base64
from pathlib import Path

enso_path = Path("storefront/static/images/logo_emblem.png")
with open(enso_path, "rb") as f:
    enso_b64 = base64.b64encode(f.read()).decode("utf-8")

svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500">
  <defs>
    <!-- Top Arc Path: Sweep clockwise from left to right along top circle -->
    <path id="top-arc" d="M 85,250 A 165,165 0 0,1 415,250" fill="none" />
    
    <!-- Bottom Arc Path: Sweep counter-clockwise from right to left along bottom circle so text reads upright left-to-right -->
    <path id="bottom-arc" d="M 415,250 A 165,165 0 0,1 85,250" fill="none" />
  </defs>

  <!-- Background Warm Archival Paper Circle -->
  <circle cx="250" cy="250" r="235" fill="#FAF6F0" stroke="#1C1C1E" stroke-width="3" />

  <!-- Outer Fine Ochre Ring -->
  <circle cx="250" cy="250" r="222" fill="none" stroke="#B8834E" stroke-width="1.5" stroke-dasharray="4,4" opacity="0.85" />

  <!-- Inner Fine Ring -->
  <circle cx="250" cy="250" r="148" fill="none" stroke="#E8E3DA" stroke-width="1.5" />

  <!-- Center Enso Brush Mark -->
  <image href="data:image/png;base64,{enso_b64}" x="145" y="145" width="210" height="210" />

  <!-- Top Text: OAK PRINT STUDIO -->
  <text font-family="'Plus Jakarta Sans', Arial, sans-serif" font-size="16" font-weight="700" letter-spacing="6" fill="#1C1C1E">
    <textPath href="#top-arc" startOffset="50%" text-anchor="middle">
      OAK PRINT STUDIO
    </textPath>
  </text>

  <!-- Bottom Text: ARCHIVAL FINE ART & FRAMING (Upright & Clean) -->
  <text font-family="'Plus Jakarta Sans', Arial, sans-serif" font-size="11" font-weight="600" letter-spacing="4" fill="#B8834E">
    <textPath href="#bottom-arc" startOffset="50%" text-anchor="middle">
      • ARCHIVAL FINE ART &amp; FRAMING •
    </textPath>
  </text>
</svg>"""

out_svg = Path("storefront/static/images/logo_seal.svg")
with open(out_svg, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Saved {out_svg} ({len(svg_content)} bytes)")
