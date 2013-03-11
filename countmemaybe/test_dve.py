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
    def jaccard(self, other):
        return len(self.intersection(other)) / (1.0 * len(self.union(other)))
    def cardinality_union(self, other):
        return len(self.union(other))
    def cardinality_intersection(self, other):
        return len(self.intersection(other))

MAX_64BIT_INT = 2**63 - 1
MAX_32BIT_INT = 2**31 - 1
MAX_16BIT_INT = 2**15 - 1

if __name__ == "__main__":
    max_val    = 3 * MAX_16BIT_INT
    chunk_size =    max_val // 500
    murmur64 = lambda x : mmh3.hash64(x)[0]

    methods = {
        "actual"          : [DVESet() for r in range(2)],
        "32bit hll m=512" : [hll.HyperLogLog(b=9) for r in range(2)],
        "32bit kmv k=512" : [kmv.KMinValues(k=2**9) for r in range(2)],
        "64bit kmv k=256" : [kmv.KMinValues(k=2**8, hasher=murmur64, hasher_max=MAX_64BIT_INT) for r in range(2)],
    }

    results = {f:{"cardinality1":[], "cardinality2":[], "union":[], "inter":[], "jaccard":[]}  for f in methods}

    x = np.arange(1, max_val, chunk_size)

    np.random.seed()
    widgets = ["Processing", Bar(), ETA()]
    p = ProgressBar(maxval=len(x), widgets=widgets).start()
    for i in p(x):
        r1 = np.random.randint(MAX_16BIT_INT, size=chunk_size)
        r2 = np.random.randint(MAX_16BIT_INT, size=chunk_size)
        for name, m in methods.items():
            m[0].update(r1)
            m[1].update(r2)
            results[name]["cardinality1"].append(m[0].cardinality())
            results[name]["cardinality2"].append(m[1].cardinality())
            results[name]["union"].append(m[0].cardinality_union(m[1]))
            results[name]["inter"].append(m[0].cardinality_intersection(m[1]))
            results[name]["jaccard"].append(m[0].jaccard(m[1]))

    for r, rv in results.iteritems():
        for t in rv:
            results[r][t] = np.asarray(results[r][t])

    for experiment in results["actual"]:
        py.figure()
        py.subplot(211)
        py.title("Comparison of distinct value estimators - %s" % experiment)
        for name, result in results.iteritems():
            py.plot(x, result[experiment], label=name)
        py.legend(loc=2)
        py.ylabel(experiment)
        py.xlim(xmax=x[-1])

        py.subplot(212)
        py.axhline(0)
        actual = results["actual"][experiment]
        for name, result in results.iteritems():
            if name == "actual":
                continue
            theoretical_eerror = methods[name][0].relative_error() * 100.0
            mean_eerror = (np.abs(actual - result[experiment]) / actual)[1000//chunk_size:].mean() * 100.0
            py.plot(x, (actual-result[experiment])/actual * 100.0, label="%s (theory: %0.2f%%," \
                    " mean: %0.2f%%)" % (name, theoretical_eerror, mean_eerror))
        py.ylim((-50., 50.))
        py.legend(loc=8, ncol=2, fontsize="small")
        py.ylabel("Relative error")
        py.xlabel("non-unique set size")
        py.xlim(xmax=x[-1])

        py.savefig("test_dve-%s.png" % experiment)
