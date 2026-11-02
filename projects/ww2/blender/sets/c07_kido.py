# A Japanese carrier of the strike force (chapter 7): shot 7 the dawn launch for Pearl Harbor (f < 2000); shots 39-41
# Midway (f >= 4600): the deck on fire, American dive bombers falling out of the clouds, three more carriers burning.
# three.js layout: the carrier at the origin, bow +x (yaw 0), flight deck top y 14 spanning x -110..+110, z -13..13.
#   Deck park: rows of Zeros / Vals / Kates (noses +x) at x -18..-100, z -7 / 0 / 7; keep clear for characters:
#   the deck at x -16..-4, z -11..-2 (deck crew) and x 6..20, z -10..4 (officers by the island at x 41, z 11).
#   Other carriers (clones) at (520, 0, 820), (-640, 0, 1150), (900, 0, -900), (-1300, 0, -500); a battleship at (300, 0, -700).
# Dawn: sun low astern (-x), planes rim-lit, engines turning; a Zero rolls down the deck and takes off (f 768..860).
# Midway: noon light, fires among the parked planes, black smoke, SBDs diving from y ~1400 onto the deck (f 4690..4790).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK
from sets import front as FR

DECK = 14.0
MIDWAY = 4600
SUN_DAWN = (-1.0, 0.09, 0.32)
SUN_DAY = (0.35, 0.8, -0.45)
OTHERS = [(520, 820), (-640, 1150), (900, -900), (-1300, -500)]

def zero_takeoff(f):
    s = (f - 768) / 30.0
    if s < 0: return None
    x = -20 + 0.5 * 9.0 * s * s if s < 3.4 else -20 + 0.5 * 9.0 * 3.4 ** 2 + 30.6 * (s - 3.4)
    y = DECK + 1.25 + max(0.0, x - 70) * 0.18
    return (x, y, 0.0), (1.0, 0.18 if x > 70 else 0.0, 0.0)
def sbd_path(k, f):
    """dive from the clouds at ~70 degrees, release over the deck at f_hit, pull out low"""
    tx, tz = (-30 + k * 30, -4 + k * 5); fh = 4752 + 28 * k
    ty = 90
    d = Vector((0.25, -1.0, 0.1 - 0.12 * k)).normalized(); rem = 150 * (fh - f) / 30.0
    if rem > 0: return Vector((tx, ty, tz)) - d * rem, d
    s_ = -rem / 150.0
    return Vector((tx + 60 * s_, ty + 25 * s_, tz + 15 * s_)), Vector((1, 0.35, 0.25))

