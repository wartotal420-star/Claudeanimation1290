# The Western Desert (chapter 9: El Alamein barrage at night, Rommel's tanks under fire, "squeezed", the Axis surrender
# in Tunisia by day). Light follows the shot: night (D["night"]) = moon + the barrage (gun flashes pulse per frame in
# update(), in step with the muzzle fx cards from ch09.ts: flashOn(i, f)), otherwise low golden desert sun.
# Layout (three, y up): sand everywhere, flat (y 0) for |x| < 40, z -8..30 and around the day camp; dunes rise beyond.
#   gun line: 25-pounders at x = GUNS[i] (every 6 m, -54..54), z 10 (front row) and x + 3, z 17 (second row), muzzles +z;
#             sandbag pits round each; crews stand at x - 1.2..+1.5, z 8.5..9.5 (behind the shields, camera side).
#   Rommel's tanks: Panzers at (6, 62) (-4, 70) (16, 74) (-14, 80) (26, 84) facing -z; Rommel's tank T0 = (6, 0, 62),
#             cupola top ~(6.75, 2.6, 62) local-turret, shell bursts are fx.
#   day camp (Tunisia, May 1943) round (70, 0, 0): wrecked Panzer (64, -6) burnt, lorry (78, 6), a road sign, wire,
#             the surrender line stands at x 64..76, z 2..4; the "squeeze" at (70, 0, -3).
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, smoke_mat, smoke_column, text
from sets import c09_kit as K

bx, cy = K.bx, K.cy
GUNS = [-54 + 6 * i for i in range(19)]
TANKS = [(6, 62, 0.15), (-4, 70, -0.1), (16, 74, 0.25), (-14, 80, 0.0), (26, 84, 0.3), (-26, 90, -0.2)]
def flash_on(i, f): return ((f * 7 + i * 13) % 23) < 6
def _out(x, z, x0, x1, z0, z1): return math.hypot(max(0.0, x0 - x, x - x1), max(0.0, z0 - z, z - z1))
def H(x, z):
    d = min(_out(x, z, -50, 45, -15, 95), _out(x, z, 50, 92, -18, 20))
    dunes = 2.6 * (0.5 + 0.5 * math.sin(x * 0.07 + 1.6 * noise.noise(Vector((x * 0.02, z * 0.02, 0.5))))) + 1.5 * noise.noise(Vector((x * 0.03, z * 0.03, 2.2)))
    return 0.1 * noise.noise(Vector((x * 0.15, z * 0.15, 0.9))) + K.sm(0, 22, d) * max(0.0, dunes + 1.0)

