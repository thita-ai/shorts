# 010: This Ant Will Build a Road Forever

Langton's ant lives on an endless grid of dark squares and follows two rules:

1. On a dark square, turn right. On a lit square, turn left.
2. Flip the color of the square, then step forward.

For about 10,000 steps it makes small symmetric shapes, then chaos. Then, at **step 9,976**, it starts building a "highway": the same 104 moves over and over, two squares diagonally each time, forever.

Chris Langton made it in 1986 to study artificial life. It has been proven that the ant can never stay trapped in a finite area, but nobody has proven that it **always** ends up building the highway, whatever squares are lit when it starts. Every start anyone has tried does.

## Results

| Start | Road starts at step |
|---|---|
| Empty grid | 9,976 |
| 10 random grids (150 lit squares in a 31×31 area, seed 2026) | 527, 7,930, 6,758, 12,139, 13,451, 13,422, 19,777, 10,269, 17,711, 18,500 |

10 out of 10 found the road.

## Run it

No dependencies, Python 3 only:

```bash
python3 ant.py
```

Try to break it: change the seed, light up a bigger area, or draw your own pattern into `mess`. If you find a start that never builds the road, you have solved an open problem.
