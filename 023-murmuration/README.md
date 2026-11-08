# 023: 500 Birds, No Leader

How do 500 birds turn at the same moment with nobody in charge? Each bird follows three rules, and it only
watches its **7 closest neighbors**:

1. Stay near them.
2. Don't bump into them.
3. Fly the way they fly.

Craig Reynolds wrote the first version of these rules ("boids") in 1986; Hollywood later used his work to fly
the bats in *Batman Returns* (1992). The number 7 comes from real birds: in 2008, Ballerini and colleagues
filmed starling flocks over Rome in 3D and found each bird tracks about 7 neighbors, near or far, not everyone
within a fixed distance. That is why a real flock can stretch out huge and still not fall apart.

## Run it

```bash
pip install numpy
python3 boids.py
```

`boids.py` is the whole thing: 13 lines. The sky wraps around, so birds that fly off one edge come back on the
other. After 1,500 steps, 99% of the birds fly the same way (3 seeds tried).

Try to break it: change 7 to 1 or 50, set "don't bump" to 0, or make the sky bigger. Which change stops the
flock from forming?
