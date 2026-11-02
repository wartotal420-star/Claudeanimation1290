# Shared kit for the chapter 2-4 sets (c02_* / c03_* / c04_*): batched vehicles (panzer, T-26, Type 89, CV-33
# tankette, lorry, armoured car, airliner, bomber, dive bomber), boats, trees, railway, poles, sandbags, lamps, map
# materials. Everything is written in three.js layout coordinates (y up) and goes through kit_sbpw.Kit (batched
# bmesh), so a set with hundreds of props builds in seconds. Vehicles: local nose +x, placed at (x, y, z) with yaw.
import bpy, bmesh, math, os, random, json
from mathutils import Vector, Matrix
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import Kit, pm, em, wood, cloth, gold, brass, iron, grime, paper, text, sign, poster, set_world, R90, cached
from sets.void import lathe, tube, worn, fire, flame, flame_mat, smoke_mat, smoke_column, mat_once, link, mesh_obj, candle

_Kit = Kit
class FastKit(_Kit):
    """Kit whose bmeshes are rolled over every ~6000 verts: bmesh operators clear flags on the whole mesh, so one huge
    bmesh makes every create_cone / create_cube O(n) (thousands of props -> minutes). Small chunks keep it linear."""
    def __init__(self, name="set", limit=6000):
        super().__init__(name); self.done = []; self.limit = limit
    def _get(self, bev):
        p = self.parts.get(bev)
        if p is not None and len(p[0].verts) > self.limit:
            self.done.append((bev, p)); del self.parts[bev]
        return super()._get(bev)
    def build(self):
        rest = dict(self.parts); obs = []
        for bev, p in self.done:
            self.parts = {bev: p}; obs += _Kit.build(self)
        self.parts = rest; obs += _Kit.build(self); self.done = []
        return obs
    def sphere(self, c, r, m, seg=12, scale=(1, 1, 1), bev=0.0):
        """UV sphere from raw verts (bmesh.ops.create_uvsphere is ~10 ms a call)"""
        bm, _ = self._get(bev); nv = max(4, seg // 2); cx, cy_, cz = T(*c); sx, sy, sz = scale[0], scale[2], scale[1]
        top = bm.verts.new((cx, cy_, cz + r * sz)); bot = bm.verts.new((cx, cy_, cz - r * sz)); rings = []
        for j in range(1, nv):
            ph = math.pi * j / nv; z = math.cos(ph) * r * sz; rr = math.sin(ph) * r
            rings.append([bm.verts.new((cx + rr * sx * math.cos(2 * math.pi * i / seg), cy_ + rr * sy * math.sin(2 * math.pi * i / seg), cz + z)) for i in range(seg)])
        for i in range(seg):
            i2 = (i + 1) % seg
            bm.faces.new((top, rings[0][i], rings[0][i2]))
            bm.faces.new((bot, rings[-1][i2], rings[-1][i]))
            for a, b in zip(rings[:-1], rings[1:]): bm.faces.new((a[i], b[i], b[i2], a[i2]))
        vs = [top, bot] + [v for rg in rings for v in rg]
        self._finish(vs, m, bev, True)
Kit = FastKit

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../blender

def wm(key, col, chip="#3a3a32", rough=0.6, metal=0.25, scale=8, amount=0.7, dirt="#4a3a26"):
    return cached("wm" + key, lambda: worn("c2" + key, col, chip, rough, metal, scale, amount, dirt))

class X:
    """local vehicle frame: nose +x, up +y, left +z; yaw about +y, uniform scale s"""
    def __init__(self, x, y, z, yaw=0.0, s=1.0): self.x, self.y, self.z, self.yaw, self.s = x, y, z, yaw, s; self.c, self.sn = math.cos(yaw), math.sin(yaw)
    def p(self, lx, ly, lz):
        s = self.s; return (self.x + (lx * self.c + lz * self.sn) * s, self.y + ly * s, self.z + (-lx * self.sn + lz * self.c) * s)
    def box(self, K, c, sz, m, bev=0.01, yaw=0.0, pitch=0.0, roll=0.0):
        s = self.s; K.box(self.p(*c), (sz[0] * s, sz[1] * s, sz[2] * s), m, self.yaw + yaw, bev * s, pitch, roll)
    def cyl(self, K, c, r, h, m, seg=16, axis="y", r2=None, bev=0.0, yaw=0.0, pitch=0.0, roll=0.0):
        s = self.s; K.cyl(self.p(*c), r * s, h * s, m, seg, axis, None if r2 is None else r2 * s, self.yaw + yaw, bev * s, pitch, roll)
    def sph(self, K, c, r, m, seg=12, scale=(1, 1, 1)):
        s = self.s; K.sphere(self.p(*c), r * s, m, seg, scale)

def loft(K, rings, m, cap0=True, cap1=True, bev=0.0, smooth=True):
    """skin closed rings (lists of three points, equal length) into one surface"""
    bm, _ = K._get(bev); V = [[bm.verts.new(T(*p)) for p in r] for r in rings]; n = len(rings[0])
    for a, b in zip(V[:-1], V[1:]):
        for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    if cap0: bm.faces.new(list(reversed(V[0])))
    if cap1: bm.faces.new(V[-1])
    vs = [v for r in V for v in r]; K._finish(vs, m, bev, True if smooth else None)

def ring(c, ax, r_y, r_z, n=12, rot=0.0):
    """ellipse of points around centre c in the plane normal to local x (for fuselages / hulls along x)"""
    return [(c[0], c[1] + r_y * math.sin(rot + i / n * math.tau), c[2] + r_z * math.cos(rot + i / n * math.tau)) for i in range(n)]

def star_pts(cx, cy, R, r, n=5, rot=math.pi / 2):
    return [(cx + (R if k % 2 == 0 else r) * math.cos(rot + k * math.pi / n), cy + (R if k % 2 == 0 else r) * math.sin(rot + k * math.pi / n)) for k in range(2 * n)]

def decal_star(K, xf, lx, ly, lz, R, m, side=1):
    """flat 5-point star on a vehicle side (plane normal local z)"""
    pts = star_pts(lx, ly, R, R * 0.4)
    q = [xf.p(px, py, lz) for px, py in pts]
    if side < 0: q = q[::-1]
    K.quad(q, m)

# ------------------------------------------------------------------ tracked vehicles
def tracks(K, xf, L, zc, r, n, hull_m, steel_m, trk_m, h=0.42, y0=0.0):
    for sd in (-1, 1):
        z = sd * zc
        xf.box(K, (0, y0 + r + 0.02, z), (L, 2 * r + 0.12, h), trk_m, 0.12)
        for k in range(n):
            x = -L / 2 + r + 0.15 + k * (L - 2 * r - 0.3) / max(1, n - 1)
            xf.cyl(K, (x, y0 + r, z + sd * (h / 2 + 0.01)), r * 0.92, 0.07, steel_m, 16, "z")
            xf.cyl(K, (x, y0 + r, z + sd * (h / 2 + 0.05)), r * 0.35, 0.04, hull_m, 10, "z")
        xf.cyl(K, (L / 2 - 0.15, y0 + r * 1.35, z + sd * (h / 2 + 0.02)), r * 0.85, 0.09, steel_m, 12, "z")
        for k in range(3): xf.cyl(K, (-L / 3 + k * L / 3, y0 + 2 * r + 0.04, z + sd * (h / 2 - 0.05)), 0.08, 0.09, steel_m, 8, "z")

def panzer(K, x, z, yaw, col="#5b5f5c", num="423", y=0.0, s=1.0, mud=0.75, crew_hatch=True, gun=1.0):
    """Panzer III style medium tank (1939-40): box hull, wide superstructure over the tracks, angled turret with
    cupola, mantlet, short gun, stowage, jerrycans, exhausts, white turret number. No insignia."""
    xf = X(x, y, z, yaw, s)
    H = wm("pz" + col, col, "#2e302c", 0.6, 0.3, 9, mud); TR = wm("pztrk", "#3a352c", "#22201a", 0.85, 0.2, 6, 0.5, "#5a4a32")
    ST = wm("pzst", "#3e403c", "#62625c", 0.45, 0.6, 30, 0.7); WH = pm("#e8e4d6", 0.6); BL = pm("#141414", 0.5)
    tracks(K, xf, 5.4, 1.2, 0.3, 6, H, ST, TR, 0.44)
    xf.box(K, (0, 0.85, 0), (5.0, 0.62, 1.95), H, 0.05)                    # lower hull
    xf.box(K, (-0.25, 1.38, 0), (4.4, 0.5, 2.88), H, 0.04)                 # superstructure over the tracks
    xf.box(K, (2.35, 1.12, 0), (0.75, 0.7, 2.0), H, 0.04, 0, 0, -0.55)     # glacis
    xf.box(K, (2.0, 1.45, 0.55), (0.3, 0.32, 0.9), H, 0.03)                # driver's plate
    xf.box(K, (2.17, 1.48, 0.55), (0.02, 0.07, 0.3), BL, 0)                # vision slit
    xf.cyl(K, (2.16, 1.42, -0.55), 0.11, 0.12, H, 12, "x")                 # hull MG ball
    xf.cyl(K, (2.3, 1.42, -0.55), 0.025, 0.4, ST, 8, "x")
    for sd in (-1, 1):
        xf.box(K, (0.0, 1.13, sd * 1.43), (5.6, 0.04, 0.12), H, 0.01)      # fender lip
        xf.box(K, (2.6, 1.0, sd * 0.9), (0.08, 0.18, 0.18), ST, 0.02)      # tow hook
        xf.cyl(K, (2.45, 1.7, sd * 1.05), 0.09, 0.14, ST, 10, "x")         # headlight
        for k in range(3): xf.box(K, (-1.9 + k * 0.7, 1.68, sd * 1.25), (0.6, 0.1, 0.1), wood("#7a5a34", "#3a2614", 12) if k == 1 else ST, 0.02)
    for k in range(6): xf.box(K, (-1.4 - k * 0.22, 1.65, 0), (0.12, 0.04, 1.6), BL, 0.005)   # engine grille
    xf.box(K, (-2.55, 1.0, 0), (0.12, 0.55, 2.2), H, 0.02)                 # rear plate
    for sd in (-1, 1): xf.cyl(K, (-2.68, 1.05, sd * 0.55), 0.13, 0.75, ST, 14, "z")   # mufflers
    for k in range(3): xf.box(K, (-2.2, 1.85, -0.9 + k * 0.38), (0.3, 0.45, 0.16), wm("jerry", "#4e5340", "#2a2a22", 0.6, 0.3, 20, 0.6), 0.03)
    xf.box(K, (-1.6, 1.82, 0.75), (0.8, 0.35, 0.6), wm("pzbox", "#4e524c", "#2a2a22", 0.6, 0.3, 14, 0.65), 0.03)   # stowage bin
    xf.cyl(K, (-1.55, 1.95, -0.3), 0.16, 1.1, cloth("#6a6248"), 12, "z")   # bedroll
    # turret: angled sides (two stacked boxes), mantlet, gun, cupola, hatches, antenna
    xf.box(K, (-0.1, 1.95, 0), (2.1, 0.5, 1.95), H, 0.05)
    xf.box(K, (-0.15, 2.3, 0), (1.9, 0.25, 1.7), H, 0.05)
    xf.box(K, (1.05, 2.05, 0), (0.3, 0.55, 1.0), H, 0.06)
    xf.cyl(K, (1.2 + 0.9 * gun, 2.08, 0.0), 0.075, 1.9 * gun, ST, 12, "x")
    xf.cyl(K, (1.25, 2.08, 0), 0.14, 0.3, H, 12, "x")
    for sd in (-0.28, 0.28): xf.cyl(K, (1.25, 2.12, sd), 0.035, 0.6, ST, 8, "x")
    xf.cyl(K, (-0.85, 2.55, 0), 0.34, 0.26, H, 18)
    xf.cyl(K, (-0.85, 2.7, 0), 0.32, 0.05, H, 18)
    for sd in (-1, 1): xf.box(K, (0.05, 2.05, sd * 0.99), (0.7, 0.4, 0.04), H, 0.015)   # side hatches
    xf.cyl(K, (-1.0, 3.2, 0.7), 0.012, 1.6, ST, 5, "y")
    for sd in (-1, 1):
        xf.box(K, (-0.95, 2.05, sd * 1.0), (0.55, 0.38, 0.1), wm("pzbox", "#4e524c", "#2a2a22", 0.6, 0.3, 14, 0.65), 0.02)
        text(num, xf.p(0.35, 2.12, sd * 1.0), 0.26 * s, WH, xf.yaw + (math.pi if sd > 0 else 0) - R90 * 0, "sans", 0.002)
    return xf

def fix_side_text(o, xf, sd):
    pass

def t26(K, x, z, yaw, col="#4c5a36", y=0.0, s=1.0, star=True):
    """Soviet T-26 light tank: small hull, round turret, long 45 mm gun, red star on the turret"""
    xf = X(x, y, z, yaw, s)
    H = wm("t26" + col, col, "#2a3020", 0.6, 0.25, 9, 0.72); TR = wm("pztrk", "#3a352c", "#22201a", 0.85, 0.2, 6, 0.5, "#5a4a32")
    ST = wm("pzst", "#3e403c", "#62625c", 0.45, 0.6, 30, 0.7); RED = pm("#c8202a", 0.5)
    tracks(K, xf, 4.6, 1.05, 0.26, 8, H, ST, TR, 0.36)
    xf.box(K, (0, 0.85, 0), (4.4, 0.62, 1.7), H, 0.04)
    xf.box(K, (-0.2, 1.3, 0), (3.6, 0.36, 2.4), H, 0.03)
    xf.box(K, (2.0, 1.0, 0), (0.6, 0.62, 1.7), H, 0.03, 0, 0, -0.7)
    xf.cyl(K, (0.1, 1.82, 0), 0.82, 0.62, H, 24)
    xf.cyl(K, (0.1, 2.15, 0), 0.75, 0.06, H, 24)
    xf.box(K, (0.95, 1.82, 0), (0.25, 0.4, 0.55), H, 0.04)
    xf.cyl(K, (2.1, 1.84, 0), 0.055, 2.3, ST, 10, "x")
    xf.cyl(K, (0.0, 2.2, 0.35), 0.24, 0.08, H, 12)
    for k in range(4): xf.box(K, (-1.3 - k * 0.2, 1.5, 0), (0.1, 0.03, 1.3), pm("#141414", 0.5), 0.005)
    xf.cyl(K, (-2.1, 1.2, 0), 0.12, 1.5, ST, 10, "z")
    for sd in (-1, 1): xf.box(K, (0, 1.12, sd * 1.25), (4.8, 0.04, 0.12), H, 0.01)
    if star:
        for sd in (-1, 1):
            pts = star_pts(0.1, 1.85, 0.26, 0.105, rot=math.pi / 2)
            q = [xf.p(px, py, sd * 0.84) for px, py in pts] + [xf.p(0.1, 1.85, sd * 0.84)]
            bm, _ = K._get(0.0); vs = [bm.verts.new(T(*p)) for p in q]
            for k in range(10):
                f = bm.faces.new((vs[k], vs[(k + 1) % 10], vs[10]) if sd < 0 else (vs[(k + 1) % 10], vs[k], vs[10]))
            K._finish(vs, RED, 0.0)
    return xf

def tankette(K, x, z, yaw, col="#8a7a52", y=0.0, s=1.0):
    """Italian CV-33 tankette: tiny box with a twin MG in the front plate"""
    xf = X(x, y, z, yaw, s)
    H = wm("cv" + col, col, "#4a3e26", 0.6, 0.25, 9, 0.7); TR = wm("pztrk", "#3a352c", "#22201a", 0.85, 0.2, 6, 0.5, "#5a4a32")
    ST = wm("pzst", "#3e403c", "#62625c", 0.45, 0.6, 30, 0.7)
    tracks(K, xf, 3.0, 0.62, 0.2, 5, H, ST, TR, 0.3)
    xf.box(K, (0, 0.62, 0), (2.9, 0.5, 1.15), H, 0.03)
    xf.box(K, (0.3, 1.0, 0), (1.6, 0.35, 1.25), H, 0.03)
    xf.box(K, (1.25, 0.8, 0), (0.5, 0.5, 1.15), H, 0.03, 0, 0, -0.5)
    for sd in (-0.15, 0.15): xf.cyl(K, (1.5, 1.0, sd), 0.03, 0.7, ST, 8, "x")
    xf.box(K, (1.12, 1.06, 0.3), (0.04, 0.06, 0.3), pm("#141414", 0.5), 0)
    xf.box(K, (-1.1, 0.98, 0), (0.6, 0.25, 0.9), H, 0.02)
    return xf

def type89(K, x, z, yaw, y=0.0, s=1.0):
    """Japanese Type 89 medium tank: three-tone camouflage, tall hull, small turret with short gun, tail skid"""
    xf = X(x, y, z, yaw, s)
    H = cached("t89cam", lambda: _camo("t89cam", ["#8a7a4a", "#5a6a3a", "#6a4a2a"], "#d8c890"))
    TR = wm("pztrk", "#3a352c", "#22201a", 0.85, 0.2, 6, 0.5, "#5a4a32"); ST = wm("pzst", "#3e403c", "#62625c", 0.45, 0.6, 30, 0.7)
    tracks(K, xf, 4.3, 1.0, 0.22, 9, H, ST, TR, 0.36)
    xf.box(K, (0, 0.95, 0), (4.0, 0.75, 1.7), H, 0.04)
    xf.box(K, (-0.2, 1.5, 0), (3.0, 0.45, 2.15), H, 0.04)
    xf.box(K, (1.7, 1.25, 0), (0.6, 0.6, 1.7), H, 0.03, 0, 0, -0.5)
    xf.cyl(K, (0.3, 1.98, 0), 0.62, 0.55, H, 8)
    xf.cyl(K, (0.3, 2.35, 0), 0.3, 0.3, H, 8)
    xf.cyl(K, (1.2, 2.0, 0), 0.07, 0.9, ST, 10, "x")
    xf.box(K, (-2.5, 0.9, 0), (1.2, 0.08, 0.8), ST, 0.02, 0, 0, 0.35)
    return xf

def _camo(name, cols, stripe):
    m = lib.principled(name, hexc(cols[0]), 0.65, 0.2); t, n, l = lib.nodes(m)
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.2; nz.inputs["Detail"].default_value = 2
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    r = lib.ramp(n, l, nz.outputs["Fac"], [(0.42, hexc(cols[0])), (0.44, hexc(cols[1])), (0.55, hexc(cols[1])), (0.57, hexc(cols[2]))])
    l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
    return m

# ------------------------------------------------------------------ wheeled vehicles
def wheel(K, xf, c, r, w, tyre, hub):
    xf.cyl(K, c, r, w, tyre, 18, "z", bev=0.03)
    xf.cyl(K, (c[0], c[1], c[2] + (0.01 if c[2] > 0 else -0.01)), r * 0.55, w + 0.02, hub, 12, "z")

def lorry(K, x, z, yaw, col="#5a5e4c", canvas="#6a6450", y=0.0, s=1.0, cover=True):
    """1930s army lorry: long bonnet, open cab with a canvas top, slatted bed with a canvas tilt"""
    xf = X(x, y, z, yaw, s)
    B = wm("lor" + col, col, "#2e2e26", 0.6, 0.25, 9, 0.72); TY = pm("#1a1a1a", 0.8); HB = wm("pzst", "#3e403c", "#62625c", 0.45, 0.6, 30, 0.7)
    CV = cloth(canvas); WD = wood("#6a5434", "#3a2a18", 10)
    xf.box(K, (0, 0.7, 0), (6.0, 0.18, 0.9), HB, 0.02)                     # chassis
    xf.box(K, (2.4, 1.15, 0), (1.3, 0.75, 1.0), B, 0.08)                   # bonnet
    xf.box(K, (3.06, 1.15, 0), (0.06, 0.72, 0.95), HB, 0.01)               # radiator grille
    for k in range(7): xf.box(K, (3.1, 1.15, -0.4 + k * 0.133), (0.02, 0.62, 0.025), B, 0)
    for sd in (-1, 1):
        xf.box(K, (2.3, 0.95, sd * 0.88), (1.7, 0.08, 0.42), B, 0.03, 0, 0, 0.0)   # mudguard
        xf.cyl(K, (2.95, 1.45, sd * 0.62), 0.12, 0.14, HB, 12, "x"); xf.cyl(K, (3.03, 1.45, sd * 0.62), 0.1, 0.02, em("#fff2c8", 0.4), 12, "x")
        wheel(K, xf, (2.2, 0.48, sd * 0.88), 0.48, 0.28, TY, B)
        wheel(K, xf, (-1.4, 0.48, sd * 0.88), 0.48, 0.28, TY, B); wheel(K, xf, (-2.4, 0.48, sd * 0.88), 0.48, 0.28, TY, B)
    xf.box(K, (1.25, 1.35, 0), (1.0, 1.1, 1.9), B, 0.04)                   # cab
    xf.box(K, (1.76, 1.72, 0), (0.03, 0.45, 1.6), pm("#2a3440", 0.08, 0.3), 0)   # windscreen
    xf.box(K, (1.25, 2.0, 0), (1.2, 0.1, 2.0), CV, 0.04)
    xf.box(K, (-1.4, 1.2, 0), (3.6, 0.12, 2.2), WD, 0.01)                  # bed
    for sd in (-1, 1): xf.box(K, (-1.4, 1.55, sd * 1.08), (3.6, 0.6, 0.06), WD, 0.01)
    xf.box(K, (-3.18, 1.55, 0), (0.06, 0.6, 2.2), WD, 0.01)
    if cover:
        xf.box(K, (-1.4, 2.2, 0), (3.7, 1.0, 2.26), CV, 0.06)
        xf.cyl(K, (-1.4, 2.7, 0), 1.13, 3.7, CV, 18, "x", bev=0.02)
    return xf

def armoured_car(K, x, z, yaw, col="#5b5f5c", y=0.0, s=1.0):
    """light four-wheeled armoured car (Sd.Kfz 222 style): faceted hull, open turret with a wire grille, 20 mm gun"""
    xf = X(x, y, z, yaw, s)
    H = wm("pz" + col, col, "#2e302c", 0.6, 0.3, 9, 0.75); TY = pm("#1a1a1a", 0.8); ST = wm("pzst", "#3e403c", "#62625c", 0.45, 0.6, 30, 0.7)
    for sd in (-1, 1):
        for xx in (1.35, -1.35): wheel(K, xf, (xx, 0.48, sd * 0.85), 0.48, 0.3, TY, H)
    xf.box(K, (0, 0.95, 0), (4.6, 0.55, 1.65), H, 0.03)
    xf.box(K, (1.9, 1.15, 0), (1.0, 0.5, 1.6), H, 0.03, 0, 0, -0.45)
    xf.box(K, (-1.9, 1.15, 0), (1.0, 0.5, 1.6), H, 0.03, 0, 0, 0.45)
    xf.box(K, (0, 1.38, 0), (2.6, 0.35, 1.9), H, 0.03)
    for sd in (-1, 1): xf.box(K, (0, 1.38, sd * 0.97), (2.6, 0.35, 0.06), H, 0.02, 0, sd * 0.3, 0)
    xf.cyl(K, (0.0, 1.8, 0), 0.75, 0.5, H, 10)
    for k in range(5): xf.box(K, (-0.6 + k * 0.3, 2.12, 0), (0.02, 0.18, 1.4), ST, 0)
    xf.cyl(K, (0.9, 1.85, 0), 0.04, 1.3, ST, 8, "x")
    for sd in (-1, 1): xf.box(K, (0, 0.95, sd * 0.98), (4.0, 0.06, 0.25), H, 0.01)
    xf.box(K, (2.25, 1.3, 0.5), (0.02, 0.06, 0.3), pm("#141414", 0.5), 0)
    return xf

# ------------------------------------------------------------------ aircraft
def airliner(K, x, y, z, yaw, s=1.0, reg="G-AFGN", line="BRITISH AIRWAYS", body="#c8ccd0", stripe="#1e3a6a", door_open=True):
    """twin-engined Lockheed 14 style airliner on its wheels (tail-down stance), oval windows, twin fins"""
    xf = X(x, y, z, yaw, s)
    AL = pm(body, 0.3, 0.75); ST = pm(stripe, 0.4); DK = pm("#22262c", 0.15, 0.4); TY = pm("#1a1a1a", 0.8); WIN = pm("#1e2834", 0.06, 0.4)
    pitch = 0.11   # nose up on the tailwheel
    def P(lx, ly, lz):
        c, s_ = math.cos(pitch), math.sin(pitch); return (lx * c - (ly - 2.0) * s_, 2.0 + lx * s_ + (ly - 2.0) * c, lz)
    rad = [(-7.0, 0.1), (-6.0, 0.35), (-4.5, 0.75), (-2.5, 1.05), (0.0, 1.15), (2.5, 1.12), (4.0, 0.95), (5.0, 0.62), (5.5, 0.28)]
    rings = []
    for lx, r in rad:
        rings.append([xf.p(*P(lx, 2.0 + r * 0.9 * math.sin(a) + (0.12 if lx < -3 else 0) * (lx + 3) * -0.12, r * math.cos(a))) for a in [i / 14 * math.tau for i in range(14)]])
    loft(K, rings, AL)
    # windows, stripe, door
    for k in range(7):
        for sd in (-1, 1): xf.box(K, P(-2.6 + k * 0.62, 2.3, sd * 1.12), (0.32, 0.26, 0.04), WIN, 0.03, 0, sd * 0.25)
    for sd in (-1, 1): xf.box(K, P(-0.6, 1.95, sd * 1.15), (8.5, 0.1, 0.03), ST, 0.0, 0, sd * 0.1)
    for sd in (-1, 1): xf.box(K, P(4.25, 2.55, sd * 0.8), (0.6, 0.3, 0.05), WIN, 0.03, 0, sd * 0.5)   # cockpit glazing
    if door_open: xf.box(K, P(-3.5, 2.0, 1.14), (0.75, 1.3, 0.05), DK, 0.02)
    # wings, engines, props
    wl = [P(1.8, 1.55, 0.0), P(-0.6, 1.55, 0.0)]
    for sd in (-1, 1):
        q = [xf.p(*P(1.8, 1.55, sd * 1.0)), xf.p(*P(-0.6, 1.55, sd * 1.0)), xf.p(*P(-0.2, 1.75, sd * 8.0)), xf.p(*P(0.9, 1.75, sd * 8.0))]
        top = [xf.p(*P(1.8, 1.75, sd * 1.0)), xf.p(*P(-0.6, 1.72, sd * 1.0)), xf.p(*P(-0.2, 1.82, sd * 8.0)), xf.p(*P(0.9, 1.84, sd * 8.0))]
        bm, _ = K._get(0.0); vb = [bm.verts.new(T(*p)) for p in q]; vt = [bm.verts.new(T(*p)) for p in top]
        for i in range(4): bm.faces.new((vb[i], vb[(i + 1) % 4], vt[(i + 1) % 4], vt[i]))
        bm.faces.new(vb[::-1]); bm.faces.new(vt); K._finish(vb + vt, AL, 0.0)
        ez = sd * 2.6
        loft(K, [[xf.p(*q) for q in ring(P(*c_), 0, ry, ry, 12)] for c_, ry in (((-1.4, 1.62, ez), 0.22), ((1.6, 1.65, ez), 0.42), ((2.3, 1.68, ez), 0.45))], AL)
        xf.cyl(K, P(2.38, 1.68, ez), 0.18, 0.2, DK, 12, "x")
        for k in range(3):
            a = k * math.tau / 3 + 0.3
            xf.box(K, P(2.5, 1.68 + 0.6 * math.sin(a), ez + 0.6 * math.cos(a)), (0.03, 1.2, 0.14), DK, 0.01, 0, 0, 0)
        xf.cyl(K, P(1.2, 0.8, ez), 0.06, 1.4, pm("#6a6e72", 0.3, 0.8), 8)
        wheel(K, xf, P(1.2, 0.45, ez), 0.45, 0.25, TY, AL)
    # tail: stabiliser + twin fins
    xf.box(K, P(-6.4, 2.25, 0), (1.1, 0.08, 5.0), AL, 0.02)
    for sd in (-1, 1): xf.box(K, P(-6.6, 2.85, sd * 2.45), (1.0, 1.25, 0.08), AL, 0.02)
    xf.cyl(K, P(-6.6, 1.5, 0), 0.03, 0.8, pm("#6a6e72", 0.3, 0.8), 8); wheel(K, xf, P(-6.6, 1.1, 0), 0.16, 0.1, TY, AL)
    for sd in (-1, 1):
        o = text(reg, xf.p(*P(-4.6, 2.3, sd * 1.0)), 0.36 * s, pm("#1a1e2a", 0.5), xf.yaw + (R90 if sd < 0 else -R90), "sans", 0.003)
        o2 = text(line, xf.p(*P(-0.8, 2.72, sd * 1.06)), 0.2 * s, pm(stripe, 0.4), xf.yaw + (R90 if sd < 0 else -R90), "sans", 0.003)
    return xf

def bomber(K, x, y, z, yaw, s=1.0, col="#3a3e2c", under="#141414", bank=0.0):
    """twin-engined Whitley style night bomber in flight: slab-sided fuselage, high thick wing, twin fins"""
    xf = X(x, y, z, yaw, s)
    B = wm("bomb" + col, col, "#1e2018", 0.6, 0.2, 6, 0.8, "#2a2a22"); U = pm(under, 0.6); G = pm("#2a3440", 0.1, 0.4)
    rings = [[xf.p(lx, r * math.sin(a), r * 1.0 * math.cos(a)) for a in [i / 12 * math.tau for i in range(12)]] for lx, r in ((-9, 0.15), (-6, 0.7), (-1, 1.0), (3, 0.95), (5.5, 0.6), (6.5, 0.2))]
    loft(K, rings, B)
    for sd in (-1, 1):
        q = [xf.p(1.5, 0.5, sd * 0.8), xf.p(-1.5, 0.5, sd * 0.8), xf.p(-0.5, 0.7, sd * 12.0), xf.p(0.8, 0.7, sd * 12.0)]
        top = [xf.p(1.5, 0.85, sd * 0.8), xf.p(-1.5, 0.85, sd * 0.8), xf.p(-0.5, 0.82, sd * 12.0), xf.p(0.8, 0.84, sd * 12.0)]
        bm, _ = K._get(0.0); vb = [bm.verts.new(T(*p)) for p in q]; vt = [bm.verts.new(T(*p)) for p in top]
        for i in range(4): bm.faces.new((vb[i], vb[(i + 1) % 4], vt[(i + 1) % 4], vt[i]))
        bm.faces.new(vb[::-1]); bm.faces.new(vt); K._finish(vb + vt, B, 0.0)
        loft(K, [[xf.p(*q) for q in ring(c_, 0, ry, ry, 12)] for c_, ry in (((-2.0, 0.5, sd * 3.6), 0.3), ((2.0, 0.55, sd * 3.6), 0.55), ((2.6, 0.55, sd * 3.6), 0.5))], B)
        xf.cyl(K, (2.7, 0.55, sd * 3.6), 1.4, 0.03, pm("#2a2a2a", 0.5), 24, "x")    # prop disc
        xf.box(K, (-8.4, 1.3, sd * 2.0), (1.4, 1.6, 0.1), B, 0.02)
    xf.box(K, (-8.5, 0.5, 0), (1.4, 0.1, 4.4), B, 0.02)
    xf.box(K, (5.0, 0.6, 0), (0.8, 0.5, 0.9), G, 0.1)
    xf.cyl(K, (-9.2, 0.0, 0), 0.4, 0.6, G, 12, "x")
    return xf

def stuka(K, x, y, z, yaw, s=1.0, pitch=0.0):
    """Ju 87 style dive bomber: gull wing, fixed spatted gear, long glazed canopy; plain grey-green (no insignia)"""
    xf = X(x, y, z, yaw, s); B = wm("stuka", "#4a5444", "#2a2e26", 0.55, 0.25, 7, 0.8); G = pm("#2a3440", 0.1, 0.4); U = pm("#8aa0b4", 0.5)
    rings = [[xf.p(lx, r * math.sin(a), r * 0.85 * math.cos(a)) for a in [i / 12 * math.tau for i in range(12)]] for lx, r in ((-5.5, 0.1), (-3, 0.45), (0, 0.7), (2.5, 0.72), (3.6, 0.55), (4.0, 0.25))]
    loft(K, rings, B)
    for sd in (-1, 1):
        q = [(1.2, -0.3, sd * 0.5), (-0.6, -0.3, sd * 0.5), (-0.4, -0.55, sd * 2.4), (1.0, -0.55, sd * 2.4), (0.9, 0.0, sd * 6.8), (-0.1, 0.0, sd * 6.8)]
        for a, b, c, d in ((0, 1, 2, 3), (3, 2, 5, 4)):
            K.quad([xf.p(*q[a]), xf.p(*q[b]), xf.p(*q[c]), xf.p(*q[d])], B)
        xf.cyl(K, (0.9, -1.2, sd * 1.6), 0.07, 1.4, B, 8)
        xf.sph(K, (0.9, -1.85, sd * 1.6), 0.35, B, 12, (1.6, 1.0, 0.6))
        xf.box(K, (-4.9, 0.9, 0), (0.9, 1.3, 0.08), B, 0.02)
    xf.box(K, (-4.9, 0.1, 0), (0.9, 0.06, 3.0), B, 0.02)
    xf.box(K, (0.6, 0.75, 0), (2.6, 0.45, 0.7), G, 0.15)
    xf.cyl(K, (4.1, 0.0, 0), 1.2, 0.03, pm("#2a2a2a", 0.5), 24, "x")
    return xf

# ------------------------------------------------------------------ boats
def hull_rings(L, B, D, n=12, bow=0.0, flat=0.6):
    """hull cross-sections along local x (-L/2 stern .. +L/2 bow): rounded-V sections, sheer rising to the bow"""
    out = []
    for k in range(n + 1):
        u = k / n; lx = -L / 2 + u * L
        w = B / 2 * (math.sin(math.pi * min(1.0, 0.18 + u * 0.95)) ** 0.6) * (1 if u < 0.6 else (1 - ((u - 0.6) / 0.4) ** 1.6) * 0.98 + 0.02)
        if u < 0.08: w = max(w, B / 2 * 0.8)
        sheer = D + 0.25 * D * ((u - 0.4) ** 2) * 4 * (1 if u > 0.4 else 0.4)
        keel = -D * 0.15 * (1 - abs(u - 0.5))
        pts = []
        for j in range(10):
            a = j / 9
            if a <= 0.5:   # starboard: deck edge -> keel
                t = a / 0.5; pts.append((lx, sheer - (sheer - keel) * t ** flat, -w * math.cos(t * math.pi / 2) ** 0.7))
            else:
                t = (a - 0.5) / 0.5; pts.append((lx, keel + (sheer - keel) * t ** (1 / flat) if False else keel + (sheer - keel) * (t ** (1 / max(flat, 0.3))), w * math.sin(t * math.pi / 2) ** 0.7))
        out.append(pts)
    return out

def boat(K, x, z, yaw, kind="fishing", s=1.0, y=0.0, col=None, name="NELLIE"):
    """little ships of Dunkirk: fishing smack, motor yacht, paddle steamer, Thames barge, destroyer"""
    xf = X(x, y, z, yaw, s); rnd = random.Random(hash((kind, round(x), round(z))) & 0xffff)
    spec = {"fishing": (9, 3.0, 1.4, "#2a4a6a"), "yacht": (11, 2.8, 1.2, "#f2ece0"), "paddle": (26, 4.5, 1.8, "#1e1e22"),
            "barge": (16, 4.2, 1.3, "#3a2a1e"), "destroyer": (60, 6.5, 2.6, "#7a8088"), "launch": (7, 2.2, 0.9, "#8a2a22")}[kind]
    L, Bm, D, hc = spec; hc = col or hc
    HM = pm(hc, 0.45, 0.1); DK = wood("#b89a6a", "#7a5a34", 8); WH = pm("#f0ece0", 0.5); BL = pm("#1a1a1e", 0.5); RD = pm("#8a2a22", 0.6)
    rings = [[xf.p(*p) for p in r] for r in hull_rings(L, Bm, D, 14, flat=0.5 if kind != "destroyer" else 0.8)]
    loft(K, rings, HM)
    xf.box(K, (0, D * 0.95, 0), (L * 0.92, 0.06, Bm * 0.86), DK, 0.0)
    if kind == "fishing":
        xf.box(K, (-1.0, D + 0.9, 0), (2.2, 1.6, 1.9), WH, 0.04); xf.box(K, (-1.0, D + 1.75, 0), (2.4, 0.1, 2.1), RD, 0.02)
        for k in range(3): xf.box(K, (-0.0, D + 1.3, (k - 1) * 0.6), (0.04, 0.4, 0.4), BL, 0.02)
        xf.cyl(K, (1.6, D + 3.0, 0), 0.07, 5.0, wood("#7a5a34", "#3a2614", 10), 8)
        xf.box(K, (2.6, D + 2.6, 0), (1.8, 2.8, 0.04), cloth("#a84a2a"), 0.02, 0, 0, 0.2)
        text(name, xf.p(L * 0.3, D * 0.6, Bm * 0.47), 0.32 * s, WH, xf.yaw + math.pi, "sans", 0.003)
    elif kind == "yacht":
        xf.box(K, (0.0, D + 0.6, 0), (4.5, 1.0, 2.0), WH, 0.08)
        for k in range(5): xf.box(K, (-1.6 + k * 0.8, D + 0.75, 1.01), (0.4, 0.3, 0.03), BL, 0.03)
        xf.box(K, (1.6, D + 1.3, 0), (1.4, 0.5, 1.8), pm("#2a3440", 0.08, 0.3), 0.05)
        xf.cyl(K, (-0.5, D + 3.5, 0), 0.06, 5.5, WH, 8)
        xf.box(K, (-4.6, D + 0.5, 0), (0.06, 1.0, 0.06), WH, 0)
        xf.box(K, (-4.6, D + 0.85, -0.3), (0.02, 0.4, 0.6), pm("#c8202a", 0.6), 0)
        text(name, xf.p(-L * 0.48, D * 0.6, 0), 0.25 * s, pm("#2a3a6a", 0.5), xf.yaw + R90, "serif", 0.003)
    elif kind == "paddle":
        xf.box(K, (0, D + 0.8, 0), (L * 0.6, 1.6, Bm * 0.9), WH, 0.04)
        for k in range(10):
            for sd in (-1, 1): xf.box(K, (-L * 0.27 + k * L * 0.06, D + 1.0, sd * Bm * 0.45), (0.5, 0.45, 0.03), BL, 0.04)
        xf.box(K, (0, D + 1.7, 0), (L * 0.65, 0.08, Bm * 1.0), WH, 0.02)
        for sd in (-1, 1):
            xf.cyl(K, (0, D + 0.5, sd * (Bm / 2 + 0.4)), 2.0, 0.9, RD, 24, "z", bev=0.03)
            text(name, xf.p(0, D + 1.0, sd * (Bm / 2 + 0.86)), 0.38 * s, gold(), xf.yaw + (0 if sd < 0 else math.pi), "serif", 0.003)
        for k, xx in enumerate((-2.0, 3.0)):
            xf.cyl(K, (xx, D + 3.5, 0), 0.55, 3.6, pm("#1a1a1a", 0.5), 16, bev=0.02)
            xf.cyl(K, (xx, D + 4.4, 0), 0.58, 0.6, pm("#d8c070", 0.5), 16)
        xf.box(K, (6.0, D + 2.6, 0), (1.6, 1.4, 2.4), WH, 0.03)
    elif kind == "barge":
        xf.box(K, (0, D + 0.25, 0), (L * 0.7, 0.5, Bm * 0.8), pm("#4a3a2a", 0.8), 0.04)
        xf.cyl(K, (1.0, D + 5.5, 0), 0.12, 11.0, wood("#7a5a34", "#3a2614", 10), 8)
        q = [xf.p(1.2, D + 1.3, 0), xf.p(6.5, D + 1.3, 0), xf.p(1.2, D + 10.5, 0)]
        K.quad(q, cloth("#8a3a1e")); K.quad(q[::-1], cloth("#8a3a1e"))
        q = [xf.p(0.8, D + 1.5, 0), xf.p(-6.2, D + 1.5, 0), xf.p(-5.0, D + 9.0, 0), xf.p(0.8, D + 10.0, 0)]
        K.quad(q, cloth("#9a4a24")); K.quad(q[::-1], cloth("#9a4a24"))
    elif kind == "launch":
        xf.box(K, (-0.5, D + 0.45, 0), (2.0, 0.7, 1.5), WH, 0.05)
        xf.box(K, (0.4, D + 0.6, 0), (0.05, 0.4, 1.3), pm("#2a3440", 0.08, 0.3), 0)
    elif kind == "destroyer":
        GR = pm("#8a9098", 0.5, 0.2); DG = pm("#5a6068", 0.5, 0.2)
        xf.box(K, (8, D + 1.2, 0), (14, 2.0, Bm * 0.7), GR, 0.05)
        xf.box(K, (12, D + 3.0, 0), (5, 2.2, 4.0), GR, 0.05)
        xf.box(K, (12.5, D + 4.3, 0), (3.5, 0.6, 4.4), DG, 0.03)
        for k in range(6): xf.box(K, (14.27, D + 3.6, -1.6 + k * 0.64), (0.04, 0.4, 0.4), BL, 0.02)
        for xx in (2.0, -3.5):
            xf.cyl(K, (xx, D + 3.6, 0), 0.9, 4.4, GR, 16, bev=0.04); xf.cyl(K, (xx, D + 5.9, 0), 0.95, 0.4, BL, 16)
        for xx, yy in ((22.0, D + 0.6), (17.5, D + 2.6), (-16.0, D + 0.6), (-21.0, D + 0.6)):
            xf.box(K, (xx, yy + 0.5, 0), (3.0, 1.2, 2.6), GR, 0.15); xf.cyl(K, (xx + 3.0, yy + 0.6, 0), 0.12, 4.0, DG, 10, "x")
        xf.cyl(K, (10.5, D + 9.0, 0), 0.15, 12.0, DG, 8)
        xf.box(K, (10.5, D + 13.0, 0), (0.1, 0.1, 5.0), DG, 0)
        for k in range(9):
            for sd in (-1, 1): xf.cyl(K, (-25 + k * 6, D + 0.9, sd * Bm * 0.43), 0.03, 0.9, GR, 6)
        xf.box(K, (-2, D + 0.8, 0), (50, 0.04, Bm * 0.9), pm("#9aa0a8", 0.6), 0)
        text("H 49", xf.p(L * 0.38, D * 0.7, Bm * 0.5), 1.2 * s, WH, xf.yaw + math.pi, "sans", 0.003)
        text("H 49", xf.p(L * 0.38, D * 0.7, -Bm * 0.5), 1.2 * s, WH, xf.yaw, "sans", 0.003)
    return xf

# ------------------------------------------------------------------ plants, land props
def pine(K, x, z, h, needle, bark, y=0.0, rnd=None, snow=None):
    r = (rnd or random).uniform
    K.cyl((x, y + h * 0.3, z), h * 0.022, h * 0.6, bark, 8)
    n = 6
    for k in range(n):
        f = k / n; rr = h * (0.32 - 0.26 * f) * r(0.85, 1.15); yy = y + h * (0.22 + 0.72 * f)
        K.cyl((x, yy, z), rr, h * 0.26, needle, 9, "y", rr * 0.08, yaw=r(0, 6.28))
        if snow and k % 2 == 0: K.cyl((x, yy + h * 0.06, z), rr * 0.7, h * 0.06, snow, 9, "y", rr * 0.2, yaw=r(0, 6.28))

def broadleaf(K, x, z, h, leaf, bark, y=0.0, rnd=None, w=1.0, n=7):
    rnd = rnd or random
    K.cyl((x, y + h * 0.25, z), h * 0.035 * w, h * 0.5, bark, 8, "y", h * 0.022 * w)
    for k in range(n):
        a = rnd.uniform(0, math.tau); d = rnd.uniform(0, h * 0.2 * w)
        K.sphere((x + d * math.cos(a), y + h * rnd.uniform(0.55, 0.85), z + d * math.sin(a)), h * rnd.uniform(0.16, 0.24) * w, leaf, 10, (1, 0.8, 1))

def birch(K, x, z, h, leaf, y=0.0, rnd=None):
    rnd = rnd or random; bark = cached("birchbark", lambda: _birch_bark())
    K.cyl((x, y + h * 0.42, z), h * 0.018, h * 0.84, bark, 8, "y", h * 0.01, roll=rnd.uniform(-0.05, 0.05))
    for k in range(5): K.sphere((x + rnd.uniform(-0.6, 0.6), y + h * rnd.uniform(0.6, 0.95), z + rnd.uniform(-0.6, 0.6)), h * rnd.uniform(0.1, 0.16), leaf, 9, (1, 1.3, 1))

def _birch_bark():
    m = lib.principled("c2birch", hexc("#e8e4da"), 0.7); t, n, l = lib.nodes(m)
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (6, 6, 30); l.new(tc.outputs["Object"], mp.inputs[0]); l.new(mp.outputs[0], nz.inputs["Vector"])
    r = lib.ramp(n, l, nz.outputs["Fac"], [(0.58, hexc("#ece8dc")), (0.62, hexc("#2a2420"))]); l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
    return m

def acacia(K, x, z, h, leaf, bark, y=0.0, rnd=None):
    rnd = rnd or random
    K.cyl((x, y + h * 0.3, z), h * 0.03, h * 0.6, bark, 8, "y", h * 0.02, roll=rnd.uniform(-0.15, 0.15))
    for k in range(3):
        a = k * 2.1 + rnd.uniform(0, 0.5); d = h * 0.25
        K.cyl((x + d * 0.5 * math.cos(a), y + h * 0.72, z + d * 0.5 * math.sin(a)), h * 0.015, h * 0.35, bark, 6, "y", None, 0, -0.5 * math.sin(a), 0.5 * math.cos(a))
        K.sphere((x + d * math.cos(a), y + h * 0.9, z + d * math.sin(a)), h * 0.3, leaf, 12, (1.0, 0.25, 1.0))
    K.sphere((x, y + h * 0.95, z), h * 0.36, leaf, 12, (1.0, 0.22, 1.0))

def rails(K, x0, z0, x1, z1, y=0.0, gauge=1.435, sleeper=None, rail=None, ballast=None, step=0.65):
    L = math.hypot(x1 - x0, z1 - z0); yaw = math.atan2(-(z1 - z0), x1 - x0); ux, uz = (x1 - x0) / L, (z1 - z0) / L; nx, nz = -uz, ux
    sleeper = sleeper or wood("#4a3826", "#2a1e14", 6, 0.9); rail = rail or pm("#7a7470", 0.3, 0.9); ballast = ballast or grime("c2ballast", "#6a645c", 0.5, 12.0)
    K.box(((x0 + x1) / 2, y + 0.12, (z0 + z1) / 2), (L, 0.24, 3.2), ballast, yaw, 0.1)
    n = int(L / step)
    for k in range(n):
        t = (k + 0.5) / n; K.box((x0 + (x1 - x0) * t, y + 0.27, z0 + (z1 - z0) * t), (0.24, 0.12, 2.5), sleeper, yaw, 0.01)
    for sd in (-1, 1):
        K.box(((x0 + x1) / 2 + nx * sd * gauge / 2, y + 0.4, (z0 + z1) / 2 + nz * sd * gauge / 2), (L, 0.14, 0.07), rail, yaw, 0.01)

def telegraph(K, x, z, h=6.5, y=0.0, yaw=0.0, mat=None):
    mat = mat or wood("#5a4630", "#2e2216", 4, 0.85)
    K.cyl((x, y + h / 2, z), 0.11, h, mat, 8)
    for k in range(2):
        K.box((x, y + h - 0.3 - k * 0.5, z), (0.1, 0.1, 1.6), mat, yaw, 0.01)
        for d in (-0.65, -0.25, 0.25, 0.65): K.cyl((x + d * math.sin(yaw), y + h - 0.2 - k * 0.5, z + d * math.cos(yaw)), 0.04, 0.12, pm("#d8e0d0", 0.2), 8)

def sandbags(K, c, yaw, n, rows, m, rnd=None):
    rnd = rnd or random; cw, sw = math.cos(yaw), math.sin(yaw)
    for r in range(rows):
        for k in range(n - (r % 2)):
            lx = (k - (n - 1) / 2 + (0.5 if r % 2 else 0)) * 0.6
            K.box((c[0] + lx * cw, c[1] + 0.11 + r * 0.2, c[2] - lx * sw), (0.58, 0.22, 0.34), m, yaw + rnd.uniform(-0.1, 0.1), 0.08, rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04))

