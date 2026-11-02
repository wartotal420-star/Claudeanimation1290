// Chapter 13: The End in the Pacific (1944-1945). Voice ~/ww2/voice/ch13.wav (137.89 s, 4137 frames), word frames from
// ch13_words.json. The atomic bomb shots (22-27) are SERIOUS: slow, quiet, no people hurt on screen, no jokes; the light
// only, then the empty riverbank, the lanterns and a stopped watch. Sets: c13_maproom, c13_leyte, c13_kamikaze, c13_iwo,
// front (Okinawa, Manchuria), c13_tokyo, c07_tokyoroom, warroom, c13_trinity, c13_city, c13_radio, c13_missouri.
import { makeChapter } from "../chapter";
import type { ChShot } from "../chapter";
import { D, Tr } from "../story";
import type { Key, Dof } from "../story";
import { P, W_, act, talk, toward, q, suit, SK, MEN, WOMEN, KIDS } from "../cast";
import type { Ctx, Beat } from "../cast";
import { MACARTHUR, TRUMAN, officer, sailor, navyOfficer, japanese, gi, codebreaker, soviet, pilot } from "../cast";
import { army, JP, SAILOR } from "../toon";
import type { Outfit, Expr, FrontOpts } from "../toon";

const TOTAL = 4137;
const JPNAVY = (i: number): [Outfit, string] => [{ ...SAILOR, jacket: "#ecebe4", pants: "#ecebe4", hat: "cap", cap: "#ecebe4", flaps: false, buttons: "#8a8a80", boots: "#3a2a1a",
  skin: ["#f5d3ac", "#ecc69b", "#f0cfa6"][i % 3], build: (["adult", "thin", "stout", "short"] as const)[i % 4], nose: (["button", "round", "long"] as const)[i % 3] }, `jn${i % 8}`];
const STARVE = (i: number): [Outfit, string] => [army(JP, i, { build: "thin", worn: true, stubble: true, haggard: true, patch: "#c8b878", jacket: "#a89a62", pants: "#988a52", bayonet: false }), `sv${i % 6}`];
/** Shigemitsu, the foreign minister, signed in a morning coat and top hat (with his cane) */
const SHIGEMITSU = suit("#1e1e24", { hat: "tophat", hatCol: "#141418", glasses: true, vest: "#3a3a40", tie: "#4a4a50", pattern: "pinstripe", patCol: "#3a3a46", build: "short",
  skin: "#f0cfa6", nose: "round", moustache: "#2a2420", stache: "plain", pocket: "#f4f0e6" });
const SCIENTIST = (i: number): [Outfit, string] => [{ ...codebreaker(i * 2)[0], hat: i % 2 ? "fedora" : "hair", hatCol: "#5a5450", glasses: true }, `sc${i}`];
const FAMILY: [Outfit, string][] = [
  [suit("#3a3a40", { hat: "hair", hair: "#1a1410", skin: "#f0cfa6", nose: "round", build: "thin", tie: "#2a2a30" }), "fa0"],
  [{ ...WOMEN[1], hat: "hair", hair: "#1a1410", dress: "#5a6a7a", dressPat: "check", jacket: "#5a6a7a", skin: "#f2d4b0", pearls: false, sashW: undefined }, "fa1"],
  [{ ...WOMEN[3], hat: "hair", hair: "#8a8a8a", dress: "#3a3040", dressPat: undefined, jacket: "#3a3040", skin: "#ecc69b", build: "short", pearls: false }, "fa2"],
  [{ ...KIDS[0], hat: "hair", hair: "#1a1410", skin: "#f2d4b0", cap: undefined, jacket: "#e8e4dc", freckles: false }, "fa3"],
  [{ ...KIDS[2], hair: "#1a1410", skin: "#f2d4b0", dress: "#c84a5a", jacket: "#c84a5a", freckles: false }, "fa4"],
];

