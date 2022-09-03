# ent2

**A randomness testing suite for Makers.**

Creation of a new accurate and easy to use randomness test suite tailored for TRNG Makers generating in the sub 1 MB space. It will be a derivative of the `ent` test suite @ https://www.fourmilab.ch/random/ incorporating PASS and FAIL statuses for individual tests, alleviating the need for interpretation of _p_ values. The results of the tests will be followed by a final conclusive recommendation as to whether the sample set can be used for cryptographic purposes.

Perhaps looking like so:-


---------------
Permuted compression ratio, (p = 0.9855), FAIL.
Runs,                       (p = 0.4000), PASS.
Serial correlation,         (p = 0.0004), FAIL.

SAMPLES ARE NOT IID.

Pure compression,           (p = 0.7897), PASS.
Chi square distribution,    (p = 0.5000), PASS.
Arithmetic mean value,      (p = 0.0008), FAIL.
Monte Carlo value for Pi,   (p = 0.5071), PASS.
Excursion from mean,        (p = 0.9998), FAIL.
Min. entropy,               (p = 0.0002), FAIL.

Min. entropy < 5.9103 bits per byte.

SAMPLES UNSUITABLE FOR CRYPTOGRAPHY @ α = 0.0500.
----------------
