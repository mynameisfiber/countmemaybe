#!/usr/bin/env python2.7

from countmemaybe import HyperLogLog, InvalidParameters


def test_constructor():
    HyperLogLog()
    HyperLogLog(b=4)
    try:
        HyperLogLog(b=17)
        raise Exception("Should have thrown an InvalidParameter exception")
    except InvalidParameters:
        pass


def test_rho():
    t1 = HyperLogLog()
    assert 1 == t1.rho(0b10101010101, width=11)
    assert 4 == t1.rho(0b00011010101, width=11)
    assert 5 == t1.rho(0b0000, width=4)


def test_union():
    t1 = HyperLogLog(list(range(10)), b=5)
    t2 = HyperLogLog(list(range(10)), b=5)
    t3 = HyperLogLog(list(range(20)), b=5)

    t1.union(t2)
    assert set(t1.M) == set(t2.M)

    t1.union(t3)
    assert set(t1.M) == set(t3.M)

    t4 = HyperLogLog(list(range(10)), b=4)
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
