# Shared kit for the chapter 9 / 10 / 12 sets (c09_*, c10_*, c12_*): heightfield terrain, snow / sand / steppe / concrete
# materials, snow dusting on any material, WW2 vehicles with real silhouettes (T-34, Tiger, desert Panzer, Sherman via
# front.tank, 25-pounder field gun, Soviet AT gun, trucks), small soldier props and lofted solids. three.js layout
# coordinates in (y up), Blender objects out. Blender 4.5 + 5.x safe.
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import (lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, flame, flame_mat, smoke_mat, smoke_column, text)

import bmesh
def _obj(name, bm, m, smooth=False, bev=0.0, segs=2):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    me.materials.append(m); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if bev:
        md = o.modifiers.new("b", "BEVEL"); md.width = bev; md.segments = segs; md.limit_method = "ANGLE"
    return o
def bx(name, c, s, m, bev=0.01, yaw=0.0):
    """box centred on three point c, three-ordered size, yaw about +y (no bpy.ops: fast for thousands of props)"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((s[0], s[2], s[1], 1.0)))
    o = _obj(name, bm, m, False, bev); o.location = T(*c); o.rotation_euler = (0, 0, yaw); return o
def cy(name, c, r, h, m, verts=20, rot=(0, 0, 0), bev=0.005):
    """cylinder centred on three point c along Blender z, then Blender-euler rot (as lib.cyl)"""
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r, radius2=r, depth=h)
    o = _obj(name, bm, m, True, bev if bev and r > 0.03 else 0.0); o.location = T(*c); o.rotation_euler = rot; return o
# ---- fast replacements for lib's bpy.ops primitives (ops get slower with every object in the scene: a set of ~2000
# objects spent most of its build time in them). Same signatures and results; patched into lib for this process only.
def _fbox(name, loc, size, mat, bevel=0.01, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((size[0], size[1], size[2], 1.0)))
    o = _obj(name, bm, mat, False, bevel); o.location = loc; o.rotation_euler = rot; return o
def _fcyl(name, loc, r, h, mat, verts=24, rot=(0, 0, 0), bevel=0.005):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r, radius2=r, depth=h)
    o = _obj(name, bm, mat, True, bevel); o.location = loc; o.rotation_euler = rot; return o
_TEX0 = {}
def _fblob(name, loc, size, mat, rough=0.08, seed=0):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0, matrix=Matrix.Diagonal((size[0], size[1], size[2], 1.0)))
    o = _obj(name, bm, mat, True); o.location = loc
    tex = _TEX0.get(0)
    if tex is None: tex = _TEX0[0] = bpy.data.textures.new("c9cloudsL", "CLOUDS"); tex.noise_scale = 0.3
    d = o.modifiers.new("d", "DISPLACE"); d.texture = tex; d.strength = rough
    return o
_FONT = {}
def _ftext(body, loc, size, mat, rot=(math.radians(90), 0, 0), align="CENTER", extrude=0.004):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.size = size; cu.align_x = align; cu.extrude = extrude
    if "f" not in _FONT:
        import os
        fs = [f for f in ("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf") if os.path.exists(f)]
        _FONT["f"] = bpy.data.fonts.load(fs[0], check_existing=True) if fs else None
    if _FONT["f"]: cu.font = _FONT["f"]
    cu.materials.append(mat); o = bpy.data.objects.new("txt", cu); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot; return o
def _flight(kind, loc, energy, col, size=0.1, rot=(0, 0, 0), size_y=None):
    d = bpy.data.lights.new("L", kind); d.energy = energy; d.color = col
    if kind == "AREA":
        d.shape = "RECTANGLE" if size_y else "SQUARE"; d.size = size
        if size_y: d.size_y = size_y
    elif kind in ("POINT", "SPOT"): d.shadow_soft_size = size
    elif kind == "SUN": d.angle = size
    o = bpy.data.objects.new("L", d); bpy.context.scene.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; return o
lib.box, lib.cyl, lib.blob, lib.text, lib.light = _fbox, _fcyl, _fblob, _ftext, _flight

def sm(a, b, x): t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

# ------------------------------------------------------------------ terrain
def heightfield(name, Hf, x0, x1, z0, z1, st, mat, attr=None):
    """ground mesh y = Hf(x, z) over a grid; attr(x, z) -> 0..1 stored as point colour 'mask' for the material"""
    nx, nz = int((x1 - x0) / st) + 1, int((z1 - z0) / st) + 1
    vs, fs = [], []
    for j in range(nz):
        for i in range(nx):
            x, z = x0 + i * st, z0 + j * st; vs.append(T(x, Hf(x, z), z))
    for j in range(nz - 1):
        for i in range(nx - 1):
            a = j * nx + i; fs.append((a, a + 1, a + nx + 1, a + nx))
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs); me.update()
    for p in me.polygons: p.use_smooth = True
    if attr:
        ca = me.color_attributes.new("mask", "FLOAT_COLOR", "POINT")
        for k, v in enumerate(vs):
            s = attr(-v.x, v.y); ca.data[k].color = (s, s, s, 1)
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me))

def _ground(name, stops, rough=0.85, bscale=0.08, fine=2.0, bump_s=0.6, mask_col=None, mask_k=1.0):
    """generic painted ground: big colour noise through a ramp x fine grain, optional 'mask' attribute tint"""
    m = lib.principled(name, stops[0][1], rough); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord"); big = n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = bscale; big.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], big.inputs["Vector"])
    r = lib.ramp(n, l, big.outputs["Fac"], stops)
    fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = fine; fn.inputs["Detail"].default_value = 10; l.new(tc.outputs["Object"], fn.inputs["Vector"])
    mul = n.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 0.3
    l.new(r.outputs["Color"], mul.inputs[6]); l.new(fn.outputs["Color"], mul.inputs[7]); out = mul.outputs[2]
    if mask_col:
        at = n.new("ShaderNodeAttribute"); at.attribute_name = "mask"
        mk = n.new("ShaderNodeMath"); mk.operation = "MULTIPLY"; mk.inputs[1].default_value = mask_k; l.new(at.outputs["Fac"], mk.inputs[0])
        mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(mk.outputs[0], mx.inputs[0]); l.new(out, mx.inputs[6]); mx.inputs[7].default_value = (*lib.hexc(mask_col), 1)
        out = mx.outputs[2]
    l.new(out, b.inputs["Base Color"])
    lib.bump(n, l, fn.outputs["Fac"], bump_s, 0.05)
    return m, n, l, b, big
def snow_ground(name="c9snow", mask_col="#5a4a40"):
    """trampled snow: blue-white drifts, grey slush, dirty tracks where 'mask' is set"""
    m, n, l, b, big = _ground(name, [(0.3, lib.hexc("#a8b4c4")), (0.5, lib.hexc("#dfe6ee")), (0.7, lib.hexc("#f4f6fa")), (0.85, lib.hexc("#c8d0dc"))], 0.55, 0.12, 3.0, 0.4, mask_col, 0.85)
    try: b.inputs["Subsurface Weight"].default_value = 0.15; b.inputs["Subsurface Radius"].default_value = (0.4, 0.5, 0.8)
    except Exception: pass
    return m
def sand_ground(name="c9sand", mask_col=None):
    m, *_ = _ground(name, [(0.25, lib.hexc("#a8784a")), (0.45, lib.hexc("#c89a62")), (0.6, lib.hexc("#d8b07a")), (0.8, lib.hexc("#e6c48e"))], 0.9, 0.05, 4.0, 0.5, mask_col, 0.7)
    return m
def steppe_ground(name="c9steppe", mask_col="#4a3a26"):
    m, *_ = _ground(name, [(0.25, lib.hexc("#5a5a24")), (0.45, lib.hexc("#7a7a34")), (0.6, lib.hexc("#9a8a44")), (0.8, lib.hexc("#b8a058"))], 0.9, 0.04, 6.0, 0.6, mask_col, 0.9)
    return m
def concrete(name="c9conc", col="#8a8680", dirt="#4a4640"): return mat_once(name, lambda: worn(name, col, dirt, 0.9, 0.0, 2.5, 0.62, "#5a5650"))

def add_snow(m, amount=0.55, col="#eef2f8"):
    """white on the up-facing parts of any material (noise-broken edge); returns m"""
    t, n, l = lib.nodes(m); b = n.get("Principled BSDF")
    if b is None: return m
    src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None
    base = b.inputs["Base Color"].default_value[:]
    geo = n.new("ShaderNodeNewGeometry"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(geo.outputs["Normal"], sp.inputs[0])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 6; l.new(geo.outputs["Position"], nz.inputs["Vector"])
    ad = n.new("ShaderNodeMath"); ad.operation = "MULTIPLY_ADD"; ad.inputs[1].default_value = 0.5; l.new(nz.outputs["Fac"], ad.inputs[0]); l.new(sp.outputs["Z"], ad.inputs[2])
    mr = n.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 1.25 - amount * 0.5; mr.inputs["From Max"].default_value = 1.32 - amount * 0.5; l.new(ad.outputs[0], mr.inputs["Value"])
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(mr.outputs["Result"], mx.inputs[0])
    if src: l.new(src, mx.inputs[6])
    else: mx.inputs[6].default_value = base
    mx.inputs[7].default_value = (*lib.hexc(col), 1); l.new(mx.outputs[2], b.inputs["Base Color"])
    return m

_TEX = {}
def blob3(name, c, size, mat, rough=0.08, seed=0):
    """lumpy blob at three point c with three-ordered size (sx, sy up, sz) - lib.blob without bpy.ops"""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=1.0, matrix=Matrix.Diagonal((size[0], size[2], size[1], 1.0)))
    o = _obj(name, bm, mat, True); o.location = T(*c)
    tex = _TEX.get(seed % 8)
    if tex is None:
        tex = _TEX[seed % 8] = bpy.data.textures.new(f"c9clouds{seed % 8}", "CLOUDS"); tex.noise_scale = 0.3
    d = o.modifiers.new("d", "DISPLACE"); d.texture = tex; d.strength = rough
    return o

# ------------------------------------------------------------------ solids
def P_of(x, z, yaw, y0=0.0, tilt=0.0):
    c, s = math.cos(yaw), math.sin(yaw); R = Matrix.Rotation(tilt, 3, "X")
    def P(lx, ly, lz):
        v = R @ Vector((lx, ly, lz)); return (x + v.x * c + v.z * s, y0 + v.y, z - v.x * s + v.z * c)
    return P
def prism(name, prof, z0, z1, P, mat):
    """side profile [(lx, ly)] (convex, CCW or CW) extruded across lz z0..z1, placed by P"""
    n = len(prof); vs = [P(x, y, z0) for x, y in prof] + [P(x, y, z1) for x, y in prof]
    fs = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    o = mesh_obj(name, vs, fs, mat)
    o.data.validate(); o.data.update()
    bpy.context.view_layer.objects.active = o
    return o
def loft2(name, ring0, y0, ring1, y1, P, mat, cap=True):
    """top-down outlines [(lx, lz)] at heights y0 and y1 (same count) joined into a tapered solid"""
    n = len(ring0); vs = [P(x, y0, z) for x, z in ring0] + [P(x, y1, z) for x, z in ring1]
    fs = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    if cap: fs += [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    return mesh_obj(name, vs, fs, mat)
def wheel(name, P, lx, ly, lz, r, w, mat, yaw, seg=20):
    o = cy(name, P(lx, ly, lz), r, w, mat, seg); o.rotation_euler = (math.radians(90), 0, yaw); return o
def star_decal(name, P, lx, ly, lz, r, mat, side=1):
    pts = []
    for k in range(10):
        a = k / 10 * math.tau + math.pi / 2; rr = r if k % 2 == 0 else r * 0.4
        pts.append(P(lx + rr * math.cos(a), ly + rr * math.sin(a), lz))
    pts.append(P(lx, ly, lz))
    fs = [(k, (k + 1) % 10, 10) if side > 0 else ((k + 1) % 10, k, 10) for k in range(10)]
    return mesh_obj(name, pts, fs, mat)

# ------------------------------------------------------------------ vehicles
def _tracks(n, P, yaw, L, zc, r, nwh, hull, dk, steel, big=False, interleave=False):
    """track run (rounded box) + road wheels + sprocket/idler on both sides at |lz| = zc"""
    for sd in (-1, 1):
        o = bx(f"{n}trk{sd}", P(0, 0.55 if not big else 0.62, sd * zc), (L, 1.05 if not big else 1.2, 0.6 if not big else 0.75), dk, 0.4 if not big else 0.45, yaw)
        sp = (L - 1.4) / (nwh - 1)
        for k in range(nwh):
            lx = -L / 2 + 0.7 + k * sp
            for e in ((0.0,) if not interleave else (-0.12, 0.12)):
                wheel(f"{n}wh{sd}{k}{e}", P, lx + (sp / 2 if e > 0 else 0), r + 0.02, sd * (zc + 0.31 + e * 0.6), r, 0.14, steel, yaw)
            wheel(f"{n}hub{sd}{k}", P, lx, r + 0.02, sd * (zc + 0.4), r * 0.32, 0.06, hull, yaw, 12)
        wheel(f"{n}spr{sd}", P, L / 2 - 0.25, 0.78, sd * (zc + 0.3), 0.32, 0.18, steel, yaw, 14)
        wheel(f"{n}idl{sd}", P, -L / 2 + 0.25, 0.7, sd * (zc + 0.3), 0.3, 0.18, steel, yaw, 14)
def t34(n, x, z, yaw, col="#4e5a32", y0=0.0, tilt=0.0, star=True, burnt=False):
    """T-34/76 (1943 hex turret): sloped glacis and sides, five big road wheels, long 76 mm gun, rear fuel drums; nose +x"""
    hull = mat_once("t34" + col, lambda: worn("t34" + col, col, "#2e3424", 0.6, 0.25, 6, 0.7, "#3a3424")) if not burnt else mat_once("tankburnt2", lambda: worn("tankburnt2", "#2a2420", "#5a2a14", 0.9, 0.3, 8, 0.55, "#141010"))
    dk = mat_once("c9trk", lambda: worn("c9trk", "#2e2a24", "#1a1814", 0.85, 0.3, 9, 0.6, "#4a3e2e"))
    steel = mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    P = P_of(x, z, yaw, y0, tilt)
    prism(f"{n}hull", [(-2.95, 0.5), (2.6, 0.5), (3.05, 0.95), (1.75, 1.55), (-2.4, 1.55), (-2.95, 1.05)], -1.1, 1.1, P, hull)
    for sd in (-1, 1):  # sloped sponsons over the tracks
        prism(f"{n}spon{sd}", [(-2.9, 1.05), (2.95, 1.0), (1.75, 1.52), (-2.4, 1.52)], sd * 1.1, sd * 1.55, P, hull)
    _tracks(n, P, yaw, 5.9, 1.3, 0.42, 5, hull, dk, steel)
    tur = [(1.2, 0.0), (0.7, 1.0), (-0.9, 1.0), (-1.2, 0.5), (-1.2, -0.5), (-0.9, -1.0), (0.7, -1.0)]
    tt = [(0.9, 0.0), (0.45, 0.78), (-0.75, 0.8), (-1.0, 0.4), (-1.0, -0.4), (-0.75, -0.8), (0.45, -0.78)]
    loft2(f"{n}tur", tur, 1.55, tt, 2.3, P, hull)
    lathe(f"{n}mant", [(0.0, -0.3), (0.28, -0.25), (0.3, 0.0), (0.28, 0.25), (0.0, 0.3)], P(1.12, 1.95, 0), hull, 16, yaw=yaw, tilt=Matrix.Rotation(math.radians(90), 3, "Z"))
    tube(f"{n}gun", [P(1.2, 1.95, 0), P(2.8, 1.97, 0), P(4.4, 2.0, 0)], 0.07, steel, res=2, bres=2)
    for sd in (-1, 1): lathe(f"{n}hat{sd}", [(0.0, 0.0), (0.26, 0.0), (0.26, 0.08), (0.0, 0.1)], P(-0.35, 2.3, sd * 0.38), hull, 16)
    for k, lz in enumerate((-0.75, 0.75)):
        wheel(f"{n}drum{k}", P, -2.75, 1.3, lz, 0.22, 0.65, mat_once("c9drum", lambda: worn("c9drum", "#3a3e2a", "#22241a", 0.6, 0.3, 10, 0.6)), yaw + math.pi / 2, 16)
    for sd in (-1, 1):
        bx(f"{n}rail{sd}", P(0.0, 1.62, sd * 0.95), (1.6, 0.05, 0.05), steel, 0.01, yaw)
        bx(f"{n}box{sd}", P(-1.6, 1.25, sd * 1.5), (0.9, 0.3, 0.25), hull, 0.03, yaw)
    if star and not burnt:
        red = pmat("c9redstar", "#b81e1e", 0.6)
        for sd in (-1, 1):
            star_decal(f"{n}star{sd}", P, -0.1, 1.92, sd * 0.92, 0.22, red, sd)
    return P
def tiger(n, x, z, yaw, col="#9a8a5a", camo="#4e5a3a", y0=0.0, tilt=0.0, burnt=False):
    """Tiger I: slab-sided box hull, wide tracks with big interleaved wheels, boxy turret, long 88 with muzzle brake; nose +x"""
    if burnt: hull = mat_once("tankburnt2", lambda: worn("tankburnt2", "#2a2420", "#5a2a14", 0.9, 0.3, 8, 0.55, "#141010"))
    else: hull = mat_once("tiger" + col, lambda: worn("tiger" + col, col, camo, 0.6, 0.2, 1.4, 0.6, "#5a4a30"))
    dk = mat_once("c9trk", lambda: worn("c9trk", "#2e2a24", "#1a1814", 0.85, 0.3, 9, 0.6, "#4a3e2e"))
    steel = mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    P = P_of(x, z, yaw, y0, tilt)
    prism(f"{n}hull", [(-3.1, 0.55), (2.9, 0.55), (3.2, 1.05), (3.0, 1.7), (-3.1, 1.75)], -1.85, 1.85, P, hull)
    bx(f"{n}deck", P(-1.9, 1.78, 0), (2.2, 0.08, 1.6), hull, 0.02, yaw)
    for k in range(4): bx(f"{n}gr{k}", P(-2.6 + k * 0.35, 1.84, 0), (0.18, 0.03, 1.3), dk, 0.01, yaw)
    _tracks(n, P, yaw, 6.3, 1.55, 0.4, 8, hull, dk, steel, big=True, interleave=True)
    for sd in (-1, 1): bx(f"{n}fend{sd}", P(0.1, 1.72, sd * 1.75), (6.2, 0.05, 0.5), hull, 0.02, yaw)
    tr = [(1.1, -0.95), (1.1, 0.95), (-0.6, 1.05), (-1.25, 0.7), (-1.4, 0.0), (-1.25, -0.7), (-0.6, -1.05)]
    loft2(f"{n}tur", tr, 1.78, [(a * 0.96, b * 0.95) for a, b in tr], 2.62, P, hull)
    bx(f"{n}mant", P(1.25, 2.18, 0), (0.35, 0.7, 1.5), hull, 0.08, yaw)
    tube(f"{n}gun", [P(1.4, 2.2, 0), P(3.4, 2.21, 0), P(5.6, 2.23, 0)], 0.085, steel, res=2, bres=2)
    wheel(f"{n}mbz", P, 5.75, 2.23, 0, 0.17, 0.4, steel, yaw + math.pi / 2, 14)
    lathe(f"{n}cup", [(0.0, 0.0), (0.36, 0.0), (0.36, 0.3), (0.3, 0.34), (0.0, 0.35)], P(-0.75, 2.62, -0.5), hull, 20)
    for sd in (-1, 1):
        for k in range(3): bx(f"{n}smk{sd}{k}", P(0.9, 2.4, sd * (0.75 + k * 0.08)), (0.12, 0.12, 0.08), steel, 0.02, yaw)
        bx(f"{n}tool{sd}", P(-0.6, 1.25, sd * 1.88), (2.2, 0.12, 0.1), wood_mat("ftool", "#6a4a2a", "#3a2614", 12, 0.7), 0.02, yaw)
    return P
def panzer(n, x, z, yaw, col="#b89a62", y0=0.0, tilt=0.0, burnt=False, short=True):
    """Panzer III / IV in desert sand: box hull, small road wheels, return rollers, side skirts off, box turret"""
    if burnt: hull = mat_once("tankburnt2", lambda: worn("tankburnt2", "#2a2420", "#5a2a14", 0.9, 0.3, 8, 0.55, "#141010"))
    else: hull = mat_once("pz" + col, lambda: worn("pz" + col, col, "#6a5a3a", 0.65, 0.2, 7, 0.68, "#8a6a40"))
    dk = mat_once("c9trk", lambda: worn("c9trk", "#2e2a24", "#1a1814", 0.85, 0.3, 9, 0.6, "#4a3e2e"))
    steel = mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    P = P_of(x, z, yaw, y0, tilt)
    prism(f"{n}hull", [(-2.8, 0.5), (2.6, 0.5), (2.85, 1.0), (2.4, 1.5), (-2.8, 1.5)], -1.45, 1.45, P, hull)
    bx(f"{n}sup", P(0.6, 1.62, 0), (1.6, 0.25, 2.2), hull, 0.03, yaw)
    _tracks(n, P, yaw, 5.6, 1.25, 0.28, 8, hull, dk, steel)
    for sd in (-1, 1):
        bx(f"{n}fend{sd}", P(0.0, 1.45, sd * 1.35), (5.7, 0.05, 0.62), hull, 0.02, yaw)
        for k in range(3): wheel(f"{n}ret{sd}{k}", P, -1.2 + k * 1.3, 1.12, sd * 1.55, 0.1, 0.1, steel, yaw, 10)
    tr = [(0.9, -0.85), (0.9, 0.85), (-1.1, 0.95), (-1.25, 0.0), (-1.1, -0.95)]
    loft2(f"{n}tur", tr, 1.62, [(0.75, -0.7), (0.75, 0.7), (-1.0, 0.82), (-1.12, 0.0), (-1.0, -0.82)], 2.35, P, hull)
    bx(f"{n}mant", P(0.95, 1.98, 0), (0.25, 0.42, 0.9), hull, 0.05, yaw)
    tube(f"{n}gun", [P(1.05, 1.98, 0), P(2.2 if short else 3.6, 1.99, 0)], 0.08 if short else 0.07, steel, res=2, bres=2)
    bx(f"{n}bin", P(-1.45, 2.0, 0), (0.45, 0.4, 1.4), hull, 0.03, yaw)
    lathe(f"{n}cup", [(0.0, 0.0), (0.3, 0.0), (0.3, 0.26), (0.0, 0.28)], P(-0.75, 2.35, 0), hull, 20)
    for k in range(4): bx(f"{n}jc{k}", P(-2.55, 1.75, -0.6 + k * 0.4), (0.15, 0.42, 0.32), mat_once("fjerry", lambda: worn("fjerry", "#4a5236", "#2a2a22", 0.6, 0.3, 20, 0.6)), 0.03, yaw)
    lathe(f"{n}tyre", [(0.25, -0.12), (0.4, -0.12), (0.4, 0.12), (0.25, 0.12), (0.25, -0.12)], P(2.3, 1.6, 0.9), pmat("ftyre", "#141414", 0.8), 16, yaw=yaw, cap=False)
    return P
def field_gun(n, x, z, yaw, col="#6a6a4a", y0=0.0):
    """British 25-pounder: box trail, round firing platform, two wheels, shield, barrel with muzzle brake; muzzle +x"""
    m = mat_once("gun" + col, lambda: worn("gun" + col, col, "#3a3a2a", 0.6, 0.3, 12, 0.68, "#4a4030"))
    steel = mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    tyre = pmat("ftyre", "#141414", 0.8)
    P = P_of(x, z, yaw, y0)
    lathe(f"{n}plat", [(0.0, 0.0), (1.1, 0.0), (1.1, 0.08), (0.0, 0.08)], P(0, 0, 0), steel, 24)
    for sd in (-1, 1):
        wheel(f"{n}w{sd}", P, 0, 0.6, sd * 0.85, 0.6, 0.22, tyre, yaw, 24); wheel(f"{n}hub{sd}", P, 0, 0.6, sd * 0.92, 0.25, 0.12, m, yaw, 12)
    bx(f"{n}axle", P(0, 0.6, 0), (0.25, 0.2, 1.5), m, 0.03, yaw)
    prism(f"{n}shield", [(0.25, 0.45), (0.25, 1.45), (0.35, 1.5), (0.35, 0.45)], -0.95, 0.95, P, m)
    tube(f"{n}trail", [P(-0.1, 0.55, 0), P(-1.4, 0.35, 0), P(-2.6, 0.08, 0)], 0.13, m, res=2, bres=2)
    bx(f"{n}spade", P(-2.65, 0.15, 0), (0.12, 0.3, 0.6), steel, 0.02, yaw)
    bx(f"{n}cradle", P(0.4, 1.0, 0), (1.1, 0.32, 0.36), m, 0.05, yaw)
    tube(f"{n}brl", [P(0.3, 1.02, 0), P(1.6, 1.04, 0), P(2.6, 1.06, 0)], 0.075, steel, res=2, bres=2)
    bx(f"{n}mbz", P(2.65, 1.06, 0), (0.25, 0.2, 0.24), steel, 0.03, yaw)
    for k in range(6): cy(f"{n}shell{k}", P(-0.6 - (k % 3) * 0.15, 0.2, 1.2 + (k // 3) * 0.15), 0.045, 0.4, mat_once("kbrass", lambda: lib.principled("kbrass", lib.hexc("#c8963a"), 0.28, 1.0)), 10)
    return P
def at_gun(n, x, z, yaw, col="#4e5a32", y0=0.0):
    """Soviet 45 mm / 76 mm divisional gun: split trails, low shield, long thin barrel"""
    m = mat_once("gun" + col, lambda: worn("gun" + col, col, "#2e3424", 0.6, 0.3, 12, 0.68, "#3a3424"))
    steel = mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    P = P_of(x, z, yaw, y0)
    for sd in (-1, 1):
        wheel(f"{n}w{sd}", P, 0, 0.42, sd * 0.7, 0.42, 0.16, pmat("ftyre", "#141414", 0.8), yaw, 20)
        tube(f"{n}tr{sd}", [P(-0.1, 0.42, sd * 0.2), P(-1.2, 0.25, sd * 0.6), P(-2.2, 0.05, sd * 0.95)], 0.07, m, res=2, bres=1)
    prism(f"{n}sh", [(0.2, 0.3), (0.2, 1.1), (0.28, 1.15), (0.28, 0.3)], -0.75, 0.75, P, m)
    tube(f"{n}brl", [P(-0.4, 0.82, 0), P(1.4, 0.84, 0), P(3.0, 0.86, 0)], 0.055, steel, res=2, bres=2)
    return P
def truck(n, x, z, yaw, col="#7a6a46", canvas="#8a7a54", y0=0.0):
    """army lorry: cab with bonnet and mudguards, canvas tilt over the bed, six wheels; nose +x"""
    m = mat_once("truck" + col, lambda: worn("truck" + col, col, "#3a3020", 0.6, 0.25, 8, 0.7, "#4a3a26"))
    cv = mat_once("tilt" + canvas, lambda: lib.cloth("tilt" + canvas, canvas))
    tyre = pmat("ftyre", "#141414", 0.8); glass = pmat("c9glass", "#1a2228", 0.08, 0.3)
    P = P_of(x, z, yaw, y0)
    bx(f"{n}chas", P(0, 0.75, 0), (6.0, 0.25, 1.6), m, 0.03, yaw)
    prism(f"{n}bon", [(1.8, 0.85), (3.0, 0.85), (3.0, 1.55), (1.8, 1.65)], -0.6, 0.6, P, m)
    prism(f"{n}cab", [(0.6, 0.85), (1.8, 0.85), (1.8, 1.7), (1.55, 2.35), (0.6, 2.35)], -1.0, 1.0, P, m)
    bx(f"{n}ws", P(1.66, 2.0, 0), (0.02, 0.5, 1.7), glass, 0.0, yaw)
    bx(f"{n}grill", P(3.02, 1.2, 0), (0.04, 0.6, 0.95), pmat("c9grill", "#2a2a24", 0.5, 0.6), 0.01, yaw)
    for sd in (-1, 1):
        prism(f"{n}mg{sd}", [(2.2, 1.0), (3.1, 1.0), (2.9, 1.25), (2.4, 1.25)], sd * 0.6, sd * 1.05, P, m)
        cy(f"{n}hl{sd}", P(3.05, 1.45, sd * 0.75), 0.12, 0.15, pmat("c9lamp", "#d8d0b8", 0.2, 0.5), 12)
    bx(f"{n}bed", P(-1.4, 1.1, 0), (3.8, 0.5, 2.2), m, 0.03, yaw)
    for k in range(5):
        lx = -3.2 + k * 0.9
        tube(f"{n}hoop{k}", [P(lx, 1.35, -1.08), P(lx, 2.5, -1.08), P(lx, 2.75, 0), P(lx, 2.5, 1.08), P(lx, 1.35, 1.08)], 0.03, pmat("c9hoop", "#3a3424", 0.6), res=4, bres=1)
    prism(f"{n}tilt", [(-3.3, 1.35), (0.45, 1.35), (0.45, 2.55), (0.3, 2.78), (-3.3, 2.78)], -1.12, 1.12, P, cv)
    for lx in (2.1, -0.9, -2.2):
        for sd in (-1, 1): wheel(f"{n}w{lx}{sd}", P, lx, 0.5, sd * 0.95, 0.5, 0.3, tyre, yaw, 20); wheel(f"{n}hb{lx}{sd}", P, lx, 0.5, sd * 1.06, 0.2, 0.1, m, yaw, 10)
    bx(f"{n}spare", P(0.4, 1.2, -1.15), (0.9, 0.9, 0.2), tyre, 0.35, yaw)
    return P

# ------------------------------------------------------------------ small props
def jerrycan(name, c, yaw, col="#4a5236"):
    bx(name, (c[0], c[1] + 0.23, c[2]), (0.34, 0.46, 0.17), mat_once("jc" + col, lambda: worn("jc" + col, col, "#2a2a22", 0.6, 0.3, 20, 0.6)), 0.03, yaw)
    cy(f"{name}c", (c[0] + 0.1 * math.cos(yaw), c[1] + 0.48, c[2] - 0.1 * math.sin(yaw)), 0.03, 0.05, pmat("c9steelp", "#3a3a34", 0.4, 0.6), 8)
def ammo_box(name, c, yaw, label="", col="#5a5a3a"):
    m = mat_once("ab" + col, lambda: worn("ab" + col, col, "#2a2a1e", 0.6, 0.3, 20, 0.6))
    bx(name, (c[0], c[1] + 0.13, c[2]), (0.32, 0.26, 0.17), m, 0.015, yaw)
    bx(f"{name}h", (c[0], c[1] + 0.27, c[2]), (0.12, 0.02, 0.03), pmat("c9steelp", "#3a3a34", 0.4, 0.6), 0.005, yaw)
def helmet_ground(name, c, yaw, col="#4c5448", kind="stahl"):
    m = mat_once("hg" + col, lambda: worn("hg" + col, col, "#2a2a24", 0.5, 0.3, 30, 0.7))
    if kind == "stahl": prof = [(0.0, 0.2), (0.1, 0.19), (0.15, 0.13), (0.16, 0.05), (0.19, 0.0), (0.2, -0.02)]
    elif kind == "brodie": prof = [(0.0, 0.13), (0.1, 0.12), (0.14, 0.06), (0.16, 0.02), (0.22, 0.0), (0.22, -0.01)]
    else: prof = [(0.0, 0.17), (0.1, 0.16), (0.15, 0.1), (0.17, 0.02), (0.18, -0.02)]
    lathe(name, prof, (c[0], c[1] + 0.02, c[2]), m, 24, yaw=yaw, cap=False, tilt=Matrix.Rotation(0.4, 3, "X"))
def bathtub(name, c, yaw, m=None):
    """cast-iron clawfoot bath, enamel inside; long axis local x"""
    m = m or mat_once("c9bath", lambda: worn("c9bath", "#e8e6de", "#4a4a48", 0.25, 0.1, 6, 0.6, "#8a8070"))
    tc = math.cos(yaw); ts = math.sin(yaw)
    ring = []
    for k in range(24):
        a = k / 24 * math.tau; ring.append((0.85 * math.cos(a) * (1 + 0.08 * (math.cos(a) > 0)), 0.38 * math.sin(a)))
    inner = [(x * 0.9, z * 0.82) for x, z in ring]
    P = P_of(c[0], c[2], yaw, c[1])
    loft2(f"{name}out", [(x * 0.92, z * 0.88) for x, z in ring], 0.18, ring, 0.62, P, m)
    loft2(f"{name}in", inner, 0.62, [(x * 0.92, z * 0.88) for x, z in inner], 0.26, P, pmat("c9enamel", "#f4f2ea", 0.15), cap=True)
    for sx in (-1, 1):
        for sz in (-1, 1): lathe(f"{name}ft{sx}{sz}", [(0.0, 0.0), (0.06, 0.0), (0.04, 0.1), (0.05, 0.2), (0.0, 0.2)], P(sx * 0.6, 0, sz * 0.25), pmat("c9foot", "#2a2a28", 0.4, 0.7), 10)
def blanket_roll(name, c, yaw, col="#6a5a46"):
    o = cy(name, c, 0.11, 0.6, mat_once("bl" + col, lambda: lib.cloth("bl" + col, col)), 14); o.rotation_euler = (math.radians(90), 0, yaw + math.pi / 2)
def sandbags(name, c, yaw, n, rows, seed=0, mat=None):
    """front.sandbag_wall built as one mesh (bevelled pillows, slight jitter)"""
    from sets.front import sandmat
    mat = mat or mat_once("fsand", lambda: sandmat())
    rnd = random.Random(seed); cw, sw = math.cos(yaw), math.sin(yaw); bm = bmesh.new()
    for r in range(rows):
        for k in range(n - (r % 2)):
            lx = (k - (n - 1) / 2 + (0.5 if r % 2 else 0)) * 0.62
            M = Matrix.Translation(T(c[0] + lx * cw, c[1] + 0.12 + r * 0.22, c[2] - lx * sw)) @ Matrix.Rotation(yaw + rnd.uniform(-0.12, 0.12), 4, "Z") @ Matrix.Rotation(rnd.uniform(-0.04, 0.04), 4, "X") @ Matrix.Diagonal((0.6, 0.36, 0.24, 1.0))
            bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    o = _obj(name, bm, mat, True, 0.09, 3); o.modifiers["b"].limit_method = "NONE"; return o
def wire(name, c, L, yaw, h=0.45):
    from sets.warroom import barbed_coil
    barbed_coil(name, c, L, h, yaw, mat_once("fbwire", lambda: worn("fbwire", "#4a4440", "#6a3a1e", 0.5, 0.8, 20, 0.6)), int(L * 3.2))
def rubble(name, c, size, mat, seed=0, n=6):
    rnd = random.Random(seed)
    for k in range(n):
        p = (c[0] + rnd.uniform(-1, 1) * size[0] * 0.5, c[1], c[2] + rnd.uniform(-1, 1) * size[2] * 0.5)
        blob3(f"{name}{k}", p, (size[0] * rnd.uniform(0.25, 0.5), size[1] * rnd.uniform(0.4, 1.0), size[2] * rnd.uniform(0.25, 0.5)), mat, 0.4 * size[1], seed * 13 + k)
def bricks(name, c, r, n, mat, seed=0, ground=lambda x, z: 0.0):
    from sets.front import boxes
    rnd = random.Random(seed); items = []
    for k in range(n):
        a = rnd.random() * math.tau; d = r * math.sqrt(rnd.random()); x_, z_ = c[0] + d * math.cos(a), c[2] + d * math.sin(a)
        items.append(((x_, ground(x_, z_) + 0.04 + rnd.random() * 0.05, z_), (0.24, 0.07, 0.12), rnd.uniform(0, 3), rnd.uniform(-0.4, 0.4)))
    return boxes(name, items, mat, 0.005)
def lamp_glow(name, c, energy, col=(1.0, 0.6, 0.3), r=0.1, cam=False):
    o = lib.light("POINT", T(*c), energy, col, r); o.visible_camera = cam; return o
def sky(top, horizon, strength=1.0, cam_top=None, cam_hor=None):
    from sets.kit_sbpw import set_world
    set_world(lib.hexc(top), lib.hexc(horizon), strength, lib.hexc(cam_top) if cam_top else None, lib.hexc(cam_hor) if cam_hor else None)
def sun(dir3, energy, col, angle_deg=2.0):
    """sun shining along -dir3 (dir3 = three-space direction towards the sun)"""
    s = lib.light("SUN", (0, 0, 0), energy, col, math.radians(angle_deg)); s.rotation_euler = (-T(*dir3)).to_track_quat("-Z", "Y").to_euler(); return s
def area(c, target, energy, col, size, size_y=None):
    o = lib.light("AREA", T(*c), energy, col, size, size_y=size_y); lib.look_at(o, T(*target)); return o
def spot(c, target, energy, col, angle_deg=60, blend=0.5, r=0.1):
    o = lib.light("SPOT", T(*c), energy, col, r); lib.look_at(o, T(*target)); o.data.spot_size = math.radians(angle_deg); o.data.spot_blend = blend; return o
def img_plane(name, c, w, h, mat, yaw=0.0, pitch=0.0):
    """vertical image quad facing three -z at yaw 0 (UV 0..1, image upright)"""
    ca, sa = math.cos(yaw), math.sin(yaw); R = Matrix.Rotation(pitch, 3, "X")
    def at(u, v):
        p = R @ Vector((u, v, 0)); return (c[0] + p.x * ca + p.z * sa, c[1] + p.y, c[2] - p.x * sa + p.z * ca)
    vs = [at(w / 2, -h / 2), at(-w / 2, -h / 2), at(-w / 2, h / 2), at(w / 2, h / 2)]
    me = bpy.data.meshes.new(name); me.from_pydata([T(*v) for v in vs], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for k, cc in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = cc
    me.materials.append(mat); return link(bpy.data.objects.new(name, me))

# ------------------------------------------------------------------ ruins
def ruin(name, x, z, w, floors, mat, seed, yaw=0.0, depth=8.0, glow_p=0.1, sign=None, fh=3.3, dark_p=0.6, ground=0.0):
    """gutted multi-storey town house (front.ruin_building, any yaw): facade with a window grid and a jagged top, side walls
    broken toward the back, slabs and beams hanging out, black or fire-lit interiors; the front faces local -z (yaw 0 = three
    -z, yaw +pi/2 = three -x, yaw -pi/2 = three +x)"""
    from sets.front import boxes
    rnd = random.Random(seed); H0 = floors * fh + 1.0; nwin = max(2, int(w / 2.6)); pitch = w / nwin
    jag = [H0 * rnd.uniform(0.4, 1.0) for _ in range(nwin + 1)]
    c, s = math.cos(yaw), math.sin(yaw)
    def W(lx, ly, lz): return (x + lx * c + lz * s, ground + ly, z - lx * s + lz * c)
    def top(lx):
        f = (lx + w / 2) / w * nwin; i = max(0, min(nwin - 1, int(f))); u = f - i; return jag[i] * (1 - u) + jag[i + 1] * u
    items = []
    def add(lx, ly0, ly1, lz, sw, dpt=0.55):
        tp = min(ly1, top(lx))
        if tp - ly0 > 0.15: items.append((W(lx, (ly0 + tp) / 2, lz), (sw, tp - ly0, dpt), yaw))
    add(0, 0, 1.0, 0, w, 0.7)
    for f in range(floors):
        y0 = 1.0 + f * fh
        for k in range(nwin + 1): add(-w / 2 + k * pitch, y0, y0 + fh, 0, 0.9 if k in (0, nwin) else 0.75)
        for k in range(nwin):
            cx = -w / 2 + (k + 0.5) * pitch
            if f == 0 and k == nwin // 2 and rnd.random() < 0.5: add(cx, y0 + fh - 0.75, y0 + fh, 0, pitch - 0.7); continue   # a doorway / blown hole
            add(cx, y0, y0 + 0.95, 0, pitch - 0.7); add(cx, y0 + fh - 0.75, y0 + fh, 0, pitch - 0.7)
            if rnd.random() < 0.5: add(cx, y0 + 0.95, y0 + 1.05, -0.3, pitch - 0.5, 0.25)
        add(0, y0 + fh - 0.3, y0 + fh, -0.18, w + 0.3, 0.3)
    for sd in (-1, 1):
        for k in range(4):
            d = (k + 0.5) * depth / 4; hh = H0 * rnd.uniform(0.25, 0.95) * (1 - k * 0.15)
            items.append((W(sd * w / 2, hh / 2, d), (0.55, hh, depth / 4), yaw))
    for f in range(1, floors):
        y0 = 1.0 + f * fh
        if rnd.random() < 0.7: items.append((W(rnd.uniform(-w * 0.2, w * 0.2), y0 - 0.1, depth * 0.4), (w * rnd.uniform(0.4, 0.8), 0.25, depth * 0.6), yaw, rnd.uniform(-0.25, 0.25)))
    o = boxes(name, items, mat, 0.04)
    beams = wood_mat("fbeam", "#2a1c14", "#100a08", 6, 0.9)
    for k in range(rnd.randint(2, 4)):
        lx = rnd.uniform(-w / 2, w / 2); y0 = min(top(lx), H0) - rnd.uniform(0.5, 2.5)
        bx(f"{name}bm{k}", W(lx, y0, 1.5), (0.22, 0.22, 4.0), beams, 0.01, yaw + rnd.uniform(-0.3, 0.3))
    glow = mat_once("c9glowwin", lambda: lib.emit("c9glowwin", (1.0, 0.28, 0.04), 1.2))
    dark = mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0))
    for f in range(floors):
        for k in range(nwin):
            cx = -w / 2 + (k + 0.5) * pitch; y0 = 1.0 + f * fh + 0.95
            if y0 + 1.6 > top(cx): continue
            r = rnd.random()
            if r < glow_p: bx(f"{name}g{f}{k}", W(cx, y0 + 0.9, 1.4), (pitch - 0.6, fh - 1.6, 0.05), glow, 0, yaw)
            elif r < glow_p + dark_p: bx(f"{name}d{f}{k}", W(cx, y0 + 0.9, 2.5), (pitch - 0.4, fh - 1.4, 0.05), dark, 0, yaw)
    if sign:
        txt, col, ink = sign
        bx(f"{name}sg", W(0, 1.0 + fh - 0.45, -0.42), (min(w * 0.8, 0.5 * len(txt) + 1.0), 0.7, 0.1), pmat("c9sign" + col, col, 0.6), 0.02, yaw)
        text(txt, W(0, 1.0 + fh - 0.66, -0.49), 0.42, pmat("c9signt" + ink, ink, 0.5), yaw=yaw, flat=False)
    return o
def ruin_mat_snow(name, plaster, brick="#8a4632", snow=0.55):
    from sets.front import ruin_mat
    return mat_once(name, lambda: add_snow(ruin_mat(name, plaster, brick), snow))