def build(M, D):
    rnd = random.Random(1942); night = bool(D.get("night"))
    if night: K.sky("#060a1c", "#1a1a34", 0.35, "#03050f", "#2a1e30")
    else: K.sky("#5a8ac8", "#f0c890", 1.0, "#3a6ab8", "#f2d0a0")
    sand = K.sand_ground("c9sand", "#8a6a44")
    def tracks(x, z):
        v = 0.0
        for tx, tz, _ in TANKS:
            for sd in (-1.25, 1.25):
                if abs(x - (tx + sd)) < 0.4 and z > tz: v = max(v, 0.7)
        return v
    K.heightfield("ground", H, -110, 150, -40, 200, 0.8, sand, tracks)
    # sand ripples / tufts of camel thorn scattered on the flats
    thorn = K.mat_once("c9thorn", lambda: lib.principled("c9thorn", lib.hexc("#6a5a34"), 0.9))
    for k in range(140):
        x_, z_ = rnd.uniform(-60, 110), rnd.uniform(-20, 60)
        if abs(z_ - 10) < 3 or abs(z_ - 17) < 3: continue
        K.blob3(f"thorn{k}", (x_, H(x_, z_), z_), (rnd.uniform(0.25, 0.6), rnd.uniform(0.15, 0.35), rnd.uniform(0.25, 0.6)), thorn, 0.12, k)
    stone = K.mat_once("c9stone", lambda: worn("c9stone", "#9a8060", "#6a5440", 0.85, 0.0, 2, 0.55, "#7a6448"))
    for k in range(60):
        x_, z_ = rnd.uniform(-70, 120), rnd.uniform(-30, 90)
        K.blob3(f"rock{k}", (x_, H(x_, z_), z_), (rnd.uniform(0.2, 0.9), rnd.uniform(0.12, 0.5), rnd.uniform(0.2, 0.8)), stone, 0.15, k + 300)
    # ---------- the gun line ----------
    sandm = K.mat_once("fsand", lambda: __import__("sets.front", fromlist=["sandmat"]).sandmat())
    for i, x_ in enumerate(GUNS):
        for row, (dx, z_) in enumerate(((0.0, 10.0), (3.0, 17.0))):
            if row and abs(x_) > 40: continue
            gx = x_ + dx
            K.field_gun(f"g{i}{row}", gx, z_, -math.pi / 2 + rnd.uniform(-0.04, 0.04))
            if abs(gx) < 20:   # sandbag horseshoe round the nearer pits
                for a_ in (-1, 1): K.sandbags(f"pit{i}{row}{a_}", (gx + a_ * 2.1, 0, z_ + 1.0), math.pi / 2 + a_ * 0.5, 4, 2, i * 3 + row, sandm)
                K.sandbags(f"pitf{i}{row}", (gx, 0, z_ + 2.6), 0.0, 6, 2, i * 5 + row, sandm)
                for k in range(3): K.ammo_box(f"ab{i}{row}{k}", (gx + 1.4 + k * 0.36, 0, z_ - 1.4 + (k % 2) * 0.2), 0.2 * k, "", "#5a5a3a")
                for k in range(5): lathe(f"cas{i}{row}{k}", [(0.0, 0.0), (0.045, 0.0), (0.045, 0.32), (0.0, 0.32)], (gx - 1.0 + rnd.uniform(-0.6, 0.6), 0.045, z_ - 1.2 + rnd.uniform(-0.5, 0.5)),
                                         K.mat_once("kbrass", lambda: lib.principled("kbrass", lib.hexc("#c8963a"), 0.28, 1.0)), 10, yaw=rnd.random() * 6, tilt=Matrix.Rotation(math.radians(90), 3, "Z"))
    # camouflage nets on poles over a few guns, a command dugout with a signboard, jerrycans, a lorry behind the line
    net = K.mat_once("c9net", lambda: worn("c9net", "#8a7a52", "#5a4a30", 0.95, 0.0, 6, 0.45, "#6a5a3a"))
    for i in (8, 11, 6):
        gx = GUNS[i]; K.blob3(f"net{i}", (gx, 2.1, 10.5), (3.2, 0.25, 2.6), net, 0.3, i)
        for sx in (-1, 1):
            for sz in (-1, 1): tube(f"np{i}{sx}{sz}", [(gx + sx * 2.6, 0, 10.5 + sz * 2.0), (gx + sx * 2.4, 2.0, 10.5 + sz * 1.8)], 0.04, wood_mat("ftool", "#6a4a2a", "#3a2614", 12, 0.7), res=2, bres=1)
    K.truck("lorry1", -9, 1.5, 0.3, "#8a7a54", "#a89870"); K.truck("lorry2", 14, 0.0, -0.2, "#8a7a54", "#a89870")
    for k in range(10): K.jerrycan(f"jc{k}", (-5.5 + (k % 5) * 0.38, 0, 3.5 + (k // 5) * 0.25), 0.1 * k, "#8a7a54" if k % 3 else "#4a5236")
    bx("dugroof", (4, 0.55, 4), (3.2, 0.15, 2.4), K.mat_once("c9tin", lambda: worn("c9tin", "#7a7060", "#4a3a2a", 0.6, 0.6, 8, 0.6)), 0.01, 0.1)
    K.sandbags("dugw", (4, 0, 2.8), 0.1, 5, 2, 11, sandm)
    bx("signb", (2.2, 1.3, 2.6), (1.4, 0.55, 0.05), pmat("c9signb", "#2a2a24", 0.7), 0.01, 0.15); tube("signp", [(2.2, 0, 2.62), (2.2, 1.05, 2.62)], 0.04, wood_mat("ftool", "#6a4a2a", "#3a2614", 12, 0.7), res=2, bres=1)
    text("8th ARMY\nR.A. HQ", (2.2, 1.3, 2.56), 0.16, pmat("c9white", "#e8e2d0", 0.7), yaw=0.15, flat=False)
    # minefield marker wire running across in front of the guns (the "devil's gardens")
    for k in range(6):
        x0 = -45 + k * 16
        K.wire(f"mw{k}", (x0, 0, 26 + (k % 2)), 12, 0.04, 0.35)
        for e in (-6, 0, 6): tube(f"mp{k}{e}", [(x0 + e, 0, 26 + (k % 2)), (x0 + e, 1.0, 26 + (k % 2))], 0.04, pmat("c9iron", "#3a3a34", 0.6, 0.5), res=2, bres=1)
    for k, x_ in enumerate((-18, 6, 30)):
        bx(f"msign{k}", (x_, 1.0, 25.6), (0.7, 0.45, 0.03), pmat("c9mred", "#c8b45a", 0.6), 0.01)
        tube(f"msp{k}", [(x_, 0, 25.62), (x_, 0.8, 25.62)], 0.03, wood_mat("ftool", "#6a4a2a", "#3a2614", 12, 0.7), res=2, bres=1)
        text("MINEN!", (x_, 1.0, 25.57), 0.14, pmat("kink2", "#1a1a1a", 0.6), flat=False)
    # ---------- Rommel's panzers ahead ----------
    for k, (x_, z_, y_) in enumerate(TANKS):
        K.panzer(f"pz{k}", x_, z_, math.pi / 2 + y_, "#b89a62", y0=H(x_, z_))
    for k in range(3):
        x_, z_ = rnd.uniform(-20, 30), rnd.uniform(66, 88)
        K.panzer(f"pzb{k}", x_, z_, rnd.uniform(0, 6), burnt=True, y0=H(x_, z_), tilt=0.06)
        fire(f"pzf{k}", (x_, H(x_, z_) + 1.3, z_), 1.2, seed=k + 3, energy=2200 if night else 900)
        smoke_column(f"pzs{k}", (x_, H(x_, z_) + 2.5, z_), 18, 1.0, 4.5, K.mat_once("c9smoke", lambda: smoke_mat("c9smoke", "#1e1a18", 0.4)), drift=(10, 6), seed=k * 7, puffs=10)
    # ---------- the Tunisian surrender camp (day) ----------
    K.panzer("wreck", 64, -6, 0.8, burnt=True, tilt=0.05); fire("wreckf", (63.5, 1.5, -6), 0.6, seed=9, energy=300)
    K.truck("tlorry", 79, 7, 2.6, "#9a8a5a", "#b8a878")
    K.truck("tlorry2", 58, 9, 0.2, "#8a7a54", "#a89870")
    for k in range(4):
        x_ = 60 + k * 5; tube(f"tp{k}", [(x_, 0, 14), (x_, 6, 14)], 0.1, wood_mat("fpole", "#4a3a2a", "#2a1e14", 4, 0.9), res=2, bres=1)
        bx(f"tpx{k}", (x_, 5.6, 14), (1.2, 0.1, 0.1), wood_mat("fpole", "#4a3a2a", "#2a1e14", 4, 0.9), 0.01)
    for k in range(3): tube(f"tw{k}", [(60 + k * 5, 5.5, 14), (62.5 + k * 5, 5.0, 14), (65 + k * 5, 5.5, 14)], 0.01, pmat("fwire", "#1a1a1a", 0.5, 0.8), res=8, bres=0)
    bx("rsign", (82, 2.2, -2), (1.8, 0.5, 0.06), pmat("c9rs", "#e8e0c8", 0.6), 0.02, -0.4); tube("rsp", [(82, 0, -1.97), (82, 2.0, -1.97)], 0.05, pmat("c9iron", "#3a3a34", 0.6, 0.5), res=2, bres=1)
    text("TUNIS  20 km", (82.0, 2.2, -2.04), 0.22, pmat("kink2", "#1a1a1a", 0.6), yaw=-0.4, flat=False)
    for k in range(14):
        K.helmet_ground(f"dh{k}", (64 + rnd.uniform(0, 14), H(64, 0), -1.5 + rnd.uniform(-1.5, 1.5)), rnd.uniform(0, 6), "#7a6a46" if k % 2 else "#4c5448", "stahl")
    for k in range(10):
        x_, z_ = 66 + (k % 5) * 0.5, -2.8 + (k // 5) * 0.3
        tube(f"rif{k}", [(x_, 0.04, z_), (x_ + 1.1, 0.06, z_ + 0.3)], 0.025, wood_mat("c9stock", "#5a3a1e", "#2a1a0c", 10, 0.6), res=2, bres=1)
    for k in range(8): K.ammo_box(f"tab{k}", (73 + (k % 4) * 0.4, 0, -4 + (k // 4) * 0.3), 0.2 * k)
    K.wire("pen1", (70, 0, 8.5), 14, 0.0, 0.5)
    for k in range(5): tube(f"pp{k}", [(63 + k * 3.5, 0, 8.5), (63 + k * 3.5, 1.4, 8.5)], 0.05, wood_mat("fpole", "#4a3a2a", "#2a1e14", 4, 0.9), res=2, bres=1)
    flagm = K.mat_once("c9white_f", lambda: lib.cloth("c9white_f", "#f2f0e8"))
    tube("wfpole", [(74.5, 0, 3.0), (74.6, 3.2, 3.0)], 0.03, wood_mat("ftool", "#6a4a2a", "#3a2614", 12, 0.7), res=2, bres=1)
    from sets.front import flag as wave_flag
    wave_flag("wflag", (74.6, 3.15, 3.0), 1.0, 0.7, (1, 0.2), flagm, 0.1)
    # ---------- light ----------
    if night:
        K.sun((-0.3, 0.55, 0.8), 0.7, (0.55, 0.65, 1.0), 1.0)          # moon
        K.area((0, 12, -10), (0, 0, 15), 2500, (0.4, 0.5, 0.9), 30)        # cool sky fill
        FL = []
        for i, x_ in enumerate(GUNS):
            if abs(x_) <= 30:
                o = lib.light("POINT", T(x_, 1.6, 13.4), 0.0, (1.0, 0.62, 0.25), 0.3); o.visible_camera = False; FL.append((i, o))
        for k in range(8):   # distant burning horizon
            K.lamp_glow(f"hz{k}", (-60 + k * 18, 3, 110), 6000, (1.0, 0.45, 0.15), 3.0)
        def update(f):
            for i, o in FL: o.data.energy = 900.0 if flash_on(i, f) else 0.0
        return {"update": update}
    K.sun((0.55, 0.35, 0.75), 4.5, (1.0, 0.78, 0.52), 1.5)
    K.area((0, 20, -30), (0, 0, 10), 6000, (0.55, 0.7, 1.0), 40)
    K.area((70, 6, -14), (70, 1, 2), 900, (1.0, 0.8, 0.6), 10)
    return {}
