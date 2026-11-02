# A US carrier at sea (chapter 7): shot 11 the Enterprise steaming safely (f < 2000, SBDs + Wildcats parked aft);
# shots 21-25 the Hornet with sixteen B-25s crammed on deck, rough grey sea, the briefing board, Doolittle's take-off
# (2400 <= f < 4000); shot 38 Midway, SBDs ranged and the pilots waiting (f >= 4400).
# three.js layout: the carrier at the origin, bow +x (yaw 0), flight deck top y 16 spanning x -110..+110, z -13..13;
#   island on the starboard side at x 14, z 10.5. Keep clear for characters: deck x 0..30, z -12..6 (forward of the
#   planes). The briefing board stands at (28, 16, -9) facing -z (Hornet frames only).
#   B-25s: two staggered columns, z -5 (x -10, -22 ... -94) and z +5 (x -16 ... -100), noses +x; the lead one (Doolittle)
#   at (-10, z -5) rolls and lifts off f 3105..3185.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj, cup
from sets import c07_kit as CK

DECK = 16.0
HORNET = (2400, 4000)
SUN = (0.5, 0.62, -0.6)
def hornet(f): return HORNET[0] <= f < HORNET[1]
def b25_take(f):
    s = (f - 3095) / 30.0
    if s < 0: return (-10, DECK + 2.3, -5.0), (1, 0.06, 0)
    x = -10 + 0.5 * 14.0 * s * s
    y = DECK + 2.3 + max(0.0, x - 95) * 0.16
    return (x, y, -5.0 + max(0.0, x - 60) * 0.02), (1, 0.16 if x > 95 else 0.06, 0)

