# Shared kit for the chapter 5 / 6 / 8 sets (c05_*, c06_*, c08_*): detailed aircraft (Spitfire, Bf 109, He 111, B-24),
# a 1940s truck, a Liberty-type cargo ship, lattice radar masts, searchlight beams, skies, height-field terrain and
# camouflage materials. Everything is in three.js layout coordinates (y up), built with kit_sbpw.Kit (batched bmesh).
# Aircraft local frame: nose +z, up +y, wings along x. `plane()` returns an Empty that the sets move per frame.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
import lib
from lib import T, hexc, nodes, ramp, bump
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, brick, paper, text, sign, poster, barrel, crate, glassm, cached, _rot, R90
from .void import lathe, tube, worn, fire, flame_mat, smoke_mat, smoke_column, mat_once, link, mesh_obj, map_mat, map_plane

# ---------------------------------------------------------------------------------------------------- materials
def camo(name, c1, c2, under, scale=0.35, metal=0.15, rough=0.55, c3=None):
    """two/three-tone disruptive camouflage on top and sides (object coords, so it travels with the plane), a plain
    underside colour where the surface faces down, faint panel grime"""
    def mk():
        m = lib.principled(name, hexc(c1), rough, metal); t, n, l = nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord")
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 1.5; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        r = n.new("ShaderNodeValToRGB"); r.color_ramp.interpolation = "CONSTANT"; e = r.color_ramp.elements
        e[0].position, e[0].color = 0.0, (*hexc(c1), 1); e[1].position, e[1].color = 0.5, (*hexc(c2), 1)
        if c3: x = e.new(0.62); x.color = (*hexc(c3), 1)
        l.new(nz.outputs["Fac"], r.inputs["Fac"])
        gm = n.new("ShaderNodeNewGeometry"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(gm.outputs["Normal"], sp.inputs[0])
        mr = n.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.25; mr.inputs["From Max"].default_value = -0.45; l.new(sp.outputs["Z"], mr.inputs["Value"])
        mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(mr.outputs["Result"], mx.inputs[0]); l.new(r.outputs["Color"], mx.inputs[6]); mx.inputs[7].default_value = (*hexc(under), 1)
        gr = n.new("ShaderNodeTexNoise"); gr.inputs["Scale"].default_value = 6; gr.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], gr.inputs["Vector"])
        dm = n.new("ShaderNodeMix"); dm.data_type = "RGBA"; dm.blend_type = "MULTIPLY"; dm.inputs[0].default_value = 0.25; l.new(mx.outputs[2], dm.inputs[6]); l.new(gr.outputs["Color"], dm.inputs[7])
        l.new(dm.outputs[2], b.inputs["Base Color"]); bump(n, l, gr.outputs["Fac"], 0.08, 0.01)
        return m
    return cached("camo" + name, mk)
def alu(name="alu", col="#b8bcc2", rough=0.32):
    """bare aluminium with panel tint variation and faint streaks"""
    def mk():
        m = lib.principled(name, hexc(col), rough, 1.0); t, n, l = nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); br = n.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 0.6
        br.inputs["Color1"].default_value = (*hexc(col), 1); br.inputs["Color2"].default_value = (*tuple(c * 0.86 for c in hexc(col)), 1); br.inputs["Mortar"].default_value = (*tuple(c * 0.5 for c in hexc(col)), 1)
        br.inputs["Mortar Size"].default_value = 0.006; br.inputs["Brick Width"].default_value = 1.4; br.inputs["Row Height"].default_value = 0.5
        l.new(tc.outputs["Object"], br.inputs["Vector"]); l.new(br.outputs["Color"], b.inputs["Base Color"]); bump(n, l, br.outputs["Fac"], 0.15, 0.004)
        return m
    return cached("alu" + name + col, mk)
def soft_mat(name, col, alpha=0.3, emit_s=0.0):
    """translucent sheet (propeller disc, beam): alpha mix, optional glow"""
    def mk():
        m = bpy.data.materials.new(name); t, n, l = nodes(m); b = n["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*hexc(col), 1); b.inputs["Alpha"].default_value = alpha; b.inputs["Roughness"].default_value = 0.6
        if emit_s: b.inputs["Emission Color"].default_value = (*hexc(col), 1); b.inputs["Emission Strength"].default_value = emit_s
        return m
    return cached("soft" + name, mk)
def beam_mat(name, col=(0.75, 0.82, 1.0), strength=2.0, alpha=0.35):
    """searchlight / headlight cone: emission that fades along the cone (generated z) and towards the silhouette edges"""
    def mk():
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
        for x in list(n): n.remove(x)
        out = n.new("ShaderNodeOutputMaterial"); em_ = n.new("ShaderNodeEmission"); tr = n.new("ShaderNodeBsdfTransparent"); mx = n.new("ShaderNodeMixShader")
        em_.inputs["Color"].default_value = (*col, 1); em_.inputs["Strength"].default_value = strength
        tc = n.new("ShaderNodeTexCoord"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Generated"], sp.inputs[0])
        iz = n.new("ShaderNodeMath"); iz.operation = "SUBTRACT"; iz.inputs[0].default_value = 1.0; l.new(sp.outputs["Z"], iz.inputs[1])
        fz = n.new("ShaderNodeMath"); fz.operation = "POWER"; fz.inputs[1].default_value = 1.3; l.new(iz.outputs[0], fz.inputs[0])
        lw = n.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
        inv = n.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; l.new(lw.outputs["Facing"], inv.inputs[1])
        a = n.new("ShaderNodeMath"); a.operation = "MULTIPLY"; l.new(fz.outputs[0], a.inputs[0]); l.new(inv.outputs[0], a.inputs[1])
        a2 = n.new("ShaderNodeMath"); a2.operation = "MULTIPLY"; a2.inputs[1].default_value = alpha; l.new(a.outputs[0], a2.inputs[0])
        l.new(a2.outputs[0], mx.inputs[0]); l.new(tr.outputs[0], mx.inputs[1]); l.new(em_.outputs[0], mx.inputs[2]); l.new(mx.outputs[0], out.inputs["Surface"])
        return m
    return cached("beam" + name, mk)
def snow_mat(name="snow", col="#eef2f8", shadow="#b8c8e0"):
    def mk():
        m = lib.principled(name, hexc(col), 0.55); t, n, l = nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.2; nz.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        r = ramp(n, l, nz.outputs["Fac"], [(0.35, hexc(shadow)), (0.65, hexc(col))])
        l.new(r.outputs["Color"], b.inputs["Base Color"])
        fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 30; fn.inputs["Detail"].default_value = 4; l.new(tc.outputs["Object"], fn.inputs["Vector"])
        bump(n, l, fn.outputs["Fac"], 0.25, 0.02)
        try:
            b.inputs["Subsurface Weight"].default_value = 0.15; b.inputs["Subsurface Radius"].default_value = (0.4, 0.5, 0.8)
        except Exception: pass
        return m
    return cached("snow" + name, mk)
def ground_mat(name, stops, scale=0.08, fine=2.0, rough=0.9, bumpk=0.6):
    """natural ground: large-scale colour ramp (stops = [(pos, hex)]) x fine noise, bump"""
    def mk():
        m = lib.principled(name, hexc(stops[0][1]), rough); t, n, l = nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); big = n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = scale; big.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], big.inputs["Vector"])
        r = ramp(n, l, big.outputs["Fac"], [(p, hexc(c)) for p, c in stops])
        fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = fine; fn.inputs["Detail"].default_value = 10; l.new(tc.outputs["Object"], fn.inputs["Vector"])
        mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 0.4; l.new(r.outputs["Color"], mx.inputs[6]); l.new(fn.outputs["Color"], mx.inputs[7])
        l.new(mx.outputs[2], b.inputs["Base Color"]); bump(n, l, fn.outputs["Fac"], bumpk, 0.05)
        return m
    return cached("gnd" + name, mk)
def fields_mat(name="fields"):
    """patchwork farmland seen from the air: voronoi fields in greens and golds with dark hedge lines"""
    def mk():
        m = lib.principled(name, hexc("#5a7a3a"), 0.9); t, n, l = nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); vo = n.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 0.012; l.new(tc.outputs["Object"], vo.inputs["Vector"])
        ve = n.new("ShaderNodeTexVoronoi"); ve.inputs["Scale"].default_value = 0.012
        try: ve.feature = "DISTANCE_TO_EDGE"
        except Exception: pass
        l.new(tc.outputs["Object"], ve.inputs["Vector"])
        r = n.new("ShaderNodeValToRGB"); r.color_ramp.interpolation = "CONSTANT"; e = r.color_ramp.elements
        cols = ["#4e6e30", "#7a9a42", "#a8a052", "#5a7a36", "#c8b060", "#6a8a3a", "#8a7a40", "#46642c"]
        e[0].position, e[0].color = 0.0, (*hexc(cols[0]), 1); e[1].position, e[1].color = 0.88, (*hexc(cols[7]), 1)
        for k, c in enumerate(cols[1:7]): x = e.new((k + 1) / 8); x.color = (*hexc(c), 1)
        sp = n.new("ShaderNodeSeparateRGB") if hasattr(bpy.types, "ShaderNodeSeparateRGB") else n.new("ShaderNodeSeparateColor")
        l.new(vo.outputs["Color"], sp.inputs[0]); l.new(sp.outputs[0], r.inputs["Fac"])
        hd = ramp(n, l, ve.outputs["Distance"], [(0.0, hexc("#1e2a14")), (0.025, hexc("#2a3a1a")), (0.05, (1, 1, 1))])
        mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1.0; l.new(r.outputs["Color"], mx.inputs[6]); l.new(hd.outputs["Color"], mx.inputs[7])
        fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 0.2; fn.inputs["Detail"].default_value = 8; l.new(tc.outputs["Object"], fn.inputs["Vector"])
        m2 = n.new("ShaderNodeMix"); m2.data_type = "RGBA"; m2.blend_type = "MULTIPLY"; m2.inputs[0].default_value = 0.35; l.new(mx.outputs[2], m2.inputs[6]); l.new(fn.outputs["Color"], m2.inputs[7])
        l.new(m2.outputs[2], b.inputs["Base Color"])
        return m
    return cached(name, mk)
