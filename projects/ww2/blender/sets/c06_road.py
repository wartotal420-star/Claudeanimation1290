# Chapter 6: the road to Moscow, autumn-winter 1941. Light "grey" = the rasputitsa (rain, a sea of mud, a tank sunk to
# its turret, a truck stuck, a cart); any other light = deep winter (snow, falling flakes, everything frozen, icicles, a
# thermometer at -40, a frozen truck and machine gun, the forest edge the Siberian ski troops burst from).
# Layout (three coords): the road along z (x -4..4) from z -30 to 400, forest of firs and birches beyond |x| 12;
# the sunk tank at (1.5, -1.3, 16), the stuck truck at (-2.0, -0.4, 26), the cart at (5, 0, 9); the thermometer on a
# post at (3.2, 0, 4.0) (dial face toward -z, centre y 1.6); the frozen MG at (-3.6, 0, 6.5); a log hut at (-9, 0, 12);
# the forest edge (ski troops) at x -14..14, z 40..46. Keep x -3..3, z 2..12 clear (soldiers).
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, glassm, crate, barrel, R90
from .c05_kit import (sky, ground_mat, height_mesh, sun_light, area, point, spot, truck, panzer, lathe, tube, worn, mat_once, cached, snow_mat, fsphere, empty,
                      smoke_mat, smoke_column, fire)

def mud_mat():
    def mk():
        m = lib.principled("c6mud", hexc("#3a2a1c"), 0.25); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.25; nz.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        r = lib.ramp(n, l, nz.outputs["Fac"], [(0.3, hexc("#2a1e14")), (0.5, hexc("#4a3624")), (0.7, hexc("#5a4630"))]); l.new(r.outputs["Color"], b.inputs["Base Color"])
        wet = lib.ramp(n, l, nz.outputs["Fac"], [(0.4, (0.08, 0.08, 0.08)), (0.6, (0.6, 0.6, 0.6))]); l.new(wet.outputs["Color"], b.inputs["Roughness"])
        fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 3; fn.inputs["Detail"].default_value = 8; l.new(tc.outputs["Object"], fn.inputs["Vector"]); lib.bump(n, l, fn.outputs["Fac"], 0.7, 0.06)
        return m
    return cached("c6mud", mk)

def fir(K, x, y, z, h, rnd, needles, trunk, snow=None):
    K.cyl((x, y + h * 0.15, z), h * 0.03, h * 0.3, trunk, 6)
    for j in range(5):
        r = h * (0.28 - j * 0.05); yy = y + h * (0.22 + j * 0.16)
        K.cyl((x, yy, z), r, h * 0.26, needles, 9, "y", 0.03)
        if snow: K.cyl((x, yy + h * 0.06, z), r * 0.75, h * 0.1, snow, 9, "y", 0.02)

