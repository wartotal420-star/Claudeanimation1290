# Interior kit for the WW2 sets paris / bakery / atelier / playroom: painted numpy textures (flags, banknotes,
# paintings, documents, posters, carpets), grain wood that streaks instead of blotching, velvet, drapes, flags with
# folds, sun shafts, image panels and labels. Works in three.js layout coordinates (lib.T); Blender 4.5 + 5.x safe.
# Only numpy (bundled with Blender) is used for images; no PIL.
import bpy, math, random
import numpy as np
from mathutils import Vector
import lib
from lib import T, TS

# ---------------- small helpers ----------------
def bx(name, c, s, m, bev=0.01, yaw=0.0): return lib.box(name, T(*c), TS(*s), m, bev, rot=(0, 0, yaw))
def cy(name, c, r, h, m, verts=20, rot=(0, 0, 0)): return lib.cyl(name, T(*c), r, h, m, verts, rot)
def bl(name, c, s, m, rough=0.03): return lib.blob(name, T(*c), TS(*s), m, rough)
def sph(name, c, r, m, seg=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(6, seg // 2), radius=r, location=T(*c)); o = bpy.context.object; o.name = name
    o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def cone(name, c, r1, r2, h, m, verts=20, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=T(*c), rotation=rot); o = bpy.context.object; o.name = name
    o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def torus(name, c, R, r, m, rot=(0, 0, 0), maj=32, mi=10):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=maj, minor_segments=mi, location=T(*c), rotation=rot); o = bpy.context.object; o.name = name
    o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def txt(body, c, size, m, yaw=0.0, align="CENTER", extrude=0.002, tilt=0.0):
    """3D text on a surface; yaw 0 faces the cameras (three -z); +90deg faces three -x, -90deg faces three +x."""
    o = lib.text(body, T(*c), size, m, rot=(math.radians(90) + tilt, 0, yaw), align=align, extrude=extrude)
    o.data.align_y = "CENTER"; return o
def hide_from_light(o):
    for a in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        try: setattr(o, a, False)
        except Exception: pass
def sun(target_dir, energy, col, angle=1.5):
    """Sun travelling along target_dir (three coords)."""
    o = lib.light("SUN", T(0, 10, 0), energy, col, math.radians(angle)); lib.look_at(o, o.location + T(*target_dir)); return o
def area(c, target, energy, col, size, size_y=None, spread=None):
    o = lib.light("AREA", T(*c), energy, col, size, size_y=size_y); lib.look_at(o, T(*target))
    if spread is not None:
        try: o.data.spread = math.radians(spread)
        except Exception: pass
    return o
def point(c, energy, col, r=0.05): return lib.light("POINT", T(*c), energy, col, r)
def spot(c, target, energy, col, angle=50, blend=0.6, r=0.05):
    o = lib.light("SPOT", T(*c), energy, col, r); o.data.spot_size = math.radians(angle); o.data.spot_blend = blend; lib.look_at(o, T(*target)); return o

# ---------------- materials ----------------
def _sock(b, *names):
    for nm in names:
        if nm in b.inputs: return b.inputs[nm]
    return None
def grain(name, light, dark, along="X", scale=1.0, rough=0.4, coat=0.0, var=0.25):
    """Varnished wood: stretched fine noise along the grain axis (Blender axis of the object), soft per-board variation."""
    m = lib.principled(name, lib.hexc(light), rough); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    st = {"X": (0.35, 18, 18), "Y": (18, 0.35, 18), "Z": (18, 18, 0.35)}[along]
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = tuple(s * scale for s in st); l.new(tc.outputs["Object"], mp.inputs[0])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 6; nz.inputs["Distortion"].default_value = 0.6
    l.new(mp.outputs[0], nz.inputs["Vector"])
    mp2 = n.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = tuple(s * scale * 7 for s in st); l.new(tc.outputs["Object"], mp2.inputs[0])
    nz2 = n.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 1.0; nz2.inputs["Detail"].default_value = 3; l.new(mp2.outputs[0], nz2.inputs["Vector"])
    big = n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 1.2 * scale; big.inputs["Detail"].default_value = 1; l.new(tc.outputs["Object"], big.inputs["Vector"])
    a1 = n.new("ShaderNodeMath"); a1.operation = "MULTIPLY_ADD"; l.new(nz.outputs["Fac"], a1.inputs[0]); a1.inputs[1].default_value = 0.75; a1.inputs[2].default_value = 0.0
    a2 = n.new("ShaderNodeMath"); a2.operation = "MULTIPLY_ADD"; l.new(nz2.outputs["Fac"], a2.inputs[0]); a2.inputs[1].default_value = 0.25 - var * 0.5; l.new(a1.outputs[0], a2.inputs[2])
    a3 = n.new("ShaderNodeMath"); a3.operation = "MULTIPLY_ADD"; l.new(big.outputs["Fac"], a3.inputs[0]); a3.inputs[1].default_value = var; l.new(a2.outputs[0], a3.inputs[2])
    lc, dc = lib.hexc(light), lib.hexc(dark)
    mid = tuple((x + y) / 2 for x, y in zip(lc, dc))
    r = lib.ramp(n, l, a3.outputs[0], [(0.38, dc), (0.5, mid), (0.62, lc)])
    l.new(r.outputs["Color"], b.inputs["Base Color"])
    bm = n.new("ShaderNodeBump"); bm.inputs["Strength"].default_value = 0.08; bm.inputs["Distance"].default_value = 0.002
    l.new(nz2.outputs["Fac"], bm.inputs["Height"]); l.new(bm.outputs["Normal"], b.inputs["Normal"])
    if coat:
        s = _sock(b, "Coat Weight", "Coat")
        if s: s.default_value = coat
        s = _sock(b, "Coat Roughness")
        if s: s.default_value = 0.08
    return m
def planks(name, light, dark, along="Y", width=0.16, length=1.6, rough=0.35, coat=0.25, diag=False):
    """Floor boards along a Blender axis: grain wood x per-board tint x dark seams."""
    m = grain(name, light, dark, along, 1.0, rough, coat, 0.15); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); mp = n.new("ShaderNodeMapping"); l.new(tc.outputs["Object"], mp.inputs[0])
    rz = math.radians(45) if diag else (math.radians(90) if along == "Y" else 0)
    mp.inputs["Rotation"].default_value = (0, 0, rz)
    br = n.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 1.0; br.offset = 0.37; br.offset_frequency = 1
    br.inputs["Brick Width"].default_value = length; br.inputs["Row Height"].default_value = width; br.inputs["Mortar Size"].default_value = 0.004
    br.inputs["Mortar Smooth"].default_value = 0.3; br.inputs["Bias"].default_value = 0.0
    br.inputs["Color1"].default_value = (1, 1, 1, 1); br.inputs["Color2"].default_value = (0.72, 0.66, 0.6, 1); br.inputs["Mortar"].default_value = (0.12, 0.08, 0.06, 1)
    l.new(mp.outputs[0], br.inputs["Vector"])
    ramp_node = [x for x in n if x.bl_idname == "ShaderNodeValToRGB"][0]
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1.0
    l.new(ramp_node.outputs["Color"], mx.inputs[6]); l.new(br.outputs["Color"], mx.inputs[7]); l.new(mx.outputs[2], b.inputs["Base Color"])
    return m