def sea_mat(name="sea", deep="#1a3a5a", shallow="#2e6a7a", rough=0.12, scale=0.6, bumpk=0.35):
    def mk():
        m = lib.principled(name, hexc(deep), rough); t, n, l = nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.02; nz.inputs["Detail"].default_value = 4; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        r = ramp(n, l, nz.outputs["Fac"], [(0.35, hexc(deep)), (0.65, hexc(shallow))]); l.new(r.outputs["Color"], b.inputs["Base Color"])
        wv = n.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = scale; wv.inputs["Distortion"].default_value = 8; wv.inputs["Detail"].default_value = 4; l.new(tc.outputs["Object"], wv.inputs["Vector"])
        fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 3; fn.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], fn.inputs["Vector"])
        ad = n.new("ShaderNodeMath"); ad.operation = "MULTIPLY_ADD"; ad.inputs[1].default_value = 0.4; l.new(wv.outputs["Fac"], ad.inputs[0]); l.new(fn.outputs["Fac"], ad.inputs[2])
        bump(n, l, ad.outputs[0], bumpk if scale > 0.05 else 0.12, 0.08)
        return m
    return cached(name, mk)
def cloud_mat(name="cloud", col="#ffffff", shade_="#9aa8c0", dens=0.92):
    """cumulus puff: bright tops, blue-grey bellies (normal z), soft transparent silhouette"""
    def mk():
        m = bpy.data.materials.new(name); t, n, l = nodes(m); b = n["Principled BSDF"]
        b.inputs["Roughness"].default_value = 1.0
        try: b.inputs["Specular IOR Level"].default_value = 0.0
        except Exception: pass
        gm = n.new("ShaderNodeNewGeometry"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(gm.outputs["Normal"], sp.inputs[0])
        r = ramp(n, l, sp.outputs["Z"], [(0.0, hexc(shade_)), (0.6, hexc(col))])
        l.new(r.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Emission Color"].default_value = (*hexc(col), 1); b.inputs["Emission Strength"].default_value = 0.08
        lw = n.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
        inv = n.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; l.new(lw.outputs["Facing"], inv.inputs[1])
        pw = n.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 0.6; l.new(inv.outputs[0], pw.inputs[0])
        mu = n.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = dens; l.new(pw.outputs[0], mu.inputs[0])
        l.new(mu.outputs[0], b.inputs["Alpha"])
        return m
    return cached(name, mk)

# ---------------------------------------------------------------------------------------------------- bmesh shapes
def loft_k(K, rings, m, bev=0.0, cap0=True, cap1=True):
    """skin closed rings (lists of three points, equal counts) into the kit mesh, smooth shaded"""
    bm, _ = K._get(bev); R = len(rings[0])
    vv = [[bm.verts.new(T(*p)) for p in r] for r in rings]; allv = [v for r in vv for v in r]
    for i in range(len(vv) - 1):
        for k in range(R):
            k2 = (k + 1) % R
            try: bm.faces.new((vv[i][k], vv[i][k2], vv[i + 1][k2], vv[i + 1][k]))
            except ValueError: pass
    for cap, r in ((cap0, vv[0]), (cap1, vv[-1])):
        if cap:
            try: bm.faces.new(r if cap is cap1 and r is vv[-1] else r[::-1])
            except ValueError: pass
    K._finish(allv, m, bev, True)
def ring(cx, cy, z, hw, top, bot, n=20, e=2.4, axis="z"):
    """superelliptic section around (cx, cy) at z (fuselage / nacelle); axis 'z' only"""
    pts = []
    for i in range(n):
        a = i / n * math.tau; c, s = math.cos(a), math.sin(a)
        x = hw * math.copysign(abs(c) ** (2 / e), c); y = (top if s > 0 else bot) * math.copysign(abs(s) ** (2 / e), s)
        pts.append((cx + x, cy + y, z))
    return pts
def body(K, m, stations, n=20, e=2.4, cx=0.0, bev=0.0):
    """stations: (z, hw, top, bot, cy)"""
    loft_k(K, [ring(cx, s[4], s[0], max(s[1], 0.004), max(s[2], 0.004), max(s[3], 0.004), n, e) for s in stations], m, bev)
def _foil(n=9):
    up = []
    for i in range(n + 1):
        u = (1 - math.cos(math.pi * i / n)) / 2
        t = 5 * (0.2969 * math.sqrt(u) - 0.126 * u - 0.3516 * u * u + 0.2843 * u ** 3 - 0.1036 * u ** 4)
        up.append((u, max(t, 0.002)))
    return up
FOIL = _foil()
def surface(K, m, stations, thick=0.12, span="x", n=None):
    """lifting surface: stations (s, le, chord, off) along the span axis; le/te along three z (le is the larger z);
    span 'x' -> thickness along y (wings, tailplanes), span 'y' -> thickness along x (fins), off = the other coord"""
    rings = []
    for st in stations:
        s, le, ch, off = st[0], st[1], max(st[2], 0.02), st[3]; th = st[4] if len(st) > 4 else thick
        pts = [(u, t) for u, t in FOIL] + [(u, -t) for u, t in FOIL[-2:0:-1]]
        r = []
        for u, t in pts:
            z = le - u * ch; d = t * th * ch * 0.5
            r.append((s, off + d, z) if span == "x" else (off + d, s, z))
        rings.append(r)
    loft_k(K, rings, m)

def place(objs, parent):
    for o in objs: o.parent = parent
def empty(name, size=1.0):
    e = bpy.data.objects.new(name, None); e.empty_display_size = size; bpy.context.scene.collection.objects.link(e); return e
def pose(e, pos, yaw=0.0, pitch=0.0, roll=0.0):
    """three-space pose: yaw about +y (0 = nose +z), pitch nose-up positive, roll right-wing-down positive"""
    e.matrix_world = Matrix.Translation(T(*pos)) @ _rot(yaw, -pitch, roll)

# ---------------------------------------------------------------------------------------------------- aircraft
def roundel(K, c, rings_, axis="y", yaw=0.0, pitch=0.0, roll=0.0, sgn=1):
    """concentric discs: rings_ = [(r, hex)], outer first; stacked 1.5 mm apart along the axis"""
    for k, (r, col) in enumerate(rings_):
        off = 0.0015 * k * sgn
        cc = (c[0] + (off if axis == "x" else 0), c[1] + (off if axis == "y" else 0), c[2])
        K.cyl(cc, r, 0.004, pm(col, 0.6), 28, axis, None, yaw, 0.0, pitch, roll)
def prop(K, c, r, blades, hub_col, spin=True, blade_col="#1a1a1a", tip="#e8c030", axis_z=True):
    """spinner + blades (static) or a blurred disc (spin)"""
    K.cyl((c[0], c[1], c[2] + 0.18), 0.001, 0.5, pm(hub_col, 0.35, 0.2), 20, "z", r * 0.17)
    if spin:
        K.cyl((c[0], c[1], c[2] - 0.02), r, 0.01, soft_mat("pdisc", "#202022", 0.12), 32, "z")
        K.cyl((c[0], c[1], c[2] - 0.025), r, 0.006, soft_mat("ptip", tip, 0.14), 32, "z", r * 0.92)
    else:
        for k in range(blades):
            a = k / blades * math.tau + 0.3
            K.box((c[0] + math.cos(a) * r * 0.5, c[1] + math.sin(a) * r * 0.5, c[2]), (r, 0.16, 0.03), pm(blade_col, 0.5), 0, 0.01, 0, a)
            K.box((c[0] + math.cos(a) * r * 0.94, c[1] + math.sin(a) * r * 0.94, c[2] - 0.002), (r * 0.12, 0.165, 0.032), pm(tip, 0.5), 0, 0.0, 0, a)
def gear(K, x, z, ytop, ybot, r, m, tyre):
    K.cyl((x, (ytop + ybot) / 2, z), 0.045, ytop - ybot, m, 10)
    K.cyl((x, ybot, z), r, 0.16, pm(tyre, 0.85), 20, "x")
    K.cyl((x, ybot, z), r * 0.45, 0.18, m, 14, "x")

def spitfire(name, code="QV", letter="K", spin=True, gear_down=False, col=("#3e5228", "#7a6038", "#a8b8a8")):
    """Supermarine Spitfire Mk I (11.2 m span): elliptical wing, Merlin nose with exhaust stubs, bubble canopy,
    radiator under the starboard wing, RAF roundels and squadron codes"""
    K = Kit(name); sk = camo(name + "c", col[0], col[1], col[2], 0.28); dk = pm("#1e1e20", 0.5, 0.3)
    st = [(3.75, 0.40, 0.42, 0.44, 0.02), (3.2, 0.46, 0.5, 0.5, 0.04), (2.4, 0.5, 0.56, 0.54, 0.05), (1.5, 0.52, 0.6, 0.56, 0.05), (0.6, 0.52, 0.6, 0.6, 0.02),
          (-0.4, 0.47, 0.52, 0.6, 0.0), (-1.4, 0.39, 0.44, 0.56, 0.0), (-2.6, 0.29, 0.36, 0.44, 0.04), (-3.7, 0.18, 0.3, 0.3, 0.1), (-4.6, 0.08, 0.26, 0.14, 0.18), (-4.95, 0.02, 0.2, 0.04, 0.22)]
    body(K, sk, st, 22)
    K.cyl((0, 0.04, 4.02), 0.42, 0.55, pm("#1a1a1c", 0.4, 0.3), 24, "z", 0.04)          # spinner (black)
    prop(K, (0, 0.04, 3.86), 1.6, 3, "#1a1a1c", spin)
    # elliptical wing with dihedral, root at the fuselage bottom
    ws = []
    for i in range(10):
        s = 0.3 + (5.55 - 0.3) * (1 - math.cos(i / 9 * math.pi / 2)); ch = 2.55 * math.sqrt(max(0.0, 1 - (s / 5.62) ** 2)); qc = 1.15
        ws.append((s, qc + 0.3 * ch, ch, -0.36 + s * 0.1, 0.13 - 0.05 * s / 5.6))
    for sd in (-1, 1): surface(K, sk, [(sd * a, b, c, d, e) for a, b, c, d, e in ws])
    for sd in (-1, 1):
        surface(K, sk, [(sd * s, -3.95 - 0.1 * (s / 1.65) ** 2 + 0.45 * math.sqrt(max(0, 1 - (s / 1.7) ** 2)), 1.05 * math.sqrt(max(0.04, 1 - (s / 1.7) ** 2)), 0.08) for s in (0.15, 0.6, 1.0, 1.35, 1.6)], 0.1)
    surface(K, sk, [(y, -4.25 - 0.18 * (y - 0.2), 1.25 * math.sqrt(max(0.05, 1 - ((y - 0.2) / 1.45) ** 2)), 0.0) for y in (0.2, 0.6, 1.0, 1.35, 1.6)], 0.1, "y")
    # canopy: blown hood with a frame, windscreen, the pilot's head behind it
    K.sphere((0, 0.62, 0.55), 0.36, glassm(), 16, (0.85, 0.75, 2.3))
    K.box((0, 0.66, 1.25), (0.5, 0.36, 0.05), glassm(), 0, 0.0, 0.5)
    for zz in (0.05, 0.55, 1.05): K.torus((0, 0.62, zz), 0.32, 0.012, dk, 16, 4, "z", scale=(0.92, 1.0, 1.0), arc=math.pi)
    K.sphere((0, 0.78, 0.4), 0.16, pm("#5a3a22", 0.7), 12)
    K.box((0, 0.58, -0.2), (0.24, 0.2, 0.06), pm("#2a2a2a", 0.6), 0, 0.01)
    # radiator, oil cooler, exhausts, aerial mast, pitot, wing guns
    K.box((1.55, -0.62, 0.9), (0.42, 0.26, 1.15), sk, 0, 0.06)
    K.box((-1.5, -0.58, 1.1), (0.2, 0.18, 0.55), sk, 0, 0.05)
    for sd in (-1, 1):
        for k in range(6): K.box((sd * 0.5, 0.22, 2.0 + k * 0.24), (0.1, 0.1, 0.16), pm("#3a2a22", 0.6, 0.6), 0, 0.02)
        for gx in (2.4, 2.75, 3.3, 3.6): K.cyl((sd * gx, -0.3 + gx * 0.1, 1.95), 0.025, 0.25, dk, 8, "z")
        K.box((sd * 2.3, -0.12, 1.7), (0.5, 0.01, 0.02), pm("#c82020", 0.6), 0, 0.0)
    K.box((0, 0.95, -0.9), (0.04, 0.6, 0.14), dk, 0, 0.01, 0.4)
    K.cyl((-3.5, -0.25, 1.6), 0.02, 0.5, dk, 6, "z")
    # roundels: type B on the upper wings, type A1 on the fuselage, fin flash; squadron codes
    for sd in (-1, 1):
        roundel(K, (sd * 3.7, -0.36 + 3.7 * 0.1 + 0.075, 0.95), [(0.6, "#22305a"), (0.24, "#a8202a")], "y", 0, 0, -sd * 0.1)
        roundel(K, (sd * 0.352, 0.0, -1.95), [(0.33, "#e8c030"), (0.27, "#22305a"), (0.18, "#f0ece0"), (0.09, "#a8202a")], "x", sgn=sd)
    for k, colf in enumerate(("#a8202a", "#f0ece0", "#22305a")):
        K.box((0, 0.55 + k * 0.0, -4.26 - k * 0.18), (0.13, 0.55, 0.17), pm(colf, 0.6), 0, 0.0)
    if gear_down:
        for sd in (-1, 1): gear(K, sd * 0.85, 1.15, -0.4, -1.95, 0.34, pm("#9a9aa0", 0.4, 0.8), "#141414")
        K.cyl((0, -0.32, -4.5), 0.03, 0.6, pm("#9a9aa0", 0.4, 0.8), 8); K.cyl((0, -0.62, -4.55), 0.12, 0.08, pm("#141414", 0.85), 12, "x")
    obs = K.build(); e = empty(name)
    for sd in (-1, 1):
        t1 = text(code if sd > 0 else letter, (sd * 0.5, 0.05, -1.1 if sd > 0 else -2.8), 0.42, pm("#9a8a6a", 0.7), -sd * R90, "sans", 0.003); obs.append(t1)
        t2 = text(letter if sd > 0 else code, (sd * 0.47, 0.05, -2.85 if sd > 0 else -1.0), 0.42, pm("#9a8a6a", 0.7), -sd * R90, "sans", 0.003); obs.append(t2)
    place(obs, e); return e

def bf109(name, spin=True, col=("#4a5444", "#6a7462", "#a8b8c8")):
    """Messerschmitt Bf 109 E (9.9 m span): slim angular fuselage, yellow cowling and rudder, squared wingtips,
    framed canopy, strut-braced tailplane; plain (no national insignia)"""
    K = Kit(name); sk = camo(name + "c", col[0], col[1], col[2], 0.45, c3="#7a8270"); yel = pm("#d8a82a", 0.5); dk = pm("#1a1a1c", 0.5, 0.3)
    nose = [(3.95, 0.3, 0.36, 0.42, 0.05), (3.3, 0.42, 0.46, 0.5, 0.06), (2.6, 0.46, 0.5, 0.54, 0.06)]
    st = [(2.6, 0.46, 0.5, 0.54, 0.06), (1.6, 0.47, 0.55, 0.56, 0.06), (0.6, 0.45, 0.56, 0.58, 0.04), (-0.5, 0.4, 0.5, 0.56, 0.02), (-1.6, 0.32, 0.42, 0.48, 0.02),
          (-2.8, 0.22, 0.34, 0.36, 0.06), (-3.9, 0.12, 0.28, 0.22, 0.12), (-4.7, 0.04, 0.24, 0.08, 0.18)]
    body(K, yel, nose, 20, 2.8); body(K, sk, st, 20, 2.8)
    K.cyl((0, 0.06, 4.2), 0.34, 0.5, yel, 22, "z", 0.04); prop(K, (0, 0.06, 4.05), 1.5, 3, "#d8a82a", spin, tip="#d8a82a")
    ws = [(s, 1.35 + 0.35 * (1 - s / 4.9), 2.05 - 0.95 * s / 4.9, -0.42 + s * 0.11, 0.13) for s in (0.3, 1.5, 3.0, 4.4, 4.85)]
    for sd in (-1, 1): surface(K, sk, [(sd * a, b, c, d, e) for a, b, c, d, e in ws])
    for sd in (-1, 1):
        surface(K, sk, [(sd * s, -3.75 - 0.05 * s, 0.95 - 0.3 * s / 1.6, 0.3) for s in (0.15, 0.8, 1.55)], 0.1)
        K.cyl((sd * 0.7, 0.0, -3.9), 0.025, 0.7, dk, 6, "y", None, 0, 0, sd * 0.5)
    surface(K, yel, [(y, -4.0 - 0.15 * y, 1.2 - 0.45 * y / 1.4, 0.0) for y in (0.25, 0.8, 1.35)], 0.1, "y")
    K.box((0, 0.66, 0.4), (0.62, 0.36, 1.3), glassm(), 0, 0.06)
    for zz in (-0.2, 0.25, 0.75, 1.05): K.box((0, 0.84, zz), (0.64, 0.04, 0.04), dk, 0, 0.005)
    for sd in (-1, 1): K.box((sd * 0.31, 0.68, 0.4), (0.03, 0.36, 1.3), dk, 0, 0.005)
    K.sphere((0, 0.78, 0.25), 0.15, pm("#3a3026", 0.7), 12)
    for sd in (-1, 1):
        for k in range(6): K.box((sd * 0.42, 0.1, 2.7 + k * 0.17), (0.08, 0.07, 0.12), pm("#3a2a22", 0.6, 0.6), 0, 0.01)
        K.box((sd * 1.2, -0.55, 1.0), (0.42, 0.18, 0.9), sk, 0, 0.04)
    K.box((0, -0.55, 2.5), (0.36, 0.18, 0.5), sk, 0, 0.04)
    if not spin:
        for sd in (-1, 1): gear(K, sd * 0.9, 1.2, -0.4, -1.8, 0.3, pm("#6a6e66", 0.5, 0.6), "#141414")
    obs = K.build(); e = empty(name); place(obs, e); return e

def nacelle(K, m, x, y, z0, z1, r, prop_c=None, spin=True, blades=3, hub="#1a1a1c"):
    st = [(z0, r * 0.6, r * 0.6, r * 0.6, y), (z0 - 0.4, r, r, r, y), (z0 - 1.3, r * 1.02, r, r * 1.05, y), (z1 + 0.6, r * 0.8, r * 0.7, r * 0.8, y), (z1, r * 0.3, r * 0.3, r * 0.4, y)]
    loft_k(K, [ring(x, s[4], s[0], s[1], s[2], s[3], 16, 2.2) for s in st], m)
    K.cyl((x, y, z0 + 0.25), 0.001, 0.5, pm(hub, 0.4, 0.2), 16, "z", r * 0.45)
    prop(K, (x, y, z0 + 0.1), r * 2.6, blades, hub, spin)

def he111(name, spin=True):
    """Heinkel He 111 H (22.6 m span): fully glazed nose, two engine nacelles, long elliptical-edged wing, single fin;
    dark green splinter camouflage, pale blue underside; no insignia"""
    K = Kit(name); sk = camo(name + "c", "#3e4a36", "#2e3a2c", "#8a9aaa", 0.14); dk = pm("#18181a", 0.5, 0.3)
    st = [(6.6, 0.85, 0.8, 0.8, 0.1), (5.2, 0.95, 0.9, 0.95, 0.1), (3.0, 0.98, 0.95, 1.0, 0.1), (0.5, 0.95, 0.92, 0.98, 0.1), (-2.5, 0.72, 0.75, 0.8, 0.2),
          (-5.5, 0.42, 0.55, 0.55, 0.35), (-7.8, 0.18, 0.42, 0.3, 0.55), (-8.9, 0.04, 0.3, 0.08, 0.65)]
    body(K, sk, st, 22)
    K.sphere((0, 0.2, 7.0), 0.92, glassm(), 18, (0.95, 0.92, 1.0))
    for k in range(5): K.torus((0, 0.2, 6.3 + k * 0.32), 0.86 - k * 0.08, 0.012, dk, 18, 4, "z")
    K.box((0, 1.1, 1.0), (0.5, 0.4, 0.9), glassm(), 0, 0.08)                         # dorsal gun position
    K.box((0, -1.05, -0.5), (0.7, 0.4, 2.0), sk, 0, 0.12)                           # ventral gondola
    ws = []
    for i in range(10):
        s = 0.8 + (11.2 - 0.8) * i / 9; ch = 5.0 * (1 - 0.62 * (s / 11.3) ** 1.3)
        ws.append((s, 1.6 - 0.25 * s / 11.3, ch, -0.3 + s * 0.06, 0.15 - 0.06 * s / 11.3))
    for sd in (-1, 1): surface(K, sk, [(sd * a, b, c, d, e) for a, b, c, d, e in ws])
    for sd in (-1, 1): nacelle(K, sk, sd * 3.7, -0.05, 3.7, -1.6, 0.62, spin=spin)
    for sd in (-1, 1): surface(K, sk, [(sd * s, -6.9 - 0.1 * s, 2.0 * math.sqrt(max(0.1, 1 - (s / 4.0) ** 2)), 0.35) for s in (0.2, 1.4, 2.6, 3.6, 3.95)], 0.1)
    surface(K, sk, [(y, -7.0 - 0.35 * y, 2.3 * math.sqrt(max(0.08, 1 - (y / 2.6) ** 2)), 0.0) for y in (0.4, 1.2, 1.9, 2.4, 2.65)], 0.1, "y")
    obs = K.build(); e = empty(name); place(obs, e); return e

def b24(name, finish="od", spin=False, gear_down=True, star=True, partial=0):
    """Consolidated B-24 Liberator (33.5 m span): deep slab-sided fuselage, high narrow Davis wing, four engines,
    twin oval fins; finish 'od' (olive drab / grey) or 'alu' (bare metal). partial > 0 drops parts (assembly stages:
    1 = no wings outboard / no props, 2 = fuselage only)"""
    K = Kit(name)
    if finish == "od": sk = camo(name + "c", "#5a5a3a", "#545436", "#8a8a88", 0.08, 0.1, 0.65)
    else: sk = alu(name + "a")
    dk = pm("#1a1a1c", 0.5, 0.3); zc = pm("#9aa84a", 0.6)
    st = [(9.9, 0.7, 0.9, 0.9, 0.5), (9.2, 1.05, 1.3, 1.3, 0.4), (7.0, 1.12, 1.5, 1.55, 0.3), (2.0, 1.15, 1.55, 1.6, 0.3), (-3.0, 1.0, 1.4, 1.35, 0.35),
          (-7.5, 0.65, 1.0, 0.9, 0.55), (-10.0, 0.4, 0.75, 0.55, 0.8), (-10.7, 0.12, 0.5, 0.2, 0.9)]
    body(K, sk, st, 24, 3.2)
    K.sphere((0, 0.6, 10.0), 0.72, glassm(), 16, (1.0, 0.9, 0.8))                       # nose glazing + turret
    K.sphere((0, 2.0, 5.4), 0.55, glassm(), 14, (1.0, 0.6, 1.0))                       # top turret
    K.box((0, 1.7, 7.6), (1.2, 0.5, 1.0), glassm(), 0, 0.12, 0.3)                       # cockpit glazing
    for sd in (-1, 1):
        for k in range(4): K.box((sd * 1.13, 1.0, 6.9 + k * 0.35), (0.02, 0.3, 0.28), glassm(), 0, 0.0)
    if partial < 2:
        span = 16.7 if partial == 0 else 6.0
        ws = [(s, 3.8 - 0.25 * s / 16.7, 4.2 - 2.8 * s / 16.7, 1.65 + s * 0.02, 0.16 - 0.06 * s / 16.7) for s in (0.9, span * 0.35, span * 0.7, span)]
        for sd in (-1, 1): surface(K, sk, [(sd * a, b, c, d, e) for a, b, c, d, e in ws])
        for sd in (-1, 1):
            for nx in ((3.8, 7.6) if partial == 0 else (3.8,)):
                nacelle(K, sk, sd * nx, 1.45, 5.6, 0.5, 0.75, spin=spin, blades=3) if partial == 0 else nacelle(K, zc, sd * nx, 1.45, 5.6, 0.5, 0.75, spin=False, blades=0)
                K.box((sd * nx, 1.0, 4.2), (0.35, 0.5, 0.8), sk, 0, 0.06)
        # tailplane + twin oval fins
        for sd in (-1, 1): surface(K, sk, [(sd * s, -8.6, 2.6 - 0.8 * s / 4.3, 1.1) for s in (0.3, 2.2, 4.3)], 0.11)
        for sd in (-1, 1):
            surface(K, sk, [(y, -8.6 + 0.9 * math.sqrt(max(0, 1 - ((y - 1.2) / 2.2) ** 2)), 2.6 * math.sqrt(max(0.06, 1 - ((y - 1.2) / 2.25) ** 2)), sd * 4.3)
                            for y in (-1.0, -0.2, 0.6, 1.2, 1.9, 2.7, 3.4)], 0.1, "y")
    if gear_down:
        for sd in (-1, 1): gear(K, sd * 3.8, 3.4, 1.2, -1.95, 0.62, pm("#8a8a90", 0.4, 0.8), "#141414")
        gear(K, 0, 8.6, -0.9, -1.95, 0.45, pm("#8a8a90", 0.4, 0.8), "#141414")
    if star and finish:
        for sd in (-1, 1):
            c = (sd * 1.16, 0.4, -3.6)
            K.cyl(c, 0.8, 0.01, pm("#22305a", 0.6), 28, "x")
            for k in range(5):
                a = k / 5 * math.tau
                K.box((c[0] + sd * 0.007, c[1] + math.cos(a) * 0.3, c[2] + math.sin(a) * 0.3), (0.012, 0.62, 0.2), pm("#f0ece0", 0.6), 0, 0.0, -a, 0)
            K.box((c[0] + sd * 0.006, c[1], c[2]), (0.012, 0.42, 2.3), pm("#f0ece0", 0.6), 0, 0.0)
    obs = K.build(); e = empty(name); place(obs, e); return e

# ---------------------------------------------------------------------------------------------------- vehicles
def truck(name, c, yaw, body_col="#4a5a3a", canvas="#6a6a4a", lights=False, load=None, Kx=None):
    """1940s 1.5 t army truck (GAZ-AA / Bedford style): bonnet with grille, round fenders, cab, cargo bed with a canvas
    tilt (or an open bed with `load`), spare wheel, headlamps; nose along +x local, c at the ground centre"""
    K = Kx or Kit(name); cw, sw = math.cos(yaw), math.sin(yaw)
    P = lambda lx, ly, lz: (c[0] + lx * cw + lz * sw, c[1] + ly, c[2] - lx * sw + lz * cw)
    m = mat_once("trk" + body_col, lambda: worn("trk" + body_col, body_col, "#3a3430", 0.6, 0.2, 9, 0.66, "#3a3020")); dk = pm("#1a1a1a", 0.7)
    wd = wood("#7a6040", "#4a3a24", 6, 0.8); tyre = pm("#161616", 0.85)
    B = lambda lc, s, mm, bev=0.03: K.box(P(*lc), s, mm, yaw, bev)
    B((-0.3, 0.72, 0), (5.2, 0.16, 0.9), dk, 0.02)                                     # chassis
    B((1.75, 1.2, 0), (1.15, 0.7, 0.95), m, 0.08)                                       # bonnet
    B((2.36, 1.15, 0), (0.08, 0.75, 0.85), dk, 0.02)                                    # grille
    for k in range(7): B((2.41, 1.15, -0.36 + k * 0.12), (0.02, 0.68, 0.03), pm("#5a5a58", 0.4, 0.7), 0.0)
    for sd in (-1, 1):
        K.cyl(P(1.75, 0.95, sd * 0.78), 0.5, 0.36, m, 20, "z", None, yaw)               # front fenders (round)
        K.cyl(P(2.3, 1.42, sd * 0.42), 0.12, 0.12, m, 14, "x", None, yaw)              # headlamps
        K.cyl(P(2.37, 1.42, sd * 0.42), 0.1, 0.02, em("#fff0c8", 6.0) if lights else pm("#e8e8d8", 0.1, 0.5), 14, "x", None, yaw)
        for wx in (1.75, -1.15, -2.0): K.cyl(P(wx, 0.45, sd * 0.8), 0.45, 0.28, tyre, 22, "z", None, yaw)
        for wx in (1.75, -1.15, -2.0): K.cyl(P(wx, 0.45, sd * 0.95), 0.2, 0.02, m, 14, "z", None, yaw)
        B((0.75, 0.82, sd * 0.85), (0.9, 0.05, 0.3), m, 0.01)                           # running boards
    B((0.75, 1.55, 0), (1.1, 1.45, 1.9), m, 0.06)                                       # cab
    B((1.28, 1.95, 0), (0.04, 0.5, 1.6), glassm() if not lights else pm("#1a2a3a", 0.05), 0.0)
    for sd in (-1, 1): B((0.75, 1.95, sd * 0.955), (0.6, 0.45, 0.02), pm("#1a2230", 0.05), 0.0)
    B((0.75, 2.3, 0), (1.2, 0.08, 1.98), m, 0.03)
    B((-1.45, 1.05, 0), (3.0, 0.12, 2.1), wd, 0.01)                                     # bed floor
    for sd in (-1, 1): B((-1.45, 1.38, sd * 1.03), (3.0, 0.55, 0.06), wd, 0.01)
    B((-2.93, 1.38, 0), (0.06, 0.55, 2.1), wd, 0.01)
    for k in range(5): B((-2.85 + k * 0.7, 1.38, 1.07), (0.06, 0.6, 0.04), dk, 0.0)
    if load is None:
        cv = cloth(canvas)
        B((-1.45, 2.1, 0), (3.0, 0.9, 2.1), cv, 0.25)
        K.cyl(P(-1.45, 2.5, 0), 1.05, 3.0, cv, 20, "x", None, yaw);
        for k in range(4): K.torus(P(-2.8 + k * 0.9, 2.1, 0), 1.06, 0.03, cv, 16, 5, "x", yaw, scale=(1, 1, 1), arc=math.pi)
    else:
        load(K, P, yaw)
    K.cyl(P(-0.15, 1.25, 1.06), 0.42, 0.22, tyre, 20, "z", None, yaw)                   # spare
    if not Kx: K.build()
    return P

def cargo_ship(name, x, z, yaw, L=134.0, B=17.0, hull_col="#5a6068", sup_col="#c8c4b8", load=0.7, rust=True, deck_cargo=True):
    """Liberty-type cargo ship (134 m): long box hull with flared bow and cruiser stern, midship house with bridge and
    funnel, five hatches, kingposts and derricks, deck cargo; local bow +x, waterline y 0"""
    c, s = math.cos(yaw), math.sin(yaw)
    P = lambda lx, ly, lz: (x + lx * c + lz * s, ly, z - lx * s + lz * c)
    K = Kit(name)
    hullm = mat_once("lhull" + hull_col, lambda: worn("lhull" + hull_col, hull_col, "#6a3a22" if rust else "#3a3a3a", 0.6, 0.25, 0.5, 0.7, "#3a3634"))
    red = mat_once("lred", lambda: worn("lred", "#6a2622", "#3a1a14", 0.7, 0.1, 1.0, 0.6, "#2a1610")); deck = pm("#5a5048", 0.8)
    sup = mat_once("lsup" + sup_col, lambda: worn("lsup" + sup_col, sup_col, "#8a6a4a", 0.6, 0.1, 2, 0.7, "#7a7468"))
    dk = pm("#1e1e20", 0.6); fb = 9.0
    rings = []
    for i in range(15):
        u = i / 14; lx = -L / 2 + u * L
        bow = max(0.0, (u - 0.82) / 0.18); stern = max(0.0, (0.1 - u) / 0.1)
        hw = B / 2 * (1 - 0.92 * bow ** 1.6) * (1 - 0.35 * stern ** 2)
        bot = -7.0 * (1 - 0.7 * bow) * (1 - 0.6 * stern)
        top = fb + 2.0 * bow ** 2 + 0.8 * stern
        rr = []
        for k in range(10):
            a = k / 9
            yy = bot + (top - bot) * a; ww = hw * (0.82 + 0.18 * min(1, a * 2.5)) * (1 + 0.06 * bow * a)
            rr.append(P(lx + bow * 3 * a, yy, ww))
        for k in range(10):
            a = 1 - k / 9
            yy = bot + (top - bot) * a; ww = hw * (0.82 + 0.18 * min(1, a * 2.5)) * (1 + 0.06 * bow * a)
            rr.append(P(lx + bow * 3 * a, yy, -ww))
        rings.append(rr)
    loft_k(K, rings, hullm)
    K.box(P(0, -1.0, 0), (L * 0.96, 2.0, B * 0.98), red, yaw, 0.2)
    K.box(P(0, fb - 0.05, 0), (L * 0.95, 0.2, B - 0.3), deck, yaw, 0.0)
    for sd in (-1, 1): K.box(P(0, fb + 0.55, sd * (B / 2 - 0.15)), (L * 0.92, 1.1, 0.12), hullm, yaw, 0.02)
    # midship house, bridge, funnel
    K.box(P(-6, fb + 3.0, 0), (20, 6.0, B - 2.5), sup, yaw, 0.15)
    K.box(P(-5, fb + 7.3, 0), (12, 2.6, B - 4), sup, yaw, 0.12)
    K.box(P(-3.2, fb + 9.4, 0), (5, 1.8, B - 1.0), sup, yaw, 0.1)
    for k in range(8): K.box(P(-0.68, fb + 9.6, -6 + k * 1.7), (0.05, 0.7, 1.2), pm("#1a2230", 0.05), yaw, 0.0)
    for k in range(10):
        for sd in (-1, 1): K.cyl(P(-14 + k * 1.8, fb + 3.6, sd * (B / 2 - 1.24)), 0.28, 0.06, pm("#1a2230", 0.05), 12, "z", None, yaw)
    K.cyl(P(-9.5, fb + 11.5, 0), 1.5, 6.5, mat_once("lfun", lambda: worn("lfun", "#2a2a2c", "#6a3a22", 0.6, 0.2, 2, 0.7)), 20, "y", None, yaw)
    K.cyl(P(-9.5, fb + 14.6, 0), 1.6, 0.4, dk, 20, "y", None, yaw)
    for k, hx in enumerate((48, 34, 18, -24, -40)):
        K.box(P(hx, fb + 0.6, 0), (9, 1.2, 7), sup, yaw, 0.08)
        K.box(P(hx, fb + 1.25, 0), (9.2, 0.1, 7.2), cloth("#3a3a2a"), yaw, 0.02)
    for mx_, h in ((41, 18), (-32, 16), (8, 20)):
        K.cyl(P(mx_, fb + h / 2, 0), 0.45, h, sup, 12, "y", None, yaw)
        for sd in (-1, 1):
            K.cyl(P(mx_ + 6, fb + h * 0.3, sd * 1.5), 0.2, 13, sup, 8, "x", None, yaw, 0, 0, -sd * 0.0 + 0.5)
        K.box(P(mx_, fb + h * 0.55, 0), (0.6, 0.5, 5.0), sup, yaw, 0.05)
    if deck_cargo:
        rnd = random.Random(int(x * 7 + z))
        for k in range(12):
            hx = rnd.choice((48, 34, 18, -24, -40)) + rnd.uniform(-3, 3); hz = rnd.uniform(-5, 5)
            K.box(P(hx, fb + 1.9 + rnd.random() * 0.2, hz), (rnd.uniform(1.6, 3), rnd.uniform(1.0, 1.6), rnd.uniform(1.4, 2.4)), wood("#9a7a4a", "#5a4428", 8, 0.8), yaw + rnd.uniform(-0.1, 0.1), 0.03)
    K.build()
    return P

# ---------------------------------------------------------------------------------------------------- structures
def lattice_mast(K, c, h, w0, w1, m, panels=None, yaw=0.0, arms=None):
    """steel lattice tower (Chain Home / radio mast / crane): four tapering legs, horizontal girts and X bracing"""
    panels = panels or max(4, int(h / 4)); cw, sw = math.cos(yaw), math.sin(yaw)
    def corner(k, y):
        w = w0 + (w1 - w0) * y / h; sx, sz = (-1, -1, 1, 1)[k], (-1, 1, 1, -1)[k]
        lx, lz = sx * w / 2, sz * w / 2
        return Vector((c[0] + lx * cw + lz * sw, c[1] + y, c[2] - lx * sw + lz * cw))
    def strut(a, b, r):
        d = b - a; L = d.length; mid = (a + b) / 2
        yaw_ = math.atan2(d.x, d.z); pitch = -math.asin(max(-1, min(1, d.y / L)))
        K.box(tuple(mid), (r, r, L), m, yaw_, 0.0, pitch)
    for k in range(4): strut(corner(k, 0), corner(k, h), 0.12 + 0.1 * w0 / 10)
    for p in range(panels + 1):
        y = h * p / panels
        for k in range(4): strut(corner(k, y), corner((k + 1) % 4, y), 0.07)
        if p < panels:
            y2 = h * (p + 1) / panels
            for k in range(4):
                strut(corner(k, y), corner((k + 1) % 4, y2), 0.05); strut(corner((k + 1) % 4, y), corner(k, y2), 0.05)
    if arms:
        for y, L in arms:
            for sd in (-1, 1):
                a = corner(0, y) * 0.5 + corner(2, y) * 0.5
                K.box((a.x + sd * L / 2 * cw, a.y, a.z - sd * L / 2 * sw), (L, 0.18, 0.18), m, yaw, 0.0)

def searchlight(name, c, yaw, pitch, length=380.0, r0=0.5, r1=9.0, strength=2.5, col=(0.78, 0.85, 1.0)):
    """a searchlight beam object (cone along its local +y after rotation); returns the object so it can sweep"""
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r0, depth=length, end_fill_type="NOTHING", location=(0, 0, 0))
    o = bpy.context.object; o.name = name
    for v in o.data.vertices: v.co.z = -v.co.z + length / 2   # narrow end at 0, wide end at +length
    o.data.materials.append(beam_mat(name, col, strength))
    o.visible_shadow = False
    try: o.visible_diffuse = False; o.visible_glossy = False
    except Exception: pass
    aim(o, c, yaw, pitch); return o
def aim(o, c, yaw, pitch):
    """point an object's local +z (blender) along three direction (yaw about +y from +z, pitch up)"""
    d = Vector((math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)))
    o.location = T(*c); o.rotation_euler = T(*d).to_track_quat("Z", "Y").to_euler()

