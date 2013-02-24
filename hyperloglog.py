#!/usr/bin/env python2.7
"""
This is a small implemintation of the hyper loglog algorithm for distinct
value estimation using the alorithm descibed in [1].  Benchmarks on 1.8 GHz
core i7 Macbook air yields 3.74 us per insertion and a relative error of
~1.34% for 160000 16bit integers using b=8 and 32bit murmur hash.

micha gorelick, micha@bit.ly

[1]: http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
"""

import mmh3
import math
from base_dve import BaseDVE

class InvalidParameters(Exception):
    pass

class HyperLogLog(BaseDVE):
    def __init__(self, items=[], b=4, hasher=mmh3.hash):
        if not 4 <= b <= 16:
            raise InvalidParameters()
        self.b = b
        self.m = 2**b
        self.M = [0,] * self.m
        self.hasher = hasher
        self._width = 31 - self.b
        if self.m >= 128:
            self.alpha = 0.7213 / (1.0 + 1.079 / self.m)
        elif self.m == 64:
            self.alpha = 0.709
        elif self.m == 32:
            self.alpha = 0.697
        elif self.m == 16:
            self.alpha = 0.673
        self.update(items)

    def _hash(self, item):
        return self.hasher(str(item))

    def rho(self, x, width=0):
        mask = 1 << (width - 1)
        i = 1
        while x & mask == 0 and mask > 0:
            mask >>= 1
            i += 1
        return i
    
    def add(self, item):
        x = self._hash(item)
        j = x >> self._width
        w = x ^ (j << self._width)
        self.M[j] = max(self.M[j], self.rho(w, width=self._width))

    def _indicator(self, M):
        return 1.0 / sum(2**-m for m in M)

    def union(self, other):
        assert self.m == other.m
        assert self.hasher == other.hasher
        assert self._width == other._width
        for i in xrange(self.m):
            self.M[i] = max(self.M[i], other.M[i])

    def cardinality(self):
        return self._card_helper(self.M, self.m, self.alpha)

    def cardinality_union(self, other):
        assert self.m == other.m
        assert self.hasher == other.hasher
        assert self._width == other._width
        M = [max(self.M[i], other.M[i]) for i in range(self.m)]
        return self._card_helper(M, self.m, self.alpha)

    def cardinality_intersection(self, other):
        A = self.cardinality()
        B = other.cardinality()
        AuB = self.cardinality_union(other)
        return A + B - AuB

    def jaccard(self, other):
        A = self.cardinality()
        B = self.cardinality()
        AuB = self.cardinality_union(other)
        return (A + B)/AuB - 1

    def _card_helper(self, M, m, alpha):
        E = alpha * m * m * self._indicator(M)
        if E <= 5.0 / 2.0 * m:
            V = M.count(0)
            if V != 0:
                Estar = m * math.log(m / (1.0 * V), 2)
            else:
                Estar = E
        else:
            if E <= 2**32 / 30.0:
                Estar = E
            else:
                Estar = -2**32 * math.log(1 - E / 2**32, 2)
        return Estar
        
    def relative_error(self):
        return 1.04 / math.sqrt(self.m)

def test_constructor():
    t1 = HyperLogLog()
    t2 = HyperLogLog(b=4)
    try:
        t3 = HyperLogLog(b=17)
        raise Exception("Should have thrown an InvalidParameter exception")
    except InvalidParameters:
        pass

def test_rho():
    t1 = HyperLogLog()
    assert 1 == t1.rho(0b10101010101, width=11)
    assert 4 == t1.rho(0b00011010101, width=11)
    assert 5 == t1.rho(0b0000, width=4)

def test_union():
    t1 = HyperLogLog(range(10), b=5)
    t2 = HyperLogLog(range(10), b=5)
    t3 = HyperLogLog(range(20), b=5)

    t1.union(t2)
    assert set(t1.M) == set(t2.M)

    t1.union(t3)
    assert set(t1.M) == set(t3.M)

    t4 = HyperLogLog(range(10), b=4)
    try:
        t1.union(t4)
        raise Exception("Should have complained about parameters")
    except:
        pass

def test_add():
    t1 = HyperLogLog(b=4)
    t1.add("TEST1")
    assert any(t1.M)

    Mmax = max(t1.M)

    t1.add("TEST1")
    assert Mmax == max(t1.M)

