# Cold open (shot 1): a dark study, a heavy table with the painted 1939 world map, a long line of black dominoes that
# topple in turn (path and timing exactly as sets.ts DOMINO_PATH / cast.ts DOMINO_T0, DOMINO_DT; table top at three
# y 0.02, map at y 0.021). The map (maps/map_void.png) is placed so Poland lies under the first domino (three (0.48, 1.49)).
# This file also holds the shared prop kit (lathe, tube, flame, smoke, worn paint, desk props) used by front / jungle / warroom.
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix, Quaternion
import lib
from lib import T, TS

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def bx(name, c, s, m, bev=0.01, yaw=0.0): return lib.box(name, T(*c), TS(*s), m, bev, rot=(0, 0, yaw))
def cy(name, c, r, h, m, verts=20, rot=(0, 0, 0), bev=0.005): return lib.cyl(name, T(*c), r, h, m, verts, rot, bev)

PATH = []
x, z, a = 0.4, 1.5, 0.0
for i in range(160):
    a += 0.18 * math.sin(i * 0.17) + (0.9 if i % 37 == 20 else 0)
    x += 0.075 * math.cos(a); z -= 0.075 * math.sin(a) * 0.7 + 0.012
    if abs(x) > 5.5: a = math.pi - a
    PATH.append((x, z))
T0, DT = 53 / 30, 0.045
C = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # three -> Blender

# =====================================================================================================================
# shared kit (three.js coordinates in, Blender objects out)
# =====================================================================================================================
_MC = {}
def mat_once(key, fn):
    m = _MC.get(key)
    if m is None or m.name not in bpy.data.materials: m = _MC[key] = fn()
    return m
def link(o):
    bpy.context.scene.collection.objects.link(o); return o
def mesh_obj(name, verts, faces, mat, smooth=False):
    """verts in three coords (already placed); faces = index tuples"""
    me = bpy.data.meshes.new(name); me.from_pydata([T(*v) for v in verts], [], faces); me.update()
    me.materials.append(mat)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return link(bpy.data.objects.new(name, me))
def lathe(name, prof, c, mat, seg=32, yaw=0.0, sx=1.0, sz=1.0, cap=True, tilt=None):
    """surface of revolution about three +y: prof = [(radius, height)], placed at c (three coords)"""
    vs, fs = [], []
    for j in range(seg):
        a = j / seg * math.tau
        for r, h in prof: vs.append((r * math.cos(a) * sx, h, r * math.sin(a) * sz))
    n = len(prof)
    for j in range(seg):
        for k in range(n - 1):
            a0, a1 = j * n + k, ((j + 1) % seg) * n + k
            fs.append((a0, a1, a1 + 1, a0 + 1))
    if cap and prof[0][0] > 1e-4:
        vs.append((0, prof[0][1], 0)); ci = len(vs) - 1
        for j in range(seg): fs.append((ci, ((j + 1) % seg) * n, j * n))
    if cap and prof[-1][0] > 1e-4:
        vs.append((0, prof[-1][1], 0)); ci = len(vs) - 1
        for j in range(seg): fs.append((ci, j * n + n - 1, ((j + 1) % seg) * n + n - 1))
    R = Matrix.Rotation(yaw, 3, "Y") @ (tilt if tilt is not None else Matrix.Identity(3))
    vs = [tuple(Vector(c) + R @ Vector(v)) for v in vs]
    return mesh_obj(name, vs, fs, mat, smooth=True)
def tube(name, pts, r, mat, res=12, bres=3, taper=None):
    """smooth tube through three-space points (wire, rope, vine, cable)"""
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = r; cu.bevel_resolution = bres; cu.resolution_u = res
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS"); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts): p.co = (*T(*q), 1)
    sp.use_endpoint_u = True; sp.order_u = min(4, len(pts))
    if taper:
        for k, p in enumerate(sp.points): p.radius = taper(k / max(1, len(pts) - 1))
    o = link(bpy.data.objects.new(name, cu)); cu.materials.append(mat); return o
def worn(name, col, chip="#3a3530", rough=0.55, metal=0.3, scale=18.0, amount=0.42, dirt="#4a3a28"):
    """painted metal with chipped spots (noise mask) and blotchy grime"""
    m = lib.principled(name, lib.hexc(col), rough, metal); t, n, l = lib.nodes(m)
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 8
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    nb = n.new("ShaderNodeTexNoise"); nb.inputs["Scale"].default_value = scale / 6; l.new(tc.outputs["Object"], nb.inputs["Vector"])
    r = lib.ramp(n, l, nz.outputs["Fac"], [(amount, (1, 1, 1)), (amount + 0.04, (0, 0, 0))])
    tint = n.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"
    l.new(nb.outputs["Fac"], tint.inputs[0]); tint.inputs[6].default_value = (*lib.hexc(col), 1); tint.inputs[7].default_value = (*lib.hexc(dirt), 1)
    ch = n.new("ShaderNodeMix"); ch.data_type = "RGBA"; l.new(r.outputs["Color"], ch.inputs[0]); l.new(tint.outputs[2], ch.inputs[7]); ch.inputs[6].default_value = (*lib.hexc(chip), 1)  # fac 1 = paint
    l.new(ch.outputs[2], n["Principled BSDF"].inputs["Base Color"])
    lib.bump(n, l, nz.outputs["Fac"], 0.25, 0.01)
    return m
