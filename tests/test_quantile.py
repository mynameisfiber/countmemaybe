#!/usr/bin/env python2.7

from countmemaybe import InvalidQuantile, Quantile


def test_targeted_uncompressed():
    quantile = Quantile([0.99, 0.95, 0.5])
    for i in range(10):
        quantile.insert(i + 1)
    for q in range(1, 10):
        assert quantile.query(q / 10.0) == q


def test_biased_uncompressed():
    quantile = Quantile()
    for i in range(10):
        quantile.insert(i + 1)
    for q in range(1, 10):
        assert quantile.query(q / 10.0) == q


def test_biased_compressed():
    import random

    quantile = Quantile()
    for i in range(1000):
        quantile.insert(random.random())
    for q in range(1, 10):
        assert abs(quantile.query(q / 10.0) - q / 10.0) < 0.05


def test_targeted_compressed():
    import random

    quantiles = [0.99, 0.98, 0.95, 0.5]
    quantile = Quantile()
    for i in range(1000):
        quantile.insert(random.random())
    for q in quantiles:
        assert abs(quantile.query(q) - q) < 0.05


def test_targeted_exception():
    import random

    quantile = Quantile([0.99])
    for i in range(1000):
        quantile.insert(random.random())
    try:
        quantile.query(0.12324123)
        raise
    except InvalidQuantile:
        return
    except:
        assert False, "Should have rasied InvalidQuantile"
