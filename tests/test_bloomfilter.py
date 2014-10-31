#!/usr/bin/env python2.7

from countmemaybe import BloomFilter

def test_bloom():
    items = ["a", "b", "c"]
    b = BloomFilter(items = items)
    for i in items:
        assert i in b
    for i in items:
        b.delete(i)
    for i in items:
        assert i not in b

def test_union():
    items1 = "ab"
    items2 = "bce"
    b1 = BloomFilter(items = items1, N=1, size=7)
    b2 = BloomFilter(items = items2, N=1, size=7)

    assert all(i in b1 for i in items1)
    assert all(i in b2 for i in items2)

    b1pb2 = b1 + b2

    assert all(i in b1pb2 for i in items1+items2)