def flame_mat(name, hot=(1.0, 0.85, 0.45), cool=(1.0, 0.32, 0.05), strength=18.0):
    """flame: emission graded from a white-hot base to orange tips, soft transparent rim (never glowing balls)"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    for x_ in list(n): n.remove(x_)
    out = n.new("ShaderNodeOutputMaterial"); em = n.new("ShaderNodeEmission"); tr = n.new("ShaderNodeBsdfTransparent"); mx = n.new("ShaderNodeMixShader")
    lw = n.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.45
    tc = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Generated"], sep.inputs[0])
    rz = n.new("ShaderNodeValToRGB"); l.new(sep.outputs["Z"], rz.inputs["Fac"])
    rz.color_ramp.elements[0].color = (*hot, 1); rz.color_ramp.elements[1].position = 0.85; rz.color_ramp.elements[1].color = (*cool, 1)
    l.new(rz.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = strength
    inv = n.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; l.new(lw.outputs["Facing"], inv.inputs[1])
    hf = n.new("ShaderNodeMath"); hf.operation = "SUBTRACT"; hf.inputs[0].default_value = 1.15; l.new(sep.outputs["Z"], hf.inputs[1])
    al = n.new("ShaderNodeMath"); al.operation = "MULTIPLY"; l.new(inv.outputs[0], al.inputs[0]); l.new(hf.outputs[0], al.inputs[1])
    pw = n.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 0.6; l.new(al.outputs[0], pw.inputs[0])
    cl = n.new("ShaderNodeClamp"); l.new(pw.outputs[0], cl.inputs[0])
    l.new(cl.outputs[0], mx.inputs[0]); l.new(tr.outputs[0], mx.inputs[1]); l.new(em.outputs[0], mx.inputs[2]); l.new(mx.outputs[0], out.inputs["Surface"])
    return m
def flame(name, c, h, r, mat, lean=0.0, seed=0):
    """a licking flame tongue: teardrop lathe with a wavy, leaning tip"""
    prof = [(r * 0.25, 0), (r * 0.85, h * 0.08), (r, h * 0.2), (r * 0.82, h * 0.42), (r * 0.5, h * 0.66), (r * 0.22, h * 0.86), (0.0, h)]
    o = lathe(name, prof, c, mat, 14, cap=True); bz = T(*c).z
    for v in o.data.vertices:
        f = max(0.0, v.co.z - bz) / h
        v.co.x += lean * f * f * h + math.sin(f * 7 + seed) * 0.08 * r * f
        v.co.y += math.cos(f * 6 + seed * 2) * 0.1 * r * f
    o.visible_shadow = False
    return o
def fire(name, c, size, seed=0, light=True, energy=None):
    """a fire: a cluster of flame tongues of different heights + a warm point light"""
    rnd = random.Random(seed)
    inner = mat_once("flamebig", lambda: flame_mat("flamebig", (1.0, 0.45, 0.06), (1.0, 0.14, 0.01), 1.3))
    outer = mat_once("flamebig_o", lambda: flame_mat("flamebig_o", (1.0, 0.25, 0.02), (0.8, 0.06, 0.0), 0.9))
    for k in range(7):
        a = rnd.random() * math.tau; d = rnd.random() * 0.45 * size
        h = size * (0.7 + rnd.random() * 0.9) * (1.3 if d < 0.2 * size else 0.8)
        flame(f"{name}f{k}", (c[0] + d * math.cos(a), c[1], c[2] + d * math.sin(a)), h, size * (0.18 + rnd.random() * 0.12), inner if k % 2 else outer, lean=(rnd.random() - 0.5) * 0.4, seed=seed * 7 + k)
    if light:
        lo = lib.light("POINT", T(c[0], c[1] + size * 0.8, c[2]), energy or 400 * size * size, (1.0, 0.5, 0.18), size * 0.5)
        lo.visible_camera = False; lo.visible_glossy = False
def smoke_mat(name, col="#2a2522", dens=0.75):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    b = n["Principled BSDF"]; b.inputs["Base Color"].default_value = (*lib.hexc(col), 1); b.inputs["Roughness"].default_value = 1.0
    try: b.inputs["Specular IOR Level"].default_value = 0.0
    except Exception: pass
    lw = n.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.6
    inv = n.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; l.new(lw.outputs["Facing"], inv.inputs[1])
    mu = n.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = dens; l.new(inv.outputs[0], mu.inputs[0])
    l.new(mu.outputs[0], b.inputs["Alpha"])
    return m
def smoke_column(name, c, h, r0, r1, mat, drift=(0.0, 0.0), seed=0, puffs=9):
    """rising smoke: soft overlapping puffs widening with height and drifting with the wind"""
    rnd = random.Random(seed)
    for k in range(puffs):
        f = k / (puffs - 1); rr = (r0 + (r1 - r0) * f) * rnd.uniform(0.7, 1.05)
        p = (c[0] + drift[0] * f * f + rnd.uniform(-0.2, 0.2) * rr, c[1] + h * f, c[2] + drift[1] * f * f + rnd.uniform(-0.2, 0.2) * rr)
        o = lib.blob(f"{name}{k}", T(*p), (rr, rr * (0.9 + rnd.random() * 0.3), rr * 0.8), mat, 0.35 * rr, seed + k)
        o.visible_shadow = False
def wood_mat(key, a, b2, scale=6.0, rough=0.5): return mat_once(key, lambda: lib.wood(key, a, b2, scale, rough))
def pmat(key, col, rough=0.5, metal=0.0): return mat_once(key, lambda: lib.principled(key, lib.hexc(col), rough, metal))
def brass(): return mat_once("kbrass", lambda: lib.principled("kbrass", lib.hexc("#c8963a"), 0.28, 1.0))
def glassm(): return mat_once("kglass", lambda: lib.glass("kglass"))
def gold(): return mat_once("kgold", lambda: lib.principled("kgold", lib.hexc("#e8c060"), 0.25, 1.0))
def ink(): return pmat("kink", "#2a1a14", 0.6)
def text(body, c, size, mat, yaw=0.0, flat=True, align="CENTER", extrude=0.0005):
    """text at three point c: flat=True lies face-up, else stands facing three -z (towards a camera on the -z side)"""
    rot = (0, 0, yaw) if flat else (math.radians(90), 0, yaw)
    return lib.text(body, T(*c), size, mat, rot, align, extrude)

def candle(name, c, h=0.22, seed=0, light=1.0):
    """brass chamberstick with a dripping wax candle and a real flame + warm point light"""
    x, y, z = c
    lathe(f"{name}b", [(0.0, 0), (0.11, 0), (0.12, 0.012), (0.1, 0.022), (0.03, 0.03), (0.022, 0.06), (0.035, 0.07), (0.03, 0.09), (0.0, 0.09)], (x, y, z), brass(), 28)
    wax = pmat("kwax", "#efe2c4", 0.45)
    lathe(f"{name}w", [(0.0, 0.09), (0.024, 0.09), (0.024, 0.09 + h), (0.02, 0.095 + h), (0.0, 0.095 + h)], (x, y, z), wax, 18)
    rnd = random.Random(seed)
    for k in range(4):
        a = rnd.random() * math.tau; top = 0.09 + h * (0.6 + rnd.random() * 0.35); bot = 0.09 + h * 0.3 * rnd.random()
        lathe(f"{name}d{k}", [(0.0, top), (0.006, top - 0.01), (0.005, bot + 0.01), (0.0, bot)], (x + 0.023 * math.cos(a), y, z + 0.023 * math.sin(a)), wax, 8)
    tube(f"{name}wick", [(x, y + 0.093 + h, z), (x, y + 0.1 + h, z), (x + 0.002, y + 0.108 + h, z)], 0.0016, pmat("kwick", "#1a1210", 0.9))
    flame(f"{name}fl", (x, y + 0.1 + h, z), 0.06, 0.011, mat_once("flamemat", lambda: flame_mat("flame")), seed=seed)
    if light: lib.light("POINT", T(x, y + 0.14 + h, z), 6 * light, (1.0, 0.6, 0.28), 0.02).visible_camera = False
def toy_tank(name, c, yaw, col="#5a6a3a", s=1.0):
    m = mat_once("toytank" + col, lambda: worn("toytank" + col, col, "#8a8a80", 0.5, 0.4, 60, 0.6))
    trk = pmat("ktoytrk", "#2a2622", 0.6, 0.3)
    cw, sw = math.cos(yaw), math.sin(yaw); P = lambda lx, ly, lz: (c[0] + (lx * cw + lz * sw) * s, c[1] + ly * s, c[2] + (-lx * sw + lz * cw) * s)
    bx(f"{name}h", P(0, 0.022, 0), (0.12 * s, 0.022 * s, 0.065 * s), m, 0.004 * s, yaw)
    for sd in (-1, 1): bx(f"{name}t{sd}", P(0, 0.012, sd * 0.038), (0.13 * s, 0.024 * s, 0.022 * s), trk, 0.008 * s, yaw)
    cy(f"{name}tu", P(-0.01, 0.042, 0), 0.026 * s, 0.018 * s, m, 16)
    o = cy(f"{name}g", P(0.04, 0.045, 0), 0.004 * s, 0.07 * s, m, 8); o.rotation_euler = (0, math.radians(90), yaw + math.pi)
def pin_flag(name, c, col, h=0.12):
    cy(f"{name}p", (c[0], c[1] + h / 2, c[2]), 0.0025, h, pmat("kpin", "#d8d0c0", 0.2, 1.0), 6, bev=0)
    bx(f"{name}f", (c[0] - 0.03, c[1] + h - 0.02, c[2]), (0.06, 0.035, 0.002), pmat("kflag" + col, col, 0.7), 0)
def unit_block(name, c, yaw, col, top="#f2ece0"):
    bx(f"{name}", (c[0], c[1] + 0.02, c[2]), (0.09, 0.04, 0.06), wood_mat("kblock" + col, col, "#3a2a1a", 20), 0.004, yaw)
    bx(f"{name}t", (c[0], c[1] + 0.0405, c[2]), (0.05, 0.002, 0.03), pmat("kbtop" + top, top, 0.6), 0, yaw)
def book(name, c, size, col, yaw=0.0):
    w, h, d = size
    bx(f"{name}c", (c[0], c[1] + h / 2, c[2]), (w, h, d), mat_once("kbook" + col, lambda: lib.cloth("kbook" + col, col)), 0.006, yaw)
    bx(f"{name}p", (c[0], c[1] + h / 2, c[2]), (w * 0.97, h * 0.86, d * 1.012), pmat("kpages", "#efe6cc", 0.8), 0.002, yaw)
def cup(name, c, col="#f2ece0", coffee=True):
    por = pmat("kporc" + col, col, 0.2)
    lathe(f"{name}s", [(0.0, 0.0), (0.07, 0.0), (0.085, 0.012), (0.08, 0.014), (0.03, 0.008), (0.0, 0.008)], c, por, 32)
    lathe(f"{name}c", [(0.0, 0.01), (0.03, 0.01), (0.045, 0.03), (0.05, 0.08), (0.046, 0.08), (0.04, 0.03), (0.0, 0.016)], c, por, 32, cap=False)
    if coffee: lathe(f"{name}k", [(0.0, 0.065), (0.047, 0.065), (0.0, 0.065)], c, pmat("kcoffee", "#2a140a", 0.05), 24)
    tube(f"{name}hd", [(c[0] + 0.048, c[1] + 0.07, c[2]), (c[0] + 0.075, c[1] + 0.065, c[2]), (c[0] + 0.074, c[1] + 0.035, c[2]), (c[0] + 0.046, c[1] + 0.03, c[2])], 0.006, por)
def compass(name, c, r=0.07):
    lathe(f"{name}", [(0.0, 0), (r, 0), (r * 1.04, r * 0.15), (r, r * 0.3), (r * 0.9, r * 0.3), (r * 0.9, r * 0.2), (0.0, r * 0.2)], c, brass(), 36)
    cy(f"{name}d", (c[0], c[1] + r * 0.21, c[2]), r * 0.88, 0.002, pmat("kdial", "#efe4c8", 0.5), 32, bev=0)
    for k in range(2): bx(f"{name}n{k}", (c[0], c[1] + r * 0.225, c[2]), (r * 1.5, 0.002, r * 0.04) if k == 0 else (r * 0.04, 0.002, r * 1.5), ink(), 0)
    bx(f"{name}ndl", (c[0], c[1] + r * 0.24, c[2]), (r * 0.1, 0.003, r * 1.5), pmat("kneedle", "#b02020", 0.4, 0.3), 0, 0.4)
    lathe(f"{name}gl", [(0.0, r * 0.3), (r * 0.9, r * 0.3), (0.0, r * 0.36)], c, glassm(), 24)
def dividers(name, c, yaw, L=0.22):
    for sd in (-1, 1):
        a = yaw + sd * 0.18
        tube(f"{name}{sd}", [(c[0], c[1] + 0.012, c[2]), (c[0] + L * math.cos(a), c[1] + 0.004, c[2] - L * math.sin(a))], 0.004, brass(), bres=1)
    cy(f"{name}h", (c[0], c[1] + 0.012, c[2]), 0.012, 0.012, brass(), 16)
def magnifier(name, c, yaw):
    lathe(f"{name}r", [(0.06, 0.0), (0.072, 0.0), (0.072, 0.012), (0.06, 0.012)], (c[0], c[1] + 0.01, c[2]), brass(), 36, cap=False)
    lathe(f"{name}l", [(0.0, 0.004), (0.062, 0.006), (0.0, 0.012)], (c[0], c[1] + 0.01, c[2]), glassm(), 32)
    o = cy(f"{name}h", (c[0] + 0.13 * math.cos(yaw), c[1] + 0.016, c[2] - 0.13 * math.sin(yaw)), 0.012, 0.12, wood_mat("khandle", "#3a1a0c", "#1a0a04", 12, 0.3), 12)
    o.rotation_euler = (0, math.radians(90), yaw)
def inkwell(name, c):
    lathe(f"{name}", [(0.0, 0), (0.045, 0), (0.05, 0.01), (0.05, 0.05), (0.03, 0.065), (0.015, 0.07), (0.015, 0.085), (0.0, 0.085)], c, pmat("kinkglass", "#14202e", 0.05), 28)
    lathe(f"{name}cap", [(0.0, 0.085), (0.018, 0.085), (0.018, 0.1), (0.0, 0.1)], c, brass(), 16)
    pts = [(c[0] + 0.02, c[1] + 0.09, c[2]), (c[0] + 0.08, c[1] + 0.2, c[2] - 0.03), (c[0] + 0.14, c[1] + 0.3, c[2] - 0.05)]
    tube(f"{name}q", pts, 0.003, pmat("kquill", "#e8e0d0", 0.7))
    for k in range(12):
        f = 0.3 + k * 0.058; p = Vector(pts[0]).lerp(Vector(pts[2]), f)
        for sd in (-1, 1): tube(f"{name}v{k}{sd}", [tuple(p), tuple(p + Vector((sd * 0.025 * (1.15 - f), -0.012, 0.0)))], 0.004 * (1.3 - f), pmat("kvane", "#f2ece0", 0.8), bres=0)
def pocket_watch(name, c, yaw):
    lathe(f"{name}", [(0.0, 0), (0.05, 0), (0.055, 0.008), (0.05, 0.016), (0.0, 0.016)], c, gold(), 36)
    cy(f"{name}f", (c[0], c[1] + 0.0165, c[2]), 0.043, 0.001, pmat("kdial", "#efe4c8", 0.5), 32, bev=0)
    for k in range(12):
        a = k / 12 * math.tau; bx(f"{name}m{k}", (c[0] + 0.035 * math.cos(a), c[1] + 0.0175, c[2] + 0.035 * math.sin(a)), (0.006, 0.001, 0.002), ink(), 0, -a)
    bx(f"{name}h1", (c[0] + 0.01, c[1] + 0.018, c[2]), (0.02, 0.001, 0.003), ink(), 0, 0.3)
    bx(f"{name}h2", (c[0], c[1] + 0.018, c[2] + 0.014), (0.003, 0.001, 0.03), ink(), 0, 0.3)
    p0 = (c[0] + 0.058 * math.cos(yaw), c[1] + 0.01, c[2] - 0.058 * math.sin(yaw)); pts = [p0]
    for k in range(1, 8): pts.append((p0[0] + 0.04 * k * math.cos(yaw + 0.3 * math.sin(k)), c[1] + 0.004, p0[2] - 0.04 * k * math.sin(yaw + 0.3 * math.sin(k))))
    tube(f"{name}ch", pts, 0.0025, gold(), bres=1)
def toy_ship(name, c, yaw, L=0.28, col="#7a828c"):
    m = mat_once("toyship" + col, lambda: worn("toyship" + col, col, "#3a3a40", 0.45, 0.4, 50, 0.65))
    cw, sw = math.cos(yaw), math.sin(yaw); vs = []
    for lx, w in ((-0.5, 0.6), (-0.3, 1.0), (0.2, 1.0), (0.42, 0.6), (0.5, 0.0)):
        for ly, ws in ((0.0, 0.8), (0.035, 1.0)):
            for sd in (-1, 1):
                X, Z = lx * L, sd * w * ws * L * 0.08
                vs.append((c[0] + X * cw + Z * sw, c[1] + ly, c[2] - X * sw + Z * cw))
    fs = []
    for i in range(4):
        b = i * 4; nb = b + 4
        fs += [(b, nb, nb + 2, b + 2), (b + 1, b + 3, nb + 3, nb + 1), (b + 2, nb + 2, nb + 3, b + 3), (b, b + 1, nb + 1, nb)]
    fs += [(0, 2, 3, 1)]
    mesh_obj(f"{name}h", vs, fs, m)
    P = lambda lx, ly: (c[0] + lx * L * cw, c[1] + ly, c[2] - lx * L * sw)
    bx(f"{name}s1", P(-0.02, 0.05), (L * 0.3, 0.03, L * 0.09), m, 0.003, yaw); bx(f"{name}s2", P(0.02, 0.075), (L * 0.12, 0.025, L * 0.06), m, 0.003, yaw)
    cy(f"{name}f", P(-0.08, 0.085), 0.012, 0.05, m, 12)
    for tx in (0.28, -0.32): cy(f"{name}t{tx}", P(tx, 0.042), 0.018, 0.012, m, 12)

def bookcase(name, c, w, h, d, rows, wood, yaw=0.0, seed=0, cols=("#7a2a2a", "#2a4a6a", "#3a5a2a", "#8a6a2a", "#5a3a5a", "#c8b48a", "#2a2a2a", "#9a4a1e")):
    """open bookcase whose front faces three -z (yaw rotates about +y round c): carcass, shelves, books in linked copies"""
    rnd = random.Random(seed); cw, sw = math.cos(yaw), math.sin(yaw)
    P = lambda lx, ly, lz: (c[0] + lx * cw + lz * sw, c[1] + ly, c[2] - lx * sw + lz * cw)
    bx(f"{name}back", P(0, h / 2, d / 2 - 0.02), (w, h, 0.04), wood, 0.005, yaw)
    for sd in (-1, 1): bx(f"{name}side{sd}", P(sd * (w / 2 - 0.03), h / 2, 0), (0.06, h, d), wood, 0.01, yaw)
    bx(f"{name}top", P(0, h + 0.04, 0), (w + 0.12, 0.08, d + 0.06), wood, 0.02, yaw)
    sh = (h - 0.1) / rows
    src = None
    for r in range(rows + 1):
        bx(f"{name}sh{r}", P(0, 0.05 + r * sh, 0), (w - 0.06, 0.04, d - 0.02), wood, 0.005, yaw)
        if r == rows: break
        xx = -w / 2 + 0.08
        while xx < w / 2 - 0.12:
            bw = 0.035 + rnd.random() * 0.04; bh = sh * (0.6 + rnd.random() * 0.3)
            if rnd.random() < 0.06: xx += 0.12; continue
            if src is None:
                src = lib.box(f"{name}bk", (0, 0, 0), (1, 1, 1), lib.cloth("bookc", "#7a2a2a"), 0.04)
                bpy.context.view_layer.update()
            o = src.copy(); o.data = src.data; link(o)
            o.location = T(*P(xx + bw / 2, 0.07 + r * sh + bh / 2, -0.01)); o.rotation_euler = (0, 0, yaw + (0.12 if rnd.random() < 0.08 else 0)); o.scale = TS(bw, bh, d * 0.8)
            o.material_slots[0].link = "OBJECT"; o.material_slots[0].material = mat_once("kbook" + cols[rnd.randrange(len(cols))], lambda: lib.cloth("kbook" + cols[0], cols[0]))
            xx += bw + 0.004
    if src: bpy.data.objects.remove(src)
def window(name, c, w, h, glow=(0.35, 0.5, 1.0), strength=2.0, curtain="#6a1418", wood=None):
    """tall window in a wall facing three -z: glowing night panes behind mullions, heavy curtains, sill"""
    wood = wood or wood_mat("kwin", "#3a2214", "#1a0e06", 8, 0.4)
    bx(f"{name}pane", (c[0], c[1] + h / 2, c[2] + 0.04), (w, h, 0.02), lib.emit(f"{name}glow", glow, strength), 0)
    for k in range(3): bx(f"{name}mv{k}", (c[0] - w / 2 + k * w / 2, c[1] + h / 2, c[2]), (0.06, h, 0.06), wood, 0.005)
    for k in range(4): bx(f"{name}mh{k}", (c[0], c[1] + k * h / 3, c[2]), (w, 0.06, 0.06), wood, 0.005)
    bx(f"{name}sill", (c[0], c[1] - 0.04, c[2] - 0.08), (w + 0.3, 0.06, 0.22), wood, 0.01)
    cm = mat_once("kcurt" + curtain, lambda: lib.cloth("kcurt" + curtain, curtain))
    for sd in (-1, 1):
        for k in range(6):
            cy(f"{name}cur{sd}{k}", (c[0] + sd * (w / 2 + 0.05 + k * 0.07), c[1] + h / 2 + 0.1, c[2] - 0.12 - (k % 2) * 0.04), 0.06, h + 0.5, cm, 10)
    cy(f"{name}rod", (c[0], c[1] + h + 0.38, c[2] - 0.14), 0.02, w + 1.3, brass(), 10, rot=(0, math.radians(90), 0))
def sconce(name, c, energy=25):
    """wall sconce: brass arm, fabric shade glowing warm, real light"""
    tube(f"{name}arm", [(c[0], c[1] - 0.15, c[2] + 0.05), (c[0], c[1] - 0.1, c[2] - 0.08), (c[0], c[1], c[2] - 0.14)], 0.01, brass())
    lathe(f"{name}sh", [(0.07, 0.0), (0.12, 0.0), (0.07, 0.16), (0.05, 0.16)], (c[0], c[1], c[2] - 0.14), mat_once("kshade", lambda: lib.principled("kshade", lib.hexc("#f0c890"), 0.8, 0.0, (1.0, 0.7, 0.4), 2.5)), 24, cap=False)
    lib.light("POINT", T(c[0], c[1] + 0.06, c[2] - 0.14), energy, (1.0, 0.68, 0.4), 0.05)

# =====================================================================================================================
def map_mat(name="worldmap", img="map_void.png", rough=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True; n = m.node_tree.nodes; l = m.node_tree.links
    it = n.new("ShaderNodeTexImage"); it.image = bpy.data.images.load(os.path.join(HERE, "maps", img)); it.interpolation = "Cubic"
    b = n["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    # paper fibre + slight cockling for the close-ups
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 400; nz.inputs["Detail"].default_value = 4
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    nw = n.new("ShaderNodeTexNoise"); nw.inputs["Scale"].default_value = 3; l.new(tc.outputs["Object"], nw.inputs["Vector"])
    ad = n.new("ShaderNodeMath"); ad.operation = "MULTIPLY_ADD"; ad.inputs[1].default_value = 0.25
    l.new(nz.outputs["Fac"], ad.inputs[0]); l.new(nw.outputs["Fac"], ad.inputs[2])
    mul = n.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 0.12
    l.new(it.outputs["Color"], mul.inputs[6]); l.new(nz.outputs["Color"], mul.inputs[7])
    l.new(mul.outputs[2], b.inputs["Base Color"])
    lib.bump(n, l, ad.outputs[0], 0.12, 0.004)
    return m
def map_plane(name, x0, x1, z0, z1, y, m):
    me = bpy.data.meshes.new(name); me.from_pydata([T(x1, y, z0), T(x0, y, z0), T(x0, y, z1), T(x1, y, z1)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for k, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = c
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); me.materials.append(m); return o

def domino_mesh(name, pips, body, ivory):
    """black lacquered domino (three-local: x +-0.06, y 0..0.24, z +-0.02) with ivory pips and divider on both faces"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0.12, 0)) @ Matrix.Diagonal((0.12, 0.24, 0.04, 1)))
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.007, segments=2, profile=0.5, affect="EDGES")
    for f in bm.faces: f.material_index = 0
    spots = {0: [], 1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, 1), (-1, 1), (1, -1)],
             5: [(-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)], 6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)]}
    for face in (1, -1):
        for half, n in zip((0.06, 0.18), pips):
            for px, py in spots[n]:
                r = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.0085, radius2=0.0085, depth=0.002,
                                          matrix=Matrix.Translation((px * 0.028, half + py * 0.028, face * 0.0201)))
                for f in {f for v in r["verts"] for f in v.link_faces}: f.material_index = 1
        r = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0.12, face * 0.0201)) @ Matrix.Diagonal((0.09, 0.004, 0.002, 1)))
        for f in {f for v in r["verts"] for f in v.link_faces}: f.material_index = 1
    for v in bm.verts: v.co = T(*v.co)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(body); me.materials.append(ivory)
    return me