const S = (id: number, a: number, b: number, set: string, light: ChShot["light"], night = false): ChShot => ({ id, a, b, set, light, night });
const SHOTS: ChShot[] = [
  S(1, 0, 248, "c13_maproom", "interior"), S(2, 248, 404, "c13_maproom", "interior"), S(3, 404, 456, "c13_maproom", "interior"), S(4, 456, 540, "c13_maproom", "interior"),
  S(5, 540, 736, "c13_leyte", "day"), S(6, 736, 892, "c13_leyte", "day"), S(7, 892, 954, "c13_leyte", "day"), S(8, 954, 1206, "c13_leyte", "day"),
  S(9, 1206, 1252, "c13_kamikaze", "golden"), S(10, 1252, 1294, "c13_leyte", "day"), S(11, 1294, 1402, "c13_leyte", "dusk"), S(12, 1402, 1503, "c13_kamikaze", "golden"),
  S(13, 1503, 1641, "c13_kamikaze", "golden"), S(14, 1641, 1694, "c13_kamikaze", "golden"), S(15, 1694, 1813, "c13_kamikaze", "golden"), S(16, 1813, 2023, "c13_iwo", "day"),
  S(17, 2023, 2112, "front", "dusk"), S(18, 2112, 2189, "c13_tokyo", "night", true), S(19, 2189, 2369, "c13_tokyo", "night", true), S(20, 2369, 2432, "c07_tokyoroom", "interior"),
  S(21, 2432, 2642, "warroom", "interior"), S(22, 2642, 2805, "c13_trinity", "night", true), S(23, 2805, 2841, "c13_trinity", "night", true),
  S(24, 2841, 2996, "c13_city", "day"), S(25, 2996, 3062, "c13_city", "day"), S(26, 3062, 3156, "c13_city", "dusk"), S(27, 3156, 3286, "c13_city", "dusk"),
  S(28, 3286, 3450, "front", "dusk"), S(29, 3450, 3592, "c13_radio", "interior"), S(30, 3592, 3656, "c13_radio", "interior"), S(31, 3656, 3771, "c13_radio", "interior"),
  S(32, 3771, 3987, "c13_missouri", "grey"), S(33, 3987, TOTAL, "c13_missouri", "grey"),
];
const XFADE: Record<number, number> = { 5: 10, 9: 8, 11: 12, 12: 10, 15: 16, 16: 10, 18: 10, 19: 16, 21: 8, 22: 14, 24: 20, 26: 30, 27: 24, 28: 14, 29: 16, 32: 12 };

const MR = "c13_maproom", LY = "c13_leyte", KZ = "c13_kamikaze", CT = "c13_city", MO = "c13_missouri", RD = "c13_radio";
const k1 = (f0: number, set: string, pos: [number, number, number], look: [number, number, number], fov = 42, rate = 0.002, roll = 0, punch = 0): Key => {
  const k = Math.min(1, 4 / Math.hypot(look[0] - pos[0], look[1] - pos[1], look[2] - pos[2]));
  return { f: f0, s: (f) => D(set, pos, look, f, f0, rate * k, { fov, roll }, punch * k) };
};
const cut = (k: Key): Key => ({ ...k, cut: true });
const glideTo = (k: Key, dur: number): Key => ({ ...k, dur });
const DZ = 30000;
const mx = (lon: number) => 2 - ((lon - 92) / 158) * 4, mz = (lat: number) => 0.215 + ((lat + 22) / 78) * 1.97;
// the hop: island list and the frame the marine lands on each (= the flag frame in c13_maproom.py)
const HOPS: [number, number, number][] = [[160.0, -9.6, 70], [172.9, 1.4, 110], [145.7, 15.2, 150], [144.8, 13.4, 185], [125.0, 11.0, 222], [141.3, 24.8, 300], [127.9, 26.5, 360]];
const hopAt = (f: number): [number, number, number] => {
  const p0: [number, number] = [mx(166), mz(-14)];
  let prev: [number, number] = p0, f0 = 40;
  for (const [lo, la, fl] of HOPS) {
    const cur: [number, number] = [mx(lo), mz(la)];
    if (f < fl) {
      const u = Math.max(0, Math.min(1, (f - (fl - 22)) / 22)), a = f < fl - 22 ? 0 : u;
      return [prev[0] + (cur[0] - prev[0]) * a, 0.952 + 0.12 * Math.sin(Math.PI * a), prev[1] + (cur[1] - prev[1]) * a];
    }
    prev = cur; f0 = fl;
  }
  return [prev[0], 0.952, prev[1]];
};

