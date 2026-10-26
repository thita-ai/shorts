"""The slime, as the 2010 paper models it (Tero et al., Science 327:439): a mesh of tubes, two rules.

  1. Food flows through the tubes. Each city in turn pumps I0 in while every other city takes an equal share out
     (Kirchhoff: solve for the pressures, flux Q = D/L * dp); a tube feels its mean flux over all 36 turns.
  2. A tube that carries flux thickens, an idle one shrinks:  dD/dt = |Q|^g / (1 + |Q|^g) - D.

Before that, the mold spreads out from Tokyo over the whole map (a growth front along the mesh).
Saves every step's tube thickness for the renderer, then measures the final network against the minimum spanning
tree (the cheapest way to join the 36 cities over land) and against single-link failures.

  python3 slime.py  -> data/sim.json + data/D.npy
"""
import json, math, pathlib, sys
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.linalg import splu
from scipy.sparse.csgraph import dijkstra, minimum_spanning_tree, connected_components

ROOT = pathlib.Path(__file__).resolve().parent
I0, G, DT, STEPS, SEED = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0, \
    float(sys.argv[2]) if len(sys.argv) > 2 else 1.8, 0.15, 420, 2026
KEEP = 0.1                                   # a tube thinner than this is gone


def main():
    g = json.load(open(ROOT / "data/geo.json"))
    P = np.array(g["nodes"]); E = np.array(g["edges"]); n, m = len(P), len(E)
    C = np.arange(len(g["cities"]))           # the cities are the first nodes
    L = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1)
    A = csr_matrix((np.r_[np.ones(m), -np.ones(m)], (np.r_[np.arange(m), np.arange(m)], np.r_[E[:, 0], E[:, 1]])), (m, n))
    W = csr_matrix((L, (E[:, 0], E[:, 1])), (n, n)); W = W + W.T

    # growth: the front leaves Tokyo and reaches every node; arrival time = distance over land, a little noise
    rng = np.random.default_rng(SEED)
    dist = dijkstra(W, indices=0)
    arrive = dist * (1 + 0.25 * rng.standard_normal(n).clip(-2, 2) * 0.4)
    arrive /= arrive.max()

    D = 1.0 + 0.05 * rng.standard_normal(m)
    hist = [D.astype(np.float16)]
    for k in range(STEPS):
        b = np.zeros((n, len(C))); b[C, :] = -I0 / (len(C) - 1); b[C, np.arange(len(C))] = I0
        Lap = (A.T @ csr_matrix((D / L, (np.arange(m), np.arange(m))), (m, m)) @ A).tocsc()
        Lap = Lap[1:, 1:]                     # ground node 0 (Tokyo)
        p = np.vstack([np.zeros(len(C)), splu(Lap).solve(b[1:])])
        Q = np.abs((D / L)[:, None] * (p[E[:, 0]] - p[E[:, 1]])).mean(1)
        D = np.maximum(D + DT * (Q ** G / (1 + Q ** G) - D), 1e-6)
        hist.append(D.astype(np.float16))
        if k % 60 == 0:
            print(f"  step {k}: tubes kept {int((D > KEEP).sum())}", flush=True)

    # the final network: thick tubes, minus dead-end stubs that lead to no city
    keep = D > KEEP
    deg = np.bincount(E[keep].ravel(), minlength=n)
    while True:
        stub = keep & (((deg[E[:, 0]] == 1) & (E[:, 0] >= len(C))) | ((deg[E[:, 1]] == 1) & (E[:, 1] >= len(C))))
        if not stub.any():
            break
        keep &= ~stub
        deg = np.bincount(E[keep].ravel(), minlength=n)

    def joined(mask):
        Gm = coo_matrix((np.ones(mask.sum()), (E[mask, 0], E[mask, 1])), (n, n))
        _, lab = connected_components(Gm, directed=False)
        return len(set(lab[C])) == 1

    assert joined(keep), "the slime left a city out; change I0/G"
    TL = L[keep].sum()

    # MST: cheapest way to join the cities over land (city-to-city distances along the mesh)
    dc = dijkstra(W, indices=C)[:, C]
    mst = minimum_spanning_tree(csr_matrix(dc)).tocoo()
    TL_mst = mst.data.sum()
    # the MST's actual paths, for drawing
    _, pred = dijkstra(W, indices=C, return_predecessors=True)
    mst_paths = []
    for a, b in zip(mst.row, mst.col):
        path, v = [int(C[b])], int(C[b])
        while v != C[a]:
            v = int(pred[a, v]); path.append(v)
        mst_paths.append(path)

    # fault tolerance: cut one random piece of track (chance proportional to its length); how often is a city stranded?
    idx = np.nonzero(keep)[0]
    strand = 0.0
    bridge = []
    for i in idx:
        mk = keep.copy(); mk[i] = False
        if not joined(mk):
            strand += L[i]; bridge.append(int(i))
    FT = 1 - strand / TL
    # the cut we show: a piece of track both networks use, where cutting the MST strands the most cities
    # (the blob must survive it), and the detour the blob's food takes around the cut
    eid = {(int(a), int(b)): i for i, (a, b) in enumerate(E)}
    on_mst = np.zeros(m, bool)
    for path in mst_paths:
        for a, b in zip(path, path[1:]):
            on_mst[eid[(min(a, b), max(a, b))]] = True

    def stranded(mask):
        Gm = coo_matrix((np.ones(mask.sum()), (E[mask, 0], E[mask, 1])), (n, n))
        _, lab = connected_components(Gm, directed=False)
        return [int(c) for c in C if lab[c] != lab[0]]

    best = None
    for i in np.nonzero(on_mst & keep)[0]:
        if i in bridge:
            continue
        mk = on_mst.copy(); mk[i] = False
        s = stranded(mk)
        mid = (P[E[i, 0]] + P[E[i, 1]]) / 2
        score = len(s) - 0.02 * np.linalg.norm(mid)               # most cities lost, near the middle of the map
        if best is None or score > best[0]:
            best = (score, int(i), s)
    _, cut, lost = best
    Wb = csr_matrix((L[keep & (np.arange(m) != cut)], (E[keep & (np.arange(m) != cut), 0],
                     E[keep & (np.arange(m) != cut), 1])), (n, n))
    a0, b0 = map(int, E[cut])
    _, pr = dijkstra(Wb, directed=False, indices=a0, return_predecessors=True)
    detour, v = [b0], b0
    while v != a0:
        v = int(pr[v]); detour.append(v)
    print(f"cut edge {cut}: MST strands {len(lost)} cities ({', '.join(g['cities'][c]['name'] for c in lost)}); "
          f"blob detour {len(detour)} nodes")
    print(f"TL {TL:.1f} km, MST {TL_mst:.1f} km, ratio {TL / TL_mst:.2f}; blob survives a random cut {FT:.1%}")
    json.dump({"I0": I0, "gamma": G, "dt": DT, "steps": STEPS, "seed": SEED, "keep": KEEP,
               "arrive": np.round(arrive, 4).tolist(), "final": np.nonzero(keep)[0].tolist(),
               "bridges": bridge, "TL": round(TL, 1), "TL_mst": round(TL_mst, 1), "ratio": round(TL / TL_mst, 2),
               "FT": round(FT, 4), "mst_paths": mst_paths, "on_mst": np.nonzero(on_mst)[0].tolist(),
               "cut": cut, "lost": lost, "detour": detour}, open(ROOT / "data/sim.json", "w"))
    np.save(ROOT / "data/D.npy", np.array(hist))


if __name__ == "__main__":
    main()
