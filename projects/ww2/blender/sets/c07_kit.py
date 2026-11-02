# Shared Pacific kit for chapters 7 and 13 (sets c07_* / c13_*), three.js layout coordinates (y up) in, Blender out.
#   sky(): painted day / dawn / dusk / night sky with sun disc and lit clouds   sea(): open-water or harbour plane
#   plane(kind): one 3D aircraft mesh (zero, val, kate, sbd, wildcat, b25, b29), nose +z, built once and instanced;
#                place(o, pos, fwd, roll) poses an instance (update(f) moves them per frame)
#   carrier(): flight-deck ship (Japanese: small island, downturned funnels; US: big island, radar, tripod)
#   us_battleship(): front.warship with a US ensign and no funnel smoke   palm(), hills(), smoke(), splash()
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj, fire, flame, flame_mat, smoke_mat, smoke_column
from sets import front as FR
from sets import ikit
from sets.jungle import frond, leaf_mat

CM = Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0)))           # three -> Blender axes (its own inverse)
def bx(name, c, s, m, bev=0.01, yaw=0.0): return lib.box(name, T(*c), TS(*s), m, bev, rot=(0, 0, yaw))
def smooth(a, b, x): t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

# ------------------------------------------------------------------ posing
def basis(fwd, roll=0.0, up=(0, 1, 0)):
    F = Vector(fwd).normalized(); X = Vector(up).cross(F)
    if X.length < 1e-6: X = Vector((1, 0, 0))
    X.normalize(); Y = F.cross(X)
    X, Y = X * math.cos(roll) + Y * math.sin(roll), Y * math.cos(roll) - X * math.sin(roll)
    return Matrix((X, Y, F)).transposed()
def place(o, pos, fwd, roll=0.0, s=1.0):
    """pose an object built in local three coords (nose +z) at three pos, nose along fwd, banked by roll"""
    R = CM @ basis(fwd, roll) @ CM
    o.matrix_world = Matrix.Translation(T(*pos)) @ R.to_4x4() @ Matrix.Diagonal((s, s, s, 1.0))
def inst(src, name):
    o = src.copy(); o.name = name; link(o); return o

# ------------------------------------------------------------------ sky
def sky(world, sun, stops, sun_col=(30.0, 22.0, 12.0), cloud_dark=(0.3, 0.32, 0.4), cloud_lit=(1.2, 1.0, 0.8), cover=0.5, strength=1.0,
        glow_col=(1.0, 0.7, 0.4), glow=0.5, disc=True, band=(0.01, 0.12), fade=(0.8, 0.4)):
    """gradient (stops = [(height 0..1 above horizon, rgb)]), sun glow + disc, a cloud deck lit on the sun side"""
    nt = world.node_tree; n = nt.nodes; l = nt.links; bg = n["Background"]
    co = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(co.outputs["Generated"], sep.inputs[0])
    sd = T(*Vector(sun).normalized()).normalized()
    mr = n.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.05; mr.inputs["From Max"].default_value = 0.9; l.new(sep.outputs["Z"], mr.inputs["Value"])
    rmp = n.new("ShaderNodeValToRGB"); l.new(mr.outputs["Result"], rmp.inputs["Fac"]); e = rmp.color_ramp.elements
    e[0].position, e[0].color = stops[0][0], (*stops[0][1], 1); e[1].position, e[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]: el = e.new(p); el.color = (*c, 1)
    dot = n.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; l.new(co.outputs["Generated"], dot.inputs[0]); dot.inputs[1].default_value = tuple(sd)
    mx0 = n.new("ShaderNodeMath"); mx0.operation = "MAXIMUM"; mx0.inputs[1].default_value = 0.0; l.new(dot.outputs["Value"], mx0.inputs[0])
    def pw(e_):
        p = n.new("ShaderNodeMath"); p.operation = "POWER"; p.inputs[1].default_value = e_; l.new(mx0.outputs[0], p.inputs[0]); return p
    g1, g2, dk = pw(8), pw(90), pw(4000)
    gs = n.new("ShaderNodeMath"); gs.operation = "MULTIPLY_ADD"; gs.inputs[1].default_value = glow * 0.5; l.new(g1.outputs[0], gs.inputs[0]); l.new(g2.outputs[0], gs.inputs[2])
    gm = n.new("ShaderNodeMath"); gm.operation = "MULTIPLY"; gm.inputs[1].default_value = glow; l.new(gs.outputs[0], gm.inputs[0])
    add1 = n.new("ShaderNodeMix"); add1.data_type = "RGBA"; add1.blend_type = "ADD"; l.new(gm.outputs[0], add1.inputs[0]); l.new(rmp.outputs["Color"], add1.inputs[6]); add1.inputs[7].default_value = (*glow_col, 1)
    zp = n.new("ShaderNodeMath"); zp.operation = "ADD"; zp.inputs[1].default_value = 0.1; l.new(sep.outputs["Z"], zp.inputs[0])
    px = n.new("ShaderNodeMath"); px.operation = "DIVIDE"; l.new(sep.outputs["X"], px.inputs[0]); l.new(zp.outputs[0], px.inputs[1])
    py = n.new("ShaderNodeMath"); py.operation = "DIVIDE"; l.new(sep.outputs["Y"], py.inputs[0]); l.new(zp.outputs[0], py.inputs[1])
    cmb = n.new("ShaderNodeCombineXYZ"); l.new(px.outputs[0], cmb.inputs[0]); l.new(py.outputs[0], cmb.inputs[1])
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.7, 1.4, 1.0); l.new(cmb.outputs[0], mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.1; nz.inputs["Detail"].default_value = 9; nz.inputs["Roughness"].default_value = 0.6; l.new(mp.outputs[0], nz.inputs["Vector"])
    cov = n.new("ShaderNodeValToRGB"); l.new(nz.outputs["Fac"], cov.inputs["Fac"]); cov.color_ramp.elements[0].position = 0.62 - 0.25 * cover; cov.color_ramp.elements[1].position = 0.74 - 0.2 * cover
    bnd = n.new("ShaderNodeMapRange"); bnd.inputs["From Min"].default_value = band[0]; bnd.inputs["From Max"].default_value = band[1]; l.new(sep.outputs["Z"], bnd.inputs["Value"])
    fd = n.new("ShaderNodeMapRange"); fd.inputs["From Min"].default_value = fade[0]; fd.inputs["From Max"].default_value = fade[1]; l.new(sep.outputs["Z"], fd.inputs["Value"])
    m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; l.new(cov.outputs["Color"], m1.inputs[0]); l.new(bnd.outputs["Result"], m1.inputs[1])
    m2 = n.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; l.new(m1.outputs[0], m2.inputs[0]); l.new(fd.outputs["Result"], m2.inputs[1])
    lit = n.new("ShaderNodeMath"); lit.operation = "POWER"; lit.inputs[1].default_value = 1.5; l.new(mx0.outputs[0], lit.inputs[0])
    sh = n.new("ShaderNodeMath"); sh.operation = "MULTIPLY_ADD"; sh.inputs[1].default_value = 0.5; sh.inputs[2].default_value = 0.25; l.new(nz.outputs["Fac"], sh.inputs[0])
    lit2 = n.new("ShaderNodeMath"); lit2.operation = "MAXIMUM"; l.new(lit.outputs[0], lit2.inputs[0]); l.new(sh.outputs[0], lit2.inputs[1])
    ccol = n.new("ShaderNodeMix"); ccol.data_type = "RGBA"; l.new(lit2.outputs[0], ccol.inputs[0]); ccol.inputs[6].default_value = (*cloud_dark, 1); ccol.inputs[7].default_value = (*cloud_lit, 1)
    mixc = n.new("ShaderNodeMix"); mixc.data_type = "RGBA"; l.new(m2.outputs[0], mixc.inputs[0]); l.new(add1.outputs[2], mixc.inputs[6]); l.new(ccol.outputs[2], mixc.inputs[7])
    out = mixc
    if disc:
        sn = n.new("ShaderNodeMix"); sn.data_type = "RGBA"; sn.blend_type = "ADD"; l.new(dk.outputs[0], sn.inputs[0]); l.new(mixc.outputs[2], sn.inputs[6]); sn.inputs[7].default_value = (*sun_col, 1); out = sn
    l.new(out.outputs[2], bg.inputs[0]); bg.inputs[1].default_value = strength
def sun_light(sun, energy, col, angle=1.5):
    o = lib.light("SUN", (0, 0, 0), energy, col, math.radians(angle)); o.rotation_euler = (-T(*Vector(sun).normalized())).to_track_quat("-Z", "Y").to_euler(); return o
def area(c, target, energy, col, size, size_y=None):
    o = lib.light("AREA", T(*c), energy, col, size, size_y=size_y); lib.look_at(o, T(*target)); return o

# ------------------------------------------------------------------ water
def water_mat(name, deep="#0c3048", shallow="#1e6a7a", scale=1.0, rough=0.06, chop=0.5):
    m = lib.principled(name, hexc(deep), rough); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0 * scale, 0.4 * scale, 1.0 * scale); l.new(tc.outputs["Object"], mp.inputs["Vector"])
    w1 = n.new("ShaderNodeTexWave"); w1.inputs["Scale"].default_value = 0.12; w1.inputs["Distortion"].default_value = 8; w1.inputs["Detail"].default_value = 5; l.new(mp.outputs[0], w1.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35 * scale; nz.inputs["Detail"].default_value = 10; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 3.0 * scale; fn.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], fn.inputs["Vector"])
    hh = n.new("ShaderNodeMath"); hh.operation = "MULTIPLY_ADD"; hh.inputs[1].default_value = 0.5; l.new(w1.outputs["Fac"], hh.inputs[0]); l.new(fn.outputs["Fac"], hh.inputs[2])
    lib.bump(n, l, hh.outputs[0], chop, 0.5)
    r = lib.ramp(n, l, nz.outputs["Fac"], [(0.35, hexc(deep)), (0.7, hexc(shallow))]); l.new(r.outputs["Color"], b.inputs["Base Color"])
    return m
