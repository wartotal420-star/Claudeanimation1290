# Picture timeline of WW2 part 1 (cold open + chapter 1), mirrors src/videos/ww2/story.ts
import json
FPS = 30
TOTAL = 3633
DUR = TOTAL / FPS          # 121.1 s
fr = lambda f: f / FPS
FLASH = fr(779)            # chapter card start (the music sting)
SHOTS = {1: (0, 140), 2: (140, 212), 3: (212, 270), 4: (270, 386), 5: (386, 504), 6: (504, 690), 7: (690, 779), 8: (779, 825),
         9: (825, 1027), 10: (1027, 1071), 11: (1071, 1290), 12: (1290, 1435), 13: (1435, 1672), 14: (1672, 1815), 15: (1815, 1930),
         16: (1930, 2057), 17: (2057, 2111), 18: (2111, 2285), 19: (2285, 2384), 20: (2384, 2547), 21: (2547, 2707), 22: (2707, 2902),
         23: (2902, 3182), 24: (3182, 3287), 25: (3287, 3355), 26: (3355, 3405), 27: (3405, 3495), 28: (3495, TOTAL)}
DOMINO_T0, DOMINO_DT = fr(53), 0.045


def shot_t(i):
    a, b = SHOTS[i]
    return fr(a), fr(b)


def words(path):
    return json.load(open(path, encoding="utf-8"))