def build(M, D):
    random.seed(1941); K_.reset(); rnd = random.Random(31)
    winter = D["light"] != "grey"
    if winter:
        sky((0.5, 0.56, 0.66), (0.72, 0.74, 0.78), (0.86, 0.86, 0.88), sun_dir=(0.4, 0.15, 0.9), sun_col=(1.0, 0.8, 0.6), glow=0.5, clouds=0.3, cloud_shade=(0.7, 0.72, 0.78))
    else:
        sky((0.32, 0.34, 0.38), (0.45, 0.46, 0.48), (0.6, 0.6, 0.6), sun_dir=(0.4, 0.3, 0.9), sun_col=(0.8, 0.8, 0.8), glow=0.1, clouds=0.5, cloud_shade=(0.4, 0.4, 0.44))
    SNOW = snow_mat("rdsnow")
    def H(x, z):
        n_ = noise.noise(Vector((x * 0.08, z * 0.08, 0.7)))
        rut = -0.18 * math.exp(-((abs(x) - 1.6) / 0.35) ** 2) if abs(x) < 4 else 0
        return 0.15 * n_ + rut + 0.02 * max(0, abs(x) - 4) ** 1.3
    ground = SNOW if winter else mud_mat()
    height_mesh("road", -60, 60, -30, 400, 0.6, H, ground)
    if not winter:
        grass = ground_mat("c6wetgrass", [(0.3, "#3a4228"), (0.6, "#5a5a32")], 0.1, 4)
        g = height_mesh("verge", -60, 60, -30, 400, 1.5, lambda x, z: H(x, z) + (0.08 if abs(x) > 6 else -1), grass)
    K = Kit("road"); needles = pm("#1e3020", 0.9); trunk = pm("#3a2a1e", 0.9); bark = mat_once("c6birch2", lambda: worn("c6birch2", "#e8e4dc", "#2a2a2a", 0.7, 0.0, 10, 0.75, "#c8c4bc"))
    for k in range(260):
        sx = rnd.choice((-1, 1)); x = sx * rnd.uniform(12, 55); z = rnd.uniform(-10, 300); h = rnd.uniform(9, 18)
        if k % 4 == 0:
            K.cyl((x, h / 2, z), 0.15, h, bark, 8)
            if not winter:
                for j in range(4): fsphere(K, (x + rnd.uniform(-1, 1), h * (0.6 + 0.1 * j), z + rnd.uniform(-1, 1)), 1.5, pm(("#a8782a", "#c89a3a", "#8a6a2a")[j % 3], 0.8), 10)
        else: fir(K, x, 0, z, h, rnd, needles, trunk, SNOW if winter else None)
    for k in range(14):                                   # the forest edge facing the road (ski troops come out here)
        x = -14 + k * 2.2; fir(K, x, 0, 44 + rnd.uniform(-1.5, 1.5), rnd.uniform(8, 12), rnd, needles, trunk, SNOW if winter else None)
    # log hut, a well, a fence, telegraph poles leaning, an onion-domed church far up the road
    LOG = wood("#5a4630", "#3a2e1e", 4, 0.85)
    for j in range(9): K.cyl((-9, 0.15 + j * 0.28, 12), 0.15, 5.0, LOG, 10, "z")
    K.cyl((-9, 3.4, 12), 3.0, 5.4, SNOW if winter else pm("#4a3a2a", 0.9), 4, "z", 0.2, math.pi / 4)
    K.box((-6.55, 1.4, 12), (0.05, 0.8, 0.8), pm("#2a4a7a", 0.4), 0, 0.02)
    for k in range(12): K.box((-7.5, 0.6, 2 + k * 0.9), (0.06, 1.2, 0.1), LOG, 0, 0.0, rnd.uniform(-0.1, 0.1))
    K.box((-7.5, 0.9, 7), (0.06, 0.08, 11), LOG, 0, 0.0)
    for k in range(10):
        z = -10 + k * 30; lean = rnd.uniform(-0.15, 0.15)
        K.cyl((6.5, 3.5, z), 0.1, 7, LOG, 8, "y", None, 0, 0, lean)
    W = grime("rdchurch", "#e8e4dc", 0.2)
    K.box((-30, 8, 220), (10, 16, 10), W, 0.3, 0.1); K.cyl((-30, 19, 220), 3, 6, W, 12); fsphere(K, (-30, 23.5, 220), 3.4, pm("#3a6a5a", 0.4, 0.3), 14, (1, 1.2, 1))
    # vehicles: the tank sunk to its turret, a stuck truck, a cart; in winter a frozen truck with icicles and a frozen MG
    panzer("sunk", (1.5, -1.25 if not winter else 0.0, 16), R90 * 1.1, "#5a5e5a", False, K)
    truck("stuck", (-2.0, -0.45 if not winter else 0.0, 26), R90 * 0.9, "#5a5e5a", "#6a6a5a")
    K.box((5, 0.6, 9), (1.6, 0.3, 2.6), LOG, 0.3, 0.02)
    for sd in (-1, 1): K.torus((5 + sd * 0.85, 0.5 if winter else 0.3, 9), 0.5, 0.05, LOG, 16, 6, "x", 0.3)
    if winter:
        ice = lib.principled("rdice", hexc("#d8eaf8"), 0.05); ice.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.6
        for k in range(16): K.cyl((1.5 + 2.6 - k * 0.32, 1.35, 16 - 1.2 + (k % 3) * 0.1), 0.03, 0.3 + (k % 3) * 0.12, ice, 6, "y", 0.002)
        for k in range(12): K.cyl((-2.0 - 1.0 + k * 0.18, 2.1, 26 - 2.2), 0.025, 0.25 + (k % 4) * 0.08, ice, 6, "y", 0.002)
        K.box((1.5, 2.95, 16), (2.6, 0.25, 2.4), SNOW, 0.0, 0.1); K.box((-2.0, 2.4, 26), (3.0, 0.25, 2.2), SNOW, 0.0, 0.1)
        # the machine gun on its tripod, crusted white
        K.cyl((-3.6, 0.55, 6.5), 0.05, 1.1, pm("#2a2a2a", 0.5, 0.6), 8, "z", None, 0.0, 0, 0.0)
        K.box((-3.6, 0.65, 6.2), (0.12, 0.14, 0.6), pm("#2a2a2a", 0.5, 0.6), 0, 0.01)
        K.box((-3.6, 0.73, 6.2), (0.14, 0.04, 0.62), SNOW, 0, 0.02)
        for sd in (-1, 1): K.box((-3.6 + sd * 0.25, 0.3, 6.4), (0.04, 0.6, 0.04), pm("#2a2a2a", 0.5, 0.6), 0, 0.0, 0, sd * 0.4)
        for k in range(6): K.cyl((-3.6 + (k - 2.5) * 0.04, 0.55, 5.95), 0.008, 0.12, ice, 5)
        # the thermometer on its post
        K.cyl((3.2, 0.8, 4.2), 0.06, 1.6, LOG, 8)
        K.box((3.2, 1.6, 4.1), (0.32, 1.0, 0.05), pm("#e8e4d8", 0.4), 0, 0.01)
        K.cyl((3.2, 1.6, 4.07), 0.012, 0.8, glassm(), 8); K.sphere((3.2, 1.17, 4.07), 0.03, pm("#c81e22", 0.3), 8)
        K.box((3.2, 1.25, 4.065), (0.01, 0.12, 0.01), pm("#c81e22", 0.3), 0, 0.0)
        for k in range(9): K.box((3.13, 1.25 + k * 0.08, 4.07), (0.05, 0.006, 0.004), pm("#1a1a1a", 0.6), 0, 0.0)
        text("-40°", (3.28, 1.29, 4.065), 0.05, pm("#1a1a1a", 0.6), 0, "sans", 0.001)
        text("0°", (3.28, 1.85, 4.065), 0.05, pm("#1a1a1a", 0.6), 0, "sans", 0.001)
        K.box((3.2, 2.15, 4.12), (0.4, 0.1, 0.12), SNOW, 0, 0.03)
    else:
        for k in range(40): fsphere(K, (rnd.uniform(-4, 4), -0.02, rnd.uniform(-5, 60)), rnd.uniform(0.4, 1.4), pm("#2a2a24", 0.02), 10, (1.4, 0.04, 1.0))   # puddles
    K.build()
    # falling snow / rain: a sheet of flakes or streaks that slides down per frame (two stacked copies)
    fl = Kit("flakes"); fm = em("#f4f8ff", 1.2) if winter else pm("#c8d0d8", 0.1)
    for k in range(1800):
        x, y, z = rnd.uniform(-10, 10), rnd.uniform(0, 8), rnd.uniform(-2, 30)
        if winter: fl.box((x, y, z), (0.025, 0.025, 0.025), fm, rnd.uniform(0, 3), 0.0)
        else: fl.box((x, y, z), (0.008, 0.35, 0.008), fm, 0, 0.0, 0.0, 0.1)
    flk = fl.build()
    flk2 = []
    for o in flk:
        c = o.copy(); bpy.context.scene.collection.objects.link(c); flk2.append(c)
    # light: overcast, cold; a soft fill
    if winter:
        sun_light((-0.4, -0.25, -0.9), 1.8, (1.0, 0.85, 0.7), 4)
        area((0, 25, -20), (0, 0, 20), 6000, (0.7, 0.78, 0.95), 30)
    else:
        sun_light((-0.4, -0.5, -0.8), 0.9, (0.85, 0.85, 0.9), 15)
        area((0, 25, -20), (0, 0, 20), 5000, (0.65, 0.68, 0.75), 30)
    def update(f):
        dy = -((f * (0.12 if winter else 0.5)) % 8.0)
        for o in flk: o.location = T(0.0 + (0.3 * math.sin(f * 0.05) if winter else 0), dy, 0)
        for o in flk2: o.location = T(0.0, dy + 8.0, 0)
    update(0)
    return {"update": update}
