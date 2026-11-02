# Painted 1939 political world maps for the WW2 sets (void table, war-room table, wall map, globe), drawn from
# Natural Earth 1:50m country outlines (maps/ne_50m_countries.geojson) with empire colours, water-lining, relief
# shadow, graticule, labels, compass rose, cartouche, paper fibres, folds and stains.
#   python3 maps/make_map2.py            (run from blender/; writes maps/map_void.png, map_table.png, map_world.png)
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = json.load(open(os.path.join(HERE, "ne_50m_countries.geojson")))
FD = "/usr/share/fonts/truetype/"
F_BOLD = FD + "dejavu/DejaVuSerif-Bold.ttf"; F_REG = FD + "dejavu/DejaVuSerif.ttf"
F_IT = FD + "freefont/FreeSerifBoldItalic.ttf" if os.path.exists(FD + "freefont/FreeSerifBoldItalic.ttf") else F_REG

# 1939 colour groups (modern borders, period empires)
GROUPS = {
    "GER": (["DEU", "AUT", "CZE"], (128, 132, 128)),
    "SOV": (["RUS", "UKR", "BLR", "KAZ", "UZB", "TKM", "KGZ", "TJK", "GEO", "ARM", "AZE", "MDA"], (196, 72, 62)),
    "BRI": (["GBR", "CAN", "AUS", "NZL", "IND", "PAK", "BGD", "MMR", "LKA", "ZAF", "EGY", "SDN", "SDS", "KEN", "UGA", "TZA", "NGA", "GHA",
             "ZMB", "ZWE", "MWI", "BWA", "NAM", "IRQ", "JOR", "ISR", "PSX", "MYS", "SGP", "BRN", "SLE", "GMB", "SOL", "IRL", "CYP", "MLT",
             "NPL", "BTN", "LSO", "SWZ", "GUY", "BLZ", "JAM", "BHS", "FJI", "PNG", "KWT", "ARE", "OMN", "YEM", "QAT", "BHR"], (230, 136, 148)),
    "FRA": (["FRA", "DZA", "MAR", "TUN", "MRT", "MLI", "NER", "TCD", "SEN", "GIN", "CIV", "BFA", "BEN", "TGO", "CMR", "CAF", "GAB", "COG",
             "MDG", "VNM", "LAO", "KHM", "SYR", "LBN", "DJI", "SUR", "NCL", "PYF"], (112, 128, 196)),
    "ITA": (["ITA", "LBY", "ETH", "ERI", "SOM", "ALB"], (122, 168, 92)),
    "JAP": (["JPN", "KOR", "PRK", "TWN"], (236, 196, 72)),
    "USA": (["USA", "PHL", "PRI"], (172, 150, 104)),
    "CHN": (["CHN", "MNG", "HKG", "MAC"], (226, 184, 120)),
    "NLD": (["NLD", "IDN", "SUR"], (236, 150, 64)),
    "BEL": (["BEL", "COD", "RWA", "BDI", "LUX"], (176, 142, 186)),
    "POR": (["PRT", "AGO", "MOZ", "GNB", "TLS"], (128, 176, 160)),
    "POL": (["POL", "LTU"], (214, 206, 132)),
}
NEUTRAL = [(214, 196, 150), (200, 180, 128), (222, 206, 166), (190, 170, 120), (206, 188, 140), (218, 190, 140), (196, 186, 142)]
CODE = {}
for g, (codes, col) in GROUPS.items():
    for c in codes: CODE.setdefault(c, col)

