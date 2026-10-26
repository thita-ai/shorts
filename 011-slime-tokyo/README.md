# 011: This Blob Designed Tokyo's Train Network

In 2010, scientists at Hokkaido University put a slime mold (*Physarum polycephalum*) on a map of the Tokyo area, with oat flakes on 36 cities, and let it grow out of Tokyo. In about a day it built a network with cost, efficiency and fault tolerance comparable to the real rail network (Tero et al., *Science* 327:439, 2010).

This code runs the paper's own model of the slime on real OpenStreetMap geography. The mold is a mesh of tubes, and it follows two rules:

1. Food flows through the tubes. Each city in turn pumps food in while the others take it out (Kirchhoff's laws give the flow in every tube).
2. A tube that carries flow gets thicker and an idle one shrinks: `dD/dt = |Q|^γ / (1 + |Q|^γ) − D`.

## Results (I0 = 15, γ = 1.8, 420 steps, seed 2026)

| | Track | Survives a random single cut |
|---|---|---|
| The blob's network | 672 km | 86% |
| Minimum spanning tree (cheapest network joining the 36 cities over land) | 404 km (40% less) | 0% |

Cutting one MST link near Tokyo cuts 23 of the 36 cities off from Tokyo. The blob's network reroutes around the same cut.

The blob comes out at 1.66× the MST's length. In the paper, the real Tokyo rail network is about 1.8× and the slime's networks average 1.75×.

## Run it

```bash
pip install -r requirements.txt
./fetch.sh               # OpenStreetMap rail + coastline -> data/osm.json
python3 geo.py           # land mask, 36 cities snapped onto the rail lines, the mesh -> data/geo.json
python3 slime.py 15 1.8  # the slime -> data/sim.json, data/D.npy
```

Try other values of I0 and γ: a low I0 gives a cheap tree-like network that strands cities when cut, a high one gives a dense, expensive one that never breaks. That trade-off is the whole point.
