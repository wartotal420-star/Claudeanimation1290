import sys, os, glob
from PIL import Image, ImageDraw
a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
fs = []
for i in range(a, b + 1): fs += sorted(glob.glob(f"/home/user/ww2/sweep/shot{i:02d}/*.png"))
W, H, C = 480, 270, 4
R = (len(fs) + C - 1) // C
c = Image.new("RGB", (W * C, H * R), (40, 40, 40)); d = ImageDraw.Draw(c)
for k, f in enumerate(fs):
    im = Image.open(f).convert("RGB").resize((W, H)); x, y = (k % C) * W, (k // C) * H
    c.paste(im, (x, y)); d.text((x + 6, y + 4), f.split("/")[-2] + " " + os.path.basename(f)[:-4], fill=(255, 255, 0))
c.save(out); print(len(fs))
