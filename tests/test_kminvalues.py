#!/usr/bin/env python2.7

from countmemaybe import KMinValues

def test_constructor():
    KMinValues(range(50))
    KMinValues(range(50), k=50)
    KMinValues(k=10)
    KMinValues()

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


