// Chapter 7: Pearl Harbor and the Pacific (1941-1943). Voice ~/ww2/voice/ch07.wav (199.69 s, 5991 frames), word frames
// from ch07_words.json. Sets: c07_maproom, c07_kido, c07_harbor, c07_usdeck, c07_capitol, c07_reich, c07_singapore,
// warroom (Churchill), c07_village, c07_tokyoroom, c07_codebreak, c07_guadal, jungle (Starvation Island).
// Set layouts and anchors are documented at the top of each ~/ww2/blender/sets/<set>.py.
import { makeChapter } from "../chapter";
import type { ChShot } from "../chapter";
import { D, Tr } from "../story";
import type { Key, Dof } from "../story";
import { P, W_, act, talk, toward, hh, q, suit, SK, MEN, WOMEN, WORKERS } from "../cast";
import type { Ctx, Beat } from "../cast";
import { TOJO_CAP, TOJO, ROOSEVELT, HITLER_WAR, CHURCHILL_BARE, officer, pilot, sailor, navyOfficer, japanese, tommy, gi, codebreaker } from "../cast";
import { army, JP, SAILOR } from "../toon";
import type { Outfit, Expr, Pose, FrontOpts } from "../toon";

const TOTAL = 5991;
// ---------------- cast for this chapter ----------------
const USOFF = suit("#2e3442", { hat: "fedora", hatCol: "#4a4a52", band: "#1e1e24", glasses: true, tie: "#8a2a2a", vest: "#4a4a52", watch: true, build: "thin", nose: "long",
  moustache: "#9a9a9a", stache: "pencil", brows: "#9a9a9a", skin: "#f8dcc4", pocket: "#f4f0e6", pattern: "pinstripe", patCol: "#4a5060" });
const JPNAVY = (i: number): [Outfit, string] => [{ ...SAILOR, jacket: "#ecebe4", pants: "#ecebe4", hat: "cap", cap: "#ecebe4", flaps: false, buttons: "#8a8a80", boots: "#3a2a1a",
  skin: ["#f5d3ac", "#ecc69b", "#f0cfa6"][i % 3], build: (["adult", "thin", "stout", "short"] as const)[i % 4], nose: (["button", "round", "long"] as const)[i % 3] }, `jn${i % 8}`];
const ROCHEFORT = suit("#7a2422", { hat: "hair", hair: "#3a2a1a", part: true, glasses: true, vest: "#2a2a30", tie: "#1e1e24", nose: "long", build: "thin", skin: "#f8dcc4",
  pocket: "#e8c45a", brows: "#3a2a1a", pattern: "check", patCol: "#5a1a18" });
const VILLAGER = (i: number): [Outfit, string] => {
  const w = i % 3 === 2;
  return [{ jacket: ["#3a4a6a", "#2a3a52", "#4a5a7a", "#5a4a3a"][i % 4], pants: ["#2a3448", "#3a3a3a", "#2a2a34"][i % 3], boots: "#3a2a1a", hat: i % 3 === 1 ? "flatcap" : "hair",
    cap: "#4a4038", hair: "#1a1410", skin: ["#f0cfa6", "#e8c49a", "#f2d4b0"][i % 3], build: (["thin", "adult", "short", "stout"] as const)[i % 4], dress: w ? "#3a5a8a" : undefined,
    nose: (["button", "round"] as const)[i % 2], moustache: i % 4 === 1 ? "#1a1410" : undefined, stache: "plain", rolled: true } as Outfit, `vl${i % 8}`];
};
const STARVE = (i: number): [Outfit, string] => [army(JP, i, { build: "thin", worn: true, stubble: true, haggard: true, patch: "#c8b878", jacket: "#a89a62", pants: "#988a52", bayonet: false }), `sv${i % 6}`];

// ---------------- shots ----------------
const S = (id: number, a: number, b: number, set: string, light: ChShot["light"], night = false): ChShot => ({ id, a, b, set, light, night });
const SHOTS: ChShot[] = [
  S(1, 0, 160, "c07_maproom", "interior"), S(2, 160, 240, "c07_maproom", "interior"), S(3, 240, 335, "c07_maproom", "interior"), S(4, 335, 495, "c07_maproom", "interior"),
  S(5, 495, 585, "c07_maproom", "interior"), S(6, 585, 697, "c07_maproom", "interior"), S(7, 697, 860, "c07_kido", "dusk"), S(8, 860, 940, "c07_harbor", "golden"),
  S(9, 940, 1115, "c07_harbor", "golden"), S(10, 1115, 1265, "c07_harbor", "golden"), S(11, 1265, 1378, "c07_usdeck", "day"), S(12, 1378, 1468, "c07_capitol", "interior"),
  S(13, 1468, 1575, "c07_reich", "interior"), S(14, 1575, 1640, "c07_reich", "interior"), S(15, 1640, 1838, "c07_reich", "interior"), S(16, 1838, 1938, "c07_maproom", "interior"),
  S(17, 1938, 2075, "c07_maproom", "interior"), S(18, 2075, 2195, "c07_singapore", "day"), S(19, 2195, 2305, "c07_singapore", "day"), S(20, 2305, 2415, "c07_singapore", "day"),
  S(21, 2415, 2540, "warroom", "interior"), S(22, 2540, 2700, "c07_usdeck", "grey"), S(23, 2700, 2890, "c07_usdeck", "grey"), S(24, 2890, 2968, "c07_usdeck", "grey"),
  S(25, 2968, 3090, "c07_usdeck", "grey"), S(26, 3090, 3185, "c07_usdeck", "grey"), S(27, 3185, 3418, "c07_village", "dusk"), S(28, 3418, 3500, "c07_village", "dusk"),
  S(29, 3500, 3600, "c07_tokyoroom", "interior"), S(30, 3600, 3665, "c07_tokyoroom", "interior"), S(31, 3665, 3795, "c07_tokyoroom", "interior"),
  S(32, 3795, 3962, "c07_codebreak", "interior"), S(33, 3962, 4098, "c07_codebreak", "interior"), S(34, 4098, 4230, "c07_codebreak", "interior"),
  S(35, 4230, 4272, "c07_codebreak", "interior"), S(36, 4272, 4385, "c07_codebreak", "interior"), S(37, 4385, 4524, "c07_codebreak", "interior"),
  S(38, 4524, 4548, "c07_codebreak", "interior"), S(39, 4548, 4675, "c07_usdeck", "day"), S(40, 4675, 4818, "c07_kido", "day"), S(41, 4818, 4938, "c07_kido", "day"),
  S(42, 4938, 5045, "c07_kido", "day"), S(43, 5045, 5225, "c07_guadal", "day"), S(44, 5225, 5268, "c07_guadal", "day"), S(45, 5268, 5330, "c07_guadal", "day"),
  S(46, 5330, 5465, "c07_guadal", "night", true), S(47, 5465, 5550, "c07_guadal", "day"), S(48, 5550, 5678, "c07_guadal", "gloom"), S(49, 5678, 5772, "jungle", "day"),
  S(50, 5772, 5885, "c07_guadal", "night", true), S(51, 5885, TOTAL, "c07_maproom", "interior"),
];
const XFADE: Record<number, number> = { 7: 10, 8: 8, 12: 8, 13: 8, 16: 8, 18: 8, 21: 8, 22: 8, 27: 8, 28: 14, 29: 8, 32: 8, 39: 8, 43: 10, 49: 10, 51: 10 };