def sea(name, x0, x1, z0, z1, y=-0.25, mat=None):
    o = mesh_obj(name, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], [(0, 1, 2, 3)], mat or water_mat(name + "m"))
    return o
def whitecaps(name, x0, x1, z0, z1, n_, rnd, y=-0.22, size=(2, 6)):
    """small foam streaks scattered on the sea (open-ocean texture)"""
    fm = mat_once("ffoam", FR.foam_mat); vs, fs = [], []
    for k in range(n_):
        x, z = rnd.uniform(x0, x1), rnd.uniform(z0, z1); L = rnd.uniform(*size); w = L * 0.18; a = rnd.uniform(-0.3, 0.3)
        ca, sa = math.cos(a), math.sin(a); b = len(vs)
        vs += [(x - L / 2 * ca, y, z - L / 2 * sa - w), (x + L / 2 * ca, y, z + L / 2 * sa - w * 0.3), (x + L / 2 * ca, y, z + L / 2 * sa + w * 0.3), (x - L / 2 * ca, y, z - L / 2 * sa + w)]
        fs.append((b, b + 1, b + 2, b + 3))
    return mesh_obj(name, vs, fs, fm)

# ------------------------------------------------------------------ aircraft
def _loft(K, rings, m, cap0=True, cap1=True):
    bm, _ = K._get(0.0); R = len(rings[0]); vs = [[bm.verts.new(T(*p)) for p in r] for r in rings]
    allv = [v for r in vs for v in r]
    for i in range(len(rings) - 1):
        for k in range(R):
            k2 = (k + 1) % R; bm.faces.new((vs[i][k], vs[i + 1][k], vs[i + 1][k2], vs[i][k2]))
    if cap0: bm.faces.new(vs[0][::-1])
    if cap1: bm.faces.new(vs[-1])
    K._finish(allv, m, 0.0, True)
def _fuse(K, prof, m, seg=14):
    """fuselage along +z: prof = [(z, half-width, half-height, centre y)]"""
    rings = []
    for z, rx, ry, cy in prof:
        rings.append([(max(rx, 0.005) * math.cos(a), cy + max(ry, 0.005) * math.sin(a), z) for a in (k / seg * math.tau for k in range(seg))])
    _loft(K, rings, m)
def _wing(K, span, root, tip, z_le, sweep, y0, dihedral, thick, m, n=10, gap=0.0, round_tip=0.35, tip_up=0.0):
    """wing / tailplane across x: chord root -> tip, leading edge at z_le (root) swept back by `sweep` at the tip"""
    rings = []
    xs = [-1 + 2 * k / n for k in range(n + 1)]
    for u in xs:
        a = abs(u); x = u * span / 2
        if gap and a * span / 2 < gap: continue
        rt = 1.0 - round_tip * smooth(0.82, 1.0, a) ** 2
        ch = (root + (tip - root) * a) * max(0.25, rt); le = z_le - sweep * a - (root + (tip - root) * a - ch) * 0.3
        y = y0 + dihedral * a * span / 2 + tip_up * a * a; t = thick * (1 - 0.6 * a)
        rings.append([(x, y + t, le), (x, y + t * 0.6, le - ch * 0.45), (x, y, le - ch), (x, y - t * 0.4, le - ch * 0.45), (x, y - t * 0.2, le - 0.02)])
    if gap:
        half = len(rings) // 2; _loft(K, rings[:half], m); _loft(K, rings[half:], m)
    else: _loft(K, rings, m)
def _fin(K, h, root, tip, z_le, sweep, y0, thick, m, x=0.0, n=6):
    rings = []
    for k in range(n + 1):
        u = k / n; ch = (root + (tip - root) * u) * (1 - 0.35 * smooth(0.75, 1.0, u) ** 2); le = z_le - sweep * u; y = y0 + h * u; t = thick * (1 - 0.5 * u)
        rings.append([(x + t, y, le - ch * 0.4), (x, y, le - ch), (x - t, y, le - ch * 0.4), (x, y, le)])
    _loft(K, rings, m)
def _roundel(K, c, r, col, ring=None, up=True, star=False, side=0):
    """insignia disc lying on a surface (up) or on the fuselage side (side = +-1)"""
    def disc(rr, m, off):
        bm, _ = K._get(0.0); vs = []
        for k in range(20):
            a = k / 20 * math.tau
            if side: p = (c[0] + side * off, c[1] + rr * math.sin(a), c[2] + rr * math.cos(a))
            else: p = (c[0] + rr * math.cos(a), c[1] + off, c[2] + rr * math.sin(a))
            vs.append(bm.verts.new(T(*p)))
        bm.faces.new(vs); K._finish(vs, m, 0.0)
    if ring: disc(r * 1.25, pm(ring, 0.6), 0.004)
    disc(r, pm(col, 0.6), 0.008)
    if star:
        bm, _ = K._get(0.0); vs = []
        for k in range(10):
            a = k / 10 * math.tau + math.pi / 2; rr = r * (0.92 if k % 2 == 0 else 0.37)
            if side: p = (c[0] + side * 0.012, c[1] + rr * math.sin(a), c[2] + rr * math.cos(a))
            else: p = (c[0] + rr * math.cos(a), c[1] + 0.012, c[2] + rr * math.sin(a))
            vs.append(bm.verts.new(T(*p)))
        bm.faces.new(vs); K._finish(vs, pm("#f2f0ea", 0.6), 0.0)
        for sd in (-1, 1):   # white bars
            if side: K.box((c[0] + side * 0.01, c[1], c[2] + sd * r * 1.25), (0.01, r * 0.42, r * 0.6), pm("#f2f0ea", 0.6), 0.0, 0.0)
            else: K.box((c[0] + sd * r * 1.25, c[1] + 0.01, c[2]), (r * 0.6, 0.01, r * 0.42), pm("#f2f0ea", 0.6), 0.0, 0.0)
