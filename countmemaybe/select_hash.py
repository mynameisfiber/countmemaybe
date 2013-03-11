#!/usr/bin/env python2.7

import sys
import time
import operator

import numpy as np
import mmh3
import pyhash

MAX_32BIT = 2**31 - 1
MAX_64BIT = 2**63 - 1

def murmur64c(key):
    h = mmh3.hash64(key)
    return (h[0] + h[1]) % MAX_64BIT

hash_functions = {
    "murmur32" : {
        "func" : mmh3.hash,
        "max_hash" : MAX_32BIT,
    },
    "murmur64a" : {
        "func" : lambda h : mmh3.hash64(h)[0],
        "max_hash" : MAX_64BIT,
    },
    "murmur64b" : {
        "func" : lambda h : mmh3.hash64(h)[1],
        "max_hash" : MAX_64BIT,
    },
    "murmur64c" : {
        "func" : murmur64c,
        "max_hash" : MAX_64BIT,
    },
    "fnv1_32" : {
        "func" : pyhash.fnv1_32(),
        "max_hash" : MAX_32BIT,
    },
    "fnv1a_32" : {
        "func" : pyhash.fnv1a_32(),
        "max_hash" : MAX_32BIT,
    },
    "fnv1_64" : {
        "func" : pyhash.fnv1_64(),
        "max_hash" : MAX_64BIT,
    },
    "fnv1a_64" : {
        "func" : pyhash.fnv1a_64(),
        "max_hash" : MAX_64BIT,
    },
    "lookup3" : {
        "func" : pyhash.lookup3(),
        "max_hash" : MAX_32BIT,
    },
    "lookup3_big" : {
        "func" : pyhash.lookup3_big(),
        "max_hash" : MAX_32BIT,
    },
    "lookup3_little" : {
        "func" : pyhash.lookup3_little(),
        "max_hash" : MAX_32BIT,
    },
    "pyhashmurmur1_32" : {
        "func" : pyhash.murmur1_32(),
        "max_hash" : MAX_32BIT,
    },
    "pyhashmurmur1_aligned_32" : {
        "func" : pyhash.murmur1_aligned_32(),
        "max_hash" : MAX_32BIT,
    },
    "pyhashmurmur2_32" : {
        "func" : pyhash.murmur2_32(),
        "max_hash" : MAX_32BIT,
    },
    "pyhashmurmur2a_32" : {
        "func" : pyhash.murmur2a_32(),
        "max_hash" : MAX_32BIT,
    },
    "pyhashmurmur2_aligned_32" : {
        "func" : pyhash.murmur2_aligned_32(),
        "max_hash" : MAX_32BIT,
    },
    "pyhashmurmur2_neutral_32" : {
        "func" : pyhash.murmur2_neutral_32(),
        "max_hash" : MAX_32BIT,
    },
    "pyhashmurmur2_x64_64a" : {
        "func" : pyhash.murmur2_x64_64a(),
        "max_hash" : MAX_64BIT,
    },
    "pyhashmurmur2_x86_64b" : {
        "func" : pyhash.murmur2_x86_64b(),
        "max_hash" : MAX_64BIT,
    },
    "pyhashmurmur3_32" : {
        "func" : pyhash.murmur3_32(),
        "max_hash" : MAX_32BIT,
    },
    "pyhashsuperfast" : {
        "func" : pyhash.super_fast_hash(),
        "max_hash" : MAX_32BIT,
    },
}

def select_hash(domain, hash_functions, buckets=10000):
    entropy = test_hash_functions(domain, hash_functions, buckets=buckets)
    best_method, E = entropy[-1]
    Emax = -np.log(1.0 / buckets)
    return (best_method, hash_functions[best_method]), (Emax - E)/Emax

def test_hash_functions(domain, hash_functions=hash_functions, buckets=10000, plot=False, verbose=False):
    data = {k:np.zeros((buckets)) for k in hash_functions}
    timing = {k:0 for k in hash_functions}
    count = 0
    for i in domain:
        count += 1
        item = str(i)
        for name, meta in hash_functions.iteritems():
            s = time.time()
            h = (meta["func"](item) & meta["max_hash"]) / (1.0 * meta["max_hash"])
            timing[name] += (time.time() - s)
            idx = h * buckets
            try:
                data[name][idx] += 1
            except IndexError:
                print "Method %s has invalid 'max_hash'" % name
                raise
    entropy = []
    for method, d in data.iteritems():
        e = -sum(p / (1.0*count) * np.log(p / (1.0*count)) for p in d if p > 0)
        entropy.append((method, e))
    entropy.sort(key=operator.itemgetter(1))
    if verbose:
        Emax = -np.log(1.0 / buckets)
        for i, (m, e) in enumerate(entropy):
            print "%s: \t E[domain] = %f (%0.2e%%) \t sec/hash = %e" % (m, e, (Emax-e)*100 / Emax, timing[m]/count)
        print "ideal: \t E[domain] = %f" % (Emax)
    if plot:
        plot_entropy(data, entropy, count, buckets)
    return entropy

def plot_entropy(data, entropy, count, buckets):
    try:
        import pylab as py
    except ImportError:
        print "Could not import pylab, canceling entropy plotting"
        return
    py.subplot(len(data), 1, 1)
    for i, (m, e) in enumerate(entropy):
        py.subplot(len(data), 1, i)
        py.title("%s - %f" % (m, e))
        py.fill_between(np.linspace(0, 1, buckets), data[m] / (1.0*count), label=m)
        py.xlim((0, 1))
    py.show()

if __name__ == "__main__":
    try:
        buckets = int(sys.argv[1])
    except (IndexError, ValueError):
        buckets = 100000

    def reader():
        count = 1
        while True:
            print count
            count += 1
            line = sys.stdin.readline()
            if not line:
                break
            yield line.strip()

    print "Starting with %d buckets" % buckets
    test_hash_functions(reader(), buckets=buckets, verbose=True, plot=False)
