# Count me Maybe

> Hey I just met you,
> This is crazy,
> But here's a number,
> So count me, maybe?

`countmemaybe` is a set of probabilistic data structures that can estimate the
cardinality of a set and also support unions.  The base set of operations are:

* Cardinality
* Union
* Cardinality of the Union
* Cardinality of the Intersection
* Jaccard Index

Insertions are quite quick!  For both hyperloglog and kminvalues there is an
average insertion time of 4us on a 1.8GHz i7 Macbook Air.

Below are some benchmarks of error rates.  The set used for estimation are
160000 random 16bit integers and the benchmark was generated using the
`test_dve.py` script.  You can see that using a hash function with a larger
domain yields better results, although it requires more memory.  Furthermore,
interesting dynamics are seen where HLL performs worse than KMV on some sets of
data, and vise versa for others.  More investigation is necessary!

![Benchmarks](https://raw.github.com/mynameisfiber/countmemaybe/master/countmemaybe/test_dve.png "Benchmarks of hyper loglog vs kmin values")
