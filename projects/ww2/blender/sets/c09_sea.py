# The North Atlantic, 1942-43 (chapter 9: U-boats, the convoys, the escorts, Black May). Grey swell under a low storm sky
# with a cold-gold streak on the horizon; a burning tanker gives warm light. Sea surface y -0.25 (ships' waterline y 0).
# Layout (three, y up):
#   periscope: (3, -0.25, 8) sticking up 2.4 m, with its feather of foam; the camera sits low (y 0.4..1.2) round (0, 0, 0).
#   convoy: merchant ships across z 160..420 (|x| < 260), heading +x; the torpedoed tanker TANKER at (30, 0, 190), burning.
#   escort destroyer at (-40, 0, 70) heading +x (bow +x), depth-charge splashes are fx cards round (-20..10, 0, 80..100).
#   surfaced U-boat U1 at (20, 0, 40) heading -x (bow -x), the attack-from-the-air target; the sinking U-boat U2 at
#   (-20, 0, 36), bow up, going down in update() over the shot (shots whose manifest set id has sink=True: D["id"] in SINK).
import bpy, math, random
from mathutils import Vector, Matrix
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, smoke_mat, smoke_column, text
from sets.front import warship, sea_mat, foam_mat, flag as wave_flag
from sets import c09_kit as K

