#!/bin/bash
# Render the Kiska short on a Mac (GPU). Needs Node 20+ (ffmpeg comes with Remotion)
set -e
cd "$(dirname "$0")"
mkdir -p src/videos/bridge out
cp ../../templates/bridge/* src/videos/bridge/
cat > src/Root.tsx <<'TSX'
import React from "react";
import { Composition } from "remotion";
import { KiskaShort, KISKA_FRAMES } from "./videos/kiska/Kiska";
export const Root: React.FC = () => <Composition id="KiskaShort" component={KiskaShort} durationInFrames={KISKA_FRAMES} fps={30} width={1080} height={1920} />;
TSX
npm ci
time npx remotion render src/index.ts KiskaShort out/kiska_video.mp4 --codec h264 --crf 16 --gl=angle --concurrency=4 "$@"
npx remotion ffmpeg -y -i out/kiska_video.mp4 -i audio/mix.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -shortest out/kiska_final.mp4
echo "Done: $(pwd)/out/kiska_final.mp4"
