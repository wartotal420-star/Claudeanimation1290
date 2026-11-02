# Tokyo, the night of 9-10 March 1945 (chapter 13: "American bombers burn Japanese cities" / the firebombing raid).
# Serious: no people, no jokes. A city of tiled wooden houses along canals, burning block by block under an orange sky of
# smoke; B-29s low overhead (they flew in low at night), searchlight beams. Fires spread over F_START..F_START+240.
# three.js layout: the city spreads over x -400..400, z 0..900 on flat ground (y 0); a canal along z 150 and x 60;
#   a temple roof at (-40, 0, 220); cameras sit on a rise at the near edge (z < 0, y 15..40) looking +z, or low on the
#   canal bank at (60, 2, 120). The B-29s cross from -x to +x at y 1500..1900 over z 300..600.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK

F_START = 2100

def build(M, D):
    rnd = random.Random(310)
    S = bpy.context.scene
    CK.sky(S.world, (0.2, 0.4, 0.9), [(0.0, (0.5, 0.16, 0.05)), (0.08, (0.28, 0.08, 0.04)), (0.3, (0.06, 0.03, 0.03)), (1.0, (0.01, 0.01, 0.02))],
           sun_col=(0, 0, 0), cloud_dark=(0.02, 0.012, 0.012), cloud_lit=(0.6, 0.18, 0.05), cover=0.7, strength=1.0, glow=0.0, disc=False, band=(0.0, 0.3), fade=(1.0, 0.6))
    CK.sun_light((0.3, 0.6, 0.7), 0.15, (0.5, 0.55, 0.8), 2.0)
    ground = mat_once("tkg", lambda: CK.green_hill_mat("tkg", "#3a3430", "#2a2420", "#4a4038"))
    CK.heightfield("tkground", -900, 900, -200, 1600, 10, lambda x, z: (max(0.0, -z - 20) * 0.25 if z < -20 else 0.0), ground)
    CK.sea("canal", -900, 900, 140, 160, -0.6, CK.water_mat("tkw", "#14181c", "#2a2420", 2.0, 0.03, 0.1))
    CK.sea("canal2", 52, 68, 0, 900, -0.6, CK.water_mat("tkw2", "#14181c", "#2a2420", 2.0, 0.03, 0.1))
    K = Kit("tk"); tile = pm("#2e2e34", 0.6); wl = mat_once("tkwall", lambda: worn("tkwall", "#8a7a64", "#4a3e30", 0.9, 0.0, 2, 0.6, "#6a5a48"))
    lit = em("#ff9a40", 2.5)
    blocks = []
    for k in range(700):
        x, z = rnd.uniform(-400, 400), rnd.uniform(0, 900)
        if 138 < z < 162 or 48 < x < 72: continue
        w, d, h = rnd.uniform(5, 10), rnd.uniform(5, 9), rnd.uniform(3, 7)
        K.box((x, h / 2, z), (w, h, d), wl, rnd.choice((0, 0, 0.1, -0.1)), 0.0)
        K.box((x, h + 0.8, z), (w + 0.8, 1.6, d + 0.8), tile, 0.0, 0.0)
        if k % 4 == 0: K.box((x, h * 0.5, z - d / 2 - 0.02), (w * 0.5, 1.0, 0.04), lit, 0.0, 0.0)
        blocks.append((x, z))
    K.box((-40, 6, 220), (24, 12, 18), wl, 0.0, 0.0)
    for k in range(3): K.box((-40, 13 + k * 2.6, 220), (32 - k * 7, 0.6, 26 - k * 6), tile, 0.0, 0.0)
    for k in range(10): K.box((60, 0.2, 40 + k * 90), (18, 0.6, 4), pm("#4a4038", 0.7), 0.0, 0.0)
    K.build()
    # the fires: rows of flames over the houses, smoke lit from below, glow lights; switched on in waves
    waves = []
    for w in range(6):
        objs = []
        for k in range(14):
            x, z = rnd.choice(blocks)
            if z > 120 + w * 130 or z < w * 100: continue
            objs += CK.fireball(f"tf{w}_{k}", (x, 6, z), rnd.uniform(4, 8), w * 20 + k, 0)
        cx = rnd.uniform(-200, 200); cz = 150 + w * 110
        objs += CK.smoke(f"ts{w}", (cx, 12, cz), 400, 40, 160, "#2a140c", 0.85, (180, 60), w, 12)
        objs += CK.smoke(f"tg{w}", (cx, 6, cz), 30, 50, 90, "#a8441a", 0.55, (0, 0), w + 20, 4)
        objs.append(lib.light("POINT", T(cx, 40, cz), 6e6, (1.0, 0.45, 0.15), 30))
        waves.append((F_START + w * 30, objs))
    # B-29s low over the city, searchlight beams
    b29 = [CK.inst(CK.plane("b29", gear=False, spin=True), f"tb{k}") for k in range(7)]
    beam_m = mat_once("tkbeam", lambda: CK.smoke_mat("tkbeam", "#d8e4ff", 0.35))
    beams = []
    for k, (x, z, dx, dz) in enumerate(((-250, 300, 0.25, 0.3), (180, 420, -0.2, 0.25), (-60, 650, 0.1, -0.2), (320, 700, -0.3, -0.1))):
        beams.append(tube(f"beam{k}", [(x, 0, z), (x + dx * 2400, 2400, z + dz * 2400)], 18, beam_m, res=2, bres=3))
    for o in beams: o.visible_shadow = False
    def update(f):
        for f0, objs in waves: CK.show(objs, f >= f0)
        for k, o in enumerate(b29):
            u = (f - F_START + 40 - k * 9) / 30.0
            CK.place(o, (-1200 + 120 * u + (k % 3) * 60, 1500 + (k % 3) * 120, 320 + k * 45), (1, 0, 0.05), 0.0, 1.0)
            o.hide_render = not (-1500 < -1200 + 120 * u < 1500)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
