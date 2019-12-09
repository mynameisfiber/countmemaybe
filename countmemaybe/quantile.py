#!/usr/bin/env python2.7
"""
Probabilistic Quantiles Datastructure.  Implemented directly from:

    http://www.cs.rutgers.edu/~muthu/bquant.pdf

Using the following as a reference implemintaiton:

    https://github.com/bmizerany/perks/blob/master/quantile/
"""


class InvalidQuantile(Exception):
    def __init__(self, q, quantiles):
        self.q = q
        self.quantiles = quantiles

    def __str__(self):
        return "Invalid Quantile. {} not in: {}".format(self.q, self.quantiles)


class Sample:
    __slots__ = ("value", "width", "delta")

    def __init__(self, value, width, delta):
        self.value = value
        self.width = width
        self.delta = delta

    def __cmp__(self, other):
        return cmp(self.value, other.value)


class Quantile(object):
    def __init__(self, quantiles=None, epsilon=0.001, buffer_size=500):
        self.quantiles = quantiles
        self.epsilon = epsilon
        self.samples = []
        self.temporary = []
        self._clean = True
        self._sorted = True
        self.size = buffer_size
        self.n = 0
        if quantiles:
            self.invariant = self.invariant_targeted
        else:
            self.invariant = self.invariant_biased

    def __getstate__(self):
        self.flush()
        return {
            "quantiles": self.quantiles,
            "epsilon": self.epsilon,
            "samples": self.samples,
            "size": self.size,
            "n": self.n,
        }

    def __setstate__(self, state):
        self.quantiles = state["quantiles"]
        self.epsilon = state["epsilon"]
        self.samples = state["samples"]
        self.temporary = []
        self._clean = True
        self._sorted = True
        self.size = state["size"]
        self.n = state["n"]
        if self.quantiles:
            self.invariant = self.invariant_targeted
        else:
            self.invariant = self.invariant_biased

    def invariant_biased(self, r):
        return 2 * self.epsilon * r

    def invariant_targeted(self, r, m=2 ** 63 - 1):
        f = 0
        for q in self.quantiles:
            if q * self.n <= r:
                f = (2.0 * self.epsilon * r) / q
            else:
                f = (2.0 * self.epsilon * (self.n - r)) / (1.0 - q)
            m = min(f, m)
        return m

    def insert(self, item):
        self.temporary.append(Sample(item, 1, 0))
        self._clean = False
        if len(self.temporary) == self.size:
            self.flush()
            self.compress()

    def flush(self):
        self.maybe_sort()
        self.merge(self.temporary)
        self.temporary = []
        self._clean = True

    def maybe_sort(self):
        if self._sorted:
            self._sorted = True
            self.temporary.sort()

    def merge(self, samples):
        i = 0
        r = 0.0
        for sample in samples:
            while i < len(self.samples):
                c = self.samples[i]
                if c.value > sample.value:
                    s = Sample(sample.value, sample.width, int(self.invariant(r)) - 1)
                    self.samples.insert(i, s)
                    break
                r += c.width
                i += 1
            else:
                self.samples.append(Sample(sample.value, sample.width, 0))
            self.n += sample.width

    def compress(self):
        if len(self.samples) < 2:
            return
        x = self.samples[-1]
        r = self.n - 1 - x.width

        i = len(self.samples) - 1
        while i > 0:
            c = self.samples[i]
            if c.width + x.width + x.delta <= self.invariant(r):
                x.width += c.width
                self.samples.pop(i)
            else:
                x = c
            r -= c.width
            i -= 1

    def query(self, q):
        if len(self.temporary) > 0 and len(self.samples) == 0:
            # if we haven't had to compress yet, we can get the exact answer
            self.maybe_sort()
            N = max(int(len(self.temporary) * q) - 1, 0)
            return self.temporary[N].value
        elif self.quantiles and q not in self.quantiles:
            raise InvalidQuantile(q, self.quantiles)
        self.flush()
        t = int(q * self.n) + 1
        t += int(self.invariant(t) / 2.0) + 1
        p = self.samples[0]
        r = 0
        for c in self.samples[1:]:
            if r + c.width + c.delta > t:
                return p.value
            r += p.width
            p = c
        return p.value
