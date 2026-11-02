# Period map variants for chapters 2-4 (map table in sets/c02_maproom.py): one equirectangular painted map
# lon -15..165, lat 72..-6, with 1937 borders built from Natural Earth outlines + hand-drawn period overlays
# (1937 Germany incl. East Prussia / Silesia / Pomerania, inter-war Poland, Czechoslovakia incl. Ruthenia, Manchuria),
# borders traced from the political raster (so modern borders never show), labels per year.
#   python3 maps/c02_maps.py        (run from anywhere; writes maps/c02_map_<variant>.png + c02_shapes.json)
import json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = json.load(open(os.path.join(HERE, "ne_50m_countries.geojson")))
FD = "/usr/share/fonts/truetype/"
F_BOLD = FD + "dejavu/DejaVuSerif-Bold.ttf"; F_REG = FD + "dejavu/DejaVuSerif.ttf"
F_IT = FD + "freefont/FreeSerifBoldItalic.ttf" if os.path.exists(FD + "freefont/FreeSerifBoldItalic.ttf") else F_REG
LON0, LON1, LAT0, LAT1 = -15.0, 165.0, 72.0, -6.0
W = int(os.environ.get("MAPW", 8192)); H = int(round(W * (LAT0 - LAT1) / (LON1 - LON0)))
SX = W / (LON1 - LON0); SY = H / (LAT0 - LAT1)
def P(lon, lat): return ((lon - LON0) * SX, (LAT0 - lat) * SY)

PAL = {  # political colours
    "GER": (128, 132, 128), "AUT": (226, 170, 96), "CZS": (176, 142, 196), "POL": (214, 206, 132), "SOV": (196, 72, 62),
    "BRI": (230, 136, 148), "FRA": (112, 128, 196), "ITA": (122, 168, 92), "JAP": (236, 196, 72), "USA": (172, 150, 104),
    "CHN": (226, 184, 120), "NLD": (236, 150, 64), "BEL": (176, 142, 186), "POR": (128, 176, 160), "ETH": (204, 214, 150),
    "HUN": (206, 188, 140), "SVK": (200, 196, 170), "DEN": (214, 160, 120), "NOR": (150, 178, 196), "VIC": (160, 170, 210),
}
GROUPS = {
    "GER": ["DEU"], "AUT": ["AUT"], "CZS": ["CZE", "SVK"], "POL": ["POL"],
    "SOV": ["RUS", "UKR", "BLR", "KAZ", "UZB", "TKM", "KGZ", "TJK", "GEO", "ARM", "AZE", "MDA"],
    "BRI": ["GBR", "CAN", "AUS", "NZL", "IND", "PAK", "BGD", "MMR", "LKA", "ZAF", "EGY", "SDN", "SDS", "KEN", "UGA", "TZA", "NGA", "GHA",
            "ZMB", "ZWE", "MWI", "BWA", "NAM", "IRQ", "JOR", "ISR", "PSX", "MYS", "SGP", "BRN", "SLE", "GMB", "SOL", "IRL", "CYP", "MLT",
            "NPL", "BTN", "LSO", "SWZ", "GUY", "BLZ", "JAM", "BHS", "FJI", "PNG", "KWT", "ARE", "OMN", "YEM", "QAT", "BHR"],
    "FRA": ["FRA", "DZA", "MAR", "TUN", "MRT", "MLI", "NER", "TCD", "SEN", "GIN", "CIV", "BFA", "BEN", "TGO", "CMR", "CAF", "GAB", "COG",
            "MDG", "VNM", "LAO", "KHM", "SYR", "LBN", "DJI", "NCL"],
    "ITA": ["ITA", "LBY", "ERI", "SOM"], "ETH": ["ETH"], "JAP": ["JPN", "KOR", "PRK", "TWN"], "USA": ["USA", "PHL"], "CHN": ["CHN", "HKG", "MAC"],
    "NLD": ["NLD", "IDN"], "BEL": ["BEL", "COD", "RWA", "BDI", "LUX"], "POR": ["PRT", "AGO", "MOZ", "GNB", "TLS"], "HUN": ["HUN"],
    "DEN": ["DNK"], "NOR": ["NOR"],
}
NEUTRAL = [(214, 196, 150), (200, 180, 128), (222, 206, 166), (190, 170, 120), (206, 188, 140), (218, 190, 140), (196, 186, 142)]
# hand-drawn period overlays (lon, lat)
GER_EAST = [(14.2, 53.95), (15.5, 54.2), (16.6, 54.6), (17.6, 54.8), (17.5, 54.2), (17.2, 53.6), (16.4, 53.3), (16.0, 52.8),
            (15.9, 52.3), (16.6, 51.75), (17.5, 51.35), (18.2, 51.2), (18.5, 50.6), (18.65, 50.2), (18.4, 49.95), (17.7, 50.0),
            (16.8, 50.2), (16.2, 50.6), (15.0, 50.9), (14.6, 51.5), (14.6, 52.6)]
