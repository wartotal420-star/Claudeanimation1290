// Chapter 5: Britain Alone (1940-1941). Voice ~/ww2/voice/ch05.wav (92.08 s, 2762 frames), word frames from
// ch05_words.json. Sets (layouts documented at the top of each ~/ww2/blender/sets/<set>.py): c05_cabinet (Churchill's
// map room), c05_berghof (Hitler's great hall + map table with moving tokens), c05_sky (the Battle of Britain),
// c05_radar (Chain Home hut + masts), c05_airfield (scramble), c05_london (Blitz night / morning after), c05_tube
// (shelterers on the platform), c05_desert (Egypt: Italians, prisoners, Rommel), c05_oval (Roosevelt), c05_dock
// (Lend-Lease cargo).
import { makeChapter } from "../chapter";
import type { ChShot } from "../chapter";
import { D, Tr } from "../story";
import type { Key, Dof } from "../story";
import { P, F, W_, act, talk, toward, hh, q, stamp, mist, MEN, WOMEN, WORKERS, KIDS, crowd } from "../cast";
import type { Ctx, Beat } from "../cast";
import { CHURCHILL, HITLER_WAR, MUSSOLINI, ROMMEL, ROOSEVELT, officer, pilot, codebreaker, navyOfficer, warden, blitz, evacuee, italian, tommy, german, sailor } from "../cast";
import { fxBomber, fxBoom, fxRing, fxTracer, fxMuzzle, fxFlame } from "../toon";
import type { Outfit, Expr, Pose, FrontOpts, Pen } from "../toon";

const TOTAL = 2762;
const at = (f: number) => f / 30;

// ---------------- shots ----------------
const S = (id: number, a: number, b: number, set: string, light: ChShot["light"], night = false): ChShot => ({ id, a, b, set, light, night });
const CB = "c05_cabinet", BG = "c05_berghof", SK = "c05_sky", RD = "c05_radar", AF = "c05_airfield", LN = "c05_london", TB = "c05_tube", DS = "c05_desert",
  OV = "c05_oval", DK = "c05_dock";
const SHOTS: ChShot[] = [
  S(1, 0, 142, CB, "interior"), S(2, 142, 248, CB, "interior"), S(3, 248, 310, BG, "interior"), S(4, 310, 371, CB, "interior"),
  S(5, 371, 502, BG, "interior"), S(6, 502, 645, SK, "day"), S(7, 645, 752, RD, "day"), S(8, 752, 903, RD, "day"), S(9, 903, 980, AF, "day"),
  S(10, 980, 1035, SK, "day"), S(11, 1035, 1104, BG, "interior"), S(12, 1104, 1188, CB, "interior"), S(13, 1188, 1264, LN, "night", true),
  S(14, 1264, 1372, TB, "interior"), S(15, 1372, 1467, LN, "golden"), S(16, 1467, 1509, LN, "night", true), S(17, 1509, 1576, DS, "day"),
  S(18, 1576, 1660, DS, "day"), S(19, 1660, 1816, DS, "day"), S(20, 1816, 1913, BG, "interior"), S(21, 1913, 1985, BG, "interior"),
  S(22, 1985, 2086, BG, "interior"), S(23, 2086, 2157, DS, "day"), S(24, 2157, 2239, DS, "day"), S(25, 2239, 2284, DS, "day"), S(26, 2284, 2329, DS, "day"),
  S(27, 2329, 2425, OV, "interior"), S(28, 2425, 2497, OV, "interior"), S(29, 2497, 2596, DK, "day"), S(30, 2596, 2634, DK, "day"),
  S(31, 2634, 2680, DK, "day"), S(32, 2680, TOTAL, OV, "interior"),
];
const XFADE: Record<number, number> = { 3: 6, 6: 8, 7: 8, 9: 6, 13: 10, 14: 8, 15: 10, 17: 10, 20: 8, 23: 8, 27: 10, 29: 8, 32: 8 };

