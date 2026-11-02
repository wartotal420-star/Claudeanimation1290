// WW2 part 1 cast: lit flat sprites + unlit effect cards, staged per shot in each set's local coordinates.
import * as THREE from "three";
import {
  Pen, bodyFront, bodySide, army, US, CA, GE, JP, KID, INK, SAILOR, shade, Outfit, Expr, FrontOpts, SideOpts, Pose,
  fxContact, fxShadow, fxMist, fxBomber, fxMushroom, fxStamp, fxBanknote, fxChart, fxPadlock, fxNewspaper, fxFlame, fxMapCut,
} from "./toon";
import { FPS, SHOTS, clamp01, smooth, DOM0 } from "./story";
import type { V3 } from "./story";
import { setOrigin } from "./sets";
import type { SetName } from "./sets";
import { NOINK } from "./ink";
import { cardShade, blobMaterial, CARD_K } from "./cardshade";

// ---------------- canvas pool ----------------
type Entry = { cv: HTMLCanvasElement; tex: THREE.CanvasTexture; w: number; h: number };
export type Req = { key: string; w: number; h: number; k: number; draw: (p: Pen) => void; tex?: THREE.CanvasTexture };
const makeEntry = (w: number, h: number): Entry => {
  const cv = document.createElement("canvas"); cv.width = w; cv.height = h;
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { cv, tex, w, h };
};
export class Pool {
  private live = new Map<string, Entry>(); private free: Entry[] = []; private reqs: Req[] = [];
  req(key: string, w: number, h: number, k: number, draw: (p: Pen) => void) { const r: Req = { key: `${w}x${h}|${key}`, w, h, k, draw }; this.reqs.push(r); return r; }
  flush() {
    const want = new Map<string, Req[]>();
    for (const r of this.reqs) { const l = want.get(r.key); if (l) l.push(r); else want.set(r.key, [r]); }
    for (const [key, e] of this.live) if (!want.has(key)) { this.live.delete(key); this.free.push(e); }
    for (const [key, rs] of want) {
      let e = this.live.get(key);
      if (!e) {
        const r = rs[0], i = this.free.findIndex((x) => x.w === r.w && x.h === r.h);
        e = i >= 0 ? this.free.splice(i, 1)[0] : makeEntry(r.w, r.h);
        const g = e.cv.getContext("2d")!;
        g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, e.w, e.h); g.setTransform(r.k, 0, 0, r.k, 0, 0);
        r.draw(new Pen(g)); e.tex.needsUpdate = true; this.live.set(key, e);
      }
      for (const r of rs) r.tex = e.tex;
    }
    this.reqs = [];
  }
}

// ---------------- sprite meshes ----------------
const blank = (() => { const c = document.createElement("canvas"); c.width = c.height = 2; return new THREE.CanvasTexture(c); })();
export const SU = 0.00216;
const BODY = (() => { const g = new THREE.PlaneGeometry(600 * SU, 1000 * SU); g.translate(0, (975 - 500) * SU, 0); return g; })();
const CARD = new THREE.PlaneGeometry(1, 1);
export class Actor {
  mesh: THREE.Mesh; mat: THREE.MeshLambertMaterial; dmat: THREE.MeshDepthMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D) {
    this.mat = cardShade(new THREE.MeshLambertMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide }));
    this.dmat = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.mesh = new THREE.Mesh(BODY, this.mat); this.mesh.customDepthMaterial = this.dmat;
    this.mesh.onBeforeRender = (r) => { const rt = r.getRenderTarget(); CARD_K.uPx.value = (rt ? rt.height : r.domElement.height) / 1440; };
    this.mesh.receiveShadow = true; this.mesh.visible = false; this.mesh.rotation.order = "YXZ"; this.mesh.renderOrder = 1; this.mesh.layers.set(NOINK);
    parent.add(this.mesh);
  }
  bind() { const t = this.r?.tex; if (t) { this.mat.map = t; this.dmat.map = t; } }
}
export class Fx {
  mesh: THREE.Mesh; mat: THREE.MeshBasicMaterial; soft: THREE.MeshBasicMaterial; blob: THREE.MeshBasicMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D) {
    this.mat = new THREE.MeshBasicMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.soft = new THREE.MeshBasicMaterial({ map: blank, transparent: true, depthWrite: false, side: THREE.DoubleSide });
    this.blob = blobMaterial(blank);
    this.mesh = new THREE.Mesh(CARD, this.mat); this.mesh.visible = false; this.mesh.layers.set(NOINK); parent.add(this.mesh);
  }
  use(soft: boolean, glow: number, opacity: number) {
    this.mesh.material = soft ? this.soft : this.mat;
    const m = this.mesh.material as THREE.MeshBasicMaterial; m.color.setScalar(glow); m.fog = glow <= 1; if (soft) m.opacity = opacity;
  }
  bind() {
    const t = this.r?.tex; if (!t) return;
    if (this.r!.key.includes("|blob|")) {
      if (t.generateMipmaps) { t.generateMipmaps = false; t.minFilter = THREE.LinearFilter; t.needsUpdate = true; }
      this.blob.map = t; this.mesh.material = this.blob; this.mesh.renderOrder = 0.5;
    } else { this.mat.map = t; this.soft.map = t; this.mesh.renderOrder = (this.mesh.material as THREE.Material).transparent ? 2 : 0; }
  }
}

export type Place = { key: string; draw: (p: Pen) => void; x: number; y: number; z: number; scale?: number; mirror?: boolean; yaw?: number; roll?: number; size?: [number, number, number] };
export type FxPlace = { key: string; cw: number; ch: number; draw: (p: Pen) => void; x: number; y: number; z: number; w: number; h: number; flat?: boolean; rot?: number; soft?: boolean; glow?: number; opacity?: number };
export type CamInfo = { pos: THREE.Vector3; right: THREE.Vector3 };
export type Stage = { places: Place[]; fx: FxPlace[] };

export const hh = (i: number, s = 0) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
export const q = (v: number, n = 120) => Math.round(v * n) / n;
const seedOf = (i: number) => ((i * 5 + 3) % 7) + 1;
const tier = (d: number): [number, number, number] => d < 3.2 ? [1800, 3000, 3.0] : d < 6.5 ? [1080, 1800, 1.8] : d < 16 ? [480, 800, 0.8] : [240, 400, 0.4];
const SUN = new THREE.Vector3(0.5, 0.75, -0.4).normalize();
const tmp = new THREE.Vector3();
let LNAME = "day";
const light2D = (cam: CamInfo, mirror: boolean) => { const sx = SUN.dot(cam.right) * (mirror ? -1 : 1), sy = -SUN.y; return Math.round(Math.atan2(sy, sx) / (Math.PI / 4)) * (Math.PI / 4); };
const LEAD = 2 / FPS, LID = [0.5, 1, 1, 0.5];
const lidAt = (t: number, i: number) => {
  const f = Math.round(t * FPS); let s = Math.round(-60 * hh(i, 9));
  for (let n = 0; s <= f && n < 400; n++) { const k = f - s; if (k >= 0 && k < 4) return LID[k]; s += Math.round(15 + 54 * hh(i * 31 + n, 13)); }
  return 0;
};
const fkey = (o: object) => JSON.stringify(o, (_k, v) => (typeof v === "number" ? q(v) : v));

// ---------------- the cast ----------------
// Our own 1919-1933 cast: open suits with lapels, vests, ties, patterned cloth, varied hats and body shapes. Every crowd
// extra is a different combination (rotated by index); no political insignia anywhere.
export const SK = ["#ffe2c2", "#f5c9a0", "#ecd0b6", "#e8c0a0", "#f8d8b8", "#d8a880"];
export const suit = (jacket: string, extra: Partial<Outfit> = {}): Outfit => ({ jacket, pants: jacket, boots: INK, buttons: "#c8c0b0", lapels: true, ...extra });
export const CLEM = suit("#2e2e38", { hat: "bald", hair: "#f2f2f2", moustache: "#f6f6f4", stache: "walrus", brows: "#f6f6f4", bushy: true, build: "stout",
  nose: "big", vest: "#6a5236", watch: true, tie: "#a8323a", pocket: true, pattern: "pinstripe", patCol: "#6a6a80", skin: "#f5d6bc", cheeks: true });
export const WILSON = suit("#34344a", { hat: "tophat", hatCol: "#22202a", glasses: true, build: "thin", nose: "long", pattern: "pinstripe", patCol: "#70708e",
  vest: "#d8d0c0", tie: "#3a5a9a", pocket: "#c8d8f0", skin: "#fbe4cc", brows: "#5a4a3a" });
export const LLOYD = suit("#4a3a2a", { hat: "hair", hair: "#e4e4ea", tufts: true, moustache: "#e8e8e8", stache: "handlebar", brows: "#e8e8e8", bushy: true, nose: "round",
  vest: "#7a5a3a", bowtie: "#2a5a9a", pattern: "check", patCol: "#33261a", watch: true, cheeks: true, pocket: "#e8c45a" });
export const GERMAN = suit("#3e4a3e", { hat: "bowler", hatCol: "#1e1c22", sweat: true, build: "short", tie: "#8a8a80", moustache: "#3a2a1a", stache: "pencil",
  nose: "round", vest: "#5a5a50", skin: "#f8dcc0" });
export const HITLER: Outfit = { jacket: "#7a6040", pants: "#5a4a30", boots: INK, hat: "hair", hair: "#2e2218", part: true, moustache: "brush:#2a1e14", buttons: "#c8a24a",
  tie: "#3a2a1e", waist: "#3a2a1e", pocket: false, nose: "round", skin: "#f8dcc4" };
export const BAKER: Outfit = { jacket: "#f4f4f2", pants: "#7a7a84", boots: "#4a3426", hat: "chef", moustache: "#5a3a2a", stache: "handlebar", build: "fat",
  buttons: "#c8c8c8", rolled: true, apron: "#dfe8f2", scarf: "#c8323a", cheeks: true, nose: "big", brows: "#5a3a2a", bushy: true };