EPRUSSIA = [(19.3, 54.4), (19.7, 54.5), (20.4, 54.75), (21.2, 55.2), (21.9, 55.1), (22.8, 54.9), (22.85, 54.4), (22.7, 53.95),
            (22.0, 53.5), (21.0, 53.25), (20.0, 53.25), (19.5, 53.45), (19.2, 53.95)]
POL_EAST = [(22.6, 49.05), (23.4, 48.85), (24.6, 48.4), (25.6, 48.3), (26.25, 48.55), (26.4, 49.9), (27.5, 50.7), (28.2, 51.6),
            (27.6, 52.5), (26.9, 53.5), (27.4, 54.3), (28.3, 55.55), (26.7, 55.75), (25.9, 55.25), (25.0, 54.8), (24.0, 54.15),
            (23.5, 53.95), (23.0, 53.6), (23.5, 52.2), (23.9, 50.4)]
RUTHENIA = [(22.15, 48.4), (22.6, 49.05), (23.4, 48.85), (24.6, 48.15), (24.0, 47.95), (23.0, 47.95), (22.6, 48.1)]
MANCHURIA = [(119.6, 53.3), (121.5, 53.4), (124.5, 53.2), (127.0, 50.4), (130.6, 48.9), (133.0, 48.3), (134.7, 48.3), (133.2, 45.2),
             (131.3, 43.0), (130.5, 42.6), (129.0, 42.2), (128.0, 41.6), (126.6, 41.7), (124.4, 40.0), (122.2, 40.5), (121.0, 40.9),
             (120.2, 40.3), (118.8, 40.2), (117.5, 41.0), (117.0, 42.6), (116.0, 44.8), (117.3, 46.5), (118.6, 47.4), (117.6, 49.4), (119.4, 50.2)]
CHINA_OCC = [(117.0, 42.6), (114.5, 41.0), (112.0, 40.5), (111.0, 38.5), (112.4, 35.6), (113.2, 32.4), (113.0, 30.6), (114.0, 29.2),
             (115.5, 28.6), (117.0, 29.8), (119.0, 30.0), (121.9, 30.6), (121.0, 32.2), (120.8, 34.4), (122.5, 37.4), (121.0, 39.0), (119.6, 39.9)]
SOV_ZONE = [(23.0, 56.0), (31.0, 56.0), (31.0, 47.0), (22.0, 47.0), (22.6, 49.1), (22.75, 49.6), (23.2, 50.3), (24.0, 50.8),
            (23.75, 51.6), (23.6, 52.3), (23.3, 52.9), (23.5, 53.6), (22.9, 54.4)]
VICHY_LINE = [(-1.8, 43.4), (-0.4, 43.6), (0.2, 46.4), (0.7, 47.2), (2.0, 47.0), (3.2, 46.7), (4.7, 46.4), (5.9, 46.25), (6.2, 46.4),
              (7.5, 45.6), (7.8, 43.6), (3.0, 42.3), (-1.8, 43.0)]

