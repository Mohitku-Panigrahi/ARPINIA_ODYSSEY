"""
Fetches Rajdhani Bold + Orbitron ExtraBold from Google Fonts (truetype),
base64-encodes them, and writes assets/banner.svg with embedded fonts.

Lastica override: place your licensed lastica.ttf at scripts/lastica.ttf
then re-run this script to bake it into the banner.

Run:   python scripts/generate_banner.py
Output: assets/banner.svg
"""

import urllib.request, base64, os, re

os.makedirs("assets", exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0"}

def fetch_font_b64(css_url):
    req = urllib.request.Request(css_url, headers=UA)
    with urllib.request.urlopen(req) as r:
        css = r.read().decode()
    # Match both woff2 and truetype URLs from gstatic
    m = re.search(r"url\((https://fonts\.gstatic\.com[^)]+)\)", css)
    if not m:
        raise RuntimeError(f"Could not parse font URL from: {css_url}\nCSS:\n{css[:500]}")
    font_url = m.group(1)
    print(f"  Fetching: {font_url}")
    with urllib.request.urlopen(font_url) as r:
        return base64.b64encode(r.read()).decode()

# ── Rajdhani Bold (ODYSSEY)
print("Fetching Rajdhani Bold...")
rajdhani_b64 = fetch_font_b64(
    "https://fonts.googleapis.com/css2?family=Rajdhani:wght@700&display=swap"
)

# ── Lastica (ARPINIA) — use local TTF if provided, else Orbitron as fallback
LASTICA_LOCAL = "scripts/lastica.ttf"
if os.path.exists(LASTICA_LOCAL):
    print("Using local Lastica TTF.")
    with open(LASTICA_LOCAL, "rb") as f:
        arpinia_b64 = base64.b64encode(f.read()).decode()
    arpinia_family = "Lastica"
else:
    print("Lastica not found — fetching Orbitron ExtraBold as visual fallback...")
    arpinia_b64 = fetch_font_b64(
        "https://fonts.googleapis.com/css2?family=Orbitron:wght@800&display=swap"
    )
    arpinia_family = "Orbitron"
    print("  (Drop scripts/lastica.ttf and re-run to use real Lastica)")

# ── Build SVG with embedded fonts
SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="140" viewBox="0 0 900 140">
  <defs>
    <style>
      @font-face {{
        font-family: 'ArpiniaFont';
        src: url('data:font/truetype;base64,{arpinia_b64}') format('truetype');
        font-weight: 800;
      }}
      @font-face {{
        font-family: 'Rajdhani';
        src: url('data:font/truetype;base64,{rajdhani_b64}') format('truetype');
        font-weight: 700;
      }}
    </style>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#030712"/>
      <stop offset="100%" style="stop-color:#0c1a2e"/>
    </linearGradient>
    <linearGradient id="glow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#06b6d4;stop-opacity:0"/>
      <stop offset="50%" style="stop-color:#06b6d4;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#a855f7;stop-opacity:0"/>
    </linearGradient>
    <filter id="softglow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="900" height="140" fill="url(#bg)" rx="12"/>

  <!-- Animated bottom glow line -->
  <rect y="136" width="900" height="4" fill="url(#glow)" rx="2">
    <animate attributeName="opacity" values="0.3;1;0.3" dur="3s" repeatCount="indefinite"/>
  </rect>

  <!-- Orbit ring decoration (right) -->
  <ellipse cx="830" cy="70" rx="54" ry="54" fill="none" stroke="#06b6d4" stroke-width="0.6" opacity="0.2">
    <animateTransform attributeName="transform" type="rotate" from="0 830 70" to="360 830 70" dur="14s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="830" cy="70" rx="37" ry="37" fill="none" stroke="#a855f7" stroke-width="0.6" opacity="0.25">
    <animateTransform attributeName="transform" type="rotate" from="360 830 70" to="0 830 70" dur="9s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="830" cy="70" rx="20" ry="20" fill="none" stroke="#f59e0b" stroke-width="0.5" opacity="0.18">
    <animateTransform attributeName="transform" type="rotate" from="0 830 70" to="360 830 70" dur="5s" repeatCount="indefinite"/>
  </ellipse>

  <!-- Satellite node -->
  <circle cx="830" cy="70" r="5" fill="#06b6d4" filter="url(#softglow)">
    <animate attributeName="r" values="5;8;5" dur="2.5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0.4;1" dur="2.5s" repeatCount="indefinite"/>
  </circle>

  <!-- ARPINIA — ArpiniaFont (Lastica/Orbitron), wide tracking, cyan glow -->
  <text
    x="44" y="76"
    font-family="ArpiniaFont, monospace"
    font-size="40"
    font-weight="800"
    fill="#06b6d4"
    letter-spacing="9"
    filter="url(#softglow)"
    opacity="0">
    ARPINIA
    <animate attributeName="opacity" values="0;1" dur="0.7s" begin="0.2s" fill="freeze"/>
  </text>

  <!-- ODYSSEY — Rajdhani Bold, wide tracking, near-white -->
  <text
    x="46" y="112"
    font-family="Rajdhani, monospace"
    font-size="28"
    font-weight="700"
    fill="#e2e8f0"
    letter-spacing="11"
    opacity="0">
    ODYSSEY
    <animate attributeName="opacity" values="0;1" dur="0.7s" begin="1.0s" fill="freeze"/>
  </text>

  <!-- Tagline -->
  <text
    x="47" y="130"
    font-family="monospace"
    font-size="8.5"
    fill="#4b5563"
    letter-spacing="2.5"
    opacity="0">
    SIH26143  ·  NTRO Disaster Management  ·  Maritime Oil-Spill Attribution
    <animate attributeName="opacity" values="0;0.8" dur="0.7s" begin="1.7s" fill="freeze"/>
  </text>
</svg>"""

out = "assets/banner.svg"
with open(out, "w", encoding="utf-8") as f:
    f.write(SVG)

print(f"\nWrote {out}  ({os.path.getsize(out) // 1024} KB)")
print(f"ARPINIA font: {arpinia_family}")
print("ODYSSEY font: Rajdhani Bold")