def sack_mat(): return cached("c2sack", lambda: lib.cloth("c2sack", "#9a8a62"))

def hanging_lamp(K, c, energy=60, col=(1.0, 0.72, 0.42), shade="#2e4a3a", cord=1.2):
    x, y, z = c
    K.cyl((x, y + cord / 2 + 0.12, z), 0.008, cord, pm("#1a1a1a", 0.5), 6)
    K.cyl((x, y + 0.08, z), 0.2, 0.16, pm(shade, 0.35, 0.5), 20, "y", 0.05)
    K.sphere((x, y - 0.02, z), 0.05, em("#fff0c8", 25.0), 10)
    return lib.light("POINT", T(x, y - 0.08, z), energy, col, 0.06)

def lantern(K, c, energy=20, col=(1.0, 0.62, 0.3)):
    x, y, z = c
    K.box((x, y + 0.14, z), (0.16, 0.22, 0.16), pm("#2a2a2a", 0.5, 0.6), 0, 0.005)
    K.cyl((x, y + 0.14, z), 0.06, 0.18, em("#ffcf80", 12.0), 10)
    K.torus((x, y + 0.31, z), 0.05, 0.008, pm("#2a2a2a", 0.5, 0.6), 12, 6, "z")
    L = lib.light("POINT", T(x, y + 0.16, z), energy, col, 0.05); L.visible_camera = False if hasattr(L, "visible_camera") else None
    return L