const WK_BUILD: Outfit["build"][] = ["adult", "stout", "thin", "adult", "fat", "thin", "short", "adult", "stout", "adult"];
export const WORKERS: Outfit[] = [
  { jacket: "#d8cfb8", sleeves: "#d8cfb8", rolled: true, vest: "#4a3a30", hat: "flatcap", cap: "#5a5048", pants: "#4a4038", patch: "#6a5a48" },
  { jacket: "#4a5a6a", hat: "flatcap", cap: "#3a3a44", scarf: "#a8443a", pants: "#3a3a40", moustache: "#4a3426" },
  { jacket: "#c8d4e0", rolled: true, braces: "#6a3a2a", hat: "flatcap", cap: "#6a5a4a", pants: "#3a3a40", nose: "long" },
  { jacket: "#6a5a4a", pattern: "check", patCol: "#4a3a2a", hat: "flatcap", cap: "#4a4a50", scarf: "#d8c070", pants: "#3e3830" },
  { jacket: "#e8e0cc", vest: "#2a2a34", watch: true, hat: "cap", cap: "#3a3a4a", moustache: "#5a3a26", stache: "walrus", pants: "#44444c", nose: "big" },
  { jacket: "#3a4a5a", hat: "flatcap", cap: "#7a6a50", scarf: "#4a6a3a", pants: "#2e3440", pattern: "stripes", patCol: "#2e3c4c" },
  { jacket: "#b8a888", rolled: true, braces: "#2a2a2a", hat: "hair", hair: "#a0502a", freckles: true, pants: "#4a4a3a", cheeks: true },
  { jacket: "#6a4a3a", pattern: "plaid", patCol: "#3a2a20", hat: "flatcap", cap: "#2e2e34", moustache: "#3a2a1a", stache: "handlebar", pants: "#3a3430" },
  { jacket: "#d0c8b0", vest: "#5a4a3a", hat: "flatcap", cap: "#5a5a60", cigar: true, pants: "#4a4440", rolled: true },
  { jacket: "#4a4a4a", hat: "flatcap", cap: "#6a5040", apron: "#8a6a4a", pants: "#3a3a3a", moustache: "#2a2018", nose: "round" },
].map((o, v) => ({ boots: "#3a2a20", skin: SK[v % 6], build: WK_BUILD[v], buttons: "#8a7a60", ...o } as Outfit));
const M_COL = ["#2a2a34", "#3a3028", "#2a3440", "#4a4a52", "#5a4a3a", "#3a4a3a", "#4a3a4a", "#6a6a70", "#2e3a4e", "#5a3a2a", "#3e3a32", "#48505a"];
const M_PAT: Outfit["pattern"][] = [undefined, "pinstripe", "check", undefined, "plaid", "pinstripe", undefined, "check", "stripes", undefined, "pinstripe", "plaid"];
const M_HAT = ["bowler", "fedora", "bowler", "tophat", "fedora", "flatcap", "bowler", "fedora", "hair", "bowler", "fedora", "tophat"];
const M_HCOL = ["#2a2630", "#5a4a3a", "#3a3a44", "#6a5a48", "#2a3a4a", "#4a3a30"];
const M_NECK = ["#a83a3a", "#3a6aa8", "#c8a040", "#3a8a5a", "#8a3a8a", "#d86a3a"];
const M_STACHE: (Outfit["stache"] | null)[] = [null, "plain", "walrus", "handlebar", "pencil", null];
const M_BUILD: Outfit["build"][] = ["adult", "stout", "thin", "fat", "short", "adult"];
export const MEN: Outfit[] = M_COL.map((c, v) => suit(c, {
  pattern: M_PAT[v], patCol: shade(c, v % 2 ? 1.5 : 0.7), hat: M_HAT[v], hatCol: M_HCOL[v % 6], hair: ["#3a2a1a", "#8a6a4a", "#1e1a18"][v % 3], cap: "#4a4448",
  tie: v % 2 ? undefined : M_NECK[v % 6], bowtie: v % 2 ? M_NECK[(v + 2) % 6] : undefined, vest: v % 3 === 0 ? ["#7a6a5a", "#c8bca0", "#5a2a2a", "#3a4a3a"][v % 4] : undefined,
  pocket: v % 2 === 0 ? "#f0e8d8" : v % 4 === 1 ? M_NECK[(v + 1) % 6] : false, cigar: v % 4 === 1, moustache: M_STACHE[v % 6] ? ["#3a2a1a", "#6a4a2a", "#9a9a9a"][v % 3] : undefined,
  stache: M_STACHE[v % 6] ?? undefined, build: M_BUILD[v % 6], skin: SK[(v + 2) % 6], glasses: v % 5 === 3, nose: (["button", "round", "long", "big"] as const)[v % 4],
  watch: v % 3 === 0, brows: v % 6 === 2 ? "#9a9a9a" : undefined,
}));
const W_DRESS = ["#a84a5a", "#4a6a9a", "#6a8a4a", "#c8904a", "#7a4a8a", "#3a7a7a", "#c86a6a", "#d8b860"];
const W_PAT: Outfit["dressPat"][] = ["dots", undefined, "stripes", undefined, "check", "dots", undefined, "stripes"];
const W_BUILD: Outfit["build"][] = ["adult", "thin", "stout", "adult", "short", "thin", "adult", "stout"];
export const WOMEN: Outfit[] = W_DRESS.map((d, v) => ({
  jacket: [d, "#2a3a5a", "#e8dcc0", "#5a3a2a", d, "#c8b8a0", "#3a2a3a", d][v], pants: "#3a3a40", boots: ["#4a3426", "#2a2228", "#6a2a2a"][v % 3], dress: d,
  dressPat: W_PAT[v], dressCol2: v % 2 ? "#f4ecd8" : shade(d, 0.7), hat: v === 3 || v === 6 ? "hair" : "cloche", hatCol: ["#5a2a3a", "#2a3a5a", "#3a4a2a", "#8a5a2a", "#3a2a3a", "#2a4a4a", "#8a2a2a", "#6a5a3a"][v],
  band: ["#e8c45a", "#c84a4a", "#f2e2a8", "#3a2a2a", "#8ac0e0", "#e86a8a", "#2a2a2a", "#4a7a4a"][v], flower: ["#f2e2a8", "#ffffff", "#e86a8a", "#f2c84a"][v % 4],
  hair: ["#5a3a2a", "#d8b060", "#2a1e18", "#a0502a"][v % 4], skin: SK[(v + 1) % 6], pearls: v % 2 === 0, sashW: v % 3 === 1 ? shade(d, 0.65) : undefined,
  pcollar: v % 3 === 2 ? "#f8f4ea" : undefined, scarf: v === 5 ? "#c8b8a0" : undefined, cheeks: v % 2 === 1, build: W_BUILD[v], socks: v % 2 ? "#e8d0b8" : "#c8a890",
  bow: v === 3 ? "#c84a4a" : v === 6 ? "#e8c45a" : undefined,
}));
export const KIDS: Outfit[] = [
  { ...KID, hat: "flatcap", cap: "#c84a3a", shorts: true, socks: "#e8e8e8", freckles: true, cheeks: true, braces: "#5a3a2a" },
  { ...KID, jacket: "#3a7ac8", hat: "flatcap", cap: "#f2c84a", pattern: "stripes", patCol: "#f4f0e6", shorts: true, socks: "#c84a4a", cheeks: true },
  { ...KID, jacket: "#c84a7a", hat: "hair", hair: "#d8a050", cap: undefined, dress: "#e86a9a", dressPat: "dots", dressCol2: "#fff4f8", pcollar: "#ffffff", bow: "#3a8ad8", cheeks: true, freckles: true },
];
export const OFFICIAL: Outfit = suit("#3a3e4a", { pants: "#2e3038", hat: "bald", hair: "#8a8a8a", moustache: "#5a5a5a", stache: "handlebar", buttons: "#c8a24a", glasses: true,
  vest: "#8a2a2a", tie: "#e8c45a", watch: true, build: "stout", nose: "big", cigar: true, pattern: "pinstripe", patCol: "#5a6070" });
export const SOLDIER = army(US, 0, { bayonet: true });
/** Onoda, 1974: thin, stubbled, patched and faded kit, cap with neck flap, still holding his rifle */
export const ONODA = army(JP, 1, { build: "thin", worn: true, stubble: true, patch: "#c8b878", jacket: "#a89a62", pants: "#988a52", bayonet: false, webbing: "#5a4a30", nose: "round" });
/** soldiers of every army, rotated so no two neighbours match (helmets: M1 with net, Brodie, plain flared steel helmet) */
const FRONT = [US, CA, GE];
export const trooper = (i: number): [Outfit, string] => { const b = FRONT[i % 3]; return [army(b, i), `tr${i % 3}_${i % 42}`]; };
export const TR_EXPR: Expr[] = ["stern", "angry", "worried", "stern", "pained", "gasp"];
/** crowd extra i: rotate women / workers / men through every variant */
export const crowd = (i: number): [Outfit, string] => {
  const k = i % 3;
  if (k === 0) { const v = (i * 5 + 3) % WOMEN.length; return [WOMEN[v], `w${v}`]; }
  if (k === 1) { const v = (i * 7 + 1) % WORKERS.length; return [WORKERS[v], `k${v}`]; }
  const v = (i * 5 + 2) % MEN.length; return [MEN[v], `m${v}`];
};

export type Who = { i: number; o: Outfit; okey: string };
export const W_ = (o: Outfit, i: number, key: string): Who => ({ i, o, okey: key });
const person = (cam: CamInfo, w: Who, x: number, y: number, z: number, fo: FrontOpts, scale = 1, side?: { so: SideOpts; mirror: boolean }): Place => {
  const d = cam.pos.distanceTo(tmp.set(x, y + 1.2 * scale, z)) / scale;
  const [cw, ch, k] = tier(d), m = !!side?.mirror, light = light2D(cam, m), seed = seedOf(w.i);
  if (side) { const s2: SideOpts = { ...side.so, light, seed }; return { key: `S|${w.okey}|${fkey(s2)}`, x, y, z, scale, mirror: m, draw: (p) => bodySide(p, w.o, s2), size: [cw, ch, k] }; }
  const f2: FrontOpts = { ...fo, light, seed };
  return { key: `F|${w.okey}|${fkey(f2)}`, x, y, z, scale, draw: (p) => bodyFront(p, w.o, f2), size: [cw, ch, k] };
};
const toSrgb = (v: number) => { const c = clamp01(v); return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055; };
const hexOf = (c: [number, number, number], k: number) => "#" + c.map((v) => Math.round(255 * toSrgb(1 - (1 - v) * k)).toString(16).padStart(2, "0")).join("");
export const blob = (out: Stage, x: number, y: number, z: number, sc = 1) => {
  const cc = hexOf([0.22, 0.2, 0.3], 1);
  out.fx.push({ key: `blob|contact|${cc}`, cw: 128, ch: 128, draw: (p) => fxContact(p, cc), x, y: y + 0.02, z, w: 0.55 * sc, h: 0.42 * sc, flat: true });
  if (LNAME === "gloom" || LNAME === "night") return;
  const hl = Math.hypot(SUN.x, SUN.z) || 1, ox = -SUN.x / hl, oz = -SUN.z / hl, rot = Math.atan2(-ox, -oz), tc = hexOf([0.42, 0.42, 0.6], 1);
  const len = 1.2 * sc, h = len + 0.5 * sc, c = 0.3 * h;
  out.fx.push({ key: `blob|shadow|${tc}`, cw: 128, ch: 256, draw: (p) => fxShadow(p, tc), x: x + ox * c, y: y + 0.015, z: z + oz * c, w: 0.7 * sc, h, flat: true, rot });
};
export const mist = (out: Stage, x: number, y: number, z: number, w: number, t: number, i: number, col = "#e6ecf2", op = 1) =>
  out.fx.push({ key: `mist${col}`, cw: 512, ch: 256, draw: (p) => fxMist(p, col), x: x + 0.25 * Math.sin(t * 0.35 + i * 1.7), y, z, w, h: w * 0.5, soft: true, opacity: op });