def velvet(name, col, sheen=1.0):
    m = lib.cloth(name, col); b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.75
    s = _sock(b, "Sheen Weight", "Sheen")
    if s: s.default_value = sheen
    s = _sock(b, "Sheen Tint")
    if s:
        try: s.default_value = (1.0, 0.75, 0.7, 1)
        except Exception: s.default_value = 0.5
    return m
def metal(name, col, rough=0.25): return lib.principled(name, lib.hexc(col), rough, 1.0)
def flat(name, col, rough=0.6): return lib.principled(name, lib.hexc(col), rough)
def shadowless_glass(o):
    hide_from_light(o)
    try: o.visible_glossy = True
    except Exception: pass

# ---------------- numpy painting ----------------
def new_img(name, a):
    """a: (h, w, 3|4) float array in sRGB 0..1, row 0 = TOP. Returns a packed image."""
    a = np.clip(np.asarray(a, np.float32), 0, 1); h, w = a.shape[:2]
    if a.shape[2] == 3: a = np.concatenate([a, np.ones((h, w, 1), np.float32)], 2)
    im = bpy.data.images.new(name, w, h, alpha=True)
    im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel())
    try: im.pack()
    except Exception as e: print("pack", e)
    return im
def rgb(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
def canvas(h, w, col): a = np.empty((h, w, 3), np.float32); a[:] = rgb(col) if isinstance(col, str) else col; return a
def grid(a):
    h, w = a.shape[:2]; y, x = np.mgrid[0:h, 0:w].astype(np.float32); return x / w, y / h
def vnoise(h, w, cells, seed=0, octaves=3):
    rs = np.random.RandomState(seed); out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        cx = max(2, int(cells * 2 ** o)); cyy = max(2, int(cells * 2 ** o * h / w))
        g = rs.rand(cyy + 2, cx + 2).astype(np.float32)
        ys = np.linspace(0, cyy, h); xs = np.linspace(0, cx, w)
        y0 = ys.astype(int); x0 = xs.astype(int); fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        v = (g[y0][:, x0] * (1 - fx) + g[y0][:, x0 + 1] * fx) * (1 - fy) + (g[y0 + 1][:, x0] * (1 - fx) + g[y0 + 1][:, x0 + 1] * fx) * fy
        out += v * amp; tot += amp; amp *= 0.5
    return out / tot
def soft(v, lo, hi): t = np.clip((v - lo) / (hi - lo), 0, 1); return t * t * (3 - 2 * t)
def put(a, mask, col, op=1.0):
    c = rgb(col) if isinstance(col, str) else np.asarray(col, np.float32)
    m = (mask.astype(np.float32) * op)[..., None]; a[:] = a * (1 - m) + c * m
def rect(a, x0, y0, x1, y1, col, op=1.0):
    x, y = grid(a); put(a, (x >= x0) & (x < x1) & (y >= y0) & (y < y1), col, op)
def frame_border(a, t, col):
    x, y = grid(a); h, w = a.shape[:2]; ty = t * w / h
    put(a, (x < t) | (x > 1 - t) | (y < ty) | (y > 1 - ty), col)
def ellipse(a, cx, cy_, rx, ry, col, op=1.0, ring=0.0):
    x, y = grid(a); d = ((x - cx) / rx) ** 2 + ((y - cy_) / ry) ** 2
    put(a, (d <= 1) & (d >= (1 - ring) ** 2 if ring else d <= 1), col, op)
def poly(a, pts, col, op=1.0):
    """Filled convex/concave polygon, pts in 0..1 (x right, y down)."""
    x, y = grid(a); inside = np.zeros(x.shape, bool); n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        cond = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-9) + x1)
        inside ^= cond
    put(a, inside, col, op)
