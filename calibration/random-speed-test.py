"""
Tests the relative rate of random number generation.
Compares Python , OS.Random and Numpy.

I get:-
Pythons's default, 6.755408763885498
Cryptographic OS generator, 0.26140356063842773
Numpy, 0.3641190528869629
"""


import os
import random
import time

import numpy as np


NO_SAMPLES = 100_000_000


# Pythons's default (MS Twister).
then = time.time()
for i in range(NO_SAMPLES):
    r = random.randbytes
    # print(r)
now = time.time()
print("Pythons's default,", now - then)


# Cryptographic OS generator (ChaCha20 on Linux).
then = time.time()
r = os.urandom(NO_SAMPLES)
# print(r)
now = time.time()
print("Cryptographic OS generator,", now - then)


# Numpy's internal generator (PCG64)
rng = np.random.default_rng()
then = time.time()
r = rng.integers(low=0, high=256, size=NO_SAMPLES)
# print(r)
now = time.time()
print("Numpy,", now - then)
