// WW2 part 1 cast: lit flat sprites + unlit effect cards, staged per shot in each set's local coordinates.
import * as THREE from "three";
import {
  Pen, bodyFront, bodySide, army, US, JP, KID, INK, Outfit, Expr, FrontOpts, SideOpts,
  fxContact, fxShadow, fxMist, fxBomber, fxMushroom, fxStamp, fxBanknote, fxChart, fxPadlock, fxNewspaper, fxFlame, fxMapCut,
} from "./toon";
import { FPS, SHOTS, V3, clamp01, smooth, DOM0 } from "./story";
import { setOrigin, SetName } from "./sets";
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

const hh = (i: number, s = 0) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
const q = (v: number, n = 120) => Math.round(v * n) / n;
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
const suit = (jacket: string, extra: Partial<Outfit> = {}): Outfit => ({ jacket, pants: jacket, boots: INK, buttons: "#c8c0b0", ...extra });
export const CLEM = suit("#2e2e38", { hat: null, moustache: "#f2f2f2", build: "stout" });
export const WILSON = suit("#3a3a50", { hat: "tophat", glasses: true });
export const LLOYD = suit("#4a3a2a", { hat: "hair", hair: "#ececec", moustache: "#e4e4e4" });
export const GERMAN = suit("#3e4a3e", { hat: "bowler", sweat: true });
export const HITLER: Outfit = { jacket: "#7a6040", pants: "#5a4a30", boots: INK, hat: "hair", hair: "#2e2218", part: true, moustache: "brush:#2a1e14", buttons: "#c8a24a" };
export const BAKER: Outfit = { jacket: "#f4f4f2", pants: "#8a8a90", boots: "#4a3426", hat: "chef", moustache: "#5a3a2a", build: "stout", buttons: "#c8c8c8" };
const WORKERS: Outfit[] = [0, 1, 2, 3, 4, 5].map((v) => ({ jacket: ["#5a4a3a", "#4a5a6a", "#6a5a4a", "#3a4a5a", "#6a4a3a", "#4a4a4a"][v], pants: "#3a3a40", boots: "#3a2a20", hat: "cap",
  cap: ["#4a4a50", "#6a5a4a", "#3a3a4a"][v % 3], moustache: v % 3 === 1 ? "#4a3426" : undefined, skin: ["#ffe2c2", "#f5c9a0", "#ecd0b6", "#e8c0a0"][v % 4] }));
const MEN: Outfit[] = [0, 1, 2, 3].map((v) => suit(["#2a2a34", "#3a3028", "#2a3440", "#4a4a52"][v], { hat: "bowler", moustache: v % 2 ? "#3a2a1a" : undefined }));
const WOMEN: Outfit[] = [0, 1, 2, 3].map((v) => ({ jacket: ["#8a3a4a", "#3a5a8a", "#5a7a3a", "#a8703a"][v], pants: "#3a3a40", boots: "#4a3426", hat: "hair", hair: ["#5a3a2a", "#d8b060", "#2a1e18", "#a0502a"][v], dress: ["#a84a5a", "#4a6a9a", "#6a8a4a", "#c8904a"][v] }));
const KIDS: Outfit[] = [KID, { ...KID, jacket: "#3a7ac8", cap: "#f2c84a" }, { ...KID, jacket: "#c84a7a", hat: "hair", hair: "#d8a050", cap: undefined }];
const OFFICIAL: Outfit = { jacket: "#3a3e4a", pants: "#2e3038", boots: INK, hat: "cap", cap: "#2a2e3a", moustache: "#2a2018", buttons: "#c8a24a" };
const SOLDIER = army(US, 0), ONODA = army(JP, 1);

