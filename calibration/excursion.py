"""
This one is for a new excursion from the mean test of a uniformly random 8 bit sequence.
The excursion test statistic measures how far the running sum of sample values deviates from its
average value at each point in the dataset. Given S = (s1 ,..., sL), the test statistic is the largest
deviation from the average.
See https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-90B.pdf section 5.1.1.

It has been tested against the NIST `ea_iid` test of SP800-90b. That's why there
is the extra `def make_samples(n)` routine (commented out). Generate a file as:
`dd if=/dev/urandom  of=/tmp/urandom-ex   bs=1000   count=512` and feed it into both
to verify this code.
"""


# spell-checker: disable #


import json
import random
import statistics
import time
from statistics import mean

import matplotlib.pyplot as plt
import numpy as np


X_LABEL = "Value"
FILENAME = "/tmp/excursion-64kB.json"
NO_SAMPLES = 64_000
NO_TRIALS = 1000
PROGRESS_DIVISOR = 10


"""
This allows input of an external file that can also be
fed into the NIST test for code validation.
"""
# def make_samples(n):
#     with open("/tmp/urandom-ex", mode='rb') as file:   # b is important -> binary
#         fileContent = file.read()
#     return fileContent


#  The specific testing code goes into here.
def test_trials():
    excursions = np.empty([0], dtype=float)

    for i in range(NO_TRIALS):
        #  Print progress, but not too quickly.
        if i % PROGRESS_DIVISOR == 0:
            print(i)
        samples = np.random.randint(256, size=NO_SAMPLES)
        average = np.mean(samples)
        cumsum = np.cumsum(samples)
        trial_excursions =  np.empty([NO_SAMPLES], dtype=float)

        for i in range(NO_SAMPLES):
            running_mean = average * (i + 1)
            trial_excursion = abs(cumsum[i] - running_mean)
            trial_excursions[i] = trial_excursion
        excursions = np.append(excursions, np.max(trial_excursions))
    return excursions


then = time.time()
all_statistics = test_trials()
now = time.time()
mean = statistics.mean(all_statistics)
print("\n\n", "mean =", mean, "bytes.")
run_rate = NO_TRIALS / (now - then)
print("At a run rate of", run_rate, "trials/s.")


# Dump data to a JSON file.
stats_list = all_statistics.tolist()
json_object = json.dumps(stats_list)
with open(FILENAME, "w") as outfile:
    # print(json_object)
    outfile.write(json_object)


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
