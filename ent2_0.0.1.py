"""
                        =============
                        =============
                            ent2. 
                        =============
                        =============

LICENSE:

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

"""

# spell-checker: disable #

import enum
import bz2
import lzma
import math
import sys
import numpy as np
import scipy.stats


ALPHA = 0.05


# The alpha boundries.
class critical_ps(float, enum.Enum):
    left_outer = ALPHA / 2
    left_inner = ALPHA
    right_inner = 1 - ALPHA
    right_outer = 1 - (ALPHA / 2)



# Lineprint formatting here.
def print_result(test_name, result, p_value):
    v = round(p_value, 4)
    print(test_name, ",     ", "p = ", v, ",", result)



# Read in file.
samples = []
filename = str(sys.argv[1])
with open(filename, "rb") as infile:
    samples = infile.read()           # byte array.
    # Check that the file is the correct length.
    assert len(samples) == 512000

# 8 bit numpy array.
samples_np = np.array(bytearray(samples),  dtype=np.uint8)       


# =====================
# Arithmetic mean test.
# =====================


MU = 127.5                     # Theoretical.
SIGMA_UNIFORM = 73.90027064    # Theoretical.
sample_mu = np.mean(samples_np)
sigma_sample_mu = SIGMA_UNIFORM / math.sqrt(samples_np.size)

# Perform the test.
z_score = (sample_mu - MU) / (sigma_sample_mu)
p_value = scipy.stats.norm.sf(z_score)   
if z_score > 0:
    p_value += 0.5
if p_value > critical_ps.left_inner and p_value < critical_ps.right_inner:
    result = "PASS"
else:
    result = "FAIL"
print_result("Arithmetic mean", result, p_value)


#=======================
# Pure compression test.
# ======================


# The filters are required for FORMAT_RAW format.
lzma_filters = [
    {"id": lzma.FILTER_DELTA, "dist": 1},
    {"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME},
]

bz2_compressed_size = len(bz2.compress(samples, compresslevel=9))
lzma_compressed_size = len(lzma.compress(
    samples, format=lzma.FORMAT_RAW, filters=lzma_filters))
compressed_size = bz2_compressed_size + lzma_compressed_size

# Perform the test.
if compressed_size >= 1_026_684:     # Value confirmed for 512 kB sample size.
    result = "PASS"
else:
    result = "FAIL"
print_result("Pure compression", result, -1)


#===================
# Min. entropy test.
# ==================


_, counts = np.unique(samples_np, return_counts=True)
max_prob = np.max(counts) / samples_np.size
minimum = -math.log(max_prob, 2)

# Perform the test.
if minimum > 7.88882911:     # Value confirmed for 512 kB sample size.
    result = "PASS"
else:
    result = "FAIL"
print_result("Min. entropy",  result, -1)


#================
# Monte Carlo Pi.
#================


floaty_bytes = np.reshape(samples_np, [128_000, 4])
integral = np.empty([0], dtype=float)
for i in range(128_000):
    f = (int.from_bytes(floaty_bytes[i], "little")) / (2**32 - 1)  
    y = math.sqrt(1 - (f * f))
    integral = np.append(integral, y)
pi = 4 * np.mean(integral)

# Perform the test.
if pi > 3.13666963 and pi < 3.14649241:     # Values confirmed for 512 kB sample size.
    result = "PASS"
else:
    result = "FAIL"
print_result("Monte Carlo pi",  result, -1)