# Chapter 6: the endless Ukrainian steppe, summer 1941: sunflower fields, a dusty road with a German tank column and
# trucks, a burning village, the golden domes of Kyiv on the horizon, columns of Soviet prisoners.
# Layout (three coords): flat ground y 0; the road runs along z (x -4..4) from z -40 to 900; sunflower fields both
# sides beyond |x| 7; the tank column on the road at z 30..300 (moves -z in update: frames 1133-1343);
# a burning village at x 60..110, z 120..200; Kyiv's domes at (-260, 0, 1400). Prisoners walk on the verge at
# x -6..-4.5 (cards); keep x -7..-4 clear. Sunflowers start at |x| 7.
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, glassm, crate, barrel, R90
from .c05_kit import (sky, ground_mat, height_mesh, sun_light, area, point, truck, panzer, pose, lathe, tube, worn, mat_once, cached, empty,
                      smoke_mat, smoke_column, fire, fsphere)

def build(M, D):
    random.seed(1941); K_.reset(); rnd = random.Random(23)
    sky((0.18, 0.36, 0.7), (0.5, 0.62, 0.8), (0.9, 0.82, 0.66), sun_dir=(0.6, 0.5, 0.6), sun_col=(1.0, 0.85, 0.55), glow=0.7, clouds=1.0, cloud_scale=1.0)
    soil = ground_mat("c6soil", [(0.3, "#4a3a28"), (0.5, "#6a5232"), (0.7, "#7a6a3a")], 0.05, 3)
    height_mesh("steppe", -1500, 1500, -60, 2200, 30, lambda x, z: 4 * noise.noise(Vector((x * 0.002, z * 0.002, 1))) * min(1, abs(x) / 50), soil)
    K = Kit("steppe"); dust = ground_mat("c6dust", [(0.3, "#8a7452"), (0.6, "#a88a62")], 0.2, 4)
    K.box((0, 0.02, 400), (8, 0.04, 900), dust, 0, 0.0)
    for x in (-2, 2):
        for k in range(150): K.box((x, 0.045, -40 + k * 6), (0.4, 0.02, 6.1), pm("#6a5638", 0.95), 0, 0.0)
    # sunflowers: rows of stems with leaves and heads facing the sun (toward -x, +z)
    stem = pm("#4a6a2a", 0.8); leaf = pm("#3a5a22", 0.8); petal = pm("#f0b820", 0.6); disc = pm("#3a2210", 0.8)
    S = Kit("sunfl")
    for sd in (-1, 1):
        for row in range(14):
            for k in range(70):
                x = sd * (7.5 + row * 0.9) + rnd.uniform(-0.15, 0.15); z = -10 + k * 0.85 + rnd.uniform(-0.2, 0.2); h = rnd.uniform(1.5, 2.1)
                S.cyl((x, h / 2, z), 0.025, h, stem, 5)
                S.box((x + 0.15, h * 0.55, z), (0.3, 0.02, 0.2), leaf, rnd.uniform(0, 3), 0.0, 0.3)
                S.cyl((x - 0.03, h + 0.05, z - 0.05), 0.2, 0.03, petal, 10, "z", None, 0.5, 0, -0.3)
                S.cyl((x - 0.04, h + 0.05, z - 0.07), 0.12, 0.05, disc, 10, "z", None, 0.5, 0, -0.3)
    S.build()
    far = ground_mat("c6far", [(0.3, "#b89a30"), (0.6, "#c8a838")], 0.01, 0.3)
    for sd in (-1, 1): K.box((sd * 300, 0.6, 350), (560, 1.2, 760), far, 0, 0.0)
    # telegraph poles, a broken cart, a knocked-out Soviet tank (BT style) by the road, a road sign in Cyrillic
    POLE = wood("#5a4a32", "#3a3020", 8, 0.8)
    for k in range(30):
        z = -20 + k * 30; K.cyl((5.5, 3.5, z), 0.1, 7, POLE, 8); K.box((5.5, 6.7, z), (1.2, 0.1, 0.1), POLE, 0, 0.01)
    sg = wood("#c8c0a0", "#8a8468", 12, 0.8)
    K.cyl((-5.2, 1.2, 8), 0.06, 2.4, sg, 6); K.box((-5.2, 2.2, 8), (1.4, 0.35, 0.05), sg, 0.2, 0.01)
    text("КИЕВ  120", (-5.17, 2.2, 7.95), 0.16, pm("#1a1a1a", 0.6), 0.2, "sans", 0.002, fit=1.2)
    burnt = mat_once("c6burnt", lambda: worn("c6burnt", "#2a2420", "#6a3a1e", 0.9, 0.3, 8, 0.55, "#141010"))
    panzer("bt", (12, 0, 40), 0.7, "#3a3a2a", True, K)
    fire("btfire", (12, 2.4, 40), 0.9, seed=4, energy=1500)
    K.box((-9, 0.6, 22), (2.2, 0.3, 1.2), wood("#5a4a32", "#3a3020", 8, 0.8), 0.5, 0.02, 0, 0.2)
    K.torus((-9.8, 0.5, 21.4), 0.5, 0.05, wood("#5a4a32", "#3a3020", 8, 0.8), 16, 6, "x", 0.5, 0, 0.6)
    # the burning village (log huts, thatched roofs), Kyiv's domes far off
    LOG = wood("#6a5438", "#3a2e1e", 4, 0.85); TH = pm("#8a7a4a", 0.95)
    for k in range(12):
        x, z = 60 + (k % 4) * 14 + rnd.uniform(-3, 3), 120 + (k // 4) * 25 + rnd.uniform(-3, 3)
        K.box((x, 1.6, z), (6, 3.2, 5), LOG, 0, 0.05); K.cyl((x, 4.0, z), 3.6, 6.4, TH if k % 3 else burnt, 4, "x", 0.2, math.pi / 4)
        if k % 3 == 0: fire(f"vfire{k}", (x, 3.5, z), 2.2, seed=k, energy=6000)
    smm = smoke_mat("c6smk", "#2a2422", 0.5)
    for k, (x, z) in enumerate(((70, 125), (95, 150), (80, 175))): smoke_column(f"vsm{k}", (x, 6, z), 80, 4, 18, smm, drift=(-40, 60), seed=k, puffs=12)
    W = grime("c6church", "#f0ece0", 0.15); GLD = K_.gold()
    for k, (x, z, s) in enumerate(((-260, 1400, 1.0), (-200, 1450, 0.7), (-320, 1480, 0.8))):
        K.box((x, 18 * s, z), (30 * s, 36 * s, 30 * s), W, 0, 0.2)
        for j, (dx, dz, r) in enumerate(((0, 0, 7), (-11, -11, 4), (11, -11, 4), (-11, 11, 4), (11, 11, 4))):
            K.cyl((x + dx * s, 40 * s + (6 if j == 0 else 0) * s, z + dz * s), r * 0.8 * s, 8 * s, W, 16)
            fsphere(K, (x + dx * s, (48 + (6 if j == 0 else 0)) * s, z + dz * s), r * s, GLD, 16, (1, 1.15, 1))
            K.cyl((x + dx * s, (55 + (8 if j == 0 else 0)) * s, z + dz * s), 0.4 * s, 6 * s, GLD, 6)
    K.build()
    # the column: tanks, trucks, motorcycles (moving), dust behind it
    col = []
    for k in range(8):
        e = empty(f"col{k}"); kk = Kit(f"colk{k}")
        if k % 3 == 2: truck(f"ctr{k}", (0, 0, 0), 0.0, "#5a5e5a", "#6a6a5a", Kx=kk)
        else: panzer(f"cp{k}", (0, 0, 0), 0.0, "#5a5e5a", k % 2 == 0, kk)
        for o in kk.build(): o.parent = e
        col.append(e)
    dm = smoke_mat("c6dustcl", "#b8a07a", 0.3)
    dust_obs = []
    for k in range(10):
        o = lib.blob(f"dcl{k}", T(0, 3, 60 + k * 24), (6, 3, 8), dm, 1.5, k); o.visible_shadow = False; dust_obs.append(o)
    sun_light((-0.55, -0.6, -0.55), 4.8, (1.0, 0.86, 0.62), 1.0)
    area((0, 30, -30), (0, 0, 40), 8000, (0.6, 0.7, 1.0), 40)
    def update(f):
        u = max(0, f - 441) if f < 1000 else max(0, f - 1133)
        for k, e in enumerate(col):
            z = 34 + k * 22 - 0.12 * u; x = 1.3 if k % 2 else -1.3
            e.location = T(x, 0.02, z); e.rotation_euler = (0, 0, math.pi / 2)
        for k, o in enumerate(dust_obs): o.location = T(rnd.uniform(-1, 1) * 0, 3, 50 + k * 24 - 0.12 * u)
    update(1133)
    return {"update": update}
