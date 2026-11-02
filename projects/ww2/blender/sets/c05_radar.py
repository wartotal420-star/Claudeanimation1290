# Chapter 5: a Chain Home radar station on the south coast, 1940.
# Inside (shot 7): the receiver hut, x -3..3, z -2.6..2.6, ceiling y 2.7: the big grey receiver console on the back
# wall (z 2.35) with the round green A-scope tube (centre (0.0, 1.45, 2.06), r 0.24) whose echo blips grow per frame,
# dials, switches, a plotting table with a map of the coast, a window in the left wall (x -3) looking out at the masts.
# The operator stands at (0.55, 0, 1.25); keep x -1.2..1.6, z -1.6..1.6 clear.
# Outside (shot 8): the hut stands on the cliff-top grass (y 0); the cliff edge runs along z = 34 (sea at y -55
# beyond); the transmitter masts (110 m steel lattice) at x -70, -150, -230 and timber receiver towers at x 60, 130,
# z 0..12; sandbag blast walls round the hut. A fence, huts, a lorry, a gun pit dress the cliff top.
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, R90
from .c05_kit import (lattice_mast, sky, sea_mat, ground_mat, height_mesh, sun_light, area, point, spot, truck, lathe, tube, worn, mat_once, cached)
from .front import sandbag_wall, sandmat

def H(x, z):
    if z > 34 + 3 * math.sin(x * 0.05): return -58 + 6 * noise.noise(Vector((x * 0.02, z * 0.02, 1)))
    return 0.6 * noise.noise(Vector((x * 0.03, z * 0.03, 0.2))) + 0.2 * noise.noise(Vector((x * 0.2, z * 0.2, 3))) - 0.004 * max(0, -z - 20) ** 1.3

