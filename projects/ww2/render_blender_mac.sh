#!/bin/bash
# The ENTIRE History of WW2 in Blender, one command on the Mac:
#   ./render_blender_mac.sh stills [part]        one frame every 1.5 s in final quality -> Finder (quick look check)
#   ./render_blender_mac.sh preview [part]       EEVEE, half size, with sound -> mp4
#   ./render_blender_mac.sh final [part]         Cycles 16 spp + denoise, 1920x1080, with sound -> mp4
# part = part1 (cold open + chapter 1, the default) | ch02 ... ch14 | all (every part, then joined into one video)
# A third argument limits a run to some shots: ./render_blender_mac.sh preview ch05 3,4
# Re-running continues where it stopped (finished frames are skipped).
set -e
cd "$(dirname "$0")"
MODE=${1:-preview}; WHAT=${2:-part1}; ONLY=${3:-all}
STEP=1
case "$MODE" in
  stills)  ENGINE=cycles; SPP=16; PCT=100; STEP=45 ;;
  preview) ENGINE=eevee;  SPP=16; PCT=50 ;;
  final)   ENGINE=cycles; SPP=16; PCT=100 ;;
  *) echo "usage: $0 stills|preview|final [part1|ch02..ch14|all] [shot ids]"; exit 1 ;;
esac
PCT=${WW2_PCT:-$PCT}; SPP=${WW2_SPP:-$SPP}         # test overrides
APP=$(ls -d /Applications/Blender*.app ~/Applications/Blender*.app 2>/dev/null | head -1)
[ -z "$APP" ] && APP=$(mdfind "kMDItemCFBundleIdentifier == 'org.blenderfoundation.blender'" | head -1)
B="$APP/Contents/MacOS/Blender"
if [ ! -x "$B" ]; then echo "Could not find Blender. Run: mdfind -name Blender.app   and send me the output."; exit 1; fi
echo "Using: $B ($MODE)"
[ -d node_modules ] || npm ci
START=$(date +%s)

render_part() {   # $1 = part1 | chNN
  local P=$1 EXP=export/$1 FR=out/$1/frames_$MODE
  # 1) export cameras + character drawings (only when the story code changed)
  if [ ! -f "$EXP/timeline.json" ] || [ -n "$(find src scripts -newer "$EXP/timeline.json" -name '*.ts' | head -1)" ]; then
    echo "== $P: exporting shots"
    if [ "$P" = part1 ]; then npx tsx scripts/export_ww2.ts "$EXP" all 1; else PART=$P npx tsx scripts/export_ww2.ts "$EXP" all 1; fi
  fi
  # 2) render every shot
  mkdir -p "$FR"
  for J in "$EXP"/shot*.json; do
    N=$(basename "$J" .json); ID=$((10#${N#shot}))
    if [ "$ONLY" != "all" ] && [[ ",$ONLY," != *",$ID,"* ]]; then continue; fi
    echo "== $P $N  ($(( ($(date +%s) - START) / 60 )) min so far)"
    WW2_ENGINE=$ENGINE "$B" -b --factory-startup -P blender/render_shot.py -- "$J" "$EXP/cards" "$FR/$N" $SPP $PCT $STEP > "$FR/$N.log" 2>&1 \
      || { echo "   FAILED, see $FR/$N.log"; tail -5 "$FR/$N.log"; }
  done
  [ "$MODE" = stills ] && return 0
  # 3) crossfades, title cards, sound -> mp4
  local MIX=audio/mix_$P.m4a; [ "$P" = part1 ] && MIX=audio/mix_part1.wav
  "$B" -b --factory-startup -P blender/assemble.py -- "$EXP" "$FR" "$MIX" "out/${P}_$MODE.mp4" > "out/$P/assemble_$MODE.log" 2>&1 \
    || { echo "assemble failed, see out/$P/assemble_$MODE.log"; tail -5 "out/$P/assemble_$MODE.log"; exit 1; }
  echo "   -> $(pwd)/out/${P}_$MODE.mp4"
}

if [ "$WHAT" = all ]; then PARTS="part1 $(ls src/videos/ww2/ch/ch*.ts 2>/dev/null | xargs -n1 basename | sed 's/\.ts$//' | sort | tr '\n' ' ')"; else PARTS=$WHAT; fi
for P in $PARTS; do render_part "$P"; done

if [ "$MODE" = stills ]; then echo "Done in $(( ($(date +%s) - START) / 60 )) min"; open out; exit 0; fi
if [ "$WHAT" = all ]; then
  : > out/parts_$MODE.txt
  for P in $PARTS; do echo "file '$(pwd)/out/${P}_$MODE.mp4'" >> out/parts_$MODE.txt; done
  npx remotion ffmpeg -y -v error -f concat -safe 0 -i out/parts_$MODE.txt -c copy "out/WW2_full_$MODE.mp4"
  OUT=out/WW2_full_$MODE.mp4
else OUT=out/${WHAT}_$MODE.mp4; fi
echo "Done in $(( ($(date +%s) - START) / 60 )) min: $(pwd)/$OUT"
open "$OUT"
