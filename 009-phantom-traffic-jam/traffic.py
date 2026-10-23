"""Phantom traffic jam on a ring road (after Sugiyama et al. 2008: 22 cars on a circle, no bottleneck; 300 m ring here).
Drivers follow the Intelligent Driver Model with a little human noise. Writes sim.json.

  python3 traffic.py
"""
import json, math
import numpy as np

N, RING, DT, SECS = 22, 300.0, 0.05, 240.0
SWAP = 70.0
BIAS = 0.3                              # m/s the calm driver may creep above its average when the gap allows
CAR = 4.5
MPH = 2.23694


def idm(v, gap, dv, v0=15.0, T=1.0, a=0.8, b=1.5, s0=2.0):
    s_star = s0 + np.maximum(0.0, v * T + v * dv / (2 * math.sqrt(a * b)))
    return a * (1 - (v / v0) ** 4 - (s_star / np.maximum(gap, 0.1)) ** 2)


def run(swap_at=None, seed=7, tap_at=8.0):
    """Human drivers; from swap_at on, car 11 becomes the calm driver."""
    rng = np.random.default_rng(seed)
    x = np.arange(N) * RING / N
    v = np.full(N, 7.0)
    hist_x, hist_v = [], []
    avg = 7.0
    for k in range(int(SECS / DT)):
        t = k * DT
        lead = (np.arange(N) + 1) % N
        gap = (x[lead] - x) % RING - CAR
        dv = v - v[lead]
        acc = idm(v, gap, dv) + rng.normal(0, 0.25, N)    # human: never perfectly smooth
        if tap_at <= t < tap_at + 2.0:
            acc[0] = -5.0                                       # one driver taps the brakes
        i = N // 2
        avg += (v[i] - avg) * DT / 30.0                         # car 11's running average speed
        if swap_at is not None and t >= swap_at:                # calm driver: hold the average, keep the gap
            target = min(avg + BIAS, max(0.0, (gap[i] - 4.0) / 1.6))
            acc[i] = np.clip((target - v[i]) * 0.6, -3.0, 1.0)
        v = np.maximum(0.0, v + acc * DT)
        x = (x + v * DT) % RING
        if k % 2 == 0:
            hist_x.append(x.round(2).tolist()); hist_v.append(v.round(2).tolist())
    return {"x": hist_x, "v": hist_v}


def stats(r, t0, t1, dt):
    V = np.array(r["v"])[int(t0 / dt):int(t1 / dt)]
    return {"avg_mph": float(V.mean() * MPH), "stopped_share": float((V < 0.5).mean()),
            "stops_per_car_min": float(((V[1:] < 0.5) & (V[:-1] >= 0.5)).sum() / N / ((t1 - t0) / 60))}


if __name__ == "__main__":
    out = {"n": N, "ring": RING, "dt": DT * 2, "swap_at": SWAP}
    out["human"], out["swap"] = run(), run(swap_at=SWAP)
    for k in ("human", "swap"):
        for name, (a, b) in (("jam", (40, SWAP)), ("after", (SECS - 60, SECS))):
            s = stats(out[k], a, b, DT * 2)
            out[f"{k}_{name}"] = s
            print(f"{k:5s} {name:5s} avg {s['avg_mph']:5.1f} mph  stopped {s['stopped_share']*100:4.1f}%  stops/car/min {s['stops_per_car_min']:.2f}")
    sw = np.array(out["swap"]["v"])
    calm_t = next(k for k in range(int(SWAP / (DT * 2)), len(sw)) if (sw[k] < 0.5).sum() == 0 and (sw[k:k + 100] < 0.5).sum() == 0)
    out["clear_at"] = calm_t * DT * 2
    print(f"jam gone {out['clear_at'] - SWAP:.0f} s after the swap")
    json.dump(out, open("sim.json", "w"))