def shade(a, amount=0.12, seed=0, cells=24):
    """Painterly brush variation."""
    h, w = a.shape[:2]; nz = vnoise(h, w, cells, seed, 3); a *= (1 - amount + 2 * amount * nz)[..., None]
def vignette(a, k=0.35):
    x, y = grid(a); d = ((x - 0.5) ** 2 + (y - 0.5) ** 2) * 2; a *= (1 - k * d)[..., None]

FONT = {
    "0": (14, 17, 19, 21, 25, 17, 14), "1": (4, 12, 4, 4, 4, 4, 14), "2": (14, 17, 1, 2, 4, 8, 31), "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2), "5": (31, 16, 30, 1, 1, 17, 14), "6": (6, 8, 16, 30, 17, 17, 14), "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14), "9": (14, 17, 17, 15, 1, 2, 12), "A": (14, 17, 17, 17, 31, 17, 17), "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14), "D": (28, 18, 17, 17, 17, 18, 28), "E": (31, 16, 16, 30, 16, 16, 31), "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15), "H": (17, 17, 17, 31, 17, 17, 17), "I": (14, 4, 4, 4, 4, 4, 14), "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17), "L": (16, 16, 16, 16, 16, 16, 31), "M": (17, 27, 21, 21, 17, 17, 17), "N": (17, 17, 25, 21, 19, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14), "P": (30, 17, 17, 30, 16, 16, 16), "Q": (14, 17, 17, 17, 21, 18, 13), "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30), "T": (31, 4, 4, 4, 4, 4, 4), "U": (17, 17, 17, 17, 17, 17, 14), "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10), "X": (17, 17, 10, 4, 10, 17, 17), "Y": (17, 17, 17, 10, 4, 4, 4), "Z": (31, 1, 2, 4, 8, 16, 31),
    ".": (0, 0, 0, 0, 0, 12, 12), ",": (0, 0, 0, 0, 12, 4, 8), "-": (0, 0, 0, 31, 0, 0, 0), ":": (0, 12, 12, 0, 12, 12, 0), "!": (4, 4, 4, 4, 4, 0, 4),
    "=": (0, 0, 31, 0, 31, 0, 0), "$": (4, 15, 20, 14, 5, 30, 4), "/": (1, 1, 2, 4, 8, 16, 16), " ": (0,) * 7, "'": (4, 4, 8, 0, 0, 0, 0),
    "Ä": (10, 0, 14, 17, 31, 17, 17), "Ü": (10, 0, 17, 17, 17, 17, 14), "Ö": (10, 0, 14, 17, 17, 17, 14), "É": (2, 4, 31, 16, 30, 16, 31),
}
def stamp(a, s, x, y, hgt, col, op=1.0, bold=0.0, align="left"):
    """Bitmap text: x,y = top-left (0..1), hgt = glyph height as a fraction of the image height."""
    h, w = a.shape[:2]; px = hgt * h / 7.0; adv = 6 * px
    width = len(s) * adv / w
    if align == "center": x -= width / 2
    elif align == "right": x -= width
    c = rgb(col) if isinstance(col, str) else np.asarray(col, np.float32)
    for k, ch in enumerate(s.upper()):
        g = FONT.get(ch, FONT[" "]); ox = x * w + k * adv
        for r, bits in enumerate(g):
            for cbit in range(5):
                if bits >> (4 - cbit) & 1:
                    x0 = int(ox + cbit * px - bold * px); x1 = int(ox + (cbit + 1) * px + bold * px + 0.999)
                    y0 = int(y * h + r * px); y1 = int(y * h + (r + 1) * px + 0.999)
                    if x1 > 0 and y1 > 0 and x0 < w and y0 < h:
                        a[max(0, y0):min(h, y1), max(0, x0):min(w, x1)] = a[max(0, y0):min(h, y1), max(0, x0):min(w, x1)] * (1 - op) + c * op
    return width

# ---- specific images ----
def flag_img(kind, w=384, h=256):
    a = canvas(h, w, "#ffffff"); x, y = grid(a)
    if kind in ("fr", "it"):
        cols = ("#1f3f8f", "#f4f1ea", "#d2232e") if kind == "fr" else ("#1d8a3c", "#f4f1ea", "#d2232e")
        for i, c in enumerate(cols): put(a, (x >= i / 3) & (x < (i + 1) / 3), c)
        if kind == "it":  # Savoy shield
            rect(a, 0.44, 0.33, 0.56, 0.62, "#3a6ac8"); rect(a, 0.455, 0.35, 0.545, 0.6, "#d2232e"); rect(a, 0.49, 0.37, 0.51, 0.58, "#f4f1ea"); rect(a, 0.465, 0.45, 0.535, 0.49, "#f4f1ea")
    elif kind == "uk":
        put(a, x >= 0, "#1d2f6e"); X = (x - 0.5) * 2; Y = (y - 0.5); k = 0.5
        d1 = np.abs(Y - k * X) / math.sqrt(1 + k * k); d2 = np.abs(Y + k * X) / math.sqrt(1 + k * k)
        put(a, (d1 < 0.1) | (d2 < 0.1), "#f4f1ea"); put(a, ((d1 < 0.035) & (X * Y > 0)) | ((d2 < 0.035) & (X * Y < 0)), "#c8202c")
        put(a, (np.abs(X) < 0.17) | (np.abs(Y) < 0.17), "#f4f1ea"); put(a, (np.abs(X) < 0.1) | (np.abs(Y) < 0.1), "#c8202c")
    elif kind == "us":
        for i in range(13): put(a, (y >= i / 13) & (y < (i + 1) / 13), "#b8202e" if i % 2 == 0 else "#f4f1ea")
        rect(a, 0, 0, 0.4, 7 / 13, "#2a3070")
        for r in range(9):
            for c in range(11 if r % 2 == 0 else 10):
                ellipse(a, 0.02 + (c + (0.5 if r % 2 else 0)) * 0.034, 0.03 + r * 0.054, 0.008, 0.012, "#f4f1ea")
    elif kind == "jp":
        put(a, x >= 0, "#f4f1ea"); ellipse(a, 0.5, 0.5, 0.2, 0.3, "#c8202c")
    shade(a, 0.06, hash(kind) % 100, 16)
    return a