// ---------------- cameras ----------------
type V3 = [number, number, number];
const k1 = (f0: number, set: string, pos: V3, look: V3, fov = 42, rate = 0.002, roll = 0, punch = 0): Key => ({ f: f0, s: (f) => D(set, pos, look, f, f0, rate, { fov, roll }, punch) });
const tr = (f0: number, set: string, pos: V3, look: V3, v: V3, fov = 42, roll = 0): Key => ({ f: f0, s: (f) => Tr(set, pos, look, f, f0, v, { fov, roll }) });
const cut = (k: Key): Key => ({ ...k, cut: true });
const gl = (k: Key, dur: number): Key => ({ ...k, dur });
const VB = 2.4;           // formation speed in c05_sky (m / frame along -z)
const RZ = (f: number) => 9 + 10 * (1 - Math.min(1, Math.max(0, (f - 2086) / 45))) ** 2;   // Rommel's tank z (c05_desert)
const CAMS: Record<number, Key[]> = {
  1: [k1(0, CB, [0.9, 1.9, -1.6], [0, 1.4, 4.3], 48, 0.0022), gl(k1(80, CB, [-0.5, 1.5, 1.0], [0, 1.45, 4.3], 44, 0.0025), 50)],
  2: [k1(142, CB, [0.55, 1.0, 1.7], [0, 1.4, 4.3], 42, 0.003, 0.03), gl(k1(215, CB, [0.3, 1.05, 2.4], [0, 1.45, 4.3], 38, 0.003, 0.03, 0.01), 14)],
  3: [k1(244, BG, [-0.3, 1.5, 6.3], [0.8, 1.5, 8.0], 40, 0.003, -0.02)],
  4: [k1(310, CB, [0.3, 1.45, 2.2], [0, 1.45, 4.3], 36, 0.003, 0, 0.009)],
  5: [k1(371, BG, [0.8, 2.0, 8.0], [0, 1.3, 5.0], 42, 0.002), gl(k1(455, BG, [0.5, 1.4, 6.9], [0, 1.6, 4.9], 40, 0.003, 0.03), 24)],
  6: [tr(502, SK, [-13, -4, -34], [0, 2, 12], [0, 0, -VB], 46, 0.04), gl(tr(588, SK, [-26, -7, -12], [0, 5, 22], [0, 0, -VB], 50, -0.06), 30)],
  7: [k1(641, RD, [1.7, 1.45, -1.3], [0.2, 1.35, 1.8], 46, 0.0025), gl(k1(715, RD, [0.75, 1.5, 0.35], [0.05, 1.42, 2.0], 36, 0.004, 0, 0.008), 14)],
  8: [k1(752, RD, [30, 1.6, -40], [-110, 26, 30], 52, 0.0015), gl(k1(840, RD, [12, 2.2, -12], [-150, 60, 20], 46, 0.0015), 40)],
  9: [tr(903, AF, [2.8, 1.3, 0.2], [-0.5, 1.4, 8], [-0.03, 0, 0], 50, 0.02)],
  10: [k1(980, SK, [-10, 12, -175], [34, 0, -95], 46, 0.002)],
  11: [k1(1031, BG, [4.1, 1.55, 0.9], [4.6, 1.1, 3.3], 40, 0.003), gl(k1(1062, BG, [4.45, 1.75, 1.6], [4.6, 0.95, 3.1], 38, 0.003, 0.04, 0.01), 8)],
  12: [k1(1104, CB, [-1.1, 1.45, 1.4], [0, 1.45, 4.2], 44, 0.0025, -0.02)],
  13: [k1(1184, LN, [2.6, 1.3, 1.5], [-1.5, 6.5, 40], 52, 0.0015, 0.02)],
  14: [tr(1264, TB, [2.4, 1.35, -5.0], [-2.8, 0.6, 1.0], [0, 0, 0.032], 50, 0.02)],
  15: [k1(1368, LN, [3.2, 1.6, 3.0], [6.0, 1.4, 14], 50, 0.0015), gl(k1(1421, LN, [1.0, 1.5, 4.0], [5.4, 1.5, 11.5], 46, 0.002), 30)],
  16: [k1(1467, LN, [-1.8, 0.9, 9.0], [-9, 5.0, 24], 46, 0.004, -0.04, 0.008)],
  17: [k1(1505, DS, [0.35, 0.9, 3.3], [0, 1.75, 6.0], 40, 0.003, 0.03)],
  18: [k1(1576, DS, [2.5, 1.3, -3.5], [0, 1.7, 16], 50, 0.0018)],
  19: [k1(1660, DS, [-2.0, 1.6, 0.5], [3.0, 1.3, 20], 46, 0.0015), gl(k1(1760, DS, [-0.5, 2.6, -1.0], [4.0, 1.2, 26], 42, 0.0015), 30)],
  20: [k1(1812, BG, [0.15, 2.0, 5.05], [-0.25, 0.93, 6.35], 38, 0.002)],
  21: [k1(1913, BG, [0.45, 1.6, 7.4], [0, 1.55, 4.9], 36, 0.003, 0, 0.007)],
  22: [k1(1985, BG, [0.1, 2.3, 4.7], [-0.2, 0.93, 6.25], 44, 0.0018), gl(k1(2050, BG, [0.4, 1.9, 5.15], [0.0, 0.93, 6.1], 40, 0.002), 24)],
  23: [{ f: 2082, s: (f) => D(DS, [-1.6, 1.5, 2.6], [0.3, 2.5, RZ(f)], f, 2082, 0.002, { fov: 42 }) }],
  24: [k1(2157, DS, [7.5, 1.5, 11.5], [7, 2.6, 36], 50, 0.0015), gl(k1(2195, DS, [8.5, 1.3, 13.5], [7, 2.0, 30], 44, 0.003, 0.03, 0.008), 10)],
  25: [k1(2239, DS, [11.5, 1.55, 15.5], [10.5, 1.6, 20.5], 42, 0.003, -0.03)],
  26: [k1(2284, DS, [0.1, 2.6, 6.6], [0.35, 3.1, 10.15], 38, 0.004, 0, 0.008)],
  27: [k1(2325, OV, [0.4, 1.45, 1.4], [0, 1.25, 5.8], 42, 0.002)],
  28: [k1(2425, OV, [-1.1, 1.3, 3.2], [0, 1.25, 5.8], 40, 0.003, 0.02)],
  29: [k1(2493, DK, [3.5, 2.0, -7.0], [0.5, 6.0, 12], 56, 0.0015)],
  30: [k1(2596, DK, [4.4, 1.35, 0.4], [5.4, 1.1, 3.7], 40, 0.004, 0.02, 0.01)],
  31: [k1(2634, DK, [-1.0, 3.6, 1.2], [40, 6, 500], 40, 0.0015)],
  32: [k1(2676, OV, [0.2, 1.45, 3.4], [0, 1.35, 5.85], 34, 0.003, 0, 0.007)],
};
const DOF: Dof[] = [
  { f: 0, cInf: 5 }, { f: 142, cInf: 10 }, { f: 248, cInf: 9 }, { f: 310, cInf: 13 }, { f: 371, cInf: 7 }, { f: 502, cInf: 0 }, { f: 645, cInf: 10 },
  { f: 715, dur: 14, cInf: 14 }, { f: 752, cInf: 2 }, { f: 903, cInf: 6 }, { f: 980, cInf: 0 }, { f: 1035, cInf: 10 }, { f: 1104, cInf: 9 },
  { f: 1188, cInf: 4 }, { f: 1264, cInf: 9 }, { f: 1372, cInf: 5 }, { f: 1467, cInf: 8 }, { f: 1509, cInf: 12 }, { f: 1576, cInf: 4 },
  { f: 1660, cInf: 4 }, { f: 1816, cInf: 11 }, { f: 1913, cInf: 14 }, { f: 1985, cInf: 10 }, { f: 2086, cInf: 8 }, { f: 2157, cInf: 6 },
  { f: 2239, cInf: 10 }, { f: 2284, cInf: 13 }, { f: 2329, cInf: 8 }, { f: 2425, cInf: 10 }, { f: 2497, cInf: 3 }, { f: 2596, cInf: 12 },
  { f: 2634, cInf: 2 }, { f: 2680, cInf: 13 },
];
const KICKS: [number, number][] = [[at(222), 0.35], [at(338), 0.5], [at(1066), 0.45], [at(1211), 0.7], [at(1485), 0.5], [at(2195), 0.6], [at(2302), 0.35], [at(2612), 0.4]];

