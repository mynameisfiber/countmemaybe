#!/usr/bin/env python2.7
"""
Not really useful for DVE, but I felt like implementing a quick little bloom
filter anyways

micha gorelick, mynameisfiber@gmail.com
http://micha.gd/
"""

import mmh3
import numpy as np

class BloomFilter:
    def __init__(self, items=[], N=3, size=20, dtype=np.uint8):
        self.bloom = np.zeros(size, dtype=dtype)
        self.size = size
        self.N = N
        self.dtype = dtype
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

    def __add__(self, other):
        if not isinstance(other, BloomFilter):
            raise ValueError("Must be instance of BloomFilter")
        if self.size != other.size or self.N != other.N or self.dtype != other.dtype:
            raise ValueError("Both blooms must have the same properties")
        newBloom = BloomFilter(N=self.N, size=self.size, dtype=self.dtype)
        for i in xrange(self.size):
            newBloom.bloom[i] = self.bloom[i] | other.bloom[i]
        return newBloom

    def delete(self, key):
        if self.contains(key):
            for idx in self._idxiter(key):
                self.bloom[idx] -= 1
