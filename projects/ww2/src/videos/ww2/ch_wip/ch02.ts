// Chapter 2 "Everyone Grabs Something" (1931-1938): ~/ww2/voice/ch02.wav (4110 f). Sets: c02_maproom (the map table +
// Hitler's desk), c02_manchuria (night railway), c02_league (Geneva), c02_china (column, Nanjing at dusk, mountain road),
// c02_rome (balcony), c02_ethiopia, c02_rhine (Cologne bridge), c04_maginot (fort interior), c02_munich, c02_airfield.
// Frames below are chapter-local word starts (s * 30) from ch02_words.json.
import { makeChapter } from "../chapter";
import type { ChShot } from "../chapter";
import { D, Tr, clamp01, smooth } from "../story";
import type { Key, Dof } from "../story";
import {
  P, F, W_, act, talk, toward, at, hh, q, crowd, mist, stamp, suit, SK, MEN, WOMEN, WORKERS, HITLER,
  MUSSOLINI, CHAMBERLAIN, CHAMBERLAIN_HAT, TOJO_CAP, officer, japanese, chinese, italian, german, french,
} from "../cast";
import type { Ctx, Beat } from "../cast";
import { fxBoom, fxStamp, INK } from "../toon";
import type { Outfit, Pen, Expr, Pose, FrontOpts } from "../toon";

const S = {
  map: "c02_maproom", man: "c02_manchuria", lg: "c02_league", cn: "c02_china", rome: "c02_rome", eth: "c02_ethiopia",
  rh: "c02_rhine", mg: "c04_maginot", mu: "c02_munich", af: "c02_airfield",
};
const SHOTS: ChShot[] = [
  { id: 1, a: 0, b: 150, set: S.map, light: "interior" },          // card; the three grabbers at the map
  { id: 2, a: 150, b: 352, set: S.map, light: "interior" },        // Japan: no oil, iron, rubber
  { id: 3, a: 352, b: 500, set: S.man, light: "night", night: true }, // officers blow up their own railway
  { id: 4, a: 500, b: 603, set: S.man, light: "night", night: true }, // blame the Chinese
  { id: 5, a: 603, b: 657, set: S.map, light: "interior" },        // take the whole region (Manchuria tile)
  { id: 6, a: 657, b: 818, set: S.lg, light: "interior" },         // the League, outraged
  { id: 7, a: 818, b: 890, set: S.lg, light: "interior" },         // a very strongly worded report
  { id: 8, a: 890, b: 958, set: S.lg, light: "interior" },         // Japan leaves the group chat
  { id: 9, a: 958, b: 1066, set: S.cn, light: "day" },             // 1937: Japan invades the rest of China
  { id: 10, a: 1066, b: 1179, set: S.cn, light: "day" },           // generals expect a few months
  { id: 11, a: 1179, b: 1214, set: S.cn, light: "day" },           // it lasts eight years
  { id: 12, a: 1214, b: 1367, set: S.cn, light: "dusk" },          // Nanjing (serious)
  { id: 13, a: 1367, b: 1490, set: S.cn, light: "dusk" },          // six weeks (serious)
  { id: 14, a: 1490, b: 1631, set: S.cn, light: "dusk" },          // tens of thousands (serious)
  { id: 15, a: 1631, b: 1733, set: S.cn, light: "day" },           // the government retreats and keeps fighting
  { id: 16, a: 1733, b: 1814, set: S.cn, light: "day" },           // that matters
  { id: 17, a: 1814, b: 2027, set: S.map, light: "interior" },     // a million soldiers stuck in China
  { id: 18, a: 2027, b: 2120, set: S.rome, light: "day" },         // Mussolini
  { id: 19, a: 2120, b: 2201, set: S.rome, light: "day" },         // the Roman Empire
  { id: 20, a: 2201, b: 2362, set: S.eth, light: "day" },          // 1935: Ethiopia
  { id: 21, a: 2362, b: 2432, set: S.lg, light: "interior" },      // outraged again
  { id: 22, a: 2432, b: 2512, set: S.lg, light: "interior" },      // does basically nothing
  { id: 23, a: 2512, b: 2611, set: S.map, light: "interior" },     // Hitler watching on a tiny TV
  { id: 24, a: 2611, b: 2677, set: S.map, light: "interior" },     // nobody is going to stop him
  { id: 25, a: 2677, b: 2869, set: S.rh, light: "golden" },        // 1936: the Rhineland
  { id: 26, a: 2869, b: 2919, set: S.rh, light: "golden" },        // his generals are terrified
  { id: 27, a: 2919, b: 3020, set: S.rh, light: "golden" },        // orders: turn around
  { id: 28, a: 3020, b: 3098, set: S.mg, light: "interior" },      // the French army does not fight back
  { id: 29, a: 3098, b: 3235, set: S.map, light: "interior" },     // Austria swallowed
  { id: 30, a: 3235, b: 3342, set: S.map, light: "interior" },     // the Sudetenland demanded
  { id: 31, a: 3342, b: 3437, set: S.mu, light: "interior" },      // Britain and France really don't want war
  { id: 32, a: 3437, b: 3540, set: S.mu, light: "interior" },      // Munich: the deal
  { id: 33, a: 3540, b: 3638, set: S.mu, light: "interior" },      // that's all he wants
  { id: 34, a: 3638, b: 3760, set: S.af, light: "grey" },          // Chamberlain flies home waving the paper
  { id: 35, a: 3760, b: 3844, set: S.af, light: "grey" },          // peace for our time
  { id: 36, a: 3844, b: 3951, set: S.map, light: "interior" },     // six months later: the rest of Czechoslovakia
  { id: 37, a: 3951, b: 4110, set: S.af, light: "grey" },          // a gym membership in January
];
const TOTAL = 4110;

// ---------------- extra cast (built only from existing Outfit fields) ----------------
const MATSUOKA = suit("#26262e", { hat: "hair", hair: "#1e1a18", part: true, glasses: true, moustache: "#1e1a18", stache: "pencil", skin: "#f2d0a8", build: "stout",
  tie: "#5a2a2a", pocket: "#f4f0e6", nose: "round", brows: "#1e1a18" });
const LYTTON = suit("#4a4038", { hat: "bald", hair: "#e4e4ea", tufts: true, moustache: "#e8e8e8", stache: "walrus", bushy: true, brows: "#e8e8e8", build: "thin", nose: "long",
  vest: "#6a5a3a", watch: true, glasses: true, bowtie: "#2a4a7a", pattern: "check", patCol: "#2e261e", skin: "#fbe4cc" });
const KOO = suit("#2a3a4a", { hat: "hair", hair: "#1e1a18", part: true, skin: "#f2d0a8", tie: "#2a4a6a", build: "thin", nose: "button", pocket: "#f4f0e6" });
const DALADIER = suit("#33333c", { hat: "hair", hair: "#3a2a1e", part: true, build: "stout", nose: "round", tie: "#5a2a2a", vest: "#33333c", watch: true, skin: "#f2d0b4",
  brows: "#3a2a1e", bushy: true, jowls: true, pocket: "#f4f0e6" } as Partial<Outfit>);
