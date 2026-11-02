# The map room (chapter 2 shots 1, 2, 5, 17, 23, 24, 29, 30, 36; chapters 3/4 reuse it via c03_maproom / c04_maproom).
# Layout (three coords): room x -7..7, z -4.5..8.5, ceiling 4.4. Map table centre (0, 0, 1.98), top 5.9 x 2.9 at y 0.92,
# the painted map (maps/c02_map_<year>.jpg|png, lon -15..165, lat 72..-6) on x 2.6..-2.6 (west = +x, screen left when the
# camera looks +z), z 0.85..3.103 at y MY. ll(lon, lat) gives table coords: Berlin (1.78, 2.54), Vienna (1.69, 2.42),
# Prague (1.75, 2.47), Rome (1.81, 2.23), Tokyo (-1.87, 2.06), Manchuria (-1.47, 2.35), Nanjing (-1.30, 1.95).
# Leaders stand round it: north side z ~3.75, west end x ~3.5, east end x ~ -3.5. Keep the north side clear (z 3.4..4.3).
# Hitler's desk (back right): desk centre (-4.4, 0, 6.4), top 0.78; he stands at (-4.4, 0, 7.15); the little television on
# the desk's +x end, the notebook at (-4.55, 0.79, 6.2). Fireplace on the +x wall at z 3. Lights: two green billiard lamps
# over the table, the fire, the desk lamp, the television glow, cold moonlight through three back windows.
# Per shot the map changes (SCHED): base image cross-fades, and 3D tiles (Manchuria, Austria) lift and slide.
import bpy, math, os, random, json
from mathutils import Vector, Matrix
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, flat_text, sign, poster, R90, cached
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets import ikit as IK
from sets.void import toy_tank, pin_flag, unit_block, compass, dividers, magnifier, cup, inkwell, candle, fire, bookcase, lathe, tube, mat_once

LON0, LON1, LAT0, LAT1 = -15.0, 165.0, 72.0, -6.0
MX0, MX1, MZ0 = 2.6, -2.6, 0.85
MZ1 = MZ0 + 5.2 * (LAT0 - LAT1) / (LON1 - LON0)
MY = 0.953
def ll(lon, lat): return (MX0 + (MX1 - MX0) * (lon - LON0) / (LON1 - LON0), MZ0 + (MZ1 - MZ0) * (lat - LAT1) / (LAT0 - LAT1))
def uv(lon, lat): return ((lon - LON0) / (LON1 - LON0), (lat - LAT1) / (LAT0 - LAT1))

def mapfile(v):
    for ext in (".jpg", ".png"):
        p = os.path.join(CK.HERE, "maps", f"c02_map_{v}{ext}")
        if os.path.exists(p): return p
    return mapfile("1931") if v != "1931" else os.path.join(CK.HERE, "maps", "c02_map_1931.png")
_IM = {}
def img(v):
    if v not in _IM: _IM[v] = bpy.data.images.load(mapfile(v), check_existing=True)
    return _IM[v]

def mix_mat(name, a, b):
    """map material: two painted maps mixed by the 'k' value node (update() swaps the images and drives k)"""
    m = bpy.data.materials.new(name); t, n, l = lib.nodes(m); B = n["Principled BSDF"]; B.inputs["Roughness"].default_value = 0.45
    ta = n.new("ShaderNodeTexImage"); ta.name = "A"; ta.image = img(a); ta.interpolation = "Cubic"
    tb = n.new("ShaderNodeTexImage"); tb.name = "B"; tb.image = img(b); tb.interpolation = "Cubic"
    k = n.new("ShaderNodeValue"); k.name = "k"; k.outputs[0].default_value = 0.0
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(k.outputs[0], mx.inputs[0]); l.new(ta.outputs["Color"], mx.inputs[6]); l.new(tb.outputs["Color"], mx.inputs[7])
    hl = n.new("ShaderNodeValue"); hl.name = "glow"; hl.outputs[0].default_value = 0.0
    l.new(mx.outputs[2], B.inputs["Base Color"]); l.new(mx.outputs[2], B.inputs["Emission Color"]); l.new(hl.outputs[0], B.inputs["Emission Strength"])
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 300; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    lib.bump(n, l, nz.outputs["Fac"], 0.06, 0.01)
    return m

