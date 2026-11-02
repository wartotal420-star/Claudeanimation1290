// Kiska as one three.js scene: sky, sea, island terrain, the Japanese camp and pier, warships, landing craft,
// bombers, rocks, and a small dark room far away. update(id, f, camera) poses everything for shot `id` at frame f.
import * as THREE from "three";
import { Batch, boxGeo, V, Kit } from "./build";
import { ctex, waterNear, waterFar, cloudHD } from "./paint";
import { LIGHTS, LOOK, LightPreset } from "./lights";
import { TONE, CHAR, LFB, untone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, stage } from "./cast";
import { FPS, SHOTS, camAt, ShotDef, V3, FIELD, BEACH_X, BZ, ROOM, USS, PIER_X, PIER_END, P12, LANE_X, smooth } from "./story";
import { H, shoreZ, CAMP, MAT, terrain, hut, ship, lcvp, plane, rock, barge, Mats } from "./island";

export const loadKit = () => Promise.resolve({} as Kit);

const SUN_SHOT: Record<number, { az?: number; el?: number }> = { 2: { az: 110, el: 35 }, 13: { az: 120, el: 55 }, 14: { az: -60, el: 55 } };

export class World {
  root = new THREE.Group();
  private pool = new Pool();
  private actors: Actor[] = [];
  private fxs: Fx[] = [];
  private hemi: THREE.HemisphereLight; private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#bccbec", 25, 420);
  private WU: Record<string, THREE.IUniform>;
  private sunCache = new Map<number, THREE.Vector3>();
  private clouds: THREE.Mesh[] = [];
  private cloudMaps: Record<string, THREE.Texture[]> = {};
  private jpShips = new THREE.Group(); private usShip = new THREE.Group();
  private planes: THREE.Group[] = [];
  private flag: THREE.Mesh; private flagPole: THREE.Mesh;
  private room = new THREE.Group();
  private frustum = new THREE.Frustum();
  private m4 = new THREE.Matrix4(); private v = new THREE.Vector3(); private sph = new THREE.Sphere();