export const stamp = (out: Stage, t: number, t0: number, text: string, x: number, y: number, z: number, w: number, flat = false, rot = 0) => {
  if (t < t0 - 1 / FPS) return;
  const k = 1 + 0.6 * (1 - smooth((t - t0) / (4 / FPS)));
  out.fx.push({ key: `stamp${text}`, cw: 600, ch: 260, draw: (p) => fxStamp(p, text), x, y, z, w: w * k, h: w * k * (260 / 600), flat, rot });
};

// ---------------- staging by shot ----------------
export type Ctx = { cam: CamInfo; t: number; f: number; out: Stage; O: (x: number, y: number, z: number) => [number, number, number] };
export const P = (c: Ctx, w: Who, x: number, y: number, z: number, fo: FrontOpts, scale = 1, side?: { so: SideOpts; mirror: boolean }, shadow = true) => {
  const [X, Y, Z] = c.O(x, y, z); c.out.places.push(person(c.cam, w, X, Y, Z, { blink: lidAt(c.t, w.i), ...fo }, scale, side)); if (shadow) blob(c.out, X, Y, Z, scale);
};
export const F = (c: Ctx, fx: FxPlace) => { const [X, Y, Z] = c.O(fx.x, fx.y, fx.z); c.out.fx.push({ ...fx, x: X, y: Y, z: Z }); };
export const at = (f: number) => f / FPS;

// ---- acting: beats timed to the narration (frame = word start s * 30) ----
/** [start frame, gesture (null = arms at rest), expression (sticky until the next one)] */
export type Beat = [number, Pose | null, Expr?];
type Act = { pose?: Pose; pk: number; expr: Expr };
/** the gesture + expression at time t: each gesture eases in over `ri` s and eases out just before the next one */
export const act = (t: number, beats: Beat[], ri = 0.2): Act => {
  let i = -1;
  for (let k = 0; k < beats.length; k++) if (t >= at(beats[k][0])) i = k;
  let expr: Expr = "neutral";
  for (let k = 0; k <= Math.max(i, 0); k++) if (beats[k]?.[2]) expr = beats[k][2]!;
  if (i < 0) return { pose: beats[0]?.[1] ?? undefined, pk: beats[0]?.[1] ? 1 : 0, expr };
  const b = beats[i], nx = beats[i + 1], pose = b[1] ?? undefined;
  if (!pose) return { pk: 0, expr };
  const inK = i > 0 && beats[i - 1][1] === pose ? 1 : clamp01((t - at(b[0])) / ri);
  const outK = nx && nx[1] !== pose ? clamp01((at(nx[0]) - t) / ri) : 1;
  return { pose, pk: q(Math.min(inK, outK), 10), expr };
};
/** talking: alternate two mouths ~6 times a second while the line runs */
export const talk = (t: number, a: Expr, b: Expr) => (Math.floor(t * 6.5 + 0.6 * Math.sin(t * 2.3)) % 2 ? a : b);
/** facing toward a target in the same set (screen side via the camera's right vector) */
export const toward = (c: Ctx, x: number, z: number, tx: number, tz: number): -1 | 1 =>
  (tx - x) * c.cam.right.x + (tz - z) * c.cam.right.z >= 0 ? 1 : -1;

export const DOMINO_T0 = at(53), DOMINO_DT = 0.045;
const s1 = (c: Ctx) => {
  const { t } = c, fall = clamp01((t - DOMINO_T0 + 0.05) / 0.45);
  const x = DOM0[0] + 0.12 * fall, y = 0.26 * (1 - fall * fall) + 0.02 * fall + 0.08 * Math.sin(Math.PI * fall), z = DOM0[2] - 0.05 * fall;
  P(c, W_(SOLDIER, 1, "dom"), x, y, z, { mode: fall > 0 ? "fall" : "stand", expr: t > at(46) ? "shock" : "neutral", tilt: -60 * fall }, 0.075, undefined, fall === 0);
};
const s2 = (c: Ctx) => {
  for (let i = 0; i < 6; i++) {
    const x = -1 + (i % 3) * 1.4 + hh(i) * 0.4, z = 7 + Math.floor(i / 3) * 3 - 0.9 * (c.t - at(140)) * 0;
    const [o, k] = trooper(i);
    P(c, W_(o, i, k), x, 0, z - 1.2 * (c.t - at(140)), { mode: "march", phase: q(((c.t * 1.8 + hh(i, 2)) % 1), 60), expr: TR_EXPR[i % 6], lift: 40 });
  }
  for (let i = 0; i < 6; i++) mist(c.out, -14 + i * 6, 3 + (i % 2), 32 + i * 5, 14, c.t, i, "#6a5048", 0.55);
};
const s3 = (c: Ctx) => {
  for (let i = 0; i < 4; i++) {
    const u = c.t - at(212);
    F(c, { key: "bomber", cw: 600, ch: 200, draw: fxBomber, x: -30 + i * 9 + u * 9, y: 26 + (i % 2) * 5, z: 90 + i * 6, w: 12, h: 4 });
  }
  for (let i = 0; i < 8; i++) mist(c.out, -30 + i * 8, 8 + (i % 3) * 4, 76 + (i % 2) * 6, 16, c.t, i, "#4a3e46", 0.8);
};
const s4 = (c: Ctx) => {
  if (c.f < 296) return;
  const g = smooth((c.t - at(300)) / 2.2);
  F(c, { key: `mush${q(g, 20)}`, cw: 512, ch: 640, draw: (p) => fxMushroom(p, q(g, 20)), x: 210, y: 60, z: 330, w: 110, h: 137, glow: 1.6 });
};
const s5 = (c: Ctx) => {
  P(c, W_(ONODA, 3, "onoda"), 0, 0, 4, { mode: "stand", expr: c.t > at(446) ? "stern" : "worried", look: c.t > at(410) && c.t < at(440) ? 1 : 0 });
  for (let i = 0; i < 5; i++) mist(c.out, -4 + i * 2, 0.4, 6 + (i % 2) * 2, 4, c.t, i, "#d8e8c8", 0.5);
};
// Paris
const LEADERS: [Outfit, number, number, string][] = [[CLEM, 0, 11.0, "clem"], [WILSON, -1.3, 10.8, "wilson"], [LLOYD, 1.3, 10.8, "lloyd"]];
const GER_A: [number, number] = [6.35, -2.3], GER_B: [number, number] = [0.05, 1.0];
/** eight delegates down the table, each a different suit, each with their own idle business */
const DL_POSE: (Pose | null)[] = ["cross", "chin", "hips", null, "cross", "chin", null, "hips"];
const DL_PROP: FrontOpts["prop"][] = [null, null, null, "paper", null, null, "news", null];
const delegates = (c: Ctx, ger: [number, number], from = 1e9, react: Expr = "scheme") => {
  for (let i = 0; i < 8; i++) {
    const s = i % 2 ? 1 : -1, z = 3 + Math.floor(i / 2) * 1.8, v = (i * 5 + 1) % MEN.length, late = c.t > at(from + i * 3);
    const pose = late && i % 3 === 0 ? "point" : DL_POSE[i] ?? undefined, f = late && i % 3 === 0 ? toward(c, s * 2.1, z, ger[0], ger[1]) : ((-s) as -1 | 1);
    P(c, W_(MEN[v], 40 + i, `m${v}`), s * 2.1, 0, z, { mode: "stand", expr: late ? (i % 2 ? react : "laugh") : i % 3 ? "smug" : "stern", facing: f, pose, prop: DL_PROP[i] });
  }
};
const parisLeaders = (c: Ctx, beats: Beat[][], prop?: number, ger: [number, number] = GER_B) =>
  LEADERS.forEach(([o, x, z, k], i) => {
    const a = act(c.t, beats[i]);
    P(c, W_(o, 30 + i, k), x, 0, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: prop === i ? "paper" : null,
      facing: a.pose === "point" ? toward(c, x, z, ger[0], ger[1]) : 0 });
  });