bx, cy = K.bx, K.cy
SINK = (33,)          # chapter-9 shot ids in which U2 sinks (see ch09.ts)
TANKER = (30, 190)
def uboat(n, x, z, yaw, y0=0.0, pitch=0.0, objs=None):
    """Type VII U-boat ~ 66 m: pressure hull, saddle tanks, casing deck, conning tower with the 'wintergarden', deck gun,
    flak, periscopes, net cutter and jumping wires; bow +x. Returns the list of objects (for the sinking parent)."""
    grey = mat_once("ubgrey", lambda: worn("ubgrey", "#646c74", "#3a2a22", 0.55, 0.3, 0.8, 0.66, "#4a4a4c"))
    dk = mat_once("ubdk", lambda: worn("ubdk", "#3a3e44", "#2a2420", 0.6, 0.3, 3, 0.7, "#2a2a2c"))
    deck = wood_mat("ubdeck", "#5a5a52", "#3a3a34", 14, 0.8)
    steel = mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    made = []
    P = K.P_of(x, z, yaw, y0, 0.0)
    R = Matrix.Rotation(pitch, 3, "Z")
    def Q(lx, ly, lz):
        v = R @ Vector((lx, ly, lz)); return P(v.x, v.y, v.z)
    L = 66.0
    prof = [(0.0, -L / 2)] + [(2.6 * math.sin(math.pi * (0.04 + 0.92 * k / 20)) ** 0.55, -L / 2 + L * k / 20) for k in range(1, 20)] + [(0.0, L / 2)]
    tilt = Matrix.Rotation(math.radians(-90), 3, "Z")
    made.append(lathe(f"{n}hull", prof, (0, 0, 0), grey, 28, tilt=tilt))
    for sd in (-1, 1): made.append(lathe(f"{n}sad{sd}", [(0.0, -14), (1.3, -10), (1.5, 0), (1.3, 10), (0.0, 14)], (0, -0.4, sd * 2.4), grey, 18, tilt=tilt))
    made.append(K.prism(f"{n}casing", [(-30, 1.2), (31, 1.2), (33, 2.0), (31, 2.3), (-29, 2.3)], -1.6, 1.6, lambda a, b, c: (a, b, c), deck))
    tw = [(4.5, 0.0), (3.8, 1.2), (0.5, 1.5), (-2.5, 1.6), (-5.5, 1.3), (-6.0, 0.0), (-5.5, -1.3), (-2.5, -1.6), (0.5, -1.5), (3.8, -1.2)]
    made.append(K.loft2(f"{n}tower", tw, 2.2, [(a * 0.92, b * 0.9) for a, b in tw], 5.0, lambda a, b, c: (a, b, c), grey))
    made.append(K.loft2(f"{n}wint", [(-2.5, -1.7), (-2.5, 1.7), (-6.5, 1.5), (-7.2, 0.0), (-6.5, -1.5)], 3.6, [(-2.5, -1.7), (-2.5, 1.7), (-6.5, 1.5), (-7.2, 0.0), (-6.5, -1.5)], 3.75, lambda a, b, c: (a, b, c), dk))
    for k in range(14):
        a = k / 13 * math.pi; made.append(tube(f"{n}rail{k}", [(-5.2 - 1.6 * math.sin(a), 3.75, 1.5 * math.cos(a)), (-5.2 - 1.6 * math.sin(a), 4.6, 1.5 * math.cos(a))], 0.03, steel, res=2, bres=0))
    made.append(tube(f"{n}railt", [(-2.6, 4.6, 1.6)] + [(-5.2 - 1.6 * math.sin(k / 8 * math.pi), 4.6, 1.5 * math.cos(k / 8 * math.pi)) for k in range(9)] + [(-2.6, 4.6, -1.6)], 0.035, steel, res=12, bres=1))
    made.append(lathe(f"{n}flak", [(0.0, 0.0), (0.3, 0.0), (0.3, 0.6), (0.0, 0.7)], (-5.5, 3.75, 0), steel, 12))
    made.append(tube(f"{n}flakb", [(-5.5, 4.3, 0), (-3.6, 4.6, 0)], 0.06, steel, res=2, bres=1))
    for k, (lx, h) in enumerate(((0.8, 3.0), (-0.4, 2.2))):
        made.append(tube(f"{n}scope{k}", [(lx, 4.8, 0), (lx, 5.0 + h, 0)], 0.09 - k * 0.02, steel, res=2, bres=1))
    made.append(K.loft2(f"{n}bridge", [(4.3, 0.0), (3.6, 1.15), (0.0, 1.4), (0.0, -1.4), (3.6, -1.15)], 5.0, [(4.6, 0.0), (3.8, 1.25), (0.0, 1.5), (0.0, -1.5), (3.8, -1.25)], 5.9, lambda a, b, c: (a, b, c), grey, cap=False))
    made.append(lathe(f"{n}gunb", [(0.0, 0.0), (0.45, 0.0), (0.4, 0.7), (0.0, 0.75)], (12, 2.3, 0), steel, 14))
    made.append(bx(f"{n}gunbox", (12.0, 3.2, 0), (1.2, 0.7, 0.9), steel, 0.05))
    made.append(tube(f"{n}gun", [(12.5, 3.25, 0), (17.0, 3.3, 0)], 0.09, steel, res=2, bres=1))
    for sd in (-1, 1): made.append(bx(f"{n}shld{sd}", (12.6, 3.3, sd * 0.5), (0.9, 0.9, 0.04), steel, 0.01))
    made.append(K.prism(f"{n}cutter", [(31, 2.3), (34.5, 1.0), (34.8, 1.2), (31.6, 3.6)], -0.06, 0.06, lambda a, b, c: (a, b, c), steel))
    made.append(tube(f"{n}jw1", [(31.6, 3.6, 0), (4.0, 5.8, 0)], 0.02, steel, res=2, bres=0))
    made.append(tube(f"{n}jw2", [(-6.8, 4.6, 0), (-31, 2.6, 0)], 0.02, steel, res=2, bres=0))
    for sd in (-1, 1): made.append(bx(f"{n}plane{sd}", (-31.5, 0.0, sd * 2.2), (1.4, 0.08, 1.8), dk, 0.02))
    made.append(text("U 1", (3.3, 4.1, -1.52), 0.6, pmat("c9white", "#e8e2d0", 0.7), flat=False))
    # place: build at the origin in boat-local three coords, then move the whole group
    root = bpy.data.objects.new(f"{n}root", None); link(root)
    for o in made:
        if o is None: continue
        o.parent = root
    root.location = T(x, y0, z); root.rotation_euler = (0, -pitch, yaw)
    if objs is not None: objs.append(root)
    return root
