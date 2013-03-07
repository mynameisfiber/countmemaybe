#!/usr/bin/env python2.7
"""
This is a small implemintation of the K-min values algorithm for distinct
value estimation using the alorithm descibed in [1].  Benchmarks on 1.8 GHz
core i7 Macbook air yields 4.18 us per insertion and a relative error of
~1.53% for 160000 16bit integers using k=256 and 32bit murmur hash.

micha gorelick, mynameisfiber@gmail.com
http://micha.gd/

[1]: http://www.mpi-inf.mpg.de/~rgemulla/publications/beyer07distinct.pdf
"""

from base_dve import BaseDVE

import mmh3
from blist import sortedlist, sortedset
import math

from operator import attrgetter
from itertools import (chain, ifilterfalse, imap)

MAX_32BIT_INT = 2**31 - 1

def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


class KMinValues(BaseDVE):
    def __init__(self, items=[], k=20, hasher=mmh3.hash, hasher_max=MAX_32BIT_INT):
        self.kmin = sortedlist()
        self.k = k
        self.hasher = hasher
        self.hasher_max = hasher_max
        self.update(items)

    def _idx(self, key):
        # Returns a (self.hasher_max)-bit unsigned int
        return self.hasher(str(key)) & self.hasher_max

    def add(self, key):
        idx = self._idx(key)
        if len(self.kmin) < self.k:
            if idx not in self.kmin: # O(log^2(n))
                self.kmin.add(idx) # O(log^2(n))
        else:
            if idx < self.kmin[-1]:
                if idx not in self.kmin: # O(log^2(n))
                    self.kmin.pop() # O(log(n))
                    self.kmin.add(idx) # O(log^2(n))

    def _smallest_k(self, *others):
        return min(self.k, *imap(attrgetter("k"), others))

    def _direct_sum(self, *others):
        n = 0
        k = self._smallest_k(*others)
        X = sortedset(chain(self.kmin, *imap(attrgetter("kmin"), others)))[:k]
        for item in self.kmin:
            if item in X and all(item in L.kmin for L in others):
                n += 1
        return n, X

    def union(self, *others):
        newk = self._smallest_k(*others)
        self.kmin = sortedlist(unique_everseen(chain(self.kmin, *imap(attrgetter("kmin"), others))))[:newk]

    def jaccard(self, other, k=0):
        n, X = self._direct_sum(other)
        return n / (1.0 * len(X))

    def cardinality_intersection(self, *others):
        n, X = self._direct_sum(*others)
        cardX = self._cardhelp(max(X), len(X))
        return n / (1.0 * len(k)) * cardX

    def cardinality_union(self, *others):
        _, X = self._direct_sum(*others)
        cardX = self._cardhelp(max(X), len(X))
        return cardX

    def _cardhelp(self, kmin, k):
        return ((k - 1.0) * self.hasher_max) / (kmin)

    def cardinality(self):
        if len(self.kmin) < self.k:
            return len(self.kmin)
        return self._cardhelp(self.kmin[-1], self.k)

    def __add__(self, other):
        assert other.k == self.k
        k = self._smallest_k(other)
        nt = KMinValues(k = k)
        nt.kmin = self.kmin
        nt.union(other)
        return nt

    def relative_error(self, confidence=0.98, D=0):
        p = 0
        if D:
            try:
                from scipy import (special, optimize)
            except ImportError:
                raise Exception("Scipy needed for relative error bounds")
            k = self.k

            u = lambda D, k, e : (k - 1.0) / ((1.0 - e) * D)
            l = lambda D, k, e : (k - 1.0) / ((1.0 + e) * D)
            objective = lambda e, D, k, confidence : special.betainc(k, D-k+1, u(D, k, e)) - special.betainc(k, D-k+1, l(D, k, e)) - confidence

            try:
                p = optimize.newton(objective, x0=0.05, args=(D, k, confidence))
            except RuntimeError:
                pass
        else:
            p = math.sqrt(2.0 / (math.pi * (self.k - 2)))
        return p


def test_constructor():
    t1 = KMinValues(range(50))
    t2 = KMinValues(range(50), k=50)
    t1 = KMinValues(k=10)
    t1 = KMinValues()

def test_add():
    t1 = KMinValues(k=1)
    t1.add("TEST1")
    assert t1.kmin != []
    assert len(t1.kmin) == 1

    t1.add("TEST2")
    assert t1.kmin != []
    assert len(t1.kmin) == 1

def test_update():
    t1 = KMinValues(k=15)
    t1.update(range(10))
    assert len(t1.kmin) == 10

def test_jaccard():
    # k == 400 => relative error of ~0.05
    t1 = KMinValues(range(500), k=256)
    t2 = KMinValues(range(100, 500), k=256)

    j_kmin = t1.jaccard(t2)
    j_real = 4. / 5.
    error = t1.relative_error()
    assert abs(1 - j_kmin / j_real) <= error

def test_union():
    t1 = KMinValues(range(10), k=5)
    t2 = KMinValues(range(10), k=5)
    t3 = KMinValues(range(20), k=5)

    t1.union(t2)
    assert set(t1.kmin) == set(t2.kmin)

    t1.union(t3)
    assert set(t1.kmin) == set(t3.kmin)

    t4 = KMinValues(range(40,50), k=5)
    t5 = t4 + t1
    assert set(t1.kmin) != set(t5.kmin)
    assert set(t4.kmin) != set(t5.kmin)