const SELASSIE: Outfit = { jacket: "#3a3a2a", pants: "#3a3a2a", boots: "#2a1e14", tallBoots: true, coat: "#1e1c22", hat: "hair", hair: "#1e1a18", moustache: "#1e1a18", stache: "plain",
  stubble: true, skin: "#8a5a38", build: "thin", nose: "long", tunic: true, buttons: "#e8c45a", medals: 4, brows: "#1e1a18" } as Outfit;
const WARRIOR = (i: number): [Outfit, string] => [{ jacket: "#f2ece0", pants: "#e8e2d4", boots: "#5a3a22", hat: "hair", hair: "#1e1a18", skin: ["#7a4a2a", "#8a5a38", "#6a4028"][i % 3],
  rifle: i % 2 === 0, scarf: ["#c8202a", "#2a8a3a", "#e8c040"][i % 3], build: (["thin", "adult", "stout"] as const)[i % 3], nose: (["long", "round", "button"] as const)[i % 3],
  moustache: i % 2 ? "#1e1a18" : undefined, stubble: i % 3 === 1, buttons: "#c8a24a" } as Outfit, `eth${i % 6}`];

// ---------------- custom effect cards ----------------
const rr = (p: Pen, x0: number, y0: number, x1: number, y1: number, r: number, fill: string | null, ol = 0) => {
  const pts: [number, number][] = [];
  for (const [cx, cy, a] of [[x1 - r, y0 + r, -90], [x1 - r, y1 - r, 0], [x0 + r, y1 - r, 90], [x0 + r, y0 + r, 180]])
    for (let i = 0; i <= 8; i++) pts.push([cx + r * Math.cos(((a + (90 * i) / 8) * Math.PI) / 180), cy + r * Math.sin(((a + (90 * i) / 8) * Math.PI) / 180)]);
  p.poly(pts, fill, ol);
};
const words = (p: Pen, s: string, x: number, y: number, px: number, col: string, font = "bold", fam = "Georgia, serif", align: CanvasTextAlign = "center") => {
  const g = p.g; g.fillStyle = col; g.font = `${font} ${px}px ${fam}`; g.textAlign = align; g.textBaseline = "middle"; g.fillText(s, x, y);
};
/** group-chat system message pill on a 1000 x 200 canvas */
const fxChat = (p: Pen, text: string) => {
  rr(p, 20, 30, 980, 170, 70, "rgba(20,26,30,0.82)", 0);
  words(p, text, 500, 100, 54, "#f4f4f0", "bold", "Arial, Helvetica, sans-serif");
};
/** tear-off desk calendar on a 420 x 480 canvas: red header, big text */
const fxCalendar = (p: Pen, head: string, big: string, sub: string) => {
  rr(p, 20, 30, 400, 470, 18, "#f6f0e2", 9);
  p.poly([[20, 48], [400, 48], [400, 150], [20, 150]], "#c8202a", 0);
  for (const x of [90, 330]) { p.ell(x, 40, 16, 16, "#3a3a40", 6); }
  words(p, head, 210, 100, 58, "#fff6e8");
  words(p, big, 210, 290, big.length > 3 ? 92 : 170, "#2a2420");
  words(p, sub, 210, 420, 46, "#8a2a22");
};
/** the army order: paper with type and a U-turn arrow, on a 640 x 460 canvas */
const fxOrder = (p: Pen) => {
  p.poly([[20, 20], [620, 30], [610, 440], [30, 450]], "#f2ead2", 8);
  words(p, "ORDER", 320, 75, 56, "#2a2420");
  words(p, "IF THE FRENCH", 320, 160, 50, "#2a2420", "bold", "Courier New, monospace");
  words(p, "FIGHT BACK:", 320, 215, 50, "#2a2420", "bold", "Courier New, monospace");
  words(p, "TURN AROUND!", 320, 300, 62, "#b81e22", "bold", "Courier New, monospace");
  p.arc(320, 395, 80, 34, 180, 360, 14, "#b81e22"); p.poly([[400, 380], [430, 410], [370, 410]], "#b81e22", 0);
};
/** laurel wreath on a 400 x 200 canvas */
const fxLaurel = (p: Pen) => {
  for (let s = -1; s <= 1; s += 2) for (let k = 0; k < 9; k++) {
    const a = (Math.PI * (0.05 + k * 0.1)), x = 200 + s * 170 * Math.cos(a), y = 150 - 110 * Math.sin(a) * 0.9;
    p.ell(x, y, 30, 13, k % 2 ? "#4a8a2a" : "#5aa034", 4, 0, 360, (s * (90 - (a * 180) / Math.PI)) + s * 35);
  }
  p.ell(200, 168, 26, 14, "#e8c040", 4);
};
/** the agreement sheet (paper with lines and two signatures) on a 240 x 320 canvas */
const fxSheet = (p: Pen) => {
  p.poly([[8, 8], [232, 8], [232, 312], [8, 312]], "#f6f0e0", 6);
  words(p, "AGREEMENT", 120, 40, 26, "#2a2420");
  for (let k = 0; k < 9; k++) p.stroke([[30, 75 + k * 20], [30 + 150 + ((k * 37) % 30), 75 + k * 20]], 4, "#7a7468");
  p.stroke([[30, 270], [70, 255], [100, 275], [120, 258]], 3, "#1e2a5a"); p.stroke([[140, 272], [165, 255], [200, 270]], 3, "#1e2a5a");
};
/** a report bound in a red cover with a title, on a 360 x 460 canvas */
const fxReport = (p: Pen) => {
  p.poly([[20, 20], [340, 20], [340, 440], [20, 440]], "#7a1a1e", 9);
  p.poly([[50, 70], [310, 70], [310, 190], [50, 190]], "#f2ead2", 5);
  words(p, "REPORT", 180, 110, 50, "#2a2420"); words(p, "MANCHURIA", 180, 160, 32, "#2a2420");
  words(p, "LEAGUE OF NATIONS", 180, 380, 24, "#e8d8a8");
};