LABELS = [  # name, lon, lat, size (relative), letter spacing (>= 0.3: spaced capitals)
    ("GERMANY", 10.3, 51.4, 0.5, 0.1), ("POLAND", 19.6, 52.3, 0.46, 0.1), ("FRANCE", 2.4, 46.6, 0.56, 0.1), ("BRITAIN", -1.6, 52.6, 0.36, 0.0),
    ("ITALY", 13.2, 42.4, 0.34, 0.0), ("SPAIN", -3.8, 40.0, 0.5, 0.1), ("U.S.S.R.", 72, 60, 2.2, 0.5), ("TURKEY", 34, 39, 0.5, 0.1),
    ("CHINA", 104, 34, 1.7, 0.5), ("JAPAN", 141.5, 38.6, 0.5, 0.0), ("INDIA", 79, 22, 1.2, 0.4), ("AUSTRALIA", 134, -25, 1.4, 0.4),
    ("EGYPT", 29.8, 26.2, 0.5, 0.0), ("LIBYA", 17.6, 27, 0.6, 0.1), ("ARABIA", 45, 23, 0.8, 0.3), ("ALGERIA", 2, 27.5, 0.62, 0.1),
    ("U.S.A.", -99, 39, 1.8, 0.5), ("CANADA", -105, 58, 1.7, 0.5), ("BRAZIL", -52, -9, 1.4, 0.4), ("MEXICO", -102, 23.5, 0.7, 0.1),
    ("PERSIA", 54, 32.5, 0.62, 0.1), ("MANCHURIA", 126, 46.5, 0.45, 0.0), ("D. E. INDIES", 113, -3.2, 0.55, 0.1), ("SWEDEN", 15.5, 63, 0.4, 0.0),
    ("NORWAY", 9, 61.6, 0.36, 0.0), ("ROMANIA", 25, 45.8, 0.3, 0.0), ("ETHIOPIA", 39.5, 8.5, 0.42, 0.0), ("CONGO", 23, -2.5, 0.62, 0.1),
    ("FR. WEST AFRICA", 0, 16, 0.5, 0.0), ("SUDAN", 30, 14, 0.5, 0.0), ("ARGENTINA", -65, -36, 0.8, 0.1), ("GREENLAND", -41, 73, 0.8, 0.3),
    ("MONGOLIA", 103, 46.5, 0.7, 0.3), ("PHILIPPINES", 124, 11.5, 0.38, 0.0), ("BURMA", 96.5, 21.5, 0.4, 0.0), ("INDOCHINA", 106.5, 14.5, 0.36, 0.0),
    ("KOREA", 127.6, 38.4, 0.3, 0.0), ("FINLAND", 26.5, 63.8, 0.4, 0.0), ("SOUTH AFRICA", 24, -30, 0.55, 0.0), ("NEW ZEALAND", 172, -42, 0.4, 0.0),
    ("ANGOLA", 17.5, -12.5, 0.45, 0.0), ("KENYA", 38, 0.5, 0.36, 0.0), ("CHILE", -71, -30, 0.36, 0.0), ("PERU", -75, -9, 0.45, 0.0),
]
SEAS = [("ATLANTIC OCEAN", -36, 30, 1.2), ("ATLANTIC OCEAN", -18, -22, 1.1), ("PACIFIC OCEAN", 170, 8, 1.4), ("PACIFIC OCEAN", -140, 18, 1.4),
        ("INDIAN OCEAN", 78, -20, 1.2), ("ARCTIC OCEAN", 40, 80, 0.9), ("MEDITERRANEAN", 17, 34.6, 0.48), ("NORTH SEA", 3.5, 56, 0.4),
        ("SEA OF JAPAN", 135, 40.5, 0.42), ("CORAL SEA", 156, -16, 0.6), ("ARABIAN SEA", 63, 14, 0.62), ("BAY OF BENGAL", 89, 14, 0.5),
        ("SOUTH CHINA SEA", 113, 11, 0.42), ("BLACK SEA", 34, 43.3, 0.38), ("CARIBBEAN", -76, 15, 0.5), ("BALTIC", 19, 57.2, 0.3)]

