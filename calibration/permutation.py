"""
This one is for a new permuted compression ratio test of a uniformly random 8 bit sequence. It
is intended to replace the Shannon entropy compression test.

IID test using permutation testing theory.
Ref. NIST Special Publication 800-90B,
(https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-90B.pdf) ,
Recommendation for the Entropy Sources Used for Random Bit Generation,
Sections 5.1 & 5.1.1.

This only works for continuous binary data.  ASCII data with line terminations (and delimiters like tabs, commas
and spaces) is obviously correlated.
"""

# spell-checker: disable #


import json
import lzma
import bz2
import os
import random
import statistics
import time

import matplotlib.pyplot as plt
import numpy as np



X_LABEL = "Ratio"
FILENAME = "permutation/permutation-512kB.json"
NO_SAMPLES = 512_000
NO_TRIALS = 100_000


# The filters are required for FORMAT_RAW format.
lzma_filters = [
    {"id": lzma.FILTER_DELTA, "dist": 1},
    {"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME},
]


def make_samples(n):
    return os.urandom(n)
    

#  The specific testing code goes into here.
def test_trials():
    rng = np.random.default_rng()    # PCG XSL RR 128/64 random number generator.
    ratios = np.empty([0], dtype=float)

    for i in range(NO_TRIALS):
        print(i)
        samples = bytearray(make_samples(NO_SAMPLES))
        bz2_compressed_size = len(bz2.compress(samples, compresslevel=9))
        lzma_compressed_size = len(lzma.compress(
            samples, format=lzma.FORMAT_RAW, filters=lzma_filters))

        rng.shuffle(samples)

        bz2_compressed_shuffled_size = len(bz2.compress(
            samples, compresslevel=9))
        lzma_compressed_shuffled_size = len(lzma.compress(
            samples, format=lzma.FORMAT_RAW, filters=lzma_filters))
        # ratio definitely >> 1 if not IID.
        ratio = (bz2_compressed_shuffled_size + lzma_compressed_shuffled_size) / \
            (bz2_compressed_size + lzma_compressed_size)
        ratios = np.append(ratios, ratio)
    return ratios


then = time.time()
all_statistics = test_trials()
now = time.time()
the_mean = statistics.mean(all_statistics)
print("\n\n", "mean =", the_mean)
run_rate = NO_TRIALS / (now - then)
print("At a run rate of", run_rate, "trials/s.")


# Dump data to a JSON file.
stats_list = all_statistics.tolist()
json_object = json.dumps(stats_list)
with open(FILENAME, "w") as outfile:
    # print(json_object)
    outfile.write(json_object)


# p values from a cumulative distribution plot.
count, bins_count = np.histogram(all_statistics, bins=100)
pdf = count / sum(count)
cdf = np.cumsum(pdf)


# p values from a cumulative distribution plot
count, bins_count = np.histogram(all_statistics, bins=100)
pdf = count / sum(count)
cdf = np.cumsum(pdf)

plt.plot(bins_count[1:], cdf, color="purple")
plt.title(FILENAME)
plt.xlabel(X_LABEL)
plt.ylabel("p value")
plt.grid()
plt.show()