const s9 = (c: Ctx) => {
  // "...World War One is finally over, and the winners meet in Paris to decide what happens to Germany"
  parisLeaders(c, [
    [[825, "cross", "stern"], [943, "hips", "smug"], [1004, "point", "shout"]],
    [[825, "chin", "smug"], [971, "pointUp", "smug"]],
    [[825, "hips", "smug"], [929, "shrug", "grin"], [1001, "cross", "scheme"]],
  ], undefined, GER_A);
  delegates(c, GER_A, 1004);
  const a = act(c.t, [[825, "collar", "nervous"], [1004, "palms", "panic"]]);
  P(c, W_(GERMAN, 20, "ger"), 6.35, 0, -2.3, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: -1 }, 0.82);
};
const s10 = (c: Ctx) => {
  // "Spoiler: nothing good."
  const a = act(c.t, [[1027, "collar", "nervous"], [1045, "head", "shock"]], 0.12);
  P(c, W_(GERMAN, 20, "ger"), 6.35, 0, -2.3, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: -1 }, 0.82);
};
const s11 = (c: Ctx) => {
  const { t } = c;
  // "Germany has to admit the war was its fault, give up land, shrink its army to just one hundred thousand men, and pay for the damage"
  parisLeaders(c, [
    [[1071, "cross", "stern"], [1123, "point", "shout"], [1172, "hips", "smug"], [1255, "point", "scheme"]],
    [[1071, "chin", "smug"], [1201, "pointUp", "stern"], [1258, "cross", "smug"]],
    [[1071, "cross", "stern"], [1152, "point", "scheme"], [1220, "hips", "grin"]],
  ], t > at(1255) ? 0 : undefined);
  delegates(c, GER_B, 1132, "grin");
  const a = act(t, [[1071, "palms", "nervous"], [1132, "collar", "worried"], [1145, "head", "gasp"], [1190, "head", "panic"], [1255, "palms", "shock"]], 0.15);
  P(c, W_(GERMAN, 20, "ger"), 0.05, 0, 1.0, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: t < at(1140) ? "paper" : null }, 0.82);
  if (c.f >= 1140 && c.f < 1250) {
    const k = smooth((t - at(1147)) / 0.5);
    F(c, { key: `mapcut${q(k, 20)}`, cw: 512, ch: 512, draw: (p) => fxMapCut(p, q(k, 20)), x: -0.15, y: 0.815, z: 2.65, w: 0.75, h: 0.75, flat: true, rot: Math.PI });
    for (let i = 0; i < 12; i++) {
      const down = i >= 2 && t > at(1190) + (i - 2) * 0.06, u = down ? smooth((t - at(1190) - (i - 2) * 0.06) / 0.18) : 0;
      const [to, tk] = trooper(i);
      P(c, W_(to, 60 + i, `toy${tk}`), 0.35 + (i % 6) * 0.09, 0.8 + 0.02 * u, 2.95 + Math.floor(i / 6) * 0.12, { mode: "stand", expr: u > 0 ? "shock" : TR_EXPR[i % 6], tilt: 85 * u }, 0.08, undefined, false);
    }
  }
};
const s12 = (c: Ctx) => {
  const { t } = c;
  // "The bill is so big that Germany is still technically paying it off ... in twenty ten"
  const a = act(t, [[1290, "palms", "shock"], [1318, "head", "panic"], [1405, "shrug", "dazed"]], 0.15);
  P(c, W_(GERMAN, 20, "ger"), 0.05, 0, 1.0, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk }, 0.82);
  parisLeaders(c, [
    [[1290, "hips", "smug"], [1366, "hips", "laugh"]],
    [[1290, "cross", "smug"], [1410, "pointUp", "grin"]],
    [[1290, "chin", "smug"], [1384, "point", "laugh"]],
  ]);
  stamp(c.out, t, at(1410), "PAID\nIN 2010", ...c.O(0.06, 0.035, -2.6), 1.5, true, Math.PI);
};
// press
const s13 = (c: Ctx) => {
  const { t } = c;
  // "The money runs out fast. To pay its bills ... does the obvious thing. It prints more money. Then more. Then a lot more."
  const a = act(t, [[1435, "shrug", "worried"], [1491, "chin", "neutral"], [1553, "pointUp", "scheme"], [1584, "point", "grin"], [1619, "armsUp", "cheer"], [1639, "cheer", "beam"], [1648, "armsUp", "laugh"]]);
  P(c, W_(OFFICIAL, 70, "off"), 2.3, 0, 1.7, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: a.pose === "point" ? toward(c, 2.3, 1.7, -2.6, 1.6) : 0 });
  const b = act(t, [[1435, "hips", "stern"], [1595, "cheer", "beam"], [1620, "shrug", "shock"], [1648, "head", "panic"]]);
  P(c, W_(WORKERS[1], 71, "k1"), -2.6, 0, 1.6, { mode: "stand", expr: b.expr, pose: b.pose, pk: b.pk, prop: "cash", facing: 1 });
  const n = Math.floor(6 + 30 * smooth((t - at(1440)) / 7));
  for (let i = 0; i < n; i++) {
    const age = ((t * 0.6 + hh(i, 1)) % 1.4) / 1.4, a = hh(i, 2) * Math.PI * 2;
    F(c, { key: `note${i % 3}`, cw: 300, ch: 150, draw: (p) => fxBanknote(p, i % 3), x: Math.cos(a) * (0.5 + 2.4 * age), y: 1.8 + 1.2 * age - 2.2 * age * age, z: 2.4 + Math.sin(a) * (0.4 + 1.6 * age) - 1.2 * age, w: 0.3, h: 0.15, rot: age * 9 + i });
  }
};
const s26 = (c: Ctx) => {
  const k = smooth((c.t - at(3362)) / 0.9);
  F(c, { key: `paper${q(k, 20)}`, cw: 400, ch: 520, draw: (p) => fxNewspaper(p, q(k, 20)), x: 3.8, y: 0.915, z: 2.0, w: 0.5, h: 0.65, flat: true, rot: Math.PI + 0.15 });
  // "newspapers are controlled"
  const a = act(c.t, [[3355, "cross", "stern"], [3384, "point", "scheme"]]);
  P(c, W_(OFFICIAL, 70, "off"), 4.6, 0, 2.6, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: a.pose === "point" ? toward(c, 4.6, 2.6, 3.8, 2.0) : 0 });
};
// bakery
export const tagAt = (f: number) => (f < 1858 ? "200.000.000.000 M" : f < 1890 ? "350.000.000.000 M" : "500.000.000.000 M");
const s14 = (c: Ctx) => {
  // "By 1923 a single loaf of bread costs two hundred billion marks"
  const a = act(c.t, [[1672, "hips", "smug"], [1712, "cheer", "proud"], [1762, "hips", "scheme"], [1786, "cheer", "beam"]]);
  P(c, W_(BAKER, 72, "baker"), 0.9, 0, 3.0, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: "bread" });
  const b = act(c.t, [[1672, "chin", "worried"], [1747, "palms", "gasp"], [1786, "head", "shock"]], 0.15);
  P(c, W_(WOMEN[0], 73, "w0"), -2.3, 0, -0.9, { mode: "stand", expr: b.expr, pose: b.pose, pk: b.pk, facing: 1 });
};
const s15 = (c: Ctx) => {
  const { t } = c, u = smooth((t - at(1815)) / 1.6);
  // "People are paid twice a day so they can shop before prices go up again"
  const a = act(t, [[1815, "hips", "smug"], [1882, "cheer", "scheme"], [1903, "pointUp", "beam"]]);
  P(c, W_(BAKER, 72, "baker"), 0.9, 0, 3.0, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: "bread" });
  const b = act(t, [[1815, null, "grin"], [1837, "cheer", "beam"], [1860, "shrug", "shock"], [1890, "head", "panic"]], 0.15);
  P(c, W_(WORKERS[0], 74, "k0"), -4 + 3.4 * u, 0, -1.0 + 2.0 * u, { mode: u < 1 ? "march" : "stand", phase: q((t * 2.2) % 1, 60), expr: b.expr, pose: b.pose, pk: b.pk, prop: "cash", lift: 70 });
  const w = act(t, [[1815, "collar", "nervous"], [1890, "palms", "gasp"]]);
  P(c, W_(WOMEN[0], 73, "w0"), -3.4, 0, 0.8, { mode: "stand", expr: w.expr, pose: w.pose, pk: w.pk, facing: 1 });
};
// playroom
const s16 = (c: Ctx) => {
  const { t } = c;
  // "Kids use stacks of cash as building blocks because it's cheaper than buying toys"
  const a = act(t, [[1930, null, "grin"], [2040, "head", "shock"]], 0.12);
  P(c, W_(KIDS[0], 80, "kid0"), -0.55, 0, 0.6, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, wave: t < at(2040) ? q(Math.sin(t * 3), 10) : undefined }, 0.72);
  const b = act(t, [[1930, "hips", "smile_closed"], [1978, "cheer", "beam"], [2010, "hips", "proud"], [2040, "point", "laugh"]], 0.15);
  P(c, W_(KIDS[2], 81, "kid2"), 0.65, 0, 0.75, { mode: "stand", expr: b.expr, pose: b.pose, pk: b.pk, facing: b.pose === "point" ? toward(c, 0.65, 0.75, -0.55, 0.6) : 0 }, 0.72);
  const n = Math.min(14, 3 + Math.floor((t - at(1930)) * 3.2)), fallT = at(2040);
  for (let i = 0; i < n; i++) {
    const u = t > fallT ? smooth((t - fallT - i * 0.02) / 0.5) : 0, side = i % 2 ? 1 : -1;
    F(c, { key: `bundle${i % 3}`, cw: 300, ch: 150, draw: (p) => fxBanknote(p, i % 3), x: 0.08 + (i % 2 ? 0.04 : -0.04) + side * 0.6 * u * (i / 14), y: 0.07 + i * 0.105 - (i * 0.105) * u, z: 0.95 - 0.3 * u * (i / 14), w: 0.34, h: 0.12, rot: side * 1.4 * u * (i / 14) });
  }
};
// street
const STR_PROP: FrontOpts["prop"][] = ["cane", null, "news", null, "case", null];
const s17 = (c: Ctx) => {
  const { t } = c;
  // "Things calm down for a few years": a dancing couple, strollers with canes and papers
  for (let i = 0; i < 2; i++) P(c, W_(i ? WOMEN[1] : MEN[4], 90 + i, i ? "w1" : "m4"), -1.2 + i * 0.55 + 0.1 * Math.sin(t * 4), 0, 3.5, { mode: "stroll", phase: q((t * 1.4 + i * 0.5) % 1, 60), expr: i ? "laugh" : "beam", wave: q(Math.sin(t * 5 + i), 10), prop: i ? null : "cane" });
  for (let i = 0; i < 6; i++) {
    const [o, k] = i % 2 ? [WOMEN[(i * 3) % 8], `w${(i * 3) % 8}`] as const : [MEN[(i * 5 + 1) % 12], `m${(i * 5 + 1) % 12}`] as const;
    P(c, W_(o, 92 + i, k), (i % 2 ? -1 : 1) * (2.5 + hh(i) * 2), 0, 6 + i * 2.5 - (t - at(2057)) * 0.6 * (i % 2 ? 1 : -1), { mode: "stroll", phase: q((t * 0.9 + hh(i, 4)) % 1, 60), expr: (["smile", "grin", "smile_closed"] as Expr[])[i % 3], prop: STR_PROP[i] });
  }
};
const s18 = (c: Ctx) => {
  const { t } = c, crashed = t > at(2166) - LEAD;
  const prog = clamp01((t - at(2111)) / 1.7), crash = clamp01((t - at(2166)) / 0.25);
  F(c, { key: `chart${q(prog, 30)}${q(crash, 10)}`, cw: 1024, ch: 512, draw: (p) => fxChart(p, q(prog, 30), q(crash, 10)), x: 0, y: 2.75, z: 6.72, w: 5.6, h: 2.8, glow: 1.1 });
  // "Then in 1929 the American stock market crashes, and the whole world goes broke with it"
  const before: Beat[][] = [
    [[2111, "hips", "smug"], [2141, "cheer", "beam"]], [[2111, "cross", "smug"]], [[2111, null, "grin"]],
    [[2111, "armsUp", "cheer"]], [[2111, "hips", "proud"]], [[2111, "chin", "scheme"], [2149, "fist", "beam"]],
  ];
  const after: Beat[][] = [
    [[2166, "head", "panic"]], [[2166, "palms", "gasp"], [2228, "shrug", "sad"]], [[2166, "head", "shock"]],
    [[2166, "head", "shock"], [2252, "shrug", "weep"]], [[2166, "palms", "panic"], [2239, "head", "worried"]], [[2166, "collar", "gasp"], [2259, "shrug", "sad"]],
  ];
  for (let i = 0; i < 6; i++) {
    const x = -4.5 + (i % 4) * 3 + (i >= 4 ? 1.5 : 0), z = i >= 4 ? 0.4 : 1.4, v = (i * 7 + 3) % MEN.length;
    if (c.f >= 2226 && i === 2) continue;
    const a = act(t, crashed ? after[i] : before[i], 0.12);
    P(c, W_(MEN[v], 100 + i, `m${v}`), x, 0, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: !crashed && i === 2 ? "news" : null });
  }
  if (c.f >= 2226) { const v = (2 * 7 + 3) % MEN.length, a = act(t, [[2226, "shrug", "sad"], [2259, "head", "weep"]]); P(c, W_(MEN[v], 102, `m${v}`), 1.5, 0, 1.4, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk }); }
};
const Q_POSE: (Pose | null)[] = ["cross", null, "hips", null, "chin", "cross", null];
const s19 = (c: Ctx) => {
  // "In Germany six million people lose their jobs": a long dole queue, every man different
  for (let i = 0; i < 14; i++) {
    const v = (i * 3 + 1) % WORKERS.length;
    P(c, W_(WORKERS[v], 110 + i, `k${v}`), 7.3 + (hh(i) - 0.5) * 0.3, 0.15, 23.5 - i * 0.9, { mode: "stand", expr: (["sad", "worried", "sad", "dazed", "weep", "sad", "stern"] as Expr[])[i % 7],
      look: Math.round(hh(i, 3) * 2 - 1), pose: Q_POSE[i % 7] ?? undefined, prop: i % 5 === 2 ? "news" : null });
  }
};
const s20 = (c: Ctx) => {
  const { t } = c;
  // "when people are hungry, angry and scared, they start listening to anyone who sounds sure of himself"
  for (let i = 0; i < 26; i++) {
    const x = (hh(i) - 0.5) * 8, z = 25 + hh(i, 2) * 6.5, [o, k] = crowd(i), r = i % 3;
    const beats: Beat[] = [[2384, r === 0 ? "cross" : null, "sad"], [2404, r === 1 ? "head" : r === 0 ? "cross" : null, r === 1 ? "worried" : "sad"],
      [2425 + (i % 4) * 2, r === 2 ? "fists" : "fist", "angry"], [2443 + (i % 3) * 2, r === 0 ? "head" : r === 1 ? "palms" : "fist", r === 2 ? "furious" : "panic"],
      [2474 + (i % 5) * 3, r === 1 ? "cross" : r === 2 ? "fist" : "chin", r ? "stern" : "angry"]];
    const a = act(t, beats, 0.15);
    P(c, W_(o, 130 + i, k), x, 0, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk });
  }
  const h = act(t, [[2384, "fist"], [2489, "point"], [2507, "pointUp"], [2526, "hips"]], 0.15);
  P(c, W_(HITLER, 9, "hit"), 0, 0.55, 34.2, { mode: "stand", expr: t > at(2526) ? "proud" : talk(t, "shout", "furious"), pose: h.pose, pk: h.pk });
};
const s21 = (c: Ctx) => {
  const { t } = c;
  // "Enter Adolf Hitler. A failed art student who was rejected by a Vienna art school - twice."
  const a = act(t, [[2547, "hips", "proud"], [2600, "palms", "nervous"], [2627, null, "sad"], [2678, "fist", "furious"]], 0.15);
  P(c, W_(HITLER, 9, "hit"), -0.4, 0, 0.45, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: "brush" });
  F(c, { key: "canvas", cw: 600, ch: 460, draw: (p) => { p.poly([[10, 10], [590, 10], [590, 450], [10, 450]], "#f2ead8", 10); p.g.fillStyle = "#9cc4e8"; p.g.fillRect(30, 30, 540, 200); p.g.fillStyle = "#6a9a4a"; p.g.fillRect(30, 230, 540, 200); p.poly([[220, 250], [380, 250], [380, 360], [220, 360]], "#f2e2b2", 5); p.poly([[200, 250], [300, 170], [400, 250]], "#b8463c", 5); }, x: 0.4, y: 1.22, z: 0.78, w: 0.85, h: 0.65 });
  stamp(c.out, t, at(2627), "REJECTED", ...c.O(0.36, 1.32, 0.72), 0.75);
  stamp(c.out, t, at(2678), "REJECTED", ...c.O(0.46, 1.1, 0.71), 0.75);
};
const BM_IDLE: (Pose | null)[] = ["hips", null, "cross", "chin", null, "hips"];
const s22 = (c: Ctx) => {
  const { t } = c;
  // "...came home furious and joined a tiny political party that met in the back room of a beer hall"
  for (let i = 0; i < 6; i++) {
    const [o, k] = i % 2 ? [WORKERS[(i * 3) % 10], `k${(i * 3) % 10}`] as const : [MEN[(i * 5 + 4) % 12], `m${(i * 5 + 4) % 12}`] as const;
    const a = act(t, [[2707, BM_IDLE[i], i % 3 ? "smug" : "neutral"], [2857 + i * 3, "cheer", i % 2 ? "laugh" : "beam"], [2895, "hips", i % 2 ? "smug" : "grin"]], 0.15);
    P(c, W_(o, 150 + i, k), (i < 3 ? -3.5 : 3.5) + (i % 3 - 1) * 0.9, 0, 7.4, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: "stein" });
  }
  if (t < at(2800)) {
    const u = smooth((t - at(2707)) / 3.0), a = act(t, [[2707, null, "angry"], [2767, "fist", "furious"]], 0.15);
    P(c, W_(HITLER, 9, "hit"), -5 + 4.6 * u, 0, 6 + 3.4 * u, { mode: u < 1 ? "march" : "stand", phase: q((t * 1.8) % 1, 60), expr: a.expr, pose: a.pose, pk: a.pk, lift: 50 });
  } else {
    const a = act(t, [[2800, "fist"], [2829, "pointUp"], [2857, "point"], [2878, "fists"]], 0.15);
    P(c, W_(HITLER, 9, "hit"), 0, 0.55, 10.6, { mode: "stand", expr: talk(t, "shout", "yell"), pose: a.pose, pk: a.pk });
  }
};
const s23 = (c: Ctx) => {
  const { t } = c, cheer = t > at(3119) - LEAD, grown = clamp01((t - at(2902)) / 4);
  const n = Math.floor(14 + 36 * grown);
  // "...he tells Germans exactly what they want to hear: none of this was your fault, it was someone else's,
  //  and I'll make Germany powerful again"
  const IDLE: (Pose | null)[] = ["cross", "hips", null, "chin", "cross", null, "hips"];
  for (let i = 0; i < n; i++) {
    const x = (hh(i, 5) - 0.5) * 12, z = 0.5 + hh(i, 6) * 8.5, [o, k] = crowd(i), r = i % 3, stein = i % 5 === 1;
    const a = act(t, [[2902, IDLE[i % 7], i % 3 ? "stern" : "smug"], [3062 + (i % 6) * 2, i % 4 === 0 ? "fist" : IDLE[i % 7], i % 4 === 0 ? "angry" : i % 3 ? "stern" : "smug"],
      [3119 + (i % 5) * 2, r === 0 ? "armsUp" : r === 1 ? "cheer" : "fists", i % 2 ? "cheer" : "laugh"]], 0.15);
    P(c, W_(o, 160 + i, k), x, 0, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: stein ? "stein" : null });
  }
  const h = act(t, [[2902, "hips"], [2956, "pointUp"], [2981, "palms"], [3032, "point"], [3076, "shrug"], [3082, "point"], [3111, "fist"], [3130, "fists"], [3162, "fist"]], 0.15);
  P(c, W_(HITLER, 9, "hit"), 0, 0.55, 10.6, { mode: "stand", expr: t < at(2930) ? "proud" : talk(t, "shout", t > at(3118) ? "yell" : "scheme"), pose: h.pose, pk: h.pk,
    facing: h.pose === "point" ? (t > at(3082) ? -1 : 1) : 0 });
};
const torches = (c: Ctx, n: number, z0: number) => {
  for (let i = 0; i < n; i++) {
    const x = (hh(i, 7) - 0.5) * 9, z = z0 + hh(i, 8) * 9, k = i % 2 ? (i * 7 + 1) % 10 : (i * 5 + 2) % 12, o = i % 2 ? WORKERS[k] : MEN[k];
    const torch = i % 2 === 0, sway = q(0.5 + 0.5 * Math.sin(c.t * 3 + i), 5);
    P(c, W_(o, 200 + i, i % 2 ? `k${k}` : `m${k}`), x, 0, z, { mode: "stand", expr: torch ? (i % 3 ? "stern" : "proud") : (["cheer", "stern", "yell"] as Expr[])[i % 3],
      prop: torch ? "torch" : null, pose: torch ? undefined : i % 4 === 1 ? "fist" : "cheer", pk: torch ? 1 : 0.6 + 0.4 * sway });
    if (torch) F(c, { key: `flame${q((c.t * 3 + i) % 1, 6)}`, cw: 160, ch: 320, draw: (p) => fxFlame(p, q((c.t * 3 + i) % 1, 6) * 6), x: x + 0.35, y: 1.9, z: z - 0.05, w: 0.3, h: 0.6, glow: 2.2 });
  }
};
const s24 = (c: Ctx) => {
  torches(c, 30, 31);
  // "In January 1933 he becomes Chancellor of Germany"
  const a = act(c.t, [[3182, "hips", "smug"], [3250, "fist", "proud"]]);
  P(c, W_(HITLER, 9, "hit"), 0, 6.3, 45.3, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk }, 1, undefined, false);
};
const s25 = (c: Ctx) => F(c, { key: "padlock", cw: 400, ch: 400, draw: fxPadlock, x: 5.98, y: 1.45, z: 26, w: 1.3, h: 1.3 });
const s27 = (c: Ctx) => {
  const u = (c.t - at(3405)) * 0.55;
  // "the people he blamed are being pushed out of public life"
  const fam: [Outfit, string, number, number, Expr][] = [[MEN[1], "m1", 0, 1, "sad"], [WOMEN[2], "w2", 0.7, 1, "worried"], [KIDS[0], "k0", 0.35, 0.72, "weep"], [KIDS[2], "k2", 1.05, 0.72, "sad"]];
  fam.forEach(([o, k, dx, sc, e], i) => P(c, W_(o, 220 + i, `fam${k}`), -7.6 + dx, 0.15, 21.5 - u - (i >= 2 ? 0.7 : 0), { mode: "stroll", phase: q((c.t * 0.8 + i * 0.25) % 1, 60), expr: e, prop: i < 2 ? "case" : null }, sc));
};
const s28 = (c: Ctx) => {
  torches(c, 14, 33);
  P(c, W_(HITLER, 9, "hit"), 0, 6.3, 45.3, { mode: "stand", expr: "smug", pose: "hips" }, 1, undefined, false);
  F(c, { key: "bigshadow", cw: 600, ch: 1000, draw: (p) => { bodyFront(p, HITLER, { mode: "stand", expr: "smug", seed: 2, pose: "hips" }); const g = p.g; g.globalCompositeOperation = "source-in"; g.fillStyle = "rgba(4,2,8,0.92)"; g.fillRect(0, 0, 600, 1000); g.globalCompositeOperation = "source-over"; },
    x: 1.6, y: 10.5, z: 45.92, w: 9, h: 15, soft: true, opacity: 1 });
};