// ---------------- staging helpers ----------------
const MIST = (c: Ctx, x: number, y: number, z: number, w: number, i: number, col = "#e6ecf2", op = 1) => mist(c.out, ...c.O(x, y, z), w, c.t, i, col, op);
const STAMP = (c: Ctx, t0: number, text: string, x: number, y: number, z: number, w: number, flat = false, rot = 0) => stamp(c.out, c.t, at(t0), text, ...c.O(x, y, z), w, flat, rot);
const A = (c: Ctx, b: Beat[], ri = 0.2) => act(c.t, b, ri);
/** a figure whose acting comes from beats (expression + gesture), optionally talking from tTalk0..tTalk1 */
const actor = (c: Ctx, o: Outfit, i: number, key: string, x: number, y: number, z: number, beats: Beat[], extra: FrontOpts = {}, talkF?: [number, number, Expr, Expr], scale = 1) => {
  const a = A(c, beats); let expr = a.expr;
  if (talkF && c.f >= talkF[0] && c.f < talkF[1]) expr = talk(c.t, talkF[2], talkF[3]);
  P(c, W_(o, i, key), x, y, z, { mode: "stand", expr, pose: a.pose, pk: a.pk, ...extra }, scale);
};
/** side-on marcher moving with velocity (vx, vz) m/s from (x0, z0) at frame f0 */
const marcher = (c: Ctx, o: Outfit, i: number, key: string, x0: number, y: number, z0: number, vx: number, vz: number, f0: number, expr: Expr = "stern", yf?: (x: number, z: number) => number) => {
  const u = c.t - at(f0), x = x0 + vx * u, z = z0 + vz * u, mirror = vx * c.cam.right.x + vz * c.cam.right.z < 0;
  P(c, W_(o, i, key), x, yf ? yf(x, z) : y, z, {}, 1, { so: { mode: "march", phase: q((c.t * 1.9 + hh(i, 3)) % 1, 60), expr, stride: 0.9 }, mirror });
};
/** front-on marcher walking toward the camera at speed v along -z */
const frontMarch = (c: Ctx, o: Outfit, i: number, key: string, x: number, y: number, z0: number, v: number, f0: number, expr: Expr, extra: FrontOpts = {}) =>
  P(c, W_(o, i, key), x, y, z0 - v * (c.t - at(f0)), { mode: "march", phase: q((c.t * 1.9 + hh(i, 3)) % 1, 60), expr, lift: 40, ...extra });
const ll = (lon: number, lat: number): [number, number] => [2.6 - 5.2 * (lon + 15) / 180, 0.85 + 2.2533 * (lat + 6) / 78];
const MY = 0.953;

// three grabbers round the map table
const HIT = (c: Ctx, beats: Beat[], x = 1.3, z = 3.8, extra: FrontOpts = {}, tk?: [number, number]) =>
  actor(c, HITLER, 9, "hit", x, 0, z, beats, extra, tk ? [tk[0], tk[1], "shout", "scheme"] : undefined);
const MUS = (c: Ctx, beats: Beat[], x = 2.9, z = 3.8, extra: FrontOpts = {}) => actor(c, MUSSOLINI, 11, "mus", x, 0, z, beats, extra);
const TOJ = (c: Ctx, beats: Beat[], x = -1.5, z = 3.8, extra: FrontOpts = {}) => actor(c, TOJO_CAP, 12, "tojo", x, 0, z, beats, extra);

