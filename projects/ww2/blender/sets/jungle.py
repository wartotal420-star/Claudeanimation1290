# Lubang jungle (shot 5): the lone soldier (Hiroo Onoda) at (0, 0, 4); the camera looks +z from about (1.4, 1.7, -1.5)
# towards (0, 1.4, 4). Ground flat (y 0) round the soldier. Dense rainforest with real leaf geometry (banana, taro, fern,
# palm, bamboo), buttressed trunks, lianas, a dappled canopy with warm light shafts, and Onoda's hide-out: a palm-thatch
# lean-to, a campfire with a pot, a tree carved with tally marks for the years, a faded Hinomaru, canteen and mess tin.
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, smoke_mat, text

def bx(name, c, s, m, bev=0.01, yaw=0.0): return lib.box(name, T(*c), TS(*s), m, bev, rot=(0, 0, yaw))
def cy(name, c, r, h, m, verts=12, rot=(0, 0, 0), bev=0.0): return lib.cyl(name, T(*c), r, h, m, verts, rot, bev)
SUNDIR = Vector((-0.45, 0.8, 0.4)).normalized()     # three-space direction towards the sun

# ------------------------------------------------------------------ materials
def leaf_mat(name, a, b, trans=(0.55, 0.85, 0.2)):
    """glossy two-tone leaf with veins, mixed with a translucent layer so backlit leaves glow"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    p = n["Principled BSDF"]; out = n["Material Output"]; p.inputs["Roughness"].default_value = 0.42
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 4; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    wv = n.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 14; wv.inputs["Distortion"].default_value = 1.5; l.new(tc.outputs["UV"] if False else tc.outputs["Object"], wv.inputs["Vector"])
    r = lib.ramp(n, l, nz.outputs["Fac"], [(0.3, lib.hexc(b)), (0.7, lib.hexc(a))])
    vm = n.new("ShaderNodeMix"); vm.data_type = "RGBA"; vm.blend_type = "MULTIPLY"; vm.inputs[0].default_value = 0.25
    l.new(r.outputs["Color"], vm.inputs[6]); l.new(wv.outputs["Color"], vm.inputs[7]); l.new(vm.outputs[2], p.inputs["Base Color"])
    tr = n.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (*trans, 1)
    mx = n.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.3
    l.new(p.outputs[0], mx.inputs[1]); l.new(tr.outputs[0], mx.inputs[2]); l.new(mx.outputs[0], out.inputs["Surface"])
    return m
def moss_mat(name, base, rough=0.9, moss="#4a6a1e", amount=0.45):
    """bark / stone with moss on the up-facing and shaded sides"""
    m = lib.principled(name, lib.hexc(base), rough); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; nz.inputs["Detail"].default_value = 8; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (9.0, 9.0, 0.35); l.new(tc.outputs["Object"], mp.inputs["Vector"])
    wv = n.new("ShaderNodeTexNoise"); wv.inputs["Scale"].default_value = 2.0; wv.inputs["Detail"].default_value = 6; wv.inputs["Distortion"].default_value = 0.6
    l.new(mp.outputs[0], wv.inputs["Vector"])
    br = lib.ramp(n, l, wv.outputs["Fac"], [(0.2, tuple(c * 0.45 for c in lib.hexc(base))), (0.8, lib.hexc(base))])
    geo = n.new("ShaderNodeNewGeometry"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(geo.outputs["Normal"], sep.inputs[0])
    ad = n.new("ShaderNodeMath"); ad.operation = "MULTIPLY_ADD"; ad.inputs[1].default_value = 0.6; l.new(sep.outputs["Z"], ad.inputs[0]); l.new(nz.outputs["Fac"], ad.inputs[2])
    mk = lib.ramp(n, l, ad.outputs[0], [(amount + 0.3, (0, 0, 0)), (amount + 0.42, (1, 1, 1))], (-200, 200))
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(mk.outputs["Color"], mx.inputs[0]); l.new(br.outputs["Color"], mx.inputs[6]); mx.inputs[7].default_value = (*lib.hexc(moss), 1)
    l.new(mx.outputs[2], b.inputs["Base Color"]); lib.bump(n, l, wv.outputs["Fac"], 0.6, 0.03)
    return m
def shaft_mat(name, col=(1.0, 0.8, 0.42), s=1.2, alpha=0.4):
    """sun shaft: faint warm emission, soft edges, fading toward the ground"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    for x_ in list(n): n.remove(x_)
    out = n.new("ShaderNodeOutputMaterial"); em = n.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*col, 1); em.inputs["Strength"].default_value = s
    tr = n.new("ShaderNodeBsdfTransparent"); mx = n.new("ShaderNodeMixShader")
    lw = n.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    inv = n.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; l.new(lw.outputs["Facing"], inv.inputs[1])
    pw = n.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 2.5; l.new(inv.outputs[0], pw.inputs[0])
    tc = n.new("ShaderNodeTexCoord"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Generated"], sp.inputs[0])
    gz = n.new("ShaderNodeMath"); gz.operation = "MULTIPLY"; l.new(pw.outputs[0], gz.inputs[0]); l.new(sp.outputs["Z"], gz.inputs[1])
    a = n.new("ShaderNodeMath"); a.operation = "MULTIPLY"; a.inputs[1].default_value = alpha; l.new(gz.outputs[0], a.inputs[0])
    l.new(a.outputs[0], mx.inputs[0]); l.new(tr.outputs[0], mx.inputs[1]); l.new(em.outputs[0], mx.inputs[2]); l.new(mx.outputs[0], out.inputs["Surface"])
    return m
def canopy_mat():
    m = lib.principled("canopy", lib.hexc("#1e3a14"), 0.6); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 10; nz.inputs["Roughness"].default_value = 0.7
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    r = lib.ramp(n, l, nz.outputs["Fac"], [(0.47, (0, 0, 0)), (0.5, (1, 1, 1))]); l.new(r.outputs["Color"], b.inputs["Alpha"])
    return m

# ------------------------------------------------------------------ plant meshes (built at the origin, three-local)
def banana_leaf(name, L, W, mat, seed):
    rnd = random.Random(seed); vs, fs = [], []; N = 14
    for i in range(N + 1):
        t = i / N; x = L * t; y = L * (0.55 * math.sin(t * math.pi * 0.8) - 0.25 * t * t)    # arching up then drooping
        w = W * math.sin(min(1.0, t * 1.05) * math.pi) ** 0.7 * (0.3 if t < 0.04 else 1.0)
        vs += [(x, y - w * 0.18, -w), (x, y + 0.02, 0), (x, y - w * 0.18, w)]
    for i in range(N):
        a = i * 3
        for k in range(2):
            if 2 < i < N - 1 and rnd.random() < 0.18: continue                  # wind-torn gaps
            fs.append((a + k, a + 3 + k, a + 4 + k, a + 1 + k))
    return mesh_obj(name, vs, fs, mat, smooth=True)
def heart_leaf(name, R, mat):
    vs, fs = [(0, 0, 0)], []; N = 24
    for ring, f in ((1, 0.5), (2, 1.0)):
        for k in range(N):
            th = k / N * math.tau; r = R * (0.62 + 0.38 * abs(math.cos(th / 2)) ** 0.5) * (0.35 if abs(math.sin(th / 2)) < 0.07 else 1)
            r *= f; x = r * math.cos(th); z = r * math.sin(th) * 0.8
            vs.append((x + R * 0.55, -0.12 * R * f * f - 0.25 * R * max(0, x / R) ** 2, z))
    for k in range(N):
        k1 = (k + 1) % N; fs.append((0, 1 + k, 1 + k1)); fs.append((1 + k, 1 + N + k, 1 + N + k1, 1 + k1))
    return mesh_obj(name, vs, fs, mat, smooth=True)
def frond(name, L, mat, leaflet=0.18, n=22, rise=0.5, seed=0, palm=False):
    """fern / palm frond along +x: arched rachis with paired leaflets"""
    rnd = random.Random(seed); vs, fs = [], []
    def rach(t): return Vector((L * t, L * (rise * math.sin(t * math.pi * 0.7) - 0.35 * t * t), 0))
    for i in range(1, n):
        t = i / n; p = rach(t); d = (rach(t + 0.01) - p).normalized()
        ll = leaflet * (math.sin(t * math.pi) ** 0.6 if not palm else (1.0 - 0.6 * t)) * rnd.uniform(0.85, 1.1)
        for sd in (-1, 1):
            tip = p + Vector((d.x * ll * 0.5, -ll * (0.5 if palm else 0.15), sd * ll)); w = ll * (0.12 if palm else 0.22)
            b = len(vs); vs += [tuple(p - d * w), tuple(p + d * w), tuple(tip + d * w * 0.3), tuple(tip - d * w * 0.3)]
            fs.append((b, b + 1, b + 2, b + 3))
    pts = [rach(i / 12) for i in range(13)]
    b = len(vs)
    for k, p in enumerate(pts): vs += [tuple(p + Vector((0, 0, -0.008))), tuple(p + Vector((0, 0, 0.008)))]
    for k in range(12): fs.append((b + k * 2, b + k * 2 + 2, b + k * 2 + 3, b + k * 2 + 1))
    return mesh_obj(name, vs, fs, mat, smooth=False)
def place(src, name, p, yaw=0.0, s=1.0, tilt=0.0):
    o = src.copy(); o.name = name; link(o); o.location = T(*p); o.rotation_euler = (0, -tilt, yaw); o.scale = (s, s, s); return o

# ------------------------------------------------------------------ terrain
def gh(x, z):
    h = 0.35 * noise.noise(Vector((x * 0.12, z * 0.12, 4.0))) + 0.1 * noise.noise(Vector((x * 0.6, z * 0.6, 9.0)))
    d = math.hypot(x - 0.2, (z - 4.5) * 0.8)
    return h * min(1.0, max(0.0, (d - 2.0) / 3.0)) + 0.4 * max(0.0, (z - 20) / 25)
def ground():
    x0, x1, z0, z1, st = -30, 30, -10, 50, 0.4
    nx, nz = int((x1 - x0) / st) + 1, int((z1 - z0) / st) + 1
    vs = [T(x0 + i * st, gh(x0 + i * st, z0 + j * st), z0 + j * st) for j in range(nz) for i in range(nx)]
    fs = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(nz - 1) for i in range(nx - 1)]
    me = bpy.data.meshes.new("jground"); me.from_pydata(vs, [], fs); me.update()
    for p in me.polygons: p.use_smooth = True
    o = link(bpy.data.objects.new("jground", me))
    m = lib.principled("jground", lib.hexc("#3a2a18"), 0.85); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); vo = n.new("ShaderNodeTexNoise"); vo.inputs["Scale"].default_value = 3.5; vo.inputs["Detail"].default_value = 10; vo.inputs["Roughness"].default_value = 0.7; l.new(tc.outputs["Object"], vo.inputs["Vector"])
    lv = n.new("ShaderNodeTexVoronoi"); lv.inputs["Scale"].default_value = 30; l.new(tc.outputs["Object"], lv.inputs["Vector"])
    nz_ = n.new("ShaderNodeTexNoise"); nz_.inputs["Scale"].default_value = 0.4; nz_.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], nz_.inputs["Vector"])
    lit = lib.ramp(n, l, vo.outputs["Fac"], [(0.3, lib.hexc("#24160c")), (0.45, lib.hexc("#4a2e16")), (0.55, lib.hexc("#7a4a1e")), (0.65, lib.hexc("#5a4a1a")), (0.75, lib.hexc("#2e3a14"))])
    mo = lib.ramp(n, l, nz_.outputs["Fac"], [(0.5, (0, 0, 0)), (0.62, (1, 1, 1))], (-200, 200))
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(mo.outputs["Color"], mx.inputs[0]); l.new(lit.outputs["Color"], mx.inputs[6]); mx.inputs[7].default_value = (*lib.hexc("#33501a"), 1)
    l.new(mx.outputs[2], b.inputs["Base Color"]); lib.bump(n, l, lv.outputs["Distance"], 0.5, 0.02)
    me.materials.append(m)

