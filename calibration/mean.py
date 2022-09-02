"""
This one is for the mean test of a uniformly random 8 bit sequence.
"""


# spell-checker: disable #


import json
import statistics
import time

import matplotlib.pyplot as plt
import numpy as np


X_LABEL = "Value"
FILENAME = "calibration/mean/mean-512kB-1M.json"
NO_SAMPLES = 512_000
NO_TRIALS = 1_000_000
PROGRESS_DIVISOR = 100


#  The specific testing code goes into here.
def test_trials():
    means = np.empty([0], dtype=float)

    for i in range(NO_TRIALS):
        #  Print progress, but not too quickly.
        if i % PROGRESS_DIVISOR == 0:
            print(i)
        samples = np.random.randint(256, size=NO_SAMPLES)
        mean_result = np.mean(samples)
        means = np.append(means, mean_result)
    return means


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
count, bins_count = np.histogram(all_statistics, bins=1_000)
pdf = count / sum(count)
cdf = np.cumsum(pdf)


plt.plot(bins_count[1:], cdf, color="purple")
plt.title(FILENAME)
plt.xlabel(X_LABEL)
plt.ylabel("p value")
plt.grid()
plt.show()
