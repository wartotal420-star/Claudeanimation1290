# Chapter 5 (and 6): Hitler's great hall at the Berghof above Berchtesgaden: the huge picture window onto the Alps
# (Untersberg), a long marble map table in front of it with the Europe & Mediterranean 1941 map (maps/c05_med1941.png),
# a red marble fireplace, tapestries, a giant globe, a desk with a telephone, sofas on a big rug. No insignia.
# Layout (three coords): hall x -8..8, z -6..9.2, ceiling y 5.6 (coffered). The window: x -4.6..4.6, y 0.8..4.6 in the
# wall z 9.2. Map table: x -1.65..1.65, z 5.5..7.7, top y 0.92; map x -1.5..1.5, z 5.6..7.6 (north at +z, readable from
# the -z side): lon -> x = 1.5 - (lon + 14) / 20, lat -> z = 5.6 + (lat - 26) / 20. Keep clear: Hitler at (0, 0, 4.9)
# (map side) or near the window (0.8, 0, 8.3); desk at (4.6, 0, 3.0), phone on it; fireplace on the wall x -7.9, z 1.5.
# Animated map tokens (update): Italian blocks into Greece and back (frames 1830-1905), German tanks into Yugoslavia /
# Greece and across to Libya (frames 1985-2080), all chapter-5 frame numbers; other shots leave them parked.
import bpy, math, random, os
from mathutils import Vector
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, R90
from .c05_kit import (img_mat, wall_quad, quad, point, area, spot, sun_light, sky, height_mesh, ground_mat, lathe, tube, worn, mat_once,
                      fire, smoke_mat, empty, cached)
from . import ikit as I
MAPS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps")
def MP(lon, lat, y=0.93): return (1.5 - (lon + 14) / 20, y, 5.6 + (lat - 26) / 20)

def marble_red():
    def mk():
        m = lib.principled("bgmarble", hexc("#7a2420"), 0.18); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.5; nz.inputs["Detail"].default_value = 10; nz.inputs["Distortion"].default_value = 3
        l.new(tc.outputs["Object"], nz.inputs["Vector"])
        r = lib.ramp(n, l, nz.outputs["Fac"], [(0.42, hexc("#5a1614")), (0.5, hexc("#c87a6a")), (0.56, hexc("#7a2420")), (0.7, hexc("#8a3028"))])
        l.new(r.outputs["Color"], b.inputs["Base Color"]); return m
    return cached("bgmarble", mk)

def alps(x, z):
    from mathutils import noise
    d = max(0.0, min(1.0, (z - 1300) / 1400)); d = d * d * (3 - 2 * d)
    ridge = 1 - abs(noise.noise(Vector((x * 0.0009, z * 0.0009, 0.5))))
    h = -320 + d * (430 * ridge ** 2.2 + 150 * noise.noise(Vector((x * 0.003, z * 0.003, 2.0))) + 180)
    h += 420 * math.exp(-((x + 300) / 900) ** 2 - ((z - 2700) / 500) ** 2)        # the Untersberg massif
    return h

