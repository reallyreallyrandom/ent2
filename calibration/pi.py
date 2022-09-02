"""
This one is for the Monte Carlo estimate of pi using
a uniformly random 8 bit sequence. 

We use the average value method from:-
https://blogs.sas.com/content/iml/2016/03/14/monte-carlo-estimates-of-pi.html
as its resultant variance is much tighter.
"""


import json
import math
import statistics
import time

import matplotlib.pyplot as plt
import numpy as np
from numpy import random


X_LABEL = "Value"
FILENAME = "/pi/pi-512kB.json"
NO_SAMPLES = int(512_000 // 4)   # It takes 4 bytes to create a float sample.
NO_TRIALS = 100
PROGRESS_DIVISOR = 25


#  The specific testing code goes into here.
def test_trials():
    pis = np.empty([0], dtype=float)

    for i in range(NO_TRIALS):
        #  Print progress, but not too quickly.
        if i % PROGRESS_DIVISOR == 0:
            print(i)
        ys = np.empty([NO_SAMPLES], dtype=float)
        samples = random.rand(NO_SAMPLES)
        # Have to do this rather than .append for speed.
        for j in range(samples.size):
            y = math.sqrt(1 - (samples[j] ** 2))
            # print(y)
            ys[j] = y

        pi = 4 * np.mean(ys)
        pis = np.append(pis, pi)
    return pis


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
