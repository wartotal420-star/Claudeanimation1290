# Chapter 6: the Leningrad Philharmonic's Grand Hall, 9 August 1942 (Shostakovich's Seventh), and a city rooftop with
# loudspeakers aimed at the German lines.
# Hall (three coords): white Corinthian columns along both sides (x +-8), crystal chandeliers, red velvet seats in rows
# (z -14..-2, the audience faces +z), the stage platform at z 2..10 (top y 1.0) with music stands and chairs for the
# orchestra (players at x -5..5, z 3..8 on y 1.0), the conductor's podium at (0, 1.0, 1.9) (top y 1.3).
# Rooftop (x 60..80, z 0..20, roof y 0): zinc roof, chimneys, a cluster of horn loudspeakers on a mast at (66, 0, 12)
# pointing +z toward the front, the frozen city and the smoke of the German lines on the horizon (z 300+).
import bpy, math, random
from mathutils import Vector, Matrix
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, glassm, R90
from .c05_kit import (sky, ground_mat, sun_light, area, point, spot, lathe, tube, worn, mat_once, cached, fsphere, smoke_mat, smoke_column)
from . import ikit as I

PLAYERS = [(0, 1), (0, 3), (0, 5), (0, 7), (1, 0), (1, 2), (1, 4), (1, 6), (2, 1), (2, 3), (2, 5)]

