"""
This one is for the runs test to determine whether or not a 
dataset comes from a random process.

See https://www.statology.org/runs-test-python/
"""



# spell-checker: disable #


import json
import statistics
import time
from statsmodels.sandbox.stats.runs import runstest_1samp  
import matplotlib.pyplot as plt
import numpy as np
from numpy import random


X_LABEL = "Z value"
FILENAME = "/runs/runs-512kB.json"
NO_SAMPLES = 512_000
NO_TRIALS = 10_00
PROGRESS_DIVISOR = 10


#  The specific testing code goes into here.
def test_trials():
    runs = np.empty([0], dtype=float)

    for i in range(NO_TRIALS):
        #  Print progress, but not too quickly.
        if i % PROGRESS_DIVISOR == 0:
            print(i)
        samples = np.random.randint(256, size=NO_SAMPLES)
        run, p = runstest_1samp(samples, correction=False)
        runs = np.append(runs, run)
    return runs


then = time.time()
all_statistics = test_trials()
now = time.time()
the_mean = statistics.mean(all_statistics)
print("\n\n", "mean =", the_mean, "")
run_rate = NO_TRIALS / (now - then)
print("At a run rate of", run_rate, "trials/s")


# Dump data to a JSON file.
# stats_list = all_statistics.tolist()
# json_object = json.dumps(stats_list)
# with open(FILENAME, "w") as outfile:
#     # print(json_object)
#     outfile.write(json_object)


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