def build(M, D):
    rnd = random.Random(1804)
    S = bpy.context.scene
    W_sun = S.world
    CK.sky(W_sun, SUN, [(0.0, (0.72, 0.8, 0.88)), (0.08, (0.42, 0.58, 0.82)), (0.4, (0.15, 0.32, 0.64)), (1.0, (0.05, 0.13, 0.4))],
           sun_col=(30, 28, 22), cloud_dark=(0.42, 0.45, 0.52), cloud_lit=(1.35, 1.28, 1.15), cover=0.55, strength=0.8, glow_col=(1.0, 0.95, 0.8), glow=0.35)
    W_grey = bpy.data.worlds.new("wgrey"); W_grey.use_nodes = True
    CK.sky(W_grey, (0.3, 0.5, -0.8), [(0.0, (0.5, 0.52, 0.55)), (0.1, (0.36, 0.4, 0.46)), (1.0, (0.16, 0.19, 0.25))],
           sun_col=(3, 3, 3), cloud_dark=(0.22, 0.24, 0.28), cloud_lit=(0.62, 0.64, 0.68), cover=1.0, strength=0.9, glow_col=(0.9, 0.9, 0.9), glow=0.2, band=(0.0, 0.3), fade=(1.0, 0.6))
    sun = CK.sun_light(SUN, 4.8, (1.0, 0.94, 0.85), 1.5); sun_g = CK.sun_light((0.3, 0.6, -0.7), 1.6, (0.85, 0.9, 1.0), 12)
    calm = CK.sea("ocean", -6000, 6000, -6000, 6000, -0.25, CK.water_mat("uwater", "#0a3050", "#1a5a70", 0.6, 0.06, 0.6))
    rough = CK.sea("rough", -6000, 6000, -6000, 6000, -0.24, CK.water_mat("rwater", "#1a2a34", "#3a5258", 1.4, 0.15, 1.6))
    caps = CK.whitecaps("caps", -1200, 1200, -1200, 1500, 700, rnd)
    rcaps = CK.whitecaps("rcaps", -1200, 1200, -1200, 1500, 2600, rnd, -0.2, (3, 9))
    before = set(bpy.data.objects.keys())
    P = CK.carrier("cv", 0, 0, 0.0, 230, 26, False, mark="8", deck_h=DECK)
    CK.wake("cv", P, 230, 26, 1.0)
    K = Kit("deckp"); CK.deck_props(K, P, DECK, -100, 60, 26, rnd, False)
    # forward of the planes: a deck tractor, ready-ammunition lockers, coiled hoses, a life-raft rack on the island side
    K.box((6, DECK + 0.55, 8.5), (2.4, 1.1, 1.5), pm("#d8b030", 0.5), 0.0, 0.05)
    for sd in (-1, 1):
        for e in (-0.8, 0.8): K.cyl((6 + e, DECK + 0.32, 8.5 + sd * 0.8), 0.32, 0.22, pm("#141414", 0.8), 14, "z")
    for k in range(4): K.box((2 + k * 1.3, DECK + 0.45, 11.6), (1.1, 0.9, 0.9), pm("#5e6a76", 0.5, 0.3), 0.0, 0.02)
    for k in range(3):
        for j in range(4): K.torus((-2 + k * 1.6, DECK + 0.05 + j * 0.07, 11.2), 0.45, 0.05, pm("#1e1e1e", 0.7), 18, 6)
    for k in range(5): K.cyl((12 + k * 2.6, DECK + 0.9, 13.4), 0.5, 0.35, pm("#c8a050", 0.6), 16, "z")
    K.build()
    # ---------- plane parks ----------
    b25s, sbds = [], []
    for k in range(16):
        col = k % 2; row = k // 2
        lx = (-10 if col == 0 else -16) - row * 12; lz = -5.0 if col == 0 else 5.0
        if k == 0: continue
        o = CK.inst(CK.plane("b25", gear=True, spin=False), f"b25_{k}"); CK.place(o, (lx, DECK + 2.3, lz), (1, 0.06, 0.08 * (1 if col else -1))); b25s.append(o)
    lead = CK.inst(CK.plane("b25", gear=True, spin=True), "b25lead")
    for r in range(6):
        for j, lz in enumerate((-8.0, 0.0, 8.0)):
            kind = "wildcat" if r < 2 else "sbd"
            o = CK.inst(CK.plane(kind, gear=True, spin=False), f"sbd{r}{j}"); CK.place(o, (-20 - r * 14 + (j % 2) * 2, DECK + 1.35, lz), (1, 0.14, 0)); sbds.append(o)
    # ---------- the briefing board (Hornet) ----------
    B = Kit("board"); bw = wood("#6a4a2a", "#3a2614", 6.0, 0.6)
    B.box((28, DECK + 1.75, -9.0), (2.4, 1.6, 0.06), pm("#1e2a24", 0.9), 0.0, 0.0)
    for sx in (-1.25, 1.25): B.box((28 + sx, DECK + 1.2, -8.95), (0.08, 2.4, 0.08), bw, 0.0, 0.0)
    B.box((28, DECK + 0.92, -9.08), (2.5, 0.06, 0.18), bw, 0.0, 0.0)
    for sx in (-1.1, 1.1): B.box((28 + sx, DECK + 0.6, -8.6), (0.07, 1.4, 0.07), bw, 0.0, 0.6, 0.0)
    board = B.build()
    txt = ktext("THE PLAN:\n1. TAKE OFF\n2. BOMB TOKYO\n3. KEEP FLYING\n4. CHINA ???", (28, DECK + 1.78, -9.04), 0.21, pm("#ecebe2", 0.9), 0.0, "sans", 0.002)
    chalk = board + [txt]
    # crew coffee on the ammo lockers, a megaphone
    cup("ucup", (2.0, DECK + 0.9, 11.6)); cup("ucup2", (3.4, DECK + 0.9, 11.5), "#e8e0d0")
    lathe("mega", [(0.03, 0.0), (0.05, 0.05), (0.16, 0.45), (0.17, 0.46)], (4.6, DECK + 0.9, 11.6), pm("#d8d4c8", 0.5), 20)
    fill = CK.area((40, DECK + 12, -40), (10, DECK + 1, -2), 9000, (1.0, 0.92, 0.85), 30)
    def update(f):
        h = hornet(f)
        S.world = W_grey if h else W_sun
        sun.hide_render = h; sun_g.hide_render = not h
        calm.hide_render = h; rough.hide_render = not h; caps.hide_render = h; rcaps.hide_render = not h
        CK.show(b25s + chalk, h); lead.hide_render = not h
        if h: p, d = b25_take(f); CK.place(lead, p, d)
        CK.show(sbds, not h)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
