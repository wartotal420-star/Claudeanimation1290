# Heston Aerodrome, 30 September 1938 (chapter 2 shots 34, 35, 37). Three coords, cameras look +z: the British Airways
# Lockheed 14 (G-AFGN) stands on the grass apron with its nose toward -x, door on the near (-z) side at about (11.0, 1.4, 9.4), steps below it at (11.0, 0, 8.7);
# a little boarding step below it. Chamberlain's spot: the microphone stand at (0.6, 0, 4.4), he stands at (0, 0, 4.6).
# Crowd behind rope lines on both sides (x -9..-3 and 3..9, z 2..8, rope at |x| 2.6) and newsreel cameras on a platform at
# (-6.5, 0, -1). Behind: the hangar with HESTON AIRPORT lettering (z 34), a control tower, windsock, parked cars, flags.
# Light: grey overcast afternoon (cool soft sky + a weak low sun), wet concrete apron reflecting; nothing at |x| < 2,
# z -4..4 so the paper can blow away (shot 37 card).
import bpy, math, random
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, flat_text, sign, poster, R90, cached, set_world
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets import ikit as IK

def build(M, D):
    random.seed(1938); KS.reset(); rnd = random.Random(930)
    K = Kit("heston")
    set_world((0.42, 0.46, 0.52), (0.72, 0.72, 0.72), 1.1, (0.46, 0.5, 0.56), (0.78, 0.78, 0.78))
    GR = CK.ground_mat("hgrass", "#5a7a3a", "#3e5a2a", 0.3); CON = lib.principled("hcon", hexc("#8a8884"), 0.25)
    t, n, l = lib.nodes(CON); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.6; tc = n.new("ShaderNodeTexCoord"); l.new(tc.outputs["Object"], nz.inputs["Vector"])
    r = lib.ramp(n, l, nz.outputs["Fac"], [(0.4, (0.05, 0.05, 0.05)), (0.6, (0.6, 0.6, 0.6))]); l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Roughness"])
    K.box((0, -0.05, 40), (220, 0.1, 160), GR, 0, 0)
    K.box((0, 0.005, 10), (40, 0.01, 40), CON, 0, 0)
    for k in range(9): K.box((-20 + k * 5, 0.012, 10), (0.04, 0.004, 40), pm("#5a5854", 0.6), 0, 0)
    # the airliner
    CK.airliner(K, 7.5, 0.0, 10.5, math.pi, 1.0)
    st = CK.X(11.0, 0, 8.9, R90)
    for j in range(3): st.box(K, (0, 0.12 + j * 0.24, -0.3 * j), (0.9, 0.06, 0.32), pm("#7a7a7e", 0.4, 0.7), 0.01)
    for sd in (-1, 1): st.box(K, (sd * 0.45, 0.45, -0.3), (0.04, 0.9, 1.0), pm("#7a7a7e", 0.4, 0.7), 0.0, 0, -0.6)
    # microphone stand + BBC box, the newsreel platform with cameras on tripods
    K.cyl((0.6, 0.75, 4.2), 0.015, 1.5, pm("#2a2a2a", 0.3, 0.7), 8); K.cyl((0.6, 0.02, 4.2), 0.18, 0.04, pm("#2a2a2a", 0.3, 0.7), 14)
    K.box((0.6, 1.55, 4.2), (0.12, 0.16, 0.06), pm("#c8c8c8", 0.2, 0.9), 0, 0.02); K.box((0.6, 1.36, 4.2), (0.22, 0.1, 0.05), pm("#1a1a1a", 0.4), 0, 0.01)
    text("BBC", (0.6, 1.36, 4.17), 0.06, pm("#f2ead6", 0.5), 0, "sans", 0.001)
    K.box((-6.5, 0.45, -1.0), (3.4, 0.9, 2.2), wood("#6a5a42", "#3a2e1e", 8), 0, 0.02)
    for k, x in enumerate((-7.5, -5.6)):
        for a in (0, 2.1, 4.2): K.cyl((x + 0.25 * math.cos(a), 1.5, -1.0 + 0.25 * math.sin(a)), 0.02, 1.2, wood("#6a5a42", "#3a2e1e", 8), 6, "y", None, 0, 0.2 * math.sin(a), -0.2 * math.cos(a))
        K.box((x, 2.2, -1.0), (0.35, 0.35, 0.5), pm("#1a1a1a", 0.4, 0.3), 0.3, 0.03)
        for sd in (-1, 1): K.cyl((x, 2.5, -1.0 + sd * 0.15), 0.16, 0.06, pm("#1a1a1a", 0.4, 0.3), 14, "x", yaw=0.3)
        K.cyl((x + 0.2, 2.2, -1.2), 0.07, 0.2, pm("#2a2a2a", 0.2, 0.6), 10, "x", yaw=0.3)
    sign(K, (-6.5, 0.6, -2.12), 2.6, 0.35, 0, "BRITISH MOVIETONE NEWS", "#1e1e2a", pm("#e8dcb8", 0.5), "sans")
    # rope lines on posts, crowd barriers
    ROPE = cloth("#c8b88a")
    for sd in (-1, 1):
        for k in range(8):
            z = -2 + k * 1.6; x = sd * 2.6
            K.cyl((x, 0.5, z), 0.035, 1.0, pm("#c8c4b8", 0.3, 0.6), 8); K.cyl((x, 0.02, z), 0.15, 0.04, pm("#2a2a2a", 0.4, 0.6), 12)
            if k < 7: K.cyl((x, 0.88, z + 0.8), 0.015, 1.6, ROPE, 6, "z")
    # hangar with lettering, control tower, windsock, cars, flags
    HW = grime("hhangar", "#c8c0b0", 0.3); ROOF = CK.wm("hroof", "#6a6e72", "#4a4a4a", 0.5, 0.5, 6, 0.7)
    K.box((0, 6, 38), (44, 12, 14), HW, 0, 0.05)
    K.cyl((0, 12, 38), 22.5, 14, ROOF, 32, "z", bev=0.05) if False else None
    for k in range(10):
        a0 = math.pi * k / 10; a1 = math.pi * (k + 1) / 10; am = (a0 + a1) / 2
        K.box((22 * math.cos(am), 12 + 5 * math.sin(am), 38), (22 * math.pi / 10 * 1.05, 0.3, 14.2), ROOF, 0, 0, 0, math.atan2(-5 * math.cos(am), 22 * math.sin(am)))
    K.box((0, 4.5, 30.95), (30, 9, 0.12), CK.wm("hdoor", "#7a8088", "#5a5a5a", 0.5, 0.5, 8, 0.75), 0, 0.01)
    for k in range(8): K.box((-13 + k * 3.7, 4.5, 30.85), (0.08, 9, 0.12), pm("#4a4e54", 0.4, 0.5), 0, 0)
    text("HESTON AIRPORT", (0, 10.2, 30.9), 1.5, pm("#1e2a4a", 0.5), 0, "sans", 0.02, fit=26)
    K.box((26, 5, 30), (6, 10, 6), HW, 0, 0.05); K.box((26, 11, 30), (5, 2.2, 5), pm("#2a3440", 0.1, 0.4), 0, 0.02); K.box((26, 12.3, 30), (6, 0.3, 6), ROOF, 0, 0.02)
    for j in range(3):
        for i in range(2): K.box((26 - 1.5 + i * 3, 2.5 + j * 2.5, 26.95), (1.0, 1.2, 0.05), pm("#2a3440", 0.1, 0.4), 0, 0)
    K.cyl((-24, 4, 22), 0.08, 8, pm("#d8d4c8", 0.4, 0.5), 8)
    K.cyl((-23.2, 7.8, 22), 0.32, 1.6, cloth("#e86a2a"), 12, "x", 0.12)
    for k, x in enumerate((-16, -12)): CK.flagpole(K, (x, 0, 28), 7, IK.img_mat(f"hfl{k}", IK.flag_img("uk"), 0.7, sheen=0.3), 2.0, 1.3)
    for k, (x, z, yaw, col) in enumerate(((-14, 12, 0.3, "#1e1e22"), (-17, 15, 0.25, "#3a2a22"), (14, 16, -0.3, "#1e2a3a"), (17, 13, -0.2, "#1e1e22"))):
        c = CK.X(x, 0, z, yaw)
        c.box(K, (0, 0.75, 0), (4.4, 0.7, 1.75), pm(col, 0.2, 0.4), 0.15); c.box(K, (-0.4, 1.4, 0), (2.2, 0.65, 1.6), pm(col, 0.2, 0.4), 0.15)
        c.box(K, (0.75, 1.4, 0), (0.05, 0.5, 1.5), pm("#2a3440", 0.06, 0.4), 0.01)
        for sd in (-1, 1):
            for xx in (1.4, -1.4): CK.wheel(K, c, (xx, 0.4, sd * 0.88), 0.4, 0.22, pm("#141414", 0.8), pm("#c8c8c8", 0.2, 0.9))
    # umbrellas over the crowd area, a police box, a fuel bowser
    for k in range(10):
        x = rnd.choice((-1, 1)) * rnd.uniform(4, 9); z = rnd.uniform(3, 9)
        K.cyl((x, 2.05, z), 0.6, 0.25, pm("#141418", 0.4), 12, "y", 0.03); K.cyl((x, 1.6, z), 0.012, 0.9, pm("#141418", 0.4), 6)
    K.box((11, 1.3, 3), (1.1, 2.6, 1.1), pm("#1e2a5a", 0.4), 0, 0.03); K.box((11, 2.75, 3), (1.2, 0.2, 1.2), pm("#1e2a5a", 0.4), 0, 0.03)
    text("POLICE", (11, 2.3, 2.43), 0.14, pm("#f2ead6", 0.5), 0, "sans", 0.002)
    CK.lorry(K, -14.0, 3.0, 0.4, "#c8a83a", "#c8a83a", 0.0, 0.9, False)
    for k in range(3): CK.KS.barrel(K, (-11.5, 0.45, 0.5 + k * 0.7), 0.3, 0.9, CK.wm("hbar", "#3a5a8a", "#2a2a2a", 0.5, 0.4, 10, 0.7), iron())
    # light: soft overcast sky, a weak low sun, cool fill
    IK.sun((0.3, -0.5, 0.8), 1.4, (1.0, 0.9, 0.78), 6.0)
    lib.light("AREA", T(0, 9, -10), 2600, (0.85, 0.9, 1.0), 16).rotation_euler = (math.radians(-60), 0, math.pi)
    K.build()
    return {}
