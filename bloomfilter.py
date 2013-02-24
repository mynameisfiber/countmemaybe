#!/usr/bin/env python2.7
"""
Not really useful for DVE, but I felt like implementing a quick little bloom
filter anyways
micha gorelick, micha@bit.ly
"""

import mmh3

class BloomFilter:
    def __init__(self, items=[], N=3, size=20):
        self.bloom = [0,] * size
        self.size = size
        self.N = N
        for i in items:
            self.add(i)

    def _idxiter(self, key):
        k1, k2 = mmh3.hash64(key)
        for i in range(self.N):
            idx = (k1 + i * k2) % self.size
            yield idx

    def add(self, key):
        for idx in self._idxiter(key):
            self.bloom[idx] += 1

    def update(self, keys):
        for key in keys:
            self.add(key)

    def contains(self, key):
        for idx in self._idxiter(key):
            if not self.bloom[idx]:
                return False
        return True

    def __contains__(self, key):
        return self.contains(key)

    def delete(self, key):
        if self.contains(key):
            for idx in self._idxiter(key):
                self.bloom[idx] -= 1

def test_bloom():
    items = ["a", "b", "c"]
    b = BloomFilter(items = items)
    for i in items:
        assert i in b
    for i in items:
        b.delete(i)
    for i in items:
        assert i not in b

def test_union(items1, items2):
    import numpy as np
    b1 = BloomFilter(items = items1, N=1, size=7)
    b2 = BloomFilter(items = items2, N=1, size=7)

    f1 = np.asarray(b1.bloom)
    f2 = np.asarray(b2.bloom)

    print "f1: ", f1
    print "f2: ", f2

    f1pf2 = f1 + f2
    f1mf2 = f1 - f2

    print f1pf2, f1pf2.sum(), f1pf2.sum() / b1.N
    print f1mf2, f1mf2.sum(), np.abs(f1mf2).sum() / b1.N / 2.0


if __name__ == "__main__":
    test_bloom()

    test_union("ab", "bce")
