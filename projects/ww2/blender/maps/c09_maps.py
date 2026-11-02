# Europe / North Africa / western USSR map for the c09_map table (chapters 9 and 12): make_map2's painted style with a
# regional label set and city dots. Region lon -14..58, lat 63..24 (equirectangular, 6144 x 3328 px).
#   python3 maps/c09_maps.py   (run from blender/; writes maps/c09_europe.png)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_map2 as M
from PIL import Image, ImageDraw, ImageFont

LON0, LON1, LAT0, LAT1 = -14, 58, 63, 24
W, H = 6144, 3328
M.LABELS = [
    ("GERMANY", 10.5, 51.0, 0.62, 0.1), ("FRANCE", 2.4, 46.8, 0.66, 0.1), ("BRITAIN", -1.8, 53.2, 0.46, 0.0), ("ITALY", 12.6, 43.2, 0.46, 0.0),
    ("SPAIN", -4.2, 38.9, 0.66, 0.1), ("POLAND", 19.0, 51.0, 0.52, 0.1), ("SOVIET UNION", 44, 57.5, 1.1, 0.35), ("TURKEY", 34, 39.0, 0.62, 0.1),
    ("EGYPT", 29.5, 26.5, 0.6, 0.0), ("LIBYA", 17.5, 28.0, 0.7, 0.1), ("ALGERIA", 2.5, 29.5, 0.7, 0.1), ("MOROCCO", -6.8, 31.2, 0.5, 0.0),
    ("TUNISIA", 9.4, 33.6, 0.32, 0.0), ("ROMANIA", 25.0, 45.9, 0.4, 0.0), ("HUNGARY", 19.3, 47.1, 0.32, 0.0), ("SWEDEN", 15.0, 61.0, 0.42, 0.0),
    ("YUGOSLAVIA", 19.5, 44.2, 0.32, 0.0), ("GREECE", 22.0, 39.6, 0.32, 0.0), ("BULGARIA", 25.3, 42.7, 0.28, 0.0), ("PORTUGAL", -8.2, 39.6, 0.24, 0.0),
    ("IRELAND", -8.0, 53.2, 0.24, 0.0), ("SYRIA", 38.6, 35.2, 0.36, 0.0), ("IRAQ", 43.5, 33.0, 0.4, 0.0), ("PERSIA", 54.0, 32.0, 0.46, 0.0),
    ("ARABIA", 41.0, 28.6, 0.5, 0.2), ("FINLAND", 26.5, 62.0, 0.4, 0.0), ("NORWAY", 9.0, 61.0, 0.36, 0.0), ("UKRAINE", 32.0, 49.3, 0.42, 0.2),
]
M.SEAS = [("ATLANTIC OCEAN", -10.5, 45, 0.62), ("MEDITERRANEAN SEA", 17.5, 34.6, 0.62), ("NORTH SEA", 3.5, 56.2, 0.44), ("BLACK SEA", 34.5, 43.3, 0.5),
          ("CASPIAN SEA", 50.8, 42.2, 0.36), ("BALTIC", 19.4, 57.2, 0.36), ("RED SEA", 37.0, 23.5, 0.3)]
CITIES = [("Berlin", 13.4, 52.5), ("London", -0.1, 51.5), ("Paris", 2.35, 48.86), ("Rome", 12.5, 41.9), ("Moscow", 37.6, 55.75), ("Leningrad", 30.3, 59.94),
          ("Stalingrad", 44.5, 48.7), ("Kiev", 30.5, 50.45), ("Warsaw", 21.0, 52.23), ("Vienna", 16.37, 48.2), ("Cairo", 31.24, 30.04), ("Algiers", 3.06, 36.75),
          ("Casablanca", -7.6, 33.57), ("Tunis", 10.18, 36.8), ("Madrid", -3.7, 40.42), ("Kursk", 36.19, 51.73), ("Sevastopol", 33.52, 44.6), ("Athens", 23.73, 37.98),
          ("Istanbul", 28.98, 41.01), ("Budapest", 19.04, 47.5), ("Bucharest", 26.1, 44.43), ("Oslo", 10.75, 59.91), ("Stockholm", 18.07, 59.33)]
if __name__ == "__main__":
    out = os.path.join(M.HERE, "c09_europe.png")
    M.render("c09_europe.png", W, H, LON0, LON1, LAT0, LAT1, rose=(-10, 58.5), cart=(52, 27.5, "EUROPE & THE EAST", "Operations Map  1942"), scale=0.5, seed=9)
    im = Image.open(out); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(M.F_BOLD, 54)
    sx, sy = W / (LON1 - LON0), H / (LAT0 - LAT1)
    for name, lo, la in CITIES:
        x, y = (lo - LON0) * sx, (LAT0 - la) * sy
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(40, 22, 16)); d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(240, 226, 190))
        d.text((x + 22, y - 4), name, font=f, anchor="lm", fill=(40, 22, 16), stroke_width=4, stroke_fill=(246, 232, 200))
    im.save(out, optimize=True); print("cities added")
