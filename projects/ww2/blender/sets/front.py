# The war montage (shots 2-4) at dusk, sets.ts buildFront layout: muddy field, tanks at (-6,10) (4,16) (-14,24) (10,30)
# (-2,40) pointing at the camera (-z), ruins at z 70..82 (x -40..44), fires among them, the sea from x 60 with three
# warships at (120,60) (175,130) (95,175). Bombers and the far flash are exported effect cards.
# The soldiers walk at x -1..2, z 4..10 on flat ground (y 0); the terrain is kept flat there and under the tanks.
# Sun low in the +z sky (slightly +x) so the ruins and ships are rim-lit against the sunset; fires and a warm bounce fill
# light the faces turned to the camera.
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import (lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, flame, flame_mat, smoke_mat, smoke_column, text)
from sets.warroom import barbed_coil

def bx(name, c, s, m, bev=0.01, yaw=0.0): return lib.box(name, T(*c), TS(*s), m, bev, rot=(0, 0, yaw))
def cy(name, c, r, h, m, verts=20, rot=(0, 0, 0), bev=0.005): return lib.cyl(name, T(*c), r, h, m, verts, rot, bev)
SUN = Vector((0.33, 0.085, 1.0)).normalized()          # three-space direction towards the sun

def boxes(name, items, mat, bev=0.0):
    """many boxes merged into one mesh: items = (centre, size, yaw[, tilt]) in three coords"""
    vs, fs = [], []
    for it in items:
        c, s, yaw = it[0], it[1], it[2]; tilt = it[3] if len(it) > 3 else 0.0
        R = Matrix.Rotation(yaw, 3, "Y") @ Matrix.Rotation(tilt, 3, "Z"); b = len(vs)
        for dx in (-0.5, 0.5):
            for dy in (-0.5, 0.5):
                for dz in (-0.5, 0.5): vs.append(tuple(Vector(c) + R @ Vector((dx * s[0], dy * s[1], dz * s[2]))))
        fs += [(b, b + 1, b + 3, b + 2), (b + 4, b + 6, b + 7, b + 5), (b, b + 4, b + 5, b + 1), (b + 2, b + 3, b + 7, b + 6), (b, b + 2, b + 6, b + 4), (b + 1, b + 5, b + 7, b + 3)]
    o = mesh_obj(name, vs, fs, mat)
    if bev:
        md = o.modifiers.new("b", "BEVEL"); md.width = bev; md.segments = 1; md.limit_method = "ANGLE"
    return o

# ------------------------------------------------------------------ sky
def dusk_sky(world):
    nt = world.node_tree; n = nt.nodes; l = nt.links; bg = n["Background"]
    co = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(co.outputs["Generated"], sep.inputs[0])
    sd = T(*SUN).normalized()
    mr = n.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.08; mr.inputs["From Max"].default_value = 0.85; l.new(sep.outputs["Z"], mr.inputs["Value"])
    rmp = n.new("ShaderNodeValToRGB"); l.new(mr.outputs["Result"], rmp.inputs["Fac"]); e = rmp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.14, 0.045, 0.03, 1)
    for p, c in ((0.08, (0.95, 0.34, 0.06)), (0.13, (0.8, 0.2, 0.07)), (0.22, (0.45, 0.08, 0.13)), (0.4, (0.13, 0.04, 0.16))): el = e.new(p); el.color = (*c, 1)
    e[-1].position, e[-1].color = 1.0, (0.02, 0.02, 0.07, 1)
    # sun glow + disc
    dot = n.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; l.new(co.outputs["Generated"], dot.inputs[0]); dot.inputs[1].default_value = tuple(sd)
    mx0 = n.new("ShaderNodeMath"); mx0.operation = "MAXIMUM"; mx0.inputs[1].default_value = 0.0; l.new(dot.outputs["Value"], mx0.inputs[0])
    def pw(e_):
        p = n.new("ShaderNodeMath"); p.operation = "POWER"; p.inputs[1].default_value = e_; l.new(mx0.outputs[0], p.inputs[0]); return p
    g1, g2, disc = pw(10), pw(80), pw(3000)
    gs = n.new("ShaderNodeMath"); gs.operation = "MULTIPLY"; gs.inputs[1].default_value = 0.35; l.new(g1.outputs[0], gs.inputs[0]); g1 = gs
    glow = n.new("ShaderNodeMath"); glow.operation = "MULTIPLY_ADD"; glow.inputs[1].default_value = 0.8; l.new(g1.outputs[0], glow.inputs[0]); l.new(g2.outputs[0], glow.inputs[2])
    add1 = n.new("ShaderNodeMix"); add1.data_type = "RGBA"; add1.blend_type = "ADD"; l.new(glow.outputs[0], add1.inputs[0]); l.new(rmp.outputs["Color"], add1.inputs[6]); add1.inputs[7].default_value = (1.0, 0.45, 0.1, 1)
    # clouds: noise projected on a cloud plane, banded above the horizon, undersides lit orange near the sun
    zp = n.new("ShaderNodeMath"); zp.operation = "ADD"; zp.inputs[1].default_value = 0.12; l.new(sep.outputs["Z"], zp.inputs[0])
    px = n.new("ShaderNodeMath"); px.operation = "DIVIDE"; l.new(sep.outputs["X"], px.inputs[0]); l.new(zp.outputs[0], px.inputs[1])
    py = n.new("ShaderNodeMath"); py.operation = "DIVIDE"; l.new(sep.outputs["Y"], py.inputs[0]); l.new(zp.outputs[0], py.inputs[1])
    cmb = n.new("ShaderNodeCombineXYZ"); l.new(px.outputs[0], cmb.inputs[0]); l.new(py.outputs[0], cmb.inputs[1])
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.5, 1.6, 1.0); l.new(cmb.outputs[0], mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.9; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.62; l.new(mp.outputs[0], nz.inputs["Vector"])
    cov = n.new("ShaderNodeValToRGB"); l.new(nz.outputs["Fac"], cov.inputs["Fac"]); cov.color_ramp.elements[0].position = 0.44; cov.color_ramp.elements[1].position = 0.62
    band = n.new("ShaderNodeMapRange"); band.inputs["From Min"].default_value = 0.015; band.inputs["From Max"].default_value = 0.09; l.new(sep.outputs["Z"], band.inputs["Value"])
    fade = n.new("ShaderNodeMapRange"); fade.inputs["From Min"].default_value = 0.75; fade.inputs["From Max"].default_value = 0.35; l.new(sep.outputs["Z"], fade.inputs["Value"])
    m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; l.new(cov.outputs["Color"], m1.inputs[0]); l.new(band.outputs["Result"], m1.inputs[1])
    m2 = n.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; l.new(m1.outputs[0], m2.inputs[0]); l.new(fade.outputs["Result"], m2.inputs[1])
    m3 = n.new("ShaderNodeMath"); m3.operation = "MULTIPLY"; m3.inputs[1].default_value = 0.92; l.new(m2.outputs[0], m3.inputs[0])
    lit = n.new("ShaderNodeMath"); lit.operation = "POWER"; lit.inputs[1].default_value = 2.0; l.new(mx0.outputs[0], lit.inputs[0])
    ccol = n.new("ShaderNodeMix"); ccol.data_type = "RGBA"; l.new(lit.outputs[0], ccol.inputs[0]); ccol.inputs[6].default_value = (0.06, 0.022, 0.045, 1); ccol.inputs[7].default_value = (1.2, 0.36, 0.06, 1)
    # rim of the clouds catches the light: brighter where the noise is thin
    mixc = n.new("ShaderNodeMix"); mixc.data_type = "RGBA"; l.new(m3.outputs[0], mixc.inputs[0]); l.new(add1.outputs[2], mixc.inputs[6]); l.new(ccol.outputs[2], mixc.inputs[7])
    sun = n.new("ShaderNodeMix"); sun.data_type = "RGBA"; sun.blend_type = "ADD"; l.new(disc.outputs[0], sun.inputs[0]); l.new(mixc.outputs[2], sun.inputs[6]); sun.inputs[7].default_value = (40.0, 26.0, 12.0, 1)
    l.new(sun.outputs[2], bg.inputs[0]); bg.inputs[1].default_value = 1.0

# ------------------------------------------------------------------ terrain
CRATERS = []
TANKS = [(-6, 10, 0.4), (4, 16, -0.3), (-14, 24, 0.2), (10, 30, 0.6), (-2, 40, 0.0)]
def smooth(a, b, x): t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def flat_mask(x, z):
    d = max(0.0, abs(x - 0.5) - 4.5) + max(0.0, abs(z - 5) - 10)            # soldiers' lane
    m = smooth(0.0, 4.0, d)
    for tx, tz, _ in TANKS: m = min(m, smooth(4.0, 7.0, math.hypot(x - tx, z - tz)))
    if z > 60: m = min(m, smooth(68, 60, z) + 0.2)                            # streets of the town
    return m
def H(x, z):
    h = 0.45 * noise.noise(Vector((x * 0.045, z * 0.045, 0.3))) + 0.12 * noise.noise(Vector((x * 0.25, z * 0.25, 1.7)))
    for cx, cz, r, dp in CRATERS:
        d = math.hypot(x - cx, z - cz)
        if d < r * 1.8: h += -dp * max(0.0, 1 - (d / r) ** 2) + dp * 0.4 * math.exp(-((d - r) / (0.3 * r)) ** 2)
    for tx, tz, yw in TANKS:                                                   # ruts behind every tank
        if z > tz + 2:
            for sd in (-1.25, 1.25):
                if abs(x - (tx + sd)) < 0.45: h -= 0.07 * (1 - abs(x - (tx + sd)) / 0.45)
    h *= flat_mask(x, z)
    h -= 2.2 * smooth(50, 66, x)                                               # the shore falls into the sea
    return h
def scorch(x, z):
    s = 0.0
    for cx, cz, r, dp in CRATERS: s = max(s, 1 - min(1.0, math.hypot(x - cx, z - cz) / (r * 1.9)))
    return s
def terrain():
    x0, x1, z0, z1, st = -130, 74, -30, 210, 0.6
    nx, nz = int((x1 - x0) / st) + 1, int((z1 - z0) / st) + 1
    vs, fs = [], []
    for j in range(nz):
        for i in range(nx):
            x, z = x0 + i * st, z0 + j * st; vs.append(T(x, H(x, z), z))
    for j in range(nz - 1):
        for i in range(nx - 1):
            a = j * nx + i; fs.append((a, a + 1, a + nx + 1, a + nx))
    me = bpy.data.meshes.new("ground"); me.from_pydata(vs, [], fs); me.update()
    for p in me.polygons: p.use_smooth = True
    ca = me.color_attributes.new("scorch", "FLOAT_COLOR", "POINT")
    for k, v in enumerate(vs):
        s = scorch(-v.x, v.y); ca.data[k].color = (s, s, s, 1)
    o = link(bpy.data.objects.new("ground", me))
    # muddy field: wet dark mud, drier clay, dead-grass patches, scorched crater rings, fine clods
    m = lib.principled("mud", lib.hexc("#4a3a2a"), 0.8); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); big = n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 0.06; big.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], big.inputs["Vector"])
    r = lib.ramp(n, l, big.outputs["Fac"], [(0.3, lib.hexc("#2a1e14")), (0.45, lib.hexc("#4a3424")), (0.55, lib.hexc("#6a5034")), (0.66, lib.hexc("#6a6634")), (0.78, lib.hexc("#857a46"))])
    fine = n.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 2.5; fine.inputs["Detail"].default_value = 10; l.new(tc.outputs["Object"], fine.inputs["Vector"])
    mul = n.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 0.45; l.new(r.outputs["Color"], mul.inputs[6]); l.new(fine.outputs["Color"], mul.inputs[7])
    at = n.new("ShaderNodeAttribute"); at.attribute_name = "scorch"
    sc = n.new("ShaderNodeMix"); sc.data_type = "RGBA"; l.new(at.outputs["Fac"], sc.inputs[0]); l.new(mul.outputs[2], sc.inputs[6]); sc.inputs[7].default_value = (0.03, 0.025, 0.022, 1)
    l.new(sc.outputs[2], b.inputs["Base Color"])
    wet = lib.ramp(n, l, big.outputs["Fac"], [(0.32, (0.25, 0.25, 0.25)), (0.42, (0.85, 0.85, 0.85))], (-200, -300)); l.new(wet.outputs["Color"], b.inputs["Roughness"])
    vo = n.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 6; l.new(tc.outputs["Object"], vo.inputs["Vector"])
    hb = n.new("ShaderNodeMath"); hb.operation = "MULTIPLY_ADD"; hb.inputs[1].default_value = 0.4; l.new(fine.outputs["Fac"], hb.inputs[0]); l.new(vo.outputs["Distance"], hb.inputs[2])
    mid = n.new("ShaderNodeTexNoise"); mid.inputs["Scale"].default_value = 0.5; mid.inputs["Detail"].default_value = 4; l.new(tc.outputs["Object"], mid.inputs["Vector"])
    mm = n.new("ShaderNodeMix"); mm.data_type = "RGBA"; mm.blend_type = "MULTIPLY"; mm.inputs[0].default_value = 0.5; l.new(sc.outputs[2], mm.inputs[6]); l.new(mid.outputs["Color"], mm.inputs[7])
    l.new(mm.outputs[2], b.inputs["Base Color"])
    lib.bump(n, l, hb.outputs[0], 1.0, 0.1)
    me.materials.append(m)
    return o

