"""Space-time diagram of the ring road: one line per car, coloured by speed.
The dark bands leaning backwards are the jam wave; after the calm driver joins (dashed line) they fade out.

  python3 traffic.py && python3 plot.py   -> spacetime.png
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

d = json.load(open("sim.json"))
X, V = np.array(d["swap"]["x"]), np.array(d["swap"]["v"]) * 2.23694
t = np.arange(len(X)) * d["dt"]
segs, cols = [], []
for c in range(X.shape[1]):
    for i in range(len(t) - 1):
        if X[i + 1, c] >= X[i, c]:               # skip the jump where a car wraps past 0 m
            segs.append([(t[i], X[i, c]), (t[i + 1], X[i + 1, c])]); cols.append(V[i, c])
fig, ax = plt.subplots(figsize=(12, 5), facecolor="black")
ax.set_facecolor("black")
lc = LineCollection(segs, array=np.array(cols), cmap="inferno", norm=plt.Normalize(0, 16), linewidths=1.2)
ax.add_collection(lc)
ax.set_xlim(0, t[-1]); ax.set_ylim(0, d["ring"])
ax.axvline(d["swap_at"], color="cyan", ls="--", lw=1)
ax.text(d["swap_at"] + 2, d["ring"] * 0.94, "one calm driver", color="cyan")
ax.set_xlabel("time (s)", color="white"); ax.set_ylabel("position on the ring (m)", color="white")
ax.tick_params(colors="white")
cb = fig.colorbar(lc, ax=ax); cb.set_label("speed (mph)", color="white"); cb.ax.tick_params(colors="white")
ax.set_title("22 human drivers, one brake tap at 8 s, one calm driver from 70 s", color="white")
fig.tight_layout(); fig.savefig("spacetime.png", dpi=130)
print("wrote spacetime.png")
