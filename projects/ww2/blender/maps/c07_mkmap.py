# Pacific theatre table map for c07_maproom / c13_maproom: make_map2 base (1941 colours) + the Pacific place names.
#   python3 maps/c07_mkmap.py  -> maps/c07_pacific.png (lon 92..250 E, lat 56..-22, 4096 x 2022)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_map2 as MM
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
LON0, LON1, LAT0, LAT1, W, H = 92.0, 250.0, 56.0, -22.0, 4096, 2022
PLACES = [  # name, lon, lat, label dx, dy (px), size
    ("TOKYO", 139.7, 35.7, 30, -10, 42), ("PEARL HARBOR", 202.05, 21.37, 0, 44, 40), ("HAWAII", 204.5, 22.6, 0, -40, 34),
    ("MIDWAY", 182.6, 28.2, 0, -44, 40), ("WAKE", 166.6, 19.3, 0, -40, 32), ("GUAM", 144.8, 13.4, 34, 0, 30),
    ("SINGAPORE", 103.8, 1.35, 0, 40, 36), ("HONG KONG", 114.2, 22.3, 0, 38, 32), ("MANILA", 121.0, 14.6, -40, -6, 30),
    ("GUADALCANAL", 160.0, -9.6, 0, 40, 36), ("IWO JIMA", 141.3, 24.8, 40, 6, 32), ("OKINAWA", 127.9, 26.5, -40, -18, 32),
    ("SAN FRANCISCO", 237.6, 37.8, -30, -40, 34), ("LEYTE", 125.0, 11.0, 46, 30, 28), ("TARAWA", 172.9, 1.4, 0, 36, 30), ("SAIPAN", 145.7, 15.2, 36, -14, 28),
]
if __name__ == "__main__":
    MM.LABELS.append(("U.S.A.", 244, 41, 0.9, 0.3))
    MM.SEAS[:] = [("PACIFIC OCEAN", 185, 8, 1.6), ("PACIFIC OCEAN", 220, 30, 1.2), ("SOUTH CHINA SEA", 113, 11, 0.42), ("CORAL SEA", 156, -16, 0.6),
                  ("SEA OF JAPAN", 135, 40.5, 0.42), ("PHILIPPINE SEA", 133, 18, 0.5), ("INDIAN OCEAN", 98, -14, 0.7)]
    MM.render("c07_pacific.png", W, H, LON0, LON1, LAT0, LAT1, rose=(232, -12), cart=(198, -14, "THE PACIFIC", "General Staff Map  1941"), scale=1.1, seed=11)
    im = Image.open(os.path.join(HERE, "c07_pacific.png")).convert("RGB"); d = ImageDraw.Draw(im)
    P = lambda lo, la: ((lo - LON0) * W / (LON1 - LON0), (LAT0 - la) * H / (LAT0 - LAT1))
    for name, lo, la, dx, dy, sz in PLACES:
        x, y = P(lo, la); r = 9
        if name != "HAWAII": d.ellipse([x - r - 4, y - r - 4, x + r + 4, y + r + 4], fill=(240, 228, 200)); d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 30, 26)) if name != "HAWAII" else None
        f = ImageFont.truetype(MM.F_BOLD, sz)
        anchor = "mm" if dx == 0 else ("lm" if dx > 0 else "rm")
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)): d.text((x + dx + ox, y + dy + oy), name, font=f, anchor=anchor, fill=(240, 230, 205))
        d.text((x + dx, y + dy), name, font=f, anchor=anchor, fill=(60, 26, 18))
    im.save(os.path.join(HERE, "c07_pacific.png"), optimize=True); print("ok", im.size)