def banknote_img(seed=0, value="1000", col="#a8c890", ink="#2e4a32", w=300, h=150):
    a = canvas(h, w, col); x, y = grid(a)
    put(a, np.sin(x * 160 + np.sin(y * 30 + seed) * 3) > 0.6, ink, 0.12)
    put(a, np.sin(y * 120 + np.sin(x * 25) * 4) > 0.75, ink, 0.1)
    frame_border(a, 0.03, ink); rect(a, 0.05, 0.1, 0.95, 0.9, ink, 0.0)
    xb, yb = grid(a); put(a, ((xb > 0.055) & (xb < 0.065) | (xb > 0.935) & (xb < 0.945)) & (yb > 0.11) & (yb < 0.89), ink)
    put(a, ((yb > 0.1) & (yb < 0.12) | (yb > 0.88) & (yb < 0.9)) & (xb > 0.055) & (xb < 0.945), ink)
    ellipse(a, 0.5, 0.5, 0.115, 0.33, ink); ellipse(a, 0.5, 0.5, 0.1, 0.3, "#ece0bc")
    ellipse(a, 0.5, 0.45, 0.04, 0.09, "#c8b890"); ellipse(a, 0.5, 0.66, 0.065, 0.1, "#b8a880")
    stamp(a, value, 0.215, 0.4, 0.17, ink, align="center", bold=0.12); stamp(a, value, 0.785, 0.4, 0.17, ink, align="center", bold=0.12)
    stamp(a, "REICHSBANKNOTE", 0.5, 0.15, 0.08, ink, align="center"); stamp(a, "MARK", 0.5, 0.86, 0.06, ink, align="center")
    shade(a, 0.08, seed, 12)
    return a
def doc_img(seed=0, title="TRAITÉ DE PAIX", w=256, h=340, col="#f3ead2", lines=True, seal=False):
    rs = random.Random(seed); a = canvas(h, w, col); shade(a, 0.05, seed, 6)
    if title: stamp(a, title, 0.5, 0.06, 0.03, "#2a221a", align="center", bold=0.2)
    y = 0.14
    while lines and y < 0.9:
        if rs.random() < 0.12: y += 0.025; continue
        ln = rs.uniform(0.55, 0.84) if rs.random() < 0.85 else rs.uniform(0.2, 0.5)
        rect(a, 0.08, y, 0.08 + ln, y + 0.009, "#4a4036", 0.75); y += 0.024
    if seal: ellipse(a, 0.78, 0.86, 0.09, 0.068, "#a81c22"); ellipse(a, 0.78, 0.86, 0.06, 0.045, "#7a1018")
    return a
def landscape_img(seed=0, w=384, h=288, house=False, naive=False, water=False):
    rs = np.random.RandomState(seed); a = canvas(h, w, "#ffffff"); x, y = grid(a)
    horizon = 0.55 + rs.uniform(-0.08, 0.06)
    sky_top, sky_bot = (rgb("#4a78b8"), rgb("#f2d6a8")) if not naive else (rgb("#8fbde6"), rgb("#b8d8f0"))
    t = np.clip(y / horizon, 0, 1)[..., None]; a[:] = sky_top * (1 - t) + sky_bot * t
    if not naive:
        cl = vnoise(h, w, 5, seed + 1, 4); put(a, soft(cl, 0.5, 0.7) * (y < horizon), "#fbf3e6", 0.75)
        hills = horizon - 0.1 * vnoise(1, w, 4, seed + 2, 2)[0]
        put(a, y > hills[None, :] * np.ones((h, 1)), "#7a8eaa")
    gr = horizon + 0.04 * (vnoise(1, w, 3, seed + 3, 2)[0] - 0.5)
    ground = y > gr[None, :] * np.ones((h, 1))
    put(a, ground, "#5f8a3e" if not naive else "#6a9a4a")
    if not naive:
        f = vnoise(h, w, 6, seed + 4, 3); put(a, ground * soft(f, 0.45, 0.65), "#a89a42", 0.55)
        put(a, ground * soft(y, gr.mean(), 1.0), "#3a5a28", 0.5)
        if water: put(a, ground & (y > horizon + 0.15) & (y < horizon + 0.26), "#5a86b0", 0.9)
        for k in range(rs.randint(3, 7)):
            tx_, ty = rs.uniform(0.05, 0.95), horizon + rs.uniform(-0.01, 0.05); s = rs.uniform(0.03, 0.07)
            rect(a, tx_ - 0.004, ty, tx_ + 0.004, ty + s * 0.9, "#3a2a1a"); ellipse(a, tx_, ty - s * 0.3, s * 0.6, s * 1.1, "#2f5a2a")
    if house or naive:
        hx = rs.uniform(0.35, 0.6) if not naive else 0.5; hw = 0.16 if naive else 0.1; hy = horizon + (0.12 if naive else 0.02)
        rect(a, hx - hw / 2, hy - hw * 1.1, hx + hw / 2, hy, "#efdfb0"); poly(a, [(hx - hw * 0.65, hy - hw * 1.1), (hx, hy - hw * 1.9), (hx + hw * 0.65, hy - hw * 1.1)], "#b84a3e")
        rect(a, hx - hw * 0.1, hy - hw * 0.5, hx + hw * 0.1, hy, "#6a4a2a")
    shade(a, 0.1 if not naive else 0.03, seed, 30)
    return a
