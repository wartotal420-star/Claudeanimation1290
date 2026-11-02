# Leyte Gulf, October 1944 (chapter 13): the ocean from above, hundreds of American ships off the Philippines; Japan's
# decoy carriers far to the north with almost no planes on their decks; then the decoy force broken and sinking.
# three.js layout (sea y -0.25):
#   The US fleet: ~160 ships (destroyers, cruisers, transports, carriers) spread over x -4000..4000, z -3000..3000, all
#   heading +x. Aerial cameras sit at y 600..1500 over (0, 0, -2500) looking +z / down.
#   The decoy force at z 30000 (far north): carrier "dc" centred (0, 0, 30000), bow +x, deck top y 14 (EMPTY deck, a
#   few crew); a second decoy carrier (200, 0, 30600). Characters stand on dc's deck at x -10..10, z 30000 +- 8.
#   f >= F_SINK: the decoy carrier lists and burns (shot "Japan's navy is basically gone"), dusk light.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK
from sets import front as FR

DZ = 30000
F_SINK = 1290
SUN = (0.5, 0.5, -0.7)

def small_ship(K, x, z, kind, rnd):
    grey = pm("#6a737c", 0.55, 0.2); dk = pm("#3a4048", 0.5, 0.3); deck = pm("#7a6a54", 0.7)
    L, B = {"dd": (110, 11), "ca": (180, 19), "ap": (140, 19), "cv": (220, 30), "bb": (210, 32), "lst": (100, 15)}[kind]
    K.box((x, 1.5, z), (L, 6, B), grey, 0.0, 0.0); K.box((x + L * 0.47, 1.5, z), (L * 0.1, 6, B * 0.5), grey, 0.0, 0.0, 0.0, 0.0)
    if kind == "cv":
        K.box((x, 9, z), (L * 0.95, 1, B), deck, 0.0, 0.0); K.box((x + L * 0.05, 14, z + B * 0.4), (L * 0.12, 9, 3), grey, 0.0, 0.0)
        for k in range(rnd.randint(8, 18)): K.box((x - L * 0.4 + k * 6, 10, z + rnd.uniform(-B * 0.3, B * 0.3)), (5, 0.8, 9), pm("#5c6e80", 0.6), 0.0, 0.0)
    else:
        K.box((x, 4.5, z), (L * 0.6, 1, B * 0.9), deck, 0.0, 0.0)
        K.box((x + L * 0.08, 8, z), (L * 0.18, 7, B * 0.5), grey, 0.0, 0.0)
        K.cyl((x - L * 0.05, 11, z), B * 0.12, 8, grey, 10)
        if kind in ("ca", "bb"):
            for t in (0.3, 0.18, -0.3): K.box((x + L * t, 6.5, z), (B * 0.35, 2.5, B * 0.35), dk, 0.0, 0.0)
        if kind == "ap":
            for k in range(4): K.box((x - L * 0.3 + k * L * 0.18, 6, z), (6, 2, 8), pm("#5a6a3a", 0.6), 0.0, 0.0)
    K.box((x - L * 1.2, -0.21, z), (L * 1.4, 0.02, B * 1.2), mat_once("ffoam", FR.foam_mat), 0.0, 0.0)

def build(M, D):
    rnd = random.Random(1023)
    S = bpy.context.scene
    W_day = S.world
    CK.sky(W_day, SUN, [(0.0, (0.75, 0.8, 0.86)), (0.08, (0.46, 0.6, 0.82)), (0.4, (0.16, 0.34, 0.66)), (1.0, (0.05, 0.14, 0.42))],
           sun_col=(30, 28, 22), cloud_dark=(0.42, 0.45, 0.52), cloud_lit=(1.35, 1.28, 1.15), cover=0.5, strength=0.8, glow=0.35)
    W_dusk = bpy.data.worlds.new("ldusk"); W_dusk.use_nodes = True
    CK.sky(W_dusk, (-0.95, 0.07, 0.2), [(0.0, (1.0, 0.45, 0.18)), (0.05, (0.8, 0.32, 0.22)), (0.16, (0.3, 0.18, 0.3)), (0.5, (0.06, 0.06, 0.16)), (1.0, (0.02, 0.02, 0.06))],
           sun_col=(26, 10, 3), cloud_dark=(0.12, 0.06, 0.1), cloud_lit=(1.3, 0.5, 0.2), cover=0.55, strength=0.9, glow_col=(1.0, 0.4, 0.12), glow=1.0)
    sun = CK.sun_light(SUN, 4.6, (1.0, 0.94, 0.85), 1.5); dsun = CK.sun_light((-0.95, 0.07, 0.2), 2.6, (1.0, 0.5, 0.22), 2.0)
    CK.sea("lsea", -40000, 40000, -40000, 60000, -0.25, CK.water_mat("lwater", "#0a3050", "#1a5a72", 0.15, 0.08, 0.8))
    CK.whitecaps("lcaps", -6000, 6000, -5000, 5000, 3000, rnd, -0.22, (8, 20))
    hill = mat_once("lhill", lambda: CK.green_hill_mat("lhill", "#3a6a2a", "#22421a", "#5a5a3a"))
    CK.heightfield("leyte", -9000, 9000, 4500, 12000, 150, CK.ridge_fn(4500, 9000, -30, 700, 5, 0.0006), hill)
    K = Kit("fleet")
    kinds = ["dd"] * 6 + ["ap"] * 4 + ["ca"] * 2 + ["lst"] * 3 + ["cv", "bb"]
    for k in range(170):
        x, z = rnd.uniform(-4000, 4000), rnd.uniform(-3000, 3000)
        small_ship(K, x, z, rnd.choice(kinds), rnd)
    K.build()
    # the decoy force: two carriers with near-empty decks, an escort
    P = CK.carrier("dc", 0, DZ, 0.0, 230, 28, True, deck_h=14.0)
    CK.wake("dc", P, 230, 28, 0.8)
    for k, (lx, lz) in enumerate(((-60, -6), (-85, 5))):
        o = CK.inst(CK.plane("zero", gear=True, spin=False), f"dz{k}"); CK.place(o, P(lx, 15.4, lz), (1, 0.12, 0))
    before = set(bpy.data.objects.keys())
    P2 = CK.carrier("dc2", 220, DZ + 700, 0.15, 220, 26, True, deck_h=14.0)
    FR.warship("dd1", -500, DZ + 300, 0.0, 120, 12, "destroyer", 0.0)
    for k in list(bpy.data.objects.keys()):
        if k.startswith("dd1smk"): bpy.data.objects.remove(bpy.data.objects[k])
        elif k.startswith("dd1ensign"): bpy.data.objects[k].data.materials[0] = CK.jp_flag_mat()
    Kp = Kit("dprops"); CK.deck_props(Kp, P, 14.0, -100, 60, 28, rnd, True); Kp.build()
    sink = CK.fireball("dsf", P(-40, 14.2, 0), 2.5, 1, 9000) + CK.fireball("dsf2", P(30, 14.2, 4), 2.0, 2, 6000)
    sink += CK.smoke("dss", P(-40, 18, 0), 260, 10, 60, "#141210", 0.9, (-200, 80), 4, 12)
    sink += CK.smoke("dss2", (220, 18, DZ + 700), 300, 12, 70, "#141210", 0.9, (-200, 80), 5, 12)
    dc_objs = [o for o in bpy.data.objects if o.name.startswith("dc") and not o.name.startswith("dc2")]
    def update(f):
        s_ = f >= F_SINK
        S.world = W_dusk if s_ else W_day; sun.hide_render = s_; dsun.hide_render = not s_
        CK.show(sink, s_)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