# ------------------------------------------------------------------ props
def grass_tuft_src(mat, seed):
    rnd = random.Random(seed); vs, fs = [], []
    for k in range(9):
        a = rnd.random() * math.tau; lean = 0.15 + rnd.random() * 0.35; h = 0.25 + rnd.random() * 0.35; w = 0.025
        bxx, bzz = math.cos(a), math.sin(a); b = len(vs)
        vs += [(-w * bzz, 0, w * bxx), (w * bzz, 0, -w * bxx), (bxx * lean * h, h, bzz * lean * h)]
        fs.append((b, b + 1, b + 2))
    return mesh_obj(f"tuft{seed}", vs, fs, mat)
def scatter(src, name, pts, yaw_rand=True, s=(0.7, 1.4), seed=0):
    rnd = random.Random(seed)
    for k, p in enumerate(pts):
        o = src.copy(); o.name = f"{name}{k}"; link(o); o.location = T(*p)
        o.rotation_euler = (0, 0, rnd.random() * math.tau if yaw_rand else 0); sc = rnd.uniform(*s); o.scale = (sc, sc, sc)
def dead_tree(name, c, h, mat, seed=0):
    rnd = random.Random(seed)
    def branch(p, d, L, r, depth):
        q = p + d * L; mid = p + d * L * 0.5 + Vector((rnd.uniform(-0.15, 0.15), 0, rnd.uniform(-0.15, 0.15))) * L
        tube(f"{name}{depth}_{rnd.randrange(1 << 30)}", [tuple(p), tuple(mid), tuple(q)], r, mat, res=6, bres=1, taper=lambda f: 1 - 0.55 * f)
        if depth == 0: return
        for k in range(2 if depth < 3 else 3):
            nd = (d + Vector((rnd.uniform(-0.9, 0.9), rnd.uniform(-0.1, 0.4), rnd.uniform(-0.9, 0.9)))).normalized()
            branch(q - d * L * rnd.uniform(0.0, 0.3), nd, L * rnd.uniform(0.5, 0.7), r * 0.55, depth - 1)
    branch(Vector(c) + Vector((0, -0.3, 0)), Vector((rnd.uniform(-0.15, 0.15), 1, rnd.uniform(-0.15, 0.15))).normalized(), h * 0.5, h * 0.035, 3)
def hedgehog(name, c, yaw, mat, L=1.9):
    items = []
    for k, (ax, tl) in enumerate(((0.0, 0.62), (math.pi * 2 / 3, 0.62), (math.pi * 4 / 3, 0.62))):
        items.append(((c[0], c[1] + 0.62, c[2]), (L, 0.16, 0.16), yaw + ax, tl))
    boxes(name, items, mat, 0.02)
def oil_drum(name, c, mat, lying=False, yaw=0.0):
    prof = [(0.0, 0.0), (0.29, 0.0), (0.3, 0.02), (0.3, 0.28), (0.31, 0.3), (0.3, 0.32), (0.3, 0.58), (0.31, 0.6), (0.3, 0.62), (0.3, 0.86), (0.29, 0.88), (0.0, 0.88)]
    tilt = Matrix.Rotation(math.radians(90), 3, "Z") if lying else None
    return lathe(name, prof, (c[0], c[1] + (0.3 if lying else 0), c[2]), mat, 24, yaw=yaw, tilt=tilt)
def crate(name, c, yaw, label="7.5cm", mat=None):
    mat = mat or wood_mat("fcrate", "#7a6a42", "#4a3a22", 10, 0.7)
    bx(f"{name}", (c[0], c[1] + 0.22, c[2]), (1.0, 0.44, 0.5), mat, 0.02, yaw)
    for sd in (-0.42, 0.42): bx(f"{name}b{sd}", (c[0] + sd * math.cos(yaw), c[1] + 0.22, c[2] - sd * math.sin(yaw)), (0.06, 0.46, 0.52), wood_mat("fcrate2", "#5a4a2a", "#3a2a14", 10, 0.7), 0.01, yaw)
    text(label, (c[0] - 0.26 * math.sin(yaw), c[1] + 0.25, c[2] - 0.26 * math.cos(yaw)), 0.11, pmat("fstencil", "#e8e0c8", 0.8), yaw=yaw, flat=False)
def sandbag_wall(name, c, yaw, n, rows, mat, seed=0):
    rnd = random.Random(seed); cw, sw = math.cos(yaw), math.sin(yaw)
    for r in range(rows):
        for k in range(n - (r % 2)):
            lx = (k - (n - 1) / 2 + (0.5 if r % 2 else 0)) * 0.62
            o = lib.box(f"{name}{r}_{k}", T(c[0] + lx * cw, c[1] + 0.12 + r * 0.22, c[2] - lx * sw), (0.6, 0.36, 0.24), mat, 0.09)
            o.modifiers["b"].segments = 4; o.modifiers["b"].limit_method = "NONE"
            o.rotation_euler = (rnd.uniform(-0.04, 0.04), rnd.uniform(-0.05, 0.05), yaw + rnd.uniform(-0.12, 0.12))
def sandmat():
    m = lib.principled("fsand", lib.hexc("#8a7650"), 0.95); t, n, l = lib.nodes(m)
    tc = n.new("ShaderNodeTexCoord"); br = n.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 60; br.inputs["Mortar Size"].default_value = 0.1
    br.inputs["Color1"].default_value = (*lib.hexc("#8a7650"), 1); br.inputs["Color2"].default_value = (*lib.hexc("#7a6644"), 1); br.inputs["Mortar"].default_value = (*lib.hexc("#5a4a30"), 1)
    l.new(tc.outputs["Object"], br.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 0.5; l.new(br.outputs["Color"], mx.inputs[6]); l.new(nz.outputs["Color"], mx.inputs[7])
    l.new(mx.outputs[2], n["Principled BSDF"].inputs["Base Color"]); lib.bump(n, l, br.outputs["Fac"], 0.3, 0.01)
    return m
def pole(name, c, h, mat, lean=0.0, yaw=0.0):
    top = (c[0] + math.sin(lean) * h * math.cos(yaw), c[1] + h * math.cos(lean), c[2] + math.sin(lean) * h * math.sin(yaw))
    tube(f"{name}", [c, top], 0.12, mat, res=2, bres=2, taper=lambda f: 1 - 0.3 * f)
    bx(f"{name}x", (top[0], top[1] - 0.4, top[2]), (1.6, 0.12, 0.12), mat, 0.01)
    for sd in (-0.65, 0.65, -0.3, 0.3): cy(f"{name}i{sd}", (top[0] + sd, top[1] - 0.28, top[2]), 0.04, 0.14, pmat("finsul", "#d8e0d0", 0.2), 10)
    return top
def cart_wheel(name, c, r, mat, yaw=0.0, tilt=0.3):
    rot = Matrix.Rotation(yaw, 3, "Y") @ Matrix.Rotation(math.pi / 2 - tilt, 3, "X")
    lathe(f"{name}rim", [(r * 0.86, -0.04), (r, -0.04), (r, 0.04), (r * 0.86, 0.04), (r * 0.86, -0.04)], c, mat, 32, cap=False, tilt=rot)
    lathe(f"{name}hub", [(0.0, -0.1), (0.1, -0.1), (0.12, 0.0), (0.1, 0.1), (0.0, 0.1)], c, mat, 16, tilt=rot)
    for k in range(10):
        a = k / 10 * math.tau; p = rot @ Vector((r * 0.88 * math.cos(a), 0, r * 0.88 * math.sin(a)))
        tube(f"{name}sp{k}", [c, tuple(Vector(c) + p)], 0.022, mat, res=2, bres=1)

def tank(n, x, z, yaw, col="#58603c", burnt=False, tilt=0.0):
    """medium tank in three local coords (nose +x), placed at (x, z) with yaw about the vertical"""
    if burnt:
        hull = mat_once("tankburnt", lambda: worn("tankburnt", "#2a2420", "#6a3a1e", 0.9, 0.3, 8, 0.55, "#141010")); dk = hull
    else:
        hull = mat_once("tank" + col, lambda: worn("tank" + col, col, "#3a3a32", 0.62, 0.25, 7, 0.72, "#4a3a26"))
        dk = mat_once("tankmud", lambda: worn("tankmud", "#3a3226", "#24201a", 0.85, 0.15, 5, 0.6, "#5a4630"))
    steel = mat_once("tanksteel", lambda: worn("tanksteel", "#3a3c36", "#5a5a54", 0.45, 0.6, 30, 0.7))
    c, s = math.cos(yaw), math.sin(yaw); R = Matrix.Rotation(tilt, 3, "X")
    def P(lx, ly, lz):
        v = R @ Vector((lx, ly, lz)); return (x + v.x * c + v.z * s, v.y, z - v.x * s + v.z * c)
    def B(nm, lc, sz, m, bev=0.04): bx(f"{n}{nm}", P(*lc), sz, m, bev, yaw)
    # hull: lower tub, sloped glacis (mesh), engine deck, fenders
    B("hull", (-0.3, 1.05, 0), (5.2, 0.9, 2.3), hull, 0.08)
    gl = [(1.9, 0.6, -1.15), (1.9, 0.6, 1.15), (3.0, 0.75, -1.1), (3.0, 0.75, 1.1), (1.9, 1.55, -1.15), (1.9, 1.55, 1.15), (2.6, 1.55, -1.1), (2.6, 1.55, 1.1)]
    mesh_obj(f"{n}glacis", [P(*v) for v in gl], [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)], hull)
    B("deck", (-1.6, 1.55, 0), (2.4, 0.1, 2.0), hull, 0.03)
    for k in range(5): B(f"grill{k}", (-2.6 + k * 0.28, 1.61, 0), (0.12, 0.03, 1.4), dk, 0.01)
    for sd in (-1, 1):
        B(f"trk{sd}", (0, 0.55, sd * 1.3), (6.1, 1.05, 0.62), dk, 0.38)
        B(f"fend{sd}", (0.1, 1.12, sd * 1.32), (6.0, 0.06, 0.72), hull, 0.02)
        for k in range(6):
            o = cy(f"{n}wh{sd}{k}", P(-2.35 + k * 0.94, 0.45, sd * 1.64), 0.36, 0.14, steel, 20); o.rotation_euler = (math.radians(90) + tilt * 0, 0, yaw)
            o = cy(f"{n}hub{sd}{k}", P(-2.35 + k * 0.94, 0.45, sd * 1.72), 0.12, 0.06, hull, 12); o.rotation_euler = (math.radians(90), 0, yaw)
        o = cy(f"{n}spr{sd}", P(2.85, 0.78, sd * 1.62), 0.32, 0.18, steel, 14); o.rotation_euler = (math.radians(90), 0, yaw)
        for k in range(4): B(f"tool{sd}{k}", (-1.8 + k * 0.9, 1.2, sd * 1.5), (0.7, 0.14, 0.1), wood_mat("ftool", "#6a4a2a", "#3a2614", 12, 0.7) if k % 2 else steel, 0.02)
    # spare track links on the glacis, headlights with guards, tow hooks, MG ball
    for k in range(3): B(f"link{k}", (2.25 + k * 0.03, 1.1 + k * 0.12, -0.5 + k * 0.0), (0.12, 0.08, 0.45), dk, 0.02)
    for sd in (-0.8, 0.8):
        cy(f"{n}hl{sd}", P(2.75, 1.0, sd), 0.1, 0.12, steel, 12)
        B(f"hook{sd}", (3.05, 0.6, sd * 0.5), (0.2, 0.12, 0.08), steel, 0.02)
    lathe(f"{n}ball", [(0.0, -0.15), (0.14, -0.1), (0.15, 0.0), (0.14, 0.1), (0.0, 0.15)], P(2.3, 1.25, 0.55), hull, 16)
    # cast turret, mantlet, gun with muzzle brake, cupola, MG, antenna, stowage
    tp = [(0.0, 0.0), (1.2, 0.0), (1.25, 0.15), (1.18, 0.45), (1.0, 0.7), (0.6, 0.82), (0.0, 0.85)]
    tu = lathe(f"{n}tur", tp, P(-0.35, 1.6, 0), hull, 40, yaw=yaw, sx=1.05, sz=0.9, tilt=None)
    B("mant", (0.85, 2.0, 0), (0.35, 0.55, 0.9), hull, 0.08)
    gun = tube(f"{n}gun", [P(0.9, 2.0, 0), P(2.4, 2.0, 0), P(4.1, 2.02, 0)], 0.085, steel, res=2, bres=2)
    cy(f"{n}mbz", P(4.15, 2.02, 0), 0.13, 0.32, steel, 12, rot=(0, math.radians(90), yaw + math.pi))
    lathe(f"{n}cup", [(0.0, 0.0), (0.34, 0.0), (0.34, 0.22), (0.28, 0.26), (0.0, 0.26)], P(-0.7, 2.4, 0.42), hull, 20)
    lathe(f"{n}hatch", [(0.0, 0.0), (0.3, 0.0), (0.3, 0.05), (0.0, 0.07)], P(-0.95, 2.66, 0.75), hull, 20, tilt=Matrix.Rotation(math.radians(70), 3, "X"))
    tube(f"{n}mg", [P(-0.5, 2.85, 0.2), P(0.6, 2.85, 0.25)], 0.035, steel, res=2, bres=1)
    cy(f"{n}mgp", P(-0.6, 2.7, 0.2), 0.03, 0.3, steel, 8)
    tube(f"{n}ant", [P(-1.1, 2.35, -0.6), P(-1.3, 3.6, -0.65), P(-1.7, 4.6, -0.7)], 0.012, steel, res=4, bres=0)
    canvas = mat_once("fcanvas", lambda: lib.cloth("fcanvas", "#7a7050")); roll = mat_once("froll", lambda: lib.cloth("froll", "#5a5038"))
    for k, (lz, m_) in enumerate(((-0.55, canvas), (0.0, roll), (0.55, canvas))):
        o = cy(f"{n}bed{k}", P(-1.55, 2.0, lz), 0.17, 0.5, m_, 14); o.rotation_euler = (0, math.radians(90), yaw)
    for k in range(3): B(f"can{k}", (-2.85, 1.45, -0.7 + k * 0.42), (0.18, 0.45, 0.34), mat_once("fjerry", lambda: worn("fjerry", "#4a5236", "#2a2a22", 0.6, 0.3, 20, 0.6)), 0.03)
    # white star and number
    wpaint = pmat("fwhite", "#e8e2d0", 0.7)
    for sd in (-1, 1):
        star = []
        for k in range(10):
            a = k / 10 * math.tau + math.pi / 2; rr = 0.42 if k % 2 == 0 else 0.17
            star.append(P(-0.6 + rr * math.cos(a), 1.08 + rr * math.sin(a), sd * 1.168))
        star.append(P(-0.6, 1.08, sd * 1.168))
        mesh_obj(f"{n}star{sd}", star, [(k, (k + 1) % 10, 10) for k in range(10)], wpaint)
    return tu

