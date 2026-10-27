#!/bin/zsh
# Reset to lesson-43, copy the prototype assets in, run the prototype step script.
cd /Users/brian/Developer/Godot/StylizedGameTemplateCourse
export TEMP=/tmp
python3 tools/verification/scripts/sgt.py reset lesson-43 > /dev/null
cp /tmp/protow/*.gdshader /tmp/sgt-phase1/workbench/art/shaders/
mkdir -p /tmp/sgt-phase1/workbench/art/water
[ -f /tmp/protow/bank_kit.glb ] && cp /tmp/protow/bank_kit.glb /tmp/sgt-phase1/workbench/art/water/
python3 tools/verification/scripts/sgt.py godot proto_water > /tmp/protow.out 2>&1
echo finished >> /tmp/protow.out
