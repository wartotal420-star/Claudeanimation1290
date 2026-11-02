// Chapter 10: The Holocaust. Voice ~/ww2/voice/ch10.wav (63.26 s, 1898 frames), word frames from ch10_words.json.
// Serious and respectful: no jokes, no gore, no victims shown suffering. Slow moves, empty places, the narration carries
// the facts. Sets: c10_camp (track, gatehouse, fences, wagons, the ramp with suitcases), street (part 1: a family on the
// pavement, a shop closed), c10_ghetto (the ghetto wall and gate; the emptied village at x 120), c10_villa (the lakeside
// villa and its empty conference room at x 100), c10_memorial (shoes, suitcases, the wall of photographs, candles).
import { makeChapter } from "../chapter";
import type { ChShot } from "../chapter";
import { D, Tr } from "../story";
import type { Key, Dof } from "../story";
import { P, F, W_, act, hh, q, mist, MEN, WOMEN, KIDS, suit } from "../cast";
import type { Ctx, Beat } from "../cast";
import type { Outfit, FrontOpts } from "../toon";

const TOTAL = 1898;
type Who3 = [Outfit, string];
// a family in plain, decent clothes; an elderly survivor
const FATHER: Who3 = [{ ...MEN[6], hat: "fedora", hatCol: "#2a2a30", moustache: "#3a2a1a", stache: "plain", cigar: false, glasses: true }, "c10fa"];
const MOTHER: Who3 = [{ ...WOMEN[6], hat: "hair", hair: "#3a2a1e", pearls: false }, "c10mo"];
const GIRL: Who3 = [{ ...KIDS[2], hair: "#3a2a1e" }, "c10gi"];
const BOY: Who3 = [{ ...KIDS[0], cap: "#3a3a44" }, "c10bo"];
const GRAN: Who3 = [{ ...WOMEN[3], hat: "hair", hair: "#d8d8d8", scarf: "#5a4a4a", build: "short" }, "c10gr"];
const SHOP: Who3 = [suit("#3a3a40", { hat: "hair", hair: "#5a4a3a", part: true, vest: "#5a4a3a", apron: "#e8e2d4", rolled: true, glasses: true, build: "stout", moustache: "#4a3a2a", stache: "plain" }), "c10sh"];
const SURVIVOR: Who3 = [suit("#2e3038", { hat: "hair", hair: "#e4e4e8", brows: "#d8d8dc", bushy: true, glasses: true, tie: "#3a3a48", build: "thin", nose: "long", skin: "#f2d8c4" }), "c10sv"];

const S = (id: number, a: number, b: number, set: string, light: ChShot["light"]): ChShot => ({ id, a, b, set, light });
const CA = "c10_camp", GH = "c10_ghetto", VI = "c10_villa", ME = "c10_memorial", STR = "street";
const SHOTS: ChShot[] = [
  S(1, 0, 212, CA, "fog"), S(2, 212, 354, STR, "gloom"), S(3, 354, 437, STR, "gloom"), S(4, 437, 556, GH, "grey"), S(5, 556, 627, GH, "grey"),
  S(6, 627, 806, GH, "fog"), S(7, 806, 1000, VI, "grey"), S(8, 1000, 1085, VI, "interior"), S(9, 1085, 1200, CA, "fog"), S(10, 1200, 1362, CA, "fog"),
  S(11, 1362, 1488, ME, "interior"), S(12, 1488, 1718, ME, "interior"), S(13, 1718, 1768, ME, "interior"), S(14, 1768, TOTAL, ME, "interior"),
];
const XFADE: Record<number, number> = { 2: 16, 3: 12, 4: 16, 5: 12, 6: 16, 7: 16, 8: 16, 9: 16, 10: 16, 11: 20, 12: 16, 13: 16, 14: 16 };