# ------------------------------------------------------------------ plants
def rain_tree(name, x, z, r, bark, rnd, buttress=True):
    y0 = gh(x, z)
    lathe(f"{name}", [(r * 2.2, -0.2), (r * 1.5, 0.3), (r * 1.15, 1.0), (r, 2.5), (r * 0.9, 18), (0.0, 18.5)], (x, y0, z), bark, 18)
    if buttress:
        for k in range(rnd.randint(3, 5)):
            a = rnd.random() * math.tau; L = r * rnd.uniform(2.4, 3.6); hh = r * rnd.uniform(2.5, 4); ca, sa = math.cos(a), math.sin(a); w = r * 0.1
            pts = [(0, -0.2, 0), (L, -0.2, 0), (r * 0.9, hh, 0)]
            vs = []
            for sd in (-1, 1):
                for px, py, pz in pts: vs.append((x + px * ca - sd * w * sa, y0 + py, z + px * sa + sd * w * ca))
            mesh_obj(f"{name}b{k}", vs, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], bark)
def banana(name, x, z, h, leafsrc, stem, rnd):
    y0 = gh(x, z); tube(f"{name}st", [(x, y0, z), (x + 0.05, y0 + h * 0.5, z), (x + 0.1, y0 + h, z)], 0.11, stem, res=4, bres=2, taper=lambda f: 1 - 0.3 * f)
    for k in range(7):
        place(rnd.choice(leafsrc), f"{name}l{k}", (x + 0.1, y0 + h - 0.1, z), k / 7 * math.tau + rnd.random() * 0.5, rnd.uniform(0.8, 1.15), tilt=rnd.uniform(-0.15, 0.25))
