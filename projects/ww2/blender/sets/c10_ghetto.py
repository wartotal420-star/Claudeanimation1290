# Chapter 10: the ghetto wall and the emptied village. Grey winter light, muted colour, no people built in.
# GHETTO (origin): a cobbled street (x -6..6) running +z, closed at z 14 by a high brick wall with barbed wire on top and a
#   timber gate (x -1.6..1.6) with the historical notice board; tenements both sides (facades at x +-6.5, facing the road),
#   laundry lines, a handcart, a dropped bundle. Behind the wall (z 14..40) the street continues: people stand at the gate's
#   bars at z 14.6..16 (characters), seen through the gate from the camera side (z < 14).
# VILLAGE (x 120): a muddy lane along z (x 117..123), small log houses with carved window frames both sides, doors open,
#   a chair tipped over, a doll in the mud at (119.6, 0, 9), a well with a sweep at (125, 0, 16), birches; mist kept to fx.
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, text
from sets import c09_kit as K
from sets.kit_sbpw import Kit, wet_cobbles

bx, cy = K.bx, K.cy
def build(M, D):
    rnd = random.Random(1941)
    K.sky("#8a9098", "#c0c0bc", 0.9, "#7a828c", "#b4b4b0")
    bx("cobble", (0, -0.05, 15), (14, 0.1, 70), wet_cobbles("c10cob", "#5e5a60", "#46424a", 0.6, 5.0), 0)
    for sd in (-1, 1): bx(f"walk{sd}", (sd * 6.0, 0.08, 15), (2.0, 0.16, 70), K.concrete("c10walk", "#7a7670"), 0.01)
    PL = ["#8a7a6a", "#7a6a5e", "#6e6a64", "#8a6e5a", "#76705e", "#6a5e56"]
    win = K.mat_once("c10win", lambda: lib.principled("c10win", lib.hexc("#1a1e24"), 0.1))
    KK = Kit("ghetto")
    for sd in (-1, 1):
        for k in range(8):
            z_ = -14 + k * 7; col = PL[(k + (sd > 0) * 3) % 6]
            m = K.mat_once("c10fac" + col, lambda c=col: worn("c10fac" + c, c, "#3a3430", 0.85, 0.0, 1.2, 0.6, "#4a4440"))
            h = 11 + (k % 3) * 2
            KK.box((sd * 10.0, h / 2, z_), (7.0, h, 6.8), m, 0, 0.02)
            KK.box((sd * 6.55, 3.6 + 0.0, z_), (0.12, 0.25, 6.8), K.concrete("c10cor", "#8a8478"), 0, 0.01)
            for fl in range(3):
                for j in range(3):
                    zz = z_ - 2.2 + j * 2.2; yy = 2.0 + fl * 3.2
                    KK.box((sd * 6.48, yy, zz), (0.05, 1.5, 0.9), win, 0, 0.0)
                    KK.box((sd * 6.45, yy - 0.8, zz), (0.1, 0.08, 1.1), K.concrete("c10cor", "#8a8478"), 0, 0.0)
            KK.box((sd * 6.48, 1.05, z_ + 2.6), (0.06, 2.1, 1.1), wood_mat("c10door", "#3a2a1e", "#1e140c", 6, 0.7), 0, 0.0)
    KK.build()
    # the wall with wire, the gate, the notice
    brick = K.mat_once("c10wbrick", lambda: lib.brickmat("c10wbrick", "#7a4232", "#6a3a2c", "#5a5048", 4))
    for sd in (-1, 1): bx(f"gwall{sd}", (sd * 4.4, 1.6, 14.2), (5.6, 3.2, 0.4), brick, 0.01)
    bx("gwalltop", (0, 3.35, 14.2), (14, 0.3, 0.5), K.concrete("c10cap", "#7a766e"), 0.01)
    for k in range(13): tube(f"wpost{k}", [(-6 + k, 3.4, 14.2), (-6 + k, 4.3, 14.0)], 0.03, pmat("c10iron", "#2a2a28", 0.5, 0.6), res=2, bres=0)
    for h in (3.6, 3.85, 4.1): tube(f"wwire{h}", [(-6, h, 14.1), (6, h, 14.1)], 0.008, pmat("c10iron", "#2a2a28", 0.5, 0.6), res=2, bres=0)
    K.wire("wcoil", (0, 3.55, 14.25), 12, 0.0, 0.3)
    gate = wood_mat("c10gate", "#4a3a2a", "#2a1e14", 5, 0.8)
    for sd in (-1, 1): bx(f"gpost{sd}", (sd * 1.65, 1.7, 14.2), (0.3, 3.4, 0.5), gate, 0.01)
    for k in range(9): bx(f"gbar{k}", (-1.4 + k * 0.35, 1.3, 14.15), (0.08, 2.6, 0.08), gate, 0.005)
    for y_ in (0.3, 1.4, 2.5): bx(f"grail{y_}", (0, y_, 14.12), (3.1, 0.12, 0.1), gate, 0.005)
    bx("notice", (2.9, 2.2, 13.96), (1.6, 0.9, 0.04), pmat("c10notice", "#e8dcbc", 0.7), 0.005)
    text("WOHNGEBIET DER JUDEN\nBETRETEN VERBOTEN", (2.9, 2.22, 13.93), 0.1, pmat("kink2", "#1a1a1a", 0.6), flat=False)
    # behind the wall: the street goes on, a lamp, a cart; laundry lines, a handcart, a bundle on this side
    for k in range(4): tube(f"line{k}", [(-6.5, 6 + k * 3, -6 + k * 9), (0, 5.4 + k * 3, -6 + k * 9), (6.5, 6 + k * 3, -6 + k * 9)], 0.008, pmat("c10rope", "#8a8070", 0.8), res=6, bres=0)
    for k in range(18):
        j = k // 5; x_ = -5 + (k % 5) * 2.2 + rnd.uniform(-0.3, 0.3)
        bx(f"cloth{k}", (x_, 5.4 + j * 3 - 0.3 + (abs(x_) / 6.5) * 0.5, -6 + j * 9), (rnd.uniform(0.4, 0.8), rnd.uniform(0.5, 0.9), 0.02), K.mat_once(f"c10cl{k % 4}", lambda: lib.cloth(f"c10cl{k % 4}", ["#d8d4c8", "#8a8a9a", "#a89a8a", "#c8c0b0"][k % 4])), 0.0)
    cart = wood_mat("c10cart", "#6a5a42", "#3a2e22", 6, 0.8)
    bx("cart", (-4.2, 0.6, 9.5), (1.2, 0.35, 1.8), cart, 0.01, 0.3)
    for sd in (-1, 1): cy(f"cwh{sd}", (-4.2 + sd * 0.65 * math.cos(0.3), 0.4, 9.5 - sd * 0.65 * math.sin(0.3)), 0.4, 0.06, cart, 16, rot=(0, math.radians(90), 0.3))
    for k in range(3): K.blob3(f"bund{k}", (-4.2 + rnd.uniform(-0.3, 0.3), 0.9, 9.5 + rnd.uniform(-0.5, 0.5)), (0.35, 0.25, 0.3), K.mat_once(f"c10bund{k}", lambda: lib.cloth(f"c10bund{k}", ["#6a6458", "#5a4a4a", "#7a7060"][k])), 0.05, k)
    tube("glamp", [(4.8, 0, 22), (4.8, 4.2, 22), (4.2, 4.4, 22)], 0.06, pmat("c10iron", "#2a2a28", 0.5, 0.6), res=2, bres=1)
    village(rnd)
    K.sun((-0.4, 0.35, 0.8), 1.1, (0.9, 0.86, 0.8), 6.0)
    K.area((0, 30, -20), (0, 0, 15), 9000, (0.72, 0.78, 0.88), 50)
    K.area((120, 30, -10), (120, 0, 15), 9000, (0.72, 0.78, 0.88), 50)
    return {}