  constructor(_kit: Kit) {
    const R = this.root, M: Mats = MAT();
    // ---- sky + light ----
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() },
        c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el));
          c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el));
          c = mix(c, c4, smoothstep(e.z, e.w, el));
          gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(2400, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK);
    R.add(this.sky);
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 1.1);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(4096, 4096);
    R.add(this.hemi, this.sun, this.sun.target);
    for (const k of Object.keys(LOOK)) this.cloudMaps[k] = [0, 1, 2, 3].map((i) => cloudHD(i, LOOK[k as keyof typeof LOOK].cloud));
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2 + 0.3, d = 1500 + (i % 3) * 150;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: this.cloudMaps.day[i % 4], transparent: true, depthWrite: false, fog: false }));
      const w = 380 + (i % 4) * 80;
      m.position.set(Math.cos(a) * d, 260 + (i % 4) * 70, Math.sin(a) * d); m.scale.set(w, w / 2, 1);
      m.layers.set(NOINK);
      this.clouds.push(m); R.add(m);
    }

    // ---- island ----
    R.add(terrain(M));
    const b = new Batch();
    // camp: huts either side of an open lane (x = LANE_X), a hut at the lane's end, sandbagged gun pit, flag
    const huts: [number, number, number][] = [
      [-146, 22, 0], [-134, 22, 0], [-96, 22, 0], [-84, 22, 0], [-146, 34, 0], [-134, 34, 0], [-96, 34, 0], [-84, 34, 0],
      [-146, 4, 0.1], [-84, 4, -0.1], [LANE_X, 28, Math.PI / 2],
      [-160, 14, 0.3], [-70, 14, -0.3],
    ];
    for (const [x, z, yaw] of huts) hut(b, M, x, z, yaw);
    for (let k = 0; k < 14; k++) { const a = (k / 14) * Math.PI * 2; const x = CAMP[0] + 26 + 3.2 * Math.cos(a), z = CAMP[2] - 6 + 3.2 * Math.sin(a);
      b.add(boxGeo(V(-0.7, 0, -0.35), V(0.7, 0.7, 0.35)), M.sandbag, new THREE.Matrix4().compose(V(x, H(x, z), z), new THREE.Quaternion().setFromAxisAngle(V(0, 1, 0), -a), V(1, 1, 1))); }
    { const x = CAMP[0] + 26, z = CAMP[2] - 6, y = H(x, z); const gb = new THREE.CylinderGeometry(0.12, 0.12, 4, 8); gb.rotateZ(1.0); gb.translate(x + 1, y + 1.8, z); b.add(gb, M.steel);
      b.add(new THREE.CylinderGeometry(0.6, 0.7, 1.0, 10).translate(x, y + 0.5, z), M.steel); }
    // crates and drums around the camp
    for (let k = 0; k < 16; k++) { const x = CAMP[0] - 40 + (k * 37) % 80, z = CAMP[2] - 10 + ((k * 23) % 40); if (Math.abs(x - LANE_X) < 4) continue;
      b.add(boxGeo(V(x - 0.5, H(x, z), z - 0.5), V(x + 0.5, H(x, z) + 0.8, z + 0.5)), M.wood); }
    // pier and the two barges at its end
    const zs = shoreZ(PIER_X);
    b.add(boxGeo(V(PIER_X - 2, 1.0, PIER_END), V(PIER_X + 2, 1.45, zs + 6), 2), M.plank);
    for (let z = PIER_END; z < zs; z += 4) for (const s of [-1.8, 1.8]) b.add(new THREE.CylinderGeometry(0.18, 0.18, 8, 6).translate(PIER_X + s, -3, z), M.wood);
    barge(b, M, PIER_X - 4.5, PIER_END - 1, -Math.PI / 2 - 0.1); barge(b, M, PIER_X + 4.2, PIER_END - 3, -Math.PI / 2 + 0.15);
    // landing craft at the beach, ramps down
    for (const x of [38, 50, 62]) lcvp(b, M, x, 0.45, BZ - 7.5, -Math.PI / 2, 1);
    for (const x of [26, 76]) lcvp(b, M, x, 0.2, BZ - 30, -Math.PI / 2, 0);
    // rocks: tundra boulders, cover rocks on the night ridges, and tall pillars that read as figures in the fog
    for (let k = 0; k < 60; k++) { const x = -40 + ((k * 53) % 200), z = -30 + ((k * 31) % 90); if (Math.hypot(x - FIELD[0], z - FIELD[1]) < 9) continue; rock(b, M, x, z, 0.5 + (k % 5) * 0.25, k); }
    for (const [x, z, s] of [[50, 26.5, 0.8], [68, 27, 0.9], [57, 31.6, 0.7]] as const) rock(b, M, x, z, s, 3);
    for (const [x, z] of [[P12[0] - 0.8, P12[1] + 8], [P12[0] + 1.3, P12[1] + 12], [P12[0] - 1.7, P12[1] + 16], [P12[0] + 2.0, P12[1] + 21], [P12[0] - 5.0, P12[1] + 17], [P12[0] + 5.5, P12[1] + 20]] as const) {
      rock(b, M, x, z, 0.45, 7, 3.4); rock(b, M, x, z + 0.05, 0.38, 9, 0.8);
      const top = new THREE.SphereGeometry(0.33, 10, 6, 0, Math.PI * 2, 0, Math.PI / 2); top.translate(x, H(x, z) + 2.25, z); b.add(top, M.rock);
    }
    // the dark room (floor, walls with a doorway on the left, a door on the back wall, warm hall light)
    const r = ROOM, rb = new Batch();
    rb.add(boxGeo(V(r[0] - 3.2, -0.1, r[2] - 3.2), V(r[0] + 3.2, 0.05, r[2] + 3.2), 2), M.roomFloor);
    rb.add(boxGeo(V(r[0] - 3.2, 0, r[2] + 3.0), V(r[0] + 3.2, 2.8, r[2] + 3.2), 2), M.roomWall);
    rb.add(boxGeo(V(r[0] + 3.0, 0, r[2] - 3.2), V(r[0] + 3.2, 2.8, r[2] + 3.2), 2), M.roomWall);
    rb.add(boxGeo(V(r[0] - 3.2, 0, r[2] - 0.6), V(r[0] - 3.0, 2.8, r[2] + 3.2), 2), M.roomWall);
    rb.add(boxGeo(V(r[0] - 3.2, 0, r[2] - 3.2), V(r[0] - 3.0, 2.8, r[2] - 1.8), 2), M.roomWall);
    rb.add(boxGeo(V(r[0] - 3.2, 2.2, r[2] - 1.8), V(r[0] - 3.0, 2.8, r[2] - 0.6), 2), M.roomWall);
    rb.add(boxGeo(V(r[0] + 0.85, 0.05, r[2] + 2.95), V(r[0] + 1.95, 2.15, r[2] + 3.0)), M.door);
    rb.add(boxGeo(V(r[0] + 1.75, 1.0, r[2] + 2.9), V(r[0] + 1.85, 1.1, r[2] + 2.95)), M.steel);
    rb.add(boxGeo(V(r[0] - 3.2, 0, r[2] - 3.2), V(r[0] + 3.2, 0.9, r[2] - 3.0), 2), M.roomWall);
    rb.build(this.room);
    const hall = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 2.2), new THREE.MeshBasicMaterial({ color: new THREE.Color(2.2, 1.5, 0.8), fog: false }));
    hall.position.set(r[0] - 3.3, 1.1, r[2] - 1.2); hall.rotation.y = Math.PI / 2; hall.layers.set(NOINK);
    this.room.add(hall);
    R.add(this.room);
    b.build(R);
    // flag over the camp (gone after the evacuation)
    this.flagPole = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 9, 8), M.pole);
    const fx = LANE_X + 6, fz = CAMP[2] + 8;
    this.flagPole.position.set(fx, H(fx, fz) + 4.5, fz); this.flagPole.castShadow = true; R.add(this.flagPole);
    this.flag = new THREE.Mesh(new THREE.PlaneGeometry(2.1, 1.4, 12, 1), M.flag);
    this.flag.position.set(fx, H(fx, fz) + 8.2, fz); this.flag.castShadow = true; this.flag.frustumCulled = false; R.add(this.flag);
    // ships: Japanese cruiser + destroyer (they slide into the harbor in shot 3), the US destroyer (lookout, mine)
    const jb = new Batch();
    ship(jb, M, -40, -75, 0.25, 120, 12);
    ship(jb, M, 25, -110, 0.1, 95, 10);
    jb.build(this.jpShips);
    this.jpShips.position.set(PIER_X, 0, -80);
    R.add(this.jpShips);
    const ub = new Batch();
    ship(ub, M, 0, 0, 0, 100, 10, true);
    ub.build(this.usShip);
    this.usShip.position.set(USS[0], 0, USS[2]);
    R.add(this.usShip);
    for (let i = 0; i < 3; i++) { const p = plane(M); this.planes.push(p); R.add(p); }

    // ---- sea ----
    const wNear = waterNear(), wFar = waterFar();
    for (const t of [wNear, wFar]) { t.colorSpace = THREE.NoColorSpace; t.anisotropy = 16; t.needsUpdate = true; }
    this.WU = {
      wNearC: { value: new THREE.Color() }, wMidC: { value: new THREE.Color() }, wFarC: { value: new THREE.Color() },
      wCrest: { value: new THREE.Color() }, wTrough: { value: new THREE.Color() }, wGlint: { value: new THREE.Color() },
      wShade: { value: new THREE.Vector3(0.5, 0.56, 0.72) }, wNearTex: { value: wNear }, wFarTex: { value: wFar }, wTime: { value: 0 },
    };
    const waterM = new THREE.MeshLambertMaterial({ color: 0xffffff });
    waterM.onBeforeCompile = (sh) => {
      Object.assign(sh.uniforms, this.WU);
      sh.vertexShader = sh.vertexShader
        .replace("#include <common>", "#include <common>\nvarying vec3 vWP;")
        .replace("#include <project_vertex>", "#include <project_vertex>\nvWP = (modelMatrix * vec4(transformed, 1.0)).xyz;");
      sh.fragmentShader = sh.fragmentShader
        .replace("#include <common>", WATER_DECL)
        .replace("#include <map_fragment>", WATER_COL)
        .replace("#include <lights_fragment_begin>", "float sunVis = 1.0;\n" + LFB)
        .replace("#include <lights_fragment_end>", "#include <lights_fragment_end>\n  reflectedLight.directDiffuse = diffuseColor.rgb * mix(wShade, vec3(1.0), sunVis);\n  reflectedLight.indirectDiffuse = vec3(0.0);");
    };
    waterM.customProgramCacheKey = () => "sea1";
    const sea = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000, 150, 150).rotateX(-Math.PI / 2), waterM); // small cells: huge triangles lose depth precision in software GL
    sea.position.y = 0.0; sea.receiveShadow = true;
    R.add(sea);
  }

  private shotSun(id: number, s: ShotDef, L: LightPreset) {
    let v = this.sunCache.get(id);
    if (v) return v;
    let fx = 0, fz = 0;
    for (let f = s.a; f < s.b; f += 3) {
      const c = camAt(id, f), x = c.look[0] - c.pos[0], z = c.look[2] - c.pos[2], n = Math.hypot(x, z) || 1;
      fx += x / n; fz += z / n;
    }
    const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
    const az = THREE.MathUtils.degToRad(s.sunAz ?? SUN_SHOT[id]?.az ?? L.az), el = THREE.MathUtils.degToRad(s.sunEl ?? SUN_SHOT[id]?.el ?? L.el);
    const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
    v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize();
    this.sunCache.set(id, v);
    return v;
  }
  private actor(i: number) { while (this.actors.length <= i) this.actors.push(new Actor(this.root)); return this.actors[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }

  update(id: number, f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = SHOTS[id - 1], L = LIGHTS[s.light], K = LOOK[s.light];
    const c = camAt(id, f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll);
    cam.fov = c.fov; cam.near = 0.25; cam.far = 3000; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = V(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    // ---- light rig ----
    const sunDir = this.shotSun(id, s, L);
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemiI;
    this.sun.color.set(L.sunCol); this.sun.intensity = L.sunI;
    const Rr = THREE.MathUtils.clamp(dist * 1.15 + 7, 12, 140);
    this.sun.position.copy(focus).addScaledVector(sunDir, 300); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera;
    sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 20; sc.far = 700; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * (Rr / 12);
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad;
    CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    // ---- sky, fog, clouds ----
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg));
    su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    const [fn, ff] = s.fog ?? [L.fogNear, L.fogFar];
    untone(L.fog, this.fog.color); this.fog.near = fn; this.fog.far = ff;
    scene.fog = this.fog; scene.background = null;
    const showClouds = s.light === "day" || s.light === "grey";
    for (let i = 0; i < this.clouds.length; i++) {
      const m = this.clouds[i], mat = m.material as THREE.MeshBasicMaterial;
      m.visible = showClouds;
      m.lookAt(cam.position.x, m.position.y, cam.position.z);
      mat.map = this.cloudMaps[s.light][i % 4];
    }
    const W = this.WU, wc = K.water;
    untone(wc.near, W.wNearC.value); untone(wc.mid, W.wMidC.value); untone(wc.far, W.wFarC.value);
    untone(wc.crest, W.wCrest.value); untone(wc.trough, W.wTrough.value); untone(wc.glint, W.wGlint.value);
    W.wShade.value.set(...wc.shade); W.wTime.value = t;
    // ---- props that move or come and go ----
    this.flag.visible = this.flagPole.visible = id <= 3;
    const p = this.flag.geometry.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < p.count; i++) { const u = (i % 13) / 12, y = i < 13 ? 0.7 : -0.7; p.setXYZ(i, u * 2.1, y + 0.06 * u * Math.sin(t * 4 - u * 3), 0.25 * u * Math.sin(t * 5 - u * 5)); }
    p.needsUpdate = true;
    // Japanese ships glide into the harbor in shot 3 (and are long gone afterwards)
    this.jpShips.visible = id === 3;
    this.jpShips.position.x = PIER_X + 70 * (1 - smooth((f - 336) / 95));
    // the US destroyer: rolls when the mine goes off
    const tm = (f - 1589) / FPS;
    this.usShip.visible = id === 4 || id === 15;
    this.usShip.rotation.x = tm > 0 ? 0.07 * Math.exp(-tm * 1.2) * Math.sin(tm * 5) : 0;
    this.usShip.position.y = tm > 0 ? -0.6 * Math.exp(-tm * 1.5) * Math.sin(tm * 4) : 0;
    // bombers pass over the camp in shot 5
    this.planes.forEach((pl, i) => {
      pl.visible = id === 5;
      const u = (f - 532) / 70, x = CAMP[0] - 6 + (i - 1) * 22, z = CAMP[2] - 40 + 200 * u - Math.abs(i - 1) * 14;
      pl.position.set(x, 52 + (i % 2) * 4, z); pl.rotation.set(0, -Math.PI / 2, 0);
    });
    this.room.visible = id === 13 || id === 14;
    // ---- cast + effects ----
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const st = stage(id, t, { pos: cam.position, right }, sunDir);
    this.frustum.setFromProjectionMatrix(this.m4.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
    let ai = 0;
    const used: Actor[] = [];
    for (const pl of st.places) {
      const sc2 = pl.scale ?? 1;
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(pl.x, pl.y + 1.1 * sc2, pl.z), 3.5))) continue;
      const a = this.actor(ai++);
      const [w, h, k] = pl.size ?? [300, 500, 0.5];
      a.r = this.pool.req(pl.key, w, h, k, pl.draw);
      a.mesh.visible = true;
      a.mesh.position.set(pl.x, pl.y, pl.z);
      a.mesh.rotation.set(0, pl.yaw ?? Math.atan2(cam.position.x - pl.x, cam.position.z - pl.z), pl.roll ?? 0);
      a.mesh.scale.set(pl.mirror ? -sc2 : sc2, sc2, sc2);
      a.mesh.castShadow = L.actorShadow;
      used.push(a);
    }
    for (let i = ai; i < this.actors.length; i++) this.actors[i].mesh.visible = false;
    let fi = 0;
    const fused: Fx[] = [];
    for (const pl of st.fx) {
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(pl.x, pl.y, pl.z), Math.max(Math.abs(pl.w), pl.h)))) continue;
      const e2 = this.fx(fi++);
      e2.r = this.pool.req(pl.key, pl.cw, pl.ch, 1, pl.draw);
      e2.use(!!pl.soft, pl.glow ?? 1);
      e2.mesh.visible = true;
      e2.mesh.position.set(pl.x, pl.y, pl.z);
      if (pl.flat) e2.mesh.rotation.set(-Math.PI / 2, 0, pl.rot ?? 0);
      else { e2.mesh.quaternion.copy(cam.quaternion); e2.mesh.rotateZ(pl.rot ?? 0); }
      e2.mesh.scale.set(pl.w, pl.h, 1);
      fused.push(e2);
    }
    for (let i = fi; i < this.fxs.length; i++) this.fxs[i].mesh.visible = false;
    this.pool.flush();
    for (const a of used) a.bind();
    for (const e3 of fused) e3.bind();
    return focus;
  }
}

const WATER_DECL = `#include <common>
varying vec3 vWP;
uniform vec3 wNearC, wMidC, wFarC, wCrest, wTrough, wGlint, wShade;
uniform sampler2D wNearTex, wFarTex;
uniform float wTime;`;
const WATER_COL = `
  vec3 wV = vWP - cameraPosition;
  float wd = length(wV);
  float wDep = asin(clamp(-wV.y / wd, 0.0, 1.0));
  float wf = 1.0 - smoothstep(0.0, 0.42, wDep);
  vec3 wc = mix(mix(wNearC, wMidC, smoothstep(0.0, 0.55, wf)), wFarC, smoothstep(0.55, 1.0, wf));
  vec2 wp = vWP.xz + vec2(0.25 * wTime, 0.1 * wTime);
  vec4 mk = mix(texture2D(wNearTex, wp / 8.0), texture2D(wFarTex, wp / 40.0 + 0.37), smoothstep(25.0, 90.0, wd));
  wc = mix(wc, wTrough, mk.g * 0.6);
  wc = mix(wc, wCrest, mk.r * 0.7);
  wc = mix(wc, wGlint, mk.b * (0.3 + 0.5 * wf));
  diffuseColor.rgb = wc;`;
void ctex; void BEACH_X;