// ---------------- cameras ----------------
const M = "c07_maproom", H = "c07_harbor", K = "c07_kido", U = "c07_usdeck", R = "c07_reich", SG = "c07_singapore", V = "c07_village", TK = "c07_tokyoroom",
  CB = "c07_codebreak", G = "c07_guadal";
/** dolly key; rate / punch are scaled so the camera travels about the same metres per second whatever the look distance */
const k1 = (f0: number, set: string, pos: [number, number, number], look: [number, number, number], fov = 42, rate = 0.002, roll = 0, punch = 0): Key => {
  const k = Math.min(1, 4 / Math.hypot(look[0] - pos[0], look[1] - pos[1], look[2] - pos[2]));
  return { f: f0, s: (f) => D(set, pos, look, f, f0, rate * k, { fov, roll }, punch * k) };
};
const cut = (k: Key): Key => ({ ...k, cut: true });
const glideTo = (k: Key, dur: number): Key => ({ ...k, dur });
const CAMS: Record<number, Key[]> = {
  1: [k1(0, M, [0.2, 2.7, -1.9], [0.5, 0.95, 1.7], 50, 0.0018), glideTo(k1(70, M, [1.45, 1.55, 0.3], [1.5, 1.3, 2.3], 42, 0.0022), 40)],
  2: [k1(160, M, [-0.15, 1.45, 0.45], [-0.4, 1.3, 2.3], 42, 0.003, 0.02, 0.006)],
  3: [k1(240, M, [0.85, 1.32, 0.8], [0.95, 1.32, 2.2], 40, 0.003, -0.02)],
  4: [k1(335, M, [1.2, 1.55, 0.55], [1.45, 1.3, 2.6], 44, 0.002), glideTo(k1(420, M, [1.35, 1.3, 0.1], [1.5, 0.95, 0.9], 40, 0.003), 36)],
  5: [k1(495, M, [1.3, 1.4, 0.75], [1.25, 1.55, 2.85], 40, 0.003, 0.03, 0.009)],
  6: [k1(585, M, [-0.95, 1.25, 0.55], [-0.75, 1.0, 1.4], 40, 0.003), glideTo(k1(640, M, [-0.6, 1.4, 0.4], [-0.3, 1.35, 2.6], 40, 0.002), 30)],
  7: [k1(690, K, [-6, 15.5, -10], [-50, 17.5, 3], 50, 0.0015, -0.02), cut(k1(772, K, [-16, 15.4, 5.5], [40, 17, -1], 46, 0.001))],
  8: [k1(856, H, [0.3, 2.3, -13.5], [-15, 13, 120], 52, 0.002)],
  9: [k1(940, H, [-0.5, 2.7, -14.5], [-40, 12, 80], 48, 0.002, 0.02), cut(k1(1030, H, [1.2, 2.4, -7.5], [-80, 9, 70], 46, 0.002, -0.02))],
  10: [k1(1115, H, [-895.2, 2.5, -35.2], [-897.6, 2.6, -29.6], 44, 0.0025)],
  11: [{ f: 1265, s: (f) => Tr(U, [170, 7, -140], [0, 14, 0], f, 1265, [-0.5, 0, 0.05], { fov: 40 }) }, cut(k1(1325, U, [20.5, 17.5, -7.5], [12, 17.3, -2], 46, 0.0015))],
  12: [k1(1374, "c07_capitol", [0.4, 1.6, -3.0], [0, 2.1, 4.6], 50, 0.0015), cut(k1(1430, "c07_capitol", [0.7, 2.9, 2.2], [0, 2.85, 4.75], 34, 0.003, 0, 0.006))],
  13: [k1(1464, R, [0.9, 1.6, 0.9], [0.6, 1.25, 3.6], 44, 0.0022), glideTo(k1(1530, R, [1.6, 1.6, 1.0], [1.8, 1.45, 3.4], 44, 0.002), 30)],
  14: [k1(1575, R, [-0.4, 1.45, 0.6], [-1.3, 1.35, 2.5], 40, 0.003, 0.02, 0.006)],
  15: [k1(1640, R, [-0.6, 1.55, 0.7], [-0.6, 1.4, 3.0], 46, -0.0025), glideTo(k1(1700, R, [0.6, 1.75, -1.8], [0.9, 1.35, 3.0], 48, 0.0012), 50)],
  16: [k1(1834, M, [0.55, 1.75, 0.15], [0.6, 0.95, 1.4], 48, 0.002)],
  17: [{ f: 1938, s: (f) => Tr(M, [1.05, 1.6, 0.05], [1.3, 0.95, 1.05], f, 1938, [0.0008, -0.0006, -0.0014], { fov: 44 }) }],
  18: [k1(2071, SG, [-6.5, 2.3, 5.0], [2, 5.0, 32], 52, 0.0015)],
  19: [k1(2195, SG, [-10, 2.4, 14], [-2, 2.0, -35], 46, 0.0015), cut(k1(2245, SG, [0.6, 1.45, -21.5], [0, 1.25, -40], 44, -0.0015))],
  20: [k1(2305, SG, [-1.5, 1.8, -10.6], [0, 1.3, -18], 46, 0.0018)],
  21: [k1(2411, "warroom", [0.6, 1.4, -0.2], [0.35, 1.55, 2.7], 42, 0.0025)],
  22: [k1(2536, U, [190, 9, -110], [0, 15, 0], 40, 0.0012), cut(k1(2604, U, [27, 19.5, -13], [-50, 16, 5], 48, 0.0012))],
  23: [k1(2700, U, [9.5, 17.5, -7.2], [16, 17.5, -4], 44, 0.002), cut(k1(2808, U, [70, 48, -55], [-40, 16, 0], 46, 0.0008))],
  24: [k1(2890, U, [11.4, 17.6, -6.4], [14, 17.6, -4.2], 34, 0.003, 0.03, 0.007)],
  25: [k1(2968, U, [28, 17.7, -14.5], [28, 17.5, -9], 46, 0.0018)],
  26: [k1(3090, U, [72, 18.0, -13], [0, 18.5, -4], 46, 0.001)],
  27: [k1(3185, V, [5, 1.7, -5], [13, 1.3, -15], 46, 0.0015), cut(k1(3345, V, [-1.5, 1.7, -4.5], [-5.5, 1.4, 4], 44, 0.002))],
  28: [k1(3414, V, [-12, 3.0, -16], [10, 4.5, 8], 46, 0.0012)],
  29: [k1(3500, TK, [0.2, 1.7, -0.9], [0, 1.45, 2.9], 46, 0.002)],
  30: [k1(3600, TK, [0.4, 1.6, 1.2], [2.8, 2.0, 5.8], 46, 0.002)],
  31: [k1(3665, TK, [0.1, 1.15, 0.5], [0, 1.4, 2.9], 40, 0.0025, 0.02), cut(k1(3750, TK, [0.05, 1.65, 0.9], [0, 1.75, 2.95], 36, 0.003, -0.03, 0.005))],
  32: [k1(3791, CB, [0.3, 1.75, -2.4], [0, 1.2, 3.6], 54, 0.0018), glideTo(k1(3890, CB, [0.3, 1.55, 0.6], [0, 1.45, 2.6], 44, 0.002), 34)],
  33: [k1(3962, CB, [-1.0, 1.55, 2.4], [-1.8, 1.6, 5.9], 46, 0.002)],
  34: [k1(4098, CB, [1.5, 1.55, 2.9], [2.5, 1.6, 5.9], 46, 0.002)],
  35: [k1(4230, CB, [0.2, 1.62, 3.3], [0.0, 1.6, 4.6], 32, 0.004, 0.03, 0.01)],
  36: [k1(4272, CB, [2.4, 1.35, 0.9], [3.9, 0.9, 2.0], 44, 0.002)],
  37: [k1(4385, CB, [2.2, 1.5, 0.6], [3.6, 1.2, 2.6], 46, 0.002)],
  38: [k1(4524, CB, [0.15, 1.62, 3.55], [0.0, 1.6, 4.6], 28, 0.006, -0.04, 0.012)],
  39: [k1(4544, U, [24, 17.5, -8], [12, 17.2, -2], 46, 0.0015)],
  40: [k1(4675, K, [-6, 14.9, -11], [-22, 60, 12], 62, 0.001), cut(k1(4757, K, [210, 45, -250], [-30, 14, 0], 40, 0.0015))],
  41: [k1(4818, K, [-520, 55, -720], [0, 30, 700], 40, 0.0008)],
  42: [k1(4938, K, [18.5, 15.5, -8.6], [10, 16.5, -2.5], 42, -0.0015)],
  43: [k1(5041, G, [0.5, 1.8, 19], [0, 1.5, 60], 50, 0.0015)],
  44: [k1(5225, G, [-1.5, 1.6, -27], [-5, 3.5, -38], 48, 0.002, 0.02)],
  45: [k1(5268, G, [3.0, 0.75, -0.6], [4.0, 0.35, 2.2], 44, 0.003)],
  46: [k1(5330, G, [1.5, 1.6, 16], [20, 6, 420], 50, 0.0012), cut(k1(5395, G, [4.2, 0.9, 5.0], [4.0, 0.6, -12], 50, 0.002))],
  47: [k1(5465, G, [-4, 0.9, 7.5], [30, 24, -2], 56, 0.001)],
  48: [k1(5550, G, [2.6, 0.75, -0.6], [4.0, 0.25, 2.3], 42, 0.0025, 0.02)],
  49: [k1(5674, "jungle", [1.2, 1.6, -1.2], [0, 1.3, 4.2], 44, 0.002)],
  50: [k1(5772, G, [7, 1.6, 17], [-4, 1.0, 30], 48, 0.0015)],
  51: [k1(5881, M, [1.25, 1.45, 0.9], [1.3, 1.5, 2.85], 40, 0.0025)],
};
const DOF: Dof[] = [
  { f: 0, cInf: 4 }, { f: 70, dur: 40, cInf: 9 }, { f: 160, cInf: 12 }, { f: 240, cInf: 13 }, { f: 335, cInf: 9 }, { f: 495, cInf: 12 }, { f: 585, cInf: 12 },
  { f: 697, cInf: 6 }, { f: 860, cInf: 3 }, { f: 940, cInf: 4 }, { f: 1030, cInf: 8 }, { f: 1115, cInf: 9 }, { f: 1265, cInf: 2 }, { f: 1325, cInf: 6 },
  { f: 1378, cInf: 6 }, { f: 1430, cInf: 12 }, { f: 1468, cInf: 9 }, { f: 1575, cInf: 12 }, { f: 1640, cInf: 8 }, { f: 1838, cInf: 9 }, { f: 1938, cInf: 11 },
  { f: 2075, cInf: 5 }, { f: 2195, cInf: 5 }, { f: 2245, cInf: 8 }, { f: 2305, cInf: 8 }, { f: 2415, cInf: 12 }, { f: 2540, cInf: 2 }, { f: 2604, cInf: 6 },
  { f: 2700, cInf: 10 }, { f: 2808, cInf: 2 }, { f: 2890, cInf: 14 }, { f: 2968, cInf: 9 }, { f: 3090, cInf: 5 }, { f: 3185, cInf: 6 }, { f: 3345, cInf: 8 },
  { f: 3418, cInf: 4 }, { f: 3500, cInf: 8 }, { f: 3600, cInf: 10 }, { f: 3665, cInf: 12 }, { f: 3795, cInf: 7 }, { f: 3962, cInf: 10 }, { f: 4230, cInf: 16 },
  { f: 4272, cInf: 10 }, { f: 4524, cInf: 16 }, { f: 4548, cInf: 7 }, { f: 4675, cInf: 4 }, { f: 4757, cInf: 2 }, { f: 4818, cInf: 1 }, { f: 4938, cInf: 6 },
  { f: 5045, cInf: 5 }, { f: 5225, cInf: 8 }, { f: 5268, cInf: 12 }, { f: 5330, cInf: 4 }, { f: 5395, cInf: 9 }, { f: 5465, cInf: 5 }, { f: 5550, cInf: 12 },
  { f: 5678, cInf: 10 }, { f: 5772, cInf: 7 }, { f: 5885, cInf: 12 },
];
const KICKS: [number, number][] = [[531 / 30, 0.7], [211 / 30, 0.3], [952 / 30, 0.6], [986 / 30, 0.5], [1020 / 30, 0.7], [1054 / 30, 0.5], [1088 / 30, 0.5], [1432 / 30, 0.3],
  [1599 / 30, 0.4], [1945 / 30, 0.25], [1969 / 30, 0.25], [1991 / 30, 0.25], [2017 / 30, 0.25], [2027 / 30, 0.25], [2037 / 30, 0.25], [3754 / 30, 0.7], [4529 / 30, 0.6],
  [4760 / 30, 1.0], [4786 / 30, 0.8], [4810 / 30, 0.8], [5350 / 30, 0.6], [5372 / 30, 0.5], [5394 / 30, 0.6], [5416 / 30, 0.5], [5438 / 30, 0.6]];

