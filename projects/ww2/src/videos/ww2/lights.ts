// Light presets per time of day. The sun is CAMERA-RELATIVE and frozen per shot (world.ts update()):
// az = degrees from the shot camera's forward axis (0 = sun straight ahead = backlight, +90 = screen right,
// 180 = behind camera), el = elevation. lit/shade/lift are LINEAR RGB multipliers for shade.ts (may exceed 1).
// Field names follow lighting.md 9.1 exactly (the CHAR and POST agents read them); values are tuned on renders.
type C3 = [number, number, number];
export type LightPreset = {
  az: number; el: number;
  lit: C3; shade: C3; lift: C3; lambert: number; sideK: number; term: number;      // world two-tone (shade.ts)
  charTint: C3; charShade: number; charGrad: number; bodyGrad: number; sideTint: C3; // character cards (cast.ts)
  blob: C3; actorShadow: boolean;                                                    // contact blobs / card shadows
  top: string; hor: string; skyCurve: C3; fog: string; fogNear: number; fogFar: number; sunDisc: string; // depth.md 6.5
  sunCol: string; sunI: number; sky: string; ground: string; hemiI: number;         // three lights (unpatched mats only)
  bias: number; normalBias: number;
};
export type LightName = "day" | "golden" | "grey" | "fog" | "night" | "interior" | "void" | "dusk" | "gloom";
export const LIGHTS: Record<LightName, LightPreset> = {
  day: {
    az: 75, el: 48,
    lit: [1.58, 1.5, 1.33], shade: [0.3, 0.29, 0.36], lift: [0.05, 0.06, 0.11], lambert: 0.35, sideK: 0.84, term: 0.2,
    charTint: [1.0, 0.94, 0.92], charShade: 0.86, charGrad: 0.07, bodyGrad: 0.2, sideTint: [0.92, 0.90, 0.96],
    blob: [0.62, 0.58, 0.58], actorShadow: false,
    top: "#3e7fd2", hor: "#b8d0ec", skyCurve: [0.0, 0.5, 0.6], fog: "#b8d0ec", fogNear: 25, fogFar: 300, sunDisc: "#000000",
    sunCol: "#fff3e0", sunI: 2.8, sky: "#dcecff", ground: "#b49a78", hemiI: 0.55,
    bias: -0.00025, normalBias: 0.015,
  },
  golden: {
    az: 6, el: 7,
    lit: [1.5, 0.68, 0.24], shade: [0.15, 0.15, 0.3], lift: [0.04, 0.06, 0.17], lambert: 0.35, sideK: 0.82, term: 0.07,
    charTint: [1.0, 0.78, 0.56], charShade: 0.88, charGrad: 0.1, bodyGrad: 0.25, sideTint: [0.85, 0.80, 0.95],
    blob: [0.75, 0.74, 0.9], actorShadow: true,
    top: "#6a4f8c", hor: "#ffd08a", skyCurve: [0.05, 0.6, 1.0], fog: "#efb489", fogNear: 50, fogFar: 380, sunDisc: "#ffcf9e",
    sunCol: "#ffab5e", sunI: 5.5, sky: "#d8b0b8", ground: "#8a6a60", hemiI: 0.5,
    bias: -0.0006, normalBias: 0.03,
  },
  // Kiska: Aleutian overcast (soft high light, cool, long haze)
  grey: {
    az: 60, el: 55,
    lit: [1.3, 1.3, 1.3], shade: [0.46, 0.48, 0.58], lift: [0.06, 0.07, 0.11], lambert: 0.3, sideK: 0.86, term: 0.35,
    charTint: [0.96, 0.97, 1.0], charShade: 0.9, charGrad: 0.06, bodyGrad: 0.18, sideTint: [0.93, 0.94, 0.98],
    blob: [0.62, 0.6, 0.64], actorShadow: false,
    top: "#7f97b2", hor: "#cdd6df", skyCurve: [0, 0.5, 0.6], fog: "#c6d0da", fogNear: 30, fogFar: 420, sunDisc: "#000000",
    sunCol: "#f4f6ff", sunI: 2.2, sky: "#dfe7f0", ground: "#8a8a7a", hemiI: 0.6,
    bias: -0.00025, normalBias: 0.015,
  },
  // thick sea fog: everything past ~40 m melts into pale blue-grey
  fog: {
    az: 50, el: 50,
    lit: [1.1, 1.12, 1.16], shade: [0.55, 0.58, 0.66], lift: [0.1, 0.11, 0.14], lambert: 0.25, sideK: 0.9, term: 0.4,
    charTint: [0.93, 0.95, 1.0], charShade: 0.92, charGrad: 0.05, bodyGrad: 0.15, sideTint: [0.94, 0.95, 0.99],
    blob: [0.7, 0.7, 0.74], actorShadow: false,
    top: "#c3cdd7", hor: "#c9d2db", skyCurve: [0, 0.5, 0.6], fog: "#c9d2db", fogNear: 2, fogFar: 46, sunDisc: "#000000",
    sunCol: "#f4f6ff", sunI: 1.8, sky: "#e6ecf2", ground: "#9a9a90", hemiI: 0.7,
    bias: -0.00025, normalBias: 0.015,
  },
  // moonlit fog night (also the dark room)
  night: {
    az: 35, el: 40,
    lit: [0.3, 0.38, 0.72], shade: [0.08, 0.1, 0.2], lift: [0.03, 0.04, 0.09], lambert: 0.35, sideK: 0.84, term: 0.25,
    charTint: [0.62, 0.72, 1.0], charShade: 0.8, charGrad: 0.1, bodyGrad: 0.25, sideTint: [0.7, 0.78, 1.0],
    blob: [0.6, 0.62, 0.8], actorShadow: false,
    top: "#141b33", hor: "#2d3b5e", skyCurve: [0, 0.5, 0.6], fog: "#2b385a", fogNear: 6, fogFar: 85, sunDisc: "#000000",
    sunCol: "#b8c8ff", sunI: 1.6, sky: "#3a4a78", ground: "#1c2030", hemiI: 0.4,
    bias: -0.00025, normalBias: 0.015,
  },
  // warm lamp-lit interior: amber key, deep blue-violet shadows
  interior: {
    az: 55, el: 50,
    lit: [1.6, 1.2, 0.78], shade: [0.2, 0.18, 0.32], lift: [0.04, 0.04, 0.1], lambert: 0.4, sideK: 0.84, term: 0.18,
    charTint: [1.0, 0.88, 0.74], charShade: 0.85, charGrad: 0.1, bodyGrad: 0.24, sideTint: [0.85, 0.82, 0.95],
    blob: [0.6, 0.55, 0.6], actorShadow: true,
    top: "#1a1424", hor: "#2a1e2a", skyCurve: [0, 0.5, 0.6], fog: "#2a2030", fogNear: 25, fogFar: 140, sunDisc: "#000000",
    sunCol: "#ffd9a8", sunI: 2.6, sky: "#ffe0c0", ground: "#5a4030", hemiI: 0.5,
    bias: -0.0004, normalBias: 0.02,
  },
  // black void with one cool-white key (cold open)
  void: {
    az: 40, el: 55,
    lit: [1.5, 1.42, 1.3], shade: [0.1, 0.1, 0.16], lift: [0.02, 0.02, 0.05], lambert: 0.45, sideK: 0.8, term: 0.15,
    charTint: [1.0, 0.97, 0.94], charShade: 0.82, charGrad: 0.12, bodyGrad: 0.25, sideTint: [0.85, 0.85, 0.95],
    blob: [0.4, 0.4, 0.45], actorShadow: true,
    top: "#050508", hor: "#0c0b10", skyCurve: [0, 0.5, 0.6], fog: "#0a090d", fogNear: 12, fogFar: 40, sunDisc: "#000000",
    sunCol: "#ffffff", sunI: 2.6, sky: "#ffffff", ground: "#202020", hemiI: 0.3,
    bias: -0.0004, normalBias: 0.02,
  },
  // war dusk: orange low sun, smoky purple shadows
  dusk: {
    az: 20, el: 10,
    lit: [1.55, 0.9, 0.45], shade: [0.17, 0.14, 0.28], lift: [0.05, 0.04, 0.12], lambert: 0.35, sideK: 0.82, term: 0.1,
    charTint: [1.0, 0.82, 0.62], charShade: 0.86, charGrad: 0.1, bodyGrad: 0.25, sideTint: [0.85, 0.78, 0.95],
    blob: [0.7, 0.66, 0.85], actorShadow: true,
    top: "#3a2a5a", hor: "#ff9a5a", skyCurve: [0.05, 0.6, 1.0], fog: "#c8785a", fogNear: 40, fogFar: 320, sunDisc: "#ffb070",
    sunCol: "#ff9a50", sunI: 4.5, sky: "#d8a0a8", ground: "#6a4a40", hemiI: 0.5,
    bias: -0.0006, normalBias: 0.03,
  },
  // grim grey day for the depression street (still saturated albedo, cool light)
  gloom: {
    az: 60, el: 40,
    lit: [1.2, 1.22, 1.3], shade: [0.3, 0.32, 0.45], lift: [0.05, 0.06, 0.1], lambert: 0.35, sideK: 0.84, term: 0.25,
    charTint: [0.94, 0.95, 1.0], charShade: 0.86, charGrad: 0.08, bodyGrad: 0.2, sideTint: [0.9, 0.92, 0.98],
    blob: [0.55, 0.55, 0.62], actorShadow: false,
    top: "#5a6a7a", hor: "#a8b0b8", skyCurve: [0, 0.5, 0.6], fog: "#9aa2ac", fogNear: 30, fogFar: 160, sunDisc: "#000000",
    sunCol: "#e8eef8", sunI: 2.0, sky: "#c8d0d8", ground: "#6a6a6a", hemiI: 0.5,
    bias: -0.0003, normalBias: 0.015,
  },
};

