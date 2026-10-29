def euclid(hits, steps):
    """Spread hits over steps as evenly as possible (Bjorklund, 2003)."""
    a = [[1]] * hits                    # the hits
    b = [[0]] * (steps - hits)          # the rests
    # Euclid: divide, keep the remainder, repeat
    while len(b) > 1:
        n = min(len(a), len(b))
        a, b = [a[i] + b[i] for i in range(n)], a[n:] or b[n:]
    return sum(a + b, [])


if __name__ == "__main__":
    for name, k, n in [("tresillo", 3, 8), ("cinquillo", 5, 8), ("bossa nova", 5, 16),
                       ("west african bell", 7, 12), ("samba", 7, 16)]:
        print(f"E({k},{n})".ljust(8), "".join("x" if s else "." for s in euclid(k, n)), name)