type Who = { i: number; o: Outfit; okey: string };
const W_ = (o: Outfit, i: number, key: string): Who => ({ i, o, okey: key });
const person = (cam: CamInfo, w: Who, x: number, y: number, z: number, fo: FrontOpts, scale = 1, side?: { so: SideOpts; mirror: boolean }): Place => {
  const d = cam.pos.distanceTo(tmp.set(x, y + 1.2 * scale, z)) / scale;
  const [cw, ch, k] = tier(d), m = !!side?.mirror, light = light2D(cam, m), seed = seedOf(w.i);
  if (side) { const s2: SideOpts = { ...side.so, light, seed }; return { key: `S|${w.okey}|${fkey(s2)}`, x, y, z, scale, mirror: m, draw: (p) => bodySide(p, w.o, s2), size: [cw, ch, k] }; }
  const f2: FrontOpts = { ...fo, light, seed };
  return { key: `F|${w.okey}|${fkey(f2)}`, x, y, z, scale, draw: (p) => bodyFront(p, w.o, f2), size: [cw, ch, k] };
};
const toSrgb = (v: number) => { const c = clamp01(v); return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055; };
const hexOf = (c: [number, number, number], k: number) => "#" + c.map((v) => Math.round(255 * toSrgb(1 - (1 - v) * k)).toString(16).padStart(2, "0")).join("");
const blob = (out: Stage, x: number, y: number, z: number, sc = 1) => {
  const cc = hexOf([0.22, 0.2, 0.3], 1);
  out.fx.push({ key: `blob|contact|${cc}`, cw: 128, ch: 128, draw: (p) => fxContact(p, cc), x, y: y + 0.02, z, w: 0.55 * sc, h: 0.42 * sc, flat: true });
  if (LNAME === "gloom" || LNAME === "night") return;
  const hl = Math.hypot(SUN.x, SUN.z) || 1, ox = -SUN.x / hl, oz = -SUN.z / hl, rot = Math.atan2(-ox, -oz), tc = hexOf([0.42, 0.42, 0.6], 1);
  const len = 1.2 * sc, h = len + 0.5 * sc, c = 0.3 * h;
  out.fx.push({ key: `blob|shadow|${tc}`, cw: 128, ch: 256, draw: (p) => fxShadow(p, tc), x: x + ox * c, y: y + 0.015, z: z + oz * c, w: 0.7 * sc, h, flat: true, rot });
};
const mist = (out: Stage, x: number, y: number, z: number, w: number, t: number, i: number, col = "#e6ecf2", op = 1) =>
  out.fx.push({ key: `mist${col}`, cw: 512, ch: 256, draw: (p) => fxMist(p, col), x: x + 0.25 * Math.sin(t * 0.35 + i * 1.7), y, z, w, h: w * 0.5, soft: true, opacity: op });
const stamp = (out: Stage, t: number, t0: number, text: string, x: number, y: number, z: number, w: number, flat = false, rot = 0) => {
  if (t < t0 - 1 / FPS) return;
  const k = 1 + 0.6 * (1 - smooth((t - t0) / (4 / FPS)));
  out.fx.push({ key: `stamp${text}`, cw: 600, ch: 260, draw: (p) => fxStamp(p, text), x, y, z, w: w * k, h: w * k * (260 / 600), flat, rot });
};

// ---------------- staging by shot ----------------
type Ctx = { cam: CamInfo; t: number; f: number; out: Stage; O: (x: number, y: number, z: number) => [number, number, number] };
const P = (c: Ctx, w: Who, x: number, y: number, z: number, fo: FrontOpts, scale = 1, side?: { so: SideOpts; mirror: boolean }, shadow = true) => {
  const [X, Y, Z] = c.O(x, y, z); c.out.places.push(person(c.cam, w, X, Y, Z, { blink: lidAt(c.t, w.i), ...fo }, scale, side)); if (shadow) blob(c.out, X, Y, Z, scale);
};
const F = (c: Ctx, fx: FxPlace) => { const [X, Y, Z] = c.O(fx.x, fx.y, fx.z); c.out.fx.push({ ...fx, x: X, y: Y, z: Z }); };
const at = (f: number) => f / FPS;