// ---------------- helpers ----------------
const docCard = (title: string, sub = "") => (p: Pen) => {
  const g = p.g; g.fillStyle = "#efe6cc"; g.fillRect(8, 8, 384, 504); g.strokeStyle = "#8a7a5a"; g.lineWidth = 4; g.strokeRect(8, 8, 384, 504);
  g.fillStyle = "#2a1e16"; g.textAlign = "center"; g.font = "bold 46px Georgia, serif";
  title.split("\n").forEach((l, i) => g.fillText(l, 200, 90 + i * 54));
  g.font = "26px Georgia, serif"; if (sub) g.fillText(sub, 200, 90 + title.split("\n").length * 54 + 10);
  g.strokeStyle = "#7a6a52"; g.lineWidth = 3; for (let k = 0; k < 8; k++) { g.beginPath(); g.moveTo(50, 260 + k * 28); g.lineTo(350 - (k % 3) * 40, 260 + k * 28); g.stroke(); }
};
const placard = (txt: string, bg: string, ink: string) => (p: Pen) => {
  const g = p.g; g.fillStyle = bg; g.fillRect(10, 10, 580, 180); g.strokeStyle = ink; g.lineWidth = 8; g.strokeRect(22, 22, 556, 156);
  g.fillStyle = ink; g.textAlign = "center"; g.textBaseline = "middle"; g.font = "bold 92px Georgia, serif"; g.fillText(txt, 300, 104);
};
const fo = (o: Partial<FrontOpts>): FrontOpts => ({ mode: "stand", ...o });
type Who = [Outfit, string];
const actor = (c: Ctx, w: Who, i: number, x: number, y: number, z: number, beats: Beat[], extra: Partial<FrontOpts> = {}, sc = 1, talkOn?: [number, number][]) => {
  const a = act(c.t, beats, 0.18); let expr = a.expr;
  if (talkOn) for (const [f0, f1] of talkOn) if (c.f >= f0 && c.f < f1) expr = talk(c.t, a.expr, "shout");
  P(c, W_(w[0], i, w[1]), x, y, z, fo({ expr, pose: a.pose, pk: a.pk, ...extra }), sc);
};
const WC: Who = [CHURCHILL, "churchill"], HI: Who = [HITLER_WAR, "hitlerw"], MU: Who = [MUSSOLINI, "mussolini"], RO: Who = [ROMMEL, "rommel"], FDR: Who = [ROOSEVELT, "fdr"];