def build(M, D):
    random.seed(1937); K_.reset(); rnd = random.Random(3); sid = D.get("id", 0)
    sky((0.2, 0.38, 0.7), (0.5, 0.64, 0.84), (0.84, 0.86, 0.88), sun_dir=(0.6, 0.45, 0.4), sun_col=(1.0, 0.82, 0.55), glow=0.6, clouds=0.9)
    # ---------------- outside ----------------
    grass = ground_mat("c5grass", [(0.3, "#4a6a2a"), (0.5, "#6a8a3a"), (0.7, "#8a9a4a")], 0.05, 3.0)
    g = height_mesh("ground", -420, 300, -300, 40, 3.0, H, grass)
    chalk = ground_mat("c5chalk", [(0.3, "#c8c4b4"), (0.6, "#ece8dc"), (0.8, "#f8f4ea")], 0.1, 1.5, 0.8, 1.0)
    Kc = Kit("cliff")
    for k in range(80):
        x = -420 + k * 9; z = 34 + 3 * math.sin(x * 0.05)
        Kc.box((x, -28, z + 2), (9.6, 58, 4 + rnd.uniform(0, 3)), chalk, rnd.uniform(-0.1, 0.1), 0.2)
    Kc.build()
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(0, -56, 2000)); sea = bpy.context.object; sea.scale = (8000, 4000, 1); bpy.ops.object.transform_apply(scale=True)
    sea.data.materials.append(sea_mat("c5sea2", "#1e4a6a", "#3a7a8a", 0.1, 0.25))
    K = Kit("radar"); steel = mat_once("c5steel", lambda: worn("c5steel", "#6a6e72", "#7a4a2a", 0.55, 0.6, 3, 0.7, "#4a4a48"))
    tim = wood("#6a5a42", "#3a3020", 8, 0.8)
    for k, x in enumerate((-70, -150, -230)):
        z = 6 + k * 4; lattice_mast(K, (x, H(x, z) - 0.5, z), 110, 9.0, 2.5, steel, 22, 0.1, arms=[(50, 18), (75, 16), (100, 14)])
        for y in (50, 75, 100):           # curtain arrays slung between the cantilevers
            for j in range(8): K.box((x, y - 1.5 - j * 2.2, z), (16, 0.04, 0.04), pm("#2a2a2a", 0.5, 0.6), 0.1, 0.0)
    for k, x in enumerate((60, 130)):
        z = 2 + k * 6; lattice_mast(K, (x, H(x, z) - 0.3, z), 72, 7.0, 3.0, tim, 14, 0.4)
    for k in range(4):                    # guy wires
        for x in (-70, -150):
            a = k * math.pi / 2 + 0.4; tube(f"guy{x}{k}", [(x, 100, 6), (x + 70 * math.cos(a), 0, 6 + 70 * math.sin(a))], 0.05, pm("#3a3a3a", 0.5, 0.6), 2, 0)
    # buildings on the cliff top: transmitter block, huts with blast walls, a fence, a lorry
    BR = K_.brick("c5brick", "#8a5a42", "#6a4232", "#4a3e36", 3.0)
    K.box((-110, 2.2, -14), (14, 4.4, 8), BR, 0, 0.05); K.box((-110, 4.6, -14), (15, 0.4, 9), pm("#3a3a38", 0.8), 0, 0.02)
    for x in (-118, -102): K.box((x, 1.2, -9.95), (1.2, 2.2, 0.1), pm("#2a3a2a", 0.6), 0, 0.01)
    K.box((0, 1.3, 0), (6.4, 2.6, 5.4), wood("#4a5a3a", "#2a3a22", 4, 0.8), 0, 0.03)          # our hut, outside skin
    K.box((0, 2.75, 0), (6.8, 0.2, 5.8), pm("#2a2a2a", 0.85), 0, 0.02)
    for (x, z) in ((40, -20), (24, -40), (-40, -30)):
        K.box((x, 1.3, z), (8, 2.6, 4), wood("#5a6a48", "#3a4a2e", 4, 0.8), 0.3, 0.03); K.cyl((x, 2.4, z), 2.0, 8, pm("#4a5240", 0.7, 0.3), 16, "x", None, 0.3)
    for k in range(60):
        x = -300 + k * 8; z = -60 - 4 * math.sin(k * 0.3)
        K.cyl((x, 0.8 + H(x, z), z), 0.06, 1.8, tim, 6)
        for y in (0.6, 1.2, 1.7): K.box((x + 4, y + H(x, z), z), (8, 0.02, 0.02), pm("#5a5a5a", 0.5, 0.6), 0, 0.0)
    gorse = [pm("#2e4a22", 0.9), pm("#3a5a26", 0.9)]; yel = pm("#e8c030", 0.7)
    for k in range(70):                       # gorse and bramble clumps over the cliff top
        x, z = rnd.uniform(-60, 60), rnd.uniform(-70, 28)
        if abs(x) < 6 and abs(z) < 6: continue
        r = rnd.uniform(0.5, 1.4); K.sphere((x, H(x, z) + r * 0.4, z), r, gorse[k % 2], 10, (1.3, 0.7, 1.1))
        if k % 3 == 0:
            for j in range(4): K.sphere((x + rnd.uniform(-r, r) * 0.8, H(x, z) + r * 0.8, z + rnd.uniform(-r, r) * 0.6), 0.09, yel, 6)
    # a sandbagged Bofors gun pit and a flagpole near the camera end of the site
    K.cyl((26, 0.6 + H(26, -28), -28), 0.5, 1.2, pm("#4a5236", 0.5, 0.4), 14)
    K.cyl((26.8, 2.0 + H(26, -28), -27.2), 0.08, 3.2, pm("#3a3a32", 0.5, 0.6), 8, "z", None, 0.6, 0, -0.9)
    K.box((26, 1.0 + H(26, -28), -28.6), (1.6, 1.0, 0.08), pm("#4a5236", 0.5, 0.4), 0.3, 0.02)
    K.cyl((6, 5 + H(6, -22), -22), 0.06, 10, pm("#e8e4d8", 0.5), 8)
    K.box((6.7, 9.4 + H(6, -22), -22), (1.4, 0.9, 0.02), pm("#7a9ac8", 0.7), 0, 0.0)
    for k in range(3):
        x = 52 + k * 7; K.box((x, 1.3, -12 - k * 3), (5, 2.6, 3), wood("#5a6a48", "#3a4a2e", 4, 0.8), 0.2, 0.03); K.box((x, 2.75, -12 - k * 3), (5.4, 0.2, 3.4), pm("#2a2a2a", 0.85), 0.2, 0.02)
    K.build()
    sand = sandmat()
    for k in range(4): sandbag_wall(f"gp{k}", (26 + 2.2 * math.cos(k * R90), H(26, -28), -28 + 2.2 * math.sin(k * R90)), k * R90 + R90, 6, 3, sand, k + 10)
    for k, (x, z, yw) in enumerate(((-3.8, -1.0, R90), (3.8, 0.5, R90), (0.0, -3.6, 0.0), (-1.8, 3.6, 0.0))): sandbag_wall(f"sbh{k}", (x, H(x, z), z), yw, 7, 4, sand, k * 3)
    truck("rlorry", (14, H(14, -8), -8), 0.6, "#3a4a5a", "#5a5a48")
    # ---------------- inside the hut ----------------
    I = Kit("hut"); WL = grime("c5hutwall", "#d8d4c0", 0.25); FLm = wood("#5a4030", "#3a2618", 4, 0.6)
    I.box((0, 0.02, 0), (6.2, 0.04, 5.2), FLm, 0, 0)
    I.box((0, 2.66, 0), (6.2, 0.06, 5.2), grime("c5hutceil", "#c8c4b0", 0.3), 0, 0)
    I.box((0, 1.3, 2.55), (6.2, 2.6, 0.08), WL, 0, 0); I.box((0, 1.3, -2.55), (6.2, 2.6, 0.08), WL, 0, 0); I.box((3.05, 1.3, 0), (0.08, 2.6, 5.2), WL, 0, 0)
    I.box((-3.05, 0.5, 0), (0.08, 1.0, 5.2), WL, 0, 0); I.box((-3.05, 2.35, 0), (0.08, 0.6, 5.2), WL, 0, 0)       # window band in the left wall
    I.box((-3.05, 1.5, -1.8), (0.08, 1.0, 1.6), WL, 0, 0); I.box((-3.05, 1.5, 1.9), (0.08, 1.0, 1.4), WL, 0, 0)
    for z in (-1.0, -0.2, 0.6, 1.2): I.box((-3.03, 1.5, z), (0.06, 1.0, 0.05), wood("#3a2a1a", "#2a1a10", 8, 0.6), 0, 0.005)
    I.box((-3.03, 1.5, 0.1), (0.05, 0.05, 2.2), wood("#3a2a1a", "#2a1a10", 8, 0.6), 0, 0.005)
    I.box((-2.95, 1.5, -1.25), (0.08, 1.2, 0.55), cloth("#1a1a20"), 0, 0.05)                  # blackout curtain
    GR = mat_once("c5console", lambda: worn("c5console", "#7a8278", "#4a4a44", 0.45, 0.4, 25, 0.75))
    I.box((0, 1.15, 2.3), (4.2, 2.3, 0.5), GR, 0, 0.03)
    I.box((0, 0.8, 1.85), (4.2, 0.06, 0.5), GR, 0, 0.02)                                  # the desk shelf
    I.cyl((0.0, 1.45, 2.06), 0.3, 0.06, pm("#2a2a2a", 0.4, 0.6), 32, "z")
    I.cyl((0.0, 1.45, 2.03), 0.25, 0.02, em("#1a5a2a", 1.2), 32, "z")
    I.box((0.0, 1.43, 2.015), (0.42, 0.006, 0.004), em("#7aff9a", 8.0), 0, 0.0)            # the trace
    for k in range(9):                                                                      # graticule ticks
        I.box((-0.2 + k * 0.05, 1.41, 2.016), (0.003, 0.02, 0.003), em("#4ad87a", 3.0), 0, 0.0)
    for k in range(18):                                                                     # knobs, dials, switches
        x = -1.9 + (k % 9) * 0.45 + (0.3 if (k % 9) > 3 else 0); y = 1.0 if k < 9 else 2.0
        if abs(x) < 0.45 and k >= 9: continue
        I.cyl((x, y, 2.05), 0.06, 0.05, pm("#141414", 0.3), 16, "z"); I.box((x, y + 0.04, 2.02), (0.01, 0.05, 0.01), pm("#e8e0d0", 0.4), 0, 0.0)
    for k, x in enumerate((-1.5, -0.9, 0.9, 1.5)):
        I.cyl((x, 1.55, 2.06), 0.14, 0.04, brass(), 24, "z"); I.cyl((x, 1.55, 2.035), 0.12, 0.01, pm("#efe6cc", 0.5), 24, "z")
        I.box((x + 0.03, 1.57, 2.028), (0.006, 0.1, 0.004), pm("#a81e22", 0.5), 0, 0.0, 0.0, 0.6 - k * 0.5)
    for k in range(6): I.box((-1.9 + k * 0.08, 0.6, 2.04), (0.03, 0.06, 0.03), pm("#1a1a1a", 0.4), 0, 0.005)
    I.box((1.6, 0.6, 2.04), (0.5, 0.3, 0.02), pm("#e8e0c8", 0.6), 0, 0.005)
    text("RF7  RECEIVER", (1.6, 0.6, 2.02), 0.045, pm("#1a1a1a", 0.6), 0, "sans", 0.001, fit=0.45)
    text("SECRET", (-1.2, 2.2, 2.04), 0.09, pm("#a81e22", 0.6), 0, "sans", 0.002)
    # plotting table with the coast map, the plotter's rake, a phone, logbook, mugs, headphones
    I.box((-1.6, 0.85, -0.8), (1.4, 0.06, 1.0), wood("#6a4428", "#3a2414", 6, 0.4), 0, 0.01)
    for dx in (-0.62, 0.62):
        for dz in (-0.42, 0.42): I.box((-1.6 + dx, 0.42, -0.8 + dz), (0.05, 0.84, 0.05), wood("#4a2e18", "#22140a", 6, 0.5), 0, 0.005)
    I.box((-1.6, 0.885, -0.8), (1.3, 0.004, 0.9), pm("#c8d8c0", 0.7), 0, 0.0)
    for k in range(10): I.box((-2.2 + k * 0.13, 0.888, -0.8), (0.004, 0.002, 0.9), pm("#5a7a5a", 0.6), 0, 0.0)
    for k in range(7): I.box((-1.6, 0.888, -1.2 + k * 0.13), (1.3, 0.002, 0.004), pm("#5a7a5a", 0.6), 0, 0.0)
    for k in range(5): I.box((-1.9 + k * 0.12, 0.9, -1.0 + k * 0.08), (0.06, 0.03, 0.04), pm(("#c81e22", "#c81e22", "#e8c030", "#2a3a8a", "#c81e22")[k], 0.5), 0.3, 0.005)
    I.cyl((-1.2, 0.95, -0.5), 0.045, 0.1, pm("#f2ece0", 0.3), 16); I.cyl((-1.05, 0.95, -0.45), 0.045, 0.1, pm("#3a5a8a", 0.3), 16)
    I.box((-2.0, 0.9, -0.45), (0.3, 0.03, 0.22), pm("#3a2a1e", 0.6), 0.1, 0.01)
    I.torus((0.9, 0.86, 1.8), 0.1, 0.012, pm("#1a1a1a", 0.5), 16, 6, "z")
    for sd in (-1, 1): I.cyl((0.9 + sd * 0.1, 0.86, 1.8), 0.04, 0.03, pm("#1a1a1a", 0.5), 12, "x")
    I.box((1.4, 0.86, 1.75), (0.2, 0.08, 0.24), pm("#1a1a1c", 0.2), 0, 0.03)
    for k in range(3): I.box((2.4, 0.5 + k * 0.5, 1.0), (0.9, 0.03, 0.4), wood("#6a4428", "#3a2414", 6, 0.4), 0, 0.005)
    for k in range(10): I.box((2.05 + k * 0.08, 0.66 + (k % 3) * 0.5, 1.0), (0.05, 0.28, 0.3), pm(("#3a3a5a", "#5a2a22", "#a89a6a")[k % 3], 0.7), 0, 0.005)
    poster(I, (2.98, 1.6, -0.8), 0.5, 0.7, R90, "#e8d8b0", [("CARELESS", 0.12), ("TALK", 0.12), ("COSTS LIVES", 0.09)], "#a81e22", None, "sans", "#a81e22")
    poster(I, (1.6, 2.15, 2.03), 0.4, 0.32, 0, "#f0e8d0", [("NO SMOKING", 0.14), ("NEAR THE SET", 0.1)], "#1a1a1a", None, "sans")
    I.cyl((1.2, 0.25, -0.2), 0.22, 0.04, pm("#5a2a1a", 0.7), 14)                             # stool
    I.cyl((1.2, 0.12, -0.2), 0.03, 0.24, pm("#3a3a3a", 0.5, 0.5), 6)
    I.build()
    # lights inside: green-shaded pendant (warm), the scope glow, daylight through the window
    I2 = Kit("hutlamp"); I2.cyl((0.4, 2.3, 0.6), 0.25, 0.14, pm("#1e4a2e", 0.3, 0.3), 20, "y", 0.05); I2.cyl((0.4, 2.48, 0.6), 0.006, 0.36, pm("#1a1a1a", 0.6), 6); I2.build()
    point((0.4, 2.12, 0.6), 140, (1.0, 0.72, 0.42), 0.05)
    point((0.0, 1.45, 1.75), 6, (0.4, 1.0, 0.55), 0.2)
    area((-3.6, 1.5, 0.1), (0, 1.0, 0.3), 160 if sid == 7 else 40, (0.75, 0.85, 1.0), 1.2, 2.2)
    sun_light((-0.6, -0.45, -0.5), 4.2, (1.0, 0.88, 0.7), 1.5)
    # echo blips on the trace (they grow as the raid closes in, shot 7)
    B = []
    for k, (x, h) in enumerate(((-0.1, 0.12), (-0.02, 0.08), (0.06, 0.15), (0.12, 0.06))):
        bpy.ops.mesh.primitive_cube_add(location=T(x, 1.43, 2.013)); o = bpy.context.object; o.scale = (0.004, 0.002, 0.5)
        o.data.materials.append(em("#9affb0", 10.0)); B.append((o, x, h, k))
    def update(f):
        for o, x, h, k in B:
            g = max(0.0, min(1.0, (f - 690 - k * 12) / 30)) * h * (0.85 + 0.15 * math.sin(f * 0.9 + k))
            o.scale = (0.004, 0.002, max(0.0005, g / 2)); o.location = T(x, 1.43 + g / 2, 2.013)
    update(645)
    return {"update": update}
