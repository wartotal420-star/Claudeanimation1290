# Kiska, Aleutians, August 1943 (chapter 9's wink): a fog-wrapped tundra hillside, Japanese sod-roofed bunkers, abandoned
# kit, a wrecked barge on the black beach; inside the main bunker only a dog is waiting. Cold overcast with the fog kept to
# wisps (soft fx cards from ch09.ts) plus a light world haze.
# Layout (three, y up): ground flat (y 0) on the approach |x| < 12, z -10..22; the bunker mouth at (0, 0, 24) facing -z
# (log frame 1.6 wide, 1.8 high), sod mound behind it; more bunkers at (-14, 0, 30) (16, 0, 34); a wrecked barge at
# (-24, 0, -6). Soldiers advance from z -8 toward the mouth. INTERIOR at x 100: dugout x 97.5..102.5, z -2..5, log walls,
# floor y 0, ceiling 2.1, the dog's spot (100.4, 0, 3.2), entrance (camera side) at z -2.
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, text, cup
from sets import c09_kit as K

bx, cy = K.bx, K.cy
def H(x, z):
    if x > 80: return 0.0
    h = 2.2 * noise.noise(Vector((x * 0.03, z * 0.03, 0.7))) + 0.3 * noise.noise(Vector((x * 0.2, z * 0.2, 1.4)))
    h += 6 * K.sm(26, 60, z) + 3 * K.sm(14, 40, abs(x))
    flat = (1 - K.sm(12, 18, abs(x))) * (1 - K.sm(22, 27, z)) * K.sm(-16, -10, z)
    h = h * (1 - flat)
    for bx_, bz_, r in ((0, 27.5, 4.5), (-14, 33, 3.5), (16, 37, 3.5)):
        d = math.hypot(x - bx_, z - bz_)
        if d < r: h = max(h, 2.1 * math.sqrt(max(0.0, 1 - (d / r) ** 2)))
    h -= 3.0 * K.sm(-12, -24, z)
    return h