type T3 = [number, number, number];
const k1 = (f0: number, set: string, pos: T3, look: T3, fov = 42, rate = 0.0015, roll = 0): Key => ({ f: f0, s: (f) => D(set, pos, look, f, f0, rate, { fov, roll }) });
const tr = (f0: number, set: string, pos: T3, look: T3, v: T3, fov = 44): Key => ({ f: f0, s: (f) => Tr(set, pos, look, f, f0, v, { fov }) });
const CAMS: Record<number, Key[]> = {
  1: [k1(0, CA, [0, 0.9, -40], [0, 3.8, 44], 40, 0.0012)],
  2: [k1(204, STR, [-4.6, 1.55, 15.6], [-7.4, 1.25, 20.2], 42, 0.0012)],
  3: [k1(348, STR, [-6.0, 1.5, 14.0], [-9.3, 1.35, 17.0], 40, 0.0015)],
  4: [k1(429, GH, [0.7, 1.5, 9.2], [0, 1.45, 15], 40, 0.0012)],
  5: [k1(550, GH, [3.5, 1.7, -4], [-0.5, 3.4, 15], 46, 0.001)],
  6: [tr(619, GH, [120.8, 1.45, -6], [120, 1.0, 10], [0, 0, 0.03], 44)],
  7: [k1(798, VI, [-6, 1.6, -14], [0, 5, 22], 46, 0.001)],
  8: [k1(992, VI, [100.3, 1.45, -2.4], [100, 0.85, 5], 42, 0.0016)],
  9: [k1(1077, CA, [-12, 1.6, 30], [0, 5, 44], 42, 0.0012)],
  10: [tr(1192, CA, [-8.6, 1.8, 61], [-2.8, 1.2, 74], [0, 0, 0.02], 44)],
  11: [k1(1352, ME, [-3.8, 1.5, 0.6], [-3.8, 0.7, 6.0], 42, 0.0015)],
  12: [tr(1480, ME, [-5.2, 1.65, 8.6], [-5.2, 2.3, 11.9], [0.034, 0, 0], 44)],
  13: [k1(1710, ME, [0, 0.78, -0.5], [0, 0.55, 0.95], 38, 0.0015)],
  14: [k1(1760, ME, [0.25, 1.25, -0.8], [0.55, 1.3, 1.9], 42, 0.0012)],
};
const DOF: Dof[] = [
  { f: 0, cInf: 3 }, { f: 212, cInf: 9 }, { f: 354, cInf: 10 }, { f: 437, cInf: 8 }, { f: 556, cInf: 4 }, { f: 627, cInf: 5 }, { f: 806, cInf: 3 },
  { f: 1000, cInf: 9 }, { f: 1085, cInf: 4 }, { f: 1200, cInf: 6 }, { f: 1362, cInf: 8 }, { f: 1488, cInf: 9 }, { f: 1718, cInf: 14 }, { f: 1768, cInf: 11 },
];

const put = (c: Ctx, w: Who3, i: number, x: number, y: number, z: number, beats: Beat[], extra: FrontOpts = {}, scale = 1) => {
  const a = act(c.t, beats, 0.35);
  P(c, W_(w[0], i, w[1]), x, y, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, ...extra }, scale);
};
const fog = (c: Ctx, n: number, x0: number, x1: number, y: number, z0: number, z1: number, w: number, col = "#e6ecf2", op = 0.45) => {
  for (let i = 0; i < n; i++) mist(c.out, ...c.O(x0 + (x1 - x0) * hh(i, 3), y + (i % 3) * 0.5, z0 + (z1 - z0) * hh(i, 5)), w, c.t, i, col, op);
};
const closedSign = (g: CanvasRenderingContext2D) => {
  g.fillStyle = "#e8dcc0"; g.fillRect(0, 0, 400, 240); g.strokeStyle = "#3a2a1a"; g.lineWidth = 10; g.strokeRect(5, 5, 390, 230);
  g.fillStyle = "#2a1a10"; g.font = "bold 58px Georgia, 'DejaVu Serif', serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("GESCHLOSSEN", 200, 105);
  g.font = "28px Georgia, 'DejaVu Serif', serif"; g.fillText("closed", 200, 172);
};

