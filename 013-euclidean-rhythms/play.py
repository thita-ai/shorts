"""Hear any Euclidean rhythm: python3 play.py 5 16  ->  rhythm_5_16.wav (4 bars, a clave on every hit)"""
import math, struct, sys, wave
from euclid import euclid

k, n = int(sys.argv[1]), int(sys.argv[2])
SR, BAR, BARS = 44100, 2.0, 4
pattern = euclid(k, n)
out = [0.0] * int(SR * BAR * BARS)
hit = [(math.sin(2 * math.pi * 2500 * i / SR) + 0.5 * math.sin(2 * math.pi * 1700 * i / SR)) * math.exp(-i / SR / 0.03)
       for i in range(int(SR * 0.2))]
for b in range(BARS):
    for j, on in enumerate(pattern):
        if on:
            start = int((b * BAR + j * BAR / n) * SR)
            for i, v in enumerate(hit[: len(out) - start]):
                out[start + i] += v * 0.6
with wave.open(f"rhythm_{k}_{n}.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in out))
print(f"E({k},{n})", "".join("x" if s else "." for s in pattern), f"-> rhythm_{k}_{n}.wav")