def build(M, D):
    random.seed(1942); K_.reset(); rnd = random.Random(7)
    sky((0.3, 0.4, 0.6), (0.62, 0.62, 0.66), (0.9, 0.78, 0.62), sun_dir=(-0.4, 0.35, 0.85), sun_col=(1.0, 0.8, 0.55), glow=0.6, clouds=0.8)
    K = Kit("hall"); WH = grime("hlwhite", "#f2eee4", 0.1); GLD = K_.gold(); VEL = I.velvet("hlvel", "#8a1e22")
    K.box((0, -0.05, -2), (18, 0.1, 32), I.planks("hlfloor", "#8a5a32", "#5a3a1e", "Y", 0.12, 1.4, 0.3, 0.3), 0, 0)
    K.box((0, 12.05, -2), (18, 0.1, 32), grime("hlceil", "#ece4d0", 0.12), 0, 0)
    for k in range(8): K.box((0, 11.6, -16 + k * 4), (17.8, 0.5, 0.4), WH, 0, 0.05)
    for sx in (-1, 1):
        K.box((sx * 9.05, 6, -2), (0.1, 12, 32), WH, 0, 0.0)
        for k in range(9):                                   # columns with capitals
            z = -15 + k * 3.4
            K.cyl((sx * 8.0, 5.5, z), 0.38, 10, WH, 20); K.cyl((sx * 8.0, 0.3, z), 0.5, 0.6, WH, 16); K.box((sx * 8.0, 10.7, z), (1.1, 0.6, 1.1), WH, 0, 0.05)
            for j in range(4): K.sphere((sx * 8.0 + 0.45 * math.cos(j * R90), 10.4, z + 0.45 * math.sin(j * R90)), 0.16, WH, 8)
        K.box((sx * 7.2, 6.0, -2), (1.6, 0.25, 32), WH, 0, 0.03)                               # balcony
        for k in range(40): K.cyl((sx * 6.45, 6.55, -17.5 + k * 0.8), 0.04, 0.85, WH, 8)
        K.box((sx * 6.45, 7.0, -2), (0.12, 0.08, 32), GLD, 0, 0.01)
    K.box((0, 6, 14.05), (18, 12, 0.1), WH, 0, 0.0)
    # organ pipes behind the stage
    for k in range(25): K.cyl((-6 + k * 0.5, 5 + 2.5 * math.sin(k / 24 * math.pi), 13.5), 0.18, 4 + 5 * math.sin(k / 24 * math.pi), pm("#c8b07a", 0.3, 0.8), 12)
    # the stage, music stands and chairs, the conductor's podium, timpani, a double bass, a harp
    K.box((0, 0.5, 6), (16, 1.0, 9), wood("#6a4428", "#3a2414", 4, 0.4), 0, 0.02)
    K.box((0, 0.98, 6), (15.8, 0.04, 8.8), I.planks("hlstage", "#7a5030", "#4a2c18", "X", 0.14, 1.6, 0.3, 0.2), 0, 0.0)
    for r in range(4):
        for k in range(9 - r):
            x = (k - (8 - r) / 2) * 1.5; z = 3.2 + r * 1.3 + 0.08 * x * x
            K.box((x, 1.45, z), (0.42, 0.05, 0.42), wood("#3a2214", "#1a0e06", 8, 0.4), 0, 0.01)
            for dx in (-0.18, 0.18): K.cyl((x + dx, 1.22, z + 0.18), 0.02, 0.45, pm("#2a2a2a", 0.4, 0.5), 6)
            K.cyl((x - 0.3, 1.55, z - 0.4), 0.012, 1.1, pm("#2a2a2a", 0.4, 0.5), 6); K.box((x - 0.3, 2.1, z - 0.42), (0.45, 0.3, 0.02), pm("#2a2a2a", 0.4, 0.5), 0, 0.005, 0.3)
            K.box((x - 0.3, 2.12, z - 0.44), (0.4, 0.26, 0.005), paper("#efe4c8"), 0, 0.0, 0.3)
    # instruments held by the seated players (ch06.ts seats players on these chairs: PLAYERS)
    VW = wood("#a85a1e", "#5a2a08", 12, 0.3)
    for r, k in PLAYERS:
        x = (k - (8 - r) / 2) * 1.5; z = 3.2 + r * 1.3 + 0.08 * x * x
        if (r + k) % 3 == 2:   # cello between the knees
            K.box((x, 1.55, z - 0.3), (0.32, 0.6, 0.14), VW, 0, 0.05); K.box((x, 2.05, z - 0.32), (0.05, 0.5, 0.04), pm("#1a1a1a", 0.4), 0, 0.005)
            K.cyl((x, 1.15, z - 0.3), 0.01, 0.3, pm("#8a8a8a", 0.3, 0.8), 6)
        else:                  # violin at the shoulder, bow across
            K.box((x + 0.12, 1.95, z - 0.25), (0.2, 0.06, 0.34), VW, 0.5, 0.03, 0.9, 0.0)
            K.box((x + 0.02, 2.05, z - 0.42), (0.03, 0.03, 0.25), pm("#1a1a1a", 0.4), 0.5, 0.005, 0.9)
            K.box((x + 0.05, 1.98, z - 0.35), (0.55, 0.01, 0.01), wood("#5a3a1e", "#2a1a0e", 10, 0.4), 0, 0.0, 0, 0.6)
    K.box((0, 1.15, 1.9), (0.9, 0.3, 0.9), wood("#3a2214", "#1a0e06", 8, 0.4), 0, 0.02)
    K.cyl((0.0, 1.9, 2.3), 0.015, 1.2, pm("#2a2a2a", 0.4, 0.5), 6); K.box((0, 2.5, 2.25), (0.6, 0.4, 0.03), pm("#2a2a2a", 0.4, 0.5), 0, 0.005, 0.4)
    for sx in (-1, 1): K.cyl((sx * 6.0, 1.4, 9.3), 0.45, 0.8, brass(), 20); K.cyl((sx * 6.0, 1.81, 9.3), 0.45, 0.02, pm("#e8e0cc", 0.5), 20)
    lathe("hlbass", [(0.0, 0.0), (0.32, 0.1), (0.25, 0.5), (0.32, 0.9), (0.16, 1.2), (0.05, 1.3), (0.04, 1.9), (0.0, 1.95)], (5.8, 1.0, 7.0), wood("#8a4a1e", "#4a2208", 10, 0.3), 16, sz=0.4)
    K.box((-6.2, 2.0, 7.2), (0.1, 2.0, 1.2), K_.gold(), 0.3, 0.02, 0, 0.1)
    # the audience: rows of red velvet seats; chandeliers
    for r in range(10):
        for k in range(16):
            x = -6.75 + k * 0.9; z = -2.5 - r * 1.15
            if abs(x) < 0.7: continue
            K.box((x, 0.45, z), (0.8, 0.12, 0.6), VEL, 0, 0.03); K.box((x, 0.85, z - 0.32), (0.8, 0.7, 0.1), VEL, 0, 0.03)
            K.box((x + 0.42, 0.6, z), (0.06, 0.5, 0.6), GLD, 0, 0.01)
    for k, (x, z) in enumerate(((-4, -10), (4, -10), (-4, 1), (4, 1), (0, -5))):
        K.cyl((x, 10.5, z), 0.01, 3, pm("#2a2a2a", 0.4, 0.5), 6)
        lathe(f"chand{k}", [(0.0, 0.0), (0.7, 0.3), (0.9, 0.7), (0.6, 1.1), (0.2, 1.4), (0.0, 1.5)], (x, 7.6, z), glassm(), 20)
        for j in range(10): K.sphere((x + 0.8 * math.cos(j * 0.628), 8.0, z + 0.8 * math.sin(j * 0.628)), 0.06, em("#ffe0b0", 12.0), 6)
        point((x, 7.9, z), 300, (1.0, 0.8, 0.55), 0.3)
    # wartime touches: coats on the chairs, the windows boarded, a banner
    for k in range(6): K.box((-6 + k * 2.3, 9.5, 14.0), (1.4, 3.0, 0.05), wood("#5a4a32", "#3a3020", 6, 0.8), 0, 0.01)
    K.box((0, 8.6, 13.9), (9, 0.9, 0.04), pm("#a81e22", 0.6), 0, 0.01)
    text("СЕДЬМАЯ СИМФОНИЯ", (0, 8.6, 13.86), 0.5, pm("#f0e8d0", 0.5), math.pi, "sans", 0.003, fit=8.4)
    K.build()
    spot((0, 11, -6), (0, 1.5, 6), 6000, (1.0, 0.85, 0.65), 50, 0.4, 0.5)
    area((0, 6, -15), (0, 2, 5), 1200, (0.9, 0.8, 0.7), 8)
    for sx in (-1, 1): area((sx * 8.5, 5, 6), (0, 1.5, 6), 500, (0.6, 0.7, 1.0), 3)
    # ---------------- the rooftop ----------------
    R = Kit("roof"); ZN = mat_once("hlzinc", lambda: worn("hlzinc", "#7a8088", "#5a4a3a", 0.5, 0.6, 4, 0.7, "#5a5e64"))
    R.box((70, -0.1, 10), (24, 0.2, 24), ZN, 0, 0.0)
    for k in range(12): R.box((60 + k * 2, 0.02, 10), (0.06, 0.06, 24), pm("#5a5e64", 0.5, 0.6), 0, 0.0)
    for k, (x, z) in enumerate(((62, 4), (77, 16), (74, 3))): R.box((x, 1.0, z), (1.0, 2.0, 1.4), K_.brick("hlch", "#8a4a36", "#7a3e2e", "#5a4a42", 4.0), 0, 0.02)
    R.cyl((66, 2.5, 12), 0.08, 5, pm("#2a2a2a", 0.5, 0.5), 8)
    for k in range(4):
        a = (k - 1.5) * 0.35; y = 4.2 + (k % 2) * 0.6
        R.cyl((66 + 0.5 * math.sin(a), y, 12 + 0.4), 0.06, 0.4, pm("#3a3a3a", 0.5, 0.5), 8, "z")
        lathe(f"horn{k}", [(0.06, 0.0), (0.12, 0.3), (0.45, 1.0), (0.47, 1.02)], (66 + 0.5 * math.sin(a), y, 12.5), pm("#3a4a3a", 0.4, 0.5), 20, cap=False,
              tilt=Matrix.Rotation(math.radians(90), 3, "X") @ Matrix.Rotation(a, 3, "Z"))
    for k in range(20): R.box((60 + k * 1.2, 0.3, 21.8), (0.06, 0.6, 0.06), pm("#2a2a2a", 0.5, 0.5), 0, 0.0)
    R.box((72, 0.6, 21.8), (24, 0.04, 0.04), pm("#2a2a2a", 0.5, 0.5), 0, 0.0)
    snow = mat_once("hlsnow", lambda: lib.principled("hlsnow", hexc("#e8eef6"), 0.6))
    for k in range(18): fsphere(R, (60 + rnd.uniform(0, 22), 0.05, rnd.uniform(0, 21)), rnd.uniform(0.4, 1.2), snow, 10, (1.5, 0.25, 1.0))
    # the city below and beyond: roofs, domes (St Isaac's), the smoke of the front far away
    for k in range(80):
        x, z = rnd.uniform(-300, 400), rnd.uniform(30, 600)
        if 50 < x < 90 and z < 40: continue
        h = rnd.uniform(-20, -6); R.box((x, h, z), (rnd.uniform(14, 30), 10, rnd.uniform(14, 30)), grime(f"hlcity{k % 4}", ("#c8b080", "#b89890", "#a8b098", "#c8c0b0")[k % 4], 0.3), 0, 0.0)
    R.cyl((120, 10, 260), 18, 30, WH, 24); fsphere(R, (120, 30, 260), 16, GLD, 20, (1, 1.1, 1))
    R.build()
    smm = smoke_mat("hlsm", "#4a4440", 0.45)
    for k in range(5): smoke_column(f"front{k}", (-200 + k * 120, -10, 900), 120, 20, 60, smm, drift=(60, 40), seed=k, puffs=8)
    sun_light((0.4, -0.35, -0.85), 2.2, (1.0, 0.82, 0.62), 2)
    return {}