def height_mesh(name, x0, x1, z0, z1, st, H, m, colfn=None):
    nx, nz = int((x1 - x0) / st) + 1, int((z1 - z0) / st) + 1
    vs, fs = [], []
    for j in range(nz):
        for i in range(nx):
            x, z = x0 + i * st, z0 + j * st; vs.append(T(x, H(x, z), z))
    for j in range(nz - 1):
        for i in range(nx - 1):
            a = j * nx + i; fs.append((a, a + 1, a + nx + 1, a + nx))
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs); me.update()
    for p in me.polygons: p.use_smooth = True
    if colfn:
        ca = me.color_attributes.new("mask", "FLOAT_COLOR", "POINT")
        for k, v in enumerate(vs): s = colfn(-v.x, v.y); ca.data[k].color = (s, s, s, 1)
    me.materials.append(m)
    return link(bpy.data.objects.new(name, me))

def sky(top, mid, horizon, sun_dir=None, sun_col=(1.0, 0.8, 0.5), glow=0.6, disc=0.0, strength=1.0, clouds=0.0, cloud_col=(1, 1, 1), cloud_shade=(0.55, 0.6, 0.72), cloud_scale=1.2):
    """sky gradient (horizon -> mid -> top), sun glow and optional painted cloud band (blender world)"""
    W = bpy.context.scene.world; nt = W.node_tree; n = nt.nodes; l = nt.links
    for x in list(n): n.remove(x)
    out = n.new("ShaderNodeOutputWorld"); bg = n.new("ShaderNodeBackground"); l.new(bg.outputs[0], out.inputs[0]); bg.inputs[1].default_value = strength
    co = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(co.outputs["Generated"], sep.inputs[0])
    rmp = n.new("ShaderNodeValToRGB"); l.new(sep.outputs["Z"], rmp.inputs["Fac"]); e = rmp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (*horizon, 1); e[1].position, e[1].color = 0.55, (*top, 1); x = e.new(0.12); x.color = (*mid, 1)
    col = rmp.outputs["Color"]
    if sun_dir is not None:
        sd = T(*sun_dir).normalized()
        dot = n.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; l.new(co.outputs["Generated"], dot.inputs[0]); dot.inputs[1].default_value = tuple(sd)
        mx0 = n.new("ShaderNodeMath"); mx0.operation = "MAXIMUM"; mx0.inputs[1].default_value = 0.0; l.new(dot.outputs["Value"], mx0.inputs[0])
        p1 = n.new("ShaderNodeMath"); p1.operation = "POWER"; p1.inputs[1].default_value = 12; l.new(mx0.outputs[0], p1.inputs[0])
        p2 = n.new("ShaderNodeMath"); p2.operation = "POWER"; p2.inputs[1].default_value = 2000; l.new(mx0.outputs[0], p2.inputs[0])
        g = n.new("ShaderNodeMath"); g.operation = "MULTIPLY"; g.inputs[1].default_value = glow; l.new(p1.outputs[0], g.inputs[0])
        g2 = n.new("ShaderNodeMath"); g2.operation = "MULTIPLY_ADD"; g2.inputs[1].default_value = disc; l.new(p2.outputs[0], g2.inputs[0]); l.new(g.outputs[0], g2.inputs[2])
        ad = n.new("ShaderNodeMix"); ad.data_type = "RGBA"; ad.blend_type = "ADD"; l.new(g2.outputs[0], ad.inputs[0]); l.new(col, ad.inputs[6]); ad.inputs[7].default_value = (*sun_col, 1)
        col = ad.outputs[2]
    if clouds:
        zp = n.new("ShaderNodeMath"); zp.operation = "ADD"; zp.inputs[1].default_value = 0.1; l.new(sep.outputs["Z"], zp.inputs[0])
        px = n.new("ShaderNodeMath"); px.operation = "DIVIDE"; l.new(sep.outputs["X"], px.inputs[0]); l.new(zp.outputs[0], px.inputs[1])
        py = n.new("ShaderNodeMath"); py.operation = "DIVIDE"; l.new(sep.outputs["Y"], py.inputs[0]); l.new(zp.outputs[0], py.inputs[1])
        cmb = n.new("ShaderNodeCombineXYZ"); l.new(px.outputs[0], cmb.inputs[0]); l.new(py.outputs[0], cmb.inputs[1])
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = cloud_scale; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.6; l.new(cmb.outputs[0], nz.inputs["Vector"])
        cov = n.new("ShaderNodeMapRange"); cov.inputs["From Min"].default_value = 0.5; cov.inputs["From Max"].default_value = 0.68; l.new(nz.outputs["Fac"], cov.inputs["Value"])
        band = n.new("ShaderNodeMapRange"); band.inputs["From Min"].default_value = 0.0; band.inputs["From Max"].default_value = 0.06; l.new(sep.outputs["Z"], band.inputs["Value"])
        fade = n.new("ShaderNodeMapRange"); fade.inputs["From Min"].default_value = 0.7; fade.inputs["From Max"].default_value = 0.3; l.new(sep.outputs["Z"], fade.inputs["Value"])
        m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; l.new(cov.outputs["Result"], m1.inputs[0]); l.new(band.outputs["Result"], m1.inputs[1])
        m2 = n.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; m2.inputs[1].default_value = clouds; l.new(m1.outputs[0], m2.inputs[0])
        m3 = n.new("ShaderNodeMath"); m3.operation = "MULTIPLY"; l.new(m2.outputs[0], m3.inputs[0]); l.new(fade.outputs["Result"], m3.inputs[1])
        sh = n.new("ShaderNodeMix"); sh.data_type = "RGBA"; l.new(nz.outputs["Fac"], sh.inputs[0]); sh.inputs[6].default_value = (*cloud_shade, 1); sh.inputs[7].default_value = (*cloud_col, 1)
        mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(m3.outputs[0], mx.inputs[0]); l.new(col, mx.inputs[6]); l.new(sh.outputs[2], mx.inputs[7])
        col = mx.outputs[2]
    l.new(col, bg.inputs[0])

