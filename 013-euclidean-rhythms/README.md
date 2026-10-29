# 013: This Algorithm Accidentally Wrote the World's Drum Beats

In 2003, Eric Bjorklund at the Spallation Neutron Source (Oak Ridge National Laboratory, Tennessee) needed to spread *k* timing pulses over *n* time slots as evenly as possible. His algorithm works like Euclid's algorithm for the greatest common divisor: divide, keep the remainder, repeat.

In 2005, computer scientist Godfried Toussaint noticed what its output really is: many of the world's traditional rhythms ("The Euclidean Algorithm Generates Traditional Musical Rhythms", BRIDGES 2005).

## Results

| E(k, n) | Pattern | Rhythm |
|---|---|---|
| E(3, 8) | `x..x..x.` | Cuban tresillo |
| E(5, 8) | `x.xx.xx.` | Cuban cinquillo |
| E(5, 16) | `x..x..x..x..x...` | bossa nova (start from the 7th step: `x..x..x...x..x..`) |
| E(7, 12) | `x.xx.x.xx.x.` | West African bell pattern |
| E(7, 16) | `x..x.x.x..x.x.x.` | samba |

## Run it

```bash
python3 euclid.py        # prints the five rhythms above
python3 play.py 5 16     # writes rhythm_5_16.wav so you can hear it
```

Pick any two numbers (hits ≤ beats) and hear your own.