def img_file_mat(name, fname, rough=0.55, emit=0.0):
    m = bpy.data.materials.new(name); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    it = n.new("ShaderNodeTexImage"); it.name = "img"; it.image = bpy.data.images.load(os.path.join(HERE, "maps", fname), check_existing=True); it.interpolation = "Cubic"
    l.new(it.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    if emit: l.new(it.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit
    return m

def quad_uv(name, pts, m, uvs=((0, 0), (1, 0), (1, 1), (0, 1))):
    me = bpy.data.meshes.new(name); me.from_pydata([T(*p) for p in pts], [], [(0, 1, 2, 3)]); uv = me.uv_layers.new()
    for k, c in enumerate(uvs): uv.data[k].uv = c
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); me.materials.append(m); return o

def ground_mat(name, a, b2, scale=0.4, rough=0.95, bumpk=0.4):
    def mk():
        m = lib.principled(name, hexc(a), rough); t, n, l = lib.nodes(m)
        tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 8
        l.new(tc.outputs["Object"], nz.inputs["Vector"])
        n2 = n.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = scale * 30; l.new(tc.outputs["Object"], n2.inputs["Vector"])
        mx = n.new("ShaderNodeMix"); mx.data_type = "FLOAT"; mx.inputs[0].default_value = 0.3; l.new(nz.outputs["Fac"], mx.inputs[2]); l.new(n2.outputs["Fac"], mx.inputs[3])
        r = lib.ramp(n, l, mx.outputs[0], [(0.35, hexc(b2)), (0.65, hexc(a))]); l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
        lib.bump(n, l, n2.outputs["Fac"], bumpk, 0.05)
        return m
    return cached(name, mk)

def terrain(name, x0, x1, z0, z1, nx, nz, hfn, m):
    """height-field grid (three coords) with hfn(x, z) -> y"""
    vs = []; fs = []
    for j in range(nz + 1):
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx; z = z0 + (z1 - z0) * j / nz; vs.append((x, hfn(x, z), z))
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i; fs.append((a, a + 1, a + nx + 2, a + nx + 1))
    o = mesh_obj(name, vs, fs, m, smooth=True); return o

def grass_patch(K, x0, x1, z0, z1, n, mats, rnd, h=(0.25, 0.6), y=0.0, hfn=None):
    """tufts of blades as thin crossed quads (cheap)"""
    for k in range(n):
        x = rnd.uniform(x0, x1); z = rnd.uniform(z0, z1); yy = hfn(x, z) if hfn else y; m = mats[k % len(mats)]
        for j in range(3):
            a = rnd.uniform(0, math.pi); hh = rnd.uniform(*h); w = 0.05; lean = rnd.uniform(-0.15, 0.15)
            K.quad([(x - w * math.cos(a), yy, z - w * math.sin(a)), (x + w * math.cos(a), yy, z + w * math.sin(a)), (x + lean, yy + hh, z + lean * 0.5)] , m)

def rock(K, c, r, m, rnd):
    K.sphere(c, r, m, 8, (rnd.uniform(0.8, 1.3), rnd.uniform(0.5, 0.8), rnd.uniform(0.8, 1.2)))

def flagpole(K, base, h, cloth_m, w, hgt, pole_m=None, yaw=0.0, wave=0.12):
    """pole + waving flag mesh (via ikit.flag)"""
    from sets import ikit as IK
    pole_m = pole_m or pm("#d8d4c8", 0.4, 0.5)
    K.cyl((base[0], base[1] + h / 2, base[2]), 0.04, h, pole_m, 8); K.sphere((base[0], base[1] + h + 0.05, base[2]), 0.07, gold(), 8)
    return IK.flag("flag", (base[0] - 0.04 * math.cos(yaw), base[1] + h - 0.05, base[2]), w, hgt, cloth_m, yaw, wave, 2.0)
