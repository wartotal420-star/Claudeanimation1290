# Fast batched set-building kit for the street / beerhall / press / wallst sets (three.js layout coordinates, y up).
# Geometry is accumulated into one bmesh per bevel width and turned into a few objects at the end (thousands of props
# without thousands of bpy.ops calls). Rotations are given in three.js axes: yaw about +y, pitch about +x, roll about +z.
# Text faces three -z at yaw 0, -x at yaw +90 deg, +x at yaw -90 deg, +z at yaw 180 deg.
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix
import lib
from lib import T, hexc, nodes, ramp, bump

R90 = math.pi / 2

def _rot(yaw=0.0, pitch=0.0, roll=0.0):
    # three Rx(pitch) -> blender Rx(-pitch); three Ry(yaw) -> blender Rz(yaw); three Rz(roll) -> blender Ry(roll)
    return Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(roll, 4, "Y") @ Matrix.Rotation(-pitch, 4, "X")

def _xf(c, s, yaw=0.0, pitch=0.0, roll=0.0):
    S = Matrix.Diagonal((s[0], s[2], s[1], 1.0))
    return Matrix.Translation(T(*c)) @ _rot(yaw, pitch, roll) @ S

# ---------------- materials (cached per build) ----------------
_MC = {}
def reset(): _MC.clear()
def cached(key, fn):
    m = _MC.get(key)
    if m is None: m = _MC[key] = fn()
    return m
def pm(hx, rough=0.6, metal=0.0, key=None):
    return cached(key or f"pm{hx}{rough}{metal}", lambda: lib.principled(f"k{hx}", hexc(hx), rough, metal))
def em(hx, s, key=None):
    return cached(key or f"em{hx}{s}", lambda: lib.emit(f"ke{hx}", hexc(hx), s))
def brass(): return cached("brass", lambda: lib.principled("kbrass", hexc("#c8963a"), 0.28, 1.0))
def gold(): return cached("gold", lambda: lib.principled("kgold", hexc("#e8b84a"), 0.25, 1.0))
def iron(hx="#26262c"): return cached("iron" + hx, lambda: lib.principled("kiron", hexc(hx), 0.45, 0.85))
def wood(a, b2, sc=6.0, rough=0.5):
    """straight-grained wood: soft bands across (x + y) with streaky noise, no camouflage blotches"""
    def mk():
        m, n, l, tc = _base(f"kw{a}", a, rough)
        sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Object"], sp.inputs[0])
        ad = n.new("ShaderNodeMath"); ad.operation = "ADD"; l.new(sp.outputs[0], ad.inputs[0]); l.new(sp.outputs[1], ad.inputs[1])
        cb = n.new("ShaderNodeCombineXYZ"); l.new(ad.outputs[0], cb.inputs[0]); l.new(sp.outputs[2], cb.inputs[1])
        mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 0.08, 1.0); l.new(cb.outputs[0], mp.inputs["Vector"])
        wv = n.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = sc * 1.5; wv.inputs["Distortion"].default_value = 1.5
        wv.inputs["Detail"].default_value = 2; wv.inputs["Detail Scale"].default_value = 2
        try: wv.bands_direction = "X"
        except Exception: pass
        l.new(mp.outputs[0], wv.inputs["Vector"])
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = sc * 6; nz.inputs["Detail"].default_value = 4; l.new(mp.outputs[0], nz.inputs["Vector"])
        mx = n.new("ShaderNodeMix"); mx.data_type = "FLOAT"; mx.inputs[0].default_value = 0.35; l.new(wv.outputs["Fac"], mx.inputs[2]); l.new(nz.outputs["Fac"], mx.inputs[3])
        A, B = hexc(a), hexc(b2)
        r = ramp(n, l, mx.outputs[0], [(0.25, B), (0.55, A), (0.85, tuple(min(1, c * 1.2) for c in A))])
        l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"]); bump(n, l, mx.outputs[0], 0.08, 0.01)
        return m
    return cached(f"wd{a}{b2}{sc}{rough}", mk)
def cloth(hx): return cached("cl" + hx, lambda: lib.cloth(f"kc{hx}", hx))
def glassm(): return cached("glass", lambda: lib.glass("kglass"))

def _base(name, hx, rough=0.6):
    m = lib.principled(name, hexc(hx), rough); t, n, l = nodes(m)
    return m, n, l, n.new("ShaderNodeTexCoord")

