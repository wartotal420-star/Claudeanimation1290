#!/bin/bash
# Blender speed test on the Mac: renders the bakery frame with Cycles (GPU) and with EEVEE at full 1920x1080.
cd "$(dirname "$0")"
B=/Applications/Blender.app/Contents/MacOS/Blender
$B --version | head -1
echo "== Cycles 64 samples"; /usr/bin/time -p $B -b --factory-startup -P bakery.py -- "$PWD/cards" "$PWD/test_cycles.png" 64 100 CYCLES 2>&1 | grep -E "^real|rendered|Error"
echo "== EEVEE";             /usr/bin/time -p $B -b --factory-startup -P bakery.py -- "$PWD/cards" "$PWD/test_eevee.png" 64 100 EEVEE 2>&1 | grep -E "^real|rendered|Error"
open test_cycles.png test_eevee.png