export const DOMINO_T0 = at(53), DOMINO_DT = 0.045;
const s1 = (c: Ctx) => {
  const { t } = c, fall = clamp01((t - DOMINO_T0 + 0.05) / 0.45);
  const x = DOM0[0] + 0.12 * fall, y = 0.26 * (1 - fall * fall) + 0.02 * fall + 0.08 * Math.sin(Math.PI * fall), z = DOM0[2] - 0.05 * fall;
  P(c, W_(SOLDIER, 1, "dom"), x, y, z, { mode: fall > 0 ? "fall" : "stand", expr: t > at(46) ? "shock" : "neutral", tilt: -60 * fall }, 0.075, undefined, fall === 0);
};
const s2 = (c: Ctx) => {
  for (let i = 0; i < 6; i++) {
    const x = -1 + (i % 3) * 1.4 + hh(i) * 0.4, z = 7 + Math.floor(i / 3) * 3 - 0.9 * (c.t - at(140)) * 0;
    P(c, W_(army(US, i), i, `fs${i % 4}`), x, 0, z - 1.2 * (c.t - at(140)), { mode: "march", phase: q(((c.t * 1.8 + hh(i, 2)) % 1), 60), expr: "stern", lift: 40 });
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
  P(c, W_(ONODA, 3, "onoda"), 0, 0, 4, { mode: "stand", expr: c.t > at(446) ? "stern" : "neutral", look: c.t > at(410) && c.t < at(440) ? 1 : 0 });
  for (let i = 0; i < 5; i++) mist(c.out, -4 + i * 2, 0.4, 6 + (i % 2) * 2, 4, c.t, i, "#d8e8c8", 0.5);
};
// Paris
const LEADERS: [Outfit, number, number, string][] = [[CLEM, 0, 11.0, "clem"], [WILSON, -1.3, 10.8, "wilson"], [LLOYD, 1.3, 10.8, "lloyd"]];
const delegates = (c: Ctx) => {
  for (let i = 0; i < 8; i++) { const s = i % 2 ? 1 : -1, z = 3 + Math.floor(i / 2) * 1.8; P(c, W_(MEN[i % 4], 40 + i, `dl${i % 4}`), s * 2.1, 0, z, { mode: "stand", expr: i % 3 ? "smug" : "stern", facing: (-s) as -1 | 1 }); }
};
const parisLeaders = (c: Ctx, exprs: Expr[], prop?: number) =>
  LEADERS.forEach(([o, x, z, k], i) => P(c, W_(o, 30 + i, k), x, 0, z, { mode: "stand", expr: exprs[i], prop: prop === i ? "paper" : null }));
const s9 = (c: Ctx) => {
  parisLeaders(c, ["stern", "smug", "smug"]); delegates(c);
  P(c, W_(GERMAN, 20, "ger"), 6.35, 0, -2.3, { mode: "stand", expr: "nervous", facing: -1 }, 0.82);
};
const s10 = (c: Ctx) => P(c, W_(GERMAN, 20, "ger"), 6.35, 0, -2.3, { mode: "stand", expr: c.t > at(1045) ? "shock" : "nervous", facing: -1 }, 0.82);
const s11 = (c: Ctx) => {
  const { t } = c;
  parisLeaders(c, ["stern", "smug", "stern"], t > at(1255) ? 0 : undefined); delegates(c);
  P(c, W_(GERMAN, 20, "ger"), 0.05, 0, 1.0, { mode: "stand", expr: t > at(1255) ? "shock" : "nervous", prop: t < at(1140) ? "paper" : null }, 0.82);
  if (c.f >= 1140 && c.f < 1250) {
    const k = smooth((t - at(1147)) / 0.5);
    F(c, { key: `mapcut${q(k, 20)}`, cw: 512, ch: 512, draw: (p) => fxMapCut(p, q(k, 20)), x: -0.15, y: 0.815, z: 2.65, w: 0.75, h: 0.75, flat: true, rot: Math.PI });
    for (let i = 0; i < 12; i++) {
      const down = i >= 2 && t > at(1190) + (i - 2) * 0.06, u = down ? smooth((t - at(1190) - (i - 2) * 0.06) / 0.18) : 0;
      P(c, W_(army(US, i), 60 + i, `toy${i % 4}`), 0.35 + (i % 6) * 0.09, 0.8 + 0.02 * u, 2.95 + Math.floor(i / 6) * 0.12, { mode: "stand", expr: u > 0 ? "shock" : "stern", tilt: 85 * u }, 0.08, undefined, false);
    }
  }
};
const s12 = (c: Ctx) => {
  const { t } = c;
  P(c, W_(GERMAN, 20, "ger"), 0.05, 0, 1.0, { mode: "stand", expr: t > at(1405) ? "dazed" : "shock" }, 0.82);
  parisLeaders(c, ["smug", "smug", "smug"]);
  stamp(c.out, t, at(1410), "PAID\nIN 2010", ...c.O(0.06, 0.035, -2.6), 1.5, true, Math.PI);
};
// press
const s13 = (c: Ctx) => {
  const { t } = c;
  P(c, W_(OFFICIAL, 70, "off"), 2.3, 0, 1.7, { mode: "stand", expr: t > at(1600) ? "grin" : "neutral", wave: q(Math.sin(t * 6), 20) });
  P(c, W_(WORKERS[1], 71, "wk1"), -2.6, 0, 1.6, { mode: "stand", expr: t > at(1620) ? "shock" : "neutral", prop: "cash", facing: 1 });
  const n = Math.floor(6 + 30 * smooth((t - at(1440)) / 7));
  for (let i = 0; i < n; i++) {
    const age = ((t * 0.6 + hh(i, 1)) % 1.4) / 1.4, a = hh(i, 2) * Math.PI * 2;
    F(c, { key: `note${i % 3}`, cw: 300, ch: 150, draw: (p) => fxBanknote(p, i % 3), x: Math.cos(a) * (0.5 + 2.4 * age), y: 1.8 + 1.2 * age - 2.2 * age * age, z: 2.4 + Math.sin(a) * (0.4 + 1.6 * age) - 1.2 * age, w: 0.3, h: 0.15, rot: age * 9 + i });
  }
};
const s26 = (c: Ctx) => {
  const k = smooth((c.t - at(3362)) / 0.9);
  F(c, { key: `paper${q(k, 20)}`, cw: 400, ch: 520, draw: (p) => fxNewspaper(p, q(k, 20)), x: 3.8, y: 0.915, z: 2.0, w: 0.5, h: 0.65, flat: true, rot: Math.PI + 0.15 });
  P(c, W_(OFFICIAL, 70, "off"), 4.6, 0, 2.6, { mode: "stand", expr: "stern" });
};
// bakery
export const tagAt = (f: number) => (f < 1858 ? "200.000.000.000 M" : f < 1890 ? "350.000.000.000 M" : "500.000.000.000 M");
const s14 = (c: Ctx) => {
  P(c, W_(BAKER, 72, "baker"), 0.9, 0, 3.0, { mode: "stand", expr: "smug", prop: "bread" });
  P(c, W_(WOMEN[0], 73, "w0"), -2.3, 0, -0.9, { mode: "stand", expr: c.t > at(1755) ? "shock" : "nervous", facing: 1 });
};
const s15 = (c: Ctx) => {
  const { t } = c, u = smooth((t - at(1815)) / 1.6);
  P(c, W_(BAKER, 72, "baker"), 0.9, 0, 3.0, { mode: "stand", expr: "smug", prop: "bread" });
  P(c, W_(WORKERS[0], 74, "wk0"), -4 + 3.4 * u, 0, -1.0 + 2.0 * u, { mode: u < 1 ? "march" : "stand", phase: q((t * 2.2) % 1, 60), expr: t > at(1860) ? "shock" : "grin", prop: "cash", lift: 70 });
  P(c, W_(WOMEN[0], 73, "w0"), -2.0, 0, -0.9, { mode: "stand", expr: "nervous", facing: 1 });
};
// playroom
const s16 = (c: Ctx) => {
  const { t } = c;
  P(c, W_(KIDS[0], 80, "k0"), -0.55, 0, 0.6, { mode: "stand", expr: t > at(2040) ? "shock" : "grin", wave: t < at(2040) ? q(Math.sin(t * 3), 10) : undefined }, 0.72);
  P(c, W_(KIDS[2], 81, "k2"), 0.65, 0, 0.75, { mode: "stand", expr: t > at(2040) ? "laugh" : "smile_closed" }, 0.72);
  const n = Math.min(14, 3 + Math.floor((t - at(1930)) * 3.2)), fallT = at(2040);
  for (let i = 0; i < n; i++) {
    const u = t > fallT ? smooth((t - fallT - i * 0.02) / 0.5) : 0, side = i % 2 ? 1 : -1;
    F(c, { key: `bundle${i % 3}`, cw: 300, ch: 150, draw: (p) => fxBanknote(p, i % 3), x: 0.08 + (i % 2 ? 0.04 : -0.04) + side * 0.6 * u * (i / 14), y: 0.07 + i * 0.105 - (i * 0.105) * u, z: 0.95 - 0.3 * u * (i / 14), w: 0.34, h: 0.12, rot: side * 1.4 * u * (i / 14) });
  }
};
// street
const s17 = (c: Ctx) => {
  const { t } = c;
  for (let i = 0; i < 2; i++) P(c, W_(i ? WOMEN[1] : MEN[0], 90 + i, `dance${i}`), -1.2 + i * 0.55 + 0.1 * Math.sin(t * 4), 0, 3.5, { mode: "stroll", phase: q((t * 1.4 + i * 0.5) % 1, 60), expr: i ? "laugh" : "grin", wave: q(Math.sin(t * 5 + i), 10) });
  for (let i = 0; i < 6; i++) P(c, W_(i % 2 ? WOMEN[i % 4] : MEN[i % 4], 92 + i, `str${i}`), (i % 2 ? -1 : 1) * (2.5 + hh(i) * 2), 0, 6 + i * 2.5 - (t - at(2057)) * 0.6 * (i % 2 ? 1 : -1), { mode: "stroll", phase: q((t * 0.9 + hh(i, 4)) % 1, 60), expr: (["smile", "grin", "smile_closed"] as Expr[])[i % 3] });
};
const s18 = (c: Ctx) => {
  const { t } = c, crashed = t > at(2166) - LEAD;
  const prog = clamp01((t - at(2111)) / 1.7), crash = clamp01((t - at(2166)) / 0.25);
  F(c, { key: `chart${q(prog, 30)}${q(crash, 10)}`, cw: 1024, ch: 512, draw: (p) => fxChart(p, q(prog, 30), q(crash, 10)), x: 0, y: 2.75, z: 6.72, w: 5.6, h: 2.8, glow: 1.1 });
  for (let i = 0; i < 6; i++) {
    const x = -4.5 + (i % 4) * 3 + (i >= 4 ? 1.5 : 0), z = i >= 4 ? 0.4 : 1.4;
    if (c.f >= 2226 && i === 2) continue;
    P(c, W_(MEN[i % 4], 100 + i, `bk${i % 4}`), x, 0, z, { mode: "stand", expr: crashed ? (i % 2 ? "shock" : "sad") : "grin", wave: !crashed && i % 3 === 0 ? q(Math.sin(t * 6 + i), 10) : undefined });
  }
  if (c.f >= 2226) P(c, W_(MEN[2], 102, "bk2"), 1.5, 0, 1.4, { mode: "stand", expr: "sad" });
};
const s19 = (c: Ctx) => {
  for (let i = 0; i < 14; i++) P(c, W_(WORKERS[i % 6], 110 + i, `wk${i % 6}`), 7.3 + (hh(i) - 0.5) * 0.3, 0.15, 23.5 - i * 0.9, { mode: "stand", expr: (["sad", "neutral", "sad", "dazed"] as Expr[])[i % 4], look: Math.round(hh(i, 3) * 2 - 1) });
};
const s20 = (c: Ctx) => {
  const { t } = c;
  for (let i = 0; i < 26; i++) {
    const x = (hh(i) - 0.5) * 8, z = 25 + hh(i, 2) * 6.5, o = i % 3 === 0 ? WOMEN[i % 4] : i % 3 === 1 ? WORKERS[i % 6] : MEN[i % 4];
    P(c, W_(o, 130 + i, `cr${i % 12}`), x, 0, z, { mode: "stand", expr: t > at(2470) ? (i % 3 ? "stern" : "angry") : (["sad", "angry", "nervous"] as Expr[])[i % 3] });
  }
  P(c, W_(HITLER, 9, "hit"), 0, 0.55, 34.2, { mode: "stand", expr: "shout", wave: q(Math.sin(t * 5), 10) });
};
const s21 = (c: Ctx) => {
  const { t } = c;
  P(c, W_(HITLER, 9, "hit"), -0.4, 0, 0.45, { mode: "stand", expr: t > at(2630) ? "sad" : t > at(2600) ? "nervous" : "smug", prop: "brush" });
  F(c, { key: "canvas", cw: 600, ch: 460, draw: (p) => { p.poly([[10, 10], [590, 10], [590, 450], [10, 450]], "#f2ead8", 10); p.g.fillStyle = "#9cc4e8"; p.g.fillRect(30, 30, 540, 200); p.g.fillStyle = "#6a9a4a"; p.g.fillRect(30, 230, 540, 200); p.poly([[220, 250], [380, 250], [380, 360], [220, 360]], "#f2e2b2", 5); p.poly([[200, 250], [300, 170], [400, 250]], "#b8463c", 5); }, x: 0.4, y: 1.22, z: 0.78, w: 0.85, h: 0.65 });
  stamp(c.out, t, at(2627), "REJECTED", ...c.O(0.36, 1.32, 0.72), 0.75);
  stamp(c.out, t, at(2678), "REJECTED", ...c.O(0.46, 1.1, 0.71), 0.75);
};
const s22 = (c: Ctx) => {
  const { t } = c;
  for (let i = 0; i < 6; i++) P(c, W_(i % 2 ? WORKERS[i % 6] : MEN[i % 4], 150 + i, `bm${i}`), (i < 3 ? -3.5 : 3.5) + (i % 3 - 1) * 0.9, 0, 7.4, { mode: "stand", expr: t > at(2857) ? (i % 2 ? "smug" : "grin") : "neutral", prop: "stein" });
  if (t < at(2800)) { const u = smooth((t - at(2707)) / 3.0); P(c, W_(HITLER, 9, "hit"), -5 + 4.6 * u, 0, 6 + 3.4 * u, { mode: u < 1 ? "march" : "stand", phase: q((t * 1.8) % 1, 60), expr: "angry", lift: 50 }); }
  else P(c, W_(HITLER, 9, "hit"), 0, 0.55, 10.6, { mode: "stand", expr: "shout", wave: q(Math.sin(t * 5), 10) });
};
const s23 = (c: Ctx) => {
  const { t } = c, cheer = t > at(3119) - LEAD, grown = clamp01((t - at(2902)) / 4);
  const n = Math.floor(14 + 36 * grown);
  for (let i = 0; i < n; i++) {
    const x = (hh(i, 5) - 0.5) * 12, z = 0.5 + hh(i, 6) * 8.5, o = i % 3 === 0 ? WOMEN[i % 4] : i % 3 === 1 ? WORKERS[i % 6] : MEN[i % 4];
    P(c, W_(o, 160 + i, `bc${i % 14}`), x, 0, z, { mode: "stand", expr: cheer ? (i % 2 ? "laugh" : "grin") : (i % 3 ? "stern" : "smug"), wave: cheer && i % 2 ? q(Math.sin(t * 7 + i), 10) : undefined });
  }
  P(c, W_(HITLER, 9, "hit"), 0, 0.55, 10.6, { mode: "stand", expr: "shout", wave: q(Math.sin(t * 5), 10) });
};
const torches = (c: Ctx, n: number, z0: number) => {
  for (let i = 0; i < n; i++) {
    const x = (hh(i, 7) - 0.5) * 9, z = z0 + hh(i, 8) * 9;
    P(c, W_(i % 2 ? WORKERS[i % 6] : MEN[i % 4], 200 + i, `tc${i % 10}`), x, 0, z, { mode: "stand", expr: i % 3 ? "stern" : "grin" });
    if (i % 2 === 0) F(c, { key: `flame${q((c.t * 3 + i) % 1, 6)}`, cw: 160, ch: 320, draw: (p) => fxFlame(p, q((c.t * 3 + i) % 1, 6) * 6), x: x + 0.35, y: 1.9, z: z - 0.05, w: 0.3, h: 0.6, glow: 2.2 });
  }
};
const s24 = (c: Ctx) => { torches(c, 30, 31); P(c, W_(HITLER, 9, "hit"), 0, 6.3, 45.3, { mode: "stand", expr: "smug" }, 1, undefined, false); };
const s25 = (c: Ctx) => F(c, { key: "padlock", cw: 400, ch: 400, draw: fxPadlock, x: 5.98, y: 1.45, z: 26, w: 1.3, h: 1.3 });
const s27 = (c: Ctx) => {
  const u = (c.t - at(3405)) * 0.55;
  const fam: [Outfit, number, number][] = [[MEN[1], 0, 1], [WOMEN[2], 0.7, 1], [KIDS[0], 0.35, 0.72], [KIDS[2], 1.05, 0.72]];
  fam.forEach(([o, dx, sc], i) => P(c, W_(o, 220 + i, `fam${i}`), -7.6 + dx, 0.15, 21.5 - u - (i >= 2 ? 0.7 : 0), { mode: "stroll", phase: q((c.t * 0.8 + i * 0.25) % 1, 60), expr: "sad", prop: i < 2 ? "case" : null }, sc));
};
const s28 = (c: Ctx) => {
  torches(c, 14, 33);
  P(c, W_(HITLER, 9, "hit"), 0, 6.3, 45.3, { mode: "stand", expr: "smug" }, 1, undefined, false);
  F(c, { key: "bigshadow", cw: 600, ch: 1000, draw: (p) => { bodyFront(p, HITLER, { mode: "stand", expr: "smug", seed: 2 }); const g = p.g; g.globalCompositeOperation = "source-in"; g.fillStyle = "rgba(4,2,8,0.92)"; g.fillRect(0, 0, 600, 1000); g.globalCompositeOperation = "source-over"; },
    x: 1.6, y: 10.5, z: 45.92, w: 9, h: 15, soft: true, opacity: 1 });
};

const STAGE: Record<number, (c: Ctx) => void> = { 1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 9: s9, 10: s10, 11: s11, 12: s12, 13: s13, 14: s14, 15: s15, 16: s16, 17: s17, 18: s18, 19: s19, 20: s20,
  21: s21, 22: s22, 23: s23, 24: s24, 25: s25, 26: s26, 27: s27, 28: s28 };

export const stage = (id: number, f: number, cam: CamInfo, sun: THREE.Vector3): Stage => {
  const out: Stage = { places: [], fx: [] }, s = SHOTS[id - 1], o = setOrigin(s.set as SetName);
  LNAME = s.light; SUN.copy(sun);
  const O = (x: number, y: number, z: number): [number, number, number] => [o[0] + x, o[1] + y, o[2] + z];
  STAGE[id]?.({ cam, t: f / FPS, f, out, O });
  return out;
};
export { V3 };