def clear_of_path(x, z, d=0.32):
    return all((x - px) ** 2 + (z - pz) ** 2 > d * d for px, pz in PATH)

DOMS = []
def build(M, D):
    random.seed(1939); DOMS.clear()
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.012, 0.01, 0.012, 1); bg.inputs[1].default_value = 1.0
    bx("floor", (0, -1.2, 0), (60, 0.1, 60), lib.parquet("vfloor", "#3a2214", "#2a180c"), 0)
    WD = lib.wood("vtable", "#5a3018", "#2a140a", 3, 0.35)
    bx("table", (0, -0.25, 0), (12.6, 0.5, 6.6), WD, 0.04)
    # moulded rim round the map, brass corner caps, turned legs
    for sz in (-1, 1): bx(f"rimz{sz}", (0, 0.01, sz * 3.15), (12.6, 0.05, 0.3), WD, 0.02)
    for sx in (-1, 1): bx(f"rimx{sx}", (sx * 6.15, 0.01, 0), (0.3, 0.05, 6.0), WD, 0.02)
    for sx in (-1, 1):
        for sz in (-1, 1):
            bx(f"cap{sx}{sz}", (sx * 6.15, 0.04, sz * 3.15), (0.32, 0.012, 0.32), brass(), 0.006)
            lathe(f"leg{sx}{sz}", [(0.0, -1.2), (0.16, -1.2), (0.12, -1.0), (0.09, -0.8), (0.14, -0.6), (0.1, -0.52), (0.0, -0.5)], (sx * 5.9, 0, sz * 2.9), WD, 20)
    map_plane("map", -6, 6, -3, 3, 0.021, map_mat())
    # dominoes: black lacquer, ivory pips; 7 pip variants shared as linked meshes
    body = lib.principled("dblack", lib.hexc("#121014"), 0.18); ivory = lib.principled("ivory", lib.hexc("#f2ead6"), 0.3)
    rnd = random.Random(7)
    meshes = [domino_mesh("domino_first", (6, 6), body, ivory)] + [domino_mesh(f"domino{k}", (rnd.randint(1, 6), rnd.randint(0, 6)), body, ivory) for k in range(6)]
    for i in range(len(PATH)):
        o = bpy.data.objects.new(f"dom{i}", meshes[0] if i == 0 else meshes[1 + i % 6]); link(o); DOMS.append(o)
    # ---------- props on the map (kept clear of the domino line) ----------
    y0 = 0.021
    def put(fn, x, z, *a, d=0.32, **k):
        if clear_of_path(x, z, d): fn(*a, **k)
    # behind the first domino (background of the opening close-up): candles, inkwell, books, the domino box
    candle("cand1", (1.55, y0, 2.45), 0.24, 1); candle("cand2", (-0.9, y0, 2.65), 0.16, 2, 0.8); candle("cand3", (2.6, y0, 2.0), 0.3, 3, 0.8)
    put(inkwell, 0.15, 2.35, "ink", (0.15, y0, 2.35))
    hs = [0.07, 0.06, 0.05, 0.06]
    for k, (w, d_, col) in enumerate(((0.34, 0.24, "#6a1e1e"), (0.31, 0.22, "#1e3a5a"), (0.33, 0.23, "#3a4a22"), (0.28, 0.2, "#7a5a2a"))):
        book(f"bk{k}", (-1.9 + k * 0.01, y0 + sum(hs[:k]), 2.35), (w, hs[k], d_), col, 0.2 + k * 0.15)
    dbm = wood_mat("kdbox", "#7a4a22", "#3a1e0c", 14, 0.4)
    bx("dbox", (1.05, y0 + 0.04, 1.95), (0.5, 0.08, 0.22), dbm, 0.01, 0.3)
    bx("dboxl", (1.2, y0 + 0.006, 2.25), (0.5, 0.012, 0.22), dbm, 0.004, 0.9)
    text("DOMINO", (1.2, y0 + 0.013, 2.25), 0.05, pmat("kgilt", "#e0b050", 0.3, 1.0), yaw=0.9)
    for k in range(4):
        o = bpy.data.objects.new(f"spare{k}", meshes[1 + k]); link(o)
        o.matrix_world = C @ Matrix.Translation((0.92 + k * 0.07, y0 + 0.06, 1.96 + k * 0.02)) @ Matrix.Rotation(0.3, 4, "Y") @ Matrix.Rotation(math.radians(-90), 4, "X")
    # Europe / Russia: toy armies, wooden unit blocks and pin flags round the start
    for k, (x, z, yw, col) in enumerate(((0.95, 1.75, 0.2, "#6a6e64"), (1.25, 1.62, -0.1, "#6a6e64"), (0.3, 1.95, 2.9, "#5a6a3a"), (-0.35, 1.7, 3.3, "#7a3a2a"),
                                         (-0.75, 1.95, 3.0, "#7a3a2a"), (1.7, 1.35, 0.5, "#4a5a7a"), (-1.3, 1.5, 3.5, "#7a3a2a"))):
        put(toy_tank, x, z, f"tt{k}", (x, y0, z), yw, col, 1.0)
    for k, (x, z, col) in enumerate(((0.75, 1.62, "#3a3a3a"), (0.05, 1.62, "#c8a02a"), (-0.55, 1.4, "#b02a2a"), (1.85, 1.62, "#2a4a9a"), (2.3, 1.85, "#b0303a"),
                                     (-1.6, 1.9, "#b02a2a"), (-2.4, 1.2, "#b02a2a"), (-3.4, 0.9, "#e8c040"), (-4.0, 0.6, "#e8c040"))):
        put(pin_flag, x, z, f"pf{k}", (x, y0, z), col, d=0.2)
    for k, (x, z, yw, col) in enumerate(((1.45, 1.92, 0.1, "#5a5e58"), (0.6, 2.05, -0.2, "#5a5e58"), (-0.15, 1.95, 0.4, "#8a3a2a"), (-1.0, 1.25, 0.2, "#8a3a2a"),
                                         (-2.0, 1.6, 0.3, "#8a3a2a"), (2.0, 1.15, 0.2, "#3a4a8a"))):
        put(unit_block, x, z, f"ub{k}", (x, y0, z), yw, col)
    # Asia / Pacific: toy fleets
    for k, (x, z, yw) in enumerate(((-4.6, 0.3, 0.3), (-4.9, -0.4, -0.2), (-5.2, 0.9, 0.6), (-3.8, -0.4, 1.2))):
        put(toy_ship, x, z, f"js{k}", (x, y0, z), yw, 0.3, "#6a6e78")
    # the Atlantic / Americas side: ships, coffee, compass, dividers, magnifier, watch, notes
    for k, (x, z, yw) in enumerate(((2.6, 0.6, 2.8), (3.0, 0.1, 2.6), (2.4, -0.6, 3.0), (3.4, 1.4, 2.9))):
        put(toy_ship, x, z, f"as{k}", (x, y0, z), yw, 0.28, "#7a828c")
    cup("cup", (4.6, y0, 2.0)); lathe("ring", [(0.075, 0.0), (0.085, 0.0), (0.085, 0.001), (0.075, 0.001)], (4.2, y0 + 0.0005, 1.75), pmat("kstain", "#5a3a1a", 0.6), 32, cap=False)
    compass("comp", (3.2, y0, -2.3), 0.09)
    dividers("div", (3.9, y0, -0.9), 0.4, 0.3)
    magnifier("mag", (1.8, y0, -1.9), 2.4)
    pocket_watch("watch", (4.9, y0, 0.4), 3.6)
    for k in range(3): bx(f"note{k}", (5.0 - k * 0.06, y0 + 0.002 + k * 0.002, -0.4 + k * 0.03), (0.32, 0.002, 0.42), pmat("kpaper", "#f0e6cc", 0.8), 0, 0.15 * k - 0.2)
    text("TOP SECRET", (4.88, y0 + 0.009, -0.3), 0.045, pmat("kred", "#a81e22", 0.5), yaw=0.1)
    candle("cand4", (-5.4, y0, 2.3), 0.2, 4, 0.7); candle("cand5", (5.4, y0, -2.6), 0.26, 5, 0.6)
    # ---------- the study beyond the table (dim, out of focus in the close-ups): panelled wall, night windows, books ----------
    WL = lib.wallpaper("vwall", "#2a3a2c", "#34463a"); PN = lib.wood("vpanel", "#3a2012", "#1a0c06", 5, 0.4)
    bx("wall", (0, 1.4, 7.6), (22, 5.2, 0.2), WL, 0); bx("wains", (0, -0.6, 7.45), (22, 1.2, 0.1), PN, 0.01); bx("rail", (0, 0.02, 7.4), (22, 0.08, 0.14), PN, 0.01)
    window("win1", (-3.2, 0.3, 7.5), 1.4, 2.6); window("win2", (4.2, 0.3, 7.5), 1.4, 2.6)
    bookcase("case", (0.6, -1.15, 7.2), 3.0, 3.2, 0.4, 6, PN, seed=3)
    for x_ in (-1.6, 2.8, -5.2, 6.2): sconce(f"sc{x_}", (x_, 1.6, 7.45))
    # sideboard with a radio (glowing dial), a decanter and a globe on the left
    bx("sideb", (-6.8, -0.75, 6.4), (2.4, 0.9, 0.6), PN, 0.02)
    bx("radio", (-6.4, -0.12, 6.4), (0.6, 0.36, 0.3), wood_mat("kradio", "#6a3a1a", "#2a140a", 9, 0.3), 0.04)
    bx("rdial", (-6.4, -0.06, 6.24), (0.3, 0.1, 0.01), lib.emit("rdial", (1.0, 0.65, 0.25), 6), 0.005)
    lathe("decanter", [(0.0, 0), (0.08, 0), (0.09, 0.08), (0.05, 0.2), (0.025, 0.24), (0.025, 0.3), (0.0, 0.3)], (-7.4, -0.3, 6.4), glassm(), 24)
    lathe("globe", [(0.0, -1.2), (0.25, -1.2), (0.05, -1.1), (0.04, -0.2), (0.0, -0.2)], (6.9, 0, 5.2), wood_mat("kglobest", "#5a3018", "#2a140a", 8, 0.4), 20)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, segments=48, ring_count=24, location=T(6.9, 0.25, 5.2)); g = bpy.context.object; bpy.ops.object.shade_smooth()
    g.data.materials.append(map_mat("vglobe", "map_world.png", 0.3))
    # ---------- light: a warm overhead lamp pool (key), candle practicals, cool rim from the far side ----------
    sp = lib.light("SPOT", T(0.6, 7.5, -1.5), 5200, (1.0, 0.82, 0.6), 0.9); lib.look_at(sp, T(-0.8, 0, 0.0)); sp.data.spot_size = math.radians(75); sp.data.spot_blend = 0.8
    sp2 = lib.light("SPOT", T(0.6, 3.0, 0.4), 260, (1.0, 0.75, 0.5), 0.4); lib.look_at(sp2, T(0.5, 0, 1.5)); sp2.data.spot_size = math.radians(60); sp2.data.spot_blend = 0.9
    rim = lib.light("AREA", T(-1, 1.6, 6.5), 450, (0.45, 0.6, 1.0), 4); lib.look_at(rim, T(0, 0, 0))
    fill = lib.light("AREA", T(2, 3, -7), 300, (0.6, 0.7, 1.0), 6); lib.look_at(fill, T(0, 0, 0))
    sm = lambda u: (lambda q: q * q * (3 - 2 * q))(max(0.0, min(1.0, u)))
    def update(f):
        t = f / 30
        for i, (px, pz) in enumerate(PATH):
            nx, pv = PATH[min(i + 1, len(PATH) - 1)], PATH[max(i - 1, 0)]
            yaw = math.atan2(nx[0] - pv[0], nx[1] - pv[1])
            ang = 1.2 * sm((t - T0 - i * DT) / 0.12)
            q3 = Quaternion((0, 1, 0), yaw) @ Quaternion((1, 0, 0), ang)          # three-space rotation (y up)
            piv = Quaternion((0, 1, 0), yaw) @ Vector((0, 0, 0.02))
            back = q3 @ Vector((0, 0, -0.02))
            p3 = Vector((px, 0.021, pz)) + piv + back
            m3 = Matrix.Translation(p3) @ q3.to_matrix().to_4x4()
            DOMS[i].matrix_world = C @ m3 @ C.inverted()
    return {"update": update}