const STAGE: Record<number, (c: Ctx) => void> = { 1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 9: s9, 10: s10, 11: s11, 12: s12, 13: s13, 14: s14, 15: s15, 16: s16, 17: s17, 18: s18, 19: s19, 20: s20,
  21: s21, 22: s22, 23: s23, 24: s24, 25: s25, 26: s26, 27: s27, 28: s28 };

/** stage any shot table: used by the chapter modules (ch/chNN.ts); origin = the set's world offset */
export const stageWith = (fn: ((c: Ctx) => void) | undefined, light: string, o: [number, number, number], f: number, cam: CamInfo, sun: THREE.Vector3): Stage => {
  const out: Stage = { places: [], fx: [] };
  LNAME = light; SUN.copy(sun);
  const O = (x: number, y: number, z: number): [number, number, number] => [o[0] + x, o[1] + y, o[2] + z];
  fn?.({ cam, t: f / FPS, f, out, O });
  return out;
};
export const stage = (id: number, f: number, cam: CamInfo, sun: THREE.Vector3): Stage => {
  const out: Stage = { places: [], fx: [] }, s = SHOTS[id - 1], o = setOrigin(s.set as SetName);
  LNAME = s.light; SUN.copy(sun);
  const O = (x: number, y: number, z: number): [number, number, number] => [o[0] + x, o[1] + y, o[2] + z];
  STAGE[id]?.({ cam, t: f / FPS, f, out, O });
  return out;
};
export type { V3 };
// ---- WW2 figures (chapters 2-14) ----
// Leaders: recognisable caricatures from silhouette, face and props only; no insignia, armbands or party emblems.
export const CHURCHILL = suit("#2a2a34", { hat: "homburg", hatCol: "#1e1e24", band: "#141418", build: "fat", jowls: true, cigar: true, bowtie: "#24346e", tieDots: "#f4f4f2",
  vest: "#34343e", watch: true, pattern: "pinstripe", patCol: "#55556a", skin: "#ffd9c6", cheeks: true, nose: "round", brows: "#c8a888", hair: "#e6d2bc", pocket: "#f4f0e6" });