def ruin_mat(name, plaster, brick="#8a4632"):
    """plaster facade with blown-off patches showing brick, soot and grime"""
    m = lib.principled(name, lib.hexc(plaster), 0.85); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); br = n.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 1.6
    br.inputs["Color1"].default_value = (*lib.hexc(brick), 1); br.inputs["Color2"].default_value = (*lib.hexc("#6a3424"), 1); br.inputs["Mortar"].default_value = (*lib.hexc("#4a4038"), 1)
    br.inputs["Mortar Size"].default_value = 0.02; l.new(tc.outputs["Object"], br.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.25; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.7; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    mask = lib.ramp(n, l, nz.outputs["Fac"], [(0.56, (0, 0, 0)), (0.6, (1, 1, 1))])
    pn = n.new("ShaderNodeTexNoise"); pn.inputs["Scale"].default_value = 1.5; pn.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], pn.inputs["Vector"])
    pc = lib.ramp(n, l, pn.outputs["Fac"], [(0.3, tuple(c * 0.6 for c in lib.hexc(plaster))), (0.7, lib.hexc(plaster))], (-200, 200))
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(mask.outputs["Color"], mx.inputs[0]); l.new(pc.outputs["Color"], mx.inputs[6]); l.new(br.outputs["Color"], mx.inputs[7])
    geo = n.new("ShaderNodeNewGeometry"); sz = n.new("ShaderNodeSeparateXYZ"); l.new(geo.outputs["Position"], sz.inputs[0])
    soot = n.new("ShaderNodeMapRange"); soot.inputs["From Min"].default_value = 6; soot.inputs["From Max"].default_value = 18; l.new(sz.outputs["Z"], soot.inputs["Value"])
    sn = n.new("ShaderNodeMath"); sn.operation = "MULTIPLY"; l.new(soot.outputs["Result"], sn.inputs[0]); l.new(pn.outputs["Fac"], sn.inputs[1])
    sm = n.new("ShaderNodeMix"); sm.data_type = "RGBA"; l.new(sn.outputs[0], sm.inputs[0]); l.new(mx.outputs[2], sm.inputs[6]); sm.inputs[7].default_value = (0.04, 0.035, 0.03, 1)
    l.new(sm.outputs[2], b.inputs["Base Color"])
    hh = n.new("ShaderNodeMath"); hh.operation = "MULTIPLY_ADD"; hh.inputs[1].default_value = 0.5; l.new(mask.outputs["Color"], hh.inputs[0]); l.new(br.outputs["Fac"], hh.inputs[2])
    lib.bump(n, l, hh.outputs[0], 0.5, 0.03)
    return m
def ruin_building(name, x, z, w, floors, mat, seed, depth=8.0, sign=None, fires=()):
    """a gutted multi-storey town house: front facade with window grid, jagged broken top, side walls, floor slabs and
    beams poking out, interiors glowing where fire still burns; front faces three -z"""
    rnd = random.Random(seed); fh = 3.4; H0 = floors * fh + 1.0; nwin = max(2, int(w / 2.6)); pitch = w / nwin
    jag = [H0 * rnd.uniform(0.45, 1.0) for _ in range(nwin + 1)]
    def top(lx):
        f = (lx + w / 2) / w * nwin; i = min(nwin - 1, int(f)); u = f - i; return jag[i] * (1 - u) + jag[i + 1] * u
    items = []
    def add(lx, ly0, ly1, lz, sw, dpt=0.55):
        tp = min(ly1, top(lx))
        if tp - ly0 > 0.15: items.append(((x + lx, (ly0 + tp) / 2, z + lz), (sw, tp - ly0, dpt), 0.0))
    add(0, 0, 1.0, 0, w, 0.7)                                                 # plinth
    for f in range(floors):
        y0 = 1.0 + f * fh
        for k in range(nwin + 1): add(-w / 2 + k * pitch, y0, y0 + fh, 0, 0.9 if k in (0, nwin) else 0.75)
        for k in range(nwin):
            cx = -w / 2 + (k + 0.5) * pitch
            add(cx, y0, y0 + 0.95, 0, pitch - 0.7); add(cx, y0 + fh - 0.75, y0 + fh, 0, pitch - 0.7)
            if rnd.random() < 0.5: add(cx, y0 + 0.95, y0 + 1.05, -0.3, pitch - 0.5, 0.25)        # sill
        add(0, y0 + fh - 0.3, y0 + fh, -0.18, w + 0.3, 0.3)                    # cornice band
    for sd in (-1, 1):                                                        # side walls, broken back
        for k in range(4):
            d = (k + 0.5) * depth / 4; hh = H0 * rnd.uniform(0.25, 0.95) * (1 - k * 0.15)
            items.append(((x + sd * w / 2, hh / 2, z + d), (0.55, hh, depth / 4), 0.0))
    for f in range(1, floors):                                                # floor slabs hanging out of the shell
        y0 = 1.0 + f * fh
        if rnd.random() < 0.7: items.append(((x + rnd.uniform(-w * 0.2, w * 0.2), y0 - 0.1, z + depth * 0.4), (w * rnd.uniform(0.4, 0.8), 0.25, depth * 0.6), 0.0, rnd.uniform(-0.25, 0.25)))
    o = boxes(name, items, mat, 0.04)
    beams = wood_mat("fbeam", "#2a1c14", "#100a08", 6, 0.9)
    for k in range(rnd.randint(2, 4)):
        lx = rnd.uniform(-w / 2, w / 2); y0 = min(top(lx), H0) - rnd.uniform(0.5, 2.5)
        bx(f"{name}bm{k}", (x + lx, y0, z + 1.5), (0.22, 0.22, 4.0), beams, 0.01, rnd.uniform(-0.3, 0.3))
    # interior glow behind some windows (fire inside), black interior elsewhere
    glow = mat_once("fglowwin", lambda: lib.emit("fglowwin", (1.0, 0.2, 0.02), 0.6))
    dark = mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0))
    for f in range(floors):
        for k in range(nwin):
            cx = -w / 2 + (k + 0.5) * pitch; y0 = 1.0 + f * fh + 0.95
            if y0 + 1.6 > top(cx): continue
            if (f, k) in fires or rnd.random() < 0.12: bx(f"{name}g{f}{k}", (x + cx, y0 + 0.9, z + 1.4), (pitch - 0.6, fh - 1.6, 0.05), glow, 0)
            elif rnd.random() < 0.5: bx(f"{name}d{f}{k}", (x + cx, y0 + 0.9, z + 2.5), (pitch - 0.4, fh - 1.4, 0.05), dark, 0)
    if sign:
        txt, col = sign
        bx(f"{name}sg", (x, 4.2, z - 0.42), (min(w * 0.7, 0.6 * len(txt) + 1.0), 0.8, 0.12), pmat("fsign" + col, col, 0.6), 0.02, rnd.uniform(-0.04, 0.04))
        text(txt, (x, 3.95, z - 0.5), 0.55, pmat("fsigntxt", "#efe2b8", 0.5), flat=False)
    return o