def prop_mat():
    def mk():
        m = bpy.data.materials.new("cprop"); m.use_nodes = True; n = m.node_tree.nodes; l = m.node_tree.links
        b = n["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1); b.inputs["Alpha"].default_value = 0.07
        return m
    return mat_once("cprop", mk)
def _engine(K, c, r, L, cowl, prop=True, blades=3, spin=True):
    x, y, z = c
    K.cyl((x, y, z - L / 2), r, L, cowl, 20, "z", r2=r * 0.92)
    K.cyl((x, y, z + 0.02), r * 0.78, 0.06, pm("#1a1a1a", 0.5), 16, "z")
    for k in range(9): K.box((x + r * 0.55 * math.cos(k * 0.7), y + r * 0.55 * math.sin(k * 0.7), z - 0.02), (0.12, 0.12, 0.06), pm("#3a3a3a", 0.4, 0.6), k * 0.7, 0.0)
    if prop:
        K.sphere((x, y, z + 0.18), r * 0.28, pm("#2a2a2a", 0.4, 0.5), 10, (1, 1, 1.4))
        if spin: K.cyl((x, y, z + 0.16), r * 2.6, 0.01, prop_mat(), 28, "z")
        else:
            for k in range(blades):
                a = k / blades * math.tau + 0.3
                K.box((x + math.cos(a) * r * 1.2, y + math.sin(a) * r * 1.2, z + 0.15), (0.16, r * 2.3, 0.03), pm("#1e1e1e", 0.5), 0.0, 0.0, a)
def _gear(K, c, h, m, spat=False):
    x, y, z = c
    K.box((x, y - h / 2, z), (0.08, h, 0.08), m, 0.0, 0.0)
    if spat: K.sphere((x, y - h, z), 0.28, m, 12, (0.5, 0.75, 1.6))
    else: K.cyl((x, y - h, z), 0.3, 0.12, pm("#1a1a1a", 0.7), 14, "x")
PLANES = {}
def plane(kind, gear=False, spin=True):
    """build (once) and return a hidden source mesh object for an aircraft kind; instance with inst() + place()"""
    key = (kind, gear, spin)
    if key in PLANES: return PLANES[key]
    K = Kit(f"pl_{kind}{int(gear)}{int(spin)}")
    glass = mat_once("cglass", lambda: lib.principled("cglass", hexc("#9ab8c8"), 0.05, 0.3))
    if kind in ("zero", "val", "kate"):
        body = mat_once("jpgrey", lambda: worn("jpgrey", "#c4c2a4", "#6a6a5a", 0.5, 0.15, 3, 0.62, "#8a8a70"))
        cowl = pm("#202022", 0.4, 0.3)
        if kind == "zero":
            _fuse(K, [(1.3, 0.62, 0.62, 0), (0.6, 0.66, 0.68, 0.0), (-1.5, 0.6, 0.78, 0.1), (-3.5, 0.42, 0.55, 0.2), (-6.0, 0.18, 0.3, 0.35), (-7.7, 0.04, 0.12, 0.45)], body)
            _wing(K, 12.0, 2.4, 1.2, 0.6, 0.3, -0.35, 0.09, 0.14, body, round_tip=0.6)
            _fin(K, 1.5, 1.5, 0.7, -6.2, 0.6, 0.35, 0.07, body); _wing(K, 4.8, 1.3, 0.7, -6.4, 0.25, 0.4, 0.0, 0.06, body, n=6)
            K.sphere((0, 0.72, -1.6), 0.5, glass, 12, (0.65, 0.8, 3.2)); _engine(K, (0, 0, 1.6), 0.64, 0.8, cowl, spin=spin)
            span, rr = 12.0, 0.55
        elif kind == "val":
            _fuse(K, [(1.4, 0.6, 0.6, 0), (0.6, 0.64, 0.66, 0.0), (-1.5, 0.6, 0.8, 0.1), (-4, 0.42, 0.55, 0.2), (-6.8, 0.18, 0.3, 0.35), (-8.6, 0.04, 0.12, 0.45)], body)
            _wing(K, 14.4, 2.6, 1.2, 0.7, 0.4, -0.35, 0.08, 0.15, body, round_tip=0.7)
            _fin(K, 1.7, 1.6, 0.8, -7.0, 0.6, 0.35, 0.07, body); _wing(K, 5.0, 1.4, 0.8, -7.2, 0.3, 0.4, 0.0, 0.06, body, n=6)
            K.sphere((0, 0.72, -2.2), 0.5, glass, 12, (0.62, 0.78, 4.2)); _engine(K, (0, 0, 1.7), 0.62, 0.8, cowl, spin=spin)
            for sd in (-1, 1): _gear(K, (sd * 1.6, -0.45, 0.4), 1.1, body, spat=True)
            K.box((0, -0.85, -0.6), (0.3, 0.3, 1.6), pm("#2a2a2a", 0.5, 0.5), 0.0, 0.0)
            span, rr = 14.4, 0.6
        else:
            _fuse(K, [(1.4, 0.64, 0.64, 0), (0.6, 0.68, 0.7, 0.0), (-1.5, 0.62, 0.8, 0.1), (-4.5, 0.42, 0.55, 0.2), (-7.4, 0.18, 0.3, 0.35), (-9.0, 0.04, 0.12, 0.45)], body)
            _wing(K, 15.5, 2.8, 1.3, 0.7, 0.4, -0.4, 0.07, 0.16, body, round_tip=0.6)
            _fin(K, 1.8, 1.8, 0.8, -7.4, 0.6, 0.35, 0.07, body); _wing(K, 5.2, 1.5, 0.8, -7.6, 0.3, 0.4, 0.0, 0.06, body, n=6)
            K.sphere((0, 0.72, -2.6), 0.5, glass, 12, (0.62, 0.78, 5.0)); _engine(K, (0, 0, 1.7), 0.66, 0.8, cowl, spin=spin)
            lathe_like = pm("#4a4a46", 0.4, 0.6)
            K.cyl((0, -0.95, -1.2), 0.27, 5.0, lathe_like, 14, "z"); K.sphere((0, -0.95, 1.3), 0.27, lathe_like, 10)
            span, rr = 15.5, 0.62
        for sd in (-1, 1): _roundel(K, (sd * span * 0.33, 0.06 + 0.09 * span * 0.33 * 0 + 0.0, 0.0 - 0.2), rr, "#c41e24")
        for sd in (-1, 1): _roundel(K, (0.0, 0.3, -4.6), 0.38, "#c41e24", ring="#f2f0ea", side=sd)
        if gear and kind == "zero":
            for sd in (-1, 1): _gear(K, (sd * 1.7, -0.4, 0.3), 1.2, body)
    elif kind in ("sbd", "wildcat"):
        top = mat_once("usblue", lambda: worn("usblue", "#5c6e80", "#3a4450", 0.55, 0.1, 3, 0.62, "#4a5866"))
        cowl = pm("#4e5e6e", 0.5, 0.2)
        if kind == "sbd":
            _fuse(K, [(1.5, 0.66, 0.66, 0), (0.6, 0.7, 0.75, 0.0), (-1.6, 0.62, 0.82, 0.1), (-4.0, 0.42, 0.6, 0.2), (-7.0, 0.2, 0.32, 0.35), (-8.6, 0.05, 0.14, 0.45)], top)
            _wing(K, 12.7, 3.0, 1.3, 0.8, 0.5, -0.4, 0.1, 0.17, top, round_tip=0.5)
            _fin(K, 1.7, 1.8, 0.9, -7.0, 0.7, 0.35, 0.07, top); _wing(K, 5.0, 1.5, 0.8, -7.3, 0.3, 0.4, 0.0, 0.06, top, n=6)
            K.sphere((0, 0.75, -2.3), 0.5, glass, 12, (0.62, 0.8, 4.0)); _engine(K, (0, 0, 1.8), 0.68, 0.9, cowl, spin=spin)
            K.box((0, -0.9, 0.1), (0.4, 0.4, 2.0), pm("#2a2a2a", 0.5, 0.5), 0.0, 0.0)          # the bomb
            span, rr = 12.7, 0.62
        else:
            _fuse(K, [(1.3, 0.72, 0.72, 0), (0.5, 0.78, 0.82, 0.0), (-1.5, 0.66, 0.85, 0.1), (-3.6, 0.42, 0.6, 0.2), (-6.2, 0.18, 0.32, 0.35), (-7.4, 0.05, 0.12, 0.45)], top)
            _wing(K, 11.6, 2.6, 1.4, 0.4, 0.2, -0.3, 0.06, 0.16, top, round_tip=0.3)
            _fin(K, 1.6, 1.6, 0.9, -5.6, 0.6, 0.35, 0.07, top); _wing(K, 4.4, 1.4, 0.8, -5.8, 0.25, 0.4, 0.0, 0.06, top, n=6)
            K.sphere((0, 0.82, -1.5), 0.48, glass, 12, (0.62, 0.8, 2.2)); _engine(K, (0, 0, 1.6), 0.74, 0.8, cowl, spin=spin)
            span, rr = 11.6, 0.6
        for sd in (-1, 1): _roundel(K, (sd * span * 0.32, 0.08, -0.4), rr, "#1e2a5a", star=True)
        for sd in (-1, 1): _roundel(K, (0.0, 0.25, -4.2), 0.42, "#1e2a5a", star=True, side=sd)
        if gear:
            for sd in (-1, 1): _gear(K, (sd * 1.5, -0.4, 0.4), 1.3, top)
    elif kind == "b25":
        od = mat_once("usod", lambda: worn("usod", "#5c5a3a", "#3a3826", 0.6, 0.05, 2, 0.6, "#4a4830"))
        _fuse(K, [(8.0, 0.25, 0.35, 0.1), (7.0, 0.75, 0.85, 0.0), (4.0, 0.85, 1.0, 0.1), (-2.0, 0.82, 1.0, 0.1), (-6.0, 0.6, 0.8, 0.25), (-8.2, 0.3, 0.45, 0.4)], od)
        K.sphere((0, 0.1, 7.6), 0.78, glass, 14, (0.95, 1.05, 1.0))
        _wing(K, 20.6, 4.0, 1.6, 1.8, 0.6, 0.35, 0.03, 0.3, od, round_tip=0.4, tip_up=0.0)
        for sd in (-1, 1):
            K.cyl((sd * 3.3, 0.25, 0.4), 0.66, 4.0, od, 18, "z", r2=0.5)
            _engine(K, (sd * 3.3, 0.25, 2.6), 0.7, 0.8, od, spin=spin)
        _wing(K, 6.8, 1.8, 1.4, -6.6, 0.1, 0.6, 0.0, 0.08, od, n=6)
        for sd in (-1, 1): _fin(K, 2.2, 1.6, 1.0, -6.9, 0.3, 0.1, 0.08, od, x=sd * 3.4)
        K.sphere((0, 1.0, 4.4), 0.55, glass, 12, (1.0, 0.7, 1.8))
        for sd in (-1, 1): _roundel(K, (sd * 7.5, 0.45, 0.6), 0.7, "#1e2a5a", star=True)
        for sd in (-1, 1): _roundel(K, (0, 0.3, -3.4), 0.55, "#1e2a5a", star=True, side=sd)
        if gear:
            for sd in (-1, 1): _gear(K, (sd * 3.3, -0.2, 0.8), 1.8, od)
            _gear(K, (0, -0.4, 6.0), 1.4, od)
    elif kind == "b29":
        al = mat_once("usal", lambda: lib.principled("usal", hexc("#b8bcc0"), 0.32, 0.85))
        _fuse(K, [(14.5, 0.2, 0.2, 0.3), (14.0, 1.2, 1.2, 0.2), (12.0, 1.45, 1.45, 0.0), (-8.0, 1.45, 1.45, 0.0), (-13.0, 0.9, 1.0, 0.4), (-15.0, 0.25, 0.4, 0.7)], al)
        K.sphere((0, 0.15, 13.4), 1.35, glass, 16, (1.0, 1.0, 1.1))
        _wing(K, 43.0, 6.0, 2.2, 3.5, 2.8, 0.0, 0.04, 0.45, al, n=12, round_tip=0.4)
        for sx in (-11.0, -5.2, 5.2, 11.0):
            K.cyl((sx, -0.1, 2.2), 0.85, 5.0, al, 18, "z", r2=0.6); _engine(K, (sx, -0.1, 4.6), 0.9, 1.0, al, spin=spin, blades=4)
        _wing(K, 13.0, 3.6, 1.6, -11.5, 0.6, 0.8, 0.0, 0.12, al, n=6)
        _fin(K, 6.0, 5.5, 2.2, -10.8, 2.2, 1.0, 0.14, al)
        for sd in (-1, 1): _roundel(K, (sd * 14.0, 0.75, 0.6), 1.0, "#1e2a5a", star=True)
        for sd in (-1, 1): _roundel(K, (0, 0.3, -8.0), 0.9, "#1e2a5a", star=True, side=sd)
    o = K.build()[0]; o.location = T(0, -500, 0); PLANES[key] = o
    return o
SPANS = {"zero": 12.0, "val": 14.4, "kate": 15.5, "sbd": 12.7, "wildcat": 11.6, "b25": 20.6, "b29": 43.0}

# ------------------------------------------------------------------ ships
def us_flag_mat(): return mat_once("usflag", lambda: ikit.img_mat("usflag", ikit.flag_img("us"), 0.8))
def jp_flag_mat(): return mat_once("jpflag", lambda: ikit.img_mat("jpflag", ikit.flag_img("jp"), 0.8))
def us_battleship(n, x, z, yaw, L=180, Bm=30, train=0.0, smoke=False):
    before = set(bpy.data.objects.keys())
    FR.warship(n, x, z, yaw, L, Bm, "battleship", train)
    names = sorted(set(bpy.data.objects.keys()) - before); keep = []
    for k in names:
        o = bpy.data.objects[k]
        if k.startswith(f"{n}ensign"): o.data.materials[0] = us_flag_mat()
        if k.startswith(f"{n}jack"): o.data.materials[0] = pmat("usjack", "#2a3070", 0.8)
        if not smoke and k.startswith(f"{n}smk"): bpy.data.objects.remove(o)
        else: keep.append(o)
    return keep

def clone(objs, dx, dz, prefix, dy=0.0):
    """linked copies of a group of objects shifted by (dx, dy, dz) three metres (fast: no new geometry)"""
    off = T(dx, dy, dz); out = []
    for o in objs:
        c = o.copy(); c.name = prefix + o.name; link(c); c.location = o.location + off; out.append(c)
    return out
def deck_paint(name, L, B, jp, mark=None):
    """flight deck: planks along the ship, centre / edge stripes, elevator outlines, a hinomaru (JP) or hull number (US)"""
    W, H = 1024, int(1024 * B / L) // 4 * 4
    a = ikit.canvas(H, W, "#8a7a5e" if jp else "#6a6658"); x, y = ikit.grid(a)
    nz = ikit.vnoise(H, W, 40, 3, 3); a *= (0.88 + 0.22 * nz)[..., None]
    for k in range(int(B / 0.25)): ikit.put(a, np.abs(y - k / (B / 0.25)) < 0.0012 * L / B, "#4a3e2e", 0.5)
    ikit.put(a, (np.abs(y - 0.5) < 0.18 / B) & ((np.sin(x * 140) > 0) if jp else (np.sin(x * 90) > -0.4)), "#f2ece0", 0.85)
    ikit.put(a, (np.abs(y - 0.04) < 0.1 / B) | (np.abs(y - 0.96) < 0.1 / B), "#f2ece0", 0.6)
    for ex in (0.28, 0.5, 0.74): ikit.put(a, (np.abs(np.abs(x - ex) - 0.03) < 0.0016) & (np.abs(y - 0.5) < 0.18) | (np.abs(np.abs(y - 0.5) - 0.18) < 0.004 * L / B) & (np.abs(x - ex) < 0.03), "#2a2420", 0.7)
    if jp:
        ikit.ellipse(a, 0.86, 0.5, 0.045, 0.045 * L / B, "#f2ece0"); ikit.ellipse(a, 0.86, 0.5, 0.03, 0.03 * L / B, "#c41e24")
        for k in range(10): ikit.put(a, (np.abs(x - (0.04 + k * 0.006)) < 0.0015), "#f2ece0", 0.8)
    elif mark: ikit.stamp(a, mark, 0.86, 0.32, 0.36, "#f2ece0", 0.9, 0.1, "center")
    ikit.shade(a, 0.06, 5, 30)
    return a
def carrier(n, x, z, yaw, L=230, Bm=26, jp=True, mark="8", deck_h=14.0, deckm=None):
    """carrier: lofted hull, open hangar sides, overhanging flight deck (deck top y = deck_h), island, AA galleries.
    ship-local: bow +x, starboard +z.  Returns the deck-to-three transform helper P."""
    c, s = math.cos(yaw), math.sin(yaw)
    P = lambda lx, ly, lz: (x + lx * c + lz * s, ly, z - lx * s + lz * c)
    grey = mat_once("cvgrey" + ("j" if jp else "u"), lambda: worn("cvgrey" + ("j" if jp else "u"), "#6e747a" if jp else "#5e6a76", "#3a4046", 0.55, 0.2, 0.5, 0.66, "#4e555c"))
    dk = mat_once("shipdk", lambda: lib.principled("shipdk", hexc("#2c3036"), 0.5, 0.3)); black = pmat("cvblack", "#141416", 0.6)
    rings, uvs = [], []; NS = 36
    for i in range(NS + 1):
        t = i / NS; lx0 = (t - 0.5) * L
        w = Bm / 2 * (0.5 + 0.5 * smooth(0.0, 0.2, t)) * max(0.06, 1 - (max(0.0, t - 0.62) / 0.38) ** 1.8)
        top = 6.0 + 1.5 * smooth(0.6, 1.0, t); keel = -4.0 + 3.6 * smooth(0.88, 1.0, t)
        side = []
        for u in (0.0, 0.1, 0.25, 0.45, 0.7, 1.0):
            yy = keel + (top - keel) * u; g = math.sin(min(1.0, u / 0.35) * math.pi / 2) ** 0.55
            rake = 0.06 * L * smooth(0.88, 1.0, t) * u ** 1.3; side.append((lx0 + rake, yy, w * g))
        rings.append([P(a, yy, -hw) for a, yy, hw in side[::-1]] + [P(a, yy, hw) for a, yy, hw in side[1:]])
        uvs += [(a, yy) for a, yy, hw in side[::-1]] + [(a, yy) for a, yy, hw in side[1:]]
    FR.loft(f"{n}hull", rings, mat_once(f"hull{L}", lambda: FR.hull_mat(f"hull{L}", L)), True, True, uvs)
    # hangar: closed lower walls with open bays (dark interior), girders up to the flight deck
    hx0, hx1 = -0.42 * L, 0.36 * L; hw = Bm * 0.47
    bx(f"{n}hangar", P((hx0 + hx1) / 2, 6.0 + (deck_h - 6.5) / 2, 0), ((hx1 - hx0), deck_h - 6.5, hw * 2 - 1.0), black, 0.0, yaw)
    for k in range(int((hx1 - hx0) / 7)):
        lx = hx0 + 3.5 + k * 7
        for sd in (-1, 1): bx(f"{n}gird{k}{sd}", P(lx, 6.0 + (deck_h - 6.5) / 2, sd * (hw - 0.6)), (0.8, deck_h - 6.5, 0.9), grey, 0.05, yaw)
    for sd in (-1, 1):
        bx(f"{n}hwall{sd}", P((hx0 + hx1) / 2, 7.6, sd * (hw - 0.4)), (hx1 - hx0, 3.2, 0.5), grey, 0.05, yaw)
        bx(f"{n}hcurt{sd}", P((hx0 + hx1) / 2 + 10, deck_h - 1.6, sd * (hw - 0.3)), (hx1 - hx0 - 30, 1.8, 0.3), grey, 0.05, yaw)
    # flight deck slab + paint, round-down at the stern, supports at the bow
    dl, d0 = 0.96 * L, -0.48 * L; img = deck_paint(f"{n}dk", dl, Bm, jp, mark)
    dm = deckm or ikit.img_mat(f"{n}deckm", img, 0.7)
    vs = [P(d0, deck_h, -Bm / 2), P(d0 + dl, deck_h, -Bm / 2), P(d0 + dl, deck_h, Bm / 2), P(d0, deck_h, Bm / 2)]
    o = mesh_obj(f"{n}deck", vs, [(0, 1, 2, 3)], dm); uv = o.data.uv_layers.new()
    for k, cc in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = cc
    bx(f"{n}deckslab", P(d0 + dl / 2, deck_h - 0.45, 0), (dl, 0.85, Bm), grey, 0.05, yaw)
    for sd in (-1, 1):
        tube(f"{n}catwalk{sd}", [P(d0 + 6, deck_h - 1.2, sd * (Bm / 2 + 0.9)), P(d0 + dl - 8, deck_h - 1.2, sd * (Bm / 2 + 0.9))], 0.08, dk, res=2, bres=0)
        bx(f"{n}cwfloor{sd}", P(d0 + dl / 2, deck_h - 1.6, sd * (Bm / 2 + 0.9)), (dl - 14, 0.15, 1.8), grey, 0.0, yaw)
        for k in range(30): tube(f"{n}stan{sd}{k}", [P(d0 + 6 + k * (dl - 14) / 29, deck_h - 1.6, sd * (Bm / 2 + 1.75)), P(d0 + 6 + k * (dl - 14) / 29, deck_h - 0.6, sd * (Bm / 2 + 1.75))], 0.03, dk, res=1, bres=0)
        tube(f"{n}rail{sd}", [P(d0 + 6, deck_h - 0.6, sd * (Bm / 2 + 1.75)), P(d0 + dl - 8, deck_h - 0.6, sd * (Bm / 2 + 1.75))], 0.03, dk, res=2, bres=0)
    for k in range(4): bx(f"{n}bowpost{k}", P(0.4 * L + k * 1.8, (deck_h + 7) / 2, (k % 2 - 0.5) * Bm * 0.3), (0.5, deck_h - 7, 0.5), grey, 0.0, yaw)
    # AA gun tubs along the deck edges
    for k in range(6):
        for sd in (-1, 1):
            if not jp and sd > 0 and -0.12 * L < (-0.35 + k * 0.14) * L < 0.12 * L: continue
            lx = (-0.35 + k * 0.14) * L; pz = sd * (Bm / 2 + 2.4)
            lathe(f"{n}aat{k}{sd}", [(1.4, 0.0), (1.5, 0.0), (1.5, 1.0), (1.4, 1.0), (1.4, 0.1), (0.0, 0.1)], P(lx, deck_h - 2.2, pz), grey, 14, cap=False)
            for j in range(2): tube(f"{n}aab{k}{sd}{j}", [P(lx + (j - 0.5) * 0.6, deck_h - 1.0, pz), P(lx + (j - 0.5) * 0.6 + 1.2, deck_h + 1.2, pz + sd * 0.8)], 0.07, dk, res=2, bres=0)
    if jp:
        # small island on the starboard side, forward; funnels curving down and out to starboard below the deck
        ix = 0.18 * L; iz = Bm / 2 - 2.0
        bx(f"{n}isl1", P(ix, deck_h + 2.0, iz), (8, 4.0, 3.2), grey, 0.15, yaw)
        bx(f"{n}isl2", P(ix + 0.5, deck_h + 5.2, iz), (5.5, 2.4, 2.8), grey, 0.12, yaw)
        bx(f"{n}islw", P(ix + 0.6, deck_h + 5.6, iz), (5.6, 0.6, 2.9), pmat("cvwin", "#0e1014", 0.1), 0.0, yaw)
        bx(f"{n}isl3", P(ix + 0.8, deck_h + 7.2, iz), (3.0, 1.6, 2.2), grey, 0.1, yaw)
        tube(f"{n}imast", [P(ix + 0.8, deck_h + 8, iz), P(ix + 0.8, deck_h + 15, iz)], 0.15, dk, res=2, bres=0)
        tube(f"{n}iyard", [P(ix + 0.8, deck_h + 13, iz - 2.5), P(ix + 0.8, deck_h + 13, iz + 2.5)], 0.08, dk, res=2, bres=0)
        for k in range(2):
            lx = -0.02 * L - k * 6
            tube(f"{n}funnel{k}", [P(lx, deck_h - 3.0, Bm / 2 - 2), P(lx, deck_h - 3.5, Bm / 2 + 3.5), P(lx, deck_h - 6.5, Bm / 2 + 6)], 1.9 - k * 0.3, grey, res=6, bres=3)
            lathe(f"{n}fcap{k}", [(0.0, 0.0), (1.9 - k * 0.3, 0.0)], P(lx, deck_h - 6.6, Bm / 2 + 6.2), black, 16, cap=False)
        ikit.flag(f"{n}flag", P(-0.47 * L, deck_h + 4.0, 0), 4.5, 3.0, jp_flag_mat(), yaw + math.pi / 2, 0.12)
        tube(f"{n}fstaff", [P(-0.47 * L, deck_h, 0), P(-0.47 * L, deck_h + 4.2, 0)], 0.08, dk, res=2, bres=0)
    else:
        ix = 0.06 * L; iz = Bm / 2 - 2.6
        bx(f"{n}isl1", P(ix, deck_h + 3.0, iz), (26, 6.0, 4.0), grey, 0.15, yaw)
        bx(f"{n}isl2", P(ix + 4, deck_h + 7.5, iz), (14, 3.0, 3.6), grey, 0.12, yaw)
        bx(f"{n}islw", P(ix + 4.1, deck_h + 8.0, iz), (14.2, 0.9, 3.7), pmat("cvwin", "#0e1014", 0.1), 0.0, yaw)
        bx(f"{n}isl3", P(ix + 5, deck_h + 10.2, iz), (8, 2.4, 3.2), grey, 0.1, yaw)
        bx(f"{n}isl3w", P(ix + 5, deck_h + 10.6, iz), (8.1, 0.6, 3.3), pmat("cvwin", "#0e1014", 0.1), 0.0, yaw)
        lathe(f"{n}funnel", [(0.0, 0.0), (2.6, 0.0), (2.6, 9.0), (2.3, 9.4), (0.0, 9.4)], P(ix - 7, deck_h + 6, iz), grey, 20, yaw=yaw, sx=2.0, sz=0.9)
        lathe(f"{n}fcap", [(2.3, 9.4), (2.0, 9.6)], P(ix - 7, deck_h + 6, iz), black, 20, yaw=yaw, sx=2.0, sz=0.9, cap=True)
        for k, (ox, oz) in enumerate(((-2, -1.6), (-2, 1.6), (2, 0))): tube(f"{n}tri{k}", [P(ix + 5 + ox, deck_h + 11.5, iz + oz), P(ix + 5, deck_h + 24, iz)], 0.22, dk, res=2, bres=0)
        bx(f"{n}radar", P(ix + 5, deck_h + 25.5, iz), (0.3, 3.0, 4.6), pmat("cvradar", "#3a3e44", 0.5, 0.5), 0.0, yaw)
        for k in range(6): tube(f"{n}rgrid{k}", [P(ix + 4.8, deck_h + 24.0 + k * 0.6, iz - 2.3), P(ix + 4.8, deck_h + 24.0 + k * 0.6, iz + 2.3)], 0.03, dk, res=1, bres=0)
        tube(f"{n}yard", [P(ix + 5, deck_h + 21, iz - 4), P(ix + 5, deck_h + 21, iz + 4)], 0.1, dk, res=2, bres=0)
        isd = mat_once("cvisd", lambda: lib.principled("cvisd", hexc("#3a4048"), 0.5, 0.3))
        for k in range(9): bx(f"{n}port{k}", P(ix - 11 + k * 2.6, deck_h + 2.4, iz - 2.02), (0.5, 0.5, 0.06), pmat("cvwin", "#0e1014", 0.1), 0.0, yaw)
        for k in range(3): bx(f"{n}door{k}", P(ix - 9 + k * 8, deck_h + 1.1, iz - 2.03), (1.0, 2.0, 0.06), isd, 0.02, yaw)
        for k in range(2):
            bx(f"{n}plat{k}", P(ix + 4 + k * 2, deck_h + 6.05 + k * 3.1, iz - 2.6), (14 - k * 5, 0.15, 1.6), grey, 0.0, yaw)
            for j in range(12 - k * 4): tube(f"{n}pr{k}{j}", [P(ix - 3 + k * 2 + j * 1.2, deck_h + 6.1 + k * 3.1, iz - 3.35), P(ix - 3 + k * 2 + j * 1.2, deck_h + 7.1 + k * 3.1, iz - 3.35)], 0.03, dk, res=1, bres=0)
            tube(f"{n}prr{k}", [P(ix - 3 + k * 2, deck_h + 7.1 + k * 3.1, iz - 3.35), P(ix + 11 - k * 3, deck_h + 7.1 + k * 3.1, iz - 3.35)], 0.03, dk, res=2, bres=0)
        for j in range(10): bx(f"{n}lad{j}", P(ix + 12.5, deck_h + 0.5 + j * 0.55, iz - 2.1), (0.8, 0.05, 0.1), dk, 0.0, yaw)
        for k in range(3): lathe(f"{n}slamp{k}", [(0.0, 0.0), (0.45, 0.0), (0.5, 0.7), (0.0, 0.75)], P(ix + 2 + k * 3, deck_h + 12.3, iz - 1.2), grey, 14)
        for k, (lab, x_) in enumerate(((mark, ix - 2),)): ktext(lab, P(x_, deck_h + 3.4, iz - 2.08), 2.6, pmat("cvnum", "#f2efe6", 0.6), yaw, "sans", 0.02)
        for k in range(4): bx(f"{n}gun5{k}", P((-0.4 + (k % 2) * 0.75) * L, deck_h - 0.2, (1 if k < 2 else -1) * (Bm / 2 + 2.2)), (3.0, 1.6, 3.0), grey, 0.1, yaw)
        tube(f"{n}fstaff", [P(-0.47 * L, deck_h, -Bm * 0.3), P(-0.47 * L, deck_h + 6.5, -Bm * 0.3)], 0.08, dk, res=2, bres=0)
        ikit.flag(f"{n}flag", P(-0.47 * L, deck_h + 6.4, -Bm * 0.3), 3.8, 2.0, us_flag_mat(), yaw + math.pi / 2, 0.12)
    return P

# ------------------------------------------------------------------ land
def palm_srcs(rnd):
    L1 = leaf_mat("cpalm1", "#4a8a2a", "#22501a", (0.6, 0.85, 0.25)); L2 = leaf_mat("cpalm2", "#6a9a32", "#2e5a1a", (0.7, 0.9, 0.3))
    pf = [frond(f"cpf{k}", 3.4 + k * 0.6, L1 if k % 2 else L2, 0.62, 28, 0.25, 50 + k, palm=True) for k in range(3)]
    for o in pf: o.location = T(0, -400, 0)
    return pf
def palm(name, x, y0, z, h, lean, yaw, frsrc, trunk, rnd, s=1.0, nuts=True):
    c_, s_ = math.cos(yaw), math.sin(yaw)
    pts = [(x + lean * h * f * f * c_, y0 + h * f, z - lean * h * f * f * s_) for f in (0, 0.33, 0.66, 1.0)]
    tube(f"{name}t", pts, 0.2 * s, trunk, res=6, bres=2, taper=lambda f: 1 - 0.4 * f)
    for k in range(11):
        o = frsrc[rnd.randrange(len(frsrc))].copy(); o.name = f"{name}f{k}"; link(o); o.location = T(*pts[-1])
        o.rotation_euler = (0, -rnd.uniform(-0.25, 0.1), k / 11 * math.tau + rnd.random() * 0.3); sc = rnd.uniform(0.85, 1.1) * s; o.scale = (sc, sc, sc)
    if nuts:
        nm = pmat("cnut", "#5a6a24", 0.6)
        for k in range(4): puff(f"{name}n{k}", (pts[-1][0] + 0.2 * s * math.cos(k * 1.6), pts[-1][1] - 0.3 * s, pts[-1][2] + 0.2 * s * math.sin(k * 1.6)), (0.14 * s, 0.17 * s, 0.14 * s), nm, k, True)
def palm_trunk(): return mat_once("cpalmtr", lambda: lib.brickmat("cpalmtr", "#8a7a5a", "#6a5a40", "#4a3e2a", 3.0, 3.0, 0.08, 0.9))
def heightfield(name, x0, x1, z0, z1, st, fn, mat):
    nx, nz = int((x1 - x0) / st) + 1, int((z1 - z0) / st) + 1
    vs = [T(x0 + i * st, fn(x0 + i * st, z0 + j * st), z0 + j * st) for j in range(nz) for i in range(nx)]
    fs = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(nz - 1) for i in range(nx - 1)]
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs); me.update()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(mat); return link(bpy.data.objects.new(name, me))
def green_hill_mat(name, a="#3a6a24", b="#22421a", rock="#6a5a46"):
    m = lib.principled(name, hexc(a), 0.85); t, n, l = lib.nodes(m); bsdf = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.02; nz.inputs["Detail"].default_value = 10; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 0.3; fn.inputs["Detail"].default_value = 8; l.new(tc.outputs["Object"], fn.inputs["Vector"])
    r = lib.ramp(n, l, nz.outputs["Fac"], [(0.35, hexc(b)), (0.55, hexc(a)), (0.72, hexc(rock))])
    mu = n.new("ShaderNodeMix"); mu.data_type = "RGBA"; mu.blend_type = "MULTIPLY"; mu.inputs[0].default_value = 0.4; l.new(r.outputs["Color"], mu.inputs[6]); l.new(fn.outputs["Color"], mu.inputs[7])
    l.new(mu.outputs[2], bsdf.inputs["Base Color"]); lib.bump(n, l, fn.outputs["Fac"], 0.8, 0.5)
    return m