export type WorldLook = {
  sky: { c: string[]; e: number[] };                         // 5 stops: c[i] at elevation e[i] (deg), smoothstep between
  water: { near: string; mid: string; far: string; crest: string; trough: string; glint: string; shade: C3 };
  bounce: C3;                                                 // shade.ts uBounce: albedo x bounce on shaded faces turned to the lens
  sat: number;                                                // shade.ts uSat: world albedo saturation (1 = as painted)
  cloud: { lit: string; mid: string; shade: string };
};
export const LOOK: Record<LightName, WorldLook> = {
  day: {
    // depth.md 2.2: horizon #9fb6e6 just above the skyline, upper sky #5e93d9 at ~20 deg (grade: frame top #5997e2)
    sky: { c: ["#b8d0ec", "#9cbfea", "#6a9fe0", "#4f8cdb", "#3373cc"], e: [0, 3, 8, 16, 40] },
    water: { near: "#22a7b6", mid: "#167fb2", far: "#1a5596", crest: "#7ddfe8", trough: "#0e4a80", glint: "#ffffff", shade: [0.5, 0.56, 0.72] },
    cloud: { lit: "#fbf8f1", mid: "#e1e5f3", shade: "#c3cbe9" },
    bounce: [0, 0, 0],
    sat: 1.08,
  },
  golden: {
    // sunset, not dusk: #ffd08a horizon, peach/orange through ~10 deg, warm rose at 20, muted warm mauve only near the top
    // (the golden grade adds ~+11/255 blue to shadows/mids, so these lean warm)
    sky: { c: ["#ffc47c", "#f7ae78", "#e8967c", "#c4848e", "#8a6f8a"], e: [0, 4, 10, 20, 40] },
    water: { near: "#1e3a6e", mid: "#355f96", far: "#d4a48e", crest: "#d9a088", trough: "#16294f", glint: "#ffe2b0", shade: [0.42, 0.46, 0.72] },
    cloud: { lit: "#ffd2a8", mid: "#f2a08f", shade: "#a98fc4" },
    bounce: [0.04, 0.02, 0.0],
    sat: 1.1,
  },
  grey: {
    sky: { c: ["#cdd6df", "#bfcad6", "#a7b7c8", "#94a8bd", "#7f97b2"], e: [0, 3, 8, 16, 40] },
    water: { near: "#3f6f80", mid: "#4f7b8c", far: "#9fb1bf", crest: "#c9dbe2", trough: "#2b4f62", glint: "#e8f0f4", shade: [0.55, 0.6, 0.7] },
    cloud: { lit: "#e9edf2", mid: "#d2d9e2", shade: "#b4bfcc" },
    bounce: [0, 0, 0], sat: 0.95,
  },
  fog: {
    sky: { c: ["#c9d2db", "#c7d0d9", "#c5ced8", "#c3cdd7", "#c3cdd7"], e: [0, 3, 8, 16, 40] },
    water: { near: "#5f808e", mid: "#8ea5b2", far: "#c9d2db", crest: "#d6e2e8", trough: "#4a6a7a", glint: "#eef3f6", shade: [0.6, 0.64, 0.72] },
    cloud: { lit: "#e9edf2", mid: "#d2d9e2", shade: "#b4bfcc" },
    bounce: [0, 0, 0], sat: 0.9,
  },
  night: {
    sky: { c: ["#2d3b5e", "#26335a", "#1f2a4c", "#19223f", "#141b33"], e: [0, 3, 8, 16, 40] },
    water: { near: "#1a2846", mid: "#22335a", far: "#2d3b5e", crest: "#5a6f9e", trough: "#101a32", glint: "#9fb4e8", shade: [0.4, 0.45, 0.65] },
    cloud: { lit: "#4a5880", mid: "#3a4670", shade: "#2a3458" },
    bounce: [0, 0, 0], sat: 1.0,
  },
  interior: {
    sky: { c: ["#2a1e2a", "#241a28", "#1e1626", "#1a1424", "#1a1424"], e: [0, 3, 8, 16, 40] },
    water: { near: "#1a2846", mid: "#22335a", far: "#2d3b5e", crest: "#5a6f9e", trough: "#101a32", glint: "#9fb4e8", shade: [0.4, 0.45, 0.65] },
    cloud: { lit: "#4a5880", mid: "#3a4670", shade: "#2a3458" }, bounce: [0.05, 0.03, 0.0], sat: 1.12,
  },
  void: {
    sky: { c: ["#0c0b10", "#0a090e", "#08070c", "#060509", "#050508"], e: [0, 3, 8, 16, 40] },
    water: { near: "#1a2846", mid: "#22335a", far: "#2d3b5e", crest: "#5a6f9e", trough: "#101a32", glint: "#9fb4e8", shade: [0.4, 0.45, 0.65] },
    cloud: { lit: "#4a5880", mid: "#3a4670", shade: "#2a3458" }, bounce: [0, 0, 0], sat: 1.1,
  },
  dusk: {
    sky: { c: ["#ffb070", "#f08a5a", "#c8646a", "#7a4a78", "#3a2a5a"], e: [0, 4, 10, 20, 40] },
    water: { near: "#2a2a4a", mid: "#4a3a5a", far: "#e88a5a", crest: "#f2a878", trough: "#1a1a3a", glint: "#ffd0a0", shade: [0.42, 0.4, 0.62] },
    cloud: { lit: "#ffb888", mid: "#c87a7a", shade: "#6a4a7a" }, bounce: [0.05, 0.02, 0.0], sat: 1.12,
  },
  gloom: {
    sky: { c: ["#a8b0b8", "#98a2ae", "#808e9e", "#6a7a8a", "#5a6a7a"], e: [0, 3, 8, 16, 40] },
    water: { near: "#3f6f80", mid: "#4f7b8c", far: "#9fb1bf", crest: "#c9dbe2", trough: "#2b4f62", glint: "#e8f0f4", shade: [0.55, 0.6, 0.7] },
    cloud: { lit: "#d8dde4", mid: "#b8c0ca", shade: "#98a2b0" }, bounce: [0, 0, 0], sat: 1.0,
  },
};