/** Churchill without the hat: bald dome, wispy side tufts */
export const CHURCHILL_BARE: Outfit = { ...CHURCHILL, hat: "bald", tufts: true };
export const STALIN: Outfit = { jacket: "#8c8268", pants: "#7a7058", boots: INK, tallBoots: true, hat: "swept", hair: "#5a4a3c", moustache: "#4a3a2c", stache: "walrus",
  brows: "#4a3a2c", bushy: true, pipe: "briar", nose: "big", skin: "#f0cfae", build: "stout", tunic: true, buttons: "#6a604a", belt: null, stubble: false };
/** Stalin in a marshal's greatcoat and peaked cap (Yalta / Potsdam) */
export const STALIN_COAT: Outfit = { ...STALIN, coat: "#8c8268", hat: "peaked", cap: "#8c8268", band: "#c8202c", visor: INK, star: true, starCol: "#c8202c", boards: "#e8c45a" };
export const ROOSEVELT = suit("#3a4050", { hat: "swept", hair: "#c4c4ca", pince: true, holder: true, cape: "#2a3042", tie: "#7a2a3a", nose: "round", jaw: true,
  skin: "#f8dcc8", brows: "#a0a0a8", pocket: "#f4f0e6" });
export const ROOSEVELT_HAT: Outfit = { ...ROOSEVELT, hat: "fedora", hatCol: "#5a5a60", band: "#2a2a30" };
/** Mussolini: black shirt and tie, grey jodhpurs, tall boots, plain black tasselled cap (no emblem), jutting jaw */
export const MUSSOLINI: Outfit = { jacket: "#1e1c22", sleeves: "#1e1c22", pants: "#4a4a52", boots: INK, tallBoots: true, hat: "fez", hatCol: "#141216", jaw: true, build: "stout",
  tie: "#121014", shirt: "#26242a", waist: "#2a2420", buttons: "#3a3a40", skin: "#f0c8a0", brows: "#2a2018", bushy: true, nose: "round" };
export const MUSSOLINI_BARE: Outfit = { ...MUSSOLINI, hat: "bald" };
export const CHAMBERLAIN = suit("#22222a", { build: "thin", hat: "hair", hair: "#c8c8cc", part: true, moustache: "#9a9aa0", stache: "plain", wing: true, tie: "#3a3a48",
  vest: "#22222a", watch: true, umbrella: true, nose: "long", brows: "#8a8a90", bushy: true, skin: "#f8e0cc", pocket: "#f4f0e6", pattern: "pinstripe", patCol: "#4a4a58" });
export const CHAMBERLAIN_HAT: Outfit = { ...CHAMBERLAIN, hat: "homburg", hatCol: "#1e1e24", part: false };
export const DEGAULLE: Outfit = { jacket: "#8a7a56", pants: "#8a7a56", boots: "#3a2a1c", tallBoots: true, hat: "kepi", cap: "#6e6046", band: "#c8a24a", build: "tall", nose: "long",
  tunic: true, lapels: true, tie: "#6a5a3a", shirt: "#c8b890", buttons: "#c8a24a", waist: "#5a3a22", moustache: "#3a2a1a", stache: "pencil", skin: "#f6dcc4", brows: "#3a2a1a" };
/** Hitler in wartime: plain field-grey jacket, shirt and tie, no armband or insignia; side parting, toothbrush moustache */
export const HITLER_WAR: Outfit = { jacket: "#66685a", pants: "#2e2e30", boots: INK, tallBoots: true, hat: "hair", hair: "#2e2218", part: true, moustache: "brush:#2a1e14",
  lapels: true, tunic: true, tie: "#2a2420", shirt: "#f0ece2", buttons: "#8a8c80", nose: "round", skin: "#f4d8c0" };
/** Hitler 1945: greying, pale, eye bags and forehead lines (stoop him with tilt / headTilt) */
export const HITLER_OLD: Outfit = { ...HITLER_WAR, hair: "#4c443e", haggard: true, skin: "#e6d2c4", brows: "#4c443e", moustache: "brush:#3a302a", jacket: "#5e6054" };
export const TRUMAN = suit("#4a4a54", { hat: "fedora", hatCol: "#7a7468", band: "#3a3430", glasses: true, bowtie: "#2a3a6a", tieDots: "#f4f0e6", pocket: "#f4f0e6", nose: "round",
  skin: "#f8dcc4", hair: "#8a8a8e", brows: "#6a6a6e" });
export const TRUMAN_BARE: Outfit = { ...TRUMAN, hat: "hair", hair: "#9a9aa0", part: true };
/** Eisenhower: short "Ike" jacket, peaked cap, ribbons; give him the "grin" */
export const EISENHOWER: Outfit = { jacket: "#6a6044", pants: "#8a7656", boots: "#5a3a22", hat: "peaked", cap: "#6a6044", band: "#5a5038", visor: "#4a3020", badge: "#e8c45a",
  tunic: true, lapels: true, tie: "#7a6a48", shirt: "#8a7a58", buttons: "#8a7a50", boards: "#6a6044", medals: 6, skin: "#f8dcc4", nose: "round", brows: "#b8a888", waist: "#6a6044" };
export const EISENHOWER_BARE: Outfit = { ...EISENHOWER, hat: "bald", hair: "#d8c8b0", tufts: true };
export const MACARTHUR: Outfit = { jacket: "#c8b48a", pants: "#c8b48a", boots: "#5a3a22", hat: "peaked", cap: "#a89060", band: "#6a5a3a", visor: "#3a2a1a", braid: true, badge: "#e8c45a",
  aviators: true, pipe: "corncob", nose: "long", jaw: true, skin: "#f2d4b8", build: "thin", tunic: true, buttons: "#8a7a50", boards: "#e8c45a" };
export const MONTGOMERY: Outfit = { jacket: "#7a7a72", pants: "#9a8a60", boots: "#3a2a20", hat: "beret", hatCol: "#1e1c24", badge: "#c8ccd4", build: "thin", nose: "long",
  moustache: "#9a8a70", stache: "pencil", skin: "#f8dcc4", brows: "#8a7a60", tunic: true, buttons: "#5a5a54", shirt: "#c8b48a", scarf: "#c8b48a" };
export const ZHUKOV: Outfit = { jacket: "#6a6a48", pants: "#3a3a4a", boots: INK, tallBoots: true, hat: "peaked", cap: "#6a6a48", band: "#c8202c", visor: INK, star: true, starCol: "#c8202c",
  build: "stout", medals: 14, boards: "#e8c45a", tunic: true, buttons: "#e8c45a", jaw: true, nose: "round", skin: "#f2d4b0", brows: "#5a4a3a", waist: "#5a3a22" };
/** Tojo: bald, round glasses, moustache, Japanese officer khaki (cap variant TOJO_CAP) */
export const TOJO: Outfit = { jacket: "#8a7a48", pants: "#8a7a48", boots: "#3a2a1a", tallBoots: true, hat: "bald", glasses: true, moustache: "#2a2420", stache: "plain", tunic: true,
  buttons: "#c8a24a", boards: "#c8202c", medals: 3, skin: "#f2d0a8", nose: "round", brows: "#2a2420", build: "short", waist: "#5a3a22" };
export const TOJO_CAP: Outfit = { ...TOJO, hat: "peaked", cap: "#8a7a48", band: "#c8202c", visor: "#3a2a1a", star: true, starCol: "#e8c45a" };
/** Rommel (Desert Fox): field grey, peaked cap, light scarf; Stauffenberg: officer with an eye patch */
export const ROMMEL: Outfit = { jacket: "#6a6e5e", pants: "#5a5e50", boots: INK, tallBoots: true, hat: "peaked", cap: "#6a6e5e", band: "#3a4a3a", visor: INK, saddle: true, badge: "#c8ccd4",
  scarf: "#e8e0cc", tunic: true, buttons: "#8a8c80", boards: "#c8ccd4", medals: 4, nose: "round", jaw: true, skin: "#f6d8c0", brows: "#5a4a3a" };
export const STAUFFENBERG: Outfit = { ...ROMMEL, scarf: undefined, eyepatch: true, jaw: false, build: "thin", nose: "long", hat: "hair", hair: "#3a2a1e", part: true, medals: 2 };
/** Paulus at Stalingrad: gaunt, greatcoat, stubble */
export const PAULUS: Outfit = { ...ROMMEL, scarf: undefined, coat: "#5e6254", jacket: "#5e6254", haggard: true, stubble: true, build: "thin", nose: "long", jaw: false, medals: 2 };
export const HIROHITO: Outfit = suit("#1e1e26", { hat: "hair", hair: "#1e1a18", glasses: true, moustache: "#1e1a18", stache: "pencil", build: "thin", skin: "#f2d0a8", nose: "button", tie: "#3a3a48" });

// ---- soldiers of every army: varied rotations (skin, build, nose, stubble, scars, moustaches, kit) ----
export const SOVIET: Outfit = { jacket: "#8a8458", pants: "#7a7448", boots: "#2a2420", tallBoots: true, hat: "pilotka", cap: "#8a8050", star: true, starCol: "#c8202c", tunic: true,
  webbing: "#6a5a3a", buttons: "#5a5030", canteen: true, belt: null, rifle: false, smg: "ppsh" };