def ridge_fn(x0, x1, base, peak, seed=0, scale=0.012):
    def f(x, z):
        u = smooth(0, 1, (z - x0) / max(1e-6, x1 - x0))
        return base + peak * u * (0.6 + 0.6 * noise.noise(Vector((x * scale, z * scale, seed)))) + 6 * noise.noise(Vector((x * 0.06, z * 0.06, seed + 3)))
    return f

# ------------------------------------------------------------------ effects
_PUFF = {}
def puff(name, c, size, mat, seed=0, shadow=False):
    """fast soft blob: linked copy of a cached displaced sphere (no bpy.ops), scaled per instance"""
    me = _PUFF.get((mat.name, seed % 4))
    if me is None:
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=1.0)
        for v in bm.verts:
            v.co *= 1.0 + 0.22 * noise.noise(v.co * 1.6 + Vector((seed % 4 * 3.1, 0, 0))) + 0.08 * noise.noise(v.co * 4.0)
        me = bpy.data.meshes.new(f"puff{len(_PUFF)}"); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        me.materials.append(mat); _PUFF[(mat.name, seed % 4)] = me
    o = link(bpy.data.objects.new(name, me)); o.location = T(*c); o.scale = (size[0], size[2], size[1])
    o.rotation_euler = (0, 0, seed * 1.3); o.visible_shadow = shadow
    return o