def portrait_img(seed=0, w=256, h=320):
    rs = np.random.RandomState(seed); a = canvas(h, w, "#2a1c14"); x, y = grid(a)
    put(a, np.ones_like(x, bool), rgb("#5a3a22"), 0.0)
    g = np.clip(1 - ((x - 0.45) ** 2 + (y - 0.35) ** 2) * 3, 0, 1); a += (g * 0.25)[..., None] * rgb("#c89a5a")
    coat = rs.choice(["#1e2a44", "#22201e", "#3a2a2a", "#2a3a2a"])
    ellipse(a, 0.5, 1.02, 0.42, 0.45, coat); rect(a, 0.44, 0.62, 0.56, 1.0, "#f2ece0")
    if rs.rand() < 0.6: poly(a, [(0.2, 0.7), (0.32, 0.66), (0.8, 1.0), (0.66, 1.0)], "#b8202c")
    ellipse(a, 0.5, 0.42, 0.13, 0.17, "#e8b890"); ellipse(a, 0.5, 0.28, 0.14, 0.08, rs.choice(["#2a1a10", "#8a8a88", "#d8d4cc"]))
    ellipse(a, 0.5, 0.53, 0.08, 0.04, rs.choice(["#3a2a1a", "#d8d4cc", "#8a8a88"]), 0.9)
    for k in range(rs.randint(1, 4)): ellipse(a, 0.62 + k * 0.05, 0.8, 0.018, 0.024, "#e8c060")
    shade(a, 0.12, seed, 30); vignette(a, 0.5)
    return a
def fresco_img(seed=0, w=384, h=256):
    a = canvas(h, w, "#7fa8d6"); x, y = grid(a)
    g = np.clip(1 - ((x - 0.5) ** 2 + (y - 0.5) ** 2) * 2.2, 0, 1); a[:] = a * (1 - g[..., None] * 0.6) + rgb("#f6dca0") * (g[..., None] * 0.6)
    cl = vnoise(h, w, 4, seed, 4); put(a, soft(cl, 0.45, 0.62), "#fbf0dc", 0.85); put(a, soft(cl, 0.4, 0.5) * (1 - soft(cl, 0.5, 0.6)), "#d8b890", 0.35)
    rs = np.random.RandomState(seed)
    for k in range(3):
        cx, cyy = rs.uniform(0.2, 0.8), rs.uniform(0.3, 0.7)
        ellipse(a, cx, cyy, 0.05, 0.1, rs.choice(["#c8423a", "#3a5aa8", "#e8c060"])); ellipse(a, cx, cyy - 0.14, 0.03, 0.05, "#f0c8a0")
    shade(a, 0.08, seed, 20)
    return a
def carpet_img(w=192, h=960, field="#8a1a20", border="#d8a840", accent="#1e2a5a"):
    a = canvas(h, w, field); x, y = grid(a)
    put(a, np.sin(x * 60) * np.sin(y * 300) > 0.6, "#a82830", 0.6)
    ab = 1 - np.minimum(np.minimum(x, 1 - x) * w, np.minimum(y, 1 - y) * h) / w
    put(a, ab > 0.88, border); put(a, (ab > 0.9) & (ab < 0.94), accent); put(a, ab > 0.97, "#3a1010")
    for k in range(8):
        cyy = (k + 0.5) / 8; d = np.abs(x - 0.5) * 2 + np.abs(y - cyy) * h / w * 2 * 0.7
        put(a, (d < 0.55) & (d > 0.42), border); put(a, d < 0.3, accent); put(a, d < 0.12, border)
    put(a, (np.sin(y * 600) > 0.85) & (ab > 0.9) & (ab < 0.97), "#f2e0b0", 0.6)
    shade(a, 0.1, 7, 40)
    return a

