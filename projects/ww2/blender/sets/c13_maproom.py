# Island hopping (chapter 13 opening): the c07_maproom Pacific map room (layout and mx/mz in c07_maproom.py), 1944.
# Japanese pin flags on the bypassed strongholds stay; the hopped islands get US flags as the hop reaches them (frames
# below); the stick marine who hops across the map is a cast card (ch13.ts HOPS uses the same island list and frames).
from sets import c07_maproom as MR

# island, lon, lat, frame the US flag pops (chapter 13 local)
HOPS = [("GUADALCANAL", 160.0, -9.6, 70), ("TARAWA", 172.9, 1.4, 110), ("SAIPAN", 145.7, 15.2, 150), ("GUAM", 144.8, 13.4, 185), ("LEYTE", 125.0, 11.0, 222),
        ("IWO JIMA", 141.3, 24.8, 300), ("OKINAWA", 127.9, 26.5, 360)]
BYPASSED = [(152.2, -4.2), (151.8, 7.4), (134.5, 7.3), (171.2, 7.1), (147.0, -2.0), (128.5, 2.0)]   # Rabaul, Truk, Palau, Kwajalein, Kavieng, Halmahera
JAPAN_HELD = [(121.5, 31.2), (116.4, 39.9), (125.5, 44.0), (113.3, 23.1), (103.8, 1.35), (110.0, -7.3), (114.0, 0.5), (101.5, -0.5), (121.0, 14.6), (114.2, 22.3), (96.5, 20.0), (104.0, 15.0)]
CFG13 = dict(china=JAPAN_HELD + BYPASSED, tanks=[], fleet=[], conquest=[], barrels=[], pipeline=False,
             usflags=[(lo, la, f) for _, lo, la, f in HOPS])
def build(M, D): return MR.build_room(M, D, CFG13)
