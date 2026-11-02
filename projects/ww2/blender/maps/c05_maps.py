# Period maps for chapters 5, 6 and 8 (c05_ / c06_ sets), drawn with make_map2.render and our own colour groups.
#   python3 maps/c05_maps.py      (from blender/) -> maps/c05_europe1940.png, c05_med1941.png, c06_east1941.png
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_map2 as M
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))

def groups(G):
    M.GROUPS.clear(); M.GROUPS.update(G); M.CODE.clear()
    for g, (codes, col) in G.items():
        for c in codes: M.CODE.setdefault(c, col)
AXIS = (92, 88, 96)
OCC = ["DEU", "AUT", "CZE", "POL", "FRA", "BEL", "NLD", "LUX", "DNK", "NOR", "SVK", "KAL"]
# East Prussia (Kaliningrad) was German until 1945: split it off the modern Russian outline
for f in M.GEO["features"]:
    if f["properties"]["ADM0_A3"] == "RUS" and f["geometry"]["type"] == "MultiPolygon":
        keep, kal = [], []
        for poly in f["geometry"]["coordinates"]:
            xs = [x for x, y in poly[0]]; ys = [y for x, y in poly[0]]
            (kal if max(xs) < 23.5 and 53 < min(ys) and max(ys) < 56 else keep).append(poly)
        if kal:
            f["geometry"]["coordinates"] = keep
            M.GEO["features"].append({"type": "Feature", "properties": {"ADM0_A3": "KAL", "MAPCOLOR7": 1}, "geometry": {"type": "MultiPolygon", "coordinates": kal}})
        break
BASE = {
    "GBR": (["GBR", "EGY", "SDN", "IRQ", "JOR", "ISR", "PSX", "CYP", "MLT"], (214, 70, 64)),
    "SOV": (["RUS", "UKR", "BLR", "KAZ", "GEO", "ARM", "AZE", "MDA", "UZB", "TKM", "LTU", "LVA", "EST"], (200, 112, 70)),
}
EU_LABELS = [("GERMANY", 10.3, 51.4, 0.9, 0.1), ("FRANCE", 2.4, 46.8, 0.95, 0.1), ("BRITAIN", -1.8, 53.0, 0.62, 0.0), ("POLAND", 19.6, 52.3, 0.7, 0.1),
             ("NORWAY", 9.5, 61.6, 0.6, 0.0), ("ITALY", 13.0, 42.6, 0.55, 0.0), ("SPAIN", -3.8, 40.0, 0.9, 0.1), ("U.S.S.R.", 36, 56, 1.4, 0.4),
             ("SWEDEN", 15.5, 63, 0.6, 0.0), ("TURKEY", 33, 39, 0.8, 0.1), ("ROMANIA", 25, 45.8, 0.55, 0.0), ("YUGOSLAVIA", 19.5, 44.0, 0.45, 0.0),
             ("GREECE", 22.0, 39.6, 0.45, 0.0), ("PORTUGAL", -8.3, 39.6, 0.32, 0.0), ("IRELAND", -8.0, 53.2, 0.32, 0.0), ("HUNGARY", 19.3, 47.1, 0.4, 0.0),
             ("FINLAND", 26.5, 63.8, 0.55, 0.0), ("ALBANIA", 20.1, 41.0, 0.24, 0.0), ("BULGARIA", 25.3, 42.7, 0.4, 0.0), ("SWITZ.", 8.2, 46.8, 0.24, 0.0),
             ("LIBYA", 17.6, 29, 0.9, 0.1), ("EGYPT", 29.8, 27.2, 0.8, 0.0), ("ALGERIA", 3, 30.5, 0.8, 0.1), ("TUNISIA", 9.3, 34.0, 0.32, 0.0), ("BELGIUM", 4.6, 50.6, 0.26, 0.0),
             ("HOLLAND", 5.6, 52.3, 0.26, 0.0), ("DENMARK", 9.2, 56.0, 0.3, 0.0), ("AUSTRIA", 14.3, 47.6, 0.3, 0.0)]
EU_SEAS = [("NORTH SEA", 3.5, 56.2, 0.65), ("ATLANTIC OCEAN", -10.5, 46, 0.6), ("MEDITERRANEAN SEA", 18, 35.0, 0.7), ("BLACK SEA", 34, 43.3, 0.55), ("BALTIC", 19.4, 57.6, 0.45)]

