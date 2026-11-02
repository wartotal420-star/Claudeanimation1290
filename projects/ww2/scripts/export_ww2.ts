// Export WW2 shots for Blender: per frame the camera, lens, and every character / effect card (set-local three.js
// coordinates), plus each unique drawing as a PNG (Node canvas). Usage:
//   npx tsx scripts/export_ww2.ts <outDir> [shotIds comma list | all] [step=1]
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { createCanvas } from "@napi-rs/canvas";

// minimal DOM shim: cast.ts makes tiny placeholder canvases at load time
(globalThis as any).document = { createElement: () => createCanvas(2, 2) };
(globalThis as any).window = globalThis;

const [outDir, which = "all", stepS = "1"] = process.argv.slice(2);
const step = Number(stepS);
const THREE = await import("three");
const story = await import("../src/videos/ww2/story");
const cast = await import("../src/videos/ww2/cast");
const sets = await import("../src/videos/ww2/sets");
const lights = await import("../src/videos/ww2/lights");
const { Pen } = await import("../src/videos/ww2/toon");

fs.mkdirSync(path.join(outDir, "cards"), { recursive: true });
const done = new Set(fs.readdirSync(path.join(outDir, "cards")).map((f) => f.replace(".png", "")));
const hashOf = (key: string, w: number, h: number) => crypto.createHash("sha1").update(`${w}x${h}|${key}`).digest("hex").slice(0, 16);
const draw = (key: string, w: number, h: number, k: number, fn: (p: any) => void) => {
  const id = hashOf(key, w, h);
  if (!done.has(id)) {
    const c = createCanvas(w, h), g = c.getContext("2d") as any;
    g.setTransform(k, 0, 0, k, 0, 0);
    fn(new Pen(g));
    fs.writeFileSync(path.join(outDir, "cards", id + ".png"), c.toBuffer("image/png"));
    done.add(id);
  }
  return id;
};
/** camera-relative sun as world.ts shotSun (mean view direction turned by az, lifted by el) */
const sunCache = new Map<number, InstanceType<typeof THREE.Vector3>>();
const shotSun = (s: any) => {
  let v = sunCache.get(s.id); if (v) return v;
  let fx = 0, fz = 0;
  for (let f = s.a; f < s.b; f += 3) { const c = story.camAt(s.id, f), x = c.look[0] - c.pos[0], z = c.look[2] - c.pos[2], n = Math.hypot(x, z) || 1; fx += x / n; fz += z / n; }
  const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
  const L = (lights.LIGHTS as any)[s.light];
  const az = THREE.MathUtils.degToRad(s.sunAz ?? L.az), el = THREE.MathUtils.degToRad(s.sunEl ?? L.el);
  const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
  v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize(); sunCache.set(s.id, v); return v;
};