def church(name, x, z, mat):
    items = [((x, 12, z), (5.5, 24, 5.5), 0.0)]
    o = boxes(name, items, mat, 0.05)
    dark = mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0))
    for sd in (-1, 1):
        bx(f"{name}bel{sd}", (x + sd * 1.0, 19.5, z - 2.76), (1.0, 3.2, 0.1), dark, 0)
    bx(f"{name}clk", (x, 15.0, z - 2.8), (1.8, 1.8, 0.05), pmat("fclock", "#e8dcc0", 0.6), 0)
    cy(f"{name}clkf", (x, 15.0, z - 2.82), 0.85, 0.04, pmat("fclockf", "#d8c8a0", 0.6), 24, rot=(math.radians(90), 0, 0))
    roof = mat_once("froof", lambda: worn("froof", "#3a5a4a", "#1a1a18", 0.6, 0.6, 3, 0.62, "#2a3a2a"))
    lathe(f"{name}sp", [(3.6, 0.0), (0.0, 9.0)], (x, 24, z), roof, 4, yaw=math.pi / 4, cap=True, tilt=Matrix.Rotation(0.18, 3, "X") @ Matrix.Rotation(0.1, 3, "Z"))
    for k in range(5): bx(f"{name}raft{k}", (x - 1.5 + k * 0.7, 25.5 + (k % 2), z - 1.0), (0.14, 3.0, 0.14), wood_mat("fbeam", "#2a1c14", "#100a08", 6, 0.9), 0.01, 0.3 * (k - 2))
    return o

def _ss(a, b, x): return smooth(a, b, x) if a < b else 1.0 - smooth(b, a, x)
def loft(name, rings, mat, cap0=True, cap1=True, uvs=None, smooth_=True):
    """skin consecutive rings (equal point counts, three coords) into one mesh; optional per-vertex uvs"""
    R = len(rings[0]); vs = [v for r in rings for v in r]; fs = []
    for i in range(len(rings) - 1):
        for k in range(R - 1): a = i * R + k; fs.append((a, a + R, a + R + 1, a + 1))
    if cap0: fs.append(tuple(range(R))[::-1])
    if cap1: fs.append(tuple(range((len(rings) - 1) * R, len(rings) * R)))
    o = mesh_obj(name, vs, fs, mat, smooth=smooth_)
    if uvs:
        uv = o.data.uv_layers.new()
        for p in o.data.polygons:
            for li in p.loop_indices: uv.data[li].uv = uvs[o.data.loops[li].vertex_index]
    return o