const pick = <T,>(a: T[], i: number) => a[((i % a.length) + a.length) % a.length];
const HAIRS = ["#3a2a1a", "#8a6a4a", "#1e1a18", "#a0502a", "#c8a060"];
/** Soviet rifleman: pilotka side cap / ushanka / steel helmet, PPSh or rifle, some in greatcoats */
export const soviet = (i: number): [Outfit, string] => {
  const hat = pick(["pilotka", "ushanka", "m33", "pilotka", "ushanka"], i), coat = i % 3 === 1;
  return [army(SOVIET, i, { hat, helmCol: "#4e5a3c", cap: hat === "ushanka" ? pick(["#7a6450", "#8a8a80", "#6a5440"], i) : "#8a8050", hair: pick(HAIRS, i), hairUnder: hat === "pilotka",
    smg: i % 3 === 2 ? undefined : "ppsh", rifle: i % 3 === 2, coat: coat ? "#7e7462" : undefined, jacket: coat ? "#7e7462" : SOVIET.jacket, canteen: !coat }), `su${i % 30}`];
};
/** winter: Soviet ski troops in white snow capes, or freezing Germans with scarves and frost (Moscow 1941) */
export const winter = (i: number): [Outfit, string] => {
  if (i % 2 === 0) return [army(SOVIET, i, { hat: "ushanka", cap: pick(["#e8e8e4", "#7a6450", "#8a8a80"], i), cape: "#eef2f6", snow: true, coat: "#e8ecf0", jacket: "#e8ecf0", pants: "#dfe4ea",
    star: i % 4 === 0, frost: i % 4 === 2, cheeks: true, smg: i % 3 ? "ppsh" : undefined, rifle: i % 3 === 0, canteen: false, webbing: undefined }), `wi${i % 30}`];
  return [army(GE, i, { coat: "#5a6054", jacket: "#5a6054", scarf: pick(["#8a3a3a", "#c8b8a0", "#4a4a6a", "#6a5a3a"], i), frost: true, cheeks: true, stubble: true, helmCol: "#e0e4e8",
    canteen: false, rifle: i % 4 !== 3, smg: i % 4 === 3 ? "smg" : undefined }), `wi${i % 30}`];
};
/** Japanese infantry: field cap with neck flap, or netted helmet with flap; rifle and bayonet */
export const japanese = (i: number): [Outfit, string] => {
  const helm = i % 2 === 1;
  return [army(JP, i, { hat: helm ? "jphelm" : "cap", net: helm, flaps: i % 3 !== 2, bayonet: true, helmCol: "#6a6a3e" }), `jp${i % 30}`];
};
/** Italian infantry: grey-green, rounded M33 helmet or side cap */
export const IT: Outfit = { jacket: "#7a7a5c", pants: "#74745a", boots: "#3a2a20", hat: "m33", helmCol: "#5e6248", tunic: true, webbing: "#6a5a3a", puttees: "#6a6a50", canteen: true,
  buttons: "#5a5a48", belt: null, rifle: true };
export const italian = (i: number): [Outfit, string] => [army(IT, i, { hat: i % 3 === 2 ? "pilotka" : "m33", cap: "#74745a", hair: pick(HAIRS, i), hairUnder: true,
  ...(i % 4 === 1 ? { stache: "handlebar" as const, moustache: "#2a2018" } : {}) }), `it${i % 30}`];
/** British Tommy: Brodie helmet, khaki battledress, pale webbing; some with a Sten */
export const tommy = (i: number): [Outfit, string] => [army(CA, i, { webbing: "#c8bc8c", jacket: "#86704a", smg: i % 4 === 3 ? "smg" : undefined, rifle: i % 4 !== 3,
  ...(i % 5 === 1 ? { moustache: "#5a3a26", stache: "handlebar" as const } : {}) }), `uk${i % 30}`];
/** US GI: M1 helmet with net; some with a Thompson */
export const gi = (i: number): [Outfit, string] => [army(US, i, { smg: i % 4 === 3 ? "smg" : undefined, rifle: i % 4 !== 3 }), `gi${i % 30}`];
/** German infantry: plain flared steel helmet, field grey, no insignia; some with an MP40-type gun */
export const german = (i: number): [Outfit, string] => [army(GE, i, { smg: i % 4 === 3 ? "smg" : undefined, rifle: i % 4 !== 3, coat: i % 5 === 2 ? "#5a6054" : undefined }), `de${i % 30}`];
/** French 1940: Adrian helmet, khaki greatcoat, puttees */
export const french = (i: number): [Outfit, string] => [army(CA, i, { hat: "adrian", helmCol: pick(["#5a6a5a", "#6a6a50"], i), jacket: "#8a7a54", pants: "#7a6a48", coat: "#8a7a54",
  puttees: "#7a6a4a", webbing: "#5a4028", ...(i % 3 === 0 ? { moustache: "#3a2a1a", stache: "walrus" as const } : {}) }), `fr${i % 30}`];
/** Polish 1939: square-topped field cap or helmet, khaki-green */
export const polish = (i: number): [Outfit, string] => [army(CA, i, { hat: i % 2 ? "stahl" : "rogatywka", helmCol: "#565a42", cap: "#6a6a48", jacket: "#6e6e4c", pants: "#64644a",
  puttees: undefined, tallBoots: true, boots: "#2a2420", webbing: "#5a4a30" }), `pl${i % 30}`];
/** Chinese National Revolutionary Army: grey-blue cotton, steel helmet or soft cap, puttees */
export const chinese = (i: number): [Outfit, string] => [army(JP, i, { hat: i % 2 ? "stahl" : "cap", helmCol: "#4a5450", cap: "#5e6a72", flaps: false, jacket: "#66727c", pants: "#5e6a72",
  puttees: "#6e7880", webbing: "#5a4a30", star: false }), `cn${i % 30}`];
/** 1945 Volkssturm: old men in civilian coats and teenage boys in oversized helmets */
export const volkssturm = (i: number): [Outfit, string] => {
  const old = i % 2 === 0, m = MEN[(i * 5 + 3) % MEN.length];
  return [{ ...m, hat: "stahl", helmCol: "#4c5448", coat: old ? m.jacket : "#5a5e54", jacket: old ? m.jacket : "#5a5e54", build: old ? pick(["fat", "stout", "thin"], i) : "short",
    moustache: old ? "#d8d8d8" : undefined, stache: old ? "walrus" : undefined, brows: old ? "#d8d8d8" : undefined, stubble: old, haggard: old, cigar: false, rifle: true, bayonet: false,
    skin: pick(SK, i), lapels: old, vest: undefined, tie: undefined, bowtie: undefined, pocket: false, pattern: undefined, watch: false }, `vs${i % 30}`];
};
type ArmyK = "su" | "uk" | "us" | "de" | "jp" | "it" | "fr";
const OFF: Record<ArmyK, Outfit> = {
  su: { jacket: "#6a6a48", pants: "#3a3a4a", boots: INK, tallBoots: true, hat: "peaked", cap: "#6a6a48", band: "#c8202c", visor: INK, star: true, starCol: "#c8202c", tunic: true,
    boards: "#e8c45a", buttons: "#e8c45a", waist: "#5a3a22" },
  uk: { jacket: "#86704a", pants: "#86704a", boots: "#5a3a22", hat: "peaked", cap: "#86704a", band: "#86704a", visor: "#5a3a22", badge: "#c8a24a", lapels: true, tie: "#86704a",
    shirt: "#c8b48a", buttons: "#c8a24a", waist: "#5a3a22", boards: "#86704a" },
  us: { jacket: "#6a6044", pants: "#8a7656", boots: "#5a3a22", hat: "peaked", cap: "#6a6044", band: "#5a5038", visor: "#4a3020", badge: "#e8c45a", lapels: true, tie: "#7a6a48",
    shirt: "#8a7a58", buttons: "#8a7a50" },
  de: { jacket: "#5e6658", pants: "#3a3a3a", boots: INK, tallBoots: true, hat: "peaked", cap: "#5e6658", band: "#3a4a3a", visor: INK, saddle: true, badge: "#c8ccd4", lapels: true,
    tie: "#2a2420", shirt: "#e8e4da", buttons: "#8a8c80", boards: "#c8ccd4" },
  jp: { jacket: "#8a7a48", pants: "#8a7a48", boots: "#3a2a1a", tallBoots: true, hat: "peaked", cap: "#8a7a48", band: "#c8202c", visor: "#3a2a1a", star: true, starCol: "#e8c45a",
    tunic: true, buttons: "#c8a24a", boards: "#c8202c", waist: "#5a3a22", sword: true },
  it: { jacket: "#7a7a5c", pants: "#5a5a50", boots: INK, tallBoots: true, hat: "peaked", cap: "#7a7a5c", band: "#7a7a5c", visor: INK, badge: "#c8a24a", lapels: true, tie: "#5a5a48",
    shirt: "#e8e4da", buttons: "#c8a24a" },
  fr: { jacket: "#8a7a56", pants: "#8a7a56", boots: "#3a2a1c", tallBoots: true, hat: "kepi", cap: "#2a3050", band: "#c8a24a", lapels: true, tie: "#6a5a3a", shirt: "#c8b890",
    buttons: "#c8a24a", waist: "#5a3a22" },
};
/** officer of an army, varied faces and builds: officer("de", 3) */
export const officer = (k: ArmyK, i: number): [Outfit, string] => [{ ...OFF[k], skin: k === "jp" ? pick(["#f5d3ac", "#ecc69b", "#f0cfa6"], i) : pick(SK, i),
  build: pick(["stout", "adult", "thin", "fat", "adult", "short"], i), nose: pick(["round", "long", "big", "button"] as Outfit["nose"][], i), glasses: i % 4 === 2,
  moustache: i % 3 === 1 ? pick(["#3a2a1a", "#8a8a8a", "#6a4a2a"], i) : undefined, stache: i % 3 === 1 ? pick(["plain", "walrus", "pencil", "handlebar"] as Outfit["stache"][], i) : undefined,
  medals: (i * 3) % 7, brows: i % 5 === 4 ? "#9a9a9a" : undefined, jowls: i % 6 === 3, jaw: i % 6 === 1 }, `of${k}${i % 12}`];