const STAGE: Record<number, (c: Ctx) => void> = {
  1: (c) => {
    // "While all of this was happening on the battlefields, something even darker was happening behind the front lines."
    fog(c, 6, -14, 14, 0.5, 10, 36, 14, "#d8dce0", 0.4);
  },
  2: (c) => {
    // "From the moment the Nazis took power, they blamed Jewish people for Germany's problems."
    put(c, FATHER, 1, -7.6, 0.15, 20.4, [[212, null, "worried"], [280, null, "sorrow"]]);
    put(c, MOTHER, 2, -6.95, 0.15, 20.6, [[212, null, "sorrow"]]);
    put(c, GIRL, 3, -7.25, 0.15, 19.9, [[212, null, "worried"]], {}, 0.72);
    // passers-by on the road side turn their backs and hurry on
    for (let i = 0; i < 3; i++) put(c, [MEN[(i * 5 + 2) % 12], `c10m${i}`], 10 + i, -4.6 + i * 1.2, 0, 24 + i * 1.4 - (c.f - 212) * 0.012 * (i % 2 ? 1 : -1), [[212, null, "stern"]], { mode: "stroll", phase: q((c.t * 0.9 + i * 0.3) % 1, 40) });
  },
  3: (c) => {
    // "First, they took away their jobs and their rights."
    put(c, SHOP, 4, -9.1, 0.15, 17.2, [[354, null, "sorrow"], [395, "collar", "sorrow"]], { facing: -1 });
    put(c, GRAN, 5, -8.3, 0.15, 17.9, [[354, null, "worried"], [412, null, "sorrow"]]);
    F(c, { key: "c10closed", cw: 400, ch: 240, draw: (p) => closedSign(p.g), x: -9.95, y: 1.55, z: 16.4, w: 0.55, h: 0.33, glow: 0.8 });
  },
  4: (c) => {
    // "Then they forced them into closed-off parts of cities called ghettos."
    put(c, FATHER, 1, -0.75, 0, 15.0, [[437, null, "sorrow"]]);
    put(c, MOTHER, 2, 0.05, 0, 15.3, [[437, null, "grief"]]);
    put(c, BOY, 6, 0.55, 0, 14.75, [[437, null, "worried"]], {}, 0.72);
    put(c, GRAN, 5, -1.25, 0, 16.0, [[437, null, "sorrow"]]);
  },
  5: (c) => {
    // "When the war began, it got worse."
    fog(c, 4, -6, 6, 1.5, 12, 30, 12, "#c8ccd0", 0.35);
  },
  6: (c) => {
    // "Special units followed the German army into the Soviet Union and murdered entire Jewish communities."
    fog(c, 8, 114, 126, 0.4, 0, 40, 12, "#dfe4e8", 0.5);
  },
  7: (c) => {
    // "And in 1942, Nazi leaders met at a villa outside Berlin to plan what they called the final solution:"
    fog(c, 4, -20, 20, 0.6, -20, -4, 18, "#e4e8ec", 0.35);
  },
  8: () => {
    // "the murder of every Jewish person in Europe." (the empty table)
  },
  9: (c) => {
    // "They built death camps, like Auschwitz, Treblinka, and Sobibor."
    fog(c, 6, -20, 10, 0.5, 20, 40, 14, "#d8dce0", 0.4);
  },
  10: (c) => {
    // "People were packed into trains, told they were being moved somewhere new, and killed when they arrived."
    fog(c, 5, -8, 8, 0.8, 70, 100, 12, "#d8dce0", 0.35);
  },
  11: () => {
    // "By the end of the war, around six million Jewish people had been murdered."
  },
  12: () => {
    // "Millions of others were killed too: Roma, disabled people, Soviet prisoners, Poles, and anyone the Nazis decided didn't belong."
  },
  13: () => {
    // "It's called the Holocaust."
  },
  14: (c) => {
    // "And it's the reason the world still says: never again."
    put(c, SURVIVOR, 20, 0.6, 0, 1.95, [[1768, null, "sorrow"], [1838, null, "grief"]], { prop: "candle" });
  },
};

export const CH = makeChapter({
  total: TOTAL, shots: SHOTS, xfade: XFADE,
  cards: [{ a: 0, b: 60, kind: "chapter", lines: ["CHAPTER 10", "THE HOLOCAUST", "1933 – 1945"] }],
  cams: CAMS, dof: DOF, kicks: [], stage: STAGE,
});