def hull_mat(name, L):
    """naval grey plating (UV = metres along hull, height): plate seams, two rows of portholes amidships, rust and
    grime streaks running down, black boot-top at the waterline, red antifouling below"""
    m = lib.principled(name, lib.hexc("#6c7682"), 0.55, 0.15); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["UV"], sep.inputs[0])
    br = n.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 1.0; br.inputs["Brick Width"].default_value = 7.0; br.inputs["Row Height"].default_value = 1.3
    br.inputs["Mortar Size"].default_value = 0.035; br.inputs["Color1"].default_value = (*lib.hexc("#6c7682"), 1); br.inputs["Color2"].default_value = (*lib.hexc("#646e7a"), 1)
    br.inputs["Mortar"].default_value = (*lib.hexc("#4a525c"), 1); l.new(tc.outputs["UV"], br.inputs["Vector"])
    # grime streaks: noise stretched vertically, stronger just under the deck edge and under the portholes
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.4, 0.07, 1.0); l.new(tc.outputs["UV"], mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 8; l.new(mp.outputs[0], nz.inputs["Vector"])
    st = lib.ramp(n, l, nz.outputs["Fac"], [(0.45, (0, 0, 0)), (0.75, (1, 1, 1))])
    sm = n.new("ShaderNodeMix"); sm.data_type = "RGBA"; l.new(st.outputs["Color"], sm.inputs[0]); l.new(br.outputs["Color"], sm.inputs[6]); sm.inputs[7].default_value = (*lib.hexc("#3e3a36"), 1)
    nr = n.new("ShaderNodeTexNoise"); nr.inputs["Scale"].default_value = 2.5; nr.inputs["Detail"].default_value = 6; l.new(mp.outputs[0], nr.inputs["Vector"])
    rs = lib.ramp(n, l, nr.outputs["Fac"], [(0.6, (0, 0, 0)), (0.72, (1, 1, 1))], (-200, 200))
    rm = n.new("ShaderNodeMix"); rm.data_type = "RGBA"; l.new(rs.outputs["Color"], rm.inputs[0]); l.new(sm.outputs[2], rm.inputs[6]); rm.inputs[7].default_value = (*lib.hexc("#6a4632"), 1)
    # portholes: two rows (y 1.7 and 2.8) every 1.8 m between -0.33 L and 0.36 L
    holes = []
    for row in (1.7, 2.8):
        fu = n.new("ShaderNodeMath"); fu.operation = "WRAP"; fu.inputs[1].default_value = 0.9; fu.inputs[2].default_value = -0.9; l.new(sep.outputs["X"], fu.inputs[0])
        dy = n.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = row; l.new(sep.outputs["Y"], dy.inputs[0])
        cmb = n.new("ShaderNodeCombineXYZ"); l.new(fu.outputs[0], cmb.inputs[0]); l.new(dy.outputs[0], cmb.inputs[1])
        ln = n.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; l.new(cmb.outputs[0], ln.inputs[0])
        lt = n.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.2; l.new(ln.outputs["Value"], lt.inputs[0]); holes.append(lt)
    hh = n.new("ShaderNodeMath"); hh.operation = "MAXIMUM"; l.new(holes[0].outputs[0], hh.inputs[0]); l.new(holes[1].outputs[0], hh.inputs[1])
    mid = n.new("ShaderNodeMapRange"); mid.inputs["From Min"].default_value = -0.33 * L; mid.inputs["From Max"].default_value = -0.33 * L + 0.01; l.new(sep.outputs["X"], mid.inputs["Value"])
    mid2 = n.new("ShaderNodeMapRange"); mid2.inputs["From Min"].default_value = 0.36 * L; mid2.inputs["From Max"].default_value = 0.36 * L - 0.01; l.new(sep.outputs["X"], mid2.inputs["Value"])
    mk = n.new("ShaderNodeMath"); mk.operation = "MULTIPLY"; l.new(mid.outputs["Result"], mk.inputs[0]); l.new(mid2.outputs["Result"], mk.inputs[1])
    ph = n.new("ShaderNodeMath"); ph.operation = "MULTIPLY"; l.new(hh.outputs[0], ph.inputs[0]); l.new(mk.outputs[0], ph.inputs[1])
    pm = n.new("ShaderNodeMix"); pm.data_type = "RGBA"; l.new(ph.outputs[0], pm.inputs[0]); l.new(rm.outputs[2], pm.inputs[6]); pm.inputs[7].default_value = (0.015, 0.015, 0.02, 1)
    # boot-top (black, y -0.5..0.6) and antifouling red below
    bt = n.new("ShaderNodeValToRGB"); mr = n.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -4.0; mr.inputs["From Max"].default_value = 2.0; l.new(sep.outputs["Y"], mr.inputs["Value"])
    l.new(mr.outputs["Result"], bt.inputs["Fac"]); e = bt.color_ramp.elements; bt.color_ramp.interpolation = "CONSTANT"
    e[0].position, e[0].color = 0.0, (*lib.hexc("#7a2a22"), 0.0)
    el = e.new((-0.5 + 4) / 6); el.color = (0.03, 0.03, 0.035, 0.0)
    e[-1].position, e[-1].color = (0.6 + 4) / 6, (1, 1, 1, 1)
    bm_ = n.new("ShaderNodeMix"); bm_.data_type = "RGBA"; l.new(bt.outputs["Alpha"], bm_.inputs[0]); l.new(bt.outputs["Color"], bm_.inputs[6]); l.new(pm.outputs[2], bm_.inputs[7])
    l.new(bm_.outputs[2], b.inputs["Base Color"])
    bb = n.new("ShaderNodeMath"); bb.operation = "MULTIPLY_ADD"; bb.inputs[1].default_value = 0.3; l.new(br.outputs["Fac"], bb.inputs[0]); l.new(ph.outputs[0], bb.inputs[2])
    lib.bump(n, l, bb.outputs[0], 0.5, 0.05)
    return m
def deck_mat():
    m = lib.principled("shipteak", lib.hexc("#8a7458"), 0.75); t, n, l = lib.nodes(m)
    tc = n.new("ShaderNodeTexCoord"); br = n.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 1.0; br.inputs["Brick Width"].default_value = 6.0; br.inputs["Row Height"].default_value = 0.16
    br.inputs["Mortar Size"].default_value = 0.012; br.inputs["Color1"].default_value = (*lib.hexc("#8a7458"), 1); br.inputs["Color2"].default_value = (*lib.hexc("#7a6448"), 1); br.inputs["Mortar"].default_value = (*lib.hexc("#2a2420"), 1)
    l.new(tc.outputs["UV"], br.inputs["Vector"]); l.new(br.outputs["Color"], n["Principled BSDF"].inputs["Base Color"]); return m
def ensign_mat():
    """white ensign: red cross on white, dark blue canton (UV)"""
    m = lib.principled("ensign", (1, 1, 1), 0.8); t, n, l = lib.nodes(m)
    tc = n.new("ShaderNodeTexCoord"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["UV"], sp.inputs[0])
    def band(out, c, w):
        d = n.new("ShaderNodeMath"); d.operation = "SUBTRACT"; d.inputs[1].default_value = c; l.new(out, d.inputs[0])
        a = n.new("ShaderNodeMath"); a.operation = "ABSOLUTE"; l.new(d.outputs[0], a.inputs[0])
        lt = n.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = w; l.new(a.outputs[0], lt.inputs[0]); return lt
    cx, cyy = band(sp.outputs["X"], 0.5, 0.06), band(sp.outputs["Y"], 0.5, 0.09)
    cr = n.new("ShaderNodeMath"); cr.operation = "MAXIMUM"; l.new(cx.outputs[0], cr.inputs[0]); l.new(cyy.outputs[0], cr.inputs[1])
    kx = n.new("ShaderNodeMath"); kx.operation = "LESS_THAN"; kx.inputs[1].default_value = 0.42; l.new(sp.outputs["X"], kx.inputs[0])
    ky = n.new("ShaderNodeMath"); ky.operation = "GREATER_THAN"; ky.inputs[1].default_value = 0.5; l.new(sp.outputs["Y"], ky.inputs[0])
    kn = n.new("ShaderNodeMath"); kn.operation = "MULTIPLY"; l.new(kx.outputs[0], kn.inputs[0]); l.new(ky.outputs[0], kn.inputs[1])
    m1 = n.new("ShaderNodeMix"); m1.data_type = "RGBA"; l.new(cr.outputs[0], m1.inputs[0]); m1.inputs[6].default_value = (0.9, 0.88, 0.84, 1); m1.inputs[7].default_value = (0.7, 0.04, 0.04, 1)
    m2 = n.new("ShaderNodeMix"); m2.data_type = "RGBA"; l.new(kn.outputs[0], m2.inputs[0]); l.new(m1.outputs[2], m2.inputs[6]); m2.inputs[7].default_value = (0.03, 0.05, 0.22, 1)
    l.new(m2.outputs[2], n["Principled BSDF"].inputs["Base Color"]); return m
def flag(name, root, w, h, dirv, mat, wave=0.12):
    """a waving flag hung from root (three point) streaming along dirv (three xz unit vector)"""
    NX, NY = 8, 4; vs, uvs = [], []
    for j in range(NY + 1):
        for i in range(NX + 1):
            u, v = i / NX, j / NY
            vs.append((root[0] + dirv[0] * w * u - dirv[1] * wave * w * math.sin(u * 5 + v) * u, root[1] - h * v - 0.15 * h * u * u,
                       root[2] + dirv[1] * w * u + dirv[0] * wave * w * math.sin(u * 5 + v) * u)); uvs.append((u, 1 - v))
    rings = [vs[j * (NX + 1):(j + 1) * (NX + 1)] for j in range(NY + 1)]
    return loft(name, rings, mat, False, False, uvs, smooth_=True)

def warship(n, x, z, yaw, L, Bm, kind="cruiser", train=0.35):
    """WW2 capital ship. Ship-local frame: bow +x, starboard +z, waterline y 0 (sea surface at y -0.25)."""
    c, s = math.cos(yaw), math.sin(yaw)
    P = lambda lx, ly, lz: (x + lx * c + lz * s, ly, z - lx * s + lz * c)
    grey = mat_once("shipgrey", lambda: worn("shipgrey", "#7a8590", "#4a525a", 0.55, 0.2, 0.5, 0.68, "#565e66"))
    grey2 = mat_once("shipgrey2", lambda: worn("shipgrey2", "#68727e", "#3e444c", 0.55, 0.2, 0.5, 0.7, "#4a5058"))
    dk = mat_once("shipdk", lambda: lib.principled("shipdk", lib.hexc("#2c3036"), 0.5, 0.3))
    black = mat_once("shipblack", lambda: lib.principled("shipblack", lib.hexc("#121214"), 0.6))
    canvas = mat_once("shipcanvas", lambda: lib.cloth("shipcanvas", "#b8b098"))
    win = mat_once("shipwin", lambda: lib.principled("shipwin", lib.hexc("#0c0e12"), 0.1, 0.0))
    lit = mat_once("shiplit", lambda: lib.emit("shiplit", (1.0, 0.55, 0.2), 0.8))
    # ---------- hull: lofted cross-sections; flared raked bow, sheer rising forward, curved bilge, narrower stern ----------
    US = [0.0, 0.06, 0.14, 0.24, 0.36, 0.5, 0.64, 0.78, 0.9, 1.0]; NS = 44
    rings, uvs, edge = [], [], []
    for i in range(NS + 1):
        t = i / NS; lx0 = (t - 0.5) * L
        w = Bm / 2 * (0.42 + 0.58 * smooth(0.0, 0.25, t)) * max(0.0, 1 - (max(0.0, t - 0.58) / 0.42) ** 1.7)
        w = max(w, 0.08)
        top = 4.0 + 3.6 * smooth(0.55, 1.0, t) ** 1.4 + 0.5 * smooth(0.15, 0.0, t)
        keel = -3.6 + 3.2 * smooth(0.86, 1.0, t) + 2.6 * smooth(0.1, 0.0, t)
        flare = smooth(0.5, 0.95, t) * min(1.0, (1 - t) * 14)
        side = []
        for u in US:
            y = keel + (top - keel) * u
            g = math.sin(min(1.0, u / 0.34) * math.pi / 2) ** 0.55
            hw = w * g + Bm * 0.08 * flare * max(0.0, (u - 0.5) / 0.5) ** 1.6
            rake = 0.07 * L * smooth(0.86, 1.0, t) * u ** 1.3 - 0.02 * L * smooth(0.06, 0.0, t) * (1 - u)
            side.append((lx0 + rake, y, hw))
        ring = [P(a, y, -hw) for a, y, hw in side[::-1]] + [P(a, y, hw) for a, y, hw in side[1:]]
        rings.append(ring); uvs += [(a, y) for a, y, hw in side[::-1]] + [(a, y) for a, y, hw in side[1:]]
        edge.append(side[-1])
    hull = loft(f"{n}hull", rings, mat_once(f"hull{L}", lambda: hull_mat(f"hull{L}", L)), True, True, uvs)
    # deck (teak planks) and a rubbing strake / deck-edge gutter
    dv = [P(a, y + 0.02, -hw * 0.995) for a, y, hw in edge] + [P(a, y + 0.02, hw * 0.995) for a, y, hw in edge[::-1]]
    duv = [(a, -hw) for a, y, hw in edge] + [(a, hw) for a, y, hw in edge[::-1]]
    d = mesh_obj(f"{n}deck", dv, [tuple(range(len(dv)))], mat_once("shipteak", deck_mat)); uv = d.data.uv_layers.new()
    for p in d.data.polygons:
        for li in p.loop_indices: uv.data[li].uv = duv[d.data.loops[li].vertex_index]
    for sd in (-1, 1):
        tube(f"{n}strake{sd}", [P(a, y - 0.15, sd * (hw + 0.06)) for a, y, hw in edge[1:-1:3]], 0.1, dk, res=3, bres=1)
        tube(f"{n}rail{sd}", [P(a, y + 1.0, sd * hw * 0.98) for a, y, hw in edge[2:-2:3]], 0.04, dk, res=3, bres=0)
    def deck_y(lx):
        t = min(1.0, max(0.0, lx / L + 0.5)); return 4.0 + 3.6 * smooth(0.55, 1.0, t) ** 1.4 + 0.5 * smooth(0.15, 0.0, t)
    def B(nm, lx, ly, lz, sx, sy, sz, m, bev=0.3): bx(f"{n}{nm}", P(lx, ly, lz), (sx, sy, sz), m, bev, yaw)
    # anchors and hawse pipes at the bow
    for sd in (-1, 1):
        ax = 0.4 * L; hwb = Bm / 2 * max(0.08, 1 - ((0.9 - 0.58) / 0.42) ** 1.7)
        lathe(f"{n}hawse{sd}", [(0.0, 0.0), (0.55, 0.0), (0.55, 0.3), (0.0, 0.3)], P(ax, deck_y(ax) - 1.6, sd * (hwb + 0.15)), black, 12, tilt=Matrix.Rotation(math.pi / 2, 3, "X"))
        B(f"anchor{sd}", ax - 0.3, deck_y(ax) - 2.6, sd * (hwb + 0.3), 0.5, 1.6, 0.3, black, 0.08)
    # ---------- layout per class ----------
    if kind == "battleship":
        turrets = [(0.31, 1, 3, 0.0), (0.21, 1, 3, 1.8), (-0.27, -1, 3, 1.8), (-0.37, -1, 3, 0.0)]; funnels = [(-0.02, 2.6, 15.0)]; tsize = 1.25
    elif kind == "destroyer":
        turrets = [(0.3, 1, 2, 0.0), (0.21, 1, 2, 1.4), (-0.33, -1, 2, 0.0)]; funnels = [(0.0, 1.3, 9.5), (-0.1, 1.3, 9.5)]; tsize = 0.75
    else:
        turrets = [(0.3, 1, 2, 0.0), (0.2, 1, 2, 1.6), (-0.33, -1, 2, 0.0)]; funnels = [(0.02, 1.7, 12.0), (-0.1, 1.7, 12.0)]; tsize = 1.0
    sc = tsize
    # ---------- superstructure: deckhouse, bridge tiers with windows, director tower, platforms ----------
    y0 = deck_y(0.0)
    B("house1", -0.06 * L, y0 + 1.4, 0, 0.36 * L, 2.8, Bm * 0.58, grey, 0.35)
    B("house2", 0.06 * L, y0 + 4.0, 0, 0.14 * L, 2.6, Bm * 0.5, grey, 0.3)
    B("bridge1", 0.1 * L, y0 + 6.4, 0, 0.075 * L, 2.3, Bm * 0.44, grey, 0.25)
    B("bridgewg", 0.115 * L, y0 + 7.4, 0, 0.03 * L, 0.25, Bm * 0.78, grey2, 0.05)
    B("bridge2", 0.105 * L, y0 + 8.6, 0, 0.055 * L, 2.0, Bm * 0.34, grey, 0.25)
    B("compass", 0.11 * L, y0 + 10.0, 0, 0.04 * L, 0.8, Bm * 0.3, grey2, 0.15)
    for tier, (lx, yy, wd) in enumerate(((0.1 * L + 0.0375 * L, y0 + 6.7, Bm * 0.44), (0.105 * L + 0.0275 * L, y0 + 8.9, Bm * 0.34))):
        B(f"wband{tier}", lx, yy, 0, 0.12, 0.55, wd * 0.9, win, 0.02)
        for sd in (-1, 1): B(f"wside{tier}{sd}", lx - 0.03 * L, yy, sd * wd / 2, 0.04 * L, 0.5, 0.1, win, 0.02)
        for k in range(5): B(f"wbar{tier}{k}", lx + 0.02, yy, (k - 2) * wd * 0.2, 0.1, 0.6, 0.12, grey2, 0.0)
    for k, (lx, yy, lz) in enumerate(((-0.12 * L, y0 + 1.6, Bm * 0.29), (-0.03 * L, y0 + 1.6, Bm * 0.29), (0.05 * L, y0 + 4.2, Bm * 0.25), (-0.18 * L, y0 + 1.4, -Bm * 0.29), (0.02 * L, y0 + 1.6, -Bm * 0.29))):
        B(f"lit{k}", lx, yy, lz + (0.06 if lz > 0 else -0.06), 0.5, 0.45, 0.05, lit, 0.0)
    # director tower with rangefinder arms on top of the bridge
    dx = 0.1 * L; dy = y0 + 10.4
    lathe(f"{n}dir", [(0.0, 0.0), (1.5 * sc, 0.0), (1.5 * sc, 1.8 * sc), (1.1 * sc, 2.4 * sc), (0.0, 2.5 * sc)], P(dx, dy, 0), grey, 8, yaw=yaw + 0.3)
    B("rf", dx - 0.2, dy + 1.4 * sc, 0, 0.6, 0.5, 5.5 * sc, grey2, 0.1)
    for sd in (-1, 1): cy(f"{n}rfe{sd}", P(dx - 0.2, dy + 1.4 * sc, sd * 2.75 * sc), 0.35, 0.6, grey2, 12, rot=(math.radians(90), 0, yaw))
    # tripod foremast with spotting top, yardarm, topmast; pole mainmast aft
    fx = 0.07 * L; mtop = P(fx, y0 + 22 * sc + 6, 0)
    for k, (ox, oz) in enumerate(((-4.5, -2.4), (-4.5, 2.4), (1.0, 0.0))):
        tube(f"{n}leg{k}", [P(fx + ox, y0 + 2.8, oz), mtop], 0.32, grey2, res=2, bres=1)
    lathe(f"{n}spot", [(0.0, 0.0), (1.8, 0.0), (1.9, 1.5), (1.4, 2.2), (0.0, 2.2)], (mtop[0], mtop[1] - 2.5, mtop[2]), grey, 12)
    tube(f"{n}topm", [mtop, (mtop[0], mtop[1] + 8, mtop[2])], 0.13, dk, res=2, bres=0)
    yard = [P(fx, mtop[1] + 2.5, -Bm * 0.4), P(fx, mtop[1] + 2.5, Bm * 0.4)]; tube(f"{n}yard", yard, 0.1, dk, res=2, bres=0)
    mx = -0.2 * L; mmt = P(mx, y0 + 18 * sc + 2, 0)
    tube(f"{n}mainm", [P(mx, y0 + 2.8, 0), mmt], 0.28, grey2, res=2, bres=1)
    yard2 = [P(mx, mmt[1] - 3, -Bm * 0.3), P(mx, mmt[1] - 3, Bm * 0.3)]; tube(f"{n}yard2", yard2, 0.09, dk, res=2, bres=0)
    # rigging: forestay to the jackstaff, backstay, wireless aerials between the masts, signal halyards with flags
    jack = P(0.5 * L + 0.07 * L, deck_y(0.5 * L) + 3.5, 0); staff = P(-0.5 * L - 0.01 * L, deck_y(-0.5 * L) + 5, 0)
    tube(f"{n}jackst", [P(0.5 * L + 0.065 * L, deck_y(0.5 * L), 0), jack], 0.08, dk, res=2, bres=0)
    tube(f"{n}ensst", [P(-0.5 * L - 0.01 * L, deck_y(-0.5 * L), 0), staff], 0.09, dk, res=2, bres=0)
    rig = mat_once("shiprig", lambda: lib.principled("shiprig", lib.hexc("#1a1c20"), 0.6, 0.5))
    for a_, b_ in ((mtop, jack), ((mtop[0], mtop[1] + 7, mtop[2]), mmt), (mmt, staff), (yard[0], (mmt[0], mmt[1] + 0, mmt[2])), (yard[1], mmt)):
        tube(f"{n}rig{len(bpy.data.objects)}", [a_, ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2 - 0.6, (a_[2] + b_[2]) / 2), b_], 0.05, rig, res=4, bres=0)
    cols = ["#c8202a", "#e8d040", "#1a3a8a", "#f0ece0", "#c8202a", "#1a3a8a"]
    for sd in (0, 1):
        p0 = Vector(yard[sd]); p1 = Vector(P(0.5 * L - 4, deck_y(0.45 * L) + 0.5, (sd * 2 - 1) * 1.5))
        tube(f"{n}hal{sd}", [tuple(p0), tuple(p1)], 0.035, rig, res=2, bres=0)
        for k in range(5):
            q = p0.lerp(p1, 0.12 + k * 0.17)
            flag(f"{n}sig{sd}{k}", tuple(q), 1.4, 1.0, (c, -s), pmat("sigf" + cols[(k + sd) % 6], cols[(k + sd) % 6], 0.8), 0.08)
    flag(f"{n}ensign", staff, 5.0, 2.6, (-c, s), mat_once("ensign", ensign_mat), 0.15)
    flag(f"{n}jack", jack, 1.8, 1.1, (-c, s), pmat("jackf", "#1a2a6a", 0.8), 0.1)
    # ---------- funnels with caps, steam pipes, searchlight platforms, smoke ----------
    smm = mat_once("fshipsmoke", lambda: smoke_mat("fshipsmoke", "#3a3434", 0.5))
    for k, (fxp, r, hgt) in enumerate(funnels):
        fl = fxp * L; tilt = Matrix.Rotation(0.09, 3, "Z")
        lathe(f"{n}fun{k}", [(0.0, y0 + 2.0), (r, y0 + 2.0), (r, y0 + hgt), (r * 1.06, y0 + hgt + 0.3), (r * 0.96, y0 + hgt + 0.5), (0.0, y0 + hgt + 0.5)], P(fl, 0, 0), grey, 28, yaw=yaw, sx=1.55, tilt=tilt)
        lathe(f"{n}cap{k}", [(r * 0.95, y0 + hgt - 0.9), (r * 1.04, y0 + hgt - 0.9), (r * 1.04, y0 + hgt + 0.55), (r * 0.9, y0 + hgt + 0.55), (r * 0.9, y0 + hgt - 0.4)], P(fl, 0, 0), black, 28, yaw=yaw, sx=1.55, tilt=tilt, cap=False)
        lathe(f"{n}grill{k}", [(0.0, y0 + hgt + 0.2), (r * 0.9, y0 + hgt + 0.2)], P(fl, 0, 0), dk, 28, yaw=yaw, sx=1.55, tilt=tilt, cap=False)
        for sd in (-1, 1): tube(f"{n}pipe{k}{sd}", [P(fl - r * 0.6, y0 + 3, sd * r * 1.05), P(fl - r * 0.6 - 0.8, y0 + hgt + 1.0, sd * r * 1.0)], 0.18, grey2, res=2, bres=0)
        lathe(f"{n}slp{k}", [(0.0, 0.0), (r * 1.9, 0.0), (r * 1.9, 0.25), (0.0, 0.25)], P(fl, y0 + hgt * 0.62, 0), grey2, 16, sx=1.0)
        for sd in (-1, 1): lathe(f"{n}sl{k}{sd}", [(0.0, 0.0), (0.45, 0.05), (0.5, 0.6), (0.0, 0.7)], P(fl + 0.4, y0 + hgt * 0.62 + 0.25, sd * r * 1.4), grey2, 12)
        top = P(fl - 0.09 * hgt, y0 + hgt + 1.2, 0)
        smoke_column(f"{n}smk{k}", top, 12, 1.0, 4.5, smm, drift=(-26 * c, 26 * s), seed=k + int(x), puffs=10)
    # ---------- main turrets: barbette, sloped gunhouse with rounded face, 2-3 barrels with canvas blast bags ----------
    def gunhouse(nm, lx, base, d, nb, train_, scl, elev=0.08):
        ang = (0 if d > 0 else math.pi) + train_
        ca, sa = math.cos(ang), math.sin(ang)
        Q = lambda fx_, fy, fz: P(lx + fx_ * ca + fz * sa, fy, -fx_ * sa + fz * ca)
        lathe(f"{n}{nm}bb", [(0.0, base - 2.0), (3.0 * scl, base - 2.0), (3.0 * scl, base + 0.3), (0.0, base + 0.3)], P(lx, 0, 0), grey2, 28)
        hl, hw, hh = 4.2 * scl, 2.7 * scl, 2.2 * scl
        def ring(y, k, back):
            pts = [(-hl * back, -hw * k), (hl * 0.55, -hw * k), (hl * 0.85 - (1 - k) * hl, -hw * 0.75 * k), (hl - (1 - k) * hl * 1.2, -hw * 0.35 * k), (hl - (1 - k) * hl * 1.2, hw * 0.35 * k),
                   (hl * 0.85 - (1 - k) * hl, hw * 0.75 * k), (hl * 0.55, hw * k), (-hl * back, hw * k)]
            return [Q(a, y, b) for a, b in pts]
        rs = [ring(base + 0.3, 1.0, 1.0), ring(base + 0.3 + hh * 0.7, 0.97, 1.0), ring(base + 0.3 + hh, 0.86, 0.97)]
        loft(f"{n}{nm}gh", [r + [r[0]] for r in rs], grey, True, True, smooth_=False)
        for sd in (-1, 1): bx(f"{n}{nm}hood{sd}", Q(-hl * 0.55, base + 0.3 + hh * 0.75, sd * (hw + 0.3)), (1.4 * scl, 0.6 * scl, 0.7 * scl), grey2, 0.1, yaw + ang)
        lathe(f"{n}{nm}cup", [(0.0, 0.0), (0.55 * scl, 0.0), (0.55 * scl, 0.45 * scl), (0.0, 0.55 * scl)], Q(-hl * 0.3, base + 0.3 + hh, hw * 0.4), grey2, 12)
        for k in range(nb):
            oz = (k - (nb - 1) / 2) * 1.2 * scl; root = Vector(Q(hl * 0.88, base + 0.3 + hh * 0.5, oz))
            dirv = Vector(Q(hl * 0.88 + math.cos(elev), base + 0.3 + hh * 0.5 + math.sin(elev), oz)) - root
            Lb = 13.0 * scl; tip = root + dirv * Lb
            tube(f"{n}{nm}brl{k}", [tuple(root), tuple(root + dirv * Lb * 0.5), tuple(tip)], 0.3 * scl, dk, res=2, bres=2, taper=lambda f: 1.0 - 0.4 * f)
            lathe(f"{n}{nm}mz{k}", [(0.0, 0.0), (0.24 * scl, 0.0), (0.24 * scl, 0.5 * scl), (0.0, 0.5 * scl)], tuple(tip - dirv * 0.4 * scl), dk, 12,
                  tilt=Matrix.Rotation(-math.pi / 2 + elev, 3, "Z"), yaw=yaw + ang)
            lathe(f"{n}{nm}bag{k}", [(0.0, 0.0), (0.45 * scl, 0.0), (0.58 * scl, 0.4 * scl), (0.5 * scl, 1.1 * scl), (0.34 * scl, 1.4 * scl), (0.0, 1.4 * scl)], tuple(root - dirv * 0.3), canvas, 14,
                  tilt=Matrix.Rotation(-math.pi / 2 + elev, 3, "Z"), yaw=yaw + ang)
    for k, (tx_, d_, nb, raise_) in enumerate(turrets):
        lx = tx_ * L; base = deck_y(lx) + raise_
        gunhouse(f"T{k}", lx, base, d_, nb, (train if d_ > 0 else -train) * (1 if k % 2 == 0 else 0.8), sc)
    # ---------- secondary casemate guns, AA tubs, lifeboats on davits ----------
    for k in range(4):
        for sd in (-1, 1):
            lx = (-0.17 + k * 0.08) * L; base = y0 + 2.8
            ang = sd * (-math.pi / 2) * 0.0
            Q = lambda fx_, fy, fz, lx=lx, sd=sd: P(lx + fx_, fy, sd * (Bm * 0.29) + fz * sd)
            lathe(f"{n}sec{k}{sd}", [(0.0, 0.0), (1.3, 0.0), (1.3, 0.9), (0.9, 1.4), (0.0, 1.5)], Q(0, base, 0.8), grey2, 14, sx=1.3)
            for j in (-0.3, 0.3): tube(f"{n}secb{k}{sd}{j}", [Q(1.2, base + 0.8, 0.8 + j), Q(6.0, base + 1.1, 1.6 + j)], 0.13, dk, res=2, bres=1)
    for k, (lx, yy, lz) in enumerate(((-0.24 * L, y0 + 2.9, 0.25 * Bm), (-0.24 * L, y0 + 2.9, -0.25 * Bm), (0.0, y0 + 5.4, 0.2 * Bm), (0.0, y0 + 5.4, -0.2 * Bm),
                                      (0.15 * L, y0 + 5.4, 0.18 * Bm), (0.15 * L, y0 + 5.4, -0.18 * Bm), (-0.13 * L, y0 + 5.4, 0.12 * Bm), (-0.13 * L, y0 + 5.4, -0.12 * Bm))):
        lathe(f"{n}aa{k}", [(1.0, 0.0), (1.1, 0.0), (1.1, 0.9), (1.0, 0.9), (1.0, 0.1), (0.0, 0.1)], P(lx, yy, lz), grey2, 14, cap=False)
        for j in range(4):
            a = j * math.pi / 2 + 0.4; p0 = Vector(P(lx + 0.3 * math.cos(a), yy + 0.8, lz + 0.3 * math.sin(a)))
            tube(f"{n}aab{k}{j}", [tuple(p0), tuple(p0 + Vector((1.4 * c, 1.2, -1.4 * s)))], 0.06, dk, res=2, bres=0)
    boat = mat_once("shipboat", lambda: worn("shipboat", "#c8c4b8", "#6a6a64", 0.6, 0.0, 1.0, 0.7, "#8a8678"))
    for k in range(3):
        for sd in (-1, 1):
            lx = -0.12 * L + k * 4.5; lz = sd * (Bm * 0.36)
            lathe(f"{n}boat{k}{sd}", [(0.0, 0.0), (0.5, 0.08), (0.75, 0.45), (0.72, 0.8), (0.0, 0.8)], P(lx, y0 + 3.4, lz), boat, 14, yaw=yaw, sx=2.9)
            for e in (-1.6, 1.6): tube(f"{n}dav{k}{sd}{e}", [P(lx + e, y0 + 2.8, sd * Bm * 0.26), P(lx + e, y0 + 5.2, sd * Bm * 0.3), P(lx + e, y0 + 5.0, lz)], 0.1, grey2, res=4, bres=0)
    # ---------- water: bow wave curling off the stem, foam along the sides, a long churned wake ----------
    foam = mat_once("ffoam", foam_mat)
    for sd in (-1, 1):
        rings_ = []
        for k in range(8):
            f = k / 7; lx = 0.5 * L + 0.02 * L - f * 0.35 * L; t = min(1.0, max(0.0, lx / L + 0.5))
            hwb = Bm / 2 * (0.42 + 0.58 * smooth(0.0, 0.25, t)) * max(0.08, 1 - (max(0.0, t - 0.58) / 0.42) ** 1.7)
            hgt = 1.6 * (1 - f) ** 1.5
            rings_.append([P(lx, -0.24, sd * (hwb + 0.2 + 7 * f)), P(lx, hgt * 0.6 - 0.2, sd * (hwb + 0.15 + 2.5 * f)), P(lx, hgt - 0.2, sd * (hwb + 0.05 + 0.6 * f))])
        loft(f"{n}bow{sd}", rings_, foam, False, False)
        vs = [P(0.2 * L, -0.22, sd * (Bm * 0.5 + 0.3)), P(-0.5 * L, -0.22, sd * (Bm * 0.48)), P(-0.9 * L, -0.22, sd * Bm * 1.2), P(-1.6 * L, -0.22, sd * Bm * 2.4),
              P(-1.6 * L, -0.22, sd * Bm * 3.2), P(-0.6 * L, -0.22, sd * Bm * 1.6), P(0.15 * L, -0.22, sd * (Bm * 1.4))]
        mesh_obj(f"{n}foam{sd}", vs, [tuple(range(len(vs)))], foam)
    mesh_obj(f"{n}wake", [P(-0.48 * L, -0.21, -Bm * 0.45), P(-0.48 * L, -0.21, Bm * 0.45), P(-1.8 * L, -0.21, Bm * 1.3), P(-1.8 * L, -0.21, -Bm * 1.3)], [(0, 1, 2, 3)], foam)
    mesh_obj(f"{n}wash", [P(-0.5 * L, -0.2, -Bm * 0.3), P(-0.5 * L, -0.2, Bm * 0.3), P(-0.8 * L, -0.2, Bm * 0.5), P(-0.8 * L, -0.2, -Bm * 0.5)], [(0, 1, 2, 3)], foam)


