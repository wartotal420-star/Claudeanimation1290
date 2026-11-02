# Chapter 11/14 maps from make_map2.render: a 1944 Europe table map (Channel to Belarus) with cities, plus labels sized
# for the close-up. Writes maps/c11_europe.png.   python3 maps/c11_make_maps.py  (from blender/)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import make_map2 as MM
from PIL import Image, ImageDraw, ImageFont
LON0, LON1, LAT0, LAT1 = -9.0, 33.0, 59.0, 43.5
W, H = 4096, 2410
MM.LABELS[:] = [("GERMANY", 10.6, 51.2, 0.28, 0.2), ("POLAND", 19.4, 51.6, 0.22, 0.2), ("FRANCE", 2.6, 47.0, 0.28, 0.2), ("BRITAIN", -1.8, 53.2, 0.18, 0.1),
    ("BELGIUM", 4.6, 50.6, 0.08, 0.0), ("HOLLAND", 5.6, 52.6, 0.09, 0.0), ("SWITZ.", 8.2, 46.85, 0.07, 0.0), ("AUSTRIA", 14.2, 47.6, 0.12, 0.1),
    ("HUNGARY", 19.4, 47.1, 0.12, 0.1), ("CZECHOSLOVAKIA", 16.6, 49.4, 0.1, 0.0), ("DENMARK", 9.3, 56.2, 0.09, 0.0), ("SWEDEN", 15.0, 57.5, 0.16, 0.2),
    ("U.S.S.R.", 29.5, 55.8, 0.3, 0.4), ("ROMANIA", 25.0, 45.9, 0.14, 0.1), ("LITHUANIA", 23.8, 55.3, 0.08, 0.0), ("LATVIA", 25.2, 56.9, 0.08, 0.0),
    ("IRELAND", -7.9, 53.2, 0.1, 0.0), ("NORWAY", 8.5, 58.6, 0.12, 0.0), ("ITALY", 10.5, 44.6, 0.12, 0.0), ("YUGOSLAVIA", 18.2, 44.4, 0.12, 0.0)]
MM.SEAS[:] = [("NORTH SEA", 3.0, 55.6, 0.24), ("BALTIC SEA", 17.6, 55.6, 0.2), ("ENGLISH CHANNEL", -3.2, 49.85, 0.14), ("BAY OF BISCAY", -6.3, 46.0, 0.16), ("ATLANTIC", -7.6, 50.8, 0.16)]
# 1944: East Prussia (today's Kaliningrad) is German, not Soviet
for f in MM.GEO["features"]:
    if f["properties"]["ADM0_A3"] == "RUS" and f["geometry"]["type"] == "MultiPolygon":
        keep, ep = [], []
        for poly in f["geometry"]["coordinates"]:
            ring = poly[0]; mlon = sum(p[0] for p in ring) / len(ring); mlat = sum(p[1] for p in ring) / len(ring)
            (ep if 19 < mlon < 23 and 54 < mlat < 56 else keep).append(poly)
        if ep:
            f["geometry"]["coordinates"] = keep
            MM.GEO["features"].append({"type": "Feature", "properties": {"ADM0_A3": "DEU", "MAPCOLOR7": 1}, "geometry": {"type": "MultiPolygon", "coordinates": ep}})
MM.render("c11_europe.png", W, H, LON0, LON1, LAT0, LAT1, rose=(-7.2, 57.6), cart=(28.0, 44.7, "EUROPE 1944", "Supreme Headquarters"), scale=0.62, seed=11)
im = Image.open(os.path.join(HERE, "c11_europe.png")).convert("RGB"); d = ImageDraw.Draw(im)
sx, sy = W / (LON1 - LON0), H / (LAT0 - LAT1)
P = lambda lon, lat: ((lon - LON0) * sx, (LAT0 - lat) * sy)
F = ImageFont.truetype(MM.F_BOLD, 34); FS = ImageFont.truetype(MM.F_BOLD, 28)
CITIES = [("LONDON", -0.13, 51.5, 1, 0), ("PARIS", 2.35, 48.86, 1, 0), ("BERLIN", 13.4, 52.52, 1, 0), ("WARSAW", 21.0, 52.23, 1, 0), ("CALAIS", 1.86, 50.95, 1, 1),
          ("MINSK", 27.56, 53.9, 1, 0), ("ARNHEM", 5.9, 51.98, 1, 1), ("BASTOGNE", 5.72, 50.0, 1, 1), ("BRUSSELS", 4.35, 50.85, 1, 0), ("AMSTERDAM", 4.9, 52.37, 1, 0),
          ("CAEN", -0.37, 49.18, 1, 1), ("VITEBSK", 30.2, 55.19, 1, 0), ("BOBRUISK", 29.2, 53.14, 1, 0), ("NUREMBERG", 11.08, 49.45, 1, 0), ("DOVER", 1.31, 51.13, 1, 0),
          ("RASTENBURG", 21.43, 54.08, 1, 0), ("VIENNA", 16.37, 48.21, 1, 0), ("PRAGUE", 14.42, 50.08, 1, 0), ("COPENHAGEN", 12.57, 55.68, 1, 0), ("MUNICH", 11.58, 48.14, 1, 0)]
for name, lon, lat, _, big in CITIES:
    x, y = P(lon, lat); r = 11
    d.ellipse([x - r, y - r, x + r, y + r], fill=(160, 30, 30), outline=(40, 20, 10), width=4)
    f = F if big else FS
    d.text((x + 16, y - 4), name, font=f, fill=(40, 22, 14), anchor="lm", stroke_width=5, stroke_fill=(236, 222, 186))
x, y = P(-0.6, 49.38); d.text((x - 10, y + 62), "NORMANDY", font=ImageFont.truetype(MM.F_BOLD, 40), fill=(90, 30, 20), anchor="mm", stroke_width=5, stroke_fill=(236, 222, 186))
x, y = P(5.5, 50.15); d.text((x + 120, y + 70), "ARDENNES", font=ImageFont.truetype(MM.F_IT, 38), fill=(40, 70, 40), anchor="mm", stroke_width=4, stroke_fill=(236, 222, 186))
im.save(os.path.join(HERE, "c11_europe.png"), optimize=True); print("ok", im.size)
# the Channel coast crop for the bunker wall map (lon -5..9, lat 47..53.5)
cx0, cx1 = int((-5 - LON0) * sx), int((9 - LON0) * sx); cy0, cy1 = int((LAT0 - 53.5) * sy), int((LAT0 - 47) * sy)
im.crop((cx0, cy0, cx1, cy1)).resize((1400, 860)).save(os.path.join(HERE, "c11_channel.png")); print("channel ok")