TOKENS = {}
def build(M, D):
    random.seed(1941); K_.reset(); K = Kit("bg"); rnd = random.Random(9)
    # ---------------- outside: sky, Alps, forested slopes ----------------
    sky((0.18, 0.36, 0.72), (0.45, 0.62, 0.85), (0.82, 0.86, 0.9), sun_dir=(-0.35, 0.45, -0.8), sun_col=(1.0, 0.85, 0.6), glow=0.5, clouds=0.7, strength=1.0)
    rock = ground_mat("bgalps", [(0.3, "#4e5640"), (0.45, "#6a6a62"), (0.6, "#8a8a84"), (0.75, "#a8a8a4")], 0.006, 0.3)
    snowm = lib.principled("bgsnowpk", hexc("#f0f4fa"), 0.5)
    m = height_mesh("alps", -4500, 4500, 500, 5200, 60, alps, rock)
    # snow above 450 m: second material by face height
    m.data.materials.append(snowm)
    for p in m.data.polygons:
        if p.center.z > 40 + 60 * math.sin(p.center.x * 0.01) and p.normal.z > 0.3: p.material_index = 1
    forest = ground_mat("bgforest", [(0.3, "#1e3a1e"), (0.6, "#2e4a26"), (0.8, "#4a6a30")], 0.02, 0.5)
    height_mesh("hill", -1500, 1500, 20, 1400, 25, lambda x, z: -12 - 0.25 * (z - 20) - 30 * math.cos(x * 0.004) + 12 * math.sin(x * 0.02 + z * 0.013), forest)
    # dark fir trees on the falling slope below the window
    trees = Kit("bgtrees"); fir = pm("#1a3020", 0.9); trunk = pm("#3a2a1e", 0.9)
    for k in range(260):
        x, z = rnd.uniform(-700, 700), rnd.uniform(40, 700); y = -12 - 0.25 * (z - 20) - 30 * math.cos(x * 0.004) + 12 * math.sin(x * 0.02 + z * 0.013)
        h = rnd.uniform(14, 26); trees.cyl((x, y + h * 0.15, z), 0.5, h * 0.3, trunk, 6)
        for j in range(3): trees.cyl((x, y + h * (0.35 + j * 0.22), z), h * (0.24 - j * 0.06), h * 0.34, fir, 8, "y", 0.2)
    trees.build()
    # ---------------- the hall ----------------
    FL = I.planks("bgfloor", "#7a5030", "#4a2c18", "Y", 0.2, 2.0, 0.35, 0.3)
    WAL = grime("bgwall", "#e8dcc4", 0.15); PAN = wood("#6a4224", "#3a2010", 5, 0.4); CEI = wood("#5a3a20", "#2e1a0c", 4, 0.5)
    K.box((0, -0.05, 1.6), (16.4, 0.1, 15.4), FL, 0, 0)
    K.box((0, 5.65, 1.6), (16.4, 0.1, 15.4), CEI, 0, 0)
    for k in range(9): K.box((-8 + k * 2, 5.4, 1.6), (0.22, 0.4, 15.2), CEI, 0, 0.02)          # coffers
    for k in range(8): K.box((0, 5.4, -6 + k * 2.1), (16.2, 0.4, 0.22), CEI, 0, 0.02)
    # back wall with the window opening
    K.box((-6.3, 2.8, 9.35), (3.4, 5.6, 0.3), WAL, 0, 0); K.box((6.3, 2.8, 9.35), (3.4, 5.6, 0.3), WAL, 0, 0)
    K.box((0, 0.4, 9.35), (9.2, 0.8, 0.3), WAL, 0, 0); K.box((0, 5.1, 9.35), (9.2, 1.0, 0.3), WAL, 0, 0)
    for k in range(7): K.box((-4.6 + k * 9.2 / 6, 2.7, 9.3), (0.09, 3.8, 0.14), PAN, 0, 0.01)           # mullions
    for k in range(4): K.box((0, 0.8 + k * 3.8 / 3, 9.3), (9.2, 0.09, 0.14), PAN, 0, 0.01)
    K.box((0, 0.78, 9.0), (9.6, 0.08, 0.5), marble_red(), 0, 0.01)                                      # window sill
    for sx in (-1, 1):                                                                                   # heavy drapes
        I.drape(f"bgdr{sx}", (sx * 5.3, 4.9, 9.05), 1.4, 4.8, I.velvet(f"bgvel{sx}", "#6a1e1a"), 0, 7, 0.09, 0.0)
    for sx in (-1, 1):
        K.box((sx * 8.15, 2.8, 1.6), (0.3, 5.6, 15.4), WAL, 0, 0)
        K.box((sx * 7.98, 1.0, 1.6), (0.06, 2.0, 15.0), PAN, 0, 0.005)
        K.box((sx * 7.94, 2.03, 1.6), (0.12, 0.08, 15.0), PAN, 0, 0.01)
    K.box((0, 2.8, -6.15), (16.4, 5.6, 0.3), WAL, 0, 0); K.box((0, 1.0, -5.98), (16, 2.0, 0.06), PAN, 0, 0.005)
    # tapestries (painted landscapes / hunting scenes) on the side walls and the back
    for k, (c, yaw, w, h) in enumerate((((7.92, 3.6, -1.5), R90, 3.2, 2.4), ((7.92, 3.6, 4.6), R90, 3.2, 2.4), ((-7.92, 3.7, -2.6), -R90, 3.0, 2.2), ((0, 3.6, -5.9), math.pi, 4.4, 2.6))):
        img = I.fresco_img(seed=k + 3) if k % 2 else I.landscape_img(seed=k + 7)
        I.framed(f"bgtap{k}", c, w, h, I.img_mat(f"bgtapm{k}", img, 0.85, sheen=0.3), wood("#8a6a30", "#4a3010", 8, 0.3), yaw, 0.1, 0.06)
    # ---------------- fireplace (red marble) with a real fire ----------------
    MR = marble_red()
    K.box((-7.75, 1.0, 1.5), (0.5, 2.0, 2.8), MR, 0, 0.02)
    K.box((-7.5, 2.08, 1.5), (1.0, 0.16, 3.1), MR, 0, 0.02)
    K.box((-7.6, 0.6, 1.5), (0.4, 1.1, 1.5), pm("#120c0a", 0.9), 0, 0.01)
    for sd in (-1, 1): K.box((-7.42, 1.0, 1.5 + sd * 1.05), (0.4, 2.0, 0.5), MR, 0, 0.02)
    for k in range(3): K.cyl((-7.55, 0.12 + k * 0.06, 1.35 + k * 0.12), 0.07, 0.8, wood("#5a3a1e", "#2a1608", 10, 0.8), 10, "z", None, 0.3 * k)
    fire("bgfire", (-7.5, 0.12, 1.5), 0.45, seed=4, energy=420)
    for k in range(4): K.cyl((-7.35, 2.2, 0.6 + k * 0.6), 0.06, 0.18, brass(), 12)                      # mantel candlesticks / vases
    # ---------------- the map table ----------------
    WD = wood("#4a2814", "#22120a", 5, 0.35)
    K.box((0, 0.88, 6.6), (3.3, 0.08, 2.2), MR, 0, 0.02)
    for sx in (-1, 1):
        for sz in (-1, 1): lathe(f"bgleg{sx}{sz}", [(0.0, 0.0), (0.12, 0.0), (0.08, 0.1), (0.06, 0.4), (0.1, 0.55), (0.07, 0.7), (0.09, 0.84), (0.0, 0.84)], (sx * 1.45, 0, 6.6 + sz * 0.9), WD, 20)
    quad("bgmap", [(1.5, 0.925, 5.6), (-1.5, 0.925, 5.6), (-1.5, 0.925, 7.6), (1.5, 0.925, 7.6)], img_mat("c05med", os.path.join(MAPS, "c05_med1941.png"), 0.5))
    # clutter round the map: magnifier, dividers, pencils, folders, a loupe, a coffee cup, a pair of spectacles
    for k in range(4): K.box((1.2 + k * 0.03, 0.935 + k * 0.004, 5.75 + k * 0.01), (0.26, 0.006, 0.34), paper("#efe4c8"), 0.2 * k, 0.0)
    K.cyl((-1.25, 0.95, 5.75), 0.045, 0.06, pm("#f2ece0", 0.2), 16); K.cyl((-1.25, 0.94, 5.75), 0.075, 0.01, pm("#f2ece0", 0.2), 18)
    for k in range(5): K.cyl((-1.0 + k * 0.03, 0.935, 7.45), 0.006, 0.18, pm(("#c8302a", "#2a4a8a", "#1a1a1a", "#3a7a3a", "#d8a030")[k], 0.5), 6, "z", None, 0.2 * k)
    # parked tokens (moved in update)
    IT = pm("#4a8a3a", 0.5); GE = pm("#5a5e62", 0.45, 0.3); GR = pm("#3a6ac8", 0.5)
    def token(name, col, kind="block"):
        k2 = Kit(name)
        if kind == "block":
            k2.box((0, 0.025, 0), (0.07, 0.05, 0.045), col, 0, 0.006); k2.box((0, 0.051, 0), (0.04, 0.003, 0.025), pm("#f2ece0", 0.6), 0, 0.0)
        else:
            k2.box((0, 0.02, 0), (0.1, 0.022, 0.06), col, 0, 0.005)
            for sd in (-1, 1): k2.box((0, 0.012, sd * 0.034), (0.11, 0.024, 0.02), pm("#2a2622", 0.6), 0, 0.006)
            k2.cyl((-0.01, 0.04, 0), 0.024, 0.018, col, 14); k2.cyl((0.04, 0.043, 0), 0.004, 0.07, col, 8, "x")
        obs = k2.build(); e = empty(name, 0.1)
        for o in obs: o.parent = e
        return e
    TOKENS.clear()
    for k in range(4): TOKENS[f"it{k}"] = token(f"it{k}", IT)
    for k in range(2): TOKENS[f"gr{k}"] = token(f"gr{k}", GR)
    for k in range(5): TOKENS[f"ge{k}"] = token(f"ge{k}", GE, "tank")
    # ---------------- the globe, the desk, sofas, rug, clock, flowers ----------------
    lathe("globestand", [(0.0, 0.0), (0.42, 0.0), (0.4, 0.06), (0.12, 0.12), (0.08, 0.6), (0.14, 0.75), (0.0, 0.78)], (-5.2, 0, 6.6), WD, 24)
    K.torus((-5.2, 1.45, 6.6), 0.72, 0.035, brass(), 40, 8, "z", 0.4)
    gl = I.sph("globe", (-5.2, 1.45, 6.6), 0.68, img_mat("bgglobe", os.path.join(MAPS, "map_world.png"), 0.4), 40)
    gl.rotation_euler = (0.4, 0, 2.2)
    me = gl.data
    if not me.uv_layers: bpy.ops.object.select_all(action="DESELECT")
    uv = me.uv_layers.active
    if uv is None: uv = me.uv_layers.new()
    for p in me.polygons:
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            u = 0.5 + math.atan2(co.y, co.x) / math.tau; v = 0.5 + math.asin(max(-1, min(1, co.z / 0.68))) / math.pi
            uv.data[li].uv = (u, v)
    # desk with lamp, phone, blotter, papers
    K.box((4.6, 0.76, 3.0), (2.2, 0.08, 1.1), WD, 0, 0.02)
    for sx in (-1, 1): K.box((4.6 + sx * 0.85, 0.37, 3.0), (0.45, 0.74, 1.0), WD, 0, 0.02)
    K.box((4.6, 0.805, 3.0), (0.9, 0.01, 0.6), pm("#2a4a32", 0.8), 0, 0.0)
    K.box((4.1, 0.85, 2.85), (0.22, 0.08, 0.26), pm("#141214", 0.15), 0, 0.03); K.box((4.1, 0.93, 2.82), (0.26, 0.05, 0.06), pm("#141214", 0.15), 0, 0.02)
    lathe("bglamp", [(0.0, 0.0), (0.1, 0.0), (0.03, 0.04), (0.02, 0.4), (0.0, 0.42)], (5.3, 0.8, 3.2), brass(), 16)
    lathe("bglampsh", [(0.09, 0.32), (0.2, 0.16), (0.21, 0.15), (0.1, 0.31)], (5.3, 0.8, 3.2), lib.principled("bglsh", hexc("#f0d8a8"), 0.8, 0.0, (1.0, 0.75, 0.45), 2.0), 24, cap=False)
    point((5.3, 1.1, 3.2), 25, (1.0, 0.72, 0.42), 0.05)
    for k in range(5): K.box((4.9 + k * 0.02, 0.81 + k * 0.004, 2.9), (0.24, 0.006, 0.32), paper("#efe4c8"), 0.15 * k - 0.2, 0.0)
    rug = lib.carpet("bgrug", "#7a2a1e", "#d8b060")
    K.box((-3.6, 0.005, 1.6), (5.2, 0.012, 4.0), rug, 0, 0.002)
    VEL = I.velvet("bgsofa", "#5a6a3a")
    for k, (x, z, yw) in enumerate(((-3.6, -0.2, 0.0), (-5.6, 1.6, R90), (-1.6, 1.6, -R90))):
        cw, sw = math.cos(yw), math.sin(yw)
        P = lambda lx, ly, lz: (x + lx * cw + lz * sw, ly, z - lx * sw + lz * cw)
        K.box(P(0, 0.25, 0), (1.9, 0.4, 0.85), VEL, yw, 0.08); K.box(P(0, 0.65, -0.35), (1.9, 0.6, 0.2), VEL, yw, 0.08)
        for sd in (-1, 1): K.box(P(sd * 0.95, 0.42, 0), (0.18, 0.5, 0.85), VEL, yw, 0.06)
    K.box((-3.6, 0.42, 1.6), (1.4, 0.06, 0.8), MR, 0, 0.02); K.box((-3.6, 0.2, 1.6), (1.2, 0.4, 0.6), WD, 0, 0.02)
    K.cyl((-3.6, 0.55, 1.6), 0.12, 0.2, pm("#2a4a8a", 0.2), 16);
    for k in range(9): K.sphere((-3.6 + 0.1 * math.cos(k), 0.72 + 0.04 * (k % 3), 1.6 + 0.1 * math.sin(k)), 0.06, pm(("#d84a3a", "#f0d050", "#f2ece0")[k % 3], 0.6), 8)
    lathe("bgclock", [(0.0, 0.0), (0.36, 0.0), (0.3, 0.1), (0.28, 1.9), (0.34, 2.0), (0.3, 2.4), (0.0, 2.5)], (7.5, 0, -4.8), WD, 4, yaw=math.pi / 4, sx=1.0, sz=0.6)
    K.cyl((7.32, 2.05, -4.8), 0.18, 0.02, pm("#efe4c8", 0.5), 24, "x")
    for sx in (-1, 1):  # big vases of flowers flanking the window
        lathe(f"bgvase{sx}", [(0.0, 0.0), (0.18, 0.0), (0.28, 0.3), (0.2, 0.7), (0.24, 0.8), (0.0, 0.8)], (sx * 5.0, 0, 8.5), pm("#2a4a7a", 0.2), 24)
        for k in range(12):
            a = k / 12 * math.tau; K.sphere((sx * 5.0 + 0.25 * math.cos(a) * rnd.random(), 0.95 + rnd.random() * 0.4, 8.5 + 0.25 * math.sin(a) * rnd.random()), 0.08, pm(("#e8c040", "#d84a3a", "#f2ece0", "#c86ab8")[k % 4], 0.6), 8)
    for k, (x, z) in enumerate(((2.6, 5.4), (-2.6, 5.4), (2.6, 7.8), (-2.6, 7.8))):     # armchairs round the map table
        K.box((x, 0.45, z), (0.6, 0.12, 0.6), VEL, 0, 0.04); K.box((x + (0.28 if x > 0 else -0.28), 0.8, z), (0.1, 0.7, 0.6), WD, 0, 0.02)
        for dx in (-0.25, 0.25):
            for dz in (-0.25, 0.25): K.cyl((x + dx, 0.2, z + dz), 0.03, 0.4, WD, 8)
    K.box((0, 0.004, 6.6), (5.0, 0.012, 3.6), lib.carpet("bgrug2", "#2a3a5a", "#c8a24a"), 0, 0.002)
    from .void import bookcase
    for k, z in enumerate((-4.6, -2.2)): bookcase(f"bgbc{k}", (7.7, 0, z), 2.2, 2.6, 0.45, 5, WD, yaw=R90, seed=k + 4)
    for x, z in ((-2.9, 8.4), (2.9, 8.4), (-6.8, -4.6), (6.6, 6.8)):                       # floor lamps with silk shades
        lathe(f"bgfl{x}{z}", [(0.0, 0.0), (0.22, 0.0), (0.05, 0.05), (0.03, 1.6), (0.0, 1.62)], (x, 0, z), brass(), 16)
        lathe(f"bgfls{x}{z}", [(0.16, 1.85), (0.3, 1.55), (0.31, 1.54), (0.17, 1.84)], (x, 0, z), lib.principled("bgfsh", hexc("#f0d8a8"), 0.8, 0.0, (1.0, 0.75, 0.45), 2.5), 24, cap=False)
        point((x, 1.65, z), 45, (1.0, 0.7, 0.4), 0.08)
    K.box((-4.6, 0.45, -5.6), (3.0, 0.9, 0.55), WD, 0, 0.03)                                # sideboard with busts and vases
    for k in range(5): K.box((-5.8 + k * 0.6, 0.45, -5.32), (0.5, 0.7, 0.02), wood("#5a3018", "#2a1408", 9, 0.3), 0, 0.01)
    lathe("bgbust", [(0.0, 0.0), (0.16, 0.0), (0.1, 0.1), (0.2, 0.3), (0.14, 0.45), (0.08, 0.5), (0.13, 0.62), (0.12, 0.75), (0.0, 0.8)], (-4.0, 0.9, -5.6), pm("#d8d0c0", 0.4), 20)
    for k, x in enumerate((-5.6, -5.0, -3.3)): lathe(f"bgv{k}", [(0.0, 0.0), (0.08, 0.0), (0.13, 0.15), (0.07, 0.35), (0.1, 0.4), (0.0, 0.4)], (x, 0.9, -5.6), pm(("#2a4a7a", "#c8a24a", "#7a2a1e")[k], 0.2, 0.3 if k == 1 else 0), 20)
    for k, (x, z) in enumerate(((-7.3, 7.6), (7.2, 8.1), (-1.0, -5.5))):                      # potted palms
        lathe(f"bgpot{k}", [(0.0, 0.0), (0.25, 0.0), (0.32, 0.5), (0.0, 0.5)], (x, 0, z), pm("#8a4a2a", 0.6), 20)
        for j in range(9):
            a = j / 9 * math.tau; tube(f"bgfr{k}{j}", [(x, 0.5, z), (x + 0.4 * math.cos(a), 1.5 + 0.2 * (j % 2), z + 0.4 * math.sin(a)), (x + 0.9 * math.cos(a), 1.2, z + 0.9 * math.sin(a))], 0.04, pm("#2a5a2a", 0.6), taper=lambda f: 1.2 - f)
    K.build()
    # ---------------- light: daylight through the window (cool), sun patches, the fire and lamps warm ----------------
    sun_light((0.35, -0.45, 0.8), 4.5, (1.0, 0.9, 0.75), 1.5)
    area((0, 2.7, 9.6), (0, 1.2, 5), 2600, (0.75, 0.85, 1.0), 9.0, 3.8)
    area((0, 4.5, -4.0), (0, 1.0, 6.0), 700, (1.0, 0.72, 0.45), 6.0)
    area((5.5, 3.5, 1.0), (0, 1.2, 5.0), 300, (1.0, 0.75, 0.5), 2.0)
    point((-6.8, 1.0, 1.5), 300, (1.0, 0.5, 0.2), 0.3)
    park = {"it0": MP(16.5, 41.0), "it1": MP(17.6, 41.6), "it2": MP(12.6, 43.8), "it3": MP(11.0, 44.5), "gr0": MP(22.0, 39.5), "gr1": MP(23.5, 38.3),
            "ge0": MP(14.0, 48.0), "ge1": MP(16.5, 47.6), "ge2": MP(12.0, 50.5), "ge3": MP(10.5, 46.5), "ge4": MP(12.6, 41.0)}
    def lerp(a, b, u): u = max(0.0, min(1.0, u)); u = u * u * (3 - 2 * u); return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))
    def update(f):
        P = dict(park)
        # Italians cross from Albania into Greece (1830-1858) and are pushed back (1872-1900)
        go = [(MP(19.8, 41.4), MP(21.4, 39.6)), (MP(20.2, 40.8), MP(22.3, 39.1)), (MP(19.6, 40.2), MP(21.0, 38.9)), (MP(20.6, 41.9), MP(22.0, 40.2))]
        for k, (a, b) in enumerate(go):
            P[f"it{k}"] = lerp(a, b, (f - 1830 - k * 3) / 26) if f < 1872 else lerp(b, (a[0] + 0.08, a[1], a[2] + 0.06), (f - 1872 - k * 2) / 22)
        P["gr0"] = lerp(MP(22.6, 38.3), MP(21.5, 40.0), (f - 1872) / 22); P["gr1"] = lerp(MP(23.8, 38.6), MP(22.2, 39.4), (f - 1876) / 22)
        # Germans into Yugoslavia and Greece, Rommel's tank across the sea to Libya
        P["ge0"] = lerp(MP(16.0, 47.2), MP(20.4, 44.5), (f - 1995) / 30); P["ge1"] = lerp(MP(18.5, 47.0), MP(22.5, 42.6), (f - 2000) / 32)
        P["ge2"] = lerp(MP(22.8, 43.0), MP(22.8, 38.6), (f - 2025) / 28) if f > 2020 else P["ge2"]
        P["ge4"] = lerp(MP(12.6, 41.0), MP(13.2, 32.6), (f - 2060) / 28)
        gl.rotation_euler = (0.4, 0, 2.2 + (0.012 * (f - 3990) if f > 3990 else 0.0))   # chapter 6: the globe turns to the Pacific
        for k, e in TOKENS.items():
            x, y, z = P[k]; e.location = T(x, 0.93, z); e.rotation_euler = (0, 0, (0.4 if k.startswith("ge") else 0.1) + (hash(k) % 7) * 0.05)
    update(0)
    return {"update": update}