def smoke(name, c, h, r0, r1, col="#1e1a18", dens=0.85, drift=(0.0, 0.0), seed=0, puffs=10):
    """rising smoke column: overlapping soft puffs widening with height, drifting with the wind"""
    smm = mat_once("csmk" + col + str(dens), lambda: smoke_mat("csmk" + col, col, dens))
    rnd = random.Random(seed); out = []
    puffs = max(puffs, int(2.2 * h / max(1e-3, r0 + r1)) + 2)
    for k in range(puffs):
        f = k / max(1, puffs - 1); rr = (r0 + (r1 - r0) * f) * rnd.uniform(0.7, 1.05)
        p = (c[0] + drift[0] * f * f + rnd.uniform(-0.2, 0.2) * rr, c[1] + h * f, c[2] + drift[1] * f * f + rnd.uniform(-0.2, 0.2) * rr)
        out.append(puff(f"{name}{k}", p, (rr, rr * rnd.uniform(0.85, 1.15), rr * 0.85), smm, seed + k))
    return out
def splash(name, c, h, r):
    """bomb / shell splash: a white water column with a spray crown"""
    fm = mat_once("csplash", lambda: smoke_mat("csplash", "#eef4f6", 0.95))
    o1 = lathe(f"{name}a", [(r * 1.6, 0.0), (r, h * 0.12), (r * 0.7, h * 0.5), (r * 0.9, h * 0.85), (r * 1.4, h * 0.95), (r * 0.6, h), (0.0, h * 1.02)], c, fm, 16)
    for v in o1.data.vertices: v.co.x += 0.25 * r * math.sin(v.co.z * 0.4 + v.co.y); v.co.y += 0.25 * r * math.cos(v.co.z * 0.3 + v.co.x)
    o2 = puff(f"{name}b", (c[0], c[1] + h * 0.92, c[2]), (r * 1.8, r * 0.9, r * 1.8), fm, 3)
    for o in (o1, o2): o.visible_shadow = False
    return [o1, o2]
