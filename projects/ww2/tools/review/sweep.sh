#!/bin/bash
# usage: sweep.sh <first> <last>   -> /home/user/ww2/sweep/shotNN/*.png (one frame per 45, 30%, 12 spp)
cd /home/user/ww2/blender
for i in $(seq $1 $2); do
  N=$(printf "shot%02d" $i); J=/home/user/ww2/export/$N.json; M=/home/user/ww2/sweep/$N.json
  python3 -c "
import json; d=json.load(open('$J')); fr=d['frames']; keep=[x for x in fr if (x['f']-d['a'])%45==20 and d['a']<=x['f']<d['b']] or [fr[len(fr)//2]]
d['frames']=keep; json.dump(d,open('$M','w'))"
  python3 render_shot.py -- $M /home/user/ww2/export/cards /home/user/ww2/sweep/$N 12 30 > /home/user/ww2/sweep/$N.log 2>&1 || echo "FAIL $N"
  echo "done $N $(ls /home/user/ww2/sweep/$N | wc -l)"
done