def grime(name, hx, dirt=0.35, scale=4.0, rough=0.85):
    """plaster / painted stucco with blotchy grime and vertical rain streaks"""
    def mk():
        m, n, l, tc = _base(name, hx, rough)
        mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale * 2.5, scale * 2.5, scale * 0.25)
        l.new(tc.outputs["Object"], mp.inputs["Vector"])
        st = n.new("ShaderNodeTexNoise"); st.inputs["Scale"].default_value = 1.0; st.inputs["Detail"].default_value = 4; l.new(mp.outputs[0], st.inputs["Vector"])
        bl = n.new("ShaderNodeTexNoise"); bl.inputs["Scale"].default_value = scale; bl.inputs["Detail"].default_value = 8; l.new(tc.outputs["Object"], bl.inputs["Vector"])
        mx = n.new("ShaderNodeMath"); mx.operation = "MULTIPLY"; l.new(st.outputs["Fac"], mx.inputs[0]); l.new(bl.outputs["Fac"], mx.inputs[1])
        a = hexc(hx)
        r = ramp(n, l, mx.outputs[0], [(0.12, tuple(min(1, c * 1.12) for c in a)), (0.25, a), (0.42, tuple(c * (1 - dirt) for c in a))])
        l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"]); bump(n, l, bl.outputs["Fac"], 0.2, 0.01)
        return m
    return cached("gr" + name + hx, mk)

def brick(name, a, b2, mortar="#5a4e46", scale=4.0, w=0.5, h=0.25, rough=0.85):
    """brick for vertical walls of any orientation: the pattern runs on (x + y, z) so courses stay horizontal"""
    def mk():
        m, n, l, tc = _base(name, a, rough)
        sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Object"], sp.inputs[0])
        ad = n.new("ShaderNodeMath"); ad.operation = "ADD"; l.new(sp.outputs[0], ad.inputs[0]); l.new(sp.outputs[1], ad.inputs[1])
        cb = n.new("ShaderNodeCombineXYZ"); l.new(ad.outputs[0], cb.inputs[0]); l.new(sp.outputs[2], cb.inputs[1])
        br = n.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = scale
        br.inputs["Color1"].default_value = (*hexc(a), 1); br.inputs["Color2"].default_value = (*hexc(b2), 1); br.inputs["Mortar"].default_value = (*hexc(mortar), 1)
        br.inputs["Brick Width"].default_value = w; br.inputs["Row Height"].default_value = h; br.inputs["Mortar Size"].default_value = 0.015
        l.new(cb.outputs[0], br.inputs["Vector"])
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 5; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 0.4
        l.new(br.outputs["Color"], mx.inputs[6]); l.new(nz.outputs["Color"], mx.inputs[7])
        l.new(mx.outputs[2], n["Principled BSDF"].inputs["Base Color"]); bump(n, l, br.outputs["Fac"], 0.6, 0.01)
        return m
    return cached("bk" + name, mk)

def stripes(name, a, b2, freq=14.0, axis=1):
    """cloth with stripes across blender axis `axis` (1 = blender y = three z)"""
    def mk():
        m, n, l, tc = _base(name, a, 0.85)
        sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Object"], sp.inputs[0])
        mu = n.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = freq; l.new(sp.outputs[axis], mu.inputs[0])
        sn = n.new("ShaderNodeMath"); sn.operation = "SINE"; l.new(mu.outputs[0], sn.inputs[0])
        gt = n.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.0; l.new(sn.outputs[0], gt.inputs[0])
        mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(gt.outputs[0], mx.inputs[0])
        mx.inputs[6].default_value = (*hexc(a), 1); mx.inputs[7].default_value = (*hexc(b2), 1)
        l.new(mx.outputs[2], n["Principled BSDF"].inputs["Base Color"])
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 80; l.new(tc.outputs["Object"], nz.inputs["Vector"]); bump(n, l, nz.outputs["Fac"], 0.2)
        return m
    return cached("str" + name + a + b2, mk)