const CAMS: Record<number, Key[]> = {
  1: [k1(0, MR, [-0.4, 2.6, -1.6], [-0.2, 0.95, 1.6], 50, 0.0015), glideTo(k1(70, MR, [0.1, 1.5, 0.15], [0.3, 0.95, 0.85], 40, 0.0015), 40)],
  2: [{ f: 248, s: (f) => Tr(MR, [0.0, 1.35, 0.3], [0.2, 0.95, 1.0], f, 248, [0.0015, 0, 0.0012], { fov: 38 }) }],
  3: [k1(404, MR, [0.3, 1.15, 0.75], [0.5, 1.0, 1.35], 32, 0.004, 0.03, 0.01)],
  4: [k1(456, MR, [0.6, 1.75, -0.6], [0.6, 1.3, 2.8], 46, -0.002)],
  5: [{ f: 536, s: (f) => Tr(LY, [-900, 900, -4200], [-300, 0, -900], f, 536, [3.0, -0.6, 2.5], { fov: 42 }) }],
  6: [{ f: 736, s: (f) => Tr(LY, [-1400, 140, -2600], [-200, 20, -1400], f, 736, [4.0, 0, 1.0], { fov: 40 }) }],
  7: [k1(892, LY, [-6, 15.6, DZ - 8], [-12, 15.6, DZ - 3], 34, 0.003, 0.03, 0.006)],
  8: [k1(954, LY, [-160, 50, DZ - 220], [0, 12, DZ], 40, 0.0015), cut(k1(1084, LY, [-24, 15.6, DZ - 10], [-4, 16.5, DZ - 1], 46, 0.002))],
  9: [k1(1206, KZ, [24, 17.7, -6], [16, 17.6, -3], 40, 0.003, 0.02, 0.008)],
  10: [k1(1252, LY, [-6, 15.6, DZ - 8], [-12, 15.6, DZ - 3], 34, 0.002)],
  11: [k1(1294, LY, [-900, 70, DZ - 700], [0, 30, DZ], 38, -0.001)],
  12: [k1(1402, KZ, [-14, 17.2, -12], [-24, 20, -16], 46, 0.0015)],
  13: [k1(1503, KZ, [-10, 16.9, -11], [-500, 420, -560], 50, 0.0008), cut(k1(1580, KZ, [80, 4, -160], [-200, 160, -300], 46, 0.0008))],
  14: [k1(1641, KZ, [-16, 17.2, -9], [-24, 17.4, -13], 38, 0.002)],
  15: [k1(1690, KZ, [-120, 40, -180], [100, 80, -60], 46, 0.0006)],
  16: [k1(1809, "c13_iwo", [1.5, 2.6, -4], [-1, 1.4, 9], 46, 0.0015), glideTo(k1(1940, "c13_iwo", [-4, 3.0, -8], [-60, 40, 120], 48, 0.0012), 50)],
  17: [{ f: 2019, s: (f) => Tr("front", [2.5, 1.1, -1.5], [-2, 1.5, 12], f, 2019, [0, 0, 0.03], { fov: 42, roll: -0.02 }) }],
  18: [k1(2108, "c13_tokyo", [0, 60, -80], [0, 20, 500], 48, 0.0008)],
  19: [{ f: 2189, s: (f) => Tr("c13_tokyo", [-160, 26, -40], [40, 10, 400], f, 2189, [0.25, 0, 0.08], { fov: 46 }) }],
  20: [k1(2369, "c07_tokyoroom", [0, 1.7, -2.2], [0, 1.25, 2.8], 46, 0.002)],
  21: [k1(2428, "warroom", [0, 2.3, -1.2], [0, 1.0, 1.4], 46, 0.0015), glideTo(k1(2530, "warroom", [0.9, 1.6, -0.3], [0.2, 1.4, 2.4], 42, 0.0015), 40)],
  22: [k1(2638, "c13_trinity", [0.5, 1.6, -11], [0, 1.6, -3.5], 44, 0.0012), cut(k1(2740, "c13_trinity", [2.2, 1.7, -7.5], [0, 8, 900], 40, 0.0004))],
  23: [k1(2805, "c13_trinity", [-6, 1.5, -10], [0, 60, 900], 40, -0.0003)],
  24: [k1(2837, CT, [-3, 1.7, -8], [0, 10, 46], 44, 0.0008), cut(k1(2925, CT, [0, 1.6, -6], [-60, 1800, 300], 16, 0.0002))],
  25: [k1(2996, CT, [2, 1.8, -10], [0, 12, 46], 46, 0.0006)],
  26: [k1(3058, CT, [1.6, 1.1, 2.2], [1.2, 0.62, 3.2], 30, 0.002)],
  27: [k1(3152, CT, [-2, 1.6, -6], [0, 6, 40], 44, 0.0008)],
  28: [{ f: 3282, s: (f) => Tr("front", [2, 0.9, -2], [-3, 1.6, 14], f, 3282, [0, 0, 0.05], { fov: 44, roll: -0.03 }) }],
  29: [k1(3446, RD, [0, 1.25, -0.6], [0, 0.8, 2.8], 48, 0.0015)],
  30: [k1(3592, RD, [0.05, 0.95, 2.0], [0, 0.85, 3.2], 34, 0.002)],
  31: [k1(3656, RD, [0.9, 1.0, 3.0], [-0.2, 0.75, 1.8], 44, 0.0015)],
  32: [k1(3767, MO, [-3.5, 1.7, -4.5], [0.5, 1.4, 2.4], 46, 0.0015), cut(k1(3880, MO, [2.4, 1.6, -2.0], [3.6, 1.6, 1.0], 40, 0.002))],
  33: [k1(3987, MO, [0.5, 1.7, 3.5], [-200, 200, -1500], 50, -0.0008)],
};
const DOF: Dof[] = [
  { f: 0, cInf: 5 }, { f: 70, dur: 40, cInf: 12 }, { f: 248, cInf: 14 }, { f: 404, cInf: 16 }, { f: 456, cInf: 8 }, { f: 540, cInf: 1 }, { f: 892, cInf: 12 },
  { f: 954, cInf: 3 }, { f: 1084, cInf: 8 }, { f: 1206, cInf: 12 }, { f: 1252, cInf: 12 }, { f: 1294, cInf: 2 }, { f: 1402, cInf: 9 }, { f: 1503, cInf: 3 },
  { f: 1641, cInf: 12 }, { f: 1694, cInf: 2 }, { f: 1813, cInf: 7 }, { f: 1940, dur: 50, cInf: 3 }, { f: 2023, cInf: 6 }, { f: 2112, cInf: 1 }, { f: 2369, cInf: 8 },
  { f: 2432, cInf: 6 }, { f: 2530, dur: 40, cInf: 10 }, { f: 2642, cInf: 8 }, { f: 2740, cInf: 4 }, { f: 2805, cInf: 2 }, { f: 2841, cInf: 3 }, { f: 2925, cInf: 0 },
  { f: 2996, cInf: 2 }, { f: 3062, cInf: 16 }, { f: 3156, cInf: 5 }, { f: 3286, cInf: 6 }, { f: 3450, cInf: 8 }, { f: 3592, cInf: 14 }, { f: 3656, cInf: 10 },
  { f: 3771, cInf: 6 }, { f: 3880, cInf: 10 }, { f: 3987, cInf: 3 },
];
const KICKS: [number, number][] = [[70 / 30, 0.15], [110 / 30, 0.15], [150 / 30, 0.15], [185 / 30, 0.15], [222 / 30, 0.15], [300 / 30, 0.15], [360 / 30, 0.15], [1232 / 30, 0.4]];

