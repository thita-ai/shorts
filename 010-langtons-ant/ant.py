"""Langton's ant: two rules, ~10,000 steps of chaos, then a road that never ends.

  python3 ant.py   # prints when the road starts, from an empty grid and from 10 random messy grids
"""
import random


def ant(lit, steps):
    """The whole program. lit = set of lit squares. Yields where the ant is after every step."""
    x, y, dx, dy = 0, 0, 0, -1                # start in the middle, facing up
    for _ in range(steps):
        if (x, y) in lit:
            dx, dy = dy, -dx                  # lit square: turn left
            lit.remove((x, y))
        else:
            dx, dy = -dy, dx                  # dark square: turn right
            lit.add((x, y))
        x, y = x + dx, y + dy
        yield x, y


def road_start(path, period=104, hold=2500):
    """First step from which the ant repeats the same 104 moves forever (the "highway")."""
    for s in range(len(path) - period - hold):
        d = (path[s + period][0] - path[s][0], path[s + period][1] - path[s][1])
        if d != (0, 0) and all((path[t + period][0] - path[t][0], path[t + period][1] - path[t][1]) == d
                               for t in range(s, s + hold)):
            return s + 1, d
    return None, None


if __name__ == "__main__":
    path = list(ant(set(), 14000))
    s, d = road_start(path)
    print(f"empty grid: the road starts at step {s:,}, moving {d} every 104 steps")

    random.seed(2026)
    for i in range(10):
        mess = {(random.randint(-15, 15), random.randint(-15, 15)) for _ in range(150)}
        s, _ = road_start(list(ant(mess, 60000)))
        print(f"random start {i + 1:>2}: the road starts at step {s:,}" if s else f"random start {i + 1:>2}: no road yet")