def wet_cobbles(name, a="#6e6a78", b2="#4c4856", wet=0.8, scale=5.0):
    """cobblestones whose puddles go mirror-glossy (wet > 0): reflect the lanterns and windows at night"""
    def mk():
        m, n, l, tc = _base(name, a, 0.5)
        vo = n.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = scale
        try: vo.feature = "DISTANCE_TO_EDGE"
        except Exception: pass
        l.new(tc.outputs["Object"], vo.inputs["Vector"])
        vc = n.new("ShaderNodeTexVoronoi"); vc.inputs["Scale"].default_value = scale; l.new(tc.outputs["Object"], vc.inputs["Vector"])
        pud = n.new("ShaderNodeTexNoise"); pud.inputs["Scale"].default_value = 0.35; pud.inputs["Detail"].default_value = 3; l.new(tc.outputs["Object"], pud.inputs["Vector"])
        stone = ramp(n, l, vc.outputs["Color"], [(0.0, hexc(b2)), (0.5, hexc(a)), (1.0, tuple(min(1, c * 1.25) for c in hexc(a)))])
        edge = ramp(n, l, vo.outputs["Distance"], [(0.0, (0.0, 0.0, 0.0)), (0.08, (1, 1, 1))])
        col = n.new("ShaderNodeMix"); col.data_type = "RGBA"; col.blend_type = "MULTIPLY"; col.inputs[0].default_value = 1.0
        l.new(stone.outputs["Color"], col.inputs[6]); l.new(edge.outputs["Color"], col.inputs[7])
        wetm = ramp(n, l, pud.outputs["Fac"], [(0.42, (0, 0, 0)), (0.52, (1, 1, 1))])
        dk = n.new("ShaderNodeMix"); dk.data_type = "RGBA"; dk.blend_type = "MULTIPLY"
        l.new(wetm.outputs["Color"], dk.inputs[0]); l.new(col.outputs[2], dk.inputs[6]); dk.inputs[7].default_value = (0.45, 0.45, 0.5, 1)
        l.new(dk.outputs[2], n["Principled BSDF"].inputs["Base Color"])
        ro = n.new("ShaderNodeMapRange"); l.new(wetm.outputs["Color"], ro.inputs[0])
        ro.inputs[3].default_value = 0.55; ro.inputs[4].default_value = 0.55 - 0.5 * wet
        l.new(ro.outputs[0], n["Principled BSDF"].inputs["Roughness"])
        # stones bulge, flatter where wet (puddle surface)
        hb = n.new("ShaderNodeMath"); hb.operation = "MULTIPLY"; l.new(vo.outputs["Distance"], hb.inputs[0])
        inv = n.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; l.new(wetm.outputs["Color"], inv.inputs[1])
        l.new(inv.outputs[0], hb.inputs[1])
        bump(n, l, hb.outputs[0], 0.7, 0.03)
        return m
    return cached("cob" + name, mk)