type Who3 = [Outfit, string];
const put = (c: Ctx, w: Who3, i: number, x: number, y: number, z: number, beats: Beat[], extra: FrontOpts = {}, scale = 1, ri = 0.2) => {
  const a = act(c.t, beats, ri);
  P(c, W_(w[0], i, w[1]), x, y, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, ...extra }, scale);
};
const BYPASS: [number, number][] = [[152.2, -4.2], [151.8, 7.4], [134.5, 7.3], [171.2, 7.1]];
const marine = (c: Ctx, cheer = false) => {
  const [x, y, z] = hopAt(c.f), air = y > 0.96;
  put(c, gi(0), 1, x, y, z, [[0, air ? "armsUp" : cheer ? "cheer" : "hips", air ? "joy" : "determined"]], {}, 0.11, 0.05);
};
const starving = (c: Ctx, from = 0) => BYPASS.forEach(([lo, la], i) => put(c, STARVE(i), 2 + i, mx(lo) + 0.03, 0.952, mz(la) - 0.02, [[from, null, i % 2 ? "sad" : "exhausted"]], {}, 0.09));

const STAGE: Record<number, (c: Ctx) => void> = {
  1: (c) => { marine(c); starving(c); },
  2: (c) => {
    // "They skip the strongest islands ... letting the rest starve."
    marine(c); starving(c);
  },
  3: (c) => marine(c, true),
  4: (c) => {
    // "And every island is bloodier than the last." (no joke)
    marine(c);
    put(c, [MACARTHUR, "mac"], 10, 0.4, 0, 2.85, [[456, "cross", "grim"]]);
    put(c, navyOfficer(2), 11, 1.3, 0, 2.75, [[456, null, "grim"], [497, "chin", "sorrow"]]);
  },
  7: (c) => {
    // "Japan's plan is wild."
    put(c, officer("jp", 4), 20, -12, 14, DZ - 2.6, [[892, "chin", "scheme"], [922, "pointUp", "scheme"]]);
  },
  8: (c) => {
    // "...aircraft carriers, now with barely any planes or pilots left, sail out as bait, to lure the main American fleet away."
    put(c, JPNAVY(0), 21, -10, 14, DZ - 3, [[954, "wave", "grin"]], { wave: q(Math.sin(c.t * 7), 10) });
    put(c, JPNAVY(1), 22, -6, 14, DZ + 2, [[954, null, "nervous"], [1121, "armsUp", "grin"]], { prop: c.f > 1110 ? ["flag", "jp"] : null, flutter: q(c.t * 3, 6) });
    put(c, officer("jp", 4), 20, -2, 14, DZ - 4, [[954, "hips", "scheme"]], { prop: "binoc" });
  },
  9: (c) => {
    // "And it actually works." The American admiral takes the bait and charges north.
    put(c, navyOfficer(5), 23, 16, 16, -3, [[1206, "point", "grin"], [1232, "fist", "cheer"]], { facing: -1 });
    put(c, sailor(1), 24, 13.4, 16, -5.6, [[1206, null, "nervous"]]);
  },
  10: (c) => put(c, officer("jp", 4), 20, -12, 14, DZ - 2.6, [[1252, "shrug", "sad"]]),
  12: (c) => {
    // "It's also where Japan tries something new and terrible." (serious)
    put(c, sailor(3), 30, -21, 16 - 0.6, -15.0, [[1402, null, "grim"], [1460, null, "dread"]]);
    put(c, sailor(4), 31, -19, 16 - 0.6, -14.3, [[1402, null, "determined"]]);
  },
  13: (c) => {
    if (c.f < 1580) {
      put(c, sailor(5), 32, -12.5, 16, -8.5, [[1503, "pointUp", "fear"]], { facing: -1 });
      put(c, sailor(6), 33, -14.5, 16, -7.2, [[1503, null, "dread"]]);
    }
  },
  14: (c) => {
    // "They're called kamikazes."
    put(c, sailor(3), 30, -21.5, 16 - 0.6, -15.0, [[1641, null, "fear"]]);
    put(c, sailor(4), 31, -19.5, 16 - 0.6, -14.6, [[1641, null, "grim"]]);
  },
  16: (c) => {
    // "...on Iwo Jima, a tiny island covered in volcanic sand, almost every Japanese defender fights to the death."
    const sand = (x: number, z: number) => 1.2 * Math.max(0, Math.min(1, (32 - z) / 32)) - 0.25;
    put(c, gi(1), 40, -2.2, sand(-2.2, 5.5) - 0.3, 5.5, [[1813, null, "grim"]], { mode: "crouch" });
    put(c, gi(2), 41, 1.2, sand(1.2, 8.0) - 0.2, 8.0, [[1813, null, "exhausted"]], { mode: "kneel" });
    put(c, gi(3), 42, 3.5, sand(3.5, 6.5) - 0.2, 6.5, [[1813, null, "determined"], [1950, "point", "grim"]], { mode: "crouch", facing: -1 });
  },
  17: (c) => {
    // "On Okinawa, the battle lasts nearly three months."
    for (let i = 0; i < 4; i++) put(c, gi(i + 4), 50 + i, -1 + (i % 2) * 1.4, 0, 6 + i * 1.3 - 1.0 * (c.t - 2023 / 30), [[2023, null, (["exhausted", "grim", "exhausted", "determined"] as Expr[])[i]]],
      { mode: "march", phase: q((c.t * 1.4 + i * 0.3) % 1, 60), lift: 30 });
  },
  20: (c) => {
    // "But Japan still refuses to surrender."
    put(c, officer("jp", 6), 60, 0, 0, 2.95, [[2369, "cross", "stern"], [2404, "fist", "determined"]]);
    for (let i = 0; i < 2; i++) put(c, officer("jp", 7 + i), 61 + i, i ? 1.35 : -1.35, 0, 1.9, [[2369, "cross", "grim"]], { mode: "chair", chair: false });
  },
  21: (c) => {
    // "...planning an invasion of Japan itself that they expect to cost hundreds of thousands of lives on both sides."
    put(c, [TRUMAN, "tru"], 70, 0.3, 0, 2.7, [[2432, null, "grim"], [2550, "chin", "dread"]]);
    put(c, [MACARTHUR, "mac"], 10, -1.0, 0, 2.6, [[2432, "point", "determined"], [2560, null, "grim"]], { facing: 1 });
    put(c, navyOfficer(2), 11, 1.6, 0, 2.5, [[2432, "cross", "grim"]]);
  },
  22: (c) => {
    // "Then, in July 1945, in the New Mexico desert, scientists test a new kind of weapon." (serious)
    for (let i = 0; i < 4; i++) put(c, SCIENTIST(i), 80 + i, -2.4 + i * 1.6, 0, -5.2 + (i % 2) * 0.8, [[2642, null, (["worried", "grim", "dread", "worried"] as Expr[])[i]], [2795 + i * 2, "head", "fear"]]);
  },
  23: (c) => {
    for (let i = 0; i < 4; i++) put(c, SCIENTIST(i), 80 + i, -2.4 + i * 1.6, 0, -5.2 + (i % 2) * 0.8, [[2805, "head", (["fear", "dread", "grief", "dread"] as Expr[])[i]]]);
  },
  29: (c) => {
    // "On the fifteenth of August, the Japanese people hear something they have never heard before."
    const pos: [number, number][] = [[-0.9, 1.9], [0.6, 2.0], [-0.2, 1.5], [1.3, 1.6], [-1.5, 1.45]];
    FAMILY.forEach((w, i) => put(c, w, 90 + i, pos[i][0], 0.05, pos[i][1], [[3450, null, (["grim", "worried", "sorrow", "neutral", "worried"] as Expr[])[i]]], { mode: "kneel" }, i >= 3 ? 0.78 : 1));
  },
  30: () => { /* "The voice of their Emperor, on the radio." The radio close-up. */ },
  31: (c) => {
    // "He tells them that Japan will endure the unendurable and surrender."
    const pos: [number, number][] = [[-0.9, 1.9], [0.6, 2.0], [-0.2, 1.5], [1.3, 1.6], [-1.5, 1.45]];
    FAMILY.forEach((w, i) => put(c, w, 90 + i, pos[i][0], 0.05, pos[i][1], [[3656, null, (["grief", "sorrow", "grief", "sad", "sad"] as Expr[])[i]], [3726 + i * 4, i === 1 ? "cry" : null, i === 1 ? "grief" : undefined]], { mode: "kneel" }, i >= 3 ? 0.78 : 1));
  },
  32: (c) => {
    // "On the second of September 1945, Japan signs the surrender on board the battleship USS Missouri, in Tokyo Bay."
    put(c, [SHIGEMITSU, "shig"], 100, 0.4, 0, 1.3, [[3771, null, "grim"], [3860, null, "sorrow"]], { prop: c.f < 3860 ? "cane" : null });
    put(c, officer("jp", 9), 101, 3.2, 0, 1.0, [[3771, null, "grim"]]);
    put(c, JPNAVY(2), 102, 4.4, 0, 1.6, [[3771, null, "sorrow"]]);
    put(c, [MACARTHUR, "mac"], 10, -1.8, 0, 2.75, [[3771, null, "stern"]], { prop: "mic", expr: c.f > 3780 && c.f < 3850 ? talk(c.t, "stern", "shout") : "stern" });
    for (let i = 0; i < 5; i++) put(c, i % 2 ? officer("us", i) : navyOfficer(i), 103 + i, -5.5 + i * 0.75, 0, 4.2 + (i % 2) * 0.7, [[3771, "cross", "stern"]]);
    for (let i = 0; i < 7; i++) put(c, sailor(i), 110 + i, -8 + i * 2.1, 3.2, 7.3, [[3771, null, (["stern", "neutral", "grim", "neutral", "stern", "grin", "neutral"] as Expr[])[i]]]);
  },
  33: (c) => {
    // "After six years and one day, World War Two is over."
    for (let i = 0; i < 6; i++) put(c, sailor(i + 7), 120 + i, -3.5 + i * 1.3, 0, 1.2 + (i % 2) * 0.9, [[3987, null, "neutral"], [4084 + i * 2, i % 2 ? "cheer" : "wave", "joy"]], { wave: q(Math.sin(c.t * 6 + i), 10) });
  },
};

export const CH = makeChapter({
  total: TOTAL, shots: SHOTS, xfade: XFADE,
  cards: [{ a: 0, b: 60, kind: "chapter", lines: ["CHAPTER 13", "THE END IN THE PACIFIC", "1944 – 1945"] }],
  cams: CAMS, dof: DOF, kicks: KICKS, stage: STAGE,
});
