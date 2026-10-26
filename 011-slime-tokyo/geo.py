"""Real Greater Tokyo geography from OpenStreetMap (data/osm.json, Overpass: main-line rail + coastline).

36 cities (the paper's template size), each snapped onto the nearest real rail line. Land mask from the coastline,
then a random land mesh for the slime to live on (a Delaunay triangulation that never crosses the sea).

  python3 geo.py  -> data/geo.json
"""
import json, math, pathlib
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import Delaunay, cKDTree

ROOT = pathlib.Path(__file__).resolve().parent
LAT0, LON0 = 35.62, 139.76
KX, KY = math.cos(math.radians(LAT0)) * 111.32, 110.57
BOX = (-48.0, -46.0, 52.0, 42.0)          # km: x0, y0 (north), x1, y1 (south); y grows south like the screen
RES = 0.1                                 # km per land-mask pixel

CITIES = [  # name, lat, lon (approx station; snapped to the nearest rail line below)
    ("Tokyo", 35.6812, 139.7671), ("Shinjuku", 35.6900, 139.7004), ("Ikebukuro", 35.7295, 139.7109),
    ("Shinagawa", 35.6285, 139.7387), ("Kawasaki", 35.5313, 139.6969), ("Yokohama", 35.4657, 139.6223),
    ("Mizonokuchi", 35.5999, 139.6107), ("Kichijoji", 35.7031, 139.5798), ("Fuchu", 35.6721, 139.4799),
    ("Tachikawa", 35.6980, 139.4137), ("Hachioji", 35.6558, 139.3389), ("Ome", 35.7906, 139.2584),
    ("Hanno", 35.8514, 139.3183), ("Tokorozawa", 35.7868, 139.4730), ("Kawagoe", 35.9070, 139.4826),
    ("Omiya", 35.9064, 139.6239), ("Ageo", 35.9772, 139.5933), ("Akabane", 35.7781, 139.7210),
    ("Kasukabe", 35.9800, 139.7525), ("Koshigaya", 35.8759, 139.7905), ("Kita-Senju", 35.7497, 139.8049),
    ("Matsudo", 35.7843, 139.9008), ("Kashiwa", 35.8622, 139.9709), ("Moriya", 35.9510, 140.0005),
    ("Ichikawa", 35.7290, 139.9087), ("Funabashi", 35.7017, 139.9853), ("Chiba", 35.6130, 140.1134),
    ("Goi", 35.5125, 140.0868), ("Kisarazu", 35.3812, 139.9264), ("Sakura", 35.7232, 140.2243),
    ("Narita", 35.7761, 140.3182), ("Machida", 35.5422, 139.4455), ("Hon-Atsugi", 35.4393, 139.3638),
    ("Fujisawa", 35.3389, 139.4875), ("Hiratsuka", 35.3279, 139.3505), ("Yokosuka", 35.2839, 139.6623),
]


def xy(lat, lon):
    return ((lon - LON0) * KX, (LAT0 - lat) * KY)


def main():
    els = json.load(open(ROOT / "data/osm.json"))["elements"]
    rails, coast = [], []
    for e in els:
        g = [xy(p["lat"], p["lon"]) for p in e.get("geometry", [])]
        if e["tags"].get("natural") == "coastline":
            coast.append(g)
        else:                                                       # every main line, JR and private: the real network
            rails.append(g)

    # land mask: draw the coastline, flood the sea from a few points known to be water
    w, h = int((BOX[2] - BOX[0]) / RES), int((BOX[3] - BOX[1]) / RES)
    px = lambda p: ((p[0] - BOX[0]) / RES, (p[1] - BOX[1]) / RES)
    im = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(im)
    for g in coast:
        d.line([px(p) for p in g], fill=0, width=3)
    for lat, lon in [(35.50, 139.85), (35.30, 139.80), (35.28, 139.40)]:   # Tokyo Bay, Uraga, Sagami Bay
        ImageDraw.floodfill(im, tuple(int(v) for v in px(xy(lat, lon))), 100)
    land = np.array(im) != 100
    print("land share", round(land.mean(), 3))

    def on_land(p):
        i, j = int((p[1] - BOX[1]) / RES), int((p[0] - BOX[0]) / RES)
        return 0 <= i < h and 0 <= j < w and land[i, j]

    # cities, snapped onto the real lines
    rp = np.array([p for g in rails for p in g])
    tree = cKDTree(rp)
    cities = []
    for name, lat, lon in CITIES:
        p = xy(lat, lon)
        dd, k = tree.query(p)
        if dd > 1.5:
            print("  far from rail:", name, round(dd, 2))
        cities.append({"name": name, "p": [round(v, 3) for v in (rp[k] if dd < 1.5 else p)]})

    # the slime's world: blue-noise points on land + the cities, triangulated, sea-crossing edges dropped
    rng = np.random.default_rng(2026)
    pts = [tuple(c["p"]) for c in cities]
    kd = cKDTree(pts)
    MIN = 1.55
    for _ in range(60000):
        q = (rng.uniform(BOX[0], BOX[2]), rng.uniform(BOX[1], BOX[3]))
        if on_land(q) and not kd.query_ball_point(q, MIN):
            pts.append(q)
            if len(pts) % 200 == 0:
                kd = cKDTree(pts)
            elif min(math.dist(q, r) for r in pts[-200:-1]) < MIN:
                pts.pop()
    P = np.array(pts)
    tri = Delaunay(P)
    edges = set()
    for s in tri.simplices:
        for a, b in ((s[0], s[1]), (s[1], s[2]), (s[0], s[2])):
            a, b = min(a, b), max(a, b)
            L = math.dist(P[a], P[b])
            if L > 4.0:
                continue
            if all(on_land(P[a] + (P[b] - P[a]) * k) for k in np.linspace(0.1, 0.9, 9)):
                edges.add((int(a), int(b)))
    # keep only the land the mold can reach from Tokyo (drops islands and stray points)
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    ea = np.array(sorted(edges))
    _, lab = connected_components(coo_matrix((np.ones(len(ea)), (ea[:, 0], ea[:, 1])), (len(P), len(P))), directed=False)
    ok = lab == lab[0]
    assert ok[:len(cities)].all(), [c["name"] for c, o in zip(cities, ok) if not o]
    new = -np.ones(len(P), int); new[ok] = np.arange(ok.sum())
    P = P[ok]
    edges = {(int(new[a]), int(new[b])) for a, b in edges if ok[a]}
    print(len(P), "nodes", len(edges), "edges")
    json.dump({"box": BOX, "cities": cities, "nodes": np.round(P, 3).tolist(), "edges": sorted(edges),
               "rails": [[[round(x, 2), round(y, 2)] for x, y in g] for g in rails],
               "coast": [[[round(x, 2), round(y, 2)] for x, y in g] for g in coast]},
              open(ROOT / "data/geo.json", "w"))
    Image.fromarray((land * 255).astype(np.uint8)).save(ROOT / "data/land.png")


if __name__ == "__main__":
    main()