def fireball(name, c, size, seed=0, energy=None):
    """a fire: many thin licking tongues of different heights (no cones, no balls) + a warm light; returns its objects"""
    rnd = random.Random(seed); out = []
    inner = mat_once("cflame_i", lambda: flame_mat("cflame_i", (1.0, 0.62, 0.18), (1.0, 0.2, 0.02), 2.2))
    outer = mat_once("cflame_o", lambda: flame_mat("cflame_o", (1.0, 0.35, 0.05), (0.7, 0.08, 0.0), 1.4))
    for k in range(14):
        a = rnd.random() * math.tau; d = rnd.random() ** 0.7 * 0.55 * size
        h = size * (0.5 + rnd.random() * 0.9) * (1.25 if d < 0.25 * size else 0.75)
        out.append(flame(f"{name}f{k}", (c[0] + d * math.cos(a), c[1], c[2] + d * math.sin(a)), h, size * (0.07 + rnd.random() * 0.07), inner if k % 3 else outer,
                         lean=(rnd.random() - 0.5) * 0.6, seed=seed * 7 + k))
    lo = lib.light("POINT", T(c[0], c[1] + size * 0.8, c[2]), energy or 400 * size * size, (1.0, 0.5, 0.18), size * 0.5)
    lo.visible_camera = False; lo.visible_glossy = False; out.append(lo)
    return out
