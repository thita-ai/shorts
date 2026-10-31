"""Collatz. Two rules: if it's even, halve it; if it's odd, triple it and add one. Every number tried so far reaches 1.

  python3 collatz.py  -> sim.json (the paths of 26 and 27, ten random huge starts, and what
                             remembering already-solved numbers saves on 1..1,000,000)
"""
import json, pathlib, random


def path(n):
    """Every value from n down to 1."""
    out = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        out.append(n)
    return out


def steps_all(limit, memo):
    """Steps to reach 1 for every n below limit. Returns the number of rule applications done."""
    known, work = {1: 0}, 0
    for n in range(2, limit):
        x, trail = n, []
        while x != 1 and not (memo and x in known):
            trail.append(x)
            x = x // 2 if x % 2 == 0 else 3 * x + 1
            work += 1
        s = known.get(x, 0)
        for v in reversed(trail):
            s += 1
            if memo:
                known[v] = s
    return work


if __name__ == "__main__":
    root = pathlib.Path(__file__).resolve().parent
    p26, p27 = path(26), path(27)
    print("26:", len(p26) - 1, "steps;  27:", len(p27) - 1, "steps, peak", max(p27), "at step", p27.index(max(p27)))
    random.seed(2026)
    big = [random.randint(10 ** 18, 10 ** 19) for _ in range(10)]
    rand = [{"n": str(n), "path": [str(v) for v in path(n)]} for n in big]
    for r in rand:
        print("random", r["n"], "->", len(r["path"]) - 1, "steps")
    LIM = 1_000_000
    naive, memo = steps_all(LIM, False), steps_all(LIM, True)
    print(f"1..{LIM:,}: naive {naive:,} steps, remembering {memo:,} steps ({naive / memo:.0f}x less)")
    # the first 30 numbers with memo: where each path first hits a number already solved
    known, firsts = {1}, []
    for n in range(2, 31):
        x, trail = n, []
        while x not in known:
            trail.append(x)
            x = x // 2 if x % 2 == 0 else 3 * x + 1
        firsts.append({"n": n, "new": trail, "hit": x})
        known.update(trail)
    json.dump({"p26": p26, "p27": p27, "random": rand, "naive": naive, "memo": memo, "lim": LIM,
               "firsts": firsts}, open(root / "sim.json", "w"))