// "all" runs the shots in batches as child processes: native canvas memory is not freed in time across ~6000 drawings
// and one long process gets killed for memory.
let ids: number[] = which === "all" ? story.SHOTS.map((s: any) => s.id) : which.split(",").map(Number);
if (which === "all") {
  const { spawnSync } = await import("node:child_process");
  for (let i = 0; i < ids.length; i += 4) {
    const r = spawnSync(process.execPath, [...process.execArgv, process.argv[1], outDir, ids.slice(i, i + 4).join(","), stepS], { stdio: "inherit" });
    if (r.status !== 0) { console.error(`export batch ${ids.slice(i, i + 4)} failed (${r.status ?? r.signal})`); process.exit(1); }
  }
  ids = [];
}
const r3 = (v: number) => Math.round(v * 1000) / 1000;
for (const id of ids) {
  const s = story.SHOTS[id - 1], o = sets.setOrigin(s.set), x = story.XFADE[id] ?? 0, xn = story.XFADE[id + 1] ?? 0;
  const f0 = Math.max(0, s.a - Math.ceil(x / 2)), f1 = Math.min(story.TOTAL, s.b + Math.ceil(xn / 2));
  const frames: any[] = [];
  for (let f = f0; f < f1; f += step) {
    const c = story.camAt(id, f);
    const pos = new THREE.Vector3(...c.pos), look = new THREE.Vector3(...c.look);
    const fwd = look.clone().sub(pos).normalize(), right = fwd.clone().cross(new THREE.Vector3(0, 1, 0)).normalize();
    const st = cast.stage(id, f, { pos, right }, shotSun(s));
    const L = (v: number[]) => [r3(v[0] - o[0]), r3(v[1] - o[1]), r3(v[2] - o[2])];
    const d = story.dofAt(f);
    const places = st.places.map((p: any) => {
      const [w, h, k] = p.size ?? [300, 500, 0.5];
      return { h: draw(p.key, w, h, k, p.draw), p: L([p.x, p.y, p.z]), s: r3(p.scale ?? 1), m: p.mirror ? 1 : 0, yaw: p.yaw ?? null, roll: p.roll ?? 0 };
    });
    const fx = st.fx.filter((e: any) => !e.key.startsWith("blob|")).map((e: any) => ({
      h: draw(e.key, e.cw, e.ch, 1, e.draw), p: L([e.x, e.y, e.z]), w: r3(e.w), hh: r3(e.h), flat: e.flat ? 1 : 0, rot: r3(e.rot ?? 0), glow: e.glow ?? 1, soft: e.soft ? 1 : 0, op: e.opacity ?? 1,
    }));
    frames.push({ f, cam: { pos: L(c.pos), look: L(c.look), fov: r3(c.fov), roll: r3(c.roll) }, dof: { c: r3(d.cInf), focus: d.focus ? L(d.focus(f)) : null }, places, fx });
  }
  fs.writeFileSync(path.join(outDir, `shot${String(id).padStart(2, "0")}.json`), JSON.stringify({ id, set: s.set, night: !!s.night, light: s.light, a: s.a, b: s.b, f0, f1, frames }));
  console.log(`shot ${id}: ${frames.length} frames, ${done.size} cards total`);
}

// timeline (shots, crossfades, total) + full-frame title / chapter card PNGs for the Blender assembly
{
  const cardsOut: any[] = [];
  story.CARDS.forEach((c: any, i: number) => {
    const W = story.W, H = story.H, cv = createCanvas(W, H), g = cv.getContext("2d") as any, title = c.kind === "title";
    if (!title) { g.fillStyle = "rgba(10,8,14,0.72)"; g.fillRect(0, 0, W, H); }
    else { const gr = g.createRadialGradient(W / 2, H / 2, H * 0.2, W / 2, H / 2, H * 0.9); gr.addColorStop(0, "rgba(0,0,0,0)"); gr.addColorStop(1, "rgba(0,0,0,0.55)"); g.fillStyle = gr; g.fillRect(0, 0, W, H); }
    g.textAlign = "center"; g.textBaseline = "middle"; g.shadowColor = "rgba(0,0,0,0.85)"; g.shadowBlur = 18; g.shadowOffsetY = 4;
    const sizes = title ? [54, 132] : [44, 110, 44], gaps = title ? [0, 100] : [0, 90, 170];
    const y0 = H / 2 - (title ? 50 : 85);
    c.lines.forEach((l: string, k: number) => {
      g.font = `bold ${sizes[k]}px Georgia, "Times New Roman", "DejaVu Serif", serif`; g.fillStyle = !title && k === 0 ? "#e8b85a" : "#f4ead2";
      g.fillText(l.split("").join(String.fromCharCode(8202)), W / 2, y0 + gaps[k]);
    });
    const file = `titlecard${i}.png`; fs.writeFileSync(path.join(outDir, file), cv.toBuffer("image/png"));
    cardsOut.push({ a: c.a, b: c.b, file });
  });
  fs.writeFileSync(path.join(outDir, "timeline.json"), JSON.stringify({ total: story.TOTAL, fps: story.FPS, xfade: story.XFADE,
    shots: story.SHOTS.map((s: any) => ({ id: s.id, a: s.a, b: s.b })), cards: cardsOut }));
  console.log("timeline + title cards written");
}