def show(objs, on):
    for o in objs:
        o.hide_render = not on
        if o.type == "LIGHT": o.hide_render = not on

def wake(n, P, L, Bm, speed=1.0):
    """bow wave, side foam and a churned wake behind a moving ship (ship-local P from carrier())"""
    foam = mat_once("ffoam", FR.foam_mat)
    for sd in (-1, 1):
        rings_ = []
        for k in range(8):
            f = k / 7; lx = 0.5 * L + 0.04 * L - f * 0.35 * L
            hgt = 2.2 * speed * (1 - f) ** 1.5; hw = Bm * 0.32 * (0.2 + 0.8 * min(1, f * 3))
            rings_.append([P(lx, -0.24, sd * (hw + 0.4 + 9 * f * speed)), P(lx, hgt * 0.6 - 0.2, sd * (hw + 0.3 + 3 * f)), P(lx, hgt - 0.2, sd * (hw + 0.1 + 0.8 * f))])
        FR.loft(f"{n}bow{sd}", rings_, foam, False, False)
        vs = [P(0.25 * L, -0.22, sd * (Bm * 0.45)), P(-0.5 * L, -0.22, sd * (Bm * 0.45)), P(-0.9 * L, -0.22, sd * Bm * 0.9), P(-1.6 * L, -0.22, sd * Bm * 1.6),
              P(-1.6 * L, -0.22, sd * Bm * 1.75), P(-0.6 * L, -0.22, sd * Bm * 0.75), P(0.2 * L, -0.22, sd * (Bm * 0.6))]
        mesh_obj(f"{n}foam{sd}", vs, [tuple(range(len(vs)))], foam)
    mesh_obj(f"{n}wake", [P(-0.48 * L, -0.21, -Bm * 0.3), P(-0.48 * L, -0.21, Bm * 0.3), P(-2.0 * L, -0.21, Bm * 0.9), P(-2.0 * L, -0.21, -Bm * 0.9)], [(0, 1, 2, 3)], foam)