def render(out, W, H, lon0, lon1, lat0, lat1, rose=(0, 0), cart=None, scale=1.0, seed=3):
    random.seed(seed); rng = np.random.default_rng(seed)
    sx = W / (lon1 - lon0); sy = H / (lat0 - lat1)
    def P(lon, lat, off=0): return ((lon + off - lon0) * sx, (lat0 - lat) * sy)
    offs = [o for o in (-360, 0, 360) if lon0 < 180 + o and lon1 > -180 + o]
    polys = []   # (code, ring)
    for f in GEO["features"]:
        g = f["geometry"]; code = f["properties"]["ADM0_A3"]
        if code == "ATA": continue
        parts = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in parts:
            for o in offs: polys.append((code, f["properties"].get("MAPCOLOR7", 1), [P(x, y, o) for x, y in poly[0]]))
    # masks
    land = Image.new("L", (W, H), 0); dl = ImageDraw.Draw(land)
    for _, _, r in polys:
        if len(r) > 2: dl.polygon(r, fill=255)
    LM = np.asarray(land) > 127
    # ocean: deep teal with depth gradient from the coast and painterly mottling
    lab, nl = ndimage.label(LM); sizes = ndimage.sum(LM, lab, range(1, nl + 1))
    BIG = np.isin(lab, 1 + np.nonzero(sizes > 2500 * (W / 4096) ** 2)[0])
    dist = ndimage.distance_transform_edt(~LM) / (W / 4096); distB = ndimage.distance_transform_edt(~BIG) / (W / 4096)
    def noise(sc, oct=4):
        acc = np.zeros((H, W), np.float32); amp = 1.0; tot = 0
        for k in range(oct):
            s = max(2, int(sc / (2 ** k))); g = rng.random((H // s + 2, W // s + 2)).astype(np.float32)
            up = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((W + s * 2, H + s * 2), Image.BICUBIC), np.float32)[:H, :W] / 255
            acc += up * amp; tot += amp; amp *= 0.5
        return acc / tot
    n1 = noise(160 * W / 4096); n2 = noise(30 * W / 4096, 3)
    shallow, deep = np.array([92, 160, 178]), np.array([30, 78, 112])
    t = np.clip(dist / 140, 0, 1)[..., None] ** 0.6
    ocean = shallow * (1 - t) + deep * t
    ocean = ocean * (0.9 + 0.2 * n1[..., None]) * (0.96 + 0.08 * n2[..., None])
    img = ocean
    # water-lining: concentric fading lines round every coast
    wl = np.zeros((H, W), np.float32)
    for k, d in enumerate((7, 14, 22, 31, 41)):
        ring = np.abs(distB - d) < 1.2 * (W / 4096) ** 0.5
        wl = np.maximum(wl, ring * (0.55 - k * 0.09))
    img = img * (1 - wl[..., None]) + np.array([214, 236, 236]) * wl[..., None]
    # graticule on the sea
    gr = Image.new("L", (W, H), 0); dg = ImageDraw.Draw(gr)
    for lo in range(-180, 541, 15):
        x = (lo - lon0) * sx
        if 0 <= x <= W: dg.line([(x, 0), (x, H)], fill=150 if lo % 45 else 230, width=max(1, int(2 * W / 4096)))
    for la in range(-90, 91, 15):
        y = (lat0 - la) * sy
        if 0 <= y <= H: dg.line([(0, y), (W, y)], fill=150 if la % 45 else 230, width=max(1, int(2 * W / 4096)))
    G = np.asarray(gr, np.float32)[..., None] / 255 * 0.35 * (~LM)[..., None]
    img = img * (1 - G) + np.array([200, 226, 230]) * G
    # land relief shadow on the sea (offset blurred mask)
    sh = np.asarray(land.filter(ImageFilter.GaussianBlur(6 * W / 4096)).transform((W, H), Image.AFFINE, (1, 0, -5 * W / 4096, 0, 1, -6 * W / 4096)), np.float32) / 255
    img = img * (1 - 0.45 * sh[..., None] * (~LM)[..., None])
    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    # countries: empire colours with painterly mottling, darker inner edges, border lines
    cl = Image.new("RGB", (W, H), (0, 0, 0)); dc = ImageDraw.Draw(cl)
    for code, mc, r in polys:
        if len(r) > 2: dc.polygon(r, fill=CODE.get(code, NEUTRAL[(mc - 1) % len(NEUTRAL)]))
    C = np.asarray(cl, np.float32)
    inner = ndimage.distance_transform_edt(LM) / (W / 4096)
    edge = np.clip(1 - inner / 10, 0, 1)[..., None]
    C = C * (0.86 + 0.22 * n1[..., None]) * (0.95 + 0.1 * n2[..., None]) * (1 - 0.25 * edge)
    lnd = Image.fromarray(np.clip(C, 0, 255).astype(np.uint8))
    base.paste(lnd, (0, 0), land)
    d = ImageDraw.Draw(base)
    lw = max(2, int(3 * W / 4096))
    for code, mc, r in polys:
        if len(r) > 2: d.line(r + [r[0]], fill=(92, 58, 38), width=lw, joint="curve")
    # country borders (dashed look: a thin dark line over a light one) only inside land
    bd = Image.new("L", (W, H), 0); db = ImageDraw.Draw(bd)
    for code, mc, r in polys:
        if len(r) > 2: db.line(r + [r[0]], fill=255, width=max(1, lw - 1))
    B = (np.asarray(bd) > 0) & (inner > 3 * W / 4096)
    A = np.asarray(base, np.float32); A[B] = A[B] * 0.55 + np.array([70, 40, 30]) * 0.45
    base = Image.fromarray(A.astype(np.uint8)); d = ImageDraw.Draw(base)
    # labels
    def spaced(txt, sp): return (" " * 0).join(txt) if sp < 0.15 else (" ").join(txt) if sp > 0.6 else txt
    fs0 = W / 4096 * 44 * scale * (360 / (lon1 - lon0)) ** 0.75
    for name, lo, la, sz, sp in LABELS:
        for o in offs:
            x, y = P(lo, la, o)
            if not (40 < x < W - 40 and 30 < y < H - 30): continue
            f = ImageFont.truetype(F_BOLD, int(fs0 * sz)); txt = " ".join(name) if sp >= 0.3 and len(name) < 10 else name
            hw = d.textlength(txt, font=f) / 2 + 30
            if x - hw < 0 or x + hw > W: continue
            d.text((x, y), txt, font=f, anchor="mm", fill=(58, 30, 20), stroke_width=max(2, int(fs0 * sz * 0.09)), stroke_fill=(246, 232, 200))
    for name, lo, la, sz in SEAS:
        for o in offs:
            x, y = P(lo, la, o)
            if not (60 < x < W - 60 and 30 < y < H - 30): continue
            f = ImageFont.truetype(F_IT, int(fs0 * sz * 1.05)); txt = "  ".join(" ".join(w) for w in name.split()) if sz >= 0.9 else name
            hw = d.textlength(txt, font=f) / 2 + 40
            if x - hw < 0 or x + hw > W: x = min(max(x, hw), W - hw)
            d.text((x, y), txt, font=f, anchor="mm", fill=(226, 242, 242), stroke_width=max(1, int(fs0 * sz * 0.05)), stroke_fill=(30, 70, 100))
    # compass rose
    cx, cy_ = P(*rose); R = W / 4096 * 150 * scale * (360 / (lon1 - lon0)) ** 0.5
    for k in range(16):
        a = k * math.pi / 8; L = R * (1.0 if k % 4 == 0 else 0.62 if k % 2 == 0 else 0.4); w_ = R * (0.16 if k % 4 == 0 else 0.1)
        tip = (cx + L * math.sin(a), cy_ - L * math.cos(a)); l_ = (cx + w_ * math.sin(a - math.pi / 2), cy_ - w_ * math.cos(a - math.pi / 2)); r_ = (cx + w_ * math.sin(a + math.pi / 2), cy_ - w_ * math.cos(a + math.pi / 2))
        d.polygon([tip, l_, (cx, cy_)], fill=(232, 214, 170) if k % 4 == 0 else (200, 70, 52)); d.polygon([tip, r_, (cx, cy_)], fill=(90, 50, 30))
    for rr, wdt in ((R * 0.5, 3), (R * 0.56, 2), (R * 1.08, 2)): d.ellipse([cx - rr, cy_ - rr, cx + rr, cy_ + rr], outline=(240, 226, 190), width=max(1, int(wdt * W / 4096)))
    fN = ImageFont.truetype(F_BOLD, int(R * 0.3)); d.text((cx, cy_ - R * 1.28), "N", font=fN, anchor="mm", fill=(246, 232, 200), stroke_width=3, stroke_fill=(60, 30, 20))
    # cartouche
    if cart:
        lo, la, title, sub = cart; x, y = P(lo, la); ch = W * 0.04 * scale
        cw = d.textlength(title, font=ImageFont.truetype(F_BOLD, int(ch * 0.62))) / 2 + ch * 0.5
        x = min(max(x, cw + W * 0.02), W - cw - W * 0.02); y = min(max(y, ch + H * 0.03), H - ch - H * 0.03)
        d.rectangle([x - cw, y - ch, x + cw, y + ch], fill=(236, 220, 180), outline=(92, 52, 32), width=max(3, int(6 * W / 4096)))
        d.rectangle([x - cw + 12, y - ch + 12, x + cw - 12, y + ch - 12], outline=(160, 40, 36), width=max(2, int(3 * W / 4096)))
        d.text((x, y - ch * 0.22), title, font=ImageFont.truetype(F_BOLD, int(ch * 0.62)), anchor="mm", fill=(70, 30, 20))
        d.text((x, y + ch * 0.48), sub, font=ImageFont.truetype(F_IT, int(ch * 0.36)), anchor="mm", fill=(140, 40, 34))
    # paper: fibres, stains, folds, vignette, ink border
    A = np.asarray(base, np.float32)
    fib = noise(6 * W / 4096, 2); A *= (0.94 + 0.1 * fib[..., None])
    st = np.zeros((H, W), np.float32)
    for k in range(10):
        x, y, r = random.random() * W, random.random() * H, (0.03 + random.random() * 0.06) * W
        yy, xx = np.ogrid[:H, :W]; dd = np.sqrt((xx - x) ** 2 + (yy - y) ** 2) / r
        st += np.clip(1 - np.abs(dd - 0.9) * 6, 0, 1) * 0.35 + np.clip(1 - dd, 0, 1) * 0.12
    A = A * (1 - 0.35 * st[..., None]) + np.array([150, 100, 50]) * 0.35 * st[..., None]
    for k in range(1, 4):
        x = int(W * k / 4); A[:, x - 2:x + 2] *= 0.82; A[:, x + 2:x + 6] *= 1.07
    y = H // 2; A[y - 2:y + 2] *= 0.82; A[y + 2:y + 6] *= 1.07
    yy, xx = np.ogrid[:H, :W]; v = ((xx / W - 0.5) ** 2 + (yy / H - 0.5) ** 2 * 0.6)
    A *= np.clip(1.08 - v * 1.1, 0.55, 1.1)[..., None]
    A = np.clip(A, 0, 255).astype(np.uint8); im = Image.fromarray(A); d = ImageDraw.Draw(im)
    b = int(W * 0.006); d.rectangle([b, b, W - b, H - b], outline=(70, 40, 26), width=max(3, int(8 * W / 4096)))
    d.rectangle([b * 2.2, b * 2.2, W - b * 2.2, H - b * 2.2], outline=(70, 40, 26), width=max(1, int(3 * W / 4096)))
    im.save(os.path.join(HERE, out), optimize=True); print("saved", out, im.size)

if __name__ == "__main__":
    # void table (12 x 6 m, 26 deg / m): Poland under the first domino at three (0.48, 1.49)
    render("map_void.png", 4096, 2048, -123.5, 188.5, 91, -65, rose=(-30, -45), cart=(-95, -40, "THE WORLD", "in the year 1939"), scale=1.0)
    # war-room table (3.9 x 2.4 m, 60 deg / m): Flanders under the WW1 helmet at three (1.2, 1.7)
    render("map_table.png", 4096, 2520, -42, 192, 80.8, -63, rose=(-25, -40), cart=(165, -50, "THEATRES OF WAR", "General Staff Map  1939"), scale=0.8, seed=5)
    # full world for the globe and the wall map
    render("map_world.png", 2048, 1024, -180, 180, 90, -90, rose=(-30, -45), cart=None, scale=1.0, seed=7)
