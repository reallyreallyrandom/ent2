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

import bz2
import enum
import lzma
import math
import os
import sys

import numpy as np
import scipy.stats
import statsmodels.api as sm
from scipy.stats import chisquare
from statsmodels.sandbox.stats.runs import runstest_1samp



ALPHA = 0.05     # TODO Are we happy with this?


# The alpha boundaries.
class critical_ps(float, enum.Enum):
    left_outer = ALPHA / 2
    left_inner = ALPHA
    right_inner = 1 - ALPHA
    right_outer = 1 - (ALPHA / 2)



# Lineprint formatting here.
def print_result(test_name, result, p_value):
    p = round(p_value, 4)
    print(test_name, ",     ", "p = ", p, ",", result)


# The filters are required for LZMA compression FORMAT_RAW format. 
lzma_filters = [
    {"id": lzma.FILTER_DELTA, "dist": 1},
    {"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME},
]   


# FIXME This makes random data internally, which makes it easier to test this code.
# =================================================================================
def make_samples(n):
    return os.urandom(n)



# Read in file.
# FIXME This is commented out to allow internal randomness generation.
# ====================================================================
# samples = []
# filename = str(sys.argv[1])
# with open(filename, "rb") as infile:
#     samples = infile.read()           # byte array.
#     # Check that the file is the correct length.
#     assert len(samples) == 512000
samples_byte = make_samples(512_000)     # FIXME Delete this line for production.
# 8 bit numpy array.
samples_np = np.array(bytearray(samples_byte),  dtype=np.uint8)       


# ===========================
# Arithmetic mean value test.
# ===========================


MEAN_MU = 127.5             # Theoretical.
MEAN_SIGMA = 73.90027064    # Theoretical.

sample_mu = np.mean(samples_np)
sigma_sample_mu = MEAN_SIGMA / math.sqrt(samples_np.size)

# Perform the test.
z_score = (sample_mu - MEAN_MU) / (sigma_sample_mu)
p_value = scipy.stats.norm.cdf(z_score)   # Has to be .cdf() to allow a 0.0 < p < 1.0 range.
if p_value > critical_ps.left_outer and p_value < critical_ps.right_outer:
    result = "PASS"
else:
    result = "FAIL"
print_result("Arithmetic mean value", result, p_value)


#=======================
# Pure compression test.
# ======================


bz2_compressed_size = len(bz2.compress(samples_byte, compresslevel=9))
lzma_compressed_size = len(lzma.compress(
    samples_byte, format=lzma.FORMAT_RAW, filters=lzma_filters))
compressed_size = bz2_compressed_size + lzma_compressed_size

# Perform the test.
if compressed_size > 1026683.41805254:     # Value confirmed for a 512 kB sample size.
    result = "PASS"
else:
    result = "FAIL"
print_result("Pure compression", result, -1)


#===================
# Min. entropy test.
# ==================


_, counts = np.unique(samples_np, return_counts=True)
max_prob = np.max(counts) / samples_np.size
Hmin = -math.log(max_prob, 2)

# Perform the test.
if Hmin > 7.88872605:     # Value confirmed for a 512 kB sample size.
    result = "PASS"
else:
    result = "FAIL"
print_result("Min. entropy",  result, -1)


#===============================
# Monte Carlo vaule for Pi test.
#===============================


PI_MU = math.pi                     # Theoretical.
PI_SIGMA = 0.0035255507775285868    # Value confirmed for a 512 kB sample size.

floaty_bytes = np.reshape(samples_np, [-1 , 8])
integral = np.empty([0], dtype=float)
for i in range(int(samples_np.size / 8)):
    f = (int.from_bytes(floaty_bytes[i], "little")) / (256**8 - 1)  
    y = math.sqrt(1 - (f * f))
    integral = np.append(integral, y)
pi = 4 * np.mean(integral)


# Perform the test.
z_score = (pi - PI_MU) / (PI_SIGMA)
p_value = scipy.stats.norm.cdf(z_score)   # Has to be .cdf() to allow a 0.0 < p < 1.0 range.
if p_value > critical_ps.left_outer and p_value < critical_ps.right_outer:
    result = "PASS"
else:
    result = "FAIL"
print_result("Monte Carlo value for Pi", result, p_value)


# ==========
# Runs test.
#===========


# Perform the test.
test_response = runstest_1samp(samples_np, correction=False)
p_value =  test_response[1]
if p_value > critical_ps.left_outer and p_value < critical_ps.right_outer:
    result = "PASS"
else:
    result = "FAIL"
print_result("Runs", result, p_value)


# ========================
# Serial correlation test.
# ========================
# TODO See https://github.com/reallyreallyrandom/ent2/issues/4


# Perform the test.
acf, qstat, p_values = sm.tsa.acf(samples_np, nlags=1, qstat=True)
p_value = p_values[0]        # The p-values associated with the Q-statistics for lags 1, 2, …, nlags (excludes lag zero). Returned if q_stat is True.
if p_value < critical_ps.right_inner:
    result = "PASS"
else:
    result = "FAIL"
print_result("Serial correlation", result, p_value)


# =============================
# Chi square distribution test.
# =============================
# TODO See https://github.com/reallyreallyrandom/ent2/issues/7
# And https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html

# Perform the test.
_, counts = np.unique(samples_np, return_counts=True)
assert counts.size == 256        # Connected to the TODO above.
test_response = chisquare(counts)
p_value = test_response.pvalue
if p_value > critical_ps.left_outer and p_value < critical_ps.right_outer:
    result = "PASS"
else:
    result = "FAIL"
print_result("Chi square distribution", result, p_value)


# =========================
# Excursion from mean test.
# =========================


sample_mu = np.mean(samples_np)
cumsum = np.cumsum(samples_np)
excursions =  np.empty(samples_np.size, dtype=float)
for i in range(samples_np.size):
    running_mean = sample_mu * (i + 1)
    excursion = abs(cumsum[i] - running_mean)
    excursions[i] = excursion
max_excursion =  np.max(excursions)    # Do this rather than .append for speed.

# Perform the test.
if max_excursion > 25416.31879631 and max_excursion < 78081.5639194:   # Values confirmed for a 512 kB sample size.
    result = "PASS"
else:
    result = "FAIL"
print_result("Excursion from mean", result, -1)


# ================================
# Permuted compression ratio test.
# ================================


PERM_MU = 1.0                         # Theoretical.
PERM_SIGMA = 9.056102826054197e-05    # Value confirmed for a 512 kB sample size.

rng = np.random.default_rng()    # PCG XSL RR 128/64 random number generator.
samples_byte = bytearray(make_samples(samples_np.size))
bz2_compressed_size = len(bz2.compress(samples_byte, compresslevel=9))
lzma_compressed_size = len(lzma.compress(
    samples_byte, format=lzma.FORMAT_RAW, filters=lzma_filters))

rng.shuffle(samples_byte)

bz2_compressed_shuffled_size = len(bz2.compress(
    samples_byte, compresslevel=9))
lzma_compressed_shuffled_size = len(lzma.compress(
    samples_byte, format=lzma.FORMAT_RAW, filters=lzma_filters))
ratio = (bz2_compressed_shuffled_size + lzma_compressed_shuffled_size) / \
    (bz2_compressed_size + lzma_compressed_size)

# Perform the test.
z_score = (ratio - PERM_MU) / (PERM_SIGMA)
p_value = scipy.stats.norm.cdf(z_score)   # Has to be .cdf() to allow a 0.0 < p < 1.0 range.
if p_value < critical_ps.right_inner:
    result = "PASS"
else:
    result = "FAIL"
print_result("Permuted compression ratio", result, p_value)
