# Working Remotion setup (tested 2026-11-02)

```bash
mkdir -p ~/shorts/src/videos/bridge ~/shorts/scripts ~/shorts/public/bridge/kenney
cp setup/package.json setup/tsconfig.json ~/shorts/
cp setup/src/* ~/shorts/src/
cp setup/scripts/bridge-stills.mjs templates/scripts/*.py ~/shorts/scripts/
cp templates/bridge/* ~/shorts/src/videos/bridge/
cd ~/shorts && npm ci || npm install
```

Fixes found while testing:
- `@react-three/postprocessing` must be **3.0.4**. 3.1+/3.2 creates its composer one render late, and Remotion renders
  each frame once, so every frame comes out blank (only the CSS background).
- `three` pinned to **0.180.0**: 0.187 removed `PCFSoftShadowMap` (harder shadows than the template expects).
- Use `--scale=1.3333333333333333` (exact 4/3). `--scale 1.3333` gives a 2559.94 px height and the render fails.
- No GPU (cloud/Linux): `GL=swangle CHROME=/opt/pw-browsers/chromium`; `bridge-stills.mjs` reads `GL`, `CHROME`,
  `PROPS` (JSON inputProps) and `ALLLOG`. Speed without a GPU: ~26 s per 2K frame (≈15 h for 67 s). With a GPU
  (`GL=angle`, default Chrome) ~4 fps.
- Kenney models (`public/bridge/kenney/*.glb`, Nature Kit + Fantasy Town Kit from kenney.nl) are optional: missing
  ones are skipped.

Final render:
```bash
npx remotion render src/index.ts <Comp> out/<name>/video.mp4 --codec h264 --crf 16 --scale=1.3333333333333333
```