def arrow(im, pts, lon0, lon1, lat0, lat1, col, w, head=1.0):
    W, H = im.size; d = ImageDraw.Draw(im)
    P = [((lo - lon0) / (lon1 - lon0) * W, (lat0 - la) / (lat0 - lat1) * H) for lo, la in pts]
    d.line(P, fill=(30, 18, 14), width=int(w * 1.5), joint="curve"); d.line(P, fill=col, width=int(w), joint="curve")
    (x0, y0), (x1, y1) = P[-2], P[-1]; import math
    a = math.atan2(y1 - y0, x1 - x0); L = w * 3.0 * head
    tri = [(x1 + math.cos(a) * L * 0.6, y1 + math.sin(a) * L * 0.6), (x1 + math.cos(a + 2.4) * L, y1 + math.sin(a + 2.4) * L), (x1 + math.cos(a - 2.4) * L, y1 + math.sin(a - 2.4) * L)]
    d.polygon(tri, fill=col, outline=(30, 18, 14))

if __name__ == "__main__":
    # 1. Churchill's wall map, Europe summer 1940: Germany, Italy and everything they hold in one dark colour
    groups({"AX": (OCC + ["ITA", "LBY", "ALB"], AXIS), **BASE})
    M.LABELS[:] = EU_LABELS; M.SEAS[:] = EU_SEAS
    M.render("c05_europe1940.png", 3000, 2000, -14, 46, 66, 26, rose=(-10, 33), cart=(38, 30.0, "EUROPE", "Situation  July 1940"), scale=0.55, seed=11)
    # 2. the Berghof table map, spring 1941: Germany grey, Italy green, Greece / Yugoslavia neutral, Britain red
    groups({"GER": (OCC, (128, 128, 132)), "ITA": (["ITA", "LBY", "ALB"], (110, 160, 84)), **BASE})
    M.render("c05_med1941.png", 3000, 2000, -14, 46, 66, 26, rose=(-10, 33), cart=(38, 30.0, "EUROPE & MEDITERRANEAN", "Lagekarte 1941"), scale=0.55, seed=12)
    # 3. Barbarossa: the Eastern Front, June 1941, with the three army-group arrows
    groups({"GER": (OCC + ["ROU", "HUN", "FIN", "SVK", "YUG", "SRB", "HRV", "BIH", "SVN", "MNE", "MKD", "GRC", "BGR", "KOS"], (128, 128, 132)), "SOV": (["RUS", "UKR", "BLR", "LTU", "LVA", "EST", "MDA", "GEO", "ARM", "AZE", "KAZ"], (200, 82, 70)), "GBR": (["GBR", "EGY", "IRQ"], (214, 120, 130)), "ITA": (["ITA", "ALB"], (110, 160, 84))})
    M.LABELS[:] = [("GERMANY", 11, 51.4, 1.0, 0.1), ("POLAND", 19.6, 52.0, 0.7, 0.1), ("U.S.S.R.", 48, 58, 2.0, 0.5), ("UKRAINE", 32, 49, 0.8, 0.2),
                   ("ROMANIA", 25, 45.8, 0.6, 0.0), ("FINLAND", 26.5, 63.8, 0.7, 0.0), ("TURKEY", 34, 39.2, 0.8, 0.1), ("SWEDEN", 15.5, 62, 0.6, 0.0),
                   ("LENINGRAD", 30.3, 60.75, 0.62, 0.0), ("MOSCOW", 37.6, 56.55, 0.7, 0.0), ("KYIV", 30.5, 51.25, 0.62, 0.0), ("STALINGRAD", 44.5, 49.45, 0.55, 0.0)]
    M.SEAS[:] = [("BLACK SEA", 34, 43.3, 0.6), ("BALTIC", 19.0, 56.6, 0.5), ("CASPIAN", 51, 42, 0.45)]
    M.render("c06_east1941.png", 3000, 2000, 6, 66, 68, 36, rose=(10, 40), cart=(60, 38.5, "EASTERN FRONT", "22 June 1941"), scale=0.55, seed=13)
    im = Image.open(os.path.join(HERE, "c06_east1941.png")).convert("RGB")
    for pts in (((21.5, 55.0), (25.5, 57.2), (28.8, 59.2)), ((23.5, 52.6), (29, 53.6), (35.6, 55.2)), ((24.0, 50.0), (27, 49.9), (29.4, 50.2))):
        arrow(im, pts, 6, 66, 68, 36, (40, 36, 40), 20)
    d = ImageDraw.Draw(im)
    for lo, la in ((30.3, 59.94), (37.6, 55.75), (30.5, 50.45), (44.5, 48.7)):
        x, y = (lo - 6) / 60 * 3000, (68 - la) / 32 * 2000; d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(250, 240, 210), outline=(40, 20, 14), width=5)
    im.save(os.path.join(HERE, "c06_east1941.png"))
    # dots for the cities
    print("maps done")