def village(rnd):
    X = 120.0
    mud = K._ground("c10mud", [(0.3, lib.hexc("#3e3428")), (0.5, lib.hexc("#4e4232")), (0.7, lib.hexc("#5e5440"))], 0.75, 0.1, 4.0, 0.6, "#2a241c", 0.6)[0]
    K.heightfield("vground", lambda x, z: 0.12 * noise.noise(Vector((x * 0.15, z * 0.15, 1.0))) * K.sm(3, 6, abs(x - X)), X - 50, X + 50, -20, 70, 1.0, mud, lambda x, z: 0.8 if abs(x - X) < 3 else 0.0)
    logm = wood_mat("c10vlog", "#5a4a3a", "#2e2418", 3, 0.85)
    trim = wood_mat("c10vtrim", "#7a8a9a", "#4a5a6a", 8, 0.7)
    thatch = K.mat_once("c10vthatch", lambda: worn("c10vthatch", "#6a5a42", "#3a3226", 0.95, 0.0, 6, 0.5, "#4a4030"))
    dark = K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0))
    for sd in (-1, 1):
        for k in range(5):
            z_ = -4 + k * 11 + rnd.uniform(-1, 1); x_ = X + sd * 8.5
            for j in range(10): tube(f"vh{sd}{k}{j}", [(x_ - sd * 3, 0.15 + j * 0.28, z_ - 3.5), (x_ - sd * 3, 0.15 + j * 0.28, z_ + 3.5)], 0.14, logm, res=2, bres=1)
            bx(f"vhb{sd}{k}", (x_, 1.45, z_), (5.8, 2.9, 6.8), logm, 0.02)
            K.loft2(f"vhr{sd}{k}", [(3.6, -3.9), (3.6, 3.9), (-3.6, 3.9), (-3.6, -3.9)], 2.9, [(0.15, -3.9), (0.15, 3.9), (-0.15, 3.9), (-0.15, -3.9)], 5.2, K.P_of(x_, z_, 0, 0), thatch)
            for j in (-1.8, 1.8):
                bx(f"vw{sd}{k}{j}", (x_ - sd * 3.05, 1.6, z_ + j), (0.05, 0.8, 0.7), dark, 0.0)
                bx(f"vwt{sd}{k}{j}", (x_ - sd * 3.08, 1.6, z_ + j), (0.04, 1.0, 0.9), trim, 0.01)
            # the door stands open
            bx(f"vd{sd}{k}", (x_ - sd * 3.03, 1.0, z_), (0.05, 1.9, 0.95), dark, 0.0)
            bx(f"vdl{sd}{k}", (x_ - sd * 3.5, 1.0, z_ + 0.55), (0.9, 1.9, 0.06), wood_mat("c10door", "#3a2a1e", "#1e140c", 6, 0.7), 0.01, sd * 0.4)
    from sets.warroom import chair
    chair("vchair", (X - 2.0, 0, 6.0), 1.2, logm, K.mat_once("c10vseat", lambda: lib.cloth("c10vseat", "#5a4a3a")))
    o = bx("vchair2", (X + 2.2, 0.25, 14), (0.45, 0.06, 0.45), logm, 0.01, 0.5); o.rotation_euler[1] = 1.4
    # the doll: cloth body, head, a faded red dress
    K.blob3("doll", (X - 0.4, 0.06, 9), (0.12, 0.05, 0.2), K.mat_once("c10doll", lambda: lib.cloth("c10doll", "#8a3a3a")), 0.01, 1)
    K.blob3("dollh", (X - 0.4, 0.07, 8.78), (0.06, 0.05, 0.06), K.mat_once("c10dollh", lambda: lib.principled("c10dollh", lib.hexc("#e8d0b8"), 0.6)), 0.0, 2)
    for k in range(4): K.blob3(f"vsack{k}", (X + rnd.uniform(-2.5, 2.5), 0.15, rnd.uniform(0, 30)), (0.3, 0.2, 0.25), K.mat_once("c10sack", lambda: lib.cloth("c10sack", "#7a7060")), 0.04, k)
    tube("vwell", [(X + 5, 0, 16), (X + 5, 3.5, 16)], 0.12, logm, res=2, bres=1)
    tube("vsweep", [(X + 2.5, 1.5, 16), (X + 8, 5.5, 16)], 0.07, logm, res=2, bres=1)
    lathe("vwellb", [(0.0, 0.0), (0.7, 0.0), (0.7, 0.8), (0.55, 0.8), (0.55, 0.1), (0.0, 0.1)], (X + 2.6, 0, 16), logm, 12)
    bark = K.mat_once("c10birch", lambda: worn("c10birch", "#e8e4dc", "#2a2a28", 0.7, 0.0, 3, 0.55, "#c8c4bc"))
    for k in range(16):
        x_, z_ = X + rnd.choice((-1, 1)) * rnd.uniform(14, 30), rnd.uniform(-10, 60); h_ = rnd.uniform(8, 13)
        tube(f"vbir{k}", [(x_, 0, z_), (x_ + 0.3, h_ * 0.5, z_), (x_, h_, z_ + 0.2)], 0.14, bark, res=3, bres=1, taper=lambda f: 1 - 0.6 * f)
    fence = wood_mat("c10vfence", "#6a5a46", "#3a3026", 6, 0.85)
    for sd in (-1, 1):
        for k in range(30): tube(f"vf{sd}{k}", [(X + sd * 4.0, 0, -6 + k * 1.6), (X + sd * 4.0, 1.1 + 0.1 * math.sin(k), -6 + k * 1.6)], 0.04, fence, res=2, bres=0)
