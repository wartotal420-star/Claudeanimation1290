# Kiska short ("The Island That Was Already Empty")

Built on the bridge template (`templates/bridge/`) and the tested setup in `setup/`.

- `src/videos/kiska/`: the short (composition `KiskaShort`, 1080x1920, 30 fps, 1940 frames).
  New files: `island.ts` (terrain, camp, ships, landing craft, planes, rocks, room), `story.ts` (17 shots timed to the
  voice), `cast.ts` (staging), `world.ts`; `toon.ts` adds the US / Canadian / Japanese soldiers, sailor, kid, dogs, coat,
  aim pose and effects; `lights.ts` adds the grey / fog / night presets.
- `audio/`: synthesized score + SFX + mix (`python3 mix.py`, needs `../voice/voice.wav` + `../voice/words.json`).
- `voice/words.json`: word timings, made by `tools/align.py` (pocketsphinx forced alignment of SCRIPT.md to the voice).
  The voice file itself is not in the repo.

Render (in a project set up per `setup/README.md`, with `src/` copied over):
```bash
npx remotion render src/index.ts KiskaShort out/kiska.mp4 --codec h264 --crf 16
ffmpeg -i out/kiska.mp4 -i audio/mix.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k kiska_final.mp4
```
Add `--scale=1.3333333333333333` for 1440x2560. No GPU: add `--gl=swangle` (about 20 s per frame).
