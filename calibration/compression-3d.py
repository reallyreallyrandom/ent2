"""
This one is for a new compressibility test of a uniformly random 8 bit sequence.
We compress the sample file with two compressors as bz2 | lzma. If one fails
to compress, the other might be able to. A double whammy.

But this one creates a 3D surface calibration file, rather than a 2D curve.
"""

# spell-checker: disable #

import bz2
import json
import lzma
import os
import random
import statistics
import time
from scipy.spatial import ConvexHull, convex_hull_plot_2d
import matplotlib.pyplot as plt
import numpy as np

X_LABEL = "Bytes"
FILENAME = "/tmp/2d-data.dat"
SAMPLES_LOW = 50_000
SAMPLES_HIGH = 1_000_000
NO_TRIALS = 1000
PROGRESS_DIVISOR = 5


def make_samples():
    n = random.randrange(SAMPLES_LOW, SAMPLES_HIGH + 1, 50_000)
    return os.urandom(n)


#  The specific testing code goes into here.
def test_trials():
    compressed_sizes = np.empty([0], dtype=int)
    samples_sizes = np.empty([0], dtype=int)

    for i in range(NO_TRIALS):
        #  Print progress, but not too quickly.
        if i % PROGRESS_DIVISOR == 0:
            print(i)
        samples = bytearray(make_samples())
        bz2_compressed_size = len(bz2.compress(samples))
        # bz2_compressed_size = 0
        # lzma_compressed_size = len(lzma.compress(samples))      
        lzma_compressed_size = 0  
        compressed_sizes = np.append(compressed_sizes, (bz2_compressed_size + lzma_compressed_size))
        samples_sizes = np.append(samples_sizes, len(samples))
    return samples_sizes, compressed_sizes


x, y = test_trials()


plt.scatter(x, ((y-x)), color="purple", marker="+")
points = np.stack((x, y-x), axis=-1)
hull = ConvexHull(points)
for simplex in hull.simplices:
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
plt.title(FILENAME)
plt.xlabel("Size.")
plt.ylabel("Comp-size increase.")
# plt.xscale("log")
# # plt.yscale("log")
plt.grid()
plt.show()