def window_glow(name, hx="#ffb866", s=3.0):
    """lit window: warm emission broken up by soft noise (lamps, curtains, rooms of different depth)"""
    def mk():
        m = bpy.data.materials.new(name); t, n, l = nodes(m); b = n["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1); b.inputs["Roughness"].default_value = 0.05
        tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 2
        l.new(tc.outputs["Object"], nz.inputs["Vector"])
        c = hexc(hx)
        r = ramp(n, l, nz.outputs["Fac"], [(0.3, tuple(x * 0.35 for x in c)), (0.55, c), (0.75, tuple(min(1, x * 1.3) for x in c))])
        l.new(r.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = s
        return m
    return cached("wg" + name + hx + str(s), mk)

def paper(hx="#efe4c8", age=0.25):
    def mk():
        m, n, l, tc = _base("kpaper" + hx, hx, 0.85)
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9; nz.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        a = hexc(hx)
        r = ramp(n, l, nz.outputs["Fac"], [(0.35, a), (0.7, (a[0] * (1 - age * 0.3), a[1] * (1 - age * 0.6), a[2] * (1 - age)))])
        l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
        return m
    return cached("pa" + hx + str(age), mk)

def set_world(top, horizon, strength=1.0, cam_top=None, cam_hor=None):
    """sky gradient (camera rays may see a richer gradient than the light it casts)"""
    W = bpy.context.scene.world; t, n, l = W.node_tree, W.node_tree.nodes, W.node_tree.links
    for x in list(n): n.remove(x)
    out = n.new("ShaderNodeOutputWorld"); tc = n.new("ShaderNodeTexCoord"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Generated"], sp.inputs[0])
    def grad(a, b2):
        r = n.new("ShaderNodeValToRGB"); r.color_ramp.elements[0].position = 0.0; r.color_ramp.elements[0].color = (*a, 1)
        r.color_ramp.elements[1].position = 0.45; r.color_ramp.elements[1].color = (*b2, 1); l.new(sp.outputs[2], r.inputs[0]); return r
    g1 = grad(horizon, top); bg1 = n.new("ShaderNodeBackground"); bg1.inputs[1].default_value = strength; l.new(g1.outputs[0], bg1.inputs[0])
    if cam_top:
        g2 = grad(cam_hor, cam_top); bg2 = n.new("ShaderNodeBackground"); bg2.inputs[1].default_value = 1.0; l.new(g2.outputs[0], bg2.inputs[0])
        lp = n.new("ShaderNodeLightPath"); mx = n.new("ShaderNodeMixShader")
        l.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); l.new(bg1.outputs[0], mx.inputs[1]); l.new(bg2.outputs[0], mx.inputs[2]); l.new(mx.outputs[0], out.inputs[0])
    else: l.new(bg1.outputs[0], out.inputs[0])

# ---------------- fonts / text ----------------
_FONTS = {}
def font(kind="serif"):
    paths = {"serif": ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
             "sans": ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Futura.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"],
             "mono": ["/System/Library/Fonts/Supplemental/Courier New Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"]}[kind]
    if kind not in _FONTS:
        _FONTS[kind] = None
        for p in paths:
            if os.path.exists(p):
                try: _FONTS[kind] = bpy.data.fonts.load(p, check_existing=True); break
                except Exception: pass
    return _FONTS[kind]
CW = {"serif": 0.66, "sans": 0.64, "mono": 0.6}
def text(body, c, size, m, yaw=0.0, kind="serif", extrude=0.004, align="CENTER", fit=None, pitch=0.0):
    """standing text centred on c (three coords); fit = max width in m (shrinks the size to fit)"""
    if fit:
        longest = max(len(s) for s in body.split("\n")) or 1
        size = min(size, fit / (CW[kind] * longest))
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.size = size; cu.align_x = align; cu.extrude = extrude
    try: cu.align_y = "CENTER"
    except Exception: pass
    f = font(kind)
    if f: cu.font = f
    cu.materials.append(m)
    o = bpy.data.objects.new("txt", cu); bpy.context.scene.collection.objects.link(o)
    o.location = T(*c); o.rotation_euler = (R90 + pitch, 0, yaw)
    return o
def flat_text(body, c, size, m, yaw=0.0, kind="serif", align="CENTER", fit=None):
    """text lying on a table top (reads from -z), c = point on the surface"""
    o = text(body, c, size, m, 0.0, kind, 0.0008, align, fit)
    o.rotation_euler = (0, 0, yaw); return o

# ---------------- batched geometry ----------------
class Kit:
    def __init__(self, name="set"):
        self.name = name; self.parts = {}
    def _get(self, bev):
        if bev not in self.parts: self.parts[bev] = [bmesh.new(), []]
        return self.parts[bev]
    def _mi(self, mats, m):
        for i, x in enumerate(mats):
            if x is m: return i
        mats.append(m); return len(mats) - 1
    def _finish(self, verts, m, bev, smooth_axis=None):
        bm, mats = self._get(bev); mi = self._mi(mats, m)
        fs = set()
        for v in verts: fs.update(v.link_faces)
        for f in fs:
            f.material_index = mi; f.normal_update()
            if smooth_axis is not None:
                f.smooth = smooth_axis is True or abs(f.normal.dot(smooth_axis)) < 0.7
        if smooth_axis is not None and smooth_axis is not True:
            es = set()
            for f in fs: es.update(f.edges)
            for e in es:
                lf = e.link_faces
                if len(lf) == 2 and lf[0].smooth != lf[1].smooth: e.smooth = False
        return fs
    def box(self, c, s, m, yaw=0.0, bev=0.01, pitch=0.0, roll=0.0):
        bm, _ = self._get(bev)
        r = bmesh.ops.create_cube(bm, size=1.0, matrix=_xf(c, s, yaw, pitch, roll))
        self._finish(r["verts"], m, bev)
    def boxr(self, x0, y0, z0, x1, y1, z1, m, bev=0.01):
        self.box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), m, 0.0, bev)
    def cyl(self, c, r, h, m, seg=16, axis="y", r2=None, yaw=0.0, bev=0.0, pitch=0.0, roll=0.0):
        """cylinder centred on c (not based!) along three axis"""
        bm, _ = self._get(bev)
        a = {"y": Matrix.Identity(4), "x": Matrix.Rotation(R90, 4, "Y"), "z": Matrix.Rotation(R90, 4, "X")}[axis]
        M = Matrix.Translation(T(*c)) @ _rot(yaw, pitch, roll) @ a
        res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h, matrix=M)
        ax = (M.to_3x3() @ Vector((0, 0, 1))).normalized()
        self._finish(res["verts"], m, bev, ax)
    def sphere(self, c, r, m, seg=12, scale=(1, 1, 1), bev=0.0):
        bm, _ = self._get(bev)
        M = Matrix.Translation(T(*c)) @ Matrix.Diagonal((scale[0], scale[2], scale[1], 1.0))
        res = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r, matrix=M)
        self._finish(res["verts"], m, bev, True)
    def torus(self, c, R, r, m, seg=24, rseg=8, axis="y", yaw=0.0, pitch=0.0, roll=0.0, scale=(1, 1, 1), arc=2 * math.pi):
        """torus around three axis (ring in the plane normal to it)"""
        bm, _ = self._get(0.0)
        a = {"y": Matrix.Identity(4), "x": Matrix.Rotation(R90, 4, "Y"), "z": Matrix.Rotation(R90, 4, "X")}[axis]
        M = Matrix.Translation(T(*c)) @ _rot(yaw, pitch, roll) @ Matrix.Diagonal((scale[0], scale[2], scale[1], 1.0)) @ a
        closed = arc >= 2 * math.pi - 1e-6; n_u = seg if closed else seg + 1
        vs = []
        for i in range(n_u):
            u = arc * i / seg
            for j in range(rseg):
                v = 2 * math.pi * j / rseg
                p = Vector(((R + r * math.cos(v)) * math.cos(u), (R + r * math.cos(v)) * math.sin(u), r * math.sin(v)))
                vs.append(bm.verts.new(M @ p))
        for i in range(seg):
            i2 = (i + 1) % n_u
            for j in range(rseg):
                j2 = (j + 1) % rseg
                bm.faces.new((vs[i * rseg + j], vs[i2 * rseg + j], vs[i2 * rseg + j2], vs[i * rseg + j2]))
        self._finish(vs, m, 0.0, True)
    def quad(self, pts, m, bev=0.0):
        """a single polygon from three-coord points"""
        bm, _ = self._get(bev); vs = [bm.verts.new(T(*p)) for p in pts]; bm.faces.new(vs); self._finish(vs, m, bev)
    def build(self):
        obs = []
        for bev, (bm, mats) in self.parts.items():
            me = bpy.data.meshes.new(f"{self.name}{bev}"); bm.normal_update(); bm.to_mesh(me); bm.free()
            for m in mats: me.materials.append(m)
            o = bpy.data.objects.new(f"{self.name}{bev}", me); bpy.context.scene.collection.objects.link(o)
            if bev:
                md = o.modifiers.new("b", "BEVEL"); md.width = bev; md.segments = 2; md.limit_method = "ANGLE"
                try: md.harden_normals = False
                except Exception: pass
            obs.append(o)
        self.parts = {}
        return obs