def build(M, D):
    rnd = random.Random(1943)
    K.sky("#7a8890", "#c8ccc8", 0.9, "#8a969c", "#d8dcd8")
    gm = K._ground("c9tundra", [(0.25, lib.hexc("#4a5a3a")), (0.45, lib.hexc("#6a7448")), (0.6, lib.hexc("#8a8458")), (0.8, lib.hexc("#5a6a4a"))], 0.9, 0.06, 5.0, 0.6, "#3a3028", 0.8)[0]
    K.heightfield("ground", H, -70, 70, -40, 90, 0.8, gm, lambda x, z: 0.7 if abs(x - 0.3 * math.sin(z * 0.3)) < 1.0 and -10 < z < 24 else 0.0)
    bx("sea", (0, -2.6, -120), (600, 0.1, 180), lib.principled("c9ksea", lib.hexc("#2a3a40"), 0.1), 0)
    grass = K.mat_once("c9kgrass", lambda: worn("c9kgrass", "#8a8a52", "#5a6a3a", 0.85, 0.0, 6, 0.5, "#7a7a48"))
    from sets.front import grass_tuft_src, scatter
    src = grass_tuft_src(grass, 5); pts = []
    while len(pts) < 900:
        x_, z_ = rnd.uniform(-50, 50), rnd.uniform(-14, 70)
        if abs(x_ - 0.3 * math.sin(z_ * 0.3)) < 1.2 and z_ < 24: continue
        pts.append((x_, H(x_, z_) - 0.03, z_))
    scatter(src, "kg", pts, s=(1.0, 2.2), seed=6); src.location = T(0, -50, 0)
    rock = K.mat_once("c9krock", lambda: worn("c9krock", "#4a4a4c", "#2a2a2c", 0.8, 0.0, 1.5, 0.55, "#3a3a3a"))
    for k in range(40):
        x_, z_ = rnd.uniform(-50, 50), rnd.uniform(-20, 70)
        if abs(x_) < 5 and z_ < 26: continue
        K.blob3(f"kr{k}", (x_, H(x_, z_), z_), (rnd.uniform(0.4, 1.6), rnd.uniform(0.3, 1.0), rnd.uniform(0.4, 1.4)), rock, 0.2, k)
    logm = wood_mat("c9klog", "#5a4a36", "#2e2418", 4, 0.85)
    dark = K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0))
    for k, (x_, z_) in enumerate(((0, 24.0), (-14, 30.0), (16, 34.0))):
        y0 = 0.0 if k == 0 else H(x_, z_ - 1.5)
        for sd in (-1, 1): tube(f"bkp{k}{sd}", [(x_ + sd * 0.85, y0 - 0.2, z_), (x_ + sd * 0.85, y0 + 1.9, z_)], 0.13, logm, res=2, bres=1)
        tube(f"bkl{k}", [(x_ - 1.3, y0 + 1.95, z_), (x_ + 1.3, y0 + 1.95, z_)], 0.15, logm, res=2, bres=1)
        for j in range(4): tube(f"bkr{k}{j}", [(x_ - 1.6, y0 + 2.2 + j * 0.05, z_ + 0.3 + j * 0.45), (x_ + 1.6, y0 + 2.2 + j * 0.05, z_ + 0.3 + j * 0.45)], 0.14, logm, res=2, bres=1)
        bx(f"bkd{k}", (x_, y0 + 0.95, z_ + 0.4), (1.6, 1.9, 0.1), dark, 0)
        for sd in (-1, 1): K.sandbags(f"bks{k}{sd}", (x_ + sd * 1.7, y0, z_ - 0.3), math.pi / 2 + sd * 0.4, 3, 3, k * 2 + sd)
    tube("kpost", [(2.4, 0, 22.5), (2.4, 1.6, 22.5)], 0.05, logm, res=2, bres=1)
    bx("ksign", (2.4, 1.45, 22.47), (0.7, 0.35, 0.03), pmat("c9ksign", "#d8ccb0", 0.7), 0.01, 0.1)
    text("立入禁止", (2.4, 1.45, 22.44), 0.12, pmat("kink2", "#1a1a1a", 0.6), yaw=0.1, flat=False)
    for k in range(5): K.helmet_ground(f"kh{k}", (rnd.uniform(-6, 6), 0, rnd.uniform(14, 22)), rnd.uniform(0, 6), "#7a7048", "brodie")
    for k in range(6): K.ammo_box(f"kab{k}", (-3.5 + (k % 3) * 0.4, 0, 19 + (k // 3) * 0.3), 0.3 * k, "", "#6a6040")
    K.blanket_roll("kbl", (3.2, 0.12, 18.5), 0.4, "#7a7048")
    K.wire("kw1", (-8, H(-8, 12), 12), 8, 0.3, 0.4); K.wire("kw2", (9, H(9, 14), 14), 8, -0.2, 0.4)
    barge = K.mat_once("c9barge", lambda: worn("c9barge", "#5a4a3a", "#3a2a1e", 0.8, 0.4, 3, 0.55, "#2a1a10"))
    P = K.P_of(-24, -8, 0.6, -1.2, 0.15)
    K.prism("barge", [(-6, 0.0), (6, 0.0), (7, 1.6), (-7, 1.8)], -2.2, 2.2, P, barge)
    for k in range(8):
        x_, z_ = -30 + k * 8, -16 + rnd.uniform(-2, 2)
        tube(f"kfence{k}", [(x_, H(x_, z_) - 0.2, z_), (x_ + 0.1, H(x_, z_) + 1.0, z_)], 0.05, logm, res=2, bres=1)
    interior(rnd, logm)
    K.sun((0.3, 0.6, -0.5), 1.2, (0.85, 0.9, 1.0), 25.0)
    K.area((0, 30, -30), (0, 0, 20), 16000, (0.75, 0.82, 0.9), 80)
    # light world haze for depth (kept thin; the visible fog banks are fx wisps)
    vol = bpy.data.materials.new("c9haze"); vol.use_nodes = True; nt = vol.node_tree
    for x in list(nt.nodes): nt.nodes.remove(x)
    o_ = nt.nodes.new("ShaderNodeOutputMaterial"); pv = nt.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Density"].default_value = 0.012
    pv.inputs["Color"].default_value = (0.85, 0.88, 0.9, 1); nt.links.new(pv.outputs[0], o_.inputs["Volume"])
    hz = bx("haze", (0, 10, 30), (180, 40, 160), vol, 0); hz.visible_shadow = False
    return {}
def interior(rnd, logm):
    X = 100.0
    bx("ifloor", (X, -0.05, 1.5), (7, 0.1, 9), K.mat_once("c9kmud", lambda: worn("c9kmud", "#4a3a2a", "#2a2018", 0.9, 0.0, 3, 0.5, "#3a2a1c")), 0)
    for k in range(9): tube(f"iwl{k}", [(X - 2.5, 0.12 + k * 0.24, -2), (X - 2.5, 0.12 + k * 0.24, 5)], 0.12, logm, res=2, bres=1)
    for k in range(9): tube(f"iwr{k}", [(X + 2.5, 0.12 + k * 0.24, -2), (X + 2.5, 0.12 + k * 0.24, 5)], 0.12, logm, res=2, bres=1)
    for k in range(11): tube(f"iwb{k}", [(X - 2.6, 0.12 + k * 0.2, 4.9), (X + 2.6, 0.12 + k * 0.2, 4.9)], 0.11, logm, res=2, bres=1)
    for k in range(16): tube(f"iceil{k}", [(X - 2.8, 2.15, -2 + k * 0.45), (X + 2.8, 2.15, -2 + k * 0.45)], 0.13, logm, res=2, bres=1)
    bx("ibench", (X - 1.6, 0.45, 2.0), (1.0, 0.06, 3.0), wood_mat("c9kplank", "#7a6040", "#4a3420", 8, 0.8), 0.01)
    for sz in (-1, 1): bx(f"ibl{sz}", (X - 1.6, 0.22, 2.0 + sz * 1.3), (0.9, 0.44, 0.06), logm, 0.01)
    for k in range(3): cup(f"ibowl{k}", (X - 1.7 + k * 0.25, 0.48, 1.4 + k * 0.2), "#e8e0d0", False)
    bx("ibox", (X + 1.7, 0.3, 3.6), (0.6, 0.6, 0.5), wood_mat("c9crate", "#8a7a52", "#5a4a2a", 10, 0.7), 0.01, 0.2)
    text("米", (X + 1.69, 0.35, 3.33), 0.18, pmat("kink2", "#1a1a1a", 0.6), yaw=0.2, flat=False)
    lathe("ilamp", [(0.0, 0.0), (0.06, 0.0), (0.06, 0.08), (0.03, 0.1), (0.05, 0.15), (0.05, 0.24), (0.0, 0.26)], (X + 1.7, 0.6, 3.6), pmat("c9lampm", "#4a4a30", 0.5, 0.6), 12)
    K.blob3("istraw", (X + 0.4, 0, 3.6), (1.0, 0.15, 0.7), K.mat_once("c9straw", lambda: worn("c9straw", "#b89a5a", "#7a6a3a", 0.95, 0.0, 20, 0.5)), 0.08, 2)
    K.blanket_roll("ibl", (X + 1.2, 0.1, 4.3), 0.0, "#6a6a4a")
    lathe("idish", [(0.0, 0.0), (0.12, 0.0), (0.14, 0.05), (0.12, 0.05), (0.0, 0.02)], (X - 0.4, 0, 3.0), pmat("c9tin", "#8a8a88", 0.4, 0.8), 16)
    K.area((X, 1.5, -3.5), (X, 0.5, 3), 120, (0.8, 0.86, 0.95), 1.6, 1.8)
    K.lamp_glow("ilg", (X + 1.6, 0.95, 3.4), 18, (1.0, 0.7, 0.4), 0.05)