def img_mat(name, arr_or_img, rough=0.6, emit=0.0, coat=0.0, metal=0.0, coords="UV", sheen=0.0):
    im = arr_or_img if isinstance(arr_or_img, bpy.types.Image) else new_img(name + "_im", arr_or_img)
    m = bpy.data.materials.new(name); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tex = n.new("ShaderNodeTexImage"); tex.image = im; tex.interpolation = "Linear"
    if coords != "UV":
        tc = n.new("ShaderNodeTexCoord"); l.new(tc.outputs[coords], tex.inputs["Vector"])
    l.new(tex.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        l.new(tex.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit
    if coat:
        s = _sock(b, "Coat Weight")
        if s: s.default_value = coat
    if sheen:
        s = _sock(b, "Sheen Weight")
        if s: s.default_value = sheen
    return m

# ---------------- geometry ----------------
def panel(name, c, w, h, m, yaw=0.0, pitch=0.0):
    """Upright image quad centred at c (three), facing the cameras (three -z) at yaw 0; UV 0..1, u to screen right."""
    me = bpy.data.meshes.new(name); me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for k, cc in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = cc
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    o.location = T(*c); o.rotation_euler = (pitch, 0, yaw); me.materials.append(m); return o
def floor_quad(name, c, w, d, m, yaw=0.0, y=0.0):
    """Flat image quad on the floor: w along three x, d along three z; u to screen right, v away from camera."""
    me = bpy.data.meshes.new(name); me.from_pydata([(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for k, cc in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = cc
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    o.location = T(c[0], y, c[1]); o.rotation_euler = (0, 0, yaw); me.materials.append(m); return o
def framed(name, c, w, h, img_m, frame_m, yaw=0.0, fw=0.08, depth=0.05):
    """Painting / poster in a frame on a wall, picture face toward yaw."""
    pn = panel(name, c, w, h, img_m, yaw)
    for k, (dx, dy, sw, sh) in enumerate(((0, h / 2 + fw / 2, w + 2 * fw, fw), (0, -h / 2 - fw / 2, w + 2 * fw, fw), (w / 2 + fw / 2, 0, fw, h), (-w / 2 - fw / 2, 0, fw, h))):
        o = lib.box(f"{name}f{k}", (0, 0, 0), (sw, depth, sh), frame_m, min(0.01, fw * 0.3)); o.parent = pn
        o.location = (dx, -depth / 2 + 0.01, dy)
    return pn
def grid_mesh(name, nx, ny, fn, m):
    """Mesh from a function fn(u, v) -> Blender Vector, with UVs; for drapes and flags."""
    verts = [fn(i / nx, j / ny) for j in range(ny + 1) for i in range(nx + 1)]
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(ny) for i in range(nx)]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); uv = me.uv_layers.new()
    for p in me.polygons:
        for li in p.loop_indices:
            vi = me.loops[li].vertex_index; uv.data[li].uv = ((vi % (nx + 1)) / nx, (vi // (nx + 1)) / ny)
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); me.materials.append(m)
    sd = o.modifiers.new("s", "SOLIDIFY"); sd.thickness = 0.008
    return o
def drape(name, c, w, h, m, yaw=0.0, folds=6, depth=0.07, gather=0.0):
    """Curtain hanging from top centre c (three), width w, folded; gather pinches the bottom (tie-back) toward u=gather side."""
    cy_, sy = math.cos(yaw), math.sin(yaw); base = T(*c)
    def fn(u, v):
        k = 1.0
        if gather:
            k = 1.0 if v > 0.75 else (0.3 + 0.7 * (v - 0.35) / 0.4 if v > 0.35 else 0.3 + 0.25 * (0.35 - v) / 0.35)
        uu = (u - 0.5) * w * k + (gather * w * 0.35 * (1 - k) if gather else 0)
        off = depth * math.sin(u * folds * 2 * math.pi) * (0.7 + 0.5 * (1 - k)) * (0.8 + 0.2 * v)
        lx, ly, lz = uu, off, -(1 - v) * h
        return base + Vector((lx * cy_ - ly * sy, lx * sy + ly * cy_, lz))
    return grid_mesh(name, folds * 8, 12, fn, m)
def flag(name, c, w, h, m, yaw=0.0, wave=0.05, waves=2.5):
    """Flag from hoist top corner c (three), extending to screen right (three -x at yaw 0), with soft folds."""
    cy_, sy = math.cos(yaw), math.sin(yaw); base = T(*c)
    def fn(u, v):
        off = wave * math.sin(u * waves * 2 * math.pi + v * 1.2) * min(1, u * 4)
        lx, ly, lz = u * w, off, -(1 - v) * h - 0.06 * u * u * h
        return base + Vector((lx * cy_ - ly * sy, lx * sy + ly * cy_, lz))
    return grid_mesh(name, 40, 10, fn, m)
def beam(name, quad, d, length, col, strength=0.6, spread=1.08):
    """Soft sun shaft: a frustum from a window quad (4 three points) along direction d. Camera-only, no shadows."""
    d = Vector(d).normalized(); P = [Vector(p) for p in quad]; ctr = sum(P, Vector()) / 4
    Q = [ctr + (p - ctr) * spread + d * length for p in P]
    verts = [T(*p) for p in P] + [T(*q) for q in Q]
    faces = [(i, (i + 1) % 4, 4 + (i + 1) % 4, 4 + i) for i in range(4)]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); uv = me.uv_layers.new()
    for p in me.polygons:
        for li in p.loop_indices:
            vi = me.loops[li].vertex_index; uv.data[li].uv = ((vi % 4) / 3, 0 if vi < 4 else 1)
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    m = bpy.data.materials.new(name + "m"); t, n, l = lib.nodes(m)
    for x in list(n): n.remove(x)
    out = n.new("ShaderNodeOutputMaterial"); tr = n.new("ShaderNodeBsdfTransparent"); em = n.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*col, 1)
    add = n.new("ShaderNodeAddShader"); lw = n.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    inv = n.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; l.new(lw.outputs["Facing"], inv.inputs[1])
    pw = n.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 3.0; l.new(inv.outputs[0], pw.inputs[0])
    tc = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["UV"], sep.inputs[0])
    fade = n.new("ShaderNodeMath"); fade.operation = "SUBTRACT"; fade.inputs[0].default_value = 1.0; l.new(sep.outputs[1], fade.inputs[1])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; mpn = n.new("ShaderNodeMapping"); mpn.inputs["Scale"].default_value = (6, 0.3, 1)
    l.new(tc.outputs["UV"], mpn.inputs[0]); l.new(mpn.outputs[0], nz.inputs["Vector"])
    m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; l.new(pw.outputs[0], m1.inputs[0]); l.new(fade.outputs[0], m1.inputs[1])
    m2 = n.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; l.new(m1.outputs[0], m2.inputs[0]); l.new(nz.outputs["Fac"], m2.inputs[1])
    m3 = n.new("ShaderNodeMath"); m3.operation = "MULTIPLY"; l.new(m2.outputs[0], m3.inputs[0]); m3.inputs[1].default_value = strength
    l.new(m3.outputs[0], em.inputs["Strength"]); l.new(tr.outputs[0], add.inputs[0]); l.new(em.outputs[0], add.inputs[1]); l.new(add.outputs[0], out.inputs["Surface"])
    try: m.blend_method = "BLEND"
    except Exception: pass
    me.materials.append(m); hide_from_light(o)
    return o
def note_stack(name, c, size, yaw, note_m, edge_m=None, band_m=None):
    """A bundle of banknotes: printed top, paper edges, a paper band. size = (w along x, h, d along z) three."""
    w, h, d = size; o = bx(name, c, size, note_m, 0.002, yaw)
    if band_m: bx(name + "b", (c[0], c[1], c[2]), (w * 0.18, h + 0.004, d + 0.004), band_m, 0.001, yaw)
    return o
def stack_mat(name, note_img, edge="#e8e2c8"):
    """Bundle material: top/bottom faces show the note (Generated XY), sides show stacked paper edges."""
    m = bpy.data.materials.new(name); t, n, l = lib.nodes(m); b = n["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.75
    tc = n.new("ShaderNodeTexCoord"); tex = n.new("ShaderNodeTexImage"); tex.image = note_img; l.new(tc.outputs["Generated"], tex.inputs["Vector"])
    geo = n.new("ShaderNodeNewGeometry"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(geo.outputs["Normal"], sep.inputs[0])
    ab = n.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; l.new(sep.outputs[2], ab.inputs[0])
    gt = n.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.6; l.new(ab.outputs[0], gt.inputs[0])
    wv = n.new("ShaderNodeTexWave"); wv.bands_direction = "Z"; wv.inputs["Scale"].default_value = 18; l.new(tc.outputs["Generated"], wv.inputs["Vector"])
    er = lib.ramp(n, l, wv.outputs["Fac"], [(0.2, lib.hexc("#8a9a78")), (0.6, lib.hexc(edge))])
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(gt.outputs[0], mx.inputs[0]); l.new(er.outputs["Color"], mx.inputs[6]); l.new(tex.outputs["Color"], mx.inputs[7])
    l.new(mx.outputs[2], b.inputs["Base Color"])
    return m
def chair(name, x, z, yaw, wood_m, seat_m, h=0.46, back=True, gilt_m=None):
    """A simple period chair: turned legs, upholstered seat, back with top rail; faces three -z at yaw 0 (back toward +z)."""
    cy_, sy = math.cos(yaw), math.sin(yaw)
    def P(dx, y, dz): return (x + dx * cy_ + dz * sy, y, z - dx * sy + dz * cy_)
    bx(name + "s", P(0, h, 0), (0.46, 0.07, 0.44), seat_m, 0.02, yaw)
    for dx in (-0.19, 0.19):
        for dz in (-0.18, 0.18): cy(f"{name}l{dx}{dz}", P(dx, h / 2, dz), 0.022, h, wood_m, 8)
    if back:
        for dx in (-0.2, 0.2): cy(f"{name}p{dx}", P(dx, h + 0.3, 0.2), 0.02, 0.6, wood_m, 8)
        bx(name + "bk", P(0, h + 0.32, 0.21), (0.36, 0.42, 0.05), seat_m, 0.02, yaw)
        bx(name + "tr", P(0, h + 0.6, 0.2), (0.48, 0.05, 0.05), gilt_m or wood_m, 0.01, yaw)
def books(name, x0, y, z, n, mats, yaw=0.0, depth=0.2, lean=True, rs=None):
    rs = rs or random.Random(len(name)); x = x0; cy_, sy = math.cos(yaw), math.sin(yaw)
    for k in range(n):
        th = rs.uniform(0.03, 0.06); hh = rs.uniform(0.18, 0.27)
        px, pz = x0 + (x - x0) * cy_, z - (x - x0) * sy
        o = bx(f"{name}{k}", (px + th / 2 * cy_, y + hh / 2, pz - th / 2 * sy), (th, hh, depth), rs.choice(mats), 0.003, yaw)
        if lean and k == n - 1 and rs.random() < 0.5: o.rotation_euler[1] += 0.25
        x += th + 0.003
    return x

def wallpaper_img(base="#c08a34", stripe="#7a2e1c", motif="#f0d8a0", w=128, h=256, seed=0):
    a = canvas(h, w, base); x, y = grid(a)
    put(a, (np.abs(x - 0.5) > 0.44) & (np.abs(x - 0.5) < 0.47), stripe); put(a, np.abs(x - 0.5) > 0.485, stripe, 0.6)
    for cy_ in (0.25, 0.75):
        cx = 0.5 if cy_ == 0.25 else 0.0
        for cxx in (cx, cx + 1.0):
            d = np.sqrt(((x - cxx) * w / h) ** 2 + (y - cy_) ** 2)
            put(a, (d < 0.06) & (np.abs(np.sin(np.arctan2(y - cy_, (x - cxx) * w / h) * 4)) * 0.03 + 0.03 > d), motif, 0.9)
            ellipse(a, cxx, cy_, 0.06, 0.03, motif, 0.0)
    put(a, np.sin(y * 80) > 0.9, stripe, 0.08)
    shade(a, 0.06, seed, 6)
    return a
def wall_mat(name, img_arr, tile=0.4, rough=0.75):
    """Repeating wallpaper on walls of either orientation: u = (X + Y) / tile, v = Z / (2 tile), object coords."""
    im = new_img(name + "_im", img_arr)
    m = bpy.data.materials.new(name); t, n, l = lib.nodes(m); b = n["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    tc = n.new("ShaderNodeTexCoord"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Object"], sp.inputs[0])
    ad = n.new("ShaderNodeMath"); ad.operation = "ADD"; l.new(sp.outputs[0], ad.inputs[0]); l.new(sp.outputs[1], ad.inputs[1])
    cu = n.new("ShaderNodeMath"); cu.operation = "DIVIDE"; l.new(ad.outputs[0], cu.inputs[0]); cu.inputs[1].default_value = tile
    cv = n.new("ShaderNodeMath"); cv.operation = "DIVIDE"; l.new(sp.outputs[2], cv.inputs[0]); cv.inputs[1].default_value = tile * 2
    cb = n.new("ShaderNodeCombineXYZ"); l.new(cu.outputs[0], cb.inputs[0]); l.new(cv.outputs[0], cb.inputs[1])
    tex = n.new("ShaderNodeTexImage"); tex.image = im; tex.extension = "REPEAT"; l.new(cb.outputs[0], tex.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.5; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    gr = n.new("ShaderNodeMix"); gr.data_type = "RGBA"; gr.blend_type = "MULTIPLY"; gr.inputs[0].default_value = 0.25
    l.new(tex.outputs["Color"], gr.inputs[6]); l.new(nz.outputs["Color"], gr.inputs[7]); l.new(gr.outputs[2], b.inputs["Base Color"])
    return m
def pretzel(name, c, s, m, yaw=0.0):
    """Pretzel: a fat torus loop plus two crossed arms, standing upright facing the camera at yaw 0."""
    o = torus(name, c, 0.07 * s, 0.022 * s, m, (math.radians(90), 0, yaw), 20, 8); o.scale = (1.2, 1, 1)
    for k, a in enumerate((0.6, -0.6)):
        cy(f"{name}a{k}", (c[0] + 0.0, c[1] - 0.02 * s, c[2] - 0.005), 0.016 * s, 0.13 * s, m, 8, (0, a, yaw))
    return o

def rooftops_img(seed=0, w=768, h=384, dusk=False):
    """Vienna-style rooftops: sky gradient, a cathedral spire, chimneys, lit windows."""
    rs = np.random.RandomState(seed); a = canvas(h, w, "#ffffff"); x, y = grid(a)
    top, bot = (rgb("#3a4a7a"), rgb("#f0b070")) if dusk else (rgb("#6a9ad0"), rgb("#e8e0d0"))
    t = np.clip(y / 0.7, 0, 1)[..., None]; a[:] = top * (1 - t) + bot * t
    cl = vnoise(h, w, 4, seed + 9, 4); put(a, soft(cl, 0.55, 0.7) * (y < 0.5), "#f6e8d8" if not dusk else "#f0a080", 0.5)
    poly(a, [(0.62, 0.62), (0.655, 0.18), (0.665, 0.08), (0.675, 0.18), (0.71, 0.62)], "#6a6a78")
    poly(a, [(0.6, 0.62), (0.6, 0.45), (0.72, 0.45), (0.72, 0.62)], "#6a6a78")
    for layer, (base, col, wcol) in enumerate(((0.55, "#8a7a78", "#f8d890"), (0.68, "#6a4e48", "#ffd070"), (0.82, "#4a3430", "#ffc860"))):
        xx = 0.0
        while xx < 1.0:
            bw = rs.uniform(0.06, 0.14); roof = base + rs.uniform(-0.05, 0.03)
            rect(a, xx, roof + 0.04, xx + bw, 1.0, col)
            poly(a, [(xx - 0.005, roof + 0.045), (xx + bw / 2, roof - rs.uniform(0.0, 0.06)), (xx + bw + 0.005, roof + 0.045)], "#9a4a3a" if layer < 2 else "#6a3a2a")
            if rs.rand() < 0.7: rect(a, xx + bw * 0.7, roof - 0.05, xx + bw * 0.7 + 0.012, roof + 0.03, col)
            for k in range(int(bw / 0.03)):
                for j in range(3):
                    if rs.rand() < 0.4: rect(a, xx + 0.008 + k * 0.03, roof + 0.07 + j * 0.06, xx + 0.02 + k * 0.03, roof + 0.1 + j * 0.06, wcol if rs.rand() < 0.5 else "#3a3a4a")
            xx += bw
    shade(a, 0.08, seed, 30)
    return a