# ---------------- reusable props ----------------
def sign(K, c, w, h, face, body, board="#1e3a2a", ink=None, kind="serif", trim=None, depth=0.05, size=None):
    """a painted shop sign: board, frame, gilt (or coloured) lettering; face = yaw (0 faces -z)"""
    yaw = face; K.box(c, (w, h, depth), pm(board, 0.45), yaw, 0.01)
    if trim: _frame(K, c, w, h, face, pm(trim, 0.4, 0.3) if isinstance(trim, str) else trim, 0.035, depth + 0.02)
    off = Vector((-math.sin(yaw), 0, -math.cos(yaw))) * (depth / 2 + 0.004)
    p = Vector(c) + off
    text(body, tuple(p), size or h * 0.62, ink or gold(), yaw, kind, 0.006, fit=w * 0.88)
def _frame(K, c, w, h, face, m, t=0.04, d=0.05):
    cx, cy_, cz = c; ca, sa = math.cos(face), math.sin(face)
    def at(u, v): return (cx + u * ca, cy_ + v, cz - u * sa)
    K.box(at(0, h / 2), (w + t, t, d), m, face, 0.006); K.box(at(0, -h / 2), (w + t, t, d), m, face, 0.006)
    K.box(at(-w / 2, 0), (t, h + t, d), m, face, 0.006); K.box(at(w / 2, 0), (t, h + t, d), m, face, 0.006)
