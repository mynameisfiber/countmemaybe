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
`test_dve.py` script.  For some as of yet unknown reason, KMV with a 64bit hash
function performs _worse_ than a 32bit hash function.  This is counterintuitive
and requires more investigation.  Furthermore, exact mean relative error rates
vary from run to run by ~1%

![Benchmarks - Cardinality](https://raw.github.com/mynameisfiber/countmemaybe/dev/countmemaybe/test_dve-cardinality1.png "Benchmarks of hyper loglog vs kmin values")
![Benchmarks - Union](https://raw.github.com/mynameisfiber/countmemaybe/dev/countmemaybe/test_dve-union.png "Benchmarks of hyper loglog vs kmin values")
![Benchmarks - Intersection](https://raw.github.com/mynameisfiber/countmemaybe/dev/countmemaybe/test_dve-inter.png "Benchmarks of hyper loglog vs kmin values")
![Benchmarks - Jaccard](https://raw.github.com/mynameisfiber/countmemaybe/dev/countmemaybe/test_dve-jaccard.png "Benchmarks of hyper loglog vs kmin values")
