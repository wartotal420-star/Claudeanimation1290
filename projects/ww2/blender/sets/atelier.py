# The painter's room in Vienna (shot 21), sets.ts buildAtelier layout: room x -5..5, z -5..5 (back wall z 3.5),
# window at (-2.5, 1.0..3.2, 3.5), easel at (0.4, 0.8) (the canvas is an exported card at (0.4, 1.22, 0.78)),
# paint table (1.8, 1.0), Hitler at (-0.4, 0.45). Keep clear: the fx cards at (0.36, 1.32, 0.72) 1.2 x 0.52.
# A poor garret: faded wallpaper with stains, a real window opening onto Vienna rooftops (cool daylight + a low warm
# sun shaft across the floor), an oil lamp and a little stove glowing warm, rejected paintings everywhere.
import bpy, math, random
import numpy as np
import lib
from lib import T, TS
from sets import ikit as K
from sets.ikit import bx, cy, bl, sph, cone, torus, txt

def naive_building(seed, kind):
    """Hitler-style careful, lifeless postcard buildings (flat colours, matching the canvas card)."""
    a = K.landscape_img(seed, 320, 240, naive=True)
    if kind == "church":
        K.rect(a, 0.3, 0.35, 0.7, 0.72, "#efe0b8"); K.poly(a, [(0.26, 0.36), (0.5, 0.2), (0.74, 0.36)], "#8a4a3a")
        K.rect(a, 0.45, 0.08, 0.55, 0.4, "#e8d8b0"); K.poly(a, [(0.43, 0.1), (0.5, -0.05), (0.57, 0.1)], "#3a7a6a")
        K.ellipse(a, 0.5, 0.5, 0.05, 0.08, "#6a4a2a")
    elif kind == "dome":
        K.rect(a, 0.2, 0.42, 0.8, 0.72, "#efe8d8"); K.ellipse(a, 0.5, 0.42, 0.14, 0.16, "#5a9a8a")
        for k in range(6): K.rect(a, 0.25 + k * 0.1, 0.48, 0.28 + k * 0.1, 0.7, "#d8ccb0")
    elif kind == "bridge":
        K.rect(a, 0, 0.62, 1, 1, "#5a8ab8"); K.rect(a, 0.1, 0.5, 0.9, 0.58, "#c8b898")
        for k in range(3): K.ellipse(a, 0.25 + k * 0.25, 0.66, 0.09, 0.08, "#5a8ab8")
    K.frame_border(a, 0.03, "#f2ece0")
    return a
def stamp_rejected(a):
    h, w = a.shape[:2]; K.rect(a, 0.12, 0.38, 0.88, 0.62, "#c81e28", 0.0)
    x, y = K.grid(a); K.put(a, ((np.abs(y - 0.5) < 0.11) & (np.abs(y - 0.5) > 0.085) | (np.abs(x - 0.5) < 0.38) & (np.abs(x - 0.5) > 0.36)) & (np.abs(y - 0.5) < 0.11) & (np.abs(x - 0.5) < 0.38), "#c81e28", 0.9)
    K.stamp(a, "ABGELEHNT", 0.5, 0.45, 0.1, "#c81e28", 0.9, 0.1, "center")
    return a

