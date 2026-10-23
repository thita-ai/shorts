# thita Shorts: the code

The real code behind the [thita.ai](https://thita.ai) Shorts and Reels. Every number you see in a video comes from running the code in its folder.

Each episode lives in its own numbered folder with its own README (what it simulates, the results, how to run it) and `requirements.txt`.

| # | Short | What the code does |
|---|---|---|
| 009 | [One Car Fixed a Traffic Jam](009-phantom-traffic-jam/) | 22 cars on a ring road, one brake tap makes a phantom jam, one calm driver clears it |

## Running an episode

```bash
cd 009-phantom-traffic-jam
pip install -r requirements.txt
python3 traffic.py
```

The video rendering (voice, captions, art) is not in this repo; only the simulations and algorithms are.

Prepping for coding interviews? [thita.ai](https://thita.ai): 99 DSA patterns, an AI coach and AI mock interviews.