// ---------------- staging helpers ----------------
type Who3 = [Outfit, string];
const put = (c: Ctx, w: Who3, i: number, x: number, y: number, z: number, beats: Beat[], extra: FrontOpts = {}, scale = 1, ri = 0.18) => {
  const a = act(c.t, beats, ri);
  P(c, W_(w[0], i, w[1]), x, y, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, ...extra }, scale);
};
const tojo = (c: Ctx, x: number, z: number, beats: Beat[], extra: FrontOpts = {}) => put(c, [TOJO_CAP, "tojo"], 1, x, 0, z, beats, extra);
const jpoff = (c: Ctx, i: number, x: number, z: number, beats: Beat[], extra: FrontOpts = {}, y = 0) => put(c, officer("jp", i), 10 + i, x, y, z, beats, extra);
const speaking = (c: Ctx, f0: number, f1: number, a: Expr, b: Expr, base: Expr) => (c.f >= f0 && c.f < f1 ? talk(c.t, a, b) : base);

// mapping helpers for the map table (c07_maproom)
const mx = (lon: number) => 2 - ((lon - 92) / 158) * 4, mz = (lat: number) => 0.215 + ((lat + 22) / 78) * 1.97;

const STAGE: Record<number, (c: Ctx) => void> = {
  1: (c) => {
    tojo(c, 1.35, 2.85, [[0, "hips", "smug"], [100, "point", "scheme"], [140, "cross", "smug"]], { facing: 1 });
    jpoff(c, 0, 2.15, 2.7, [[0, "cross", "stern"], [121, "fist", "proud"]]);
    jpoff(c, 1, 0.2, 2.75, [[0, "chin", "stern"], [130, "hips", "smug"]]);
  },
  2: (c) => {
    // "To stop it, America cuts off Japan's oil": the official turns the valve shut
    put(c, [USOFF, "usoff"], 2, -0.42, 0, 2.7, [[160, "hips", "stern"], [196, "fists", "determined"], [238, "cross", "smug"]]);
  },
  3: (c) => {
    // "And Japan imports most of its oil from America": the gauge drops, Tojo's face drops with it
    tojo(c, 1.22, 2.75, [[240, "hips", "neutral"], [270, "collar", "nervous"], [298, "head", "panic"]]);
  },
  4: (c) => {
    // "...give up their empire, or take the oil they need by force, from the British and Dutch colonies"
    tojo(c, 1.3, 2.85, [[335, "chin", "worried"], [374, "shrug", "sad"], [401, "chin", "scheme"], [427, "point", "scheme"]], { facing: 1 });
    jpoff(c, 2, 2.1, 2.7, [[335, "cross", "stern"], [440, "point", "grin"]], { facing: 1 });
  },
  5: (c) => {
    // "They choose force."
    tojo(c, 1.25, 2.85, [[495, "chin", "scheme"], [526, "fist", "furious"], [560, "fists", "determined"]], {}, );
    jpoff(c, 0, 2.05, 3.05, [[495, null, "stern"], [532, "cheer", "yell"]]); jpoff(c, 1, 0.45, 3.05, [[495, null, "stern"], [534, "fist", "angry"]]);
  },
  6: (c) => {
    // "But first, they need to stop the American navy from getting in the way."
    tojo(c, -0.15, 2.85, [[585, "hips", "scheme"], [634, "point", "scheme"], [670, "fist", "determined"]], { facing: toward(c, -0.15, 2.85, mx(202), mz(21)) });
  },
  7: (c) => {
    // "On the seventh of December 1941, Japanese planes from six aircraft carriers attack..."
    if (c.f < 772) {
      put(c, JPNAVY(0), 20, -12.5, 14, -6.0, [[690, "wave", "cheer"]], { wave: q(Math.sin(c.t * 5), 10) });
      put(c, JPNAVY(1), 21, -15.5, 14, -2.0, [[690, "cheer", "joy"]]);
      put(c, pilot(3), 22, -16.5, 14, -8.5, [[690, "salute", "determined"]]);
      put(c, pilot(7), 23, -17.5, 14, -5.5, [[690, null, "grim"], [730, "salute", "determined"]]);
    } else {
      for (let i = 0; i < 5; i++) put(c, JPNAVY(i + 2), 24 + i, -8 + i * 2.6, 14, 3.2 + (i % 2) * 1.6, [[772, "wave", "cheer"]], { wave: q(Math.sin(c.t * 6 + i), 10) });
      put(c, officer("jp", 3), 30, 6, 14, 5.5, [[772, "hips", "proud"]]);
    }
  },
  8: (c) => {
    // "...the American navy base at Pearl Harbor, in Hawaii": a quiet Sunday morning, then the sky fills with planes
    put(c, sailor(0), 40, -1.6, 1.6, -9.5, [[860, null, "smile"], [902, "pointUp", "shock"]], { prop: c.f < 902 ? "news" : null, facing: -1 });
    put(c, sailor(1), 41, 1.4, 1.6, -8.8, [[860, "cross", "neutral"], [895, null, "gasp"], [915, "head", "fear"]]);
    put(c, sailor(2), 42, 3.2, 1.6, -5.0, [[860, null, "whistle"], [908, "palms", "shock"]], { look: 1 });
  },
  9: (c) => {
    // "In under two hours, they sink or damage eight battleships and kill more than two thousand Americans." (serious)
    if (c.f < 1030) {
      for (let i = 0; i < 5; i++) put(c, sailor(i + 3), 43 + i, -4.2 + i * 1.9, 1.6, -7 + (i % 2) * 2.2, [[940 + i * 4, i % 2 ? "head" : "pointUp", i % 2 ? "fear" : "shock"]], { facing: -1 });
    } else {
      put(c, sailor(8), 50, -0.6, 1.6, -3.4, [[1030, "head", "dread"], [1065, null, "grief"]]);
      put(c, sailor(9), 51, 1.0, 1.6, -2.6, [[1030, null, "fear"], [1075, "cry", "grief"]]);
      put(c, navyOfficer(1), 52, -2.2, 1.6, -1.8, [[1030, "point", "grim"], [1080, null, "sorrow"]], { facing: -1 });
    }
  },
  10: (c) => {
    // "But they miss something important. America's aircraft carriers aren't in the harbor that day."
    put(c, sailor(10), 53, -898.6, 1.6, -30.6, [[1115, "hips", "neutral"], [1150, "point", "scheme"], [1221, "shrug", "grin"], [1252, "palms", "smile"]], { facing: toward(c, -898.6, -30.6, -896, -29) });
  },
  11: (c) => {
    // "And in this new kind of war, carriers are what really matter."
    if (c.f >= 1325) {
      put(c, navyOfficer(0), 60, 14, 16, -3.5, [[1325, "hips", "proud"], [1347, "point", "smug"]], { facing: -1 });
      put(c, sailor(11), 61, 18, 16, -6.5, [[1325, "cross", "smile"]]);
      put(c, pilot(1), 62, 11, 16, 0.5, [[1325, null, "grin"], [1350, "salute", "proud"]]);
    }
  },
  12: (c) => {
    // "The next day, America declares war on Japan."
    put(c, [ROOSEVELT, "fdr"], 3, 0, 1.2, 4.75, [[1378, null, "determined"], [1419, "fist", "determined"]], { expr: speaking(c, 1383, 1460, "shout", "determined", "determined") });
    put(c, navyOfficer(2), 63, -1.1, 1.9, 6.4, [[1378, null, "stern"], [1440, "clap", "proud"]]);
    put(c, officer("us", 1), 64, 1.1, 1.9, 6.4, [[1378, "cross", "stern"], [1440, "clap", "proud"]]);
    if (c.f < 1430) for (let i = 0; i < 6; i++) {
      const v = (i * 5 + 3) % MEN.length, sx = i % 2 ? 1 : -1;
      put(c, [MEN[v], `m${v}`], 70 + i, sx * (1.9 + (i >> 1) * 1.2), 0, 0.8 + (i >> 1) * 0.7, [[1378, null, "stern"], [1432 + i * 2, "clap", "cheer"]]);
    }
  },
  13: (c) => {
    // "And a few days later, Hitler does something nobody asked him to do."
    put(c, [HITLER_WAR, "hitw"], 4, 0.6, 0, 3.55, [[1468, null, "smug"], [1530, null, "scheme"]], { mode: "chair", chair: false, prop: "news" });
    put(c, officer("de", 0), 80, 2.6, 0, 3.6, [[1468, "cross", "stern"], [1547, "palms", "worried"]], { facing: -1 });
    put(c, officer("de", 1), 81, 3.4, 0, 2.9, [[1468, null, "neutral"], [1550, "collar", "nervous"]]);
  },
  14: (c) => {
    // "He declares war on America."
    put(c, [HITLER_WAR, "hitw"], 4, -0.75, 0, 2.95, [[1575, "hips", "proud"], [1599, "point", "shout"]], { facing: toward(c, -0.75, 2.95, -1.5, 2.2) });
  },
  15: (c) => {
    // "He's now at war with the British Empire, the Soviet Union, and the biggest factory on Earth, all at the same time."
    put(c, [HITLER_WAR, "hitw"], 4, -0.75, 0, 2.95, [[1640, "hips", "proud"], [1700, "pointUp", "smug"], [1795, "hips", "proud"]]);
    put(c, officer("de", 0), 80, 1.4, 0, 3.6, [[1640, "cross", "stern"], [1686, "head", "shock"], [1760, "head", "dread"]]);
    put(c, officer("de", 1), 81, 2.4, 0, 3.0, [[1640, null, "neutral"], [1722, "collar", "panic"], [1790, "palms", "gasp"]]);
    const fall = Math.max(0, Math.min(1, (c.f - 1807) / 10));
    put(c, officer("de", 2), 82, 3.3, 0, 3.8, [[1640, "cross", "stern"], [1757, "head", "gasp"]], fall > 0 ? { mode: "fall", tilt: 80 * fall, expr: "dazed" } : {});
  },
  16: (c) => {
    // "For the next six months, Japan is unstoppable."
    tojo(c, 1.25, 2.85, [[1838, "hips", "smug"], [1899, "armsUp", "cheer"]]);
    jpoff(c, 2, 1.7, 2.75, [[1838, "cross", "smug"], [1907, "cheer", "laugh"]]);
  },
  17: (c) => {
    // "Hong Kong, the Philippines, Malaya, and the Dutch East Indies all fall."
    tojo(c, 1.3, 2.85, [[1938, "point", "scheme"], [1991, "fist", "proud"], [2037, "armsUp", "laugh"]], { facing: 1 });
  },
  18: (c) => {
    // "The British fortress of Singapore had huge guns pointing out to sea."
    put(c, officer("uk", 1), 90, -2.2, 0.27, 10.8, [[2075, null, "smug"], [2150, "point", "proud"]], { prop: c.f < 2150 ? "binoc" : null, facing: 1 });
    put(c, tommy(0), 91, -5.0, 0.27, 8.6, [[2075, "hips", "proud"]]);
    put(c, tommy(1), 92, -3.6, 0.27, 9.6, [[2075, "cross", "smug"]]);
    put(c, tommy(2), 93, 0.4, 0.27, 13.0, [[2075, null, "whistle"], [2163, "pointUp", "grin"]]);
  },
  19: (c) => {
    // "The Japanese came from the jungle behind it, on bicycles."
    if (c.f < 2245) {
      put(c, tommy(0), 91, -7.2, 0.27, 9.0, [[2195, "hips", "proud"]]); put(c, tommy(1), 92, -5.4, 0.27, 7.6, [[2195, "cross", "whistle"]]);
      put(c, officer("uk", 1), 90, -8.6, 0.27, 7.0, [[2195, null, "smug"]], { prop: "binoc" });
    }
    for (let k = 0; k < 6; k++) {
      const BX = [-4.5, -1.5, 1.5, 4.2, -3.0, 0.4][k], lag = [0, 1.6, 0.4, 2.2, 4.5, 5.2][k];
      const x = BX + 0.3 * Math.sin(c.f * 0.05 + k), z = -40 - lag + (4 * (c.f - 2195)) / 30;
      const j = japanese(k);
      put(c, j, 100 + k, x, 0.48, z, [[2195, null, k % 2 ? "grin" : "determined"]], { mode: "chair", chair: false });
    }
  },
  20: (c) => {
    // "More than eighty thousand British and Commonwealth soldiers surrender." (no jokes)
    put(c, officer("uk", 2), 110, -0.9, 0.27, -14.5, [[2305, null, "grim"]], { prop: ["flag", "white"], flutter: q(c.t * 2, 6) });
    put(c, officer("uk", 3), 111, 0.9, 0.27, -14.8, [[2305, null, "sorrow"]], { prop: ["flag", "uk"], flutter: q(c.t * 2 + 1, 6) });
    for (let i = 0; i < 6; i++) put(c, tommy(i + 3), 112 + i, -3 + (i % 3) * 1.4 + (i >= 3 ? 0.7 : 0), 0.27, -17 - (i >= 3 ? 1.6 : 0), [[2305, "armsUp", (["exhausted", "grim", "sorrow"] as Expr[])[i % 3]]]);
    for (let i = 0; i < 3; i++) put(c, japanese(i + 6), 120 + i, i % 2 ? 3.8 : -3.9, 0.27, -12.5 - i * 1.2, [[2305, null, "stern"]]);
  },
  21: (c) => {
    // "Churchill calls it the worst disaster in British military history."
    put(c, [CHURCHILL_BARE, "chb"], 5, 0.3, 0, 2.65, [[2415, null, "worried"], [2450, "head", "dread"]], { prop: c.f < 2450 ? "paper" : null });
  },
  22: (c) => {
    // "America needs some good news. So in April 1942, it tries something crazy."
    if (c.f >= 2604) {
      put(c, pilot(1), 130, 20.5, 16, -9.5, [[2604, "hips", "grin"], [2675, "pointUp", "scheme"]], { facing: -1 });
      put(c, sailor(12), 131, 22.5, 16, -11.2, [[2604, null, "nervous"], [2685, "head", "shock"]]);
    }
  },
  23: (c) => {
    // "Sixteen big army bombers... a ship they were never designed to take off from."
    if (c.f < 2808) put(c, pilot(5), 132, 14.2, 16, -4.4, [[2700, null, "neutral"], [2752, null, "nervous"], [2842, "collar", "worried"]]);
  },
  24: (c) => {
    // "And they definitely can't land back on it."
    put(c, pilot(5), 132, 14.2, 16, -4.4, [[2890, "collar", "nervous"], [2916, "palms", "panic"]]);
  },
  25: (c) => {
    // "The plan: take off, bomb Tokyo, and keep flying until you reach China."
    put(c, pilot(1), 130, 26.3, 16, -9.6, [[2968, "hips", "grin"], [2990, "point", "scheme"], [3031, "pointUp", "grin"], [3072, "shrug", "grin"]], { facing: 1, expr: speaking(c, 2973, 3080, "grin", "shout", "grin") });
    put(c, pilot(5), 132, 30.6, 16, -10.9, [[2968, null, "worried"], [3072, null, "shock"]], { mode: "chair", chair: false });
    put(c, pilot(9), 133, 25.4, 16, -11.0, [[2968, "cross", "nervous"], [3007, null, "gasp"], [3072, "head", "panic"]], { mode: "chair", chair: false });
  },
  26: (c) => {
    // "It's called the Doolittle Raid, after the pilot who leads it."
    for (let i = 0; i < 4; i++) put(c, sailor(13 + i), 134 + i, 62 - i * 3.0, 16, 2.5 + (i % 2) * 1.6, [[3090 + i * 3, "wave", "cheer"]], { wave: q(Math.sin(c.t * 6 + i), 10) });
  },
  27: (c) => {
    // "...most of the planes crash-land or run out of fuel over China, where Chinese villagers hide the crews."
    if (c.f < 3345) {
      put(c, pilot(1), 140, 10.3, 0, -11.8, [[3185, "head", "dazed"], [3260, "shrug", "exhausted"]]);
      put(c, pilot(9), 141, 12.6, 0, -12.8, [[3185, null, "dazed"], [3290, "palms", "worried"]]);
      put(c, VILLAGER(0), 142, 7.6, 0.05, -11.0, [[3185, null, "shock"], [3300, "wave", "determined"]], { facing: -1 });
    } else {
      const u = Math.min(1, (c.f - 3345) / 70);
      put(c, VILLAGER(1), 143, -5.2 + 0.3, 0.1, 3.1, [[3345, "wave", "determined"]], { facing: -1 });
      put(c, pilot(1), 140, -2.2 - 1.6 * u, 0.1, 1.6 + 1.2 * u, [[3345, null, "relief"]], { mode: u < 1 ? "stroll" : "stand", phase: q((c.t * 1.4) % 1, 60) });
      put(c, pilot(9), 141, -0.8 - 1.4 * u, 0.1, 1.2 + 1.0 * u, [[3345, null, "worried"]], { mode: u < 1 ? "stroll" : "stand", phase: q((c.t * 1.4 + 0.5) % 1, 60) });
      put(c, VILLAGER(2), 144, -7.2, 0.1, 2.5, [[3345, "pointUp", "worried"]]);
      put(c, VILLAGER(3), 145, 0.6, 0.1, 2.9, [[3345, null, "determined"], [3390, "wave", "determined"]], { facing: -1 });
    }
  },
  28: () => { /* "Japan takes a terrible revenge on those villages." The empty village at dusk, smoke rising. */ },
  29: (c) => {
    // "But in Tokyo, Japan's leaders are humiliated."
    tojo(c, 0, 2.95, [[3500, "cross", "furious"], [3566, "head", "dread"]]);
    for (let i = 0; i < 4; i++) jpoff(c, i + 3, i % 2 ? 1.35 : -1.35, 0.7 + (i >> 1) * 1.2, [[3500, null, (["nervous", "worried", "pained", "dread"] as Expr[])[i]], [3562 + i * 3, i % 2 ? "head" : "collar", "nervous"]], { mode: "chair", chair: false });
  },
  30: (c) => {
    // "America just bombed their capital."
    jpoff(c, 7, 2.2, 4.6, [[3600, "point", "shock"], [3638, "head", "panic"]], { facing: 1 });
  },
  31: (c) => {
    // "So they decide to wipe out what's left of the American navy, once and for all."
    tojo(c, 0, 2.95, [[3665, "point", "scheme"], [3688, "fist", "furious"], [3754, "fists", "yell"]]);
    jpoff(c, 3, -1.35, 2.2, [[3665, null, "stern"], [3756, "fist", "angry"]], { mode: "chair", chair: false });
    jpoff(c, 4, 1.35, 2.2, [[3665, null, "stern"], [3758, "fist", "determined"]], { mode: "chair", chair: false });
  },
  32: (c) => {
    // "But in an American basement in Hawaii, codebreakers have been reading parts of Japan's secret messages."
    put(c, [ROCHEFORT, "roch"], 6, 0, 0, 2.65, [[3795, "chin", "neutral"], [3887, null, "scheme"]], { prop: c.f > 3858 ? "paper" : null });
    put(c, codebreaker(0), 150, -2.4, 0, 1.35, [[3795, null, "exhausted"]], { mode: "chair", chair: false });
    put(c, codebreaker(1), 151, 2.4, 0, 1.15, [[3795, null, "worried"]], { mode: "chair", chair: false });
    put(c, codebreaker(2), 152, -3.4, 0, 3.0, [[3795, "chin", "neutral"]]);
  },
  33: (c) => {
    // "They know Japan is planning a big attack on a target called AF."
    put(c, [ROCHEFORT, "roch"], 6, -0.75, 0, 5.2, [[3962, "chin", "neutral"], [4025, "point", "scheme"], [4069, "point", "shock"]], { facing: toward(c, -0.75, 5.2, -2.2, 5.9) });
  },
  34: (c) => {
    // "They think AF is Midway, a tiny island in the middle of the Pacific."
    put(c, [ROCHEFORT, "roch"], 6, 3.75, 0, 5.15, [[4098, "chin", "scheme"], [4141, "point", "grin"]], { facing: toward(c, 3.75, 5.15, 2.25, 5.9) });
    put(c, codebreaker(3), 153, 1.1, 0, 4.7, [[4098, null, "worried"], [4166, "shrug", "nervous"]]);
  },
  35: (c) => put(c, [ROCHEFORT, "roch"], 6, 0.0, 0, 4.6, [[4230, "chin", "scheme"], [4243, "hips", "scheme"]]),
  36: (c) => {
    // "Midway sends out a fake message saying its water machine is broken."
    put(c, codebreaker(4), 154, 3.55, 0, 2.95, [[4272, null, "whistle"], [4342, "shrug", "smug"]], { mode: "chair", chair: false });
  },
  37: (c) => {
    // "A few days later, the Japanese send a message saying: AF is short of water."
    put(c, codebreaker(4), 154, 3.4, 0, 3.3, [[4385, "chin", "neutral"], [4474, "point", "shock"]], { facing: 1 });
    put(c, codebreaker(1), 151, 2.7, 0, 3.6, [[4385, null, "neutral"], [4491, "cheer", "beam"]]);
    put(c, [ROCHEFORT, "roch"], 6, 1.9, 0, 3.1, [[4385, "chin", "neutral"], [4506, "fist", "grin"]]);
  },
  38: (c) => put(c, [ROCHEFORT, "roch"], 6, 0.0, 0, 4.6, [[4524, "fist", "laugh"]]),
  39: (c) => {
    // "In June 1942, at the Battle of Midway, the Americans are waiting."
    put(c, pilot(13), 160, 14, 16, -6.5, [[4548, "cross", "determined"]]);
    put(c, pilot(17), 161, 17.5, 16, -3.5, [[4548, null, "smug"], [4653, "cross", "grin"]], { mode: "chair", chair: false });
    put(c, pilot(21), 162, 11.0, 16, -1.5, [[4548, "hips", "stern"]]);
    put(c, navyOfficer(3), 163, 20, 16, -8.5, [[4548, null, "stern"], [4640, "pointUp", "determined"]]);
  },
  40: (c) => {
    // "In about five minutes, American dive bombers set three Japanese carriers on fire."
    if (c.f < 4757) {
      put(c, JPNAVY(5), 170, -8.5, 14, -6.5, [[4675, null, "neutral"], [4700, "pointUp", "shock"], [4738, "head", "panic"]], { facing: -1 });
      put(c, JPNAVY(6), 171, -4.5, 14, -6.0, [[4675, null, "neutral"], [4713, "head", "fear"]]);
    }
  },
  41: () => { /* "By the end of the battle, Japan has lost four of its biggest carriers." Burning carriers on the horizon. */ },
  42: (c) => {
    // "Japan will never attack in the Pacific on this scale again."
    put(c, officer("jp", 5), 172, 14, 14, -5.2, [[4938, null, "grim"], [4990, null, "sorrow"]]);
    put(c, JPNAVY(7), 173, 16.5, 14, -3.4, [[4938, null, "exhausted"]]);
  },
  43: (c) => {
    // "Two months later, American Marines land on Guadalcanal..."
    for (let i = 0; i < 5; i++) {
      const u = Math.max(0, (c.f - 5045 - i * 12) / 30);
      put(c, gi(i), 180 + i, -5 + i * 2.6, 0, 27 - Math.min(9, u * 1.6), [[5045, null, (["determined", "grim", "stern", "determined", "nervous"] as Expr[])[i]]],
        { mode: "march", phase: q((c.t * 2 + i * 0.3) % 1, 60), lift: 50 });
    }
  },
  44: (c) => {
    // "They grab it in a day."
    for (let i = 0; i < 4; i++) put(c, gi(i + 5), 190 + i, -9 + i * 1.6, 0.06, -34 - (i % 2) * 1.2, [[5225 + i * 2, i % 2 ? "cheer" : "armsUp", "joy"]]);
  },
  45: (c) => {
    // "Keeping it takes six months."
    put(c, gi(9), 200, 3.4, -0.95, 2.4, [[5268, null, "joy"], [5292, null, "dazed"]]);
    put(c, gi(10), 201, 4.7, -0.95, 2.7, [[5268, "cheer", "grin"], [5301, null, "exhausted"]]);
  },
  46: (c) => {
    // "Every night, Japanese ships race in to drop off troops and shell the airfield."
    if (c.f >= 5395) {
      put(c, gi(9), 200, 3.3, -0.95, 1.9, [[5395, "head", "fear"]]);
      put(c, gi(10), 201, 4.8, -0.95, 1.6, [[5395, null, "dread"], [5433, "head", "fear"]]);
    }
  },
  47: (c) => {
    // "Every day, American planes chase them away."
    put(c, gi(9), 200, 3.4, -0.95, 2.3, [[5465, null, "exhausted"], [5492, "pointUp", "cheer"]], { facing: 1 });
    put(c, gi(10), 201, 4.7, -0.95, 2.7, [[5465, null, "dazed"], [5509, "armsUp", "joy"]]);
  },
  48: (c) => {
    // "And in between, both sides are fighting malaria, rain, and hunger."
    put(c, gi(10), 201, 4.0, -0.95, 2.5, [[5550, "collar", "exhausted"], [5614, "head", "pained"], [5651, "cross", "exhausted"]], { tilt: q(Math.sin(c.t * 18) * 2, 4) });
  },
  49: (c) => {
    // "Japanese soldiers start calling it Starvation Island."
    put(c, STARVE(0), 210, 0, 0, 4.0, [[5678, null, "exhausted"]]);
    put(c, STARVE(1), 211, 1.3, 0, 5.2, [[5678, null, "sad"], [5729, "collar", "exhausted"]]);
    put(c, STARVE(2), 212, -1.4, 0, 4.9, [[5678, null, "exhausted"]], { mode: "kneel" });
  },
  50: (c) => {
    // "In February 1943, Japan quietly pulls out."
    for (let i = 0; i < 5; i++) {
      const z = 21 + i * 1.6 + (c.f - 5772) * 0.03;
      put(c, japanese(i + 10), 220 + i, -6 + i * 1.8, 0, Math.min(30.5, z), [[5772, null, "nervous"]], { mode: "stroll", phase: q((c.t * 0.9 + i * 0.2) % 1, 60) });
    }
  },
  51: (c) => {
    // "From now on, Japan is on defense."
    tojo(c, 1.3, 2.85, [[5885, "collar", "nervous"], [5933, "palms", "worried"]]);
  },
};

export const CH = makeChapter({
  total: TOTAL, shots: SHOTS, xfade: XFADE,
  cards: [{ a: 0, b: 60, kind: "chapter", lines: ["CHAPTER 7", "PEARL HARBOR AND THE PACIFIC", "1941 – 1943"] }],
  cams: CAMS, dof: DOF, kicks: KICKS, stage: STAGE,
});