class Tile:
    """a raised piece of the map (country outline), textured with the map images, that can lift, slide and recolour"""
    def __init__(self, name, lonlat, a, b, thick=0.012):
        self.m = mix_mat(name + "m", a, b)
        pts = [ll(x, y) for x, y in lonlat]; cx = sum(p[0] for p in pts) / len(pts); cz = sum(p[1] for p in pts) / len(pts)
        self.c = (cx, cz)
        vs = [T(p[0] - cx, thick, p[1] - cz) for p in pts] + [T(p[0] - cx, 0.0, p[1] - cz) for p in pts]; n = len(pts)
        fs = [tuple(range(n))[::-1] if False else tuple(range(n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs); me.update()
        if me.polygons[0].normal.z < 0: me.flip_normals()
        uvl = me.uv_layers.new()
        for p in me.polygons:
            for li in p.loop_indices:
                vi = me.loops[li].vertex_index; lo, la = lonlat[vi % n]; uvl.data[li].uv = uv(lo, la)
        me.materials.append(self.m); self.o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(self.o)
        self.base = T(cx, MY - thick + 0.0015, cz); self.o.location = self.base; self.o.hide_render = True
    def pose(self, on, lift=0.0, dx=0.0, dz=0.0, k=0.0, glow=0.0, tilt=0.0):
        self.o.hide_render = not on
        self.o.location = self.base + T(dx, lift, dz) - T(0, 0, 0)
        self.o.rotation_euler = (tilt, 0, 0)
        self.m.node_tree.nodes["k"].outputs[0].default_value = k; self.m.node_tree.nodes["glow"].outputs[0].default_value = glow

def sm(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)

def screen_img():
    """the little television: grainy blue-grey picture of the League's council table + caption"""
    a = IK.canvas(120, 160, "#9aa8b0"); x, y = IK.grid(a)
    a[:] = IK.rgb("#8a98a2") * (0.75 + 0.35 * (1 - y))[..., None]
    IK.rect(a, 0.0, 0.62, 1.0, 1.0, "#5a6670"); IK.ellipse(a, 0.5, 0.66, 0.42, 0.1, "#3a444c")
    for k in range(7):
        cx = 0.14 + k * 0.12; IK.ellipse(a, cx, 0.46, 0.035, 0.05, "#2a3036"); IK.rect(a, cx - 0.04, 0.5, cx + 0.04, 0.64, "#2a3036")
    IK.rect(a, 0.0, 0.0, 1.0, 0.16, "#2a3036"); IK.stamp(a, "GENEVA", 0.5, 0.035, 0.09, "#e8eef2", align="center")
    rng = np.random.default_rng(3); a *= (0.85 + 0.3 * rng.random(a.shape[:2]))[..., None]
    for r in range(0, 120, 3): a[r] *= 0.82
    return a
import numpy as np

def build_room(M, D, sched):
    random.seed(1931); KS.reset(); rnd = random.Random(31)
    K = Kit("maproom")
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.01, 0.012, 0.02, 1); bg.inputs[1].default_value = 1.0
    FL = lib.parquet("mrfloor", "#5a3420", "#3a2012"); WALLP = IK.wall_mat("mrwall", IK.wallpaper_img("#2e4a3a", "#1e3428", "#6a8a5a", seed=4), 0.45)
    PAN = wood("#4a2814", "#22120a", 5, 0.35); DK = wood("#3a1e0e", "#1a0c06", 4, 0.4); TW = wood("#5a3018", "#2a140a", 3, 0.35)
    GILT = lib.gilt("mrgilt"); BR = brass(); PAPER = paper(); LEATH = pm("#5a1e14", 0.45); GREEN = pm("#1e4a2e", 0.35, 0.4)
    # ---------------- shell ----------------
    K.box((0, -0.05, 2), (14.4, 0.1, 13.4), FL, 0, 0)
    K.box((0, 0.006, 2.0), (8.4, 0.012, 5.4), lib.carpet("mrrug", "#6a1418", "#c8a24a"), 0, 0.003)
    K.box((0, 4.45, 2), (14.4, 0.1, 13.4), lib.plaster("mrceil", "#3a3430"), 0, 0)
    for k in range(6): K.box((0, 4.3, -3.5 + k * 2.4), (14.2, 0.25, 0.28), DK, 0, 0.02)
    K.box((0, 2.2, 8.65), (14.4, 4.4, 0.3), WALLP, 0, 0)
    K.box((0, 2.2, -4.65), (14.4, 4.4, 0.3), WALLP, 0, 0)
    for sx in (-1, 1): K.box((sx * 7.15, 2.2, 2), (0.3, 4.4, 13.4), WALLP, 0, 0)
    for sx in (-1, 1):
        K.box((sx * 6.96, 0.6, 2), (0.08, 1.2, 13.2), PAN, 0, 0.01); K.box((sx * 6.92, 1.22, 2), (0.12, 0.06, 13.2), DK, 0, 0.01)
        K.box((sx * 6.95, 4.12, 2), (0.14, 0.14, 13.2), GILT, 0, 0.01)
    K.box((0, 0.6, 8.46), (14, 1.2, 0.08), PAN, 0, 0.01); K.box((0, 1.22, 8.42), (14, 0.06, 0.12), DK, 0, 0.01); K.box((0, 4.12, 8.45), (14, 0.14, 0.14), GILT, 0, 0.01)
    for k in range(12):
        x = -6.5 + k * 1.18
        if abs(x) > 0.3: K.box((x, 0.6, 8.41), (0.9, 0.85, 0.03), DK, 0, 0.02)
    # back wall: three tall windows (cold night outside), velvet drapes with gilt pelmets
    for x in (-1.9, 0.0, 1.9):
        K.box((x, 2.6, 8.62), (1.25, 2.6, 0.04), em("#2a3c66", 1.4), 0, 0)
        for j in range(4): K.box((x, 1.3 + j * 0.866, 8.56), (1.3, 0.05, 0.06), DK, 0, 0.005)
        for j in range(3): K.box((x - 0.625 + j * 0.625, 2.6, 8.56), (0.05, 2.6, 0.06), DK, 0, 0.005)
        K.box((x, 1.22, 8.42), (1.6, 0.08, 0.3), DK, 0, 0.01)
        K.box((x, 4.0, 8.35), (2.2, 0.35, 0.12), GILT, 0, 0.02)
        for sd in (-1, 1): IK.drape(f"dr{x}{sd}", (x + sd * 0.95, 3.85, 8.32), 0.7, 3.8, IK.velvet("mrdrape", "#5a0e16", 0.8), 0, 4, 0.06, gather=sd * 0.8)
        CK.lib.light("AREA", T(x, 2.6, 8.9), 120, (0.55, 0.68, 1.0), 1.2).rotation_euler = (math.radians(-90), 0, 0)
    from sets.void import sconce
    for x in (-3.4, -0.95, 0.95, 3.4, 5.5, -5.5): sconce(f"sc{x}", (x, 2.5, 8.45), 30)
    # +x wall: fireplace with a real fire, overmantel painting, clock
    MARB = lib.marble("mrmarble")
    for sd in (-1, 1): K.box((6.75, 0.5, 3.0 + sd * 0.95), (0.5, 1.0, 0.5), MARB, 0, 0.02)
    K.box((6.75, 1.15, 3.0), (0.5, 0.3, 2.4), MARB, 0, 0.02); K.box((7.0, 0.5, 3.0), (0.1, 1.0, 1.5), pm("#0e0a08", 0.9), 0, 0.0)
    K.box((6.6, 0.03, 3.0), (0.8, 0.06, 2.6), MARB, 0, 0.01)
    K.box((6.55, 1.33, 3.0), (0.85, 0.1, 2.7), MARB, 0, 0.02)
    for k in range(5): K.cyl((6.75, 0.1 + (k % 2) * 0.08, 2.75 + k * 0.12), 0.06, 0.6, wood("#4a3020", "#2a1a10", 8), 8, "z", yaw=0.3)
    fire("hearth", (6.75, 0.12, 3.0), 0.42, 4, True, 260)
    for k in range(3): K.cyl((6.4, 0.12, 2.5 + k * 0.08), 0.012, 0.9, BR, 6, "y", pitch=0.2)
    IK.framed("ovm", (6.98, 2.6, 3.0), 1.9, 1.3, IK.img_mat("ovmi", IK.landscape_img(77, 384, 260, house=True, water=True), 0.55, coat=0.3), GILT, math.pi / 2, 0.12, 0.08)
    for z in (1.35, 4.65):
        K.cyl((6.6, 1.55, z), 0.06, 0.4, BR, 10)
        CK.candle(f"mc{z}", (6.6, 1.38, z), 0.2, int(z * 3), 0.8)
    # -x wall: bookcases, a framed Europe map, a globe on a stand
    for k, z in enumerate((-2.5, 0.5, 3.5)):
        bookcase(f"bc{k}", (-6.8, 0, z), 2.6, 3.0, 0.45, 6, PAN, math.pi / 2 + math.pi, seed=40 + k)
    lathe("globe", [(0.0, -0.42), (0.18, -0.4), (0.3, -0.3), (0.38, -0.12), (0.4, 0.0), (0.38, 0.12), (0.3, 0.3), (0.18, 0.4), (0.0, 0.42)], (5.3, 1.45, 6.9),
          CK.img_file_mat("globem", "map_world.png", 0.4), 32)
    K.torus((5.3, 1.45, 6.9), 0.46, 0.015, BR, 32, 6, "z", yaw=0.4)
    K.cyl((5.3, 0.55, 6.9), 0.05, 1.0, TW, 10); K.cyl((5.3, 0.04, 6.9), 0.35, 0.08, TW, 16)
    for a in (0, 2.1, 4.2): K.cyl((5.3 + 0.2 * math.cos(a), 0.2, 6.9 + 0.2 * math.sin(a)), 0.03, 0.45, TW, 6, "y", pitch=0.4 * math.sin(a), roll=-0.4 * math.cos(a))
    # ---------------- the map table ----------------
    K.box((0, 0.89, 1.98), (5.9, 0.07, 2.9), TW, 0, 0.02)
    K.box((0, 0.75, 1.98), (5.6, 0.22, 2.6), TW, 0, 0.02)
    for sx in (-1, 1):
        for sz in (-1, 1):
            lathe(f"tleg{sx}{sz}", [(0.0, 0.0), (0.12, 0.0), (0.08, 0.1), (0.06, 0.3), (0.11, 0.45), (0.07, 0.55), (0.09, 0.66), (0.0, 0.66)], (sx * 2.6, 0, 1.98 + sz * 1.15), TW, 20)
    K.box((0, MY - 0.002, (MZ0 + MZ1) / 2), (5.3, 0.004, MZ1 - MZ0 + 0.08), DK, 0, 0)
    base = mix_mat("mapbase", "1931", "1931")
    CK.quad_uv("map", [(MX0, MY, MZ0), (MX1, MY, MZ0), (MX1, MY, MZ1), (MX0, MY, MZ1)], base)
    for sx in (-1, 1):
        for sz in (MZ0 - 0.03, MZ1 + 0.03): K.box((sx * 2.63, MY + 0.004, sz), (0.12, 0.012, 0.12), BR, 0, 0.003)
    # clutter round the map edges (kept off the countries): rulers, dividers, a compass, ink, papers, cups, an ashtray
    for k in range(5): K.box((2.85, MY + 0.002 + k * 0.002, 1.2 + k * 0.03), (0.24, 0.002, 0.32), PAPER, 0.15 * k, 0)
    flat_text("SECRET", (2.85, MY + 0.014, 1.2), 0.04, pm("#a81e22", 0.5), 0.6)
    compass("comp", (-2.75, MY, 1.0), 0.06); dividers("div", (2.75, MY, 2.9), 2.6, 0.2); magnifier("mag", (-2.8, MY, 2.9), 0.8)
    inkwell("ink", (2.82, MY, 0.7)); cup("cup1", (-2.78, MY, 0.62)); cup("cup2", (2.8, MY, 3.2))
    K.box((0.4, MY + 0.003, 0.68), (1.0, 0.006, 0.05), wood("#c8a46a", "#8a6a3a", 20), 0.02, 0.002)
    for k in range(10): K.box((-0.07 + k * 0.1, MY + 0.007, 0.68), (0.004, 0.001, 0.02), pm("#2a1a10", 0.6), 0, 0)
    # leaders' pieces: toy tanks, blocks, pins (Germany / Italy / Japan), ships at sea
    Y = MY
    for k, (lo, la, yw, col) in enumerate(((9.5, 50.8, 0.2, "#5a5e58"), (12.2, 52.2, -0.3, "#5a5e58"), (11.5, 44.8, 1.6, "#5a7a3a"), (14.5, 41.5, 1.4, "#5a7a3a"),
                                          (135.5, 34.6, 2.9, "#9a8a4a"), (140.2, 39.2, 3.0, "#9a8a4a"))):
        x, z = ll(lo, la); toy_tank(f"tt{k}", (x, Y, z), yw, col, 0.9)
    for k, (lo, la, col) in enumerate(((8.0, 53.2, "#3a3a3a"), (13.0, 48.8, "#3a3a3a"), (9.2, 40.2, "#2a7a3a"), (16.4, 38.6, "#2a7a3a"), (132.0, 33.0, "#e8c040"),
                                       (137.6, 37.0, "#e8c040"), (-3.0, 53.0, "#2a4a9a"), (1.0, 46.0, "#3a5ac8"), (37.6, 55.8, "#b02a2a"), (104.0, 30.6, "#d89a3a"))):
        x, z = ll(lo, la); pin_flag(f"pf{k}", (x, Y, z), col, 0.1)
    from sets.void import toy_ship
    for k, (lo, la, yw) in enumerate(((150.0, 30.0, 2.6), (156.0, 22.0, 2.4), (-9.0, 47.0, 0.4), (30.0, 33.6, 3.0))):
        x, z = ll(lo, la); toy_ship(f"ts{k}", (x, Y, z), yw, 0.2, "#6a7280")
    # Japan's three nearly empty supply crates (shot 2), in the Pacific off Japan, labels toward the camera (-z)
    CR = wood("#b8945a", "#7a5a30", 14, 0.7); INKM = pm("#2a1a10", 0.6)
    for k, (lab, lo, la) in enumerate((("OIL", 145.0, 33.0), ("IRON", 149.5, 33.0), ("RUBBER", 154.0, 33.0))):
        x, z = ll(lo, la); s = 0.13
        K.box((x, Y + 0.005, z), (s, 0.01, s), CR, 0, 0.002)
        for sd in (-1, 1):
            K.box((x + sd * s / 2, Y + s * 0.4, z), (0.01, s * 0.8, s), CR, 0, 0.002); K.box((x, Y + s * 0.4, z + sd * s / 2), (s, s * 0.8, 0.01), CR, 0, 0.002)
        text(lab, (x, Y + s * 0.45, z - s / 2 - 0.006), 0.034 if len(lab) > 4 else 0.045, INKM, 0, "sans", 0.001)
        if k == 0: K.cyl((x + 0.03, Y + 0.03, z + 0.02), 0.018, 0.05, pm("#2a2a2a", 0.4, 0.5), 10)
        if k == 1: K.box((x - 0.02, Y + 0.02, z), (0.05, 0.02, 0.025), pm("#6a6a70", 0.4, 0.8), 0.3, 0.003)
        if k == 2: K.sphere((x, Y + 0.025, z + 0.01), 0.018, pm("#3a2a1a", 0.7), 8)
    # Japanese toy soldiers bogged down all over China (shot 17)
    SOLD = pm("#a8955a", 0.6); HEAD = pm("#e8c8a0", 0.6); BASE = pm("#3a4a2a", 0.6)
    for k in range(46):
        lo = rnd.uniform(106, 121); la = rnd.uniform(24, 41)
        if lo > 119.5 and la < 30: continue
        x, z = ll(lo, la)
        K.cyl((x, Y + 0.002, z), 0.012, 0.004, BASE, 8); K.cyl((x, Y + 0.022, z), 0.007, 0.036, SOLD, 6); K.sphere((x, Y + 0.046, z), 0.0075, HEAD, 6)
        K.cyl((x, Y + 0.053, z), 0.008, 0.004, SOLD, 6)
    # chairs round the table (pushed back so the leaders stand clear)
    for k, (x, z, yw) in enumerate(((-1.0, -0.3, 0), (1.0, -0.3, 0), (-3.6, 0.9, R90), (3.6, 0.9, -R90))):
        IK.chair(f"ch{k}", x, z, yw, TW, LEATH, 0.48, True, GILT)
    # billiard lamps over the table
    for x in (-1.4, 1.4):
        K.cyl((x, 3.5, 1.98), 0.01, 1.8, pm("#1a1a1a", 0.5), 6)
        K.box((x, 2.55, 1.98), (1.6, 0.16, 0.5), GREEN, 0, 0.04); K.box((x, 2.47, 1.98), (1.5, 0.02, 0.42), em("#fff0c8", 6.0), 0, 0)
        lib.light("AREA", T(x, 2.42, 1.98), 420, (1.0, 0.8, 0.55), 1.4, size_y=0.4).rotation_euler = (0, 0, 0)
    # ---------------- Hitler's desk (back right): lamp, the little television, notebook, telephone, files ----------------
    dx, dz = -4.4, 6.4
    K.box((dx, 0.76, dz), (1.9, 0.06, 0.95), DK, 0, 0.02)
    for sd in (-1, 1): K.box((dx + sd * 0.72, 0.37, dz), (0.42, 0.74, 0.85), DK, 0, 0.02)
    for sd in (-1, 1):
        for j in range(3): K.box((dx + sd * 0.72, 0.15 + j * 0.24, dz - 0.43), (0.36, 0.2, 0.02), PAN, 0, 0.01); K.cyl((dx + sd * 0.72, 0.25 + j * 0.24, dz - 0.45), 0.015, 0.03, BR, 8, "z")
    K.box((dx, 0.795, dz + 0.05), (0.7, 0.01, 0.5), pm("#2a3a2a", 0.6), 0, 0.002)
    # television: tall walnut cabinet, small bright screen, knobs, speaker cloth
    tvx, tvz, tvy = dx + 0.6, dz - 0.18, 0.79; ty = R90 * 0.5
    tw = CK.X(tvx, tvy, tvz, -1.25)
    tw.box(K, (0, 0.3, 0), (0.42, 0.6, 0.5), wood("#6a3a1a", "#3a1a08", 10, 0.3), 0.02)
    tw.box(K, (0.212, 0.42, 0), (0.01, 0.17, 0.22), pm("#141414", 0.3), 0.01)
    scr = IK.img_mat("tvscreen", screen_img(), 0.3, emit=2.2)
    sp = [tw.p(0.219, 0.35, 0.1), tw.p(0.219, 0.35, -0.1), tw.p(0.219, 0.49, -0.1), tw.p(0.219, 0.49, 0.1)]
    CK.quad_uv("tvscr", sp, scr)
    tw.box(K, (0.212, 0.17, 0), (0.01, 0.16, 0.36), cloth("#8a7a5a"), 0.0)
    for k in range(3): tw.cyl(K, (0.225, 0.06, -0.12 + k * 0.12), 0.022, 0.03, gold(), 12, "x")
    lib.light("POINT", T(*tw.p(0.4, 0.42, 0)), 6, (0.7, 0.8, 1.0), 0.1)
    # banker's lamp, telephone, notebook, files, pen
    K.cyl((dx - 0.55, 0.82, dz + 0.15), 0.08, 0.03, BR, 14); K.cyl((dx - 0.55, 0.98, dz + 0.15), 0.012, 0.3, BR, 8)
    K.box((dx - 0.55, 1.14, dz + 0.08), (0.36, 0.08, 0.16), GREEN, 0, 0.03)
    lib.light("POINT", T(dx - 0.55, 1.06, dz + 0.05), 25, (1.0, 0.75, 0.45), 0.05)
    K.box((dx - 0.25, 0.83, dz + 0.3), (0.2, 0.06, 0.14), pm("#141414", 0.3), 0.3, 0.02); K.cyl((dx - 0.25, 0.9, dz + 0.3), 0.025, 0.2, pm("#141414", 0.3), 10, "x", yaw=0.3)
    nb = (dx - 0.15, 0.795, dz - 0.18)
    K.box((nb[0], nb[1], nb[2]), (0.42, 0.01, 0.3), pm("#3a2a1e", 0.6), 0.1, 0.002)
    K.box((nb[0], nb[1] + 0.008, nb[2]), (0.4, 0.006, 0.28), paper("#f2ead6", 0.2), 0.1, 0)
    NOTE = pm("#1e2a4a", 0.5); notes = []
    for j, s in enumerate(("1931 JAPAN: report", "1935 ITALY: report", "")):
        if s: notes.append(flat_text(s, (nb[0] + 0.0, nb[1] + 0.013, nb[2] + 0.08 - j * 0.045), 0.024, NOTE, 0.1, "mono"))
    lesson = flat_text("NOBODY WILL\nSTOP ME!", (nb[0] - 0.01, nb[1] + 0.013, nb[2] - 0.07), 0.034, pm("#8a1a1a", 0.5), 0.1, "sans")
    uline = K  # underline drawn as a box below (always there)
    K.box((nb[0] - 0.01, nb[1] + 0.012, nb[2] - 0.115), (0.17, 0.002, 0.004), pm("#8a1a1a", 0.5), 0.1, 0)
    K.cyl((nb[0] + 0.24, nb[1] + 0.01, nb[2] - 0.05), 0.006, 0.15, pm("#1a1a1a", 0.3, 0.4), 8, "x", yaw=0.5)
    for k in range(4): K.box((dx - 0.75, 0.80 + k * 0.025, dz - 0.15), (0.3, 0.024, 0.4), pm(["#c8b080", "#a8c0d0", "#d8c8a0", "#c89a8a"][k], 0.8), 0.05 * k, 0.003)
    IK.chair("dchair", dx, dz + 0.95, math.pi, DK, LEATH, 0.5, True, GILT)
    # filing cabinets, coat stand, standing lamp near the desk
    for k in range(2):
        K.box((-6.5, 0.7, 5.8 + k * 0.6), (0.6, 1.4, 0.55), pm("#4a4e44", 0.45, 0.4), 0, 0.02)
        for j in range(3): K.cyl((-6.18, 0.35 + j * 0.42, 5.8 + k * 0.6), 0.015, 0.12, BR, 8, "z")
    K.cyl((-2.8, 0.85, 7.9), 0.03, 1.7, DK, 8); K.cyl((-2.8, 0.03, 7.9), 0.25, 0.05, DK, 12)
    K.box((-2.8, 1.35, 7.95), (0.4, 0.7, 0.2), cloth("#3a3a40"), 0, 0.06)
    K.cyl((3.6, 0.8, 7.6), 0.025, 1.6, BR, 8); K.cyl((3.6, 1.7, 7.6), 0.28, 0.32, pm("#e8c890", 0.7, 0.0), 16, "y", 0.18)
    lib.light("POINT", T(3.6, 1.6, 7.6), 40, (1.0, 0.7, 0.4), 0.1)
    # wall clock and portraits of nobody in particular
    K.cyl((-6.95, 3.1, 6.8), 0.3, 0.06, pm("#f2ece0", 0.4), 24, "x"); K.torus((-6.92, 3.1, 6.8), 0.31, 0.03, BR, 24, 6, "x")
    IK.framed("pt1", (6.98, 2.5, 6.3), 0.9, 1.15, IK.img_mat("pt1i", IK.portrait_img(91), 0.55, coat=0.3), GILT, math.pi / 2, 0.08, 0.06)
    IK.framed("pt2", (6.98, 2.5, -0.2), 0.9, 1.15, IK.img_mat("pt2i", IK.portrait_img(93), 0.55, coat=0.3), GILT, math.pi / 2, 0.08, 0.06)
    # fills: warm bounce from the camera side, cool rim from the windows
    lib.light("AREA", T(0, 3.5, -3.8), 520, (1.0, 0.82, 0.62), 4.0, size_y=1.5).rotation_euler = (math.radians(-60), 0, math.pi)
    K.build()
    # dynamic: tiles
    shp = json.load(open(os.path.join(CK.HERE, "maps", "c02_shapes.json")))["shapes"]
    tiles = {"MAN": Tile("tileMAN", shp["MAN"], "1931", "1932"), "AUT": Tile("tileAUT", shp["AUT"], "1937", "1938a")}
    TB = base.node_tree.nodes
    def update(f):
        st = sched(D["id"], f)
        a, b, k = st.get("base", ("1931", "1931", 0.0))
        TB["A"].image = img(a); TB["B"].image = img(b); TB["k"].outputs[0].default_value = k; TB["glow"].outputs[0].default_value = st.get("glow", 0.0)
        for nm, t in tiles.items():
            if nm in st.get("tiles", {}): t.pose(True, *st["tiles"][nm])
            else: t.pose(False)
        lesson.hide_render = not st.get("lesson", False)
    return {"update": update}

# chapter 2 schedule: shot id -> map state at frame f (chapter-local frames)
def sched2(sid, f):
    if sid in (1, 2): return {"base": ("1931", "1931", 0.0)}
    if sid == 5:
        t0 = 612; u = sm((f - t0) / 10); c = sm((f - t0 - 12) / 14); d = sm((f - t0 - 30) / 10)
        return {"base": ("1931", "1932", d), "tiles": {"MAN": (d < 1, 0.06 * u * (1 - d), 0, 0, c, 0.0)}}
    if sid == 17: return {"base": ("1937", "1937", 0.0)}
    if sid in (23, 24): return {"base": ("1932", "1932", 0.0), "lesson": sid == 24 and f >= 2622}
    if sid == 29:
        t0 = 3146; u = sm((f - t0) / 12); s = sm((f - t0 - 10) / 18); c = sm((f - t0 - 22) / 12); d = sm((f - t0 - 40) / 10)
        return {"base": ("1937", "1938a", d), "tiles": {"AUT": (d < 1, 0.05 * u * (1 - d), -0.03 * s * (1 - d), 0.03 * s * (1 - d), c, 0.0)}}
    if sid == 30:
        p = 0.5 + 0.5 * math.sin((f - 3315) * 0.35) if f >= 3315 else 0.0
        return {"base": ("1938a", "1938s", 0.85 * p), "glow": 0.0}
    if sid == 36: return {"base": ("1938s", "1939m", sm((f - 3884) / 18))}
    return {"base": ("1932", "1932", 0.0)}

def build(M, D): return build_room(M, D, sched2)