LABELS = {  # name: (lon, lat, size, spaced)
    "GERMANY": (11.0, 51.3, 0.55, 0), "AUSTRIA": (14.6, 47.55, 0.32, 0), "CZECHOSLOVAKIA": (17.2, 49.55, 0.26, 0), "POLAND": (22.6, 52.1, 0.5, 0),
    "FRANCE": (2.4, 46.6, 0.56, 0), "BRITAIN": (-1.6, 52.6, 0.36, 0), "ITALY": (13.2, 42.4, 0.34, 0), "SPAIN": (-3.8, 40.0, 0.5, 0),
    "U.S.S.R.": (72, 60, 2.2, 1), "TURKEY": (34, 39, 0.5, 0), "CHINA": (104, 33, 1.7, 1), "JAPAN": (139.4, 36.8, 0.42, 0),
    "INDIA": (79, 22, 1.2, 1), "EGYPT": (29.8, 26.2, 0.5, 0), "LIBYA": (17.6, 27, 0.6, 0), "ARABIA": (45, 23, 0.8, 1), "ALGERIA": (2, 27.5, 0.62, 0),
    "PERSIA": (54, 32.5, 0.62, 0), "MANCHURIA": (126.2, 46.2, 0.42, 0), "SWEDEN": (15.5, 63, 0.4, 0), "NORWAY": (9, 61.6, 0.36, 0),
    "ROMANIA": (25, 45.8, 0.3, 0), "HUNGARY": (19.4, 47.1, 0.26, 0), "YUGOSLAVIA": (19.5, 44.0, 0.26, 0), "ETHIOPIA": (39.5, 8.5, 0.42, 0),
    "SUDAN": (30, 14, 0.5, 0), "MONGOLIA": (103, 46.5, 0.7, 1), "BURMA": (96.5, 21.5, 0.4, 0), "INDOCHINA": (106.5, 14.5, 0.36, 0),
    "KOREA": (127.6, 38.6, 0.26, 0), "FINLAND": (26.5, 63.8, 0.4, 0), "DENMARK": (9.2, 55.95, 0.2, 0), "PHILIPPINES": (124, 11.5, 0.38, 0),
    "D. E. INDIES": (113, -2.2, 0.55, 0), "BELGIUM": (4.6, 50.6, 0.16, 0), "HOLLAND": (5.6, 52.4, 0.16, 0), "SLOVAKIA": (19.4, 48.75, 0.2, 0),
    "BALTIC STATES": (24.5, 57.0, 0.22, 0), "IRAQ": (43.5, 33, 0.36, 0), "VICHY FRANCE": (3.2, 44.8, 0.28, 0), "OCCUPIED CHINA": (116.5, 35.0, 0.36, 0),
}
SEAS = [("ATLANTIC", -11, 46, 0.6), ("PACIFIC OCEAN", 146, 24, 1.1), ("INDIAN OCEAN", 75, 2, 1.1), ("MEDITERRANEAN", 18, 34.4, 0.48),
        ("NORTH SEA", 3.5, 56.2, 0.38), ("SEA OF JAPAN", 134.5, 40.5, 0.4), ("ARABIAN SEA", 63, 14, 0.62), ("BAY OF BENGAL", 89, 14, 0.5),
        ("SOUTH CHINA SEA", 113, 13, 0.42), ("BLACK SEA", 34, 43.3, 0.38), ("BALTIC", 19.2, 57.6, 0.24), ("EAST CHINA SEA", 125.5, 29.5, 0.36)]

