# ent2

**A randomness testing suite for Makers.**

Creation of a new accurate and easy to use randomness test suite tailored for TRNG Makers generating in the sub 1 MB space. It will be a derivative of the `ent` test suite @ https://www.fourmilab.ch/random/ incorporating PASS and FAIL statuses for individual tests, alleviating the need for interpretation of _p_ values. The results of the tests will be followed by a final conclusive recommendation as to whether the sample set can be used for cryptographic purposes.

Perhaps looking like so:-



```
Testing test-samples/urandom.bin.

Permuted compression ratio  p = 0.985  FAIL.
Runs                        p = 0.400  PASS.
Serial correlation          p = 0.006  FAIL.

SAMPLES ARE NOT IID.

Pure compression            p = 0.789  PASS.
Chi square distribution     p = 1.000  PASS.
Arithmetic mean value       p = 0.000  FAIL.
Monte Carlo value for Pi    p = 0.507  PASS.
Excursion from mean         p = 0.999  FAIL.
Min. entropy                p = 0.000  FAIL.

Min. entropy < 5.31 bits per byte.

SAMPLES UNSUITABLE FOR CRYPTOGRAPHY @ α = 0.05.
```



The current release version of `ent2` only accepts sample files that are **exactly** 512,000 bytes in length. Future releases will accommodate 64,000 byte, 128,000 byte and 256,000 byte sample sizes, as well as the current 512,000 byte samples size. Predetermined file sample lengths are absolutely necessary as some of the tests have no algebraic forms and so have to be calibrated via simulation.