const s1 = (c: Ctx) => {
  // "Here's the thing. Hitler isn't the only one who wants more."
  const [ex, ez] = ll(15, 50), [ix, iz] = ll(39, 9), [cx, cz] = ll(120, 40);
  HIT(c, [[0, "hips", "smug"], [88, "pointUp", "scheme"], [125, "point", "grin"]], 1.3, 3.8, { facing: toward(c, 1.3, 3.8, ex, ez) });
  MUS(c, [[0, "hips", "proud"], [111, "point", "grin"]], 2.9, 3.8, { facing: toward(c, 2.9, 3.8, ix, iz) });
  TOJ(c, [[0, "cross", "stern"], [129, "point", "scheme"]], -1.5, 3.8, { facing: toward(c, -1.5, 3.8, cx, cz) });
};
const s2 = (c: Ctx) => {
  // "Over in Asia, Japan is an island nation with big ambitions and almost no oil, iron, or rubber of its own."
  TOJ(c, [[150, "hips", "proud"], [227, "armsUp", "beam"], [259, "chin", "worried"], [284, "shrug", "shock"], [318, "head", "panic"]], -1.75, 3.75);
  const crates: [number, number][] = [ll(145, 33), ll(149.5, 33), ll(154, 33)];
  [284, 300, 318].forEach((f0, k) => STAMP(c, f0, "EMPTY", crates[k][0], MY + 0.2, crates[k][1] - 0.08, 0.17));
};
// Manchuria: the plotting officers
const OFF_A = officer("jp", 1), OFF_B = officer("jp", 4);
const s3 = (c: Ctx) => {
  // "So in 1931, Japanese officers blow up a small piece of their own railway in Manchuria"
  const boom = 424;
  actor(c, OFF_A[0], 21, OFF_A[1], 1.95, 0, 3.15, [[352, null, "scheme"], [409, "fists", "grin"], [boom, "fists", "shock"], [boom + 12, "cheer", "laugh"]], { mode: "crouch" });
  actor(c, OFF_B[0], 22, OFF_B[1], -0.55, 0, 3.0, [[352, "cross", "stern"], [393, "chin", "scheme"], [boom, "head", "shock"], [boom + 14, "hips", "smug"]], { prop: c.f < boom ? "binoc" : null });
  const [j, jk] = japanese(3); actor(c, j, 23, jk, 3.3, 0, 3.8, [[352, null, "stern"], [boom, null, "gasp"], [boom + 16, null, "grin"]]);
  if (c.f >= boom - 1 && c.f < boom + 40) {
    const k = q(clamp01((c.t - at(boom)) / 1.2), 24);
    F(c, { key: `boom${k}`, cw: 600, ch: 660, draw: (p) => fxBoom(p, k), x: 0.4, y: 1.9, z: 5.4, w: 3.6, h: 3.9, glow: 1.6 });
  }
  for (let i = 0; i < 3; i++) MIST(c, 0.4 + i * 0.8, 1.6 + i * 0.5, 6.4, 3, i, "#5a5a62", c.f > boom ? 0.6 : 0);
};
const s4 = (c: Ctx) => {
  // "...in northern China, blame the Chinese, and use it as an excuse to take the whole region"
  const bx = -18, bz = 70;
  actor(c, OFF_A[0], 21, OFF_A[1], 1.9, 0, 3.4, [[500, "hips", "smug"], [548, "point", "shout"], [579, "pointUp", "scheme"]], { facing: toward(c, 1.9, 3.4, bx, bz) }, [548, 600, "shout", "scheme"]);
  actor(c, OFF_B[0], 22, OFF_B[1], -0.55, 0, 3.0, [[500, "cross", "stern"], [555, "point", "angry"], [585, "fist", "scheme"]], { facing: toward(c, -0.55, 3.0, bx, bz) });
  const [j, jk] = japanese(3); actor(c, j, 23, jk, 3.3, 0, 3.8, [[500, null, "stern"], [561, "point", "angry"]], { facing: toward(c, 3.3, 3.8, bx, bz) });
  for (let i = 0; i < 4; i++) MIST(c, 0.2 + i * 1.2, 2 + i * 0.9, 6.5 + i * 0.4, 4, i, "#4a4a52", 0.55);
};
const s5 = (c: Ctx) => {
  // "...take the whole region"
  const [mx, mz] = ll(126, 46);
  TOJ(c, [[603, "point", "scheme"], [630, "hips", "smug"]], -1.55, 3.8, { facing: toward(c, -1.55, 3.8, mx, mz) });
};
// the League
const DELEG: [number, number, string][] = [[4.4, 2.6, "JP"], [4.4, 3.9, "CN"], [4.4, 5.2, ""], [4.4, 6.5, ""], [-4.4, 2.6, ""], [-4.4, 3.9, ""], [-4.4, 5.2, ""], [-4.4, 6.5, ""]];
for (let k = 0; k < 5; k++) { const a = Math.PI * (k + 0.5) / 5 * 0.9 + 0.16; DELEG.push([4.4 * Math.cos(a), 7.0 + 4.4 * Math.sin(a), ""]); }
const delegates = (c: Ctx, mood: (i: number) => Beat[], skipJP = false) => {
  DELEG.forEach(([x, z, tag], i) => {
    if (tag === "JP") { if (!skipJP) actor(c, MATSUOKA, 40, "matsu", x, 0, z, mood(i)); return; }
    if (tag === "CN") { actor(c, KOO, 41, "koo", x, 0, z, mood(i)); return; }
    const v = (i * 5 + 2) % MEN.length; actor(c, MEN[v], 42 + i, `m${v}`, x, 0, z, mood(i), { facing: (x > 0 ? -1 : 1) as -1 | 1 });
  });
};
const LYT = (c: Ctx, beats: Beat[], extra: FrontOpts = {}, tk?: [number, number]) => actor(c, LYTTON, 39, "lytton", 0, 0, 5.05, beats, extra, tk ? [tk[0], tk[1], "shout", "stern"] : undefined);
const s6 = (c: Ctx) => {
  // "The League of Nations, which was basically the world's group chat for keeping the peace, is outraged."
  LYT(c, [[657, "palms", "proud"], [716, "pointUp", "smile"], [789, "fist", "furious"]]);
  delegates(c, (i) => [[657, (["cross", "chin", null, "hips"] as (Pose | null)[])[i % 4], (["smug", "neutral", "smile", "stern"] as Expr[])[i % 4]],
    [789 + (i % 4) * 2, (["fist", "fists", "point", "fist"] as Pose[])[i % 4], (["angry", "furious", "shout", "angry"] as Expr[])[i % 4]]]);
};
const s7 = (c: Ctx) => {
  // "It writes a very strongly worded report."
  LYT(c, [[818, "pointUp", "stern"], [846, "point", "angry"], [873, "pointUp", "proud"]], { prop: "paper" }, [823, 885]);
  if (c.f >= 840) F(c, { key: "report", cw: 360, ch: 460, draw: fxReport, x: -0.55, y: 1.55, z: 4.85, w: 0.42, h: 0.54, rot: 0.08 });
  STAMP(c, 862, "STRONGLY\nWORDED", -0.55, 1.5, 4.75, 0.5);
};
const s8 = (c: Ctx) => {
  // "Japan reads it, and leaves the group chat."
  const walk = 922, u = Math.max(0, c.t - at(walk));
  const x = 4.4 + 0.9 * u, z = 2.6 - 1.6 * u;
  if (c.f < walk) actor(c, MATSUOKA, 40, "matsu", 4.4, 0, 2.6, [[890, null, "stern"], [903, "chin", "sneer"]], { prop: "paper" });
  else P(c, W_(MATSUOKA, 40, "matsu"), x, 0, z, { mode: "march", phase: q((c.t * 1.8) % 1, 60), expr: "sneer", lift: 50 });
  actor(c, KOO, 41, "koo", 4.4, 0, 3.9, [[890, null, "worried"], [924, "palms", "gasp"]], { facing: -1 });
  for (let i = 2; i < 6; i++) { const [dx, dz] = DELEG[i]; const v = (i * 5 + 2) % MEN.length; actor(c, MEN[v], 42 + i, `m${v}`, dx, 0, dz, [[890, null, "stern"], [926 + i, "head", "shock"]]); }
  if (c.f >= 936) {
    const k = smooth((c.t - at(936)) / 0.25);
    F(c, { key: "chat", cw: 1000, ch: 200, draw: (p) => fxChat(p, "JAPAN HAS LEFT THE GROUP"), x: 3.2, y: 2.65, z: 3.4, w: 2.6 * k, h: 0.52 * k, glow: 1.0 });
  }
};
// China
const JPCOL = (c: Ctx, f0: number, n: number) => {
  for (let i = 0; i < n; i++) {
    const [o, k] = japanese(i + 1), row = Math.floor(i / 2), lane = i % 2;
    marcher(c, o, 60 + i, k, -1.6 + lane * 0.9, 0, -9 + row * 1.6 - (lane ? 0.5 : 0), 0, 1.35, f0, (["stern", "determined", "grim", "stern"] as Expr[])[i % 4]);
  }
};
const s9 = (c: Ctx) => {
  // "In 1937, Japan invades the rest of China." (side-on column marching to the gate)
  JPCOL(c, 958, 14);
  const [o, k] = officer("jp", 6); marcher(c, o, 80, k, -2.6, 0, -4.0, 0, 1.35, 958, "proud");
};
const GEN = (c: Ctx, beats: Beat[], extra: FrontOpts = {}, tk?: [number, number]) => actor(c, TOJO_CAP, 12, "tojo", 7.1, 0.08, 5.6, beats, extra, tk ? [tk[0], tk[1], "grin", "smug"] : undefined);
const s10 = (c: Ctx) => {
  // "Japan's generals expect it to be over in a few months."
  GEN(c, [[1066, "hips", "proud"], [1094, "pointUp", "smug"], [1141, "cheer", "laugh"]], { prop: c.f < 1094 ? "binoc" : null }, [1094, 1150]);
  const [o, k] = officer("jp", 2); actor(c, o, 13, k, 8.5, 0.05, 6.3, [[1066, "chin", "smug"], [1118, "hips", "grin"]]);
  const [s, sk] = japanese(5); actor(c, s, 14, sk, 5.7, 0.0, 6.6, [[1066, null, "stern"]]);
  if (c.f >= 1118) F(c, { key: "cal3", cw: 420, ch: 480, draw: (p) => fxCalendar(p, "1937", "3", "MONTHS"), x: 6.1, y: 1.9, z: 5.5, w: 0.6, h: 0.69 });
};
const s11 = (c: Ctx) => {
  // "It lasts eight years."
  GEN(c, [[1179, "head", "shock"], [1196, "head", "panic"]], { tilt: 0 });
  const flips = Math.min(8, Math.floor((c.t - at(1185)) * 14));
  const yr = 1937 + Math.max(0, flips);
  F(c, { key: `cal${yr}`, cw: 420, ch: 480, draw: (p) => fxCalendar(p, String(Math.min(1945, yr)), flips >= 8 ? "8" : String(3 + flips), flips >= 8 ? "YEARS" : "MONTHS"), x: 6.1, y: 1.9, z: 5.5, w: 0.6, h: 0.69 });
  STAMP(c, 1196, "1937-1945", 6.1, 1.95, 5.45, 0.62);
};
const s12 = (c: Ctx) => {
  // Nanjing, December 1937: the wall at dusk, smoke, nobody
  for (let i = 0; i < 5; i++) MIST(c, -14 + i * 7, 8 + (i % 2) * 3, 24 + i, 10, i, "#3a3236", 0.55);
};
const s13 = (c: Ctx) => { for (let i = 0; i < 4; i++) MIST(c, -2 + i * 1.4, 2.5 + i * 0.6, 50 + i * 5, 5, i, "#4a4044", 0.45); };
const s14 = (c: Ctx) => { for (let i = 0; i < 3; i++) MIST(c, -0.5 + i * 0.8, 0.8 + i * 0.4, 47 + i, 3, i, "#5a5054", 0.35); };
const s15 = (c: Ctx) => {
  // "The Chinese government retreats deep into the country and keeps fighting." (side-on up the mountain road)
  for (let i = 0; i < 9; i++) {
    const [o, k] = chinese(i);
    marcher(c, o, 90 + i, k, 200.2 + (i % 2) * 0.7, 0, -1 + i * 1.5, 0, 1.0, 1631, (["determined", "grim", "exhausted"] as Expr[])[i % 3], (x, z) => Math.max(0, z * 0.08) + 0.03);
  }
  for (let i = 0; i < 4; i++) MIST(c, 196 + i * 3, 3 + i, 18 + i * 6, 9, i, "#e8eef2", 0.5);
};
const s16 = (c: Ctx) => {
  // "And that matters more than most people realise."
  const [o, k] = chinese(1);
  actor(c, o, 91, k, 200.6, 0.67, 8.0, [[1733, null, "exhausted"], [1748, null, "determined"], [1782, "fist", "determined"]]);
  const [o2, k2] = chinese(4); actor(c, o2, 94, k2, 199.3, 0.9, 10.5, [[1733, null, "grim"]]);
  for (let i = 0; i < 3; i++) MIST(c, 197 + i * 3, 2.5 + i, 16 + i * 5, 8, i, "#e8eef2", 0.45);
};
const s17 = (c: Ctx) => {
  // "...around a million Japanese soldiers are stuck in China, soldiers Japan will badly need everywhere else."
  TOJ(c, [[1814, "chin", "worried"], [1908, "head", "shock"], [1985, "palms", "panic"]], -1.5, 3.8);
  const [sx, sz] = ll(113, 33); STAMP(c, 1908, "STUCK", sx, MY + 0.02, sz, 0.45, true, Math.PI);
};
// Rome
const ROMECROWD = (c: Ctx) => {
  for (let i = 0; i < 26; i++) {
    const x = (hh(i, 1) - 0.5) * 18, z = -3.5 - hh(i, 2) * 11, [o, k] = i % 4 === 3 ? italian(i) : crowd(i + 3), r = i % 3;
    const a = A(c, [[2027, r === 0 ? "cheer" : r === 1 ? "wave" : "armsUp", (["cheer", "beam", "laugh"] as Expr[])[i % 3]]]);
    P(c, W_(o, 120 + i, k), x, 0, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: q(0.6 + 0.4 * Math.abs(Math.sin(c.t * 2.5 + i)), 5), prop: i % 5 === 1 ? ["flag", "it"] : null, flutter: q((c.t * 1.3 + i * 0.3) % 1, 12) });
  }
};
const DUCE = (c: Ctx, beats: Beat[], tk?: [number, number]) => actor(c, MUSSOLINI, 11, "mus", 0, 4.6, -0.45, beats, {}, tk ? [tk[0], tk[1], "shout", "proud"] : undefined);
const s18 = (c: Ctx) => {
  // "Meanwhile in Italy, a dictator named Benito Mussolini..."
  ROMECROWD(c);
  DUCE(c, [[2027, "hips", "proud"], [2068, "fists", "shout"], [2093, "hips", "smug"]]);
};
const s19 = (c: Ctx) => {
  // "...dreams of rebuilding the Roman Empire."
  DUCE(c, [[2120, "hips", "proud"], [2127, "chin", "scheme"], [2164, "armsUp", "beam"]]);
  if (c.f >= 2164) {
    const k = smooth((c.t - at(2164)) / 0.3);
    F(c, { key: "laurel", cw: 400, ch: 200, draw: fxLaurel, x: 0, y: 4.6 + 2.12 + 0.3 * (1 - k), z: -0.5, w: 0.62, h: 0.31 });
  }
};
const s20 = (c: Ctx) => {
  // "So in 1935, he invades Ethiopia, one of the last independent countries in Africa."
  for (let i = 0; i < 8; i++) { const [o, k] = italian(i); frontMarch(c, o, 130 + i, k, -1.3 + (i % 3) * 1.1, 0, 15 + Math.floor(i / 3) * 1.8, 1.1, 2201, (["stern", "proud", "grim"] as Expr[])[i % 3]); }
  actor(c, SELASSIE, 140, "selassie", -7.0, 1.2, 7.2, [[2201, "cross", "stern"], [2285, "fist", "determined"], [2325, "point", "angry"]], { facing: 1 });
  for (let i = 0; i < 4; i++) { const [o, k] = WARRIOR(i); actor(c, o, 141 + i, k, -8.6 + i * 0.95 + (i > 1 ? 1.4 : 0), i > 1 ? 0.3 : 0.9, 7.8 + (i % 2) * 0.6, [[2201, null, "stern"], [2290 + i * 4, "fist", "determined"]]); }
};
const s21 = (c: Ctx) => {
  // "The League of Nations is outraged again."
  LYT(c, [[2362, "fist", "angry"], [2399, "fists", "furious"]]);
  delegates(c, (i) => [[2362, (["fist", "fists", "point", "fist"] as Pose[])[i % 4], (["angry", "furious", "shout", "angry"] as Expr[])[i % 4]]], true);
};
const s22 = (c: Ctx) => {
  // "And again, it does basically nothing."
  LYT(c, [[2432, "fist", "angry"], [2462, "shrug", "neutral"], [2487, "shrug", "dazed"]]);
  delegates(c, (i) => [[2432, "fist", "angry"], [2465 + (i % 3) * 3, (["shrug", "cross", "chin"] as Pose[])[i % 3], (["neutral", "exhausted", "dazed"] as Expr[])[i % 3]]], true);
  STAMP(c, 2487, "NOTHING", 0, 2.3, 4.9, 1.0);
};
// Hitler at his desk (chair, the 3D desk in front)
const DESKH = (c: Ctx, beats: Beat[]) => actor(c, HITLER, 9, "hit", -4.4, 0, 7.05, beats, { mode: "chair", chair: false });
const s23 = (c: Ctx) => {
  // "Hitler is watching all of this and learning one lesson."
  DESKH(c, [[2512, "chin", "scheme"], [2563, "pointUp", "smug"]]);
};
const s24 = (c: Ctx) => {
  // "Nobody is going to stop him."
  DESKH(c, [[2611, "chin", "scheme"], [2635, "fist", "grin"]]);
};
// the Rhineland
const s25 = (c: Ctx) => {
  // "In 1936, he marches troops into the Rhineland, a strip of Germany that was supposed to stay empty of soldiers."
  for (let i = 0; i < 15; i++) { const [o, k] = german(i); frontMarch(c, o, 150 + i, k, -2.4 + (i % 4) * 1.6, 0, 14 + Math.floor(i / 4) * 1.9, 1.3, 2677, (["proud", "stern", "grim", "determined"] as Expr[])[i % 4]); }
  for (let i = 0; i < 12; i++) {
    const sd = i % 2 ? 1 : -1, [o, k] = crowd(i + 7);
    const a = A(c, [[2677, i % 3 ? "wave" : "cheer", (["cheer", "beam", "laugh"] as Expr[])[i % 3]]]);
    P(c, W_(o, 170 + i, k), sd * (5.0 + hh(i) * 1.6), 0.24, -1.5 - Math.floor(i / 2) * 1.7, { mode: "stand", expr: a.expr, pose: a.pose, pk: q(0.6 + 0.4 * Math.abs(Math.sin(c.t * 3 + i)), 5) });
  }
};
const GENS = (c: Ctx, a: Beat[], b: Beat[], extra: FrontOpts = {}) => {
  const [o1, k1] = officer("de", 3), [o2, k2] = officer("de", 7);
  actor(c, o1, 180, k1, -4.6, 0, -3.4, a, extra);
  actor(c, o2, 181, k2, -3.2, 0, -3.1, b, { facing: -1 });
};
const s26 = (c: Ctx) => {
  // "His generals are terrified."
  GENS(c, [[2869, "collar", "fear"], [2896, "head", "dread"]], [[2869, null, "nervous"], [2893, "cry", "fear"]], { prop: "binoc" });
};
const s27 = (c: Ctx) => {
  // "They have orders to turn around if the French army fights back."
  GENS(c, [[2919, null, "worried"], [2945, "point", "panic"], [2991, "head", "fear"]], [[2919, "collar", "nervous"], [2970, "palms", "fear"]], { prop: "paper" });
  F(c, { key: "order", cw: 640, ch: 460, draw: fxOrder, x: -3.95, y: 1.75, z: -3.6, w: 0.95, h: 0.68, rot: -0.05 });
};
const s28 = (c: Ctx) => {
  // "The French army does not fight back."
  const seats: [number, number, number][] = [[-1.0, 4.4, 1], [1.0, 4.4, -1], [0, 5.2, 0]];
  seats.forEach(([x, z, f], i) => {
    const [o, k] = french(i * 2 + 1);
    actor(c, o, 190 + i, k, x, 0, z, [[3020, i === 2 ? "chin" : null, (["smug", "grin", "neutral"] as Expr[])[i]], [3057 + i * 3, "shrug", (["dazed", "smug", "exhausted"] as Expr[])[i]]], { mode: "chair", chair: false, facing: f as -1 | 0 | 1 });
  });
  const [o, k] = french(4); actor(c, o, 193, k, 1.9, 0, 6.2, [[3020, "hips", "smile"], [3069, "shrug", "laugh"]], { prop: "stein" });
};
// the map: Austria, Sudetenland, Czechoslovakia
const s29 = (c: Ctx) => {
  // "In 1938, Germany swallows Austria without firing a shot."
  const [vx, vz] = ll(15, 47.6);
  HIT(c, [[3098, "hips", "scheme"], [3146, "point", "lick"], [3195, "hips", "smug"]], 1.3, 3.8, { facing: toward(c, 1.3, 3.8, vx, vz) });
};
const s30 = (c: Ctx) => {
  // "Then Hitler demands a piece of Czechoslovakia called the Sudetenland."
  const [sx, sz] = ll(14.5, 50.2);
  HIT(c, [[3235, "fist", "angry"], [3254, "point", "shout"], [3303, "fists", "furious"]], 1.3, 3.8, { facing: toward(c, 1.3, 3.8, sx, sz) }, [3254, 3335]);
  MUS(c, [[3235, "hips", "smug"], [3315, "chin", "scheme"]], 2.9, 3.8);
};
// Munich
const CHAM = (c: Ctx, x: number, z: number, beats: Beat[], extra: FrontOpts = {}, tk?: [number, number]) => actor(c, CHAMBERLAIN, 30, "cham", x, 0, z, beats, extra, tk ? [tk[0], tk[1], "shout", "smile"] : undefined);
const DAL = (c: Ctx, x: number, z: number, beats: Beat[], extra: FrontOpts = {}) => actor(c, DALADIER, 31, "dal", x, 0, z, beats, extra);
const s31 = (c: Ctx) => {
  // "Britain and France really, really don't want another war."
  const shake = c.f >= 3368 && c.f < 3430 ? q(Math.sin(c.t * 14) * 8, 2) : 0;
  CHAM(c, -2.1, 5.4, [[3342, "collar", "worried"], [3368, "palms", "fear"]], { headTilt: shake, prop: "umbrella" });
  DAL(c, -0.7, 5.4, [[3342, null, "nervous"], [3383, "palms", "fear"]], { headTilt: -shake, facing: -1 });
};
const s32 = (c: Ctx) => {
  // "So their leaders fly to Munich and make a deal: Hitler gets the Sudetenland..."
  CHAM(c, -2.1, 5.4, [[3437, "collar", "nervous"], [3483, "palms", "smile"]], { prop: "umbrella" });
  DAL(c, -0.7, 5.4, [[3437, null, "worried"], [3490, "shrug", "nervous"]]);
  HIT(c, [[3437, "hips", "smug"], [3502, "point", "grin"], [3524, "hips", "scheme"]], 0.7, 5.4, { facing: -1 });
  MUS(c, [[3437, "cross", "proud"], [3514, "hips", "smug"]], 2.1, 5.4);
};
const s33 = (c: Ctx) => {
  // "...and in return, he promises that's all he wants."
  HIT(c, [[3540, "hips", "smug"], [3577, "pray", "smile"], [3596, "palms", "beam"], [3616, "pointUp", "scheme"]], 0.7, 5.4, {}, [3570, 3630]);
  DAL(c, -0.7, 5.4, [[3540, null, "nervous"], [3604, "shrug", "worried"]], { facing: 1 });
  MUS(c, [[3540, "cross", "smug"], [3616, "chin", "scheme"]], 2.1, 5.4, { facing: -1 });
};
// Heston
const HCROWD = (c: Ctx, f0: number) => {
  for (let i = 0; i < 18; i++) {
    const sd = i % 2 ? 1 : -1, [o, k] = crowd(i + 11), r = i % 4;
    const a = A(c, [[f0, (["cheer", "wave", "armsUp", "clap"] as Pose[])[r], (["cheer", "beam", "laugh", "joy"] as Expr[])[i % 4]]]);
    P(c, W_(o, 200 + i, k), sd * (3.3 + hh(i, 4) * 5.0), 0, 2.4 + hh(i, 5) * 6, { mode: "stand", expr: a.expr, pose: a.pose, pk: q(0.6 + 0.4 * Math.abs(Math.sin(c.t * 3 + i)), 5), prop: i % 6 === 2 ? ["flag", "uk"] : null, flutter: q((c.t + i * 0.3) % 1, 12) });
  }
  const [p1, pk1] = [suit("#4a4038", { hat: "fedora", hatCol: "#5a4a3a", cigar: true, build: "stout" }), "press1"];
  actor(c, p1, 220, pk1, -6.0, 0.9, -0.6, [[f0, "chin", "grin"]]);
};
const s34 = (c: Ctx) => {
  // "The British Prime Minister, Neville Chamberlain, flies home waving the agreement..."
  HCROWD(c, 3638);
  CHAM(c, 0, 4.6, [[3638, "wave", "beam"], [3702, "pointUp", "proud"], [3724, "wave", "laugh"]], { prop: "paper" });
};
const s35 = (c: Ctx) => {
  // "...and tells everyone he's secured peace for our time."
  HCROWD(c, 3760);
  CHAM(c, 0, 4.6, [[3760, "pointUp", "proud"], [3807, "pointUp", "beam"]], { prop: "paper" }, [3768, 3840]);
};
const s36 = (c: Ctx) => {
  // "Six months later, Hitler takes the rest of Czechoslovakia anyway."
  const [px, pz] = ll(15.5, 49.8);
  HIT(c, [[3844, "hips", "smug"], [3884, "point", "grin"], [3934, "shrug", "smug"]], 1.3, 3.8, { facing: toward(c, 1.3, 3.8, px, pz) });
  STAMP(c, 3934, "MARCH 1939", px - 0.05, MY + 0.02, pz - 0.05, 0.4, true, Math.PI);
};
const s37 = (c: Ctx) => {
  // "Peace for our time lasted about as long as a gym membership in January."
  const gone = 4057;
  CHAM(c, 0, 4.6, [[3951, "pointUp", "beam"], [3987, "pointUp", "smile"], [4025, null, "worried"], [gone, "shrug", "sad"]], { prop: c.f < gone ? "paper" : null });
  if (c.f >= gone) {
    const u = c.t - at(gone);
    F(c, { key: "sheet", cw: 240, ch: 320, draw: fxSheet, x: -0.35 - 2.2 * u, y: 1.9 + 1.2 * u + 0.2 * Math.sin(u * 6), z: 4.5 + 1.5 * u, w: 0.26, h: 0.34, rot: u * 4 });
  }
  STAMP(c, 4057, "EXPIRED", 0, 2.75, 4.5, 0.8);
};

