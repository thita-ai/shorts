import numpy as np
P = np.random.rand(500, 2) * 720  # 500 birds
V = np.random.randn(500, 2)
for step in range(1500):
    R = (P - P[:, None] + 360) % 720 - 360
    near = (R**2).sum(-1).argsort(1)[:, 1:8]
    r = R[np.c_[:500], near]  # its 7 closest
    close = (r**2).sum(-1)[..., None] < 144
    V += 0.0035 * r.mean(1)  # stay near
    V -= 0.05 * (r * close).sum(1)  # don't bump
    V += 0.06 * (V[near].mean(1) - V)  # fly along
    V *= 2.5 / np.linalg.norm(V, axis=1)[:, None]
    P = (P + V) % 720
