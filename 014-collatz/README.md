# 014: This Number Should Never Come Back Down

Pick any number. If it's even, cut it in half. If it's odd, triple it and add one. Repeat.

Lothar Collatz posed this in 1937. Every number anyone has ever tried ends at 1, and computers have checked far past a quintillion. Nobody has proven that every number does. That's the Collatz conjecture (also called 3n + 1), still unsolved.

## Results

| Start | Steps to reach 1 | Note |
|---|---|---|
| 26 | 10 | 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1 |
| 27 | 111 | climbs to 9,232 at step 77 before it crashes |
| 10 random numbers in the quintillions (seed 2026) | 283 to 539 | 10 out of 10 reach 1 |

Making it fast: remember every number you've already solved (memoization). Paths keep running into numbers you've seen, so you can stop there.

| All numbers from 1 to 1,000,000 | Rule applications |
|---|---|
| Without remembering | 131,434,272 |
| Remembering solved numbers | 2,168,610 (61x less work) |

## Run it

```bash
python3 five_lines.py   # the whole thing: steps for 27 (111)
python3 collatz.py      # every number above, written to sim.json
```

Change the 27 in `five_lines.py` and try your own. Find a number that never reaches 1 and you've solved it.