const STAGE: Record<number, (c: Ctx) => void> = {
  1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6, 7: s7, 8: s8, 9: s9, 10: s10, 11: s11, 12: s12, 13: s13, 14: s14, 15: s15, 16: s16, 17: s17, 18: s18,
  19: s19, 20: s20, 21: s21, 22: s22, 23: s23, 24: s24, 25: s25, 26: s26, 27: s27, 28: s28, 29: s29, 30: s30, 31: s31, 32: s32, 33: s33, 34: s34,
  35: s35, 36: s36, 37: s37,
};

// ---------------- cameras (set-local, look +z unless noted) ----------------
const CAMS: Record<number, Key[]> = {
  1: [
    { f: 0, s: (f) => D(S.map, [0.4, 3.4, -2.2], [0.5, 1.0, 2.4], f, 0, 0.0018, { fov: 46 }) },
    { f: 66, dur: 36, s: (f) => D(S.map, [0.9, 1.75, 0.0], [0.7, 1.25, 3.2], f, 66, 0.0025, { fov: 52 }) },
  ],
  2: [
    { f: 150, s: (f) => D(S.map, [-1.25, 1.55, 0.55], [-1.75, 1.2, 2.8], f, 150, 0.0022, { fov: 44, roll: 0.02 }) },
    { f: 268, cut: true, s: (f) => D(S.map, [-1.72, 1.25, 1.2], [-1.83, 0.98, 2.05], f, 268, 0.003, { fov: 34 }) },
  ],
  3: [{ f: 352, s: (f) => D(S.man, [1.1, 0.95, -0.4], [0.7, 1.15, 4.8], f, 352, 0.0028, { fov: 44 }) }],
  4: [{ f: 500, s: (f) => D(S.man, [3.6, 1.3, -0.2], [-0.6, 1.7, 8], f, 500, 0.002, { fov: 48, roll: -0.03 }) }],
  5: [{ f: 603, s: (f) => D(S.map, [-1.2, 1.6, 1.25], [-1.47, 0.97, 2.35], f, 603, 0.004, { fov: 36 }) }],
  6: [
    { f: 657, s: (f) => D(S.lg, [0.0, 3.2, -3.2], [0.0, 1.3, 7.0], f, 657, 0.0018, { fov: 50 }) },
    { f: 772, dur: 22, s: (f) => D(S.lg, [1.6, 1.55, 0.2], [1.6, 1.45, 5.6], f, 772, 0.003, { fov: 46, roll: 0.03 }) },
  ],
  7: [{ f: 818, s: (f) => D(S.lg, [-0.15, 1.6, 2.2], [-0.2, 1.55, 5.0], f, 818, 0.004, { fov: 40 }, 0.008) }],
  8: [{ f: 890, s: (f) => Tr(S.lg, [1.6, 1.55, -1.6], [4.2, 1.45, 2.4], f, 890, [0.012, 0, -0.006], { fov: 46 }) }],
  9: [{ f: 958, s: (f) => Tr(S.cn, [8.5, 1.3, 2.0], [0.0, 2.4, 9.0], f, 958, [0, 0, 0.03], { fov: 50 }) }],
  10: [{ f: 1066, s: (f) => D(S.cn, [5.6, 1.45, 2.2], [7.3, 1.35, 5.8], f, 1066, 0.0025, { fov: 44 }) }],
  11: [{ f: 1179, s: (f) => D(S.cn, [6.4, 1.6, 3.6], [6.8, 1.75, 5.6], f, 1179, 0.006, { fov: 40, roll: -0.05 }, 0.01) }],
  12: [{ f: 1209, s: (f) => D(S.cn, [1.5, 1.8, -2.0], [0.0, 7.0, 30.0], f, 1209, 0.0012, { fov: 48 }) }],
  13: [{ f: 1362, s: (f) => Tr(S.cn, [2.2, 1.6, 37.5], [-0.4, 1.5, 52.0], f, 1362, [0, 0, 0.012], { fov: 44 }) }],
  14: [{ f: 1485, s: (f) => D(S.cn, [1.4, 0.4, 42.5], [0.7, 0.1, 44.0], f, 1485, 0.0016, { fov: 38 }) }],
  15: [{ f: 1626, s: (f) => Tr(S.cn, [207.0, 2.6, 2.0], [199.6, 1.6, 6.0], f, 1626, [0, 0.003, 0.03], { fov: 46 }) }],
  16: [{ f: 1733, s: (f) => D(S.cn, [200.9, 2.3, 5.3], [200.6, 2.15, 8.0], f, 1733, 0.003, { fov: 40 }) }],
  17: [
    { f: 1814, s: (f) => D(S.map, [-0.9, 1.75, 0.55], [-1.3, 1.0, 2.1], f, 1814, 0.002, { fov: 46 }) },
    { f: 1950, dur: 40, s: (f) => D(S.map, [-1.95, 1.65, 0.5], [-2.3, 0.95, 1.7], f, 1950, 0.002, { fov: 46, roll: 0.03 }) },
  ],
  18: [{ f: 2027, s: (f) => D(S.rome, [2.5, 1.0, -17.0], [0.0, 5.6, 0.0], f, 2027, 0.0022, { fov: 46 }) }],
  19: [{ f: 2120, s: (f) => D(S.rome, [0.6, 5.7, -4.6], [0.0, 5.8, -0.45], f, 2120, 0.003, { fov: 36 }) }],
  20: [
    { f: 2201, s: (f) => D(S.eth, [2.6, 1.3, -3.5], [-0.8, 1.6, 14.0], f, 2201, 0.0018, { fov: 48 }) },
    { f: 2282, dur: 36, s: (f) => D(S.eth, [-3.6, 2.0, 1.8], [-7.2, 2.3, 7.6], f, 2282, 0.003, { fov: 44 }) },
  ],
  21: [{ f: 2362, s: (f) => D(S.lg, [-2.4, 1.5, -0.8], [0.6, 1.5, 6.4], f, 2362, 0.003, { fov: 48, roll: -0.03 }) }],
  22: [{ f: 2432, s: (f) => D(S.lg, [0.2, 2.3, -1.8], [0.0, 1.3, 6.0], f, 2432, 0.003, { fov: 46 }) }],
  23: [{ f: 2512, s: (f) => D(S.map, [-2.85, 1.45, 4.6], [-4.15, 1.05, 6.7], f, 2512, 0.0025, { fov: 42 }) }],
  24: [{ f: 2611, s: (f) => D(S.map, [-4.45, 1.55, 5.55], [-4.5, 0.85, 6.4], f, 2611, 0.003, { fov: 40 }) }],
  25: [
    { f: 2677, s: (f) => D(S.rh, [-2.2, 1.3, -6.0], [0.4, 2.6, 22.0], f, 2677, 0.0015, { fov: 48 }) },
    { f: 2790, dur: 30, s: (f) => D(S.rh, [2.2, 0.8, 1.0], [0.0, 1.9, 9.0], f, 2790, 0.002, { fov: 46, roll: 0.03 }) },
  ],
  26: [{ f: 2869, s: (f) => D(S.rh, [-3.6, 1.55, -6.3], [-3.9, 1.55, -3.2], f, 2869, 0.005, { fov: 40 }, 0.01) }],
  27: [{ f: 2919, s: (f) => D(S.rh, [-3.2, 1.6, -6.0], [-4.0, 1.6, -3.4], f, 2919, 0.003, { fov: 40 }) }],
  28: [{ f: 3020, s: (f) => D(S.mg, [0.4, 1.35, 1.6], [0.1, 0.95, 5.0], f, 3020, 0.0025, { fov: 44 }) }],
  29: [{ f: 3098, s: (f) => D(S.map, [1.2, 1.55, 1.4], [1.62, 0.98, 2.5], f, 3098, 0.0025, { fov: 38 }) }],
  30: [{ f: 3235, s: (f) => D(S.map, [0.95, 1.55, 0.9], [1.45, 1.25, 3.2], f, 3235, 0.003, { fov: 44, roll: -0.02 }) }],
  31: [{ f: 3342, s: (f) => D(S.mu, [-1.3, 1.55, 2.3], [-1.4, 1.5, 5.4], f, 3342, 0.003, { fov: 42 }) }],
  32: [{ f: 3437, s: (f) => D(S.mu, [0.6, 2.2, -1.0], [0.0, 1.35, 5.4], f, 3437, 0.002, { fov: 48 }) }],
  33: [{ f: 3540, s: (f) => D(S.mu, [0.9, 1.5, 2.6], [0.7, 1.55, 5.4], f, 3540, 0.004, { fov: 40, roll: 0.03 }, 0.006) }],
  34: [{ f: 3638, s: (f) => D(S.af, [1.4, 1.5, -4.2], [1.2, 1.9, 7.0], f, 3638, 0.002, { fov: 48 }) }],
  35: [{ f: 3760, s: (f) => D(S.af, [0.5, 1.65, 1.9], [0.0, 1.7, 4.6], f, 3760, 0.004, { fov: 38 }) }],
  36: [{ f: 3844, s: (f) => D(S.map, [1.15, 1.6, 1.3], [1.6, 1.05, 2.6], f, 3844, 0.0025, { fov: 40 }) }],
  37: [{ f: 3951, s: (f) => D(S.af, [1.2, 1.6, 1.0], [0.0, 1.7, 4.6], f, 3951, 0.0015, { fov: 42 }) }],
};
const DOF: Dof[] = [
  { f: 0, cInf: 6 }, { f: 66, dur: 36, cInf: 9 }, { f: 150, cInf: 9 }, { f: 268, cInf: 14 }, { f: 352, cInf: 8 }, { f: 500, cInf: 6 }, { f: 603, cInf: 12 },
  { f: 657, cInf: 4 }, { f: 772, dur: 22, cInf: 9 }, { f: 818, cInf: 12 }, { f: 890, cInf: 9 }, { f: 958, cInf: 5 }, { f: 1066, cInf: 9 }, { f: 1179, cInf: 12 },
  { f: 1214, cInf: 3 }, { f: 1367, cInf: 6 }, { f: 1490, cInf: 14 }, { f: 1631, cInf: 5 }, { f: 1733, cInf: 11 }, { f: 1814, cInf: 9 }, { f: 2027, cInf: 4 },
  { f: 2120, cInf: 10 }, { f: 2201, cInf: 5 }, { f: 2282, dur: 36, cInf: 8 }, { f: 2362, cInf: 7 }, { f: 2432, cInf: 7 }, { f: 2512, cInf: 10 }, { f: 2611, cInf: 14 },
  { f: 2677, cInf: 4 }, { f: 2790, dur: 30, cInf: 7 }, { f: 2869, cInf: 12 }, { f: 2919, cInf: 11 }, { f: 3020, cInf: 9 }, { f: 3098, cInf: 13 }, { f: 3235, cInf: 10 },
  { f: 3342, cInf: 11 }, { f: 3437, cInf: 6 }, { f: 3540, cInf: 12 }, { f: 3638, cInf: 5 }, { f: 3760, cInf: 11 }, { f: 3844, cInf: 12 }, { f: 3951, cInf: 9 },
];

export const CH = makeChapter({
  total: TOTAL,
  shots: SHOTS,
  xfade: { 3: 6, 6: 8, 9: 8, 12: 14, 13: 12, 14: 12, 15: 14, 18: 8, 20: 8, 25: 8, 28: 6, 31: 8, 34: 8 },
  cards: [{ a: 0, b: 60, kind: "chapter", lines: ["CHAPTER 2", "EVERYONE GRABS SOMETHING", "1931 – 1938"] }],
  cams: CAMS,
  dof: DOF,
  kicks: [[424 / 30, 1.4], [789 / 30, 0.4], [1196 / 30, 0.6], [3146 / 30, 0.4], [3315 / 30, 0.5], [4057 / 30, 0.3]],
  stage: STAGE,
});
