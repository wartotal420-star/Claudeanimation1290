#!/bin/bash
# WW2 part 1 in Blender, one command on the Mac:
#   ./render_blender_mac.sh stills           one frame every 1.5 s in final quality (~15 min) -> Finder
#   ./render_blender_mac.sh preview          EEVEE, half size (fast check of every shot)
#   ./render_blender_mac.sh final            Cycles 16 spp + denoise, full 1920x1080
#   ./render_blender_mac.sh preview 9,14     only these shots (then assembles whatever exists)
# Re-running continues where it stopped (finished frames are skipped).
set -e
cd "$(dirname "$0")"
MODE=${1:-preview}; ONLY=${2:-all}
STEP=1
case "$MODE" in
  stills)  ENGINE=cycles; SPP=16; PCT=100; STEP=45 ;;
  preview) ENGINE=eevee;  SPP=16; PCT=50 ;;
  final)   ENGINE=cycles; SPP=16; PCT=100 ;;
  *) echo "usage: $0 stills|preview|final [shot ids]"; exit 1 ;;
esac
APP=$(ls -d /Applications/Blender*.app ~/Applications/Blender*.app 2>/dev/null | head -1)
[ -z "$APP" ] && APP=$(mdfind "kMDItemCFBundleIdentifier == 'org.blenderfoundation.blender'" | head -1)
B="$APP/Contents/MacOS/Blender"
if [ ! -x "$B" ]; then echo "Could not find Blender. Run: mdfind -name Blender.app   and send me the output."; exit 1; fi
echo "Using: $B ($MODE)"

# 1) export cameras + character drawings from the story code (only when the code changed)
[ -d node_modules ] || npm ci
if [ ! -f export/timeline.json ] || [ -n "$(find src scripts -newer export/timeline.json -name '*.ts' | head -1)" ]; then
  echo "== exporting shots"; npx tsx scripts/export_ww2.ts export all 1
fi

# 2) render every shot
FR=out/frames_$MODE; mkdir -p "$FR"
START=$(date +%s)
for J in export/shot*.json; do
  N=$(basename "$J" .json); ID=$((10#${N#shot}))
  if [ "$ONLY" != "all" ] && [[ ",$ONLY," != *",$ID,"* ]]; then continue; fi
  echo "== $N  ($(( ($(date +%s) - START) / 60 )) min so far)"
  WW2_ENGINE=$ENGINE "$B" -b --factory-startup -P blender/render_shot.py -- "$J" export/cards "$FR/$N" $SPP $PCT $STEP > "$FR/$N.log" 2>&1 \
    || { echo "   FAILED, see $FR/$N.log"; tail -5 "$FR/$N.log"; }
done

if [ "$MODE" = stills ]; then echo "Done in $(( ($(date +%s) - START) / 60 )) min: $(pwd)/$FR"; open "$FR"; exit 0; fi

# 3) crossfades, title cards, sound -> mp4
OUT=out/ww2_part1_$MODE.mp4
"$B" -b --factory-startup -P blender/assemble.py -- export "$FR" audio/mix_part1.wav "$OUT" > out/assemble_$MODE.log 2>&1 \
  || { echo "assemble failed, see out/assemble_$MODE.log"; tail -5 out/assemble_$MODE.log; exit 1; }
echo "Done in $(( ($(date +%s) - START) / 60 )) min: $(pwd)/$OUT"
open "$OUT"