VARIANTS = {
    # name: (manchuria jap, occupied china, austria ger, sudeten ger, bohemia ger, poland split, north (DK/NO) ger, france fallen)
    "1931": (0, 0, 0, 0, 0, 0, 0, 0), "1932": (1, 0, 0, 0, 0, 0, 0, 0), "1937": (1, 1, 0, 0, 0, 0, 0, 0), "1938a": (1, 1, 1, 0, 0, 0, 0, 0),
    "1938s": (1, 1, 1, 1, 0, 0, 0, 0), "1939m": (1, 1, 1, 1, 1, 0, 0, 0), "1939p": (1, 1, 1, 1, 1, 1, 0, 0), "1940n": (1, 1, 1, 1, 1, 1, 1, 0),
    "1940f": (1, 1, 1, 1, 1, 1, 1, 1),
}

def noise(rng, sc, oct=4):
    acc = np.zeros((H, W), np.float32); amp = 1.0; tot = 0
    for k in range(oct):
        s = max(2, int(sc / (2 ** k))); g = rng.random((H // s + 2, W // s + 2)).astype(np.float32)
        up = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((W + s * 2, H + s * 2), Image.BICUBIC), np.float32)[:H, :W] / 255
        acc += up * amp; tot += amp; amp *= 0.5
    return acc / tot

def base_rasters():
    """land mask + ISO-code index raster"""
    codes = []; idx = Image.new("I", (W, H), 0); di = ImageDraw.Draw(idx); land = Image.new("L", (W, H), 0); dl = ImageDraw.Draw(land)
    for f in GEO["features"]:
        g = f["geometry"]; code = f["properties"]["ADM0_A3"]
        if code == "ATA": continue
        codes.append((code, f["properties"].get("MAPCOLOR7", 1))); k = len(codes)
        parts = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in parts:
            r = [P(x, y) for x, y in poly[0]]
            if len(r) > 2: di.polygon(r, fill=k); dl.polygon(r, fill=255)
    return np.asarray(land) > 127, np.asarray(idx, np.int32), codes

def poly_mask(pts):
    im = Image.new("L", (W, H), 0); ImageDraw.Draw(im).polygon([P(*p) for p in pts], fill=255); return np.asarray(im) > 127

def political(LM, IDX, codes, v):
    names = list(PAL) + [f"N{k}" for k in range(len(NEUTRAL))]; nid = {n: i for i, n in enumerate(names)}
    code2 = {}
    for g, cs in GROUPS.items():
        for c in cs: code2[c] = nid[g]
    lut = np.zeros(len(codes) + 1, np.int32)
    for k, (c, mc) in enumerate(codes): lut[k + 1] = code2.get(c, nid[f"N{(mc - 1) % len(NEUTRAL)}"])
    L = lut[IDX]
    def paint(pts, g, where=None):
        m = poly_mask(pts) & LM
        if where is not None: m &= where
        L[m] = nid[g]
    paint(POL_EAST, "POL", (L == nid["SOV"]) | (L == nid["POL"]) | np.isin(IDX, [k + 1 for k, (c, _) in enumerate(codes) if c == "LTU"]))
    paint(GER_EAST, "GER"); paint(EPRUSSIA, "GER"); paint(RUTHENIA, "CZS", L == nid["SOV"])
    rou = np.isin(IDX, [k + 1 for k, (c, _) in enumerate(codes) if c == "ROU"]); mda = np.isin(IDX, [k + 1 for k, (c, _) in enumerate(codes) if c == "MDA"])
    if rou.any(): L[mda] = np.bincount(L[rou]).argmax()
    man = poly_mask(MANCHURIA) & LM & (L == nid["CHN"])
    occ = poly_mask(CHINA_OCC) & LM & (L == nid["CHN"]) & ~man
    mj, oc, au, su, bo, ps, no, fr = VARIANTS[v]
    if mj: L[man] = nid["JAP"]
    hatch = np.zeros((H, W), bool)
    if oc: hatch |= occ
    cze = np.isin(IDX, [k + 1 for k, (c, _) in enumerate(codes) if c == "CZE"])
    if au: L[L == nid["AUT"]] = nid["GER"]
    if su:
        ger = (L == nid["GER"])
        d = ndimage.distance_transform_edt(~ger) / SX   # degrees
        L[cze & (d < 0.3)] = nid["GER"]
    if bo:
        L[cze] = nid["GER"]; L[(L == nid["CZS"]) & np.isin(IDX, [k + 1 for k, (c, _) in enumerate(codes) if c == "SVK"])] = nid["SVK"]
        L[L == nid["CZS"]] = nid["HUN"]
    if ps:
        pol = L == nid["POL"]; sz = poly_mask(SOV_ZONE)
        L[pol & sz] = nid["SOV"]; L[pol & ~sz] = nid["GER"]
    if no:
        L[L == nid["DEN"]] = nid["GER"]; L[L == nid["NOR"]] = nid["GER"]
    if fr:
        fra = np.isin(IDX, [k + 1 for k, (c, _) in enumerate(codes) if c in ("FRA",)]); vi = poly_mask(VICHY_LINE)
        L[fra & ~vi] = nid["GER"]; L[fra & vi] = nid["VIC"]
        for c in ("NLD", "BEL", "LUX"): L[np.isin(IDX, [k + 1 for k, (cc, _) in enumerate(codes) if cc == c])] = nid["GER"]
    cols = np.array([PAL[n] if n in PAL else NEUTRAL[int(n[1:])] for n in names], np.float32)
    return L, cols, hatch, man

def labels_for(v):
    mj, oc, au, su, bo, ps, no, fr = VARIANTS[v]
    out = dict(LABELS)
    if au: out.pop("AUSTRIA")
    if bo: out.pop("CZECHOSLOVAKIA")
    else: out.pop("SLOVAKIA")
    if ps: out.pop("POLAND")
    if no: out.pop("DENMARK"); out.pop("NORWAY")
    if not fr: out.pop("VICHY FRANCE")
    else: out.pop("FRANCE"); out.pop("BELGIUM"); out.pop("HOLLAND")
    if not oc: out.pop("OCCUPIED CHINA")
    return out

def render(v, LM, IDX, codes, shared):
    rng = np.random.default_rng(5); random.seed(5)
    n1, n2, dist, distB, GR, SH = shared
    shallow, deep = np.array([92, 160, 178]), np.array([30, 78, 112])
    t = np.clip(dist / 140, 0, 1)[..., None] ** 0.6
    img = (shallow * (1 - t) + deep * t) * (0.9 + 0.2 * n1[..., None]) * (0.96 + 0.08 * n2[..., None])
    wl = np.zeros((H, W), np.float32)
    for k, d in enumerate((7, 14, 22, 31)):
        wl = np.maximum(wl, (np.abs(distB - d) < 1.4) * (0.5 - k * 0.1))
    img = img * (1 - wl[..., None]) + np.array([214, 236, 236]) * wl[..., None]
    img = img * (1 - GR) + np.array([200, 226, 230]) * GR
    img = img * (1 - 0.45 * SH[..., None] * (~LM)[..., None])
    L, cols, hatch, man = political(LM, IDX, codes, v)
    C = cols[L]
    inner = ndimage.distance_transform_edt(LM) / (W / 4096)
    # political edges: a label change between neighbours (land only)
    e = np.zeros((H, W), bool)
    e[:, 1:] |= L[:, 1:] != L[:, :-1]; e[1:, :] |= L[1:, :] != L[:-1, :]
    e &= LM
    pe = ndimage.binary_dilation(e, iterations=max(1, W // 4096))
    dpe = ndimage.distance_transform_edt(~pe) / (W / 4096)
    edge = np.clip(1 - np.minimum(inner, dpe) / 12, 0, 1)[..., None]
    C = C * (0.86 + 0.22 * n1[..., None]) * (0.95 + 0.1 * n2[..., None]) * (1 - 0.28 * edge)
    if hatch.any():
        yy, xx = np.mgrid[0:H, 0:W]; st = ((xx + yy) // max(3, W // 1100)) % 4 == 0
        jc = np.array(PAL["JAP"], np.float32)
        C[hatch] = C[hatch] * 0.45 + jc * 0.55
        C[hatch & st] = C[hatch & st] * 0.55 + np.array([150, 60, 40]) * 0.45
    img[LM] = C[LM]
    A = img
    coast = LM & ~ndimage.binary_erosion(LM, iterations=max(2, W // 2700))
    A[coast] = np.array([92, 58, 38])
    A[pe & ~coast] = A[pe & ~coast] * 0.35 + np.array([70, 30, 24]) * 0.65
    im = Image.fromarray(np.clip(A, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    fs0 = W / 4096 * 44 * 0.8 * (360 / (LON1 - LON0)) ** 0.75
    for name, (lo, la, sz, sp) in labels_for(v).items():
        x, y = P(lo, la); f = ImageFont.truetype(F_BOLD, max(10, int(fs0 * sz))); txt = " ".join(name) if sp else name
        d.text((x, y), txt, font=f, anchor="mm", fill=(58, 30, 20), stroke_width=max(2, int(fs0 * sz * 0.09)), stroke_fill=(246, 232, 200))
    for name, lo, la, sz in SEAS:
        x, y = P(lo, la); f = ImageFont.truetype(F_IT, int(fs0 * sz * 1.05)); txt = "  ".join(" ".join(w) for w in name.split()) if sz >= 0.9 else name
        d.text((x, y), txt, font=f, anchor="mm", fill=(226, 242, 242), stroke_width=max(1, int(fs0 * sz * 0.05)), stroke_fill=(30, 70, 100))
    # compass rose in the Pacific, cartouche in the Indian Ocean
    cx, cy_ = P(150, 4); R = W / 4096 * 150 * 0.9 * (360 / (LON1 - LON0)) ** 0.5
    for k in range(16):
        a = k * math.pi / 8; Lr = R * (1.0 if k % 4 == 0 else 0.62 if k % 2 == 0 else 0.4); w_ = R * (0.16 if k % 4 == 0 else 0.1)
        tip = (cx + Lr * math.sin(a), cy_ - Lr * math.cos(a)); l_ = (cx + w_ * math.sin(a - math.pi / 2), cy_ - w_ * math.cos(a - math.pi / 2)); r_ = (cx + w_ * math.sin(a + math.pi / 2), cy_ - w_ * math.cos(a + math.pi / 2))
        d.polygon([tip, l_, (cx, cy_)], fill=(232, 214, 170) if k % 4 == 0 else (200, 70, 52)); d.polygon([tip, r_, (cx, cy_)], fill=(90, 50, 30))
    for rr, wdt in ((R * 0.5, 3), (R * 1.08, 2)): d.ellipse([cx - rr, cy_ - rr, cx + rr, cy_ + rr], outline=(240, 226, 190), width=max(1, int(wdt * W / 4096)))
    fN = ImageFont.truetype(F_BOLD, int(R * 0.3)); d.text((cx, cy_ - R * 1.28), "N", font=fN, anchor="mm", fill=(246, 232, 200), stroke_width=3, stroke_fill=(60, 30, 20))
    x, y = P(2, 1.5); ch = W * 0.02; title = "EUROPE AND ASIA  " + v[:4]
    cw = d.textlength(title, font=ImageFont.truetype(F_BOLD, int(ch * 0.62))) / 2 + ch * 0.5
    d.rectangle([x - cw, y - ch, x + cw, y + ch], fill=(236, 220, 180), outline=(92, 52, 32), width=max(3, int(6 * W / 4096)))
    d.rectangle([x - cw + 10, y - ch + 10, x + cw - 10, y + ch - 10], outline=(160, 40, 36), width=max(2, int(3 * W / 4096)))
    d.text((x, y - ch * 0.22), title, font=ImageFont.truetype(F_BOLD, int(ch * 0.62)), anchor="mm", fill=(70, 30, 20))
    d.text((x, y + ch * 0.5), "Political Map", font=ImageFont.truetype(F_IT, int(ch * 0.36)), anchor="mm", fill=(140, 40, 34))
    A = np.asarray(im, np.float32)
    A *= (0.94 + 0.1 * shared_fib[..., None])
    for k in range(1, 4):
        xk = int(W * k / 4); A[:, xk - 2:xk + 2] *= 0.84; A[:, xk + 2:xk + 6] *= 1.06
    yk = H // 2; A[yk - 2:yk + 2] *= 0.84; A[yk + 2:yk + 6] *= 1.06
    yy, xx = np.ogrid[:H, :W]; vg = ((xx / W - 0.5) ** 2 + (yy / H - 0.5) ** 2 * 0.6)
    A *= np.clip(1.08 - vg * 1.1, 0.55, 1.1)[..., None]
    A = np.clip(A, 0, 255).astype(np.uint8); im = Image.fromarray(A); d = ImageDraw.Draw(im)
    b = int(W * 0.005); d.rectangle([b, b, W - b, H - b], outline=(70, 40, 26), width=max(3, int(8 * W / 4096)))
    out = os.path.join(HERE, f"c02_map_{v}.jpg"); im.convert("RGB").save(out, quality=90); print("saved", out, im.size, flush=True)

if __name__ == "__main__":
    which = sys.argv[1:] or list(VARIANTS)
    LM, IDX, codes = base_rasters()
    rng = np.random.default_rng(3)
    n1 = noise(rng, 160 * W / 4096); n2 = noise(rng, 30 * W / 4096, 3); shared_fib = noise(rng, 6 * W / 4096, 2)
    lab, nl = ndimage.label(LM); sizes = ndimage.sum(LM, lab, range(1, nl + 1))
    BIG = np.isin(lab, 1 + np.nonzero(sizes > 2500 * (W / 4096) ** 2)[0])
    dist = ndimage.distance_transform_edt(~LM) / (W / 4096); distB = ndimage.distance_transform_edt(~BIG) / (W / 4096)
    gr = Image.new("L", (W, H), 0); dg = ImageDraw.Draw(gr)
    for lo in range(-180, 181, 15):
        x = (lo - LON0) * SX
        if 0 <= x <= W: dg.line([(x, 0), (x, H)], fill=150 if lo % 45 else 230, width=max(1, int(2 * W / 4096)))
    for la in range(-90, 91, 15):
        y = (LAT0 - la) * SY
        if 0 <= y <= H: dg.line([(0, y), (W, y)], fill=150 if la % 45 else 230, width=max(1, int(2 * W / 4096)))
    GR = np.asarray(gr, np.float32)[..., None] / 255 * 0.35 * (~LM)[..., None]
    land = Image.fromarray((LM * 255).astype(np.uint8))
    SH = np.asarray(land.filter(ImageFilter.GaussianBlur(6 * W / 4096)).transform((W, H), Image.AFFINE, (1, 0, -5 * W / 4096, 0, 1, -6 * W / 4096)), np.float32) / 255
    shared = (n1, n2, dist, distB, GR, SH)
    for v in which: render(v, LM, IDX, codes, shared)
    # tile outlines (lon/lat) for the 3D pieces that lift and slide on the table
    shapes = {}
    for f in GEO["features"]:
        c = f["properties"]["ADM0_A3"]
        if c in ("AUT", "CZE", "POL", "DNK", "NOR", "JPN"):
            g = f["geometry"]; parts = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            big = max(parts, key=lambda p: len(p[0])); shapes[c] = [[round(x, 3), round(y, 3)] for x, y in big[0][::2]]
    shapes["MAN"] = MANCHURIA
    json.dump({"extent": [LON0, LON1, LAT0, LAT1], "shapes": shapes}, open(os.path.join(HERE, "c02_shapes.json"), "w"))
    print("shapes saved")