def deck_props(K, P, deck_h, x0, x1, Bm, rnd, jp=True):
    """flight-deck clutter: wheel chocks, fuel hoses, fire extinguishers, ammo boxes, tie-down rings, a tow tractor"""
    red = pm("#a8282a", 0.5, 0.2); yel = pm("#d8b030", 0.5); olive = pm("#4a4a36", 0.6); hose = pm("#1a1a1a", 0.7); steel = pm("#5a5e62", 0.4, 0.6)
    for k in range(40):
        lx = rnd.uniform(x0, x1); lz = rnd.uniform(-Bm * 0.45, Bm * 0.45)
        K.cyl(P(lx, deck_h + 0.01, lz), 0.08, 0.02, steel, 8)
    for k in range(10):
        lx = x0 + (x1 - x0) * k / 9; sd = 1 if k % 2 else -1
        K.cyl(P(lx, deck_h + 0.35, sd * (Bm / 2 - 0.5)), 0.12, 0.7, red, 12); K.cyl(P(lx, deck_h + 0.75, sd * (Bm / 2 - 0.5)), 0.04, 0.12, pm("#1a1a1a", 0.5), 8)
    for k in range(8):
        lx = rnd.uniform(x0, x1); sd = rnd.choice((-1, 1))
        K.box(P(lx, deck_h + 0.2, sd * (Bm / 2 - 1.2)), (0.9, 0.4, 0.5), olive, rnd.uniform(-0.2, 0.2), 0.02)
        K.box(P(lx + 1.0, deck_h + 0.15, sd * (Bm / 2 - 1.3)), (0.6, 0.3, 0.4), olive if k % 2 else yel, rnd.uniform(-0.3, 0.3), 0.02)
    for k in range(3):
        lx = rnd.uniform(x0, x1)
        K.box(P(lx, deck_h + 0.45, -Bm * 0.3), (2.2, 0.8, 1.3), yel if not jp else pm("#6a6a5a", 0.5), 0.1, 0.06)
        for sd in (-1, 1):
            for e in (-0.7, 0.7): K.cyl(P(lx + e, deck_h + 0.3, -Bm * 0.3 + sd * 0.7), 0.3, 0.2, hose, 12, "z")

# ------------------------------------------------------------------ jungle edge (plants on any ground function)
from sets.jungle import banana_leaf, heart_leaf
_JS = {}
def jungle_srcs():
    if _JS: return _JS
    L1 = leaf_mat("cj1", "#3e8a24", "#1e4a12"); L2 = leaf_mat("cj2", "#5a9a2a", "#2a5a14", (0.7, 0.9, 0.25)); L3 = leaf_mat("cj3", "#2a6a2a", "#123a14")
    BAN = leaf_mat("cjban", "#6aa832", "#3a6a1a", (0.75, 0.95, 0.3))
    _JS["bl"] = [banana_leaf(f"cbl{k}", 1.9 + k * 0.3, 0.32, BAN, k) for k in range(3)]
    _JS["fr"] = [frond(f"cfr{k}", 1.0 + k * 0.25, [L1, L2, L3][k], 0.17, 22, 0.55, k) for k in range(3)]
    _JS["stem"] = mat_once("cjstem", lambda: worn("cjstem", "#5a7a2a", "#6a4a2a", 0.6, 0.0, 6, 0.6, "#3a4a1a"))
    for o in _JS["bl"] + _JS["fr"]: o.location = T(0, -400, 0)
    return _JS
def _cp(src, name, p, yaw, s, tilt=0.0):
    o = src.copy(); o.name = name; link(o); o.location = T(*p); o.rotation_euler = (0, -tilt, yaw); o.scale = (s, s, s); return o
def banana(name, x, z, h, gfn, rnd):
    J = jungle_srcs(); y0 = gfn(x, z)
    tube(f"{name}st", [(x, y0, z), (x + 0.05, y0 + h * 0.5, z), (x + 0.1, y0 + h, z)], 0.11, J["stem"], res=4, bres=2, taper=lambda f: 1 - 0.3 * f)
    for k in range(7): _cp(rnd.choice(J["bl"]), f"{name}l{k}", (x + 0.1, y0 + h - 0.1, z), k / 7 * math.tau + rnd.random() * 0.5, rnd.uniform(0.8, 1.15), rnd.uniform(-0.15, 0.25))
def fern(name, x, z, gfn, rnd, s=1.0):
    J = jungle_srcs(); y0 = gfn(x, z)
    for k in range(8): _cp(rnd.choice(J["fr"]), f"{name}{k}", (x, y0, z), k / 8 * math.tau + rnd.random() * 0.4, s * rnd.uniform(0.7, 1.15))
def jungle_wall(name, x0, x1, z0, z1, gfn, rnd, n=40, trees=10, palms=None, trunk=None):
    """a dense jungle edge in the box: rain-forest trunks, bananas, ferns, palms"""
    bark = mat_once("cjbark", lambda: worn("cjbark", "#5a4632", "#3a2a1a", 0.9, 0.0, 3, 0.55, "#3e5a1a"))
    for k in range(trees):
        x, z = rnd.uniform(x0, x1), rnd.uniform(z0, z1); r = rnd.uniform(0.3, 0.6); y0 = gfn(x, z)
        hh_ = rnd.uniform(8, 12); lathe(f"{name}tr{k}", [(r * 2.0, -0.2), (r * 1.3, 0.4), (r, 2.5), (r * 0.85, hh_), (0.0, hh_ + 0.4)], (x, y0, z), bark, 14)
    for k in range(n):
        x, z = rnd.uniform(x0, x1), rnd.uniform(z0, z1)
        if k % 2 == 0: banana(f"{name}b{k}", x, z, rnd.uniform(2.2, 3.6), gfn, rnd)
        else: fern(f"{name}f{k}", x, z, gfn, rnd, rnd.uniform(1.2, 2.2))
    if palms:
        for k in range(max(3, n // 6)):
            x, z = rnd.uniform(x0, x1), rnd.uniform(z0, z1)
            palm(f"{name}p{k}", x, gfn(x, z), z, rnd.uniform(9, 15), 0.15, rnd.uniform(0, 6), palms, trunk, rnd, 1.1, nuts=False)
    canopy = mat_once("cjcan", lambda: leaf_mat("cjcan", "#2a5a1a", "#14300c"))
    for k in range(max(4, trees)):
        x, z = rnd.uniform(x0, x1), rnd.uniform(z0, z1)
        puff(f"{name}c{k}", (x, gfn(x, z) + rnd.uniform(7, 11), z), (rnd.uniform(4, 7), rnd.uniform(2.5, 4), rnd.uniform(4, 7)), canopy, k, True)
def bicycle():
    """a 1940s roadster bicycle along +z (local), wheels touching y 0; built once, instance with inst()/place()"""
    if ("bike",) in PLANES: return PLANES[("bike",)]
    K = Kit("bike"); fr = pm("#2a2a26", 0.4, 0.5); tyre = pm("#141414", 0.8); chrome = pm("#b8bcc0", 0.2, 1.0)
    for z in (-0.55, 0.55):
        K.torus((0, 0.34, z), 0.34, 0.025, tyre, 28, 6, "x"); K.torus((0, 0.34, z), 0.31, 0.008, chrome, 28, 4, "x")
        for k in range(8): K.box((0, 0.34, z), (0.004, 0.6, 0.004), chrome, 0.0, 0.0, k * math.pi / 8)
    for a, b in (((0, 0.34, -0.55), (0, 0.85, -0.12)), ((0, 0.34, -0.55), (0, 0.4, 0.05)), ((0, 0.4, 0.05), (0, 0.85, -0.12)), ((0, 0.85, -0.12), (0, 0.9, 0.45)),
                 ((0, 0.4, 0.05), (0, 0.9, 0.45)), ((0, 0.34, 0.55), (0, 1.0, 0.48))):
        A, B = Vector(a), Vector(b); d = B - A; L = d.length
        n_ = 6
        for i in range(n_):
            p = A + d * ((i + 0.5) / n_); K.box(tuple(p), (0.03, 0.03, L / n_ + 0.01), fr, 0.0, 0.0, math.atan2(-d.y, d.z))
    K.box((0, 0.95, -0.14), (0.12, 0.05, 0.24), pm("#3a2418", 0.6), 0.0, 0.01)
    K.cyl((0, 1.02, 0.48), 0.012, 0.56, chrome, 8, "x"); K.cyl((0, 0.4, 0.05), 0.09, 0.02, fr, 14, "x")
    K.box((0, 0.62, 0.62), (0.3, 0.12, 0.3), wood("#8a6a3a", "#5a4020", 8.0, 0.7), 0.0, 0.01)
    o = K.build()[0]; o.location = T(0, -500, 0); PLANES[("bike",)] = o
    return o