def build(M, D):
    rnd = random.Random(1206)
    S = bpy.context.scene
    W_dawn = S.world
    CK.sky(W_dawn, SUN_DAWN, [(0.0, (1.0, 0.45, 0.16)), (0.04, (0.85, 0.35, 0.22)), (0.12, (0.32, 0.2, 0.32)), (0.35, (0.08, 0.08, 0.2)), (1.0, (0.02, 0.025, 0.08))],
           sun_col=(30, 12, 4), cloud_dark=(0.08, 0.05, 0.1), cloud_lit=(1.4, 0.55, 0.22), cover=0.55, strength=1.0, glow_col=(1.0, 0.4, 0.12), glow=1.0)
    W_day = bpy.data.worlds.new("wday"); W_day.use_nodes = True
    CK.sky(W_day, SUN_DAY, [(0.0, (0.7, 0.78, 0.86)), (0.08, (0.42, 0.58, 0.8)), (0.4, (0.16, 0.32, 0.62)), (1.0, (0.05, 0.14, 0.4))],
           sun_col=(30, 28, 24), cloud_dark=(0.42, 0.44, 0.5), cloud_lit=(1.3, 1.25, 1.18), cover=0.75, strength=0.8, glow_col=(1.0, 0.95, 0.85), glow=0.3,
           band=(0.0, 0.25), fade=(0.95, 0.5))
    sun_d = CK.sun_light(SUN_DAWN, 3.0, (1.0, 0.55, 0.25), 1.0); sun_n = CK.sun_light(SUN_DAY, 5.0, (1.0, 0.95, 0.88), 1.5)
    CK.sea("ocean", -6000, 6000, -6000, 6000, -0.25, CK.water_mat("kwater", "#0a2a40", "#1a4a5e", 0.6, 0.08, 0.7))
    CK.whitecaps("caps", -1500, 1500, -1500, 2000, 900, rnd)
    # ---------- the carrier ----------
    before = set(bpy.data.objects.keys())
    P = CK.carrier("cv", 0, 0, 0.0, 230, 28, True, deck_h=DECK)
    CK.wake("cv", P, 230, 28, 1.0)
    ship = [bpy.data.objects[k] for k in set(bpy.data.objects.keys()) - before]
    K = Kit("deckp"); CK.deck_props(K, P, DECK, -100, 80, 28, rnd, True)
    # signal-flag man's stand, a bamboo pole with a streamer, chocks next to every plane, a deck crane by the island
    K.box((10, DECK + 0.5, -12.0), (1.2, 1.0, 1.2), pm("#6a6a5a", 0.5), 0.0, 0.02)
    K.box((46, DECK + 2.5, 8.0), (0.5, 5.0, 0.5), pm("#4a4e52", 0.5, 0.5), 0.0, 0.0); K.box((50, DECK + 4.8, 8.0), (8.0, 0.4, 0.4), pm("#4a4e52", 0.5, 0.5), 0.0, 0.0)
    tube("crhook", [(54, DECK + 4.8, 8.0), (54, DECK + 1.6, 8.0)], 0.03, pmat("hcable", "#1a1a1a", 0.6), res=2, bres=0)
    # ---------- the deck park ----------
    planes = []; chocks = pm("#c8b060", 0.6)
    rows = [("zero", -20), ("zero", -33), ("val", -47), ("val", -62), ("kate", -78), ("kate", -95)]
    for r, (kind, lx) in enumerate(rows):
        for j, lz in enumerate((-7.5, 0.0, 7.5)):
            if r == 0 and j == 1: continue                   # the first Zero is the one taking off
            src = CK.plane(kind, gear=True, spin=True)
            o = CK.inst(src, f"dp{r}{j}"); CK.place(o, (lx + (j % 2) * 2.0, DECK + 1.25 + (0.25 if kind == "zero" else 0.3), lz), (1, 0.12, 0)); planes.append(o)
            for sd in (-1, 1): K.box((lx + 0.8 + (j % 2) * 2, DECK + 0.12, lz + sd * 1.7), (0.3, 0.24, 0.5), chocks, 0.0, 0.02)
    K.build()
    zt = CK.inst(CK.plane("zero", gear=True, spin=True), "ztake")
    # ---------- the rest of the strike force ----------
    for k, (x, z) in enumerate(OTHERS): CK.clone(ship, x, z, f"o{k}")
    FR.warship("bbj", 300, -700, 0.0, 200, 30, "battleship", 0.0)
    for k in list(bpy.data.objects.keys()):
        o = bpy.data.objects[k]
        if k.startswith("bbjensign"): o.data.materials[0] = CK.jp_flag_mat()
        if k.startswith("bbjsmk"): bpy.data.objects.remove(o)
    # ---------- Midway: fires, smoke, wrecked planes, the dive bombers ----------
    burn = []
    for k, (x, z, sz) in enumerate(((-28, -3, 1.6), (-55, 5, 2.0), (-82, -6, 1.8), (-34, 2, 1.2), (-40, 9, 1.3), (-70, -9, 1.5), (-100, 2, 2.0), (-62, -2, 1.4))):
        burn += CK.fireball(f"bf{k}", (x, DECK + 0.2, z), sz, k, 2500)
    burn += CK.smoke("bsm0", (-70, DECK + 5, 2), 300, 10, 70, "#121010", 0.92, (-320, 140), 3, 12)
    burn += CK.smoke("bsm1", (-100, DECK + 4, 4), 200, 8, 50, "#1a1614", 0.9, (-280, 110), 5, 10)
    burn += CK.smoke("bglow", (-50, DECK + 2, 0), 10, 9, 14, "#8a3810", 0.6, (0, 0), 11, 4)
    for k, (x, z) in enumerate(OTHERS[:3]):
        burn += CK.fireball(f"of{k}", (x - 40, DECK + 1, z), 6.0, 20 + k, 30000)
        burn += CK.smoke(f"osm{k}", (x - 40, DECK + 5, z), 420, 20, 110, "#121010", 0.92, (-260, 120), 20 + k, 12)
    explo = []
    for k, (x, z, f0) in enumerate(((-35, 2, 4760), (-75, -2, 4786), (5, -1, 4810))):
        explo.append((f0, CK.fireball(f"ex{k}", (x, DECK + 1, z), 4.0, 40 + k, 80000) + CK.smoke(f"exs{k}", (x, DECK + 6, z), 40, 8, 18, "#2a1a10", 0.85, (0, 0), 40 + k, 5)))
    sbd = [CK.inst(CK.plane("sbd", gear=False, spin=True), f"sbd{k}") for k in range(3)]
    fill = CK.area((40, 30, -60), (-20, DECK, 0), 30000, (0.9, 0.85, 0.8), 40)
    def update(f):
        mid = f >= MIDWAY
        S.world = W_day if mid else W_dawn
        sun_d.hide_render = mid; sun_n.hide_render = not mid
        CK.show(burn, f >= 4760)
        for f0, objs in explo: CK.show(objs, mid and f >= f0)
        r = None if mid else zero_takeoff(f)
        if mid or f < 700:
            CK.place(zt, (-20, DECK + 1.5, 0.0), (1, 0.12, 0))
        elif r is None: CK.place(zt, (-20, DECK + 1.5, 0.0), (1, 0.12, 0))
        else: CK.place(zt, r[0], r[1])
        for k, o in enumerate(sbd):
            if not mid: o.hide_render = True; continue
            p, d = sbd_path(k, f); o.hide_render = p.y > 2600
            CK.place(o, tuple(p), tuple(d), 0.3 * k, 2.0)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
