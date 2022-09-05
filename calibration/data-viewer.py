"""

Copyright (c) 2022:
Paul Uszak. Email: paul.uszak_at_gmail.com. (Change _at_ to @)



Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


For viewing our JSON calibration data, and determining cutoffs 
at alpha = X. We then interpolate the test statistics. 

See https://docs.scipy.org/doc/scipy/tutorial/interpolate.html
"""

# spell-checker: disable #


import enum
import json
import math
import sys
from turtle import color, width

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate, stats
from scipy.interpolate import UnivariateSpline, interp1d



# This is rather important.
ALPHA = 0.05


# The alpha boundries.
class critical_ps(float, enum.Enum):
    left_outer = ALPHA / 2
    left_inner = ALPHA
    right_inner = 1 - ALPHA
    right_outer = 1 - (ALPHA / 2)


# read in file.
all_statistics = []
filename = str(sys.argv[1])
with open(filename, "rb") as infile:
    all_statistics = json.load(infile)
    statistics = np.array(all_statistics, dtype=float)


# Decide on how many histogram bins we want.
# Use the square root of the sample size method.
no_bins = round(math.sqrt(statistics.size))


# Create parallel normal distribution for comparison.
mu = np.mean(statistics)
sigma = np.std(statistics)
theoretical_statistics = np.random.normal(mu, sigma, statistics.size)


# Check for Normality.
statistic, p_value = stats.ks_2samp(statistics, theoretical_statistics)
print("\n\nmu =", mu, ", sigma =", sigma)
print("\n\nNormality test, p =", p_value)
if p_value > critical_ps.left_outer and p_value < critical_ps.right_outer:
    print("Normally distributed :-)")
else:
    print("Not normally distributed :-(")



# Obtain the cummulative distribution.
hist, bin_edges = np.histogram(statistics, bins=no_bins)
pdf = hist / np.sum(hist)
cdf = np.cumsum(pdf)


# TODO Try to improve the interpolatioin smoothing.
# FIXME Firm up these critical alpha values with Adam.
# Interpolate p -> test statistic.
criticals = np.array([critical_ps.left_outer,
                      critical_ps.left_inner,
                      critical_ps.right_inner,
                      critical_ps.right_outer])
# interp_func = UnivariateSpline(cdf, bins_count[1:])
interp_func = interp1d(cdf, bin_edges[1:], kind="linear")
# tck = interpolate.splrep(cdf, bins_count[1:])
# ynew = interpolate.splev(cutoffs, tck, der=0)
critical_statistics = interp_func(criticals)
print("\nCriticals @ p =", criticals, "=", critical_statistics)








# print(bin_edges[1:], "\n\n\n", cdf)







# Plot two charts.
# Test statistic vs p.
fig = plt.figure()
stat = plt.subplot(121)
plt.plot(bin_edges[1:], cdf, color="purple", linewidth=3)
plt.matplotlib.pyplot.axhline(critical_ps.left_outer, color="red", label="")
plt.matplotlib.pyplot.axhline(critical_ps.left_inner, color="blue", label="")
plt.matplotlib.pyplot.axhline(critical_ps.right_inner, color="green", label="")
plt.matplotlib.pyplot.axhline(critical_ps.right_outer, color="red", label="")
plt.xlabel("Test statistic.")
plt.ylabel("$p$ value.")
plt.grid()


# p vs test statistic.
ps = plt.subplot(122)
plt.plot(cdf, bin_edges[1:], color="purple", linewidth=3)
# Highlight alpha space.
xnew = np.linspace(critical_ps.left_outer, critical_ps.right_outer, 100)
plt.plot(xnew, interp_func(xnew), linewidth=10, color="purple", alpha=0.3)
plt.xlabel("$p$ value.")
plt.ylabel("Test statistic.")
plt.grid()

plt.suptitle(filename)

plt.tight_layout()
plt.show()
