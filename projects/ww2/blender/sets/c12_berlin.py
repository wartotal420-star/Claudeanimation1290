# Berlin, April-May 1945 (chapter 12): a bombed-out avenue of gutted blocks leading to the Reichstag, smoke and fires,
# Soviet T-34s in the street, a Volkssturm barricade of a tram car, rubble and paving stones. Hazy spring sun through
# smoke (warm, low, from behind the Reichstag), fires for warm accents.
# Layout (three, y up): the avenue runs +z, road |x| < 9 flat (y 0) for z -20..70; blocks on both sides (facades at
#   x +-11, facing the road); the barricade across x -6..2 at z 10 (Volkssturm stand at z 8..9, camera side);
#   T-34s at (-3, 26) (4, 36) (-4, 48) noses -z; the Reichstag square z 70..100: the Reichstag front at z 104 (x -45..45,
#   facing -z) with corner towers, the portico (x -14..14) with "DEM DEUTSCHEN VOLKE", the steel dome skeleton at y 30..46;
#   the flat roof parapet over the portico at y 21.5 (z 102..106): the flag-raiser stands at (6, 21.5, 103.2).
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, smoke_mat, smoke_column, text
from sets import c09_kit as K

bx, cy = K.bx, K.cy
def H(x, z):
    flat = (1 - K.sm(9, 12, abs(x))) if -24 < z < 100 else 0.0
    return 0.3 * noise.noise(Vector((x * 0.08, z * 0.08, 0.6))) * (1 - flat)
def build(M, D):
    rnd = random.Random(1945)
    K.sky("#7a7a8a", "#e8b890", 0.9, "#6a6a80", "#f0c098")
    gm = K._ground("c12ground", [(0.3, lib.hexc("#4a4440")), (0.5, lib.hexc("#5e5650")), (0.7, lib.hexc("#6e665e"))], 0.85, 0.08, 3.0, 0.6, "#3a342e", 0.7)[0]
    K.heightfield("ground", H, -120, 120, -40, 160, 1.0, gm, lambda x, z: 0.6 if abs(x) < 8 and z < 100 else 0.0)
    from sets.kit_sbpw import wet_cobbles
    bx("road", (0, 0.01, 30), (16, 0.04, 110), wet_cobbles("c12cob", "#5a5660", "#3e3a44", 0.3, 4.0), 0)
    from sets.front import ruin_mat
    PL = ["#a89a88", "#9a8070", "#8a8c90", "#b09a80", "#8a7a6a", "#a8705a", "#a8a088", "#7a8478"]
    RM = [K.mat_once(f"c12ruin{k}", lambda c=c, k=k: ruin_mat(f"c12ruin{k}", c)) for k, c in enumerate(PL)]
    signs = {1: ("APOTHEKE", "#2a3a2a", "#e8dcb8"), 3: ("KAUFHAUS", "#4a1a1a", "#efe2b8"), 6: ("CAFÉ KRANZLER", "#1a2a4a", "#efe2b8"), 9: ("BÄCKEREI", "#3a2a1a", "#efe2b8")}
    for sd in (-1, 1):
        zz = -30.0; k = 0
        while zz < 66:
            w = rnd.uniform(8, 12)
            K.ruin(f"r{sd}{k}", sd * 11.2, zz + w / 2, w, rnd.randint(3, 5), RM[(k + (sd > 0) * 4) % 8], 70 + k + (sd > 0) * 40, yaw=sd * math.pi / 2, sign=signs.get(k + (sd > 0)), glow_p=0.12)
            zz += w + rnd.uniform(0.5, 2.5); k += 1
    brick = K.mat_once("c12brick", lambda: lib.brickmat("c12brick", "#8a4a36", "#6a3424", "#5a4a40", 30))
    rub = K.mat_once("c12rub", lambda: ruin_mat("c12rub", "#7a6a5a", "#7a3e2c"))
    for k in range(30):
        sd = -1 if k % 2 else 1; z_ = -20 + k * 3.0 + rnd.uniform(-1, 1)
        K.rubble(f"rb{k}", (sd * rnd.uniform(7.5, 10.5), 0, z_), (rnd.uniform(1.5, 3.0), rnd.uniform(0.7, 1.6), rnd.uniform(1.5, 2.6)), rub, k, 4)
    K.bricks("bricks", (0, 0, 20), 16, 600, brick, 3, H)
    # the barricade: a tram car on its side, paving stones, a cart, sandbags
    tram = K.mat_once("c12tram", lambda: worn("c12tram", "#d8c070", "#5a4a2a", 0.6, 0.3, 4, 0.6, "#8a7a4a"))
    o = bx("tram", (-2.0, 1.3, 11.2), (9.0, 2.4, 2.6), tram, 0.12); o.rotation_euler = (math.radians(80), 0, 0.08)
    for k in range(6): bx(f"twin{k}", (-5.6 + k * 1.4, 2.5, 11.0), (1.0, 0.1, 0.8), K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0)), 0.0, 0.08)
    K.rubble("barr", (3.5, 0, 11.0), (4.0, 1.2, 2.0), rub, 9, 6)
    for k in range(4): K.sandbags(f"bsb{k}", (-6 + k * 2.6, 0, 9.4), 0.0, 4, 2, k + 3)
    from sets.front import hedgehog
    steel = K.mat_once("frust", lambda: worn("frust", "#4a3a30", "#7a3a1a", 0.7, 0.5, 6, 0.55, "#2a1a10"))
    for k, x_ in enumerate((-7.5, 6.0)): hedgehog(f"hh{k}", (x_, 0, 13.5), k * 0.7, steel)
    K.truck("dtruck", 6.5, 20, 2.3, "#4a4a3e", "#5a5a48"); fire("dtf", (6.4, 1.5, 20), 0.8, seed=4, energy=700)
    for k, (x_, z_, lean) in enumerate(((-8.2, 4, 0.0), (8.1, 18, 0.3), (-8.3, 32, -0.4), (8.0, 46, 0.1), (-8.1, 60, 0.0))):
        top = (x_ + math.sin(lean) * 6, 6 * math.cos(lean), z_)
        tube(f"lp{k}", [(x_, 0, z_), ((x_ + top[0]) / 2, 3.1, z_), top, (top[0] + (0.9 if x_ < 0 else -0.9), top[1] + 0.2, z_)], 0.09, pmat("c12iron", "#2a2a28", 0.6, 0.5), res=4, bres=1)
    # T-34s in the street (noses -z) with tank-riders' kit
    for k, (x_, z_) in enumerate(((-3, 26), (4, 36), (-4, 48))): K.t34(f"t{k}", x_, z_, math.pi / 2 + rnd.uniform(-0.08, 0.08))
    # the Reichstag
    reich(rnd)
    sm = K.mat_once("c12smoke", lambda: smoke_mat("c12smoke", "#2a2422", 0.4))
    for k in range(10):
        x_, z_ = rnd.uniform(-60, 60), rnd.uniform(40, 140)
        if abs(x_) < 10 and z_ < 70: continue
        fire(f"ff{k}", (x_, 1.0, z_), 2.0, seed=k + 60, energy=5000)
        smoke_column(f"fs{k}", (x_, 8, z_), 50, 2.5, 10, sm, drift=(-30, 20), seed=k + 70, puffs=12)
    for k in range(4):
        x_, z_ = (-1) ** k * rnd.uniform(9, 11), rnd.uniform(0, 60)
        fire(f"rf{k}", (x_, rnd.uniform(4, 9), z_), 1.4, seed=k + 80, energy=2500)
    # light: low hazy sun behind the Reichstag, smoke-tinted sky fill, warm bounce in the street
    K.sun((0.25, 0.3, 1.0), 3.0, (1.0, 0.72, 0.5), 3.0)
    K.area((0, 40, -40), (0, 0, 30), 20000, (0.62, 0.66, 0.8), 80)
    K.area((0, 6, -10), (0, 1.5, 12), 1500, (1.0, 0.72, 0.5), 16)
    return {}