def build(M, D):
    random.seed(1907); rs = random.Random(1907)
    FL = K.planks("atfloor", "#9a6e44", "#4a2e16", "Y", 0.18, 2.0, 0.55, 0.0)
    WP = K.wall_mat("atwallp", K.wallpaper_img("#8a9672", "#5a6448", "#c8c8a0", seed=3), 0.45)
    WD = K.grain("atwood", "#7a4a26", "#3a200c", "X", 1.0, 0.5); WDV = K.grain("atwoodv", "#7a4a26", "#3a200c", "Z", 1.0, 0.5)
    BR = M["brass"]; DARK = M["dark"]; IRON = M["iron"]; WHITE = K.flat("atwhite", "#ece4d0", 0.6)
    bx("floor", (0, -0.05, 0), (11, 0.1, 11), FL, 0)
    bx("ceil", (0, 3.65, 0), (11, 0.1, 11), lib.plaster("atceil", "#d8ccb2"), 0)
    for k in range(5): bx(f"cbeam{k}", (-4 + k * 2, 3.5, 0), (0.22, 0.24, 11), K.grain("atbeam", "#5a3a20", "#2a1a0c", "Z", 0.6, 0.7), 0.02)
    # back wall with a real window opening (x -3.35..-1.65, y 1.0..3.2)
    bx("backL", (-4.3, 1.8, 3.65), (2.0, 3.6, 0.3), WP, 0); bx("backR", (1.8, 1.8, 3.65), (6.9, 3.6, 0.3), WP, 0)
    bx("backB", (-2.5, 0.5, 3.65), (1.7, 1.0, 0.3), WP, 0); bx("backT", (-2.5, 3.4, 3.65), (1.7, 0.4, 0.3), WP, 0)
    bx("left", (5.15, 1.8, 0), (0.3, 3.6, 11), WP, 0); bx("right", (-5.15, 1.8, 0), (0.3, 3.6, 11), WP, 0)
    bx("dado", (0, 0.45, 3.47), (10.4, 0.9, 0.04), WDV, 0.005); bx("dadorail", (0, 0.91, 3.45), (10.4, 0.05, 0.06), WD, 0.005)
    bx("skirt", (0, 0.07, 3.45), (10.4, 0.14, 0.06), WD, 0.005)
    # water stains and a torn patch on the wallpaper
    STAIN = K.img_mat("stain", np.dstack([np.full((64, 64), 0.25)] * 3 + [np.clip(1 - 2.2 * np.hypot(*np.mgrid[-1:1:64j, -1:1:64j]), 0, 1) * 0.45]).astype(np.float32), 0.9)
    try: STAIN.blend_method = "BLEND"
    except Exception: pass
    t, n, l = lib.nodes(STAIN); tex = [x for x in n if x.bl_idname == "ShaderNodeTexImage"][0]
    l.new(tex.outputs["Alpha"], n["Principled BSDF"].inputs["Alpha"])
    for k, (x, y, s) in enumerate(((2.6, 3.2, 1.0), (4.2, 2.6, 0.7), (-4.4, 3.0, 0.9))): K.panel(f"stain{k}", (x, y, 3.495), 1.2 * s, 0.9 * s, STAIN, 0)
    bx("torn", (3.6, 1.35, 3.497), (0.35, 0.28, 0.004), lib.plaster("atplas", "#c8b898"), 0.0)
    # window: frame, muntins, sill with a flower pot, the rooftops of Vienna outside
    for sx in (-1, 1): bx(f"wj{sx}", (-2.5 + sx * 0.82, 2.1, 3.5), (0.08, 2.2, 0.22), WD, 0.005)
    bx("wt", (-2.5, 3.18, 3.5), (1.72, 0.08, 0.22), WD, 0.005); bx("wsill", (-2.5, 0.98, 3.38), (1.95, 0.06, 0.32), WD, 0.01)
    for y in (1.75, 2.45): bx(f"wb{y}", (-2.5, y, 3.52), (1.64, 0.04, 0.05), WD, 0.003)
    bx("wv", (-2.5, 2.1, 3.52), (0.05, 2.2, 0.05), WD, 0.003)
    cy("wpot", (-2.95, 1.09, 3.4), 0.08, 0.16, K.flat("terra", "#b85a32", 0.8), 16)
    for k in range(6): bl(f"wleaf{k}", (-2.95 + rs.uniform(-0.08, 0.08), 1.25 + rs.uniform(0, 0.15), 3.4 + rs.uniform(-0.05, 0.05)), (0.06, 0.03, 0.04), K.flat("leaf", "#4a7a32", 0.6), 0.01)
    out = K.panel("vienna", (-2.0, 2.0, 7.5), 10, 5, K.img_mat("vienna", K.rooftops_img(1908), 0.9, emit=0.9), 0); K.hide_from_light(out)
    K.area((-2.5, 2.1, 4.3), (-1.5, 1.0, 0.5), 420, (0.72, 0.82, 1.0), 1.6, 2.2)
    SUN_D = (0.35, -0.6, -1.0)
    K.sun(SUN_D, 12.0, (1.0, 0.78, 0.5), 1.0)
    K.beam("atshaft", [(-3.3, 3.15, 3.55), (-1.7, 3.15, 3.55), (-1.7, 1.0, 3.55), (-3.3, 1.0, 3.55)], SUN_D, 5.5, (1.0, 0.85, 0.6), 0.25)
    # drop cloth and paint splatters
    bx("drop", (0.3, 0.004, 0.8), (2.6, 0.008, 2.0), lib.cloth("dropcloth", "#d8ccb0"), 0)
    SPL = [K.flat(f"spl{k}", c, 0.3) for k, c in enumerate(["#c8323a", "#2a4a8a", "#e8c84a", "#3a7a3a", "#f2f2f2", "#8a5a2a"])]
    for k in range(40): cy(f"spl{k}", (rs.uniform(-1, 1.6), 0.01, rs.uniform(-0.2, 1.8)), rs.uniform(0.015, 0.06), 0.002, SPL[k % 6], 12)
    # the easel (three legs, ledge, top clamp)
    for dx, dz, ry in ((-0.35, -0.1, 0.18), (0.35, -0.1, -0.18), (0.0, 0.35, 0.0)):
        o = bx(f"eleg{dx}{dz}", (0.4 + dx * 0.6, 0.9, 0.8 + dz * 0.6), (0.05, 1.85, 0.05), WD, 0.005)
        o.rotation_euler = (math.radians(-12 if dz > 0 else 6), ry, 0)
    bx("eledge", (0.4, 0.85, 0.74), (1.0, 0.05, 0.12), WD, 0.005); bx("eclamp", (0.4, 1.62, 0.76), (0.2, 0.06, 0.08), WD, 0.005)
    # paint table: jars of brushes, tubes, palette, rags, an oil lamp, a bowl with a dry crust
    bx("ptab", (1.8, 0.74, 1.0), (0.95, 0.05, 0.62), WD, 0.01)
    for dx in (-0.4, 0.4):
        for dz in (-0.25, 0.25): bx(f"ptl{dx}{dz}", (1.8 + dx, 0.36, 1.0 + dz), (0.05, 0.72, 0.05), WD, 0)
    for k in range(5): cy(f"jar{k}", (1.45 + (k % 3) * 0.14, 0.82, 0.82 + (k // 3) * 0.16), 0.045, 0.12, K.flat(f"pj{k}", ["#c8323a", "#2a4a8a", "#e8c84a", "#3a7a3a", "#f2f2f2"][k], 0.3), 14)
    cy("bjar", (2.05, 0.84, 1.18), 0.05, 0.16, M["glass"], 14)
    for k in range(6): cy(f"brush{k}", (2.05 + rs.uniform(-0.02, 0.02), 1.0, 1.18 + rs.uniform(-0.02, 0.02)), 0.006, 0.32, WD, 6, (rs.uniform(-0.25, 0.25), rs.uniform(-0.25, 0.25), 0))
    for k in range(6): cy(f"tube{k}", (1.5 + k * 0.06, 0.775, 1.24), 0.012, 0.09, K.flat("tube", "#c8c8c0", 0.3, ), 8, (math.radians(90), 0, rs.uniform(-0.5, 0.5)))
    bx("palette", (2.0, 0.775, 0.85), (0.34, 0.01, 0.25), K.grain("palw", "#c09060", "#8a6038", "X", 1.5, 0.5), 0.004, 0.4)
    for k in range(6): sph(f"blob{k}", (1.9 + rs.uniform(0, 0.18), 0.785, 0.8 + rs.uniform(0, 0.1)), 0.018, SPL[k], 8)
    bl("rag", (2.15, 0.79, 0.95), (0.12, 0.03, 0.09), lib.cloth("rag", "#b8a888"), 0.03)
    cy("bowl", (1.6, 0.8, 1.2), 0.07, 0.05, WHITE, 16); bl("crust", (1.6, 0.83, 1.2), (0.05, 0.02, 0.03), M["bread2"], 0.01)
    cy("lampb", (1.45, 0.79, 1.18), 0.07, 0.04, BR, 16); sph("lampf", (1.45, 0.86, 1.18), 0.06, M["glass"])
    cy("lampc", (1.45, 1.0, 1.18), 0.03, 0.18, M["glass"], 12); cy("lampfl", (1.45, 0.96, 1.18), 0.01, 0.04, lib.emit("atflame", (1.0, 0.6, 0.2), 30), 8)
    K.point((1.45, 1.02, 1.18), 45, (1.0, 0.62, 0.3), 0.04)
    # rejected paintings: leaning stacks along the back wall and on the floor, some stamped ABGELEHNT
    kinds = ["house", "church", "dome", "bridge"]
    pics = [K.img_mat(f"rej{k}", stamp_rejected(naive_building(60 + k, kinds[k % 4])) if k % 2 == 0 else naive_building(60 + k, kinds[k % 4]), 0.6) for k in range(8)]
    BACKC = K.flat("canvback", "#d8ccb0", 0.9)
    for k in range(6):
        x = 1.2 + k * 0.62; w, h = rs.choice(((0.6, 0.45), (0.7, 0.52), (0.5, 0.4)))
        p = K.panel(f"lean{k}", (x, h / 2 * math.cos(0.2) + 0.01, 3.3 - h / 2 * math.sin(0.2) - k % 2 * 0.12), w, h, pics[k % 8], 0, -0.2)
        bx(f"leanf{k}", (x, h / 2 * math.cos(0.2) + 0.01, 3.32 - h / 2 * math.sin(0.2) - k % 2 * 0.12), (w + 0.04, h + 0.04, 0.03), BACKC, 0.004).rotation_euler[0] = -0.2
    for k in range(3):
        o = K.panel(f"lean2{k}", (-1.2 + k * 0.08, 0.3, 3.2 - k * 0.12), 0.55, 0.42, pics[(k + 3) % 8], 0, -0.25)
    for k in range(3):
        K.floor_quad(f"floorpic{k}", (-1.6 + k * 0.45, -0.4 - k * 0.2), 0.5, 0.38, pics[(k + 5) % 8], rs.uniform(-0.5, 0.5), 0.012 + k * 0.004)
    # framed postcards pinned in a grid, the Academy's rejection letter, a calendar
    for k in range(6):
        K.framed(f"card{k}", (0.9 + (k % 3) * 0.55, 2.55 - (k // 3) * 0.45, 3.48), 0.42, 0.3, pics[(k + 1) % 8], WD, 0, 0.03, 0.02)
    let = K.doc_img(1907, "AKADEMIE WIEN", 256, 340, "#f6eedc")
    K.stamp(let, "ABGELEHNT", 0.5, 0.62, 0.06, "#c81e28", 0.95, 0.15, "center")
    K.panel("letter", (-0.35, 2.35, 3.485), 0.36, 0.48, K.img_mat("letter", let, 0.8), 0).rotation_euler[1] = 0.06
    sph("pin", (-0.35, 2.57, 3.47), 0.012, M["red"], 8)
    # furniture: bookcase, plaster bust, little iron stove with glow, washstand, chair with a coat, suitcase
    BK = [K.flat(f"bk{k}", c, 0.6) for k, c in enumerate(["#7a2a2a", "#2a4a6a", "#3a5a2a", "#8a6a2a", "#5a3a5a"])]
    for row in range(4):
        bx(f"bsh{row}", (4.0, 0.3 + row * 0.5, 3.3), (1.4, 0.04, 0.3), WD, 0.005)
        K.books(f"bk{row}", 3.35, 0.32 + row * 0.5, 3.3, 14 - row * 2, BK, 0, 0.22, True, random.Random(row))
    for sx in (-1, 1): bx(f"bside{sx}", (4.0 + sx * 0.72, 1.0, 3.3), (0.04, 2.0, 0.32), WD, 0.005)
    K.bl("bust", (4.0, 2.25, 3.3), (0.13, 0.18, 0.13), lib.plaster("bust", "#f2ece0"), 0.02); K.bl("bustb", (4.0, 2.07, 3.3), (0.18, 0.08, 0.12), lib.plaster("bust", "#f2ece0"), 0.02)
    cy("stove", (2.9, 0.45, 2.9), 0.25, 0.8, IRON, 20); cy("stovet", (2.9, 0.88, 2.9), 0.28, 0.05, IRON, 20)
    cy("pipe", (2.9, 2.2, 3.0), 0.06, 2.6, IRON, 12)
    bx("grate", (2.9, 0.3, 2.64), (0.2, 0.12, 0.02), lib.emit("grateg", (1.0, 0.4, 0.1), 8), 0)
    K.point((2.9, 0.3, 2.45), 25, (1.0, 0.45, 0.15), 0.1)
    cy("kettle", (2.9, 0.98, 2.9), 0.09, 0.14, K.metal("kettle", "#6a6a6a", 0.4), 16)
    bx("wash", (-4.0, 0.45, 2.9), (0.6, 0.9, 0.45), WD, 0.01); cy("basin", (-4.0, 0.93, 2.9), 0.2, 0.06, WHITE, 24); cy("pitcher", (-3.85, 1.05, 3.0), 0.07, 0.22, WHITE, 16)
    bx("mirror", (-4.0, 1.6, 3.48), (0.4, 0.5, 0.02), K.metal("atmir", "#b8b8b0", 0.15), 0.004)
    bx("stool", (-0.6, 0.45, 0.3), (0.42, 0.05, 0.42), WD, 0.02, 0.6)
    for dx in (-0.15, 0.15):
        for dz in (-0.15, 0.15): bx(f"stl{dx}{dz}", (-0.6 + dx, 0.22, 0.3 + dz), (0.04, 0.44, 0.04), WD, 0)
    K.chair("chair", 3.2, 1.6, 2.6, WD, WD, 0.45, True)
    K.bl("coat", (3.25, 0.9, 1.75), (0.25, 0.35, 0.12), lib.cloth("atcoat", "#2e2a28"), 0.05)
    bx("suitc", (-1.6, 0.18, 2.9), (0.7, 0.36, 0.22), K.flat("suit", "#6a4024", 0.5), 0.03, 0.15); bx("suith", (-1.6, 0.38, 2.9), (0.14, 0.04, 0.04), DARK, 0.01, 0.15)
    for k, (x, z) in enumerate(((-0.9, -0.3), (1.2, -0.2), (0.9, 2.2), (-1.3, 1.5), (2.3, 0.3))): K.bl(f"crump{k}", (x, 0.06, z), (0.06, 0.055, 0.06), M["paper"], 0.04)
    cy("bottle", (2.2, 0.85, 1.2), 0.035, 0.26, K.flat("btl", "#2a4a2a", 0.15), 12); cy("candle", (-3.7, 1.05, 2.75), 0.02, 0.12, WHITE, 8)
    # fills: warm low fill from the camera side, cool bounce from the window side
    K.area((0, 2.6, -4.6), (0, 1.2, 1.5), 120, (1.0, 0.85, 0.7), 5)
    K.area((-4.5, 2.8, 0.5), (0, 1.0, 1.0), 120, (0.75, 0.85, 1.0), 2)
    return {}