/** pilots: leather helmet + goggles, flight jacket with a fur collar, silk scarf (RAF / US / German / Japanese rotation) */
export const pilot = (i: number): [Outfit, string] => {
  const k = i % 4;
  return [{ jacket: pick(["#6a4a30", "#7a5236", "#2a2624", "#8a7a48"], k), pants: pick(["#4a5468", "#6a6044", "#4c5048", "#8a7a48"], k), boots: "#2a2018", tallBoots: k > 1,
    hat: "leather", hatCol: pick(["#5a3a24", "#6a4428", "#2a2420", "#6a5a3a"], i), fur: k === 2 ? undefined : "#efe4cc", scarf: pick(["#f4f0e6", "#e8e0cc", "#c8c8c8", "#f4f4f0"], i),
    skin: k === 3 ? pick(["#f5d3ac", "#ecc69b"], i) : pick(SK, i), build: pick(["adult", "thin", "stout", "adult", "short"], i), nose: pick(["round", "long", "button", "big"] as Outfit["nose"][], i),
    moustache: k === 0 && i % 2 === 0 ? "#6a4a2a" : undefined, stache: "handlebar", buttons: "#3a2a20", pocket: false } as Outfit, `pi${i % 24}`];
};
/** US sailors in blues or whites with the square collar */
export const sailor = (i: number): [Outfit, string] => {
  const whites = i % 3 === 2;
  return [{ ...SAILOR, jacket: whites ? "#f2f2ee" : "#2e4270", pants: whites ? "#f2f2ee" : "#2a3350", sailorCollar: "#2a3a66", tie: "#1e1c24", buttons: "#c9ccd2", boots: INK,
    skin: pick(SK, i), build: pick(["adult", "thin", "stout", "short", "adult"], i), nose: pick(["button", "round", "long", "big"] as Outfit["nose"][], i), freckles: i % 5 === 1,
    cheeks: i % 5 === 1, stubble: i % 7 === 4 }, `sa${i % 24}`];
};
/** navy officers: dark double-breasted blues, gold cuff rings, white-topped peaked cap (senior ones with gold braid) */
export const navyOfficer = (i: number): [Outfit, string] => [{ jacket: "#1e2438", pants: "#1e2438", boots: INK, lapels: true, tie: "#141418", shirt: "#f4f4f2", buttons: "#e8c45a",
  rings: 2 + (i % 3), hat: "peaked", cap: "#f4f4f2", band: "#1e1c24", visor: INK, badge: "#e8c45a", braid: i % 3 === 2, skin: pick(SK, i + 1),
  build: pick(["stout", "adult", "thin", "fat"], i), moustache: i % 4 === 1 ? "#8a8a8a" : undefined, nose: pick(["round", "long", "big"] as Outfit["nose"][], i), medals: 3 + (i % 4),
  brows: i % 2 ? "#9a9a9a" : undefined, jowls: i % 4 === 3 }, `nv${i % 24}`];
/** US paratrooper: jump jacket, netted M1, brown jump boots, Thompson or rifle */
export const para = (i: number): [Outfit, string] => [army(US, i, { jacket: "#9a8a62", pants: "#8a7a54", tallBoots: true, boots: "#6a4428", puttees: undefined, smg: i % 2 ? "smg" : undefined,
  rifle: i % 2 === 0, webbing: "#7a7048", scarf: i % 3 === 0 ? "#c8c0a0" : undefined }), `pa${i % 24}`];
/** army nurses: blue or white dress, white pinafore with a red cross, white cap; some with a cape */
export const nurse = (i: number): [Outfit, string] => [{ ...WOMEN[i % WOMEN.length], dress: pick(["#7a9ac8", "#f2f2ee", "#8aa8c8"], i), jacket: pick(["#7a9ac8", "#f2f2ee", "#8aa8c8"], i),
  dressPat: undefined, sashW: undefined, pearls: false, scarf: undefined, apron: "#fbfbf8", redcross: true, hat: "nurse", hairUnder: true, pcollar: "#ffffff", bow: undefined, lashes: true,
  cape: i % 3 === 1 ? "#2a3050" : undefined, socks: "#e8d8c8", boots: "#2a2228" }, `nu${i % 16}`];
/** factory women ("Rosie"): red polka-dot bandana, denim coveralls, rolled sleeves */
export const rosie = (i: number): [Outfit, string] => [{ jacket: pick(["#5a7aa8", "#6a8ab8", "#4a6a98"], i), pants: pick(["#2e4a7a", "#3a5688", "#344e80"], i), bib: pick(["#2e4a7a", "#3a5688", "#344e80"], i),
  rolled: true, hat: "bandana", cap: pick(["#c8202c", "#d0303a", "#c8202c", "#2a5aa8"], i), patCol: "#ffffff", hair: pick(["#5a3a2a", "#2a1e18", "#c88a40", "#8a3a1e"], i), lashes: true,
  cheeks: true, boots: "#4a3020", skin: pick(SK, i + 2), build: pick(["adult", "thin", "stout", "short"], i), nose: pick(["button", "round", "button", "long"] as Outfit["nose"][], i),
  freckles: i % 4 === 2, buttons: "#c8ccd4", tunic: false }, `ro${i % 16}`];
/** codebreakers (Bletchley-style office wear): tweed and cardigans for the men, blouses + cardigans + skirts for the women */
export const codebreaker = (i: number): [Outfit, string] => {
  if (i % 2 === 0) return [suit(pick(["#6a5a44", "#5a5a50", "#4a4038", "#6a6a5a"], i), { pattern: pick(["check", "plaid", "check", undefined] as Outfit["pattern"][], i), patCol: "#3a3028",
    vest: pick(["#8a6a3a", "#5a6a4a", "#7a3a3a"], i), tie: pick(["#7a2a2a", "#2a4a6a", "#4a6a3a"], i), glasses: i % 4 === 0, hat: "hair", hair: pick(HAIRS, i), part: i % 3 === 0,
    skin: pick(SK, i), build: pick(["thin", "adult", "stout"], i), nose: pick(["long", "round", "button"] as Outfit["nose"][], i), pipe: i % 6 === 2 ? "briar" : undefined }), `cb${i % 16}`];
  const w = WOMEN[(i * 3) % WOMEN.length];
  return [{ ...w, hat: "hair", jacket: pick(["#8a6a8a", "#5a7a6a", "#c8a870", "#6a7a9a"], i), dress: pick(["#4a4a5a", "#5a4a3a", "#3a4a5a", "#6a5a4a"], i), dressPat: undefined, sashW: undefined,
    pcollar: "#f4f0e6", glasses: i % 3 === 1, lashes: true, pearls: i % 4 === 1, scarf: undefined }, `cb${i % 16}`];
};
/** Blitz: ARP wardens (black helmet with a W, dark overalls, gas-mask box) and civilians with gas-mask boxes */
export const warden = (i: number): [Outfit, string] => [{ jacket: "#2a3040", pants: "#2a3040", boots: INK, hat: "brodie", helmCol: "#1e1e22", helmMark: "W", gasbox: true, tunic: true,
  buttons: "#5a5a60", skin: pick(SK, i), build: pick(["stout", "fat", "adult", "thin"], i), moustache: i % 2 ? pick(["#8a8a8a", "#5a3a26"], i) : undefined, stache: pick(["walrus", "plain"] as Outfit["stache"][], i),
  nose: pick(["big", "round", "long"] as Outfit["nose"][], i), cheeks: true, waist: "#3a3020" }, `wd${i % 16}`];
export const blitz = (i: number): [Outfit, string] => { const [o, k] = crowd(i); return [{ ...o, gasbox: true, coat: i % 3 === 1 && !o.dress ? o.jacket : undefined }, `bz${k}${i % 3}`]; };
/** evacuee children: name tags, gas-mask boxes, caps and berets (give them prop "case") */
export const evacuee = (i: number): [Outfit, string] => {
  const k = KIDS[i % KIDS.length];
  return [{ ...k, tag: true, gasbox: true, jacket: pick(["#5a6a8a", "#8a5a3a", "#6a7a4a", "#a84a4a", "#4a5a6a"], i), hat: i % 3 === 2 ? "hair" : "flatcap",
    cap: pick(["#4a4a5a", "#8a3a3a", "#3a5a3a"], i), skin: pick(SK, i + 1), coat: i % 2 ? pick(["#5a6a8a", "#8a5a3a", "#6a7a4a"], i) : undefined, freckles: i % 2 === 0 }, `ev${i % 16}`];
};
/** refugees: worn coats, headscarves and flat caps (props "bundle" / "case") */
export const refugee = (i: number): [Outfit, string] => {
  if (i % 2 === 0) { const w = WOMEN[(i * 3 + 1) % WOMEN.length]; return [{ ...w, hat: "headscarf", hatCol: pick(["#7a3a3a", "#4a5a7a", "#6a5a3a", "#5a3a4a"], i), patCol: i % 4 === 0 ? "#e8d8b0" : undefined,
    pearls: false, dress: shade(w.dress!, 0.8), dressPat: undefined, jacket: pick(["#5a4a3a", "#4a4a52", "#5a5040"], i), lashes: false, socks: "#5a5050" }, `rf${i % 16}`]; }
  const m = WORKERS[(i * 3) % WORKERS.length];
  return [{ ...m, coat: pick(["#4a4038", "#3e3a36", "#5a4a3a"], i), jacket: pick(["#4a4038", "#3e3a36", "#5a4a3a"], i), stubble: true, patch: "#6a5a48", cigar: false, apron: undefined }, `rf${i % 16}`];
};
/** prisoners in striped uniforms (Holocaust chapter): thin, plain, shaved or capped; stage with "sorrow" / "grief" only */
export const prisoner = (i: number): [Outfit, string] => [{ jacket: "#d4d8de", pants: "#d4d8de", pattern: "bars", patCol: "#56627e", pantsPat: "bars", boots: "#3a3030",
  hat: i % 3 === 1 ? "bald" : "stripecap", cap: "#d4d8de", build: pick(["thin", "thin", "adult", "short"], i), skin: pick(["#ecd6c4", "#e6d0bc", "#f0dccc", "#dcc4ae"], i),
  nose: pick(["long", "round", "button", "long"] as Outfit["nose"][], i), stubble: i % 2 === 0, buttons: "#9aa0aa", brows: pick(["#3a2a1a", "#5a4a3a", "#8a8a8a"], i), haggard: i % 4 === 3 }, `pr${i % 16}`];

/** every outfit, for lineup previews (scripts) */
export const CAST = { SOLDIER, ONODA, trooper, CLEM, WILSON, LLOYD, GERMAN, HITLER, BAKER, OFFICIAL, WORKERS, MEN, WOMEN, KIDS };
/** chapters 2-14: leaders (fixed outfits) and the varied generators ((i) => [Outfit, key]), for lineup previews */
export const CAST2 = {
  CHURCHILL, CHURCHILL_BARE, STALIN, STALIN_COAT, ROOSEVELT, ROOSEVELT_HAT, MUSSOLINI, MUSSOLINI_BARE, CHAMBERLAIN, CHAMBERLAIN_HAT, DEGAULLE, HITLER_WAR, HITLER_OLD,
  TRUMAN, TRUMAN_BARE, EISENHOWER, EISENHOWER_BARE, MACARTHUR, MONTGOMERY, ZHUKOV, TOJO, TOJO_CAP, ROMMEL, STAUFFENBERG, PAULUS, HIROHITO, ONODA,
  soviet, winter, japanese, italian, tommy, gi, german, french, polish, chinese, volkssturm, officer, pilot, sailor, navyOfficer, para, nurse, rosie, codebreaker, warden, blitz,
  evacuee, refugee, prisoner,
};
