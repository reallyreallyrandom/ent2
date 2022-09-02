"""
Calculate the empirical values for mean and standard deviation
of various entv2 tests. Such as:-

Entropy = 7.966590 bits per byte.

Optimum compression would reduce the size
of this 218232 byte file by 0 percent.

Chi square distribution for 218232 samples is 10670.66, and randomly
would exceed this value less than 0.01 percent of the times.

Arithmetic mean value of data bytes is 121.4964 (127.5 = random).
Monte Carlo value for Pi is 3.227207742 (error 2.73 percent).
Serial correlation coefficient is 0.095710 (totally uncorrelated = 0.0).
---------------------------
This one is for a new test with a random walk over a uniformly random 8 bit sequence.
"""

import time

import matplotlib.pyplot as plt
import numpy as np
import pylab
import seaborn as sns

NO_SAMPLES = 500_000
NO_TRIALS = 10
PROGRESS_DIVISOR = 1


#  The specific testing code goes into here.
def test_trials():
    translations = np.empty([0], dtype=float)
    xpos = ypos = 0

    for i in range(NO_TRIALS):
        x = np.zeros(NO_SAMPLES)
        y = np.zeros(NO_SAMPLES)
        #  Print progress, but not too quickly.
        if i % PROGRESS_DIVISOR == 0:
            print(i)
        for step in range(NO_SAMPLES):
            compass = samples[step] & 0b11

            if compass == 1:
                x[i] = x[i - 1] + 1
                y[i] = y[i - 1]
            elif compass == 2:
                x[i] = x[i - 1] - 1
                y[i] = y[i - 1]
            elif compass == 3:
                x[i] = x[i - 1]
                y[i] = y[i - 1] + 1
            else:
                x[i] = x[i - 1]
                y[i] = y[i - 1] - 1

        # plotting stuff:
        pylab.plot(x, y)
        pylab.show()

        mean_result = np.mean(samples)
        means = np.append(means, mean_result)
    return translations


then = time.time()
all_statistics = test_trials()
now = time.time()
mean = np.mean(all_statistics)
std_dev = np.std(all_statistics)
print("\n\n", "mean =", mean, "standard deviation =", std_dev)
run_rate = NO_TRIALS / (now - then)
print("At a run rate of", run_rate, "trials/s")

sns.displot(all_statistics, kind="kde", fill=True, color="violet").set(title="Arithmetic Mean")
plt.show()
