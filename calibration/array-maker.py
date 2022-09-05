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


import enum
import json
import math
import sys

import numpy as np


# Read in calibration file.
all_statistics = []
# filename = str(sys.argv[1])
filename = "/mnt/bazinga/ent2/calibration/entropy/entropy-512kB.json"
with open(filename, "rb") as infile:
    all_statistics = json.load(infile)
    statistics = np.array(all_statistics, dtype=float)


# Decide on how many histogram bins we want.
# Use the square root of the sample size method.
no_bins = round(math.sqrt(statistics.size))


# Obtain the mass distribution.
hist, bin_edges = np.histogram(statistics, bins=no_bins)
pdf = hist / np.sum(hist)
print(filename)
print(pdf)
print(bin_edges)