def foam_mat():
    m = lib.principled("ffoam", lib.hexc("#e8eef0"), 0.6); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    geo = n.new("ShaderNodeNewGeometry"); mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.25, 0.25, 0.25); l.new(geo.outputs["Position"], mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; nz.inputs["Detail"].default_value = 8; l.new(mp.outputs[0], nz.inputs["Vector"])
    vo = n.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 2.5; l.new(mp.outputs[0], vo.inputs["Vector"])
    mu = n.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; l.new(nz.outputs["Fac"], mu.inputs[0]); l.new(vo.outputs["Distance"], mu.inputs[1])
    r = lib.ramp(n, l, mu.outputs[0], [(0.04, (0, 0, 0)), (0.32, (0.7, 0.7, 0.7))]); l.new(r.outputs["Color"], b.inputs["Alpha"])
    b.inputs["Emission Color"].default_value = (0.75, 0.8, 0.85, 1); b.inputs["Emission Strength"].default_value = 0.12
    return m
def sea_mat():
    m = lib.principled("sea", lib.hexc("#123048"), 0.12); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 0.35, 1.0); l.new(tc.outputs["Object"], mp.inputs["Vector"])
    w1 = n.new("ShaderNodeTexWave"); w1.inputs["Scale"].default_value = 0.08; w1.inputs["Distortion"].default_value = 9; w1.inputs["Detail"].default_value = 4; l.new(mp.outputs[0], w1.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.5; nz.inputs["Detail"].default_value = 10; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    hh = n.new("ShaderNodeMath"); hh.operation = "MULTIPLY_ADD"; hh.inputs[1].default_value = 0.6; l.new(w1.outputs["Fac"], hh.inputs[0]); l.new(nz.outputs["Fac"], hh.inputs[2])
    lib.bump(n, l, hh.outputs[0], 0.6, 0.6)
    r = lib.ramp(n, l, nz.outputs["Fac"], [(0.35, lib.hexc("#0c2236")), (0.65, lib.hexc("#1e4a5a"))]); l.new(r.outputs["Color"], b.inputs["Base Color"])
    return m

# ------------------------------------------------------------------ build
def build(M, D):
    random.seed(1939)
    S = bpy.context.scene; dusk_sky(S.world)
    rnd = random.Random(44)
    # shell craters across the field (none in the soldiers' lane or under the tanks)
    for k in range(70):
        cx, cz = rnd.uniform(-60, 50), rnd.uniform(-10, 66); r = rnd.uniform(1.2, 3.8)
        if flat_mask(cx, cz) > 0.9: CRATERS.append((cx, cz, r, r * 0.32))
    terrain()
    # puddles in the deeper craters: they mirror the burning sky
    water = lib.principled("puddle", lib.hexc("#1a1410"), 0.03)
    for k, (cx, cz, r, dp) in enumerate(CRATERS):
        if k % 2 == 0 and r > 1.8: lathe(f"pud{k}", [(0.0, 0.0), (r * 0.55, 0.0)], (cx, H(cx, cz) + dp * 0.35, cz), water, 20, cap=False, sx=1.0, sz=0.8 + (k % 3) * 0.1)
    # sea, with the beach and its defences
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(260, -0.25, 140)); sea = bpy.context.object; sea.scale = (420, 640, 1); bpy.ops.object.transform_apply(scale=True)
    sea.data.materials.append(sea_mat())
    for i, (x, z, yw, L, Bm, kind, tr) in enumerate(((120, 60, 0.4, 110, 15, "cruiser", 0.45), (175, 130, 0.2, 150, 22, "battleship", 0.3), (95, 175, 0.6, 90, 10, "destroyer", -0.3))):
        warship(f"w{i}", x, z, yw, L, Bm, kind, tr)
    steel = mat_once("frust", lambda: worn("frust", "#4a3a30", "#7a3a1a", 0.7, 0.5, 6, 0.55, "#2a1a10"))
    for k, (x, z) in enumerate(((57, 14), (59, 19), (57.5, 25), (60, 30), (58, 35), (61, 41), (59, 47), (56.5, 52), (60.5, 22), (62, 36))):
        hedgehog(f"hh{k}", (x, H(x, z) - 0.15, z), k * 0.7, steel)
    bunker = mat_once("fconcrete", lambda: worn("fconcrete", "#8a8478", "#5a564e", 0.9, 0.0, 2, 0.6, "#4a463e"))
    by = H(55.5, 22) - 0.3
    lathe("bunker", [(0.0, 0.0), (3.2, 0.0), (3.1, 1.2), (2.95, 1.25), (2.95, 1.75), (3.05, 1.8), (2.6, 2.4), (1.2, 2.75), (0.0, 2.8)], (55.5, by, 22), bunker, 8, yaw=0.3)
    lathe("bunkerslit", [(3.0, 1.26), (3.0, 1.74)], (55.5, by, 22), pmat("fdark", "#0a0808", 1.0), 8, yaw=0.3, cap=False, sx=1.01, sz=1.01)
    net = mat_once("fnet", lambda: worn("fnet", "#4a4a2a", "#2a2a1a", 0.95, 0.0, 3, 0.45, "#5a5a34"))
    lib.blob("bunkernet", T(55.2, by + 2.5, 22.3), (2.4, 0.5, 2.2), net, 0.35, 5)
    text("Wn 62", (55.5, by + 2.0, 18.9), 0.35, pmat("fstencil", "#e8e0c8", 0.8), yaw=0.25, flat=False)
    tube("bunkergun", [(57.3, H(55.5, 22) + 1.2, 20.7), (60.5, H(55.5, 22) + 1.3, 18.6)], 0.14, steel)
    for k in range(4): sandbag_wall(f"bsb{k}", (52.5 + k * 1.6, H(52.5 + k * 1.6, 18) + 0.0, 18 - k * 0.4), 0.3, 5, 3, mat_once("fsand", lambda: sandmat()), seed=k * 9)
    for k in range(10):
        x, z = rnd.uniform(52, 60), rnd.uniform(10, 50)
        lib.blob(f"rock{k}", T(x, H(x, z), z), (rnd.uniform(0.6, 1.6), rnd.uniform(0.4, 1.0), rnd.uniform(0.6, 1.4)), mat_once("frock", lambda: worn("frock", "#5a5650", "#3a3632", 0.8, 0.0, 1.5, 0.5, "#2a2824")), 0.3, k)
    # tanks: four advancing, one knocked out and burning
    for i, (x, z, y) in enumerate(TANKS): tank(f"t{i}", x, z, math.pi / 2 + y)
    tank("wreck", -22, 36, math.pi / 2 + 0.9, burnt=True, tilt=0.12)
    fire("wreckfire", (-22.5, 1.8, 35.5), 1.8, seed=3, energy=2500)
    smm = mat_once("fsmoke", lambda: smoke_mat("fsmoke", "#2a2220", 0.42))
    smoke_column("wrecksmoke", (-22.5, 3.5, 36), 22, 1.1, 4.5, smm, drift=(-16, 10), seed=5, puffs=14)
    # the ruined town: gutted houses with signs, a church tower, rubble, fires and smoke
    PL = ["#b89868", "#a8704a", "#7a7c80", "#c08a50", "#8a7a6a", "#a85a3a", "#b8a070", "#6a7468"]
    rm = [ruin_mat(f"ruin{k}", c) for k, c in enumerate(PL)]
    signs = {1: ("BÄCKEREI", "#2a3a2a"), 3: ("HOTEL", "#4a1a1a"), 5: ("CAFÉ", "#1a2a4a"), 7: ("APOTHEKE", "#2a2a2a"), 9: ("KOLONIALWAREN", "#3a2a1a")}
    xs = -42.0; k = 0
    while xs < 46:
        w = rnd.uniform(7, 11); z_ = 70 + (k % 3) * 4 + rnd.uniform(-1, 1)
        if abs(xs + w / 2 - 6) < 4: xs += 1.5
        if abs(xs + w / 2 + 10) < 3.5:
            church("church", xs + w / 2, z_ + 4, rm[2]); xs += 7; k += 1; continue
        ruin_building(f"rb{k}", xs + w / 2, z_, w, rnd.randint(3, 5), rm[k % len(rm)], 100 + k, sign=signs.get(k), fires={(0, rnd.randrange(2)), (1, rnd.randrange(2))})
        xs += w + rnd.uniform(0.8, 3.0); k += 1
    # second row behind (silhouettes)
    for j in range(8):
        x_ = -40 + j * 11 + rnd.uniform(-2, 2); ruin_building(f"rr{j}", x_, 92 + rnd.uniform(-2, 2), rnd.uniform(8, 12), rnd.randint(4, 6), rm[(j + 3) % len(rm)], 300 + j)
    brick = ruin_mat("rubble", "#5a4a3a", "#7a3e2c")
    for j in range(40):
        x_, z_ = rnd.uniform(-38, 44), rnd.uniform(62, 70)
        lib.blob(f"rubble{j}", T(x_, 0.0, z_), (rnd.uniform(1.5, 3.5), rnd.uniform(0.6, 1.6), rnd.uniform(1.2, 2.5)), brick, 0.5, j)
    bricks = []
    for j in range(260):
        x_, z_ = rnd.uniform(-36, 42), rnd.uniform(56, 70)
        bricks.append(((x_, H(x_, z_) + 0.05, z_), (0.24, 0.07, 0.12), rnd.uniform(0, 3), rnd.uniform(-0.3, 0.3)))
    boxes("bricks", bricks, mat_once("fbrick", lambda: lib.brickmat("fbrick", "#8a4a36", "#6a3424", "#5a4a40", 30)))
    for k, (x_, z_, sz) in enumerate(((-18, 67, 1.6), (6, 72, 2.0), (22, 66, 1.4), (-5, 58, 1.2), (14, 75, 1.8), (-30, 72, 1.5), (34, 70, 1.4))):
        fire(f"tfire{k}", (x_, H(x_, z_) if z_ < 62 else 0.3, z_), sz, seed=k + 10, energy=1800 * sz)
    for k, (x_, z_, h_) in enumerate(((-16, 74, 40), (8, 78, 46), (26, 72, 34), (-32, 80, 30), (40, 82, 28))):
        smoke_column(f"tsmoke{k}", (x_, 8, z_), h_, 1.6, 6, smm, drift=(-24, 14), seed=20 + k, puffs=14)
    # street furniture at the town edge: bent lamp posts, a wrecked car, a tram pole, a road sign
    iron = mat_once("firon", lambda: worn("firon", "#2a2a28", "#4a3020", 0.5, 0.6, 10, 0.65))
    for k, (x_, z_, lean) in enumerate(((-8, 64, 0.2), (12, 63, -0.35), (26, 65, 0.05))):
        top = (x_ + math.sin(lean) * 5, 5 * math.cos(lean), z_)
        tube(f"lamp{k}", [(x_, 0, z_), ((x_ + top[0]) / 2, 2.6, z_), top, (top[0] + 0.8, top[1] + 0.2, z_)], 0.09, iron, res=4, bres=1)
        lathe(f"lampsh{k}", [(0.0, 0.0), (0.35, -0.3), (0.3, -0.35), (0.0, -0.2)], (top[0] + 0.8, top[1] + 0.2, z_), iron, 12)
    carm = mat_once("fcar", lambda: worn("fcar", "#1e1e22", "#5a2a14", 0.6, 0.4, 6, 0.55, "#2a1a10"))
    bx("car", (-2, 0.7, 62), (4.2, 0.9, 1.8), carm, 0.3, 0.4); bx("carcab", (-2.3, 1.45, 62.1), (2.0, 0.7, 1.6), carm, 0.25, 0.4)
    for sx in (-1.4, 1.4):
        for sz in (-0.9, 0.9): cy(f"carw{sx}{sz}", (-2 + sx * math.cos(0.4) + sz * math.sin(0.4), 0.38, 62 - sx * math.sin(0.4) + sz * math.cos(0.4)), 0.38, 0.25, pmat("ftyre", "#141414", 0.8), 16, rot=(math.radians(90), 0, 0.4))
    fire("carfire", (-2.2, 1.2, 62), 0.8, seed=31, energy=600)
    bx("rsign", (16, 2.6, 60), (2.4, 0.7, 0.08), pmat("fysign", "#d8b830", 0.5), 0.02, 0.15); cy("rsignp", (16, 1.2, 60.05), 0.05, 2.6, iron, 8)
    text("BERLIN 12 km", (16.02, 2.47, 59.94), 0.32, pmat("fink", "#1a1a1a", 0.6), yaw=0.15, flat=False)
    # the field: dead trees, telegraph poles with sagging wire, wire entanglements on X-pickets, sandbags, debris
    bark = mat_once("fbark", lambda: worn("fbark", "#2a221c", "#4a3a2a", 0.9, 0.0, 3, 0.6, "#1a1410"))
    for k, (x_, z_, h_) in enumerate(((-12, 18, 9), (16, 22, 7), (-28, 44, 11), (22, 46, 9), (-4, 54, 8), (34, 30, 10), (-40, 26, 9), (8, 58, 7))):
        dead_tree(f"tree{k}", (x_, H(x_, z_), z_), h_, bark, seed=k)
    pm = wood_mat("fpole", "#4a3a2a", "#2a1e14", 4, 0.9); tops = []
    for k in range(7):
        z_ = 8 + k * 9; x_ = 13 + k * 0.5
        tops.append(pole(f"pole{k}", (x_, H(x_, z_) - 0.2, z_), 7.5, pm, lean=[0, 0.05, 0.15, 0, -0.1, 0.3, 0.05][k], yaw=0.5))
    wm = pmat("fwire", "#1a1a1a", 0.5, 0.8)
    for k in range(len(tops) - 1):
        a_, b_ = Vector(tops[k]), Vector(tops[k + 1])
        for sd in (-0.65, 0.65):
            p, q = a_ + Vector((sd, -0.36, 0)), b_ + Vector((sd, -0.36, 0)); mid = (p + q) / 2 - Vector((0, 0.9, 0))
            tube(f"tw{k}{sd}", [tuple(p), tuple(mid), tuple(q)], 0.015, wm, res=8, bres=0)
    bw = mat_once("fbwire", lambda: worn("fbwire", "#4a4440", "#6a3a1e", 0.5, 0.8, 20, 0.6))
    for k, (x_, z_, yw) in enumerate(((-16, 12, 0.1), (-26, 14, -0.1), (12, 9, 0.2), (22, 11, 0.0), (-9, 20, 0.15), (30, 14, 0.1))):
        barbed_coil(f"cw{k}", (x_, H(x_, z_), z_), 8, 0.45, yw, bw, 26)
        for e in (-4, 0, 4):
            px_, pz_ = x_ + e * math.cos(yw), z_ - e * math.sin(yw)
            for sd in (-1, 1): tube(f"pk{k}{e}{sd}", [(px_ - 0.35 * sd, H(px_, pz_) - 0.1, pz_), (px_ + 0.35 * sd, H(px_, pz_) + 1.2, pz_)], 0.05, pm, res=2, bres=1)
    sand = mat_once("fsand", lambda: sandmat())
    for k, (x_, z_, yw) in enumerate(((-9, 2.5, 0.1), (8, 3.5, -0.15), (-14, 6, 0.4), (14, 8, -0.3), (-5, 16, 0.0))):
        sandbag_wall(f"sb{k}", (x_, H(x_, z_), z_), yw, 6, 3, sand, seed=k * 7)
    drum = mat_once("fdrum", lambda: worn("fdrum", "#6a2a1e", "#3a2a20", 0.6, 0.4, 8, 0.6, "#2a1a10"))
    for k, (x_, z_, ly) in enumerate(((5.5, 1.5, False), (6.3, 2.2, False), (6.9, 1.2, True), (-6.5, 4.5, False), (-21, 30, True), (18, 18, False))):
        oil_drum(f"drum{k}", (x_, H(x_, z_), z_), drum, ly, k * 0.8)
    for k, (x_, z_, yw, lab) in enumerate(((-5.5, 1.0, 0.3, "7.5cm"), (-4.3, 1.3, -0.2, "MUNITION"), (-4.9, 1.2, 0.1, ""), (7.5, 6.5, 0.6, "7.5cm"), (-11, 9, 0.2, "AMMO"))):
        crate(f"crate{k}", (x_, H(x_, z_) + (0.44 if lab == "" else 0), z_), yw, lab)
    cart_wheel("cwheel", (9.5, 0.3, 5.0), 0.7, wood_mat("fwheel", "#5a4a32", "#2a2014", 8, 0.8), yaw=0.4, tilt=1.25)
    planks = [((rnd.uniform(-20, 20), 0.06, rnd.uniform(1, 30)), (rnd.uniform(1.0, 2.6), 0.06, 0.2), rnd.uniform(0, 3), rnd.uniform(-0.1, 0.1)) for _ in range(40)]
    planks = [((p[0][0], H(p[0][0], p[0][2]) + 0.05, p[0][2]), p[1], p[2], p[3]) for p in planks if flat_mask(p[0][0], p[0][2]) > 0.3 or abs(p[0][0]) > 4]
    boxes("planks", planks, wood_mat("fplank", "#6a5236", "#3a2a1a", 6, 0.8), 0.01)
    # ---- shot-2 foreground: puddles in the lane, a supply dump on the left, a sandbagged MG nest on the right ----
    for k, (x_, z_, r_) in enumerate(((0.2, 2.6, 1.3), (1.8, 8.2, 0.9), (-2.2, 6.4, 1.1), (-0.8, 12.5, 1.6), (3.2, 1.0, 0.7))):
        rr = random.Random(k); prof = [(0.0, 0.0)] + [(r_ * (0.8 + 0.3 * rr.random()), 0.0) for _ in range(1)]
        o = lathe(f"lpud{k}", [(0.0, 0.0), (r_, 0.0)], (x_, 0.012, z_), water, 24, cap=False, sx=1.3, sz=0.7)
        for v in o.data.vertices:
            d = Vector((v.co.x + x_, v.co.y - z_)).length
            if d > 0.05: f_ = 1 + 0.25 * noise.noise(Vector((v.co.x * 1.3, v.co.y * 1.3, k))); v.co.x = -x_ + (v.co.x + x_) * f_; v.co.y = z_ + (v.co.y - z_) * f_
    for k, (x_, z_, yw, lab) in enumerate(((3.6, 4.2, 0.4, "7.5cm"), (4.1, 5.3, 0.1, "MUNITION"), (3.7, 4.3, 0.5, ""))):
        crate(f"fcr{k}", (x_, 0.44 if lab == "" else 0.0, z_), yw, lab)
    for k, (x_, z_, ly) in enumerate(((4.6, 3.4, False), (5.2, 4.0, False), (4.2, 2.6, True))): oil_drum(f"fdr{k}", (x_, 0, z_), drum, ly, k * 1.1)
    for k in range(3): bx(f"fjc{k}", (3.3 + k * 0.4, 0.23, 3.0 - k * 0.15), (0.18, 0.46, 0.34), mat_once("fjerry", lambda: worn("fjerry", "#4a5236", "#2a2a22", 0.6, 0.3, 20, 0.6)), 0.03, 0.2 * k)
    sandbag_wall("mgnest", (-3.2, 0, 3.6), 0.35, 6, 3, sand, seed=77); sandbag_wall("mgnest2", (-4.6, 0, 5.4), 1.2, 4, 3, sand, seed=78)
    tube("mgbar", [(-3.0, 0.85, 3.4), (-2.3, 0.9, 2.6)], 0.035, mat_once("tanksteel", lambda: worn("tanksteel", "#3a3c36", "#5a5a54", 0.45, 0.6, 30, 0.7)))
    for e in (-1, 1): tube(f"mgleg{e}", [(-3.0, 0.85, 3.4), (-3.0 + 0.25 * e, 0.72, 3.0)], 0.015, iron)
    for k in range(14):
        x_, z_ = rnd.uniform(-3.5, 4.5), rnd.uniform(0.5, 9)
        lathe(f"fcase{k}", [(0.0, 0.0), (0.012, 0.0), (0.012, 0.07), (0.0, 0.07)], (x_, 0.012, z_), mat_once("kbrass", lambda: lib.principled("kbrass", lib.hexc("#c8963a"), 0.28, 1.0)), 8, tilt=Matrix.Rotation(math.radians(90), 3, "Z"), yaw=rnd.random() * 6)
    tube("tread1", [(-6.5, 0.02, 7), (-3.5, 0.02, 3), (1.0, 0.02, -2)], 0.06, mat_once("tankmud", lambda: worn("tankmud", "#3a3226", "#24201a", 0.85, 0.15, 5, 0.6, "#5a4630")))
    # grass tufts, thickest at the field edges, none in the lane
    gm = mat_once("fgrass", lambda: worn("fgrass", "#8a7a3a", "#5a5a24", 0.8, 0.0, 4, 0.5, "#6a6a2a"))
    src = grass_tuft_src(gm, 1); pts = []
    while len(pts) < 600:
        x_, z_ = rnd.uniform(-45, 45), rnd.uniform(-6, 64)
        if flat_mask(x_, z_) > 0.6 or (abs(x_) > 5 and rnd.random() < 0.4): pts.append((x_, H(x_, z_) - 0.03, z_))
    scatter(src, "tf", pts, s=(0.8, 2.0), seed=2); src.location = T(0, -50, 0)
    # ---------- light: low warm sun behind the scene, warm bounce from the camera side, cool sky fill ----------
    sun = lib.light("SUN", (0, 0, 0), 6.0, (1.0, 0.5, 0.22), math.radians(2.5))
    sun.rotation_euler = (-T(*SUN)).to_track_quat("-Z", "Y").to_euler()
    f1 = lib.light("AREA", T(4, 7, -16), 3500, (1.0, 0.55, 0.38), 14); lib.look_at(f1, T(0, 1, 10))
    f2 = lib.light("AREA", T(-6, 20, 30), 25000, (0.9, 0.5, 0.45), 40); lib.look_at(f2, T(0, 8, 74))
    f3 = lib.light("AREA", T(60, 30, -10), 60000, (0.9, 0.6, 0.5), 60); lib.look_at(f3, T(130, 0, 100))
    return {}
