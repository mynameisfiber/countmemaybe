#!/usr/bin/env python2.7
"""
Benchmark for the DVE's in this package

micha gorelick, mynameisfiber@gmail.com
http://micha.gd/
"""

import numpy as np
import pylab as py

import mmh3
import hyperloglog as hll
import kminvalues as kmv

from progressbar import ProgressBar, Bar, ETA

class DVESet(set):
    def cardinality(self):
        return len(self)

MAX_64BIT_INT = 2**63 - 1
MAX_32BIT_INT = 2**31 - 1
MAX_16BIT_INT = 2**15 - 1

if __name__ == "__main__":
    max_val    = 5 * MAX_16BIT_INT
    chunk_size =    max_val // 500
    murmur64 = lambda x : mmh3.hash64(x)[0]

    methods = {
        "actual"          : DVESet(),
        "32bit hll m=256" : hll.HyperLogLog(b=8),
        "32bit kmv k=256" : kmv.KMinValues(k=2**8),
        "64bit kmv k=256" : kmv.KMinValues(k=2**8, hasher=murmur64, hasher_max=MAX_64BIT_INT),
    }

    results = {f:[] for f in methods}

    x = np.arange(1, max_val, chunk_size)

    widgets = ["Processing", Bar(), ETA()]
    p = ProgressBar(maxval=len(x), widgets=widgets).start()
    for i in p(x):
        r = np.random.randint(MAX_16BIT_INT, size=chunk_size)
        for name, m in methods.items():
            m.update(r)
            results[name].append(m.cardinality())

    for r in results:
        results[r] = np.asarray(results[r])

    py.subplot(211)
    py.title("Comparison of distinct value estimators")
    for name, result in results.iteritems():
        py.plot(x, result, label=name)
    py.legend(loc=2)
    py.ylabel("Cardinality")
    py.xlim(xmax=x[-1])

    py.subplot(212)
    py.axhline(0)
    actual = results["actual"]
    for name, result in results.iteritems():
        if name == "actual":
            continue
        theoretical_eerror = methods[name].relative_error() * 100.0
        mean_eerror = (np.abs(actual - result) / actual).mean() * 100.0
        py.plot(x, (actual-result)/actual * 100.0, label="%s (theory: %0.2f%%," \
                " mean: %0.2f%%)" % (name, theoretical_eerror, mean_eerror))
    py.ylim((-25., 25.))
    py.legend(loc=8, ncol=2, fontsize="small")
    py.ylabel("Relative error")
    py.xlabel("non-unique set size")
    py.xlim(xmax=x[-1])

    py.savefig("test_dve.png")
