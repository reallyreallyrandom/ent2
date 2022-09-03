"""
This one is for a new compressibility test of a uniformly random 8 bit sequence.
We compress the sample file with two compressors as bz2 | lzma. If one fails
to compress, the other might be able to. A double whammy.
"""

# spell-checker: disable #

import lzma
import bz2
import json
import random
import time
import statistics
import matplotlib.pyplot as plt
import numpy as np


X_LABEL = "Bytes"
FILENAME = "compression/compression-xxkB.json"
NO_SAMPLES = 64_000
NO_TRIALS = 100_000
PROGRESS_DIVISOR = 100


# The filters are required for FORMAT_RAW format.
lzma_filters = [
    {"id": lzma.FILTER_DELTA, "dist": 1},
    {"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME},
]


def make_samples(n):
    for _ in range(n):
        yield random.getrandbits(8)


#  The specific testing code goes into here.
def test_trials():
    compressed_sizes = np.empty([0], dtype=int)

    for i in range(NO_TRIALS):
        #  Print progress, but not too quickly.
        if i % PROGRESS_DIVISOR == 0:
            print(i)
        samples = bytearray(make_samples(NO_SAMPLES))
        bz2_compressed_size = len(bz2.compress(samples, compresslevel=9))
        lzma_compressed_size = len(lzma.compress(
            samples, format=lzma.FORMAT_RAW, filters=lzma_filters))
        compressed_sizes = np.append(
            compressed_sizes, (bz2_compressed_size + lzma_compressed_size))
    return compressed_sizes


then = time.time()
all_statistics = test_trials()
now = time.time()
the_mean = statistics.mean(all_statistics)
print("\n\n", "mean =", the_mean, "bytes.")
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


plt.plot(bins_count[1:], cdf, color="purple")
plt.title(FILENAME)
plt.xlabel(X_LABEL)
plt.ylabel("p value")
plt.grid()
plt.show()