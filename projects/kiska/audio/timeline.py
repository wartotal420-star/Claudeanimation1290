# Picture timeline of the Kiska short (mirrors src/videos/kiska/story.ts + cast.ts) so every sound lands on the frame.
import json

FPS = 30
TOTAL = 1940
DUR = TOTAL / FPS            # 64.667 s
fr = lambda f: f / FPS
FLASH = fr(162)
# shot id: (first frame, end frame)
SHOTS = {1: (0, 162), 2: (162, 336), 3: (336, 504), 4: (504, 532), 5: (532, 651), 6: (651, 810), 7: (810, 895), 8: (895, 1005),
         9: (1005, 1131), 10: (1131, 1182), 11: (1182, 1247), 12: (1247, 1343), 13: (1343, 1446), 14: (1446, 1508),
         15: (1508, 1685), 16: (1685, 1838), 17: (1838, TOTAL)}
XFADE = {3: 8, 5: 6, 9: 8, 10: 8, 13: 10, 15: 6, 16: 12}
BOOMS = [602, 614, 627, 640]          # bombs land (frames)
SHOT_A, SHOT_B = fr(940), fr(985)    # "opens fire" / "fires back"
TRAP, MINE = fr(1546), fr(1589)


def shot_t(i):
    a, b = SHOTS[i]
    return fr(a), fr(b)


def hh(i, s=0):
    import math
    v = math.sin(i * 127.1 + s * 311.7) * 43758.5453
    return v - math.floor(v)


def night_shots():
    """the trading of fire in shot 9a (cast.ts stage9): every soldier fires on his own period"""
    a, b = fr(1005), fr(1075)
    out = []
    for i in range(12):
        period = 0.9 + hh(i, 3) * 0.8
        off = hh(i, 4) * 3
        # flash when (t + off) % period < 4 f  -> shot times t = k * period - off
        k = 0
        while True:
            t = k * period - off
            k += 1
            if t < a:
                continue
            if t >= b:
                break
            out.append((t, i < 6))
    for i, f in enumerate([1080, 1092, 1087, 1100]):
        out.append((fr(f), i % 2 == 0))
    return sorted(out)


def words(path):
    return json.load(open(path, encoding="utf-8"))