def poster(K, c, w, h, face, bg, lines, ink="#1a1a1a", accent=None, kind="sans", border=None):
    """a pasted bill: coloured paper, a border, an accent band / disc, lines of big readable text"""
    yaw = face; nrm = Vector((-math.sin(yaw), 0, -math.cos(yaw))); ca, sa = math.cos(yaw), math.sin(yaw)
    K.box(c, (w, h, 0.006), paper(bg, 0.35), yaw, 0)
    def at(u, v, d): p = Vector(c) + nrm * d; return (p.x + u * ca, p.y + v, p.z - u * sa)
    if border: _frame(K, at(0, 0, 0.004), w - 0.06, h - 0.06, face, pm(border, 0.8), 0.025, 0.003)
    if accent:
        K.box(at(0, -h * 0.18, 0.005), (w * 0.8, h * 0.22, 0.003), pm(accent, 0.8), yaw, 0)
    n = len(lines); y = h * 0.32
    for i, (s, rel) in enumerate(lines):
        sz = h * rel
        text(s, at(0, y - sz * 0.5, 0.008), sz, pm(ink, 0.7), yaw, kind, 0.002, fit=w * 0.86)
        y -= sz * 1.25
def barrel(K, c, r, h, M_wood, hoop, axis="y", yaw=0.0):
    x, y, z = c
    K.cyl(c, r * 0.92, h, M_wood, 16, axis, None, yaw)
    K.cyl(c, r, h * 0.6, M_wood, 16, axis, None, yaw)
    for dv in (-0.42, -0.2, 0.2, 0.42):
        if axis == "y": cc = (x, y + dv * h, z)
        elif axis == "x":
            cc = (x + dv * h * math.cos(yaw), y, z - dv * h * math.sin(yaw))
        else: cc = (x + dv * h * math.sin(yaw), y, z + dv * h * math.cos(yaw))
        rr = r * (0.94 if abs(dv) > 0.3 else 1.005)
        K.cyl(cc, rr + 0.008, 0.035, hoop, 16, axis, None, yaw)
def crate(K, c, s, m, yaw=0.0, slat=None):
    K.box(c, (s, s * 0.8, s), m, yaw, 0.01)
    sm = slat or m
    for dy in (-0.3, 0.3):
        K.box((c[0], c[1] + dy * s * 0.8, c[2]), (s + 0.02, s * 0.1, s + 0.02), sm, yaw, 0.004)
def stein(K, c, beer, glass_m, foam, handle):
    x, y, z = c
    K.cyl((x, y + 0.095, z), 0.058, 0.19, glass_m, 14)
    K.cyl((x, y + 0.075, z), 0.05, 0.14, beer, 12)
    K.cyl((x, y + 0.17, z), 0.06, 0.05, foam, 12, "y", 0.066)
    K.torus((x + 0.07, y + 0.1, z), 0.045, 0.012, handle, 12, 6, "z")
def pretzel(K, c, m, s=1.0, yaw=0.0):
    x, y, z = c
    K.torus((x, y + 0.02 * s, z), 0.07 * s, 0.018 * s, m, 18, 6, "y", yaw, scale=(1.0, 1.0, 0.85))
    K.torus((x - 0.035 * s, y + 0.025 * s, z + 0.01 * s), 0.035 * s, 0.016 * s, m, 14, 6, "y", yaw)
    K.torus((x + 0.035 * s, y + 0.025 * s, z + 0.01 * s), 0.035 * s, 0.016 * s, m, 14, 6, "y", yaw)
def cash_bundle(K, c, m_note, m_band, yaw=0.0, n=1):
    x, y, z = c
    for i in range(n):
        K.box((x, y + 0.03 + i * 0.062, z), (0.16, 0.06, 0.08), m_note, yaw + random.uniform(-0.15, 0.15), 0.003)
        K.box((x, y + 0.03 + i * 0.062, z), (0.03, 0.064, 0.084), m_band, yaw, 0)
def books(K, x0, x1, y, z, depth, face, rnd, cols=("#7a1e22", "#1e3a5a", "#2a4a2a", "#6a4a1e", "#3a2a4a", "#a8782a")):
    """a row of books along three x (face irrelevant: spines toward -z)"""
    x = x0
    while x < x1 - 0.03:
        w = rnd.uniform(0.03, 0.06); h = rnd.uniform(0.18, 0.28)
        K.box((x + w / 2, y + h / 2, z), (w, h, depth), pm(rnd.choice(cols), 0.6), 0, 0.003); x += w + 0.004
