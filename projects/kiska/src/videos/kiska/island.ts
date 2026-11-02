// Kiska as one place: terrain height, shoreline, named sites, and the hand-built props (huts, ships, landing craft,
// planes, rocks). Everything is our own simple geometry (no external models); materials are two-tone (shade.ts).
import * as THREE from "three";
import { Batch, boxGeo, V, lam } from "./build";
import { ctex } from "./paint";
import { twoTone } from "./shade";

export type V3 = [number, number, number];
const sm = (a: number, b: number, x: number) => { const u = Math.max(0, Math.min(1, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const bump = (u: number) => Math.max(0, 1 - u * u) ** 2;

/** shoreline: z of the waterline at x (land is z > shoreZ). A cove in front of the Japanese camp. */
export const shoreZ = (x: number) => -60 + 10 * Math.sin(x / 57) + 6 * Math.sin(x / 23 + 1) + 35 * bump((x + 115) / 55);
export const CAMP: V3 = [-115, 0, 12];
export const VOLCANO: V3 = [260, 0, 620];
/** ground height (m) at x, z; below 0 is the sea bed */
export const H = (x: number, z: number) => {
  const d = z - shoreZ(x);
  let h: number;
  if (d < 0) h = Math.max(-14, -1.2 + d * 0.35);
  else if (d < 25) h = d * 0.07;
  else h = 1.75 + 10 * sm(25, 140, d) + 3.5 * Math.sin(x / 31) * Math.sin(z / 27) * sm(25, 80, d) + 40 * sm(160, 460, d);
  const r = Math.hypot(x - VOLCANO[0], z - VOLCANO[2]);
  if (r < 520) h = Math.max(h, 280 * (1 - r / 520) ** 1.7); // (was max(h, 0) everywhere: it lifted the sea bed to the water line)
  // flatten the camp terrace
  const rc = Math.hypot(x - CAMP[0], z - CAMP[2]);
  if (d > 0) h = h + (3.2 + 0.03 * (z - CAMP[2]) - h) * bump(rc / 75);
  return h;
};
/** ground point */
export const G = (x: number, z: number, dy = 0): V3 => [x, H(x, z) + dy, z];

// ---------------- materials ----------------
const noiseTex = () => ctex("groundNoise", 512, 512, (g, r) => {
  g.fillStyle = "#e8e8e8"; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 2600; i++) {
    const v = 200 + Math.floor(r() * 55), x = r() * 512, y = r() * 512, w = 4 + r() * 18;
    g.fillStyle = `rgba(${v},${v},${v},0.5)`; g.beginPath(); g.ellipse(x, y, w, w * 0.45, r() * 3, 0, Math.PI * 2); g.fill();
  }
  for (let i = 0; i < 380; i++) { g.fillStyle = "rgba(120,110,100,0.35)"; g.fillRect(r() * 512, r() * 512, 2 + r() * 3, 2 + r() * 3); }
});
const woodTex = () => ctex("hutWood", 512, 512, (g, r) => {
  g.fillStyle = "#8a6a4a"; g.fillRect(0, 0, 512, 512);
  for (let y = 0; y < 512; y += 32) {
    g.fillStyle = `hsl(28, 30%, ${30 + r() * 10}%)`; g.fillRect(0, y, 512, 30);
    g.fillStyle = "rgba(30,20,20,0.85)"; g.fillRect(0, y + 30, 512, 2);
  }
});
const tarTex = () => ctex("tarpaper", 256, 256, (g, r) => {
  g.fillStyle = "#4d4a4a"; g.fillRect(0, 0, 256, 256);
  for (let y = 0; y < 256; y += 42) { g.fillStyle = "rgba(20,18,22,0.9)"; g.fillRect(0, y, 256, 3); }
  for (let i = 0; i < 300; i++) { g.fillStyle = `rgba(${90 + r() * 30},${88 + r() * 30},${90 + r() * 30},0.4)`; g.fillRect(r() * 256, r() * 256, 3, 3); }
});
export const jpFlagTex = () => ctex("flagJapan", 300, 200, (g) => {
  g.fillStyle = "#f6f3ec"; g.fillRect(0, 0, 300, 200);
  g.fillStyle = "#c8202c"; g.beginPath(); g.arc(150, 100, 58, 0, Math.PI * 2); g.fill();
});
export const MAT = () => ({
  ground: (() => { const m = twoTone(new THREE.MeshLambertMaterial({ map: noiseTex(), vertexColors: true })); m.map!.repeat.set(1, 1); return m; })(),
  wood: lam("hutWood", () => ({ map: woodTex() })),
  tar: lam("tarpaper", () => ({ map: tarTex() })),
  dark: lam("darkDoor", () => ({ color: "#2b2420" })),
  hull: twoTone(new THREE.MeshPhongMaterial({ color: "#7c858f", specular: "#555555", shininess: 20 }), 0.6),
  hullUS: twoTone(new THREE.MeshPhongMaterial({ color: "#6c7a88", specular: "#555555", shininess: 20 }), 0.6),
  deck: lam("shipDeck", () => ({ color: "#8f8270" })),
  boot: lam("bootTop", () => ({ color: "#7a3b34" })),
  steel: twoTone(new THREE.MeshPhongMaterial({ color: "#4b5058", specular: "#777777", shininess: 30 }), 0.6),
  olive: lam("oliveDrab", () => ({ color: "#5f6640" })),
  craft: lam("lcvp", () => ({ color: "#6a7458" })),
  rock: lam("rockGrey", () => ({ color: "#6f6c68" })),
  sandbag: lam("sandbag", () => ({ color: "#b8a77a" })),
  pole: lam("flagPole", () => ({ color: "#d9d4c8" })),
  flag: lam("flagJapan", () => ({ map: jpFlagTex(), side: THREE.DoubleSide })),
  plank: lam("pierPlank", () => ({ color: "#7a6450" })),
  roomWall: lam("roomWall", () => ({ color: "#8a8fa8" })),
  roomFloor: lam("roomFloor", () => ({ map: woodTex() })),
  door: lam("roomDoor", () => ({ color: "#a07c5a" })),
});
export type Mats = ReturnType<typeof MAT>;

// ---------------- terrain ----------------
const col = (x: number, z: number, h: number, out: THREE.Color) => {
  const d = z - shoreZ(x);
  const sand = new THREE.Color("#cdb98a"), wet = new THREE.Color("#8f8466"), tundra = new THREE.Color("#7c8a4e"), moss = new THREE.Color("#94a058"),
    rock = new THREE.Color("#7a756d"), snow = new THREE.Color("#f2f4f6");
  if (d < 2) out.copy(wet).lerp(sand, Math.max(0, (d + 4) / 6));
  else if (d < 22) out.copy(sand).lerp(tundra, sm(14, 22, d));
  else out.copy(tundra).lerp(moss, 0.5 + 0.5 * Math.sin(x / 13) * Math.sin(z / 17));
  out.lerp(rock, sm(70, 150, h) * 0.85);
  out.lerp(snow, sm(185, 215, h + 18 * Math.sin(x / 40 + z / 33)));
  return out;
};
/** terrain mesh: dense rows near the shore, coarse inland */
export const terrain = (m: Mats) => {
  const xs: number[] = [], zs: number[] = [];
  for (let x = -700; x <= 900; x += x > -260 && x < 240 ? 2.5 : 8) xs.push(x);
  for (let z = -320; z <= 1300; z += z > -110 && z < 110 ? 1.6 : z < 400 ? 6 : 14) zs.push(z);
  const nx = xs.length, nz = zs.length, pos = new Float32Array(nx * nz * 3), cols = new Float32Array(nx * nz * 3), uv = new Float32Array(nx * nz * 2);
  const c = new THREE.Color();
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    const x = xs[i], z = zs[j], h = H(x, z), k = j * nx + i;
    pos.set([x, h, z], k * 3); col(x, z, h, c); cols.set([c.r, c.g, c.b], k * 3); uv.set([x / 12, z / 12], k * 2);
  }
  const idx: number[] = [];
  for (let j = 0; j < nz - 1; j++) for (let i = 0; i < nx - 1; i++) {
    const a = j * nx + i, b = a + 1, d = a + nx, e = d + 1;
    idx.push(a, d, b, b, d, e);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setAttribute("color", new THREE.BufferAttribute(cols, 3));
  g.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals();
  const mesh = new THREE.Mesh(g, m.ground);
  mesh.receiveShadow = true; mesh.castShadow = true;
  return mesh;
};

// ---------------- props ----------------
const M4 = (x: number, y: number, z: number, yaw = 0, s = 1) => new THREE.Matrix4().compose(V(x, y, z), new THREE.Quaternion().setFromAxisAngle(V(0, 1, 0), yaw), V(s, s, s));
const prism = (w: number, d: number, h: number) => {
  // gable roof along z: ridge at height h over a w-wide base
  const s = new THREE.Shape([new THREE.Vector2(-w / 2, 0), new THREE.Vector2(w / 2, 0), new THREE.Vector2(0, h)]);
  const g = new THREE.ExtrudeGeometry(s, { depth: d, bevelEnabled: false });
  g.translate(0, 0, -d / 2);
  return g;
};
/** wooden hut with a tar-paper gable roof and a dark door, base centre (x, z), long axis rotated by yaw */
export const hut = (b: Batch, m: Mats, x: number, z: number, yaw: number, w = 5.5, d = 9, h = 2.6) => {
  const y = H(x, z) - 0.15, T = M4(x, y, z, yaw);
  b.add(boxGeo(V(-w / 2, 0, -d / 2), V(w / 2, h, d / 2), 2), m.wood, T);
  b.add(prism(w + 0.7, d + 0.6, 1.7), m.tar, new THREE.Matrix4().multiplyMatrices(T, new THREE.Matrix4().makeTranslation(0, h, 0)));
  b.add(boxGeo(V(-0.6, 0, d / 2), V(0.6, 1.9, d / 2 + 0.04)), m.dark, T);
  for (const s of [-1, 1]) b.add(boxGeo(V(s * w / 2, 1.1, -1.2), V(s * (w / 2 + 0.04), 1.8, 1.2)), m.dark, T);
};
/** grey warship (destroyer / cruiser), bow toward +x of its yaw; waterline at y = 0 */
export const ship = (b: Batch, m: Mats, x: number, z: number, yaw: number, L = 100, Bm = 10, us = false) => {
  const T = M4(x, 0, z, yaw), hullM = us ? m.hullUS : m.hull;
  const s = new THREE.Shape([new THREE.Vector2(-L / 2, -Bm / 2), new THREE.Vector2(L * 0.3, -Bm / 2), new THREE.Vector2(L / 2, 0),
    new THREE.Vector2(L * 0.3, Bm / 2), new THREE.Vector2(-L / 2, Bm / 2 * 0.9)]);
  const hull = new THREE.ExtrudeGeometry(s, { depth: 5.5, bevelEnabled: false });
  hull.rotateX(-Math.PI / 2); hull.translate(0, -1.5, 0);
  b.add(hull, hullM, T);
  const boot = new THREE.ExtrudeGeometry(s, { depth: 0.6, bevelEnabled: false }); boot.rotateX(-Math.PI / 2); boot.scale(1.002, 1, 1.01); boot.translate(0, -0.2, 0);
  b.add(boot, m.boot, T);
  const deck = new THREE.ShapeGeometry(s); deck.rotateX(-Math.PI / 2); deck.translate(0, 4.02, 0);
  b.add(deck, m.deck, T);
  const add = (g: THREE.BufferGeometry, mat: THREE.Material) => b.add(g, mat, T);
  add(boxGeo(V(-L * 0.12, 4, -Bm * 0.3), V(L * 0.12, 7.5, Bm * 0.3), 0, true), hullM); // superstructure
  add(boxGeo(V(L * 0.04, 7.5, -Bm * 0.22), V(L * 0.12, 10.5, Bm * 0.22), 0, true), hullM); // bridge
  add(boxGeo(V(L * 0.05, 9.6, -Bm * 0.23), V(L * 0.121, 10.0, Bm * 0.23)), m.steel); // bridge windows band
  for (const fx of [-0.02, -0.09]) { const f = new THREE.CylinderGeometry(1.3, 1.5, 6, 14); f.translate(L * fx, 10, 0); add(f, hullM);
    const c = new THREE.CylinderGeometry(1.32, 1.32, 0.6, 14); c.translate(L * fx, 12.8, 0); add(c, m.steel); }
  const mast = new THREE.CylinderGeometry(0.18, 0.25, 14, 6); mast.translate(L * 0.02, 14, 0); add(mast, m.steel);
  for (const [tx, dir] of [[L * 0.24, 1], [L * 0.33, 1], [-L * 0.26, -1], [-L * 0.36, -1]] as const) {
    add(boxGeo(V(tx - 2, 4, -1.8), V(tx + 2, 6, 1.8), 0, true), hullM);
    for (const s2 of [-0.5, 0.5]) { const gb = new THREE.CylinderGeometry(0.22, 0.22, 7, 8); gb.rotateZ(Math.PI / 2); gb.translate(tx + dir * 5, 5.1, s2); add(gb, m.steel); }
  }
};
/** small motor barge (daihatsu-like): pointed hull, ramp bow, low wheelhouse at the stern; bow toward +x of yaw */
export const barge = (b: Batch, m: Mats, x: number, z: number, yaw: number) => {
  const T = M4(x, 0, z, yaw);
  const s = new THREE.Shape([new THREE.Vector2(-6.5, -1.7), new THREE.Vector2(4.5, -1.7), new THREE.Vector2(6.5, -0.8), new THREE.Vector2(6.5, 0.8),
    new THREE.Vector2(4.5, 1.7), new THREE.Vector2(-6.5, 1.7)]);
  const hull = new THREE.ExtrudeGeometry(s, { depth: 1.7, bevelEnabled: false }); hull.rotateX(-Math.PI / 2); hull.translate(0, -0.5, 0);
  b.add(hull, m.hull, T);
  const deck = new THREE.ShapeGeometry(s); deck.rotateX(-Math.PI / 2); deck.scale(0.92, 1, 0.85); deck.translate(0, 1.0, 0);
  b.add(deck, m.deck, T);
  b.add(boxGeo(V(-6.2, 1.2, -1.0), V(-4.2, 2.7, 1.0), 0, true), m.hull, T);
  b.add(boxGeo(V(-6.25, 2.2, -1.02), V(-4.15, 2.45, 1.02)), m.steel, T);
  b.add(new THREE.CylinderGeometry(0.15, 0.15, 1.2, 6).translate(-5.6, 3.3, 0), m.steel, T);
};
/** landing craft (LCVP-like), bow ramp toward +x of yaw, ramp lowered by rampK (0 up .. 1 down on the sand) */
export const lcvp = (b: Batch, m: Mats, x: number, y: number, z: number, yaw: number, rampK = 1) => {
  const T = M4(x, y, z, yaw);
  b.add(boxGeo(V(-5.5, -0.6, -1.65), V(4.6, 1.6, -1.45), 0, true), m.craft, T);
  b.add(boxGeo(V(-5.5, -0.6, 1.45), V(4.6, 1.6, 1.65), 0, true), m.craft, T);
  b.add(boxGeo(V(-5.7, -0.6, -1.65), V(-5.5, 2.2, 1.65), 0, true), m.craft, T);
  b.add(boxGeo(V(-5.5, -0.6, -1.45), V(4.6, -0.4, 1.45)), m.deck, T);
  const ramp = boxGeo(V(0, 0, -1.45), V(0.15, 2.3, 1.45));
  ramp.applyMatrix4(new THREE.Matrix4().makeRotationZ(-rampK * 1.35));
  ramp.translate(4.6, -0.5, 0);
  b.add(ramp, m.craft, T);
};
/** bomber silhouette (olive, four engines), nose toward +x; its own group so it can fly */
export const plane = (m: Mats) => {
  const g = new THREE.Group(), add = (geo: THREE.BufferGeometry, mat: THREE.Material) => { const o = new THREE.Mesh(geo, mat); o.castShadow = true; g.add(o); };
  const fus = new THREE.CylinderGeometry(1.3, 0.7, 20, 12); fus.rotateZ(Math.PI / 2); add(fus, m.olive);
  const nose = new THREE.SphereGeometry(1.3, 12, 8); nose.translate(10, 0, 0); add(nose, m.olive);
  add(boxGeo(V(-1.5, -0.2, -16), V(2.2, 0.25, 16), 0, true), m.olive);
  add(boxGeo(V(-10.5, -0.1, -5), V(-8.5, 0.15, 5), 0, true), m.olive);
  for (const z of [-5, 5]) add(boxGeo(V(-10.4, 0, z - 0.15), V(-8.6, 3.4, z + 0.15), 0, true), m.olive);
  for (const z of [-11, -5.5, 5.5, 11]) { const e = new THREE.CylinderGeometry(0.75, 0.75, 3.2, 10); e.rotateZ(Math.PI / 2); e.translate(1.6, -0.1, z); add(e, m.steel); }
  g.traverse((o) => o.layers.set(0));
  return g;
};
/** boulder: squashed low-poly blob */
export const rock = (b: Batch, m: Mats, x: number, z: number, s: number, seed = 1, tall = 1) => {
  const g = new THREE.DodecahedronGeometry(1, 1), p = g.attributes.position as THREE.BufferAttribute;
  for (let i = 0; i < p.count; i++) {
    const k = 1 + 0.18 * Math.sin(p.getX(i) * 5 + seed) * Math.cos(p.getZ(i) * 4 + seed * 2);
    p.setXYZ(i, p.getX(i) * k, p.getY(i) * k * tall, p.getZ(i) * k);
  }
  g.computeVertexNormals();
  b.add(g, m.rock, M4(x, H(x, z) + 0.35 * s * tall, z, seed, s));
};