def fern(name, x, z, srcs, rnd, s=1.0):
    y0 = gh(x, z)
    for k in range(9): place(rnd.choice(srcs), f"{name}{k}", (x, y0, z), k / 9 * math.tau + rnd.random() * 0.4, s * rnd.uniform(0.7, 1.15))
def taro(name, x, z, leaf, stalk, rnd, face=0.0):
    y0 = gh(x, z)
    for k in range(4):
        a = face + rnd.uniform(-0.9, 0.9); hh = rnd.uniform(0.8, 1.5); L = rnd.uniform(0.2, 0.4)
        tip = (x + L * math.cos(a), y0 + hh, z - L * math.sin(a))
        tube(f"{name}s{k}", [(x, y0, z), (x + L * 0.4 * math.cos(a), y0 + hh * 0.6, z - L * 0.4 * math.sin(a)), tip], 0.025, stalk, res=4, bres=1)
        place(leaf, f"{name}l{k}", tip, a, rnd.uniform(0.8, 1.2), tilt=rnd.uniform(0.2, 0.5))
def palm(name, x, z, h, lean, yaw, frsrc, trunk, rnd):
    y0 = gh(x, z); c, s = math.cos(yaw), math.sin(yaw)
    pts = [(x + lean * h * f * f * c, y0 + h * f, z - lean * h * f * f * s) for f in (0, 0.33, 0.66, 1.0)]
    tube(f"{name}t", pts, 0.2, trunk, res=6, bres=2, taper=lambda f: 1 - 0.35 * f)
    for k in range(11): place(rnd.choice(frsrc), f"{name}f{k}", pts[-1], k / 11 * math.tau + rnd.random() * 0.3, rnd.uniform(0.85, 1.1), tilt=rnd.uniform(-0.2, 0.1))