// ---------------- staging ----------------
const cabinetStaff = (c: Ctx, cheer = false) => {
  const { t } = c;
  const staff: [Who, number, number, number, Partial<FrontOpts>, Beat[]][] = [
    [officer("uk", 1), -1.7, 0, 3.9, {}, [[0, "point", "stern"], [90, "cross", "stern"]]],
    [navyOfficer(0), 1.75, 0, 3.7, {}, [[0, "cross", "grim"], [120, "chin", "stern"]]],
    [codebreaker(1), -4.35, 0, 0.6, { mode: "chair", prop: "phone" }, [[0, null, "worried"]]],
    [codebreaker(3), 4.35, 0, -1.0, { mode: "chair" }, [[0, null, "neutral"]]],
    [officer("uk", 4), 2.5, 0, 1.0, { prop: "paper" }, [[0, null, "stern"]]],
    [codebreaker(5), -2.6, 0, 2.2, { prop: "paper" }, [[0, null, "neutral"]]],
  ];
  staff.forEach(([w, x, y, z, ex, b], i) => {
    const beats: Beat[] = cheer ? [[1104, i % 3 === 2 ? "clap" : i % 2 ? "cheer" : "fist", i % 2 ? "joy" : "grin"]] : b;
    const exx = cheer && ex.mode === "chair" ? { ...ex, prop: null } : ex;
    if (cheer && (i === 4 || i === 3)) return;
    actor(c, w, 300 + i, x, y, z, beats, { ...exx, facing: toward(c, x, z, 0, 4.3) }, 1);
  });
  void t;
};
const s1 = (c: Ctx) => {
  // "Britain has a new Prime Minister, Winston Churchill."
  actor(c, WC, 1, 0, 0, 4.3, [[0, "hips", "stern"], [113, "hips", "proud"], [126, "chin", "smug"]]);
  cabinetStaff(c);
};
const s2 = (c: Ctx) => {
  // "And Churchill has one very simple plan: never give up."
  actor(c, WC, 1, 0, 0, 4.3, [[142, "hips", "determined"], [192, "pointUp", "stern"], [222, "fist", "furious"], [232, "fists", "determined"]], {}, 1, [[222, 245]]);
  stamp(c.out, c.t, at(222), "NEVER\nGIVE UP", ...c.O(0.95, 2.35, 5.2), 1.3);
};
const s3 = (c: Ctx) => {
  // "Hitler expects Britain to make peace."
  actor(c, HI, 2, 0.8, 0, 8.0, [[248, null, "smug"], [276, null, "grin"], [297, "hips", "smug"]], { prop: "phone", look: c.f > 270 ? 1 : 0 });
  actor(c, officer("de", 2), 3, 2.6, 0, 7.4, [[248, "cross", "grim"]], { prop: null }, 1);
};
const s4 = (c: Ctx) => {
  // "Britain does not make peace."
  actor(c, WC, 1, 0, 0, 4.3, [[310, "cross", "stern"], [338, "fist", "furious"], [356, "fists", "determined"]], {}, 1, [[326, 368]]);
  stamp(c.out, c.t, at(338), "NO.", ...c.O(0.75, 2.25, 4.9), 0.85);
};
const s5 = (c: Ctx) => {
  // "So Hitler decides to invade. But first, he needs to control the sky."
  actor(c, HI, 2, 0, 0, 4.9, [[371, "hips", "scheme"], [406, "point", "shout"], [431, "chin", "scheme"], [462, "pointUp", "shout"], [479, "pointUp", "furious"]], { facing: 0 }, 1, [[388, 420], [450, 495]]);
  actor(c, officer("de", 0), 4, -1.5, 0, 5.1, [[371, "cross", "grim"], [440, "chin", "worried"]]);
  actor(c, german(3), 5, 1.6, 0, 5.0, [[371, null, "stern"]]);
};
const s6 = (c: Ctx) => {
  // waves of bombers; tracer from the diving Spitfires (cards travel with the formation)
  const u = c.f - 502;
  if (c.f > 600 && c.f < 640) for (let k = 0; k < 3; k++) {
    const v = (c.f - 600 + k * 5) % 12 / 12;
    F(c, { key: "tracer", cw: 400, ch: 40, draw: fxTracer, x: 20 - 30 * v - k * 6, y: 40 - 22 * v, z: -VB * u - 40 + 10 * v, w: 8, h: 0.8, rot: -0.6, glow: 2 });
  }
  for (let k = 0; k < 6; k++) F(c, { key: "bomber", cw: 600, ch: 200, draw: fxBomber, x: -200 + k * 70, y: 90 + (k % 2) * 25, z: 600 - VB * u + k * 40, w: 26, h: 9 });
};
const s7 = (c: Ctx) => {
  // "What they don't know is that Britain has a secret weapon: radar."
  actor(c, codebreaker(1), 10, 0.6, 0, 1.25, [[645, null, "neutral"], [675, "point", "determined"], [715, "point", "joy"]], { facing: toward(c, 0.6, 1.25, 0, 2.06) });
  actor(c, officer("uk", 3), 11, -0.9, 0, 0.1, [[645, "cross", "stern"], [701, "chin", "grim"], [731, "fist", "grin"]]);
  actor(c, codebreaker(4), 12, -1.75, 0, -1.35, [[645, null, "neutral"]], { mode: "chair", prop: "phone" });
};
const s8 = (c: Ctx) => {
  // "A chain of towers along the coast can see German planes coming before they even reach the shore."
  for (const [x, z] of [[-70, 6], [-150, 10], [-230, 14]] as [number, number][])
    for (let k = 0; k < 2; k++) {
      const u = ((c.t * 0.7 + k * 0.5 + x * 0.01) % 1 + 1) % 1;
      F(c, { key: `ring${q(u, 12)}`, cw: 600, ch: 600, draw: (p) => fxRing(p, q(u, 12)), x, y: 100, z, w: 70, h: 70, soft: true, opacity: 0.8, glow: 1.4 });
    }
  for (let k = 0; k < 7; k++) {
    const u = c.f - 752; F(c, { key: "bomber", cw: 600, ch: 200, draw: fxBomber, x: -260 + k * 40, y: 120 + (k % 3) * 15, z: 900 - u * 0.8 + (k % 2) * 30, w: 20, h: 7 });
  }
  actor(c, officer("uk", 2), 13, 22.6, 0.1, -36.2, [[752, null, "stern"], [818, null, "determined"]], { prop: "binoc" });
  actor(c, codebreaker(3), 14, 23.9, 0.1, -35.2, [[752, null, "neutral"], [804, "point", "determined"]], { facing: toward(c, 23.9, -35.2, -100, 10) });
};
const s9 = (c: Ctx) => {
  // "So British fighters are always waiting for them." the bell rings, the pilots run for the Spitfires
  for (let i = 0; i < 5; i++) {
    const [o, k] = pilot(i); const t0 = 908 + i * 6; const u = Math.max(0, c.f - t0);
    const x = 6.3 - i * 0.6 - u * 0.17, z = 5.6 + (i % 3) * 0.9;
    P(c, W_(o, 20 + i, k), x, 0, z, fo({ expr: i % 2 ? "determined" : "grim" }), 1, { so: { mode: c.f > t0 ? "run" : "stand", phase: q((c.t * 2.4 + i * 0.3) % 1, 30), stride: 1.2 }, mirror: true });
  }
  actor(c, [WORKERS[2], "k2"], 26, 5.5, 0, 4.9, [[903, "wave", "shout"]], {}, 1, [[903, 975]]);
  actor(c, [WORKERS[5], "k5"], 27, -4.2, 0, 11.0, [[903, "point", "shout"], [940, "wave", "determined"]], { facing: 1 });
};
const s10 = (c: Ctx) => { void c; };
const s11 = (c: Ctx) => {
  // "The Germans lose so many planes that Hitler quietly cancels the invasion."
  F(c, { key: "sealion", cw: 400, ch: 520, draw: docCard("OPERATION\nSEA LION", "invasion of Britain"), x: 4.6, y: 0.815, z: 3.0, w: 0.34, h: 0.44, flat: true, rot: Math.PI });
  stamp(c.out, c.t, at(1066), "CANCELLED", ...c.O(4.6, 0.82, 3.0), 0.42, true, Math.PI + 0.15);
  actor(c, HI, 2, 4.6, 0, 3.75, [[1035, "collar", "nervous"], [1050, "shrug", "worried"], [1066, "fist", "pained"], [1085, "head", "dazed"]], { look: c.f < 1062 ? (Math.floor(c.t * 2) % 2 ? 1 : -1) : 0 });
};
const s12 = (c: Ctx) => {
  // "It's the first time anybody has really stopped him."
  actor(c, WC, 1, 0, 0, 4.3, [[1104, "hips", "proud"], [1137, "fist", "smug"], [1166, "cheer", "grin"]]);
  cabinetStaff(c, true);
};
const beamCard = (p: Pen) => {
  const g = p.g, gr = g.createLinearGradient(0, 1000, 0, 0); gr.addColorStop(0, "rgba(220,230,255,0.85)"); gr.addColorStop(1, "rgba(200,215,255,0)");
  g.fillStyle = gr; g.beginPath(); g.moveTo(44, 1000); g.lineTo(56, 1000); g.lineTo(100, 0); g.lineTo(0, 0); g.closePath(); g.fill();
};
const beams = (c: Ctx, f0: number) => {
  for (let k = 0; k < 5; k++) {
    const a = 0.45 * Math.sin((c.f - f0) * 0.012 + k * 1.7) + (k - 2) * 0.12, L = 260;
    const bx = -120 + k * 70, bz = 260 + k * 40;
    F(c, { key: "beam", cw: 100, ch: 1000, draw: beamCard, x: bx - Math.sin(a) * L / 2, y: L / 2 * Math.cos(a) * 0.9, z: bz, w: 22, h: L, rot: a, soft: true, opacity: 0.55, glow: 1.6 });
  }
};
const s13 = (c: Ctx) => {
  // "Instead, he bombs British cities at night."
  const u = c.f - 1188; beams(c, 1188);
  for (let k = 0; k < 8; k++) F(c, { key: "bomber", cw: 600, ch: 200, draw: fxBomber, x: 40 - u * 0.35 - k * 11, y: 60 + (k % 3) * 8, z: 120 + k * 14, w: 11, h: 3.7 });
  if (c.f >= 1211) { const g = Math.min(1, (c.f - 1211) / 14); F(c, { key: `boom${q(g, 10)}`, cw: 600, ch: 600, draw: (p) => fxBoom(p, q(g, 10)), x: 14, y: 8, z: 70, w: 22, h: 22, glow: 2.5 }); }
  actor(c, warden(0), 30, 2.6, 0.14, 9.5, [[1188, null, "worried"], [1211, "pointUp", "fear"]], { facing: -1 }, 1, [[1215, 1255]]);
  actor(c, warden(1), 31, 3.6, 0.14, 11.5, [[1188, "wave", "shout"], [1236, "point", "fear"]], { facing: 1 });
  actor(c, blitz(2), 32, -2.5, 0, 14, [[1188, null, "fear"]], { mode: "run" });
};
const s14 = (c: Ctx) => {
  // "For eight months, Londoners sleep in underground train stations"
  const ppl: [Who, number, number, Partial<FrontOpts>, Expr][] = [
    [blitz(0), -2.2, -5.0, { mode: "sit" }, "sorrow"], [evacuee(0), -1.4, -4.5, { mode: "sit", blink: 1 }, "neutral"], [blitz(4), -1.5, -3.0, { pose: "palms" }, "joy"],
    [blitz(5), -2.6, -1.4, { mode: "sit", prop: "news" }, "neutral"], [evacuee(1), -1.0, -0.6, { mode: "sit", blink: 1 }, "neutral"], [blitz(7), -2.0, 0.6, { mode: "sit", pose: "hug" }, "sorrow"],
    [evacuee(2), -1.3, 1.0, { mode: "sit" }, "joy"], [blitz(8), -2.5, 2.4, { mode: "sit", blink: 1 }, "exhausted"], [warden(2), -0.9, 3.6, {}, "stern"],
    [blitz(10), -2.2, 4.8, { mode: "sit", prop: "news" }, "grim"], [blitz(11), -1.2, 6.2, { mode: "sit", blink: 1 }, "neutral"], [evacuee(3), -2.6, 7.0, { mode: "sit" }, "worried"],
    [blitz(13), -1.6, 8.6, { mode: "sit" }, "exhausted"], [blitz(14), -2.4, 10.4, { mode: "sit", blink: 1 }, "neutral"], [blitz(16), -1.0, 11.6, {}, "sorrow"],
  ];
  ppl.forEach(([w, x, z, ex, e], i) => {
    const sc = w[1].startsWith("ev") ? 0.72 : 1;
    P(c, W_(w[0], 40 + i, w[1]), x, 0, z, fo({ expr: e, ...ex, wave: ex.mode === "sit" ? undefined : q(Math.sin(c.t * 2 + i), 10) * 0 }), sc);
  });
};
const s15 = (c: Ctx) => {
  // "...then climb out every morning and go to work anyway."
  const u = (c.f - 1372) / 30;
  const walkers: [Who, number, number, number, Partial<FrontOpts>, Expr][] = [
    [[MEN[2], "m2"], 6.4, 13, 0.0, { prop: "umbrella" }, "determined"], [blitz(20), 6.0, 15, 0.4, { prop: "case" }, "grim"], [blitz(21), 6.6, 17, 0.8, {}, "determined"],
    [blitz(23), 5.8, 19.5, 1.2, { prop: "news" }, "neutral"], [[WORKERS[4], "k4"], 6.3, 21, 1.6, { prop: "crate" }, "joy"],
  ];
  walkers.forEach(([w, x, z0, d, ex, e], i) => {
    const k = Math.max(0, u - d), z = z0 - 1.25 * k, xx = x - (z0 - 12.5 > 0 ? 0 : 0);
    P(c, W_(w[0], 60 + i, w[1]), xx - Math.min(0.8, k * 0.3), 0.14, z, fo({ mode: "stroll", phase: q((c.t * 1.6 + i * 0.37) % 1, 40), expr: e, ...ex }));
  });
  // a city gent strolls past the rubble on the left; the milkman steps over the bricks
  P(c, W_(MEN[4], 66, "m4"), -6.0, 0.14, 26 - 1.0 * u, fo({ mode: "stroll", phase: q((c.t * 1.4) % 1, 40), expr: "smug", prop: "umbrella" }));
  actor(c, warden(3), 67, 4.6, 0, 9.0, [[1372, "wave", "joy"], [1421, "hips", "determined"]]);
};
const s16 = (c: Ctx) => {
  // "That's the Blitz."
  beams(c, 1467);
  actor(c, warden(1), 31, -4.4, 0, 17.0, [[1467, "point", "fear"], [1485, "head", "dread"]], { facing: -1 });
  actor(c, warden(4), 33, -3.2, 0, 15.6, [[1467, "fists", "grim"]], { facing: -1 });
  for (let k = 0; k < 3; k++) F(c, { key: "bomber", cw: 600, ch: 200, draw: fxBomber, x: -6 + k * 9 - (c.f - 1467) * 0.3, y: 40 + k * 5, z: 90 + k * 10, w: 9, h: 3 });
};
const s17 = (c: Ctx) => {
  // "Meanwhile, Mussolini wants a win of his own."
  actor(c, MU, 50, 0, 0, 6.0, [[1509, "hips", "proud"], [1543, "fists", "determined"], [1552, "cheer", "joy"]], {}, 1, [[1528, 1570]]);
  actor(c, italian(0), 51, -1.6, 0, 8.0, [[1509, null, "proud"]], { prop: ["flag", "it"], flutter: q(c.t % 1, 12) });
  actor(c, italian(1), 52, 1.7, 0, 8.3, [[1509, null, "smug"], [1552, "cheer", "joy"]]);
};
const s18 = (c: Ctx) => {
  // "He invades British-held Egypt with a huge army."
  const u = (c.f - 1576) / 30;
  for (let i = 0; i < 36; i++) {
    const [o, k] = italian(i + 3); const row = Math.floor(i / 6), col = i % 6;
    P(c, W_(o, 70 + i, k), -4.2 + col * 1.5 + (row % 2) * 0.4, 0, 9 + row * 2.0 - u * 1.1, fo({ mode: "march", phase: q((c.t * 1.9 + (i % 2) * 0.5) % 1, 40), expr: (["proud", "grin", "smug", "determined"] as Expr[])[i % 4], lift: 45 }));
  }
  actor(c, italian(1), 52, -5.6, 0, 7.5 - u * 1.1, [[1576, null, "proud"]], { prop: ["flag", "it"], flutter: q(c.t % 1, 12), mode: "march", phase: q((c.t * 1.9) % 1, 40) });
  actor(c, MU, 50, 6.2, 0, 6.5, [[1576, "point", "shout"], [1632, "cheer", "joy"]], { facing: -1 }, 1, [[1576, 1600]]);
};
const s19 = (c: Ctx) => {
  // "The British counterattack with a much smaller one, and capture over a hundred thousand Italian soldiers."
  const u = (c.f - 1660) / 30;
  const tm: [number, number][] = [[0.6, 6.0], [1.8, 6.6], [-0.4, 7.2]];
  tm.forEach(([x, z], i) => actor(c, tommy(i), 90 + i, x, 0, z, [[1660, null, "determined"], [1720, i === 1 ? "point" : null, "smug"], [1771, i === 0 ? "hips" : null, "grin"]], { facing: 1 }));
  for (let i = 0; i < 44; i++) {
    const [o, k] = italian(i + 40); const z = 9 + i * 1.25 - u * 0.9;
    if (z < 8.5) continue;
    P(c, W_(o, 100 + i, k), 3.2 + 0.35 * Math.sin(i * 1.7), 0, z, fo({ mode: "march", phase: q((c.t * 1.4 + i * 0.3) % 1, 40), pose: "armsUp", pk: 1, lift: 35,
      expr: (["sorrow", "worried", "dazed", "grin", "exhausted", "nervous"] as Expr[])[i % 6] }));
  }
  stamp(c.out, c.t, at(1771), "130,000\nPRISONERS", ...c.O(7.2, 4.4, 16), 4.2);
};
const s20 = (c: Ctx) => {
  // "Then he invades Greece. The Greeks push him back too." (the map tokens move in the set)
  F(c, { key: "itflagmap", cw: 600, ch: 400, draw: (p) => { const g = p.g; g.fillStyle = "#1d8a3c"; g.fillRect(0, 0, 200, 400); g.fillStyle = "#f4f1ea"; g.fillRect(200, 0, 200, 400); g.fillStyle = "#d2232e"; g.fillRect(400, 0, 200, 400); },
    x: 0.42, y: 0.99, z: 6.42, w: 0.09, h: 0.06 });
  void c;
};
const s21 = (c: Ctx) => {
  // "So Hitler has to keep rescuing his ally."
  actor(c, HI, 2, 0, 0, 4.9, [[1913, "shrug", "worried"], [1938, "head", "pained"], [1964, "head", "exhausted"]], {}, 1, [[1919, 1945]]);
};
const s22 = (c: Ctx) => {
  // "He sends troops into Greece and Yugoslavia, and sends a general named Erwin Rommel to North Africa."
  actor(c, HI, 2, 1.3, 0, 5.4, [[1985, "point", "shout"], [2058, "point", "scheme"]], { facing: toward(c, 1.3, 5.4, -0.3, 6.2) }, 1, [[1990, 2040]]);
};
const s23 = (c: Ctx) => {
  // Rommel arrives, waving from his turret
  actor(c, RO, 120, 0.35, 2.12, RZ(c.f) + 1.15, [[2086, null, "smug"], [2104, "wave", "grin"]], {}, 1);
};
const s24 = (c: Ctx) => {
  // "Rommel is so good at surprise attacks in the desert..." a British brew-up, then tanks over the dune
  const T0 = 2196;
  const brits: [number, number, Partial<FrontOpts>][] = [[9.2, 18.6, { mode: "sit" }], [10.8, 18.4, { mode: "sit" }], [9.8, 17.6, {}], [11.6, 19.4, {}]];
  brits.forEach(([x, z, ex], i) => {
    const late = c.f > T0 + i * 3;
    P(c, W_(tommy(i + 5)[0], 130 + i, tommy(i + 5)[1]), x, 0, z, fo({ ...(late ? { mode: "stand" } : ex), expr: late ? (["shock", "panic", "fear", "gasp"] as Expr[])[i] : (["joy", "grin", "smile", "neutral"] as Expr[])[i],
      pose: late ? (i % 2 ? "armsUp" : "head") : undefined, pk: 1 }));
  });
};
const s25 = (c: Ctx) => {
  // "...the British start calling him the Desert Fox."
  actor(c, tommy(9), 140, 10.2, 0, 20.4, [[2239, "point", "furious"], [2265, "fist", "angry"]], { facing: -1 }, 1, [[2245, 2280]]);
  actor(c, officer("uk", 6), 141, 11.4, 0, 21.2, [[2239, "cross", "grim"], [2258, "chin", "stern"]]);
  actor(c, tommy(11), 142, 9.2, 0, 21.6, [[2239, "head", "dread"]]);
};
const s26 = (c: Ctx) => {
  actor(c, RO, 120, 0.35, 2.12, RZ(c.f) + 1.15, [[2284, null, "smug"], [2302, "chin", "grin"]]);
  stamp(c.out, c.t, at(2302), "THE\nDESERT FOX", ...c.O(-0.9, 3.4, 10.5), 1.6);
};
const s27 = (c: Ctx) => {
  // "Across the ocean, America is officially staying out of the war."
  F(c, { key: "neutral", cw: 600, ch: 200, draw: placard("NEUTRAL", "#f0e8d0", "#1e2a5a"), x: 0.35, y: 0.86, z: 4.7, w: 0.42, h: 0.14 });
  actor(c, FDR, 150, 0, 0, 5.85, [[2329, null, "smug"], [2375, "shrug", "smug"], [2403, "palms", "grin"]], { mode: "chair" }, 1, [[2355, 2420]]);
};
const s28 = (c: Ctx) => {
  // "But President Franklin Roosevelt starts sending Britain weapons, food, and ships anyway..."
  actor(c, FDR, 150, 0, 0, 5.85, [[2425, null, "scheme"], [2468, "point", "grin"], [2497, null, "smug"]], { mode: "chair", prop: c.f < 2465 ? "paper" : null }, 1, [[2440, 2495]]);
  actor(c, officer("us", 2), 151, -1.6, 0, 5.4, [[2425, null, "stern"], [2468, "salute", "determined"]]);
};
const s29 = (c: Ctx) => {
  // "...and lets them pay later." loading the ship
  const crew: [Who, number, number, Pose | null, Expr][] = [[[WORKERS[0], "k0"], -2.0, 1.5, "pointUp", "shout"], [[WORKERS[3], "k3"], 1.2, 2.0, "wave", "grin"],
    [[WORKERS[7], "k7"], 3.6, 0.2, null, "determined"], [sailor(1), -3.2, 5.6, "point", "stern"], [[WORKERS[9], "k9"], 6.5, 2.4, "fists", "determined"]];
  crew.forEach(([w, x, z, p, e], i) => actor(c, w, 160 + i, x, 0, z, [[2497, p, e]], { prop: i === 2 ? "crate" : i === 0 ? null : null }, 1, i === 0 ? [[2500, 2560]] : undefined));
  actor(c, officer("us", 4), 166, -0.6, 0, -0.6, [[2497, null, "stern"], [2574, "point", "grin"]], { prop: c.f < 2570 ? "paper" : null });
};
const s30 = (c: Ctx) => {
  // "It's called Lend-Lease."
  stamp(c.out, c.t, at(2612), "LEND-LEASE", ...c.O(5.45, 0.95, 3.6), 1.5);
  actor(c, [WORKERS[6], "k6"], 170, 4.0, 0, 3.1, [[2596, "pointUp", "grin"], [2612, "fist", "joy"]], { facing: -1 });
};
const s31 = (c: Ctx) => {
  // "America isn't fighting yet." the convoy sails
  actor(c, sailor(3), 175, -2.2, 0, 6.4, [[2634, "wave", "joy"]]);
  actor(c, evacuee(4), 176, -1.3, 0, 6.6, [[2634, "wave", "joy"]], {}, 0.72);
};
const s32 = (c: Ctx) => {
  // "But it's definitely picked a side."
  actor(c, FDR, 150, 0, 0, 5.85, [[2680, null, "smug"], [2707, null, "grin"]], { mode: "chair", prop: ["flag", "uk"], flutter: q(c.t % 1, 12), blink: c.f > 2712 && c.f < 2726 ? 1 : 0 });
};
const STAGE: Record<number, (c: Ctx) => void> = { 1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6, 7: s7, 8: s8, 9: s9, 10: s10, 11: s11, 12: s12, 13: s13, 14: s14, 15: s15,
  16: s16, 17: s17, 18: s18, 19: s19, 20: s20, 21: s21, 22: s22, 23: s23, 24: s24, 25: s25, 26: s26, 27: s27, 28: s28, 29: s29, 30: s30, 31: s31, 32: s32 };
void mist; void hh; void fxMuzzle; void fxFlame; void crowd; void KIDS;

export const CH = makeChapter({
  total: TOTAL, shots: SHOTS, xfade: XFADE,
  cards: [{ a: 0, b: 60, kind: "chapter", lines: ["CHAPTER 5", "BRITAIN ALONE", "1940 – 1941"] }],
  cams: CAMS, dof: DOF, kicks: KICKS, stage: STAGE,
});