def reich(rnd):
    st = K.mat_once("c12reich", lambda: worn("c12reich", "#b8ae98", "#5a5448", 0.85, 0.0, 0.8, 0.56, "#3a3630"))
    dark = K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0))
    Z = 104.0
    bx("rbody", (0, 10.5, Z + 18), (90, 21, 36), st, 0.05)
    for sx in (-1, 1): bx(f"rtower{sx}", (sx * 40, 14, Z + 2), (14, 28, 14), st, 0.05)
    for sx in (-1, 1):
        for sz in (0,):
            for k in range(4): cy(f"rtc{sx}{k}", (sx * 40 - 5 + k * 3.3, 24.5, Z - 5.2), 0.5, 5, st, 14)
    bx("rportico", (0, 10.5, Z - 2), (30, 21, 6), st, 0.05)
    for k in range(6): cy(f"rcol{k}", (-12.5 + k * 5, 9.5, Z - 6.5), 1.2, 17, st, 20)
    K.prism("rped", [(-15, 18.5), (15, 18.5), (0, 24)], Z - 7.5, Z - 4.0, lambda a, b, c: (a, b, c), st)
    bx("rinscr", (0, 17.5, Z - 7.35), (22, 1.6, 0.3), st, 0.02)
    text("DEM DEUTSCHEN VOLKE", (0, 17.4, Z - 7.6), 1.15, pmat("c12insc", "#3a3228", 0.6), flat=False)
    for k in range(5): bx(f"rdoor{k}", (-10 + k * 5, 5, Z - 4.9), (2.4, 7, 0.1), dark, 0.0)
    for sx in (-1, 1):
        for fl in range(3):
            for k in range(5):
                x_ = sx * (18 + k * 3.4)
                bx(f"rw{sx}{fl}{k}", (x_, 4 + fl * 6, Z - 0.02), (1.6, 3.2, 0.1), dark if rnd.random() < 0.8 else K.mat_once("c9glowwin", lambda: lib.emit("c9glowwin", (1.0, 0.28, 0.04), 1.2)), 0.0)
    bx("rroof", (0, 21.4, Z + 2), (30, 0.4, 10), st, 0.02)
    for k in range(16): bx(f"rpar{k}", (-14.5 + k * 1.93, 22.0, Z - 2.9), (1.0, 0.9, 0.5), st, 0.02)
    # the burnt dome: a ring and steel ribs only
    steel = K.mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    cy("rdrum", (0, 24, Z + 18), 14, 6, st, 40)
    for k in range(20):
        a = k / 20 * math.tau; pts = []
        for j in range(9):
            b = j / 8 * math.pi / 2; pts.append((13 * math.cos(b) * math.cos(a), 27 + 15 * math.sin(b), Z + 18 + 13 * math.cos(b) * math.sin(a)))
        tube(f"rrib{k}", pts, 0.18, steel, res=6, bres=1)
    for j in range(4):
        b = (j + 1) / 5 * math.pi / 2; r = 13 * math.cos(b)
        pts = [(r * math.cos(k / 24 * math.tau), 27 + 15 * math.sin(b), Z + 18 + r * math.sin(k / 24 * math.tau)) for k in range(25)]
        tube(f"rring{j}", pts, 0.14, steel, res=6, bres=1)