def bamboo(name, x, z, n, mat, node, leafsrc, rnd):
    y0 = gh(x, z)
    for k in range(n):
        px, pz = x + rnd.uniform(-0.5, 0.5), z + rnd.uniform(-0.5, 0.5); lean = rnd.uniform(-0.12, 0.12); h = rnd.uniform(7, 11); r = rnd.uniform(0.04, 0.07)
        top = (px + lean * h, y0 + h, pz + lean * h * 0.5)
        tube(f"{name}{k}", [(px, y0, pz), (px + lean * h * 0.5, y0 + h * 0.5, pz + lean * h * 0.25), top], r, mat, res=4, bres=1)
        for j in range(1, int(h / 0.45)):
            f = j * 0.45 / h; cy(f"{name}n{k}{j}", (px + lean * h * f, y0 + j * 0.45, pz + lean * h * 0.5 * f), r * 1.15, 0.025, node, 10)
        for j in range(4):
            f = 0.55 + j * 0.12; place(leafsrc, f"{name}lf{k}{j}", (px + lean * h * f, y0 + h * f, pz + lean * h * 0.5 * f), rnd.random() * 6.3, rnd.uniform(0.6, 0.9))

def build(M, D):
    random.seed(1974); rnd = random.Random(1974)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.3, 0.5, 0.26, 1); bg.inputs[1].default_value = 1.0
    ground()
    BARK = moss_mat("jbark", "#5a4632", 0.9, "#3e5a1a", 0.35); BARK2 = moss_mat("jbark2", "#7a6a56", 0.85, "#4a6a20", 0.4)
    L1 = leaf_mat("jleaf1", "#3e8a24", "#1e4a12"); L2 = leaf_mat("jleaf2", "#5a9a2a", "#2a5a14", (0.7, 0.9, 0.25)); L3 = leaf_mat("jleaf3", "#2a6a2a", "#123a14")
    BAN = leaf_mat("jbanana", "#6aa832", "#3a6a1a", (0.75, 0.95, 0.3)); TAR = leaf_mat("jtaro", "#2e7a2a", "#164a16", (0.5, 0.85, 0.25))
    STEM = mat_once("jstem", lambda: worn("jstem", "#5a7a2a", "#6a4a2a", 0.6, 0.0, 6, 0.6, "#3a4a1a"))
    # source meshes (moved out of sight, instanced as linked copies)
    bl = [banana_leaf(f"bl{k}", 1.9 + k * 0.3, 0.32, BAN, k) for k in range(3)]
    hl = heart_leaf("hl", 0.42, TAR)
    fr = [frond(f"fr{k}", 1.0 + k * 0.25, [L1, L2, L3][k], 0.17, 22, 0.55, k) for k in range(3)]
    pf = [frond(f"pf{k}", 3.6 + k * 0.5, L1 if k else L3, 0.7, 30, 0.25, 10 + k, palm=True) for k in range(2)]
    bf = frond("bf", 0.6, L2, 0.12, 10, 0.1, 21, palm=True)
    for o in bl + fr + pf + [hl, bf]: o.location = T(0, -40, 0)
    # big trunks with buttress roots; the near ones frame the soldier
    trees = [(-3.2, 7.5, 0.55), (3.6, 10.5, 0.7), (-6.5, 13, 0.8), (6.8, 6.5, 0.6), (-1.5, 17, 0.6), (9, 15, 0.9), (-10, 9, 0.7), (2.0, 24, 0.9),
             (-7, 24, 1.0), (12, 22, 0.8), (-14, 18, 0.9), (16, 12, 0.7), (-4, 32, 1.1), (8, 32, 1.0), (-18, 30, 1.0), (20, 30, 1.0), (0, 40, 1.2)]
    for k, (x, z, r) in enumerate(trees): rain_tree(f"tr{k}", x, z, r * 0.6, BARK if k % 3 else BARK2, rnd)
    # thin understorey saplings and lianas looping between trunks
    for k in range(30):
        x, z = rnd.uniform(-16, 16), rnd.uniform(8, 38)
        if abs(x) < 2 and z < 12: continue
        tube(f"sap{k}", [(x, gh(x, z), z), (x + rnd.uniform(-0.3, 0.3), 4, z), (x + rnd.uniform(-0.6, 0.6), 9, z + rnd.uniform(-0.5, 0.5))], rnd.uniform(0.04, 0.1), BARK2, res=4, bres=1)
    VINE = mat_once("jvine", lambda: worn("jvine", "#4a5a2a", "#3a2a1a", 0.8, 0.0, 10, 0.55, "#2a3a14"))
    for k in range(16):
        a, b = trees[rnd.randrange(len(trees))], trees[rnd.randrange(len(trees))]
        if a == b: continue
        pa, pb = Vector((a[0], rnd.uniform(6, 11), a[1])), Vector((b[0], rnd.uniform(6, 11), b[1]))
        mid = (pa + pb) / 2 - Vector((0, rnd.uniform(2, 5), 0))
        tube(f"liana{k}", [tuple(pa), tuple((pa + mid) / 2 - Vector((0, 0.8, 0))), tuple(mid), tuple((pb + mid) / 2 - Vector((0, 0.8, 0))), tuple(pb)], rnd.uniform(0.025, 0.06), VINE, res=10, bres=1)
    for k, (x, z) in enumerate(((-2.4, 6.0), (2.8, 9.0), (-4.5, 11), (5.0, 7.5), (-1.0, 14), (1.6, 6.8))):
        top = rnd.uniform(7, 10); pts = [(x + math.sin(j * 0.9) * 0.15, top - j * (top - rnd.uniform(1.0, 2.6)) / 5, z + math.cos(j * 0.7) * 0.1) for j in range(6)]
        tube(f"hang{k}", pts, 0.018, VINE, res=8, bres=1)
    # banana plants, taro, ferns, palms, bamboo
    for k, (x, z, h) in enumerate(((-2.8, 4.2, 2.4), (3.4, 6.2, 2.8), (-5.5, 9.0, 3.0), (5.8, 11.5, 3.2), (-1.6, 12.0, 2.6), (8.0, 9.0, 2.7), (-8.5, 15, 3.0), (3.0, 16, 2.6), (-4, 20, 3.2), (10, 18, 3.0))):
        banana(f"ban{k}", x, z, h, bl, STEM, rnd)
    TSTALK = mat_once("jtstalk", lambda: worn("jtstalk", "#4a7a2a", "#2a4a14", 0.5, 0.0, 6, 0.6))
    for k, (x, z, f) in enumerate(((1.9, 2.6, 2.6), (-1.7, 2.2, 0.6), (2.6, 4.5, 2.8), (-2.2, 5.6, 0.3), (4.4, 3.0, 2.9), (-3.8, 3.4, 0.2), (1.2, 8.5, 2.0), (-0.9, 9.5, 1.0))):
        taro(f"taro{k}", x, z, hl, TSTALK, rnd, face=f)
    for k in range(70):
        x, z = rnd.uniform(-12, 12), rnd.uniform(0.5, 28)
        if math.hypot(x - 0.1, (z - 4.2) * 1.4) < 1.6: continue
        if math.hypot(x - 1.0, z - 0.5) < 1.2: continue
        fern(f"fern{k}", x, z, fr, rnd, rnd.uniform(0.7, 1.4))
    TRUNK = mat_once("jpalm", lambda: lib.brickmat("jpalm", "#7a6a50", "#5a4a36", "#3a3020", 3.0, 3.0, 0.08, 0.9))
    for k, (x, z, h, ln, yw) in enumerate(((-9, 20, 10, 0.2, 0.5), (11, 25, 12, 0.15, 2.5), (-15, 26, 11, 0.25, 0.2), (4.5, 30, 13, 0.1, 1.8), (16, 17, 9, 0.3, 2.9), (-3, 36, 12, 0.2, 1.0))):
        palm(f"palm{k}", x, z, h, ln, yw, pf, TRUNK, rnd)
    bamboo("bam1", -7.5, 6.0, 9, mat_once("jbamboo", lambda: worn("jbamboo", "#7a9a3a", "#a89a4a", 0.35, 0.0, 4, 0.55, "#5a7a2a")), pmat("jbnode", "#5a6a2a", 0.5), bf, rnd)
    bamboo("bam2", 7.5, 13.5, 7, mat_once("jbamboo", lambda: None), pmat("jbnode", "#5a6a2a", 0.5), bf, rnd)
    # mossy rocks and a fallen log with bracket fungi
    ROCK = moss_mat("jrock", "#6a6a60", 0.8, "#4a6a1e", 0.25)
    for k, (x, z, s_) in enumerate(((-1.4, 2.6, 0.35), (2.2, 5.4, 0.3), (-3.6, 8.4, 0.6), (4.5, 9.4, 0.5), (0.9, 11, 0.4), (-2.0, 1.2, 0.25))):
        lib.blob(f"rock{k}", T(x, gh(x, z), z), (s_ * 1.4, s_, s_ * 1.2), ROCK, 0.25 * s_, k)
    LOG = moss_mat("jlog", "#4a3a2a", 0.9, "#4a6a1e", 0.2)
    tube("log", [(-6.5, 0.35, 10.5), (-4, 0.45, 11.2), (-1.5, 0.4, 12.6)], 0.42, LOG, res=6, bres=3)
    FUN = pmat("jfungus", "#d88a2a", 0.5)
    for k in range(7): lathe(f"fung{k}", [(0.0, 0.0), (0.16 - k * 0.012, 0.01), (0.13 - k * 0.01, 0.04), (0.0, 0.045)], (-5.6 + k * 0.6, 0.55 + (k % 3) * 0.1, 10.5 + k * 0.28), FUN, 16, sz=0.6, cap=True)
    # ---------- Onoda's hide-out ----------
    BAM = mat_once("jbamboo", lambda: None); THATCH = leaf_mat("jthatch", "#8a7a3a", "#5a4a22", (0.6, 0.5, 0.2))
    for k, (x, z, h) in enumerate(((2.2, 7.6, 1.9), (4.6, 7.2, 1.9), (2.0, 9.4, 0.9), (4.4, 9.0, 0.9))):
        tube(f"post{k}", [(x, 0, z), (x, h, z)], 0.05, BAM, res=2, bres=1)
    tube("ridge", [(2.2, 1.9, 7.6), (4.6, 1.9, 7.2)], 0.045, BAM, res=2, bres=1)
    thsrc = frond("thatchfr", 2.4, THATCH, 0.35, 18, 0.0, 33, palm=True); thsrc.location = T(0, -40, 0)
    for k in range(12):
        f = k / 11; x, z = 2.1 + 2.6 * f, 7.55 - 0.4 * f
        place(thsrc, f"thatch{k}", (x, 2.0, z), -math.pi / 2 + rnd.uniform(-0.15, 0.15), rnd.uniform(0.9, 1.05), tilt=0.55)
    MAT = mat_once("jmat", lambda: lib.brickmat("jmat", "#b8a06a", "#9a8250", "#7a6440", 20, 0.08, 0.5, 0.9))
    bx("sleepmat", (3.4, 0.03, 8.4), (1.8, 0.03, 0.9), MAT, 0.005, 0.15)
    tube("blanket", [(2.7, 0.12, 8.7), (3.4, 0.12, 8.75), (4.0, 0.12, 8.6)], 0.11, mat_once("jblank", lambda: lib.cloth("jblank", "#6a5a3a")))
    bx("ammobox", (4.2, 0.18, 7.9), (0.5, 0.36, 0.3), wood_mat("jbox", "#6a5232", "#3a2a1a", 10, 0.8), 0.02, 0.3)
    # the campfire: ring of stones, crossed logs, flames, a blackened pot on a tripod, a thin smoke wisp
    fx, fz = -1.5, 6.6
    for k in range(9):
        a = k / 9 * math.tau; lib.blob(f"fst{k}", T(fx + 0.42 * math.cos(a), 0.06, fz + 0.42 * math.sin(a)), (0.13, 0.09, 0.11), ROCK, 0.03, k)
    CHAR = mat_once("jchar", lambda: worn("jchar", "#2a1e16", "#120c08", 0.9, 0.0, 12, 0.5, "#1a1410"))
    for k in range(4):
        a = k / 4 * math.pi; tube(f"flog{k}", [(fx - 0.35 * math.cos(a), 0.05, fz - 0.35 * math.sin(a)), (fx + 0.35 * math.cos(a), 0.12, fz + 0.35 * math.sin(a))], 0.045, CHAR, res=2, bres=1)
    fire("campfire", (fx, 0.08, fz), 0.32, seed=5, energy=55)
    for e in range(3):
        a = e / 3 * math.tau + 0.3; tube(f"tri{e}", [(fx + 0.55 * math.cos(a), 0, fz + 0.55 * math.sin(a)), (fx, 1.0, fz)], 0.018, BARK2, res=2, bres=1)
    IRON = mat_once("jiron", lambda: worn("jiron", "#2a2622", "#5a3a20", 0.6, 0.6, 14, 0.6))
    lathe("pot", [(0.0, 0.4), (0.12, 0.42), (0.17, 0.5), (0.17, 0.62), (0.15, 0.66), (0.0, 0.66)], (fx, 0, fz), IRON, 20)
    tube("potwire", [(fx - 0.16, 0.64, fz), (fx, 0.95, fz), (fx + 0.16, 0.64, fz)], 0.005, IRON, res=6, bres=0)
    lathe("smokew", [(0.0, 0.7), (0.05, 0.8), (0.12, 1.4), (0.3, 2.6), (0.5, 3.8), (0.0, 4.2)], (fx, 0, fz), smoke_mat("jsmoke", "#c8ccc0", 0.18), 16)
    # canteen, mess tin, a tree carved with tally marks for the years in hiding, a faded Hinomaru on a bamboo pole
    lathe("canteen", [(0.0, 0.0), (0.09, 0.01), (0.1, 0.1), (0.09, 0.19), (0.03, 0.22), (0.02, 0.25), (0.0, 0.25)], (1.0, 0.0, 5.3), worn("jcanteen", "#5a5a34", "#3a3020", 0.6, 0.3, 30, 0.6), 20, sz=0.55)
    lathe("cork", [(0.0, 0.24), (0.022, 0.24), (0.02, 0.29), (0.0, 0.29)], (1.0, 0.0, 5.3), pmat("jcork", "#a87a4a", 0.8), 10)
    lathe("messtin", [(0.0, 0.0), (0.1, 0.0), (0.11, 0.07), (0.0, 0.07)], (-0.95, 0.0, 5.6), pmat("jalu", "#8a8a80", 0.4, 0.8), 20, sx=1.3, sz=0.8)
    KNOT = pmat("jcarve", "#c8a878", 0.8)
    tx_, tz_, tr_ = -3.2, 7.5, 0.33
    for g in range(6):
        for k in range(5 if g < 5 else 3):
            a = math.radians(-120) + g * 0.12 + k * 0.022; y_ = 1.2 + (g % 3) * 0.3
            o = bx(f"tally{g}{k}", (tx_ + tr_ * math.cos(a), y_, tz_ - tr_ * math.sin(a)), (0.012, 0.22, 0.02), KNOT, 0, a)
        if g < 5: bx(f"tallyx{g}", (tx_ + tr_ * math.cos(a - 0.05), 1.2 + (g % 3) * 0.3, tz_ - tr_ * math.sin(a - 0.05)), (0.012, 0.25, 0.02), KNOT, 0, a - 0.05).rotation_euler.x = 0.0
    tube("flagpole", [(4.7, 0, 7.0), (4.75, 2.8, 7.05)], 0.025, BAM, res=2, bres=1)
    fm = lib.principled("jflag", lib.hexc("#e8e0cc"), 0.9); t_, n_, l_ = lib.nodes(fm)
    tc_ = n_.new("ShaderNodeTexCoord"); sp_ = n_.new("ShaderNodeSeparateXYZ"); l_.new(tc_.outputs["UV"], sp_.inputs[0])
    dx = n_.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = 0.5; l_.new(sp_.outputs["X"], dx.inputs[0])
    dy = n_.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = 0.5; l_.new(sp_.outputs["Y"], dy.inputs[0])
    sx_ = n_.new("ShaderNodeMath"); sx_.operation = "MULTIPLY"; sx_.inputs[1].default_value = 1.5; l_.new(dx.outputs[0], sx_.inputs[0])
    cmb = n_.new("ShaderNodeCombineXYZ"); l_.new(sx_.outputs[0], cmb.inputs[0]); l_.new(dy.outputs[0], cmb.inputs[1])
    ln = n_.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; l_.new(cmb.outputs[0], ln.inputs[0])
    dr = lib.ramp(n_, l_, ln.outputs["Value"], [(0.29, lib.hexc("#a8282a")), (0.3, lib.hexc("#e0d6bc"))])
    dn = n_.new("ShaderNodeTexNoise"); dn.inputs["Scale"].default_value = 8; l_.new(tc_.outputs["Object"], dn.inputs["Vector"])
    dm = n_.new("ShaderNodeMix"); dm.data_type = "RGBA"; dm.blend_type = "MULTIPLY"; dm.inputs[0].default_value = 0.35; l_.new(dr.outputs["Color"], dm.inputs[6]); l_.new(dn.outputs["Color"], dm.inputs[7])
    l_.new(dm.outputs[2], n_["Principled BSDF"].inputs["Base Color"])
    fv, ff = [], []; NX, NY = 10, 6
    for j in range(NY + 1):
        for i in range(NX + 1):
            u, v = i / NX, j / NY; fv.append((4.75 - 0.75 * u, 2.75 - 0.5 * v - 0.1 * u * u, 7.05 + 0.06 * math.sin(u * 7 + v * 2)))
    for j in range(NY):
        for i in range(NX):
            if i > 7 and (i + j) % 3 == 0: continue                                  # frayed end
            a = j * (NX + 1) + i; ff.append((a, a + 1, a + NX + 2, a + NX + 1))
    fo = mesh_obj("flag", fv, ff, fm); uv = fo.data.uv_layers.new()
    for p in fo.data.polygons:
        for li in p.loop_indices:
            vi = fo.data.loops[li].vertex_index; uv.data[li].uv = ((vi % (NX + 1)) / NX, 1 - (vi // (NX + 1)) / NY)
    # ---------- depth: a far wall of foliage, extra plants in the distance, two thin mist layers ----------
    for k in range(40):
        x, z = rnd.uniform(-22, 22), rnd.uniform(26, 44)
        if k % 3 == 0: banana(f"fban{k}", x, z, rnd.uniform(2.5, 4), bl, STEM, rnd)
        else: fern(f"ffern{k}", x, z, fr, rnd, rnd.uniform(1.2, 2.0))
    for k in range(8): palm(f"fpalm{k}", rnd.uniform(-25, 25), rnd.uniform(38, 46), rnd.uniform(9, 14), 0.15, rnd.uniform(0, 6), pf, TRUNK, rnd)
    wall = lib.principled("jwall", lib.hexc("#1e3a14"), 0.7); t_, n_, l_ = lib.nodes(wall)
    tcw = n_.new("ShaderNodeTexCoord"); nw = n_.new("ShaderNodeTexNoise"); nw.inputs["Scale"].default_value = 0.25; nw.inputs["Detail"].default_value = 12; l_.new(tcw.outputs["Object"], nw.inputs["Vector"])
    rw = lib.ramp(n_, l_, nw.outputs["Fac"], [(0.35, lib.hexc("#0e2008")), (0.55, lib.hexc("#2a5218")), (0.7, lib.hexc("#4a7a24"))]); l_.new(rw.outputs["Color"], n_["Principled BSDF"].inputs["Base Color"])
    lib.bump(n_, l_, nw.outputs["Fac"], 1.0, 0.5)
    mesh_obj("fwall", [(-60, -1, 48), (60, -1, 48), (60, 30, 48), (-60, 30, 48)], [(0, 1, 2, 3)], wall)
    mist = mat_once("jmist", lambda: smoke_mat("jmist", "#b8d8c0", 0.22))
    for k, (z, y) in enumerate(((24, 1.2), (34, 1.8))):
        lib.blob(f"mist{k}", T(rnd.uniform(-4, 4), y, z), (16, 1.4, 1.2), mist, 0.4, k).visible_shadow = False
    # ---------- light: sun through a dappled canopy, visible shafts, warm bounce on the soldier, cool green sky fill ----------
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(0, 13, 18)); cp = bpy.context.object; cp.scale = (70, 80, 1); bpy.ops.object.transform_apply(scale=True)
    cp.data.materials.append(canopy_mat())
    sun = lib.light("SUN", (0, 0, 0), 11.0, (1.0, 0.8, 0.5), math.radians(1.2)); sun.rotation_euler = (-T(*SUNDIR)).to_track_quat("-Z", "Y").to_euler()
    SH = shaft_mat("jshaft")
    for k, (x, z, w) in enumerate(((-2.0, 9.0, 0.7), (1.5, 13.0, 1.1), (-5.0, 15.0, 0.9), (4.0, 19.0, 1.3), (-0.5, 22.0, 1.6), (6.5, 10.0, 0.6))):
        top = Vector((x, 0, z)) + SUNDIR * (13.0 / SUNDIR.y)
        tube(f"shaft{k}", [(x, 0, z), tuple(top)], w, SH, res=2, bres=4).visible_shadow = False
    fill = lib.light("AREA", T(1.5, 2.6, -2.5), 160, (1.0, 0.82, 0.55), 3); lib.look_at(fill, T(0, 1.2, 4))
    green = lib.light("AREA", T(-3, 5, 12), 400, (0.55, 0.9, 0.5), 8); lib.look_at(green, T(0, 1, 4))
    return {}
