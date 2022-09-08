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


For generating numpy array data to model the simulated test results from 
our JSON calibration data.
"""

# spell-checker: disable #


from cProfile import label
import enum
import json
import math
import sys
from turtle import color

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

 
NO_EXPORT_POINTS = 15   # This is rather important.
ALPHA = 0.05


# The alpha boundries.
class critical_ps(float, enum.Enum):
    left_outer = ALPHA / 2
    left_inner = ALPHA
    right_inner = 1 - ALPHA
    right_outer = 1 - (ALPHA / 2)


# The alpha boundries for interpolation.
# Allow some headroom mutlipliers for interpolation (5%)
class interpolation_ps(float, enum.Enum):
    left_outer = 0.02
    right_outer = 0.98


# Read in calibration file.
all_statistics = []
# filename = str(sys.argv[1])
filename = "/mnt/bazinga/ent2/calibration/entropy/entropy-512kB.json"
# filename = "/mnt/bazinga/ent2/calibration/excursion/excursion-512kB.json"
# filename = "/mnt/bazinga/ent2/calibration/compression/compression-512kB.json"
with open(filename, "rb") as infile:
    all_statistics = json.load(infile)
    statistics = np.array(all_statistics, dtype=float)


# Decide on how many histogram bins we want.
# Use the square root of the sample size method.
no_bins = round(math.sqrt(statistics.size))


# Obtain the histogram and other statistics.
hist, bin_edges = np.histogram(statistics, bins=no_bins)
pdf = hist / np.sum(hist)
cdf = np.cumsum(pdf)


# Reverse interpolation to find cut offs for export point curve fit.
criticals = np.array([interpolation_ps.left_outer,
                      interpolation_ps.right_outer])
reverse_interpolation_function = interp1d(cdf, bin_edges[1:], kind="linear")
critical_statistics = reverse_interpolation_function(criticals)


# Interpolation function for export points.
points_interpolation_function = interp1d(bin_edges[1:], cdf, kind="cubic")
# first_interpolation_function = UnivariateSpline(bin_edges[1:], cdf, k = 5, s=0.001)    # s is a smoothing factor.


# Interpolate N export points for 2nd curve fit.
points_x = np.linspace(critical_statistics[0], critical_statistics[1], NO_EXPORT_POINTS)
points_y = points_interpolation_function(points_x)


# Print out histogram arrays to fit second curve from.
# These points to go into the ent2 source code.
np.set_printoptions(threshold=sys.maxsize)
print("x values")
print(points_x.tolist())
print("\ny values")
print(points_y.tolist())


# Fitted export points..
fig = plt.figure()
first = plt.subplot(121)
plt.plot(bin_edges[1:], cdf, color="purple", linewidth=6, label="Raw samples", alpha=0.3)    # Raw data.
plt.scatter(points_x, points_y, color="purple", marker="o", label="Export points")       # Interpolated data.
plt.matplotlib.pyplot.axhline(critical_ps.left_outer, color="red", label="")
plt.matplotlib.pyplot.axhline(critical_ps.left_inner, color="blue", label="")
plt.matplotlib.pyplot.axhline(critical_ps.right_inner, color="green", label="")
plt.matplotlib.pyplot.axhline(critical_ps.right_outer, color="red", label="")
plt.xlabel("Test statistic.")
plt.ylabel("$p$ value.")

plt.suptitle(filename)
plt.legend()
plt.grid()


# This is the function that makes the calibration cdf in ent2.
second_interpolation_function = interp1d(points_x, points_y, kind="cubic")
second_x = np.linspace(np.min(points_x), np.max(points_x), 100)
second_y = second_interpolation_function(second_x)


# 2nd curve fit derived from first.
ps = plt.subplot(122)
plt.plot(bin_edges[1:], cdf, color="purple", linewidth=6, label="Raw samples", alpha=0.3)    # Raw data.
plt.plot(second_x, second_y, color="purple", linewidth=2, label="Points curve fit")   
plt.matplotlib.pyplot.axhline(critical_ps.left_outer, color="red", label="")
plt.matplotlib.pyplot.axhline(critical_ps.left_inner, color="blue", label="")
plt.matplotlib.pyplot.axhline(critical_ps.right_inner, color="green", label="")
plt.matplotlib.pyplot.axhline(critical_ps.right_outer, color="red", label="")
plt.xlabel("Test statistic.")
plt.ylabel("$p$ value.")

plt.legend()
plt.grid()

plt.show()