def fsphere(K, c, r, m, seg=12, scale=(1, 1, 1)):
    """uv sphere written straight into the kit bmesh (bmesh.ops.create_uvsphere gets slow on big meshes)"""
    bm, _ = K._get(0.0); rings = max(4, seg // 2); vs = []
    top = bm.verts.new(T(c[0], c[1] + r * scale[1], c[2])); bot = bm.verts.new(T(c[0], c[1] - r * scale[1], c[2]))
    for i in range(1, rings):
        ph = math.pi * i / rings; y = math.cos(ph); rr = math.sin(ph)
        vs.append([bm.verts.new(T(c[0] + r * scale[0] * rr * math.cos(a * math.tau / seg), c[1] + r * scale[1] * y, c[2] + r * scale[2] * rr * math.sin(a * math.tau / seg))) for a in range(seg)])
    for a in range(seg):
        a2 = (a + 1) % seg
        bm.faces.new((top, vs[0][a2], vs[0][a])); bm.faces.new((bot, vs[-1][a], vs[-1][a2]))
        for i in range(rings - 2): bm.faces.new((vs[i][a], vs[i][a2], vs[i + 1][a2], vs[i + 1][a]))
    allv = [top, bot] + [v for r_ in vs for v in r_]
    K._finish(allv, m, 0.0, True)

def cumulus(K, c, w, h, rnd, m, n=9):
    """a cumulus heap: many overlapping puffs on a flat base, tallest and biggest in the middle, small cauliflower
    puffs round the rim"""
    n = max(n, 14)
    for k in range(n):
        a = rnd.random() * math.tau; d = math.sqrt(rnd.random()) * 0.5 * w; f = 1 - d / (0.5 * w)
        r = w * (0.08 + 0.16 * f) * rnd.uniform(0.75, 1.15)
        y = c[1] + r * 0.35 + f * h * rnd.uniform(0.5, 1.0)
        fsphere(K, (c[0] + d * math.cos(a), y, c[2] + d * math.sin(a) * 0.7), r, m, 12, (1.0, 0.85, 1.0))
    for k in range(6):
        a = rnd.random() * math.tau; r = w * 0.18
        fsphere(K, (c[0] + 0.25 * w * math.cos(a), c[1] + r * 0.2, c[2] + 0.18 * w * math.sin(a)), r, m, 12, (1.3, 0.35, 1.0))

def sun_light(direction, energy, col, angle=2.0):
    """sun travelling along three direction"""
    o = lib.light("SUN", T(0, 10, 0), energy, col, math.radians(angle)); lib.look_at(o, o.location + T(*direction)); return o
def area(c, target, energy, col, size, size_y=None):
    o = lib.light("AREA", T(*c), energy, col, size, size_y=size_y); lib.look_at(o, T(*target)); return o
def point(c, energy, col, r=0.05, cam=False):
    o = lib.light("POINT", T(*c), energy, col, r)
    if not cam:
        try: o.visible_camera = False
        except Exception: pass
    return o
def spot(c, target, energy, col, angle=50, blend=0.6, r=0.05):
    o = lib.light("SPOT", T(*c), energy, col, r); o.data.spot_size = math.radians(angle); o.data.spot_blend = blend; lib.look_at(o, T(*target)); return o

def img_mat(name, path, rough=0.6, emit=0.0):
    """image texture on UVs (posters, maps, photos)"""
    def mk():
        m = lib.principled(name, (1, 1, 1), rough); t, n, l = nodes(m); b = n["Principled BSDF"]
        it = n.new("ShaderNodeTexImage"); it.image = bpy.data.images.load(path, check_existing=True); it.interpolation = "Cubic"
        l.new(it.outputs["Color"], b.inputs["Base Color"])
        if emit: l.new(it.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit
        return m
    return cached("img" + name, mk)
def quad(name, corners, m):
    """textured quad from four three-space corners (bl, br, tr, tl)"""
    me = bpy.data.meshes.new(name); me.from_pydata([T(*p) for p in corners], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for k, cc in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = cc
    me.materials.append(m); return link(bpy.data.objects.new(name, me))
def wall_quad(name, c, w, h, m, yaw=0.0):
    """upright textured quad centred on c facing three -z at yaw 0"""
    ca, sa = math.cos(yaw), math.sin(yaw)
    P = lambda u, v: (c[0] + u * ca, c[1] + v, c[2] - u * sa)
    return quad(name, [P(w / 2, -h / 2), P(-w / 2, -h / 2), P(-w / 2, h / 2), P(w / 2, h / 2)], m)

def clone(e, name):
    """linked copy of a built model (an Empty with children): shares the meshes, new Empty to move"""
    e2 = empty(name)
    for ch in e.children:
        o = ch.copy(); o.name = name + "_" + ch.name; bpy.context.scene.collection.objects.link(o); o.parent = e2
    return e2
def show(e, on):
    e.hide_render = not on
    for ch in e.children: ch.hide_render = not on

def panzer(name, c, yaw, col="#b89a62", hatch_open=True, Kx=None, scheme_dark=False):
    """German medium tank (Panzer III style, 5.5 m): box hull with superstructure, side-skirt wheels, three-sided turret
    with a short gun and a commander's cupola (open hatch), stowage, jerrycans; nose +x local; c = ground centre.
    Plain finish (no insignia)."""
    K = Kx or Kit(name); cw, sw = math.cos(yaw), math.sin(yaw)
    P = lambda lx, ly, lz: (c[0] + lx * cw + lz * sw, c[1] + ly, c[2] - lx * sw + lz * cw)
    hull = mat_once("pz" + col, lambda: worn("pz" + col, col, "#5a4a32", 0.62, 0.25, 7, 0.68, "#6a5a3a"))
    trk = mat_once("pztrk", lambda: worn("pztrk", "#3a3430", "#5a4a3a", 0.8, 0.4, 20, 0.6)); stl = pm("#2a2a2a", 0.4, 0.6)
    B = lambda lc, s, m, bev=0.04: K.box(P(*lc), s, m, yaw, bev)
    B((0, 1.05, 0), (5.2, 0.9, 2.2), hull, 0.05)
    B((-0.2, 1.75, 0), (4.6, 0.6, 2.9), hull, 0.04)
    B((2.45, 1.25, 0), (0.6, 0.8, 2.1), hull, 0.05)
    for sd in (-1, 1):
        B((0, 0.6, sd * 1.25), (5.6, 0.9, 0.5), trk, 0.3)
        for k in range(6): K.cyl(P(-2.0 + k * 0.78, 0.48, sd * 1.32), 0.3, 0.12, hull, 18, "z", None, yaw)
        for k in range(3): K.cyl(P(-1.6 + k * 1.3, 1.0, sd * 1.32), 0.1, 0.1, hull, 10, "z", None, yaw)
        K.cyl(P(2.6, 0.75, sd * 1.32), 0.32, 0.14, stl, 14, "z", None, yaw)
        B((0, 1.47, sd * 1.36), (5.4, 0.05, 0.42), hull, 0.01)
        for k in range(3): B((-2.4 + k * 0.42, 1.65, sd * 1.25), (0.2, 0.42, 0.32), pm("#4a4a3a", 0.6), 0.03)
    B((0.85, 2.15, 0), (0.1, 0.25, 1.6), hull, 0.02)
    B((-0.5, 2.4, 0), (2.4, 0.75, 2.0), hull, 0.06)                     # turret
    B((-0.5, 2.82, 0), (2.1, 0.08, 1.8), hull, 0.02)
    B((0.85, 2.38, 0), (0.35, 0.55, 0.85), hull, 0.05)                  # mantlet
    K.cyl(P(1.75, 2.38, 0), 0.08, 1.8, stl, 12, "x", None, yaw)
    K.cyl(P(2.62, 2.38, 0), 0.1, 0.12, stl, 12, "x", None, yaw)
    K.cyl(P(-1.15, 3.0, 0.35), 0.36, 0.3, hull, 18)                      # cupola
    if hatch_open:
        for sd in (-1, 1): K.box(P(-1.15, 3.32, 0.35 + sd * 0.3), (0.55, 0.36, 0.04), hull, yaw, 0.01, 0, 0)
    else: K.cyl(P(-1.15, 3.18, 0.35), 0.34, 0.06, hull, 18)
    B((-1.75, 2.3, 0), (0.25, 0.55, 1.6), hull, 0.03)                   # stowage bin
    K.cyl(P(-1.9, 2.95, -0.7), 0.012, 1.4, stl, 4, "y", None, yaw, 0, 0.2)
    for k in range(2): K.cyl(P(-2.5, 1.65, -0.6 + k * 1.2), 0.18, 0.5, pm("#5a4a2a", 0.85), 12, "x", None, yaw)
    K.cyl(P(-2.75, 1.6, 0.0), 0.32, 0.12, trk, 14, "x", None, yaw)
    if not Kx: K.build()
    return P

# kit_sbpw.Kit.sphere goes through bmesh.ops.create_uvsphere, which slows to seconds per call on a big kit mesh:
# in our sets every Kit sphere is written directly instead (same signature).
Kit.sphere = lambda self, c, r, m, seg=12, scale=(1, 1, 1), bev=0.0: fsphere(self, c, r, m, seg, scale)

def i16(name, wrecked=False, col=("#4a5a32", "#4a5a32", "#8aa0b0")):
    """Polikarpov I-16 (9 m span): barrel fuselage behind a big round radial cowling, short tapered wings, open cockpit,
    red stars; wrecked = scorched, a wing broken off"""
    K = Kit(name); sk = camo(name + "c", *col, 0.4) if not wrecked else mat_once("i16burnt", lambda: worn("i16burnt", "#2a2420", "#5a3a1e", 0.9, 0.3, 6, 0.55, "#141010"))
    st = [(2.6, 0.62, 0.62, 0.62, 0.0), (2.2, 0.66, 0.66, 0.66, 0.0), (1.2, 0.62, 0.66, 0.64, 0.02), (0.0, 0.52, 0.56, 0.56, 0.05), (-1.4, 0.34, 0.42, 0.4, 0.1),
          (-2.8, 0.16, 0.3, 0.2, 0.2), (-3.4, 0.05, 0.24, 0.06, 0.25)]
    body(K, sk, st, 22, 2.0)
    K.cyl((0, 0, 2.62), 0.5, 0.04, pm("#1a1a1a", 0.6), 22, "z")
    K.cyl((0, 0, 2.8), 0.001, 0.35, pm("#3a3a3a", 0.4, 0.4), 16, "z", 0.22)
    if not wrecked: prop(K, (0, 0, 2.75), 1.4, 2, "#3a3a3a", False)
    span = 4.5 if not wrecked else 2.0
    for sd in (-1, 1):
        sp = span if (sd > 0 or not wrecked) else 4.5
        surface(K, sk, [(sd * s, 1.5 - 0.3 * s / 4.5, 2.2 - 1.0 * s / 4.5, -0.35 + s * 0.06) for s in (0.4, sp * 0.5, sp)], 0.14)
        if not wrecked:
            for c_ in ((sd * 3.4, -0.15, 0.9),): roundel(K, c_, [(0.4, "#c81e22")], "y")
    for sd in (-1, 1): surface(K, sk, [(sd * s, -2.7, 0.9 - 0.3 * s / 1.5, 0.15) for s in (0.1, 0.8, 1.5)], 0.1)
    surface(K, sk, [(y, -2.75 - 0.1 * y, 1.0 - 0.4 * y / 1.2, 0.0) for y in (0.2, 0.7, 1.2)], 0.1, "y")
    K.box((0, 0.66, 0.3), (0.5, 0.25, 0.2), glassm(), 0, 0.02, 0.5)
    for sd in (-1, 1): gear(K, sd * 0.8, 0.9, -0.3, -1.25, 0.32, pm("#5a5a5a", 0.5, 0.6), "#141414")
    obs = K.build(); e = empty(name); place(obs, e); return e

def t34(name, c, yaw, col="#4a5a32", Kx=None, unpainted=False):
    """Soviet T-34 (1941): low hull with sloped glacis and sides, big road wheels, cast turret with a long 76 mm gun,
    hatch; nose +x local; plain with a white tactical number"""
    K = Kx or Kit(name); cw, sw = math.cos(yaw), math.sin(yaw)
    P = lambda lx, ly, lz: (c[0] + lx * cw + lz * sw, c[1] + ly, c[2] - lx * sw + lz * cw)
    hull = mat_once("t34" + col, lambda: worn("t34" + col, col, "#3a3a32", 0.62, 0.3, 7, 0.7, "#4a4a3a")) if not unpainted else mat_once("t34raw", lambda: worn("t34raw", "#5a5a58", "#7a4a2a", 0.5, 0.6, 5, 0.6, "#3a3a38"))
    trk = mat_once("t34trk", lambda: worn("t34trk", "#2a2826", "#5a4a3a", 0.8, 0.5, 20, 0.6)); stl = pm("#2a2a2a", 0.4, 0.6)
    K.box(P(0, 1.0, 0), (5.2, 0.8, 2.3), hull, yaw, 0.04)
    K.box(P(2.35, 1.0, 0), (1.2, 0.7, 2.3), hull, yaw, 0.03, 0, -0.9)          # sloped glacis
    K.box(P(-0.3, 1.5, 0), (4.4, 0.25, 2.9), hull, yaw, 0.03)
    for sd in (-1, 1):
        K.box(P(0, 0.6, sd * 1.3), (5.8, 0.85, 0.55), trk, yaw, 0.28)
        for k in range(5): K.cyl(P(-2.1 + k * 1.05, 0.55, sd * 1.36), 0.4, 0.14, hull, 20, "z", None, yaw)
    lathe(f"{name}tur", [(0.0, 0.0), (1.05, 0.0), (1.1, 0.2), (0.95, 0.65), (0.0, 0.7)], P(0.1, 1.6, 0), hull, 24, yaw=yaw, sx=1.15, sz=0.95)
    K.cyl(P(2.2, 2.0, 0), 0.07, 3.0, stl, 10, "x", None, yaw)
    K.box(P(0.95, 2.0, 0), (0.4, 0.4, 0.5), hull, yaw, 0.05)
    K.cyl(P(-0.3, 2.33, 0), 0.32, 0.06, hull, 16)
    for sd in (-1, 1): K.box(P(-2.0, 1.65, sd * 1.2), (0.6, 0.3, 0.35), pm("#3a3a2a", 0.6), yaw, 0.03)
    if not Kx: K.build()
    return P

def jeep(name, c, yaw, col="#4a5232", Kx=None):
    """Willys MB jeep: flat bonnet with slotted grille, open body, fold-down screen, spare on the back; nose +x local"""
    K = Kx or Kit(name); cw, sw = math.cos(yaw), math.sin(yaw)
    P = lambda lx, ly, lz: (c[0] + lx * cw + lz * sw, c[1] + ly, c[2] - lx * sw + lz * cw)
    m = mat_once("jeep" + col, lambda: worn("jeep" + col, col, "#3a3a2a", 0.6, 0.2, 9, 0.7)); tyre = pm("#161616", 0.85); dk = pm("#1a1a1a", 0.6)
    K.box(P(0.95, 0.85, 0), (1.2, 0.35, 1.25), m, yaw, 0.04)
    K.box(P(1.56, 0.8, 0), (0.04, 0.42, 1.0), dk, yaw, 0.0)
    for k in range(9): K.box(P(1.59, 0.8, -0.4 + k * 0.1), (0.02, 0.36, 0.04), m, yaw, 0.0)
    K.box(P(-0.5, 0.75, 0), (1.9, 0.45, 1.4), m, yaw, 0.04)
    K.box(P(-0.5, 0.96, 0), (1.7, 0.04, 1.2), pm("#3a3a2a", 0.8), yaw, 0.0)
    K.box(P(0.32, 1.25, 0), (0.04, 0.45, 1.3), m, yaw, 0.01)
    for sd in (-1, 1):
        for wx in (1.0, -1.05): K.cyl(P(wx, 0.4, sd * 0.68), 0.38, 0.22, tyre, 20, "z", None, yaw)
        K.cyl(P(1.5, 0.95, sd * 0.42), 0.09, 0.06, pm("#e8e8d8", 0.2, 0.3), 12, "x", None, yaw)
    K.cyl(P(-1.5, 0.85, 0), 0.36, 0.2, tyre, 20, "x", None, yaw)
    K.box(P(-0.2, 0.95, 0.3), (0.5, 0.35, 0.45), pm("#3a3a2a", 0.8), yaw, 0.05); K.box(P(-0.2, 0.95, -0.3), (0.5, 0.35, 0.45), pm("#3a3a2a", 0.8), yaw, 0.05)
    K.cyl(P(0.15, 1.1, 0.3), 0.18, 0.04, dk, 14, "y", None, yaw, 0, 0.6)
    if not Kx: K.build()
    return P