def merchant(n, x, z, yaw, L=120.0, B=17.0, kind="cargo", hull="#3a3a3a", rnd=None):
    """convoy merchant: Liberty-style cargo ship (midship house, three masts with derricks, hatches with deck cargo) or a
    tanker (bridge amidships, engine house aft, catwalk and pipes); bow +x, waterline y 0"""
    rnd = rnd or random.Random(7)
    hm = mat_once("mh" + hull, lambda: worn("mh" + hull, hull, "#6a3a1e", 0.6, 0.3, 0.6, 0.62, "#2a2220"))
    gry = mat_once("mgrey", lambda: worn("mgrey", "#7a8088", "#4a4a4a", 0.55, 0.3, 1.0, 0.66, "#5a5a5a"))
    rust = mat_once("mrust", lambda: worn("mrust", "#6a3a22", "#3a2014", 0.8, 0.3, 2, 0.6, "#4a2a18"))
    win = mat_once("shipwin", lambda: lib.principled("shipwin", lib.hexc("#0c0e12"), 0.1, 0.0))
    P = K.P_of(x, z, yaw, 0.0)
    out = [(L / 2 + 2, 0.0), (L / 2 - 8, B / 2 * 0.8), (L / 2 - 25, B / 2), (-L / 2 + 12, B / 2), (-L / 2, B / 2 * 0.6), (-L / 2 - 1, 0.0),
           (-L / 2, -B / 2 * 0.6), (-L / 2 + 12, -B / 2), (L / 2 - 25, -B / 2), (L / 2 - 8, -B / 2 * 0.8)]
    K.loft2(f"{n}hull", [(a * 0.97, b * 0.8) for a, b in out], -1.0, [(a + (1.5 if a > L / 2 - 1 else 0), b) for a, b in out], 7.0, P, hm)
    bx(f"{n}boot", P(0, 0.3, 0), (L * 0.9, 0.6, B * 0.98), mat_once("mboot", lambda: lib.principled("mboot", lib.hexc("#6a2a22"), 0.7)), 0.05, yaw)
    def house(lx, w, d, h, lvl=2):
        for k in range(lvl):
            ww, dd = w * (1 - 0.15 * k), d * (1 - 0.1 * k)
            bx(f"{n}h{lx}{k}", P(lx, 7.0 + h * k + h / 2, 0), (ww, h, dd), gry, 0.05, yaw)
            for j in range(int(ww / 1.6)):
                for sd in (-1, 1): bx(f"{n}w{lx}{k}{j}{sd}", P(lx - ww / 2 + 0.8 + j * 1.6, 7.0 + h * k + h * 0.55, sd * dd / 2), (0.7, 0.6, 0.06), win, 0.0, yaw)
        bx(f"{n}br{lx}", P(lx, 7.0 + h * lvl + 0.4, 0), (w * 0.5, 0.8, d * 1.05), gry, 0.03, yaw)
    if kind == "tanker":
        house(-L / 2 + 10, 14, B * 0.85, 2.6, 2); house(4, 9, B * 0.8, 2.4, 3)
        lathe(f"{n}fun", [(0.0, 0.0), (1.6, 0.0), (1.6, 5.5), (0.0, 5.5)], P(-L / 2 + 8, 12, 0), mat_once("mfun", lambda: lib.principled("mfun", lib.hexc("#2a2a2a"), 0.6)), 16)
        tube(f"{n}cat", [P(-L / 2 + 18, 8.6, 0), P(L / 2 - 6, 8.6, 0)], 0.25, gry, res=2, bres=1)
        for k in range(4): tube(f"{n}pipe{k}", [P(-L / 2 + 16, 7.2, -2 + k), P(L / 2 - 10, 7.2, -2 + k)], 0.18, rust, res=2, bres=1)
        for k in range(6): cy(f"{n}valve{k}", P(-30 + k * 12, 7.6, 0), 0.6, 0.8, rust, 12)
    else:
        house(-8, 12, B * 0.8, 2.5, 3)
        lathe(f"{n}fun", [(0.0, 0.0), (1.4, 0.0), (1.4, 5.0), (0.0, 5.0)], P(-14, 13, 0), mat_once("mfun", lambda: lib.principled("mfun", lib.hexc("#2a2a2a"), 0.6)), 16)
        for k, lx in enumerate((L / 2 - 22, 18, -L / 2 + 22)):
            tube(f"{n}mast{k}", [P(lx, 7, 0), P(lx, 24, 0)], 0.35, gry, res=2, bres=1)
            for sd in (-1, 1): tube(f"{n}der{k}{sd}", [P(lx, 9, sd * 0.4), P(lx + (8 if lx > -20 else -8), 13, sd * 2.5)], 0.15, gry, res=2, bres=1)
            tube(f"{n}stay{k}", [P(lx, 24, 0), P(lx + 12, 7.2, 0)], 0.04, gry, res=2, bres=0)
        for k, lx in enumerate((L / 2 - 32, L / 2 - 12, 28, -30, -L / 2 + 14)):
            bx(f"{n}hatch{k}", P(lx, 7.6, 0), (8, 1.2, 8), rust, 0.05, yaw)
            if rnd.random() < 0.6: bx(f"{n}cargo{k}", P(lx, 9.0, 0), (6.5, 1.6, 6.0), mat_once("mcargo", lambda: lib.cloth("mcargo", "#5a5a40")), 0.2, yaw)
    return P

