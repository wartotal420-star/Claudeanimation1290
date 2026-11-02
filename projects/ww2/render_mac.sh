#!/bin/bash
# Render WW2 part 1 (cold open + chapter 1) on a Mac. Needs Node 20+ (ffmpeg comes with Remotion).
set -e
cd "$(dirname "$0")"
mkdir -p out
cat > src/Root.tsx <<'TSX'
import React from "react";
import { Composition } from "remotion";
import { WW2Long, WW2_FRAMES } from "./videos/ww2/WW2";
export const Root: React.FC = () => <Composition id="WW2Long" component={WW2Long} durationInFrames={WW2_FRAMES} fps={30} width={1920} height={1080} />;
TSX
[ -d node_modules ] || npm ci
time npx remotion render src/index.ts WW2Long out/ww2_part1_video.mp4 --codec h264 --crf 16 --gl=angle --concurrency=4 "$@"
npx remotion ffmpeg -y -i out/ww2_part1_video.mp4 -i audio/mix_part1.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -shortest out/ww2_part1.mp4
echo "Done: $(pwd)/out/ww2_part1.mp4"