def build(M, D):
    rnd = random.Random(1943)
    K.sky("#3a4658", "#c8a080", 0.9, "#2a3448", "#e0a878")
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(0, -0.25, 400)); sea = bpy.context.object; sea.scale = (2400, 2400, 1); bpy.ops.object.transform_apply(scale=True)
    sea.data.materials.append(sea_mat())
    foam = mat_once("ffoam", foam_mat)
    # convoy columns
    for k in range(12):
        col, row = k % 4, k // 4
        x_ = -220 + col * 140 + rnd.uniform(-20, 20); z_ = 200 + row * 90 + rnd.uniform(-15, 15)
        if math.hypot(x_ - TANKER[0], z_ - TANKER[1]) < 50: continue
        merchant(f"m{k}", x_, z_, rnd.uniform(-0.05, 0.05), rnd.uniform(110, 140), 17, "tanker" if k % 3 == 1 else "cargo", ["#3a3a3a", "#4a4440", "#2e3238"][k % 3], rnd)
    merchant("tank1", TANKER[0], TANKER[1], 0.15, 140, 19, "tanker", "#3a3a3a", rnd)
    for k in range(6): fire(f"tf{k}", (TANKER[0] - 40 + k * 14, 7.5, TANKER[1] + rnd.uniform(-4, 4)), 5.0, seed=k + 3, energy=60000)
    for k in range(5): fire(f"tsf{k}", (TANKER[0] - 50 + k * 20, -0.2, TANKER[1] - 12 + rnd.uniform(-3, 3)), 3.0, seed=k + 30, energy=15000, light=k % 2 == 0)
    smm = mat_once("c9smoke2", lambda: smoke_mat("c9smoke2", "#14100e", 0.55))
    for k in range(3): smoke_column(f"ts{k}", (TANKER[0] - 30 + k * 25, 14, TANKER[1] + 5), 90, 6, 28, smm, drift=(-90, 30), seed=k + 9, puffs=16)
    # escorts
    warship("dd1", -40, 70, 0.0, 110, 11, "destroyer", 0.0)
    warship("dd2", -260, 300, 0.1, 100, 10, "destroyer", 0.0)
    warship("cv1", 240, 330, -0.05, 120, 13, "destroyer", 0.0)
    # U-boats
    uboat("u1", 20, 40, math.pi, 0.0, 0.0)
    for sd in (-1, 1):
        mesh_obj(f"u1wake{sd}", [(20 - 34, -0.21, 40 + sd * 2), (20 - 30, -0.21, 40 + sd * 6), (20 + 40, -0.21, 40 + sd * 14), (20 + 40, -0.21, 40 + sd * 4)], [(0, 1, 2, 3)], foam)
    u2 = uboat("u2", -20, 36, 0.3, 0.0, 0.0)
    # periscope with a feather of spray
    steel = mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    tube("pscope", [(3, -1.0, 8), (3, 1.8, 8)], 0.11, steel, res=2, bres=1)
    lathe("pshead", [(0.0, 0.0), (0.13, 0.0), (0.13, 0.35), (0.09, 0.45), (0.0, 0.45)], (3, 1.8, 8), steel, 16)
    bx("pswin", (3.0, 2.05, 7.87), (0.12, 0.1, 0.02), pmat("c9lens", "#0a1218", 0.05, 0.4), 0.0)
    lathe("psfoam", [(0.0, 0.0), (0.4, 0.0), (0.25, 0.12), (0.0, 0.15)], (3, -0.24, 8), foam, 16, sx=1.0, sz=2.2)
    mesh_obj("psfeather", [(2.7, -0.22, 8.2), (3.3, -0.22, 8.2), (4.6, -0.22, 2.0), (1.4, -0.22, 2.0)], [(0, 1, 2, 3)], foam)
    # floating wreckage near the tanker and lifeboat
    for k in range(20): bx(f"deb{k}", (TANKER[0] - 60 + rnd.uniform(0, 120), -0.22, TANKER[1] - 30 + rnd.uniform(-10, 10)), (rnd.uniform(0.6, 3), 0.15, rnd.uniform(0.3, 1.2)), wood_mat("fplank", "#6a5236", "#3a2a1a", 6, 0.8), 0.01, rnd.random() * 3)
    # light: low cold-gold sun under the cloud deck, grey sky fill, the burning tanker
    K.sun((0.2, 0.12, 1.0), 2.4, (1.0, 0.72, 0.5), 3.0)
    K.area((0, 60, -80), (0, 0, 60), 50000, (0.55, 0.65, 0.85), 120)
    K.area((-10, 8, -20), (-10, 2, 36), 6000, (0.7, 0.75, 0.85), 20)
    def update(f):
        if D.get("id") in SINK:
            u = max(0.0, min(1.0, (f - D["a"]) / max(1, D["b"] - D["a"])))
            u2.location = T(-20, -1.0 - 16.0 * u * u, 36); u2.rotation_euler = (0, -math.radians(28 + 10 * u), 0.3)
    if D.get("id") in SINK: update(D["a"])
    return {"update": update}
