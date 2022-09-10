"""
                        =============
                        =============
                            ent2. 
                        =============
                        =============

MIT License

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
import lzma
import math
import os
import sys
from enum import Enum

import numpy as np
import scipy.stats
import statsmodels.api as sm
from scipy.stats import chisquare
from statsmodels.sandbox.stats.runs import runstest_1samp
from scipy.interpolate import interp1d


# This is the calibration data for some of the tests.
# It's a def so that I can code fold it in my IDE.
def hidden_data():
    global entropy_512_x 
    entropy_512_x = \
        [7.88156, 7.88508, 7.8886, 7.89212, 7.89564, 7.89916, 7.90268, 7.9062, 7.90972,
        7.91324, 7.91676, 7.92028, 7.92379, 7.92731, 7.93083]
    global entropy_512_y 
    entropy_512_y = \
        [0.01992, 0.03309, 0.0488, 0.07243, 0.11214, 0.15585, 0.2278, 0.31783, 0.41298,
        0.54992, 0.66945, 0.77759, 0.87863, 0.94333, 0.97985]


    global compression_512_x
    compression_512_x = \
        [1026698.85226, 1026718.41452, 1026737.97678, 1026757.53905, 1026777.10131, 
        1026796.66357, 1026816.22583, 1026835.7881, 1026855.35036, 1026874.91262, 
        1026894.47489, 1026914.03715, 1026933.59941, 1026953.16168, 1026972.72394]
    global compression_512_y 
    compression_512_y = \
        [0.01999, 0.03041, 0.04642, 0.07446, 0.11734, 0.18638, 0.27715, 0.38938, 
        0.50839, 0.63119, 0.74003, 0.83449, 0.9037, 0.95095, 0.98013]


    global excursion_512_x 
    excursion_512_x = \
        [24836.93383, 28783.02858, 32729.12332, 36675.21807, 40621.31281, 44567.40755, 
        48513.5023, 52459.59704, 56405.69179, 60351.78653, 64297.88128, 68243.97602, 
        72190.07076, 76136.16551, 80082.26025]
    global excursion_512_y 
    excursion_512_y = \
        [0.01999, 0.0712, 0.16181, 0.27988, 0.40554, 0.5254, 0.63327, 0.72418,
        0.79767, 0.85428, 0.89798, 0.93031, 0.95241, 0.96892, 0.98]


NO_IID_TESTS = 3
NO_RANDOMNESS_TESTS = 6
NO_SAMPLES = 512000   # Fixed for now.
P_DECIMALS = 3    # p value precision.
H_DECIMALS = 2    # Hmin precision.
ALPHA = 0.05     # TODO Are we happy with this?

# The alpha boundaries.


class critical_ps(float, Enum):
    left_outer = ALPHA / 2
    left_inner = ALPHA
    right_inner = 1 - ALPHA
    right_outer = 1 - (ALPHA / 2)


# Interpolate a p value from calibration data above.
# We also have to allow for interpolation values outside of
# the fitted function's domain.
def interpolate_p_value(points_x, points_y, test_statistic):
    if test_statistic <= np.min(points_x):
        p_value = 0.0
    elif test_statistic >= np.max(points_x):
        p_value = 1.0
    else:
        interpolation_function = interp1d(points_x, points_y, kind="cubic")
        p_value = interpolation_function(test_statistic)   # Interpolated value is a 0 dimension array.
    return p_value


# Lineprint formatting here.
def print_result(test_name, result, p_value):
    p = np.around(p_value, decimals=P_DECIMALS)
    # TODO Pretty print. Add red/green colours to PASS/FAIL test?
    print(test_name.ljust(28), "p =", str(p).ljust(7), str(result) + ".")


# Read in samples file.
# If no filename is supplied, samples will be generated internally.
# TODO Add a usage text.
# ====================================================================
hidden_data()
iid_pass_counter = 0
randomness_pass_counter = 0

samples_byte = []
if len(sys.argv) > 1:         # Check is a filename has been provided.
    try:
        filename = str(sys.argv[1])
        with open(filename, "rb") as infile:
            samples_byte = bytearray(infile.read())    # byte array.
            # FIXME Check that the file is the correct length.
            assert len(samples_byte) == NO_SAMPLES
            print("Testing", filename + ".\n")
    except:
        print("Could not load", filename)
        raise SystemExit(1)
else:
    # No filename provided, so make internal samples.
    samples_byte = bytearray(os.urandom(NO_SAMPLES))
    print("Testing internal cryptographic RNG.\n")
samples_np = np.array(samples_byte,  dtype=np.uint8)   # 8 bit numpy array.



# ================================
# Permuted compression ratio test.
# ================================


PERM_MU = 1.0                         # Theoretical.
PERM_SIGMA = 9.082622798203179e-05    # Value confirmed for a 512 kB sample size.

rng = np.random.default_rng()    # PCG XSL RR 128/64 random number generator.
bz2_compressed_size = len(bz2.compress(samples_byte))
lzma_compressed_size = len(lzma.compress(samples_byte))
compressed_size = bz2_compressed_size + lzma_compressed_size

rng.shuffle(samples_byte)

bz2_compressed_shuffled_size = len(bz2.compress(samples_byte))
lzma_compressed_shuffled_size = len(lzma.compress(samples_byte))
compressed_shuffled_size = bz2_compressed_shuffled_size + lzma_compressed_shuffled_size
perm_ratio = compressed_shuffled_size / compressed_size

# Perform the test.
z_score = (perm_ratio - PERM_MU) / (PERM_SIGMA)
# Has to be .cdf() to allow a 0.0 < p < 1.0 range.
p_value = scipy.stats.norm.cdf(z_score)
if p_value < critical_ps.right_inner:
    result = "PASS"
    iid_pass_counter += 1
else:
    result = "FAIL"
print_result("Permuted compression ratio", result, p_value)



# ==========
# Runs test.
# ===========


# Perform the test.
test_response = runstest_1samp(samples_np, correction=False)
p_value = test_response[1]
if critical_ps.left_outer < p_value and p_value < critical_ps.right_outer:
    result = "PASS"
    iid_pass_counter += 1
else:
    result = "FAIL"
print_result("Runs", result, p_value)



# ========================
# Serial correlation test.
# ========================
# TODO See https://github.com/reallyreallyrandom/ent2/issues/4


# Perform the test.
acf, qstat, p_values = sm.tsa.acf(samples_np, nlags=1, qstat=True)
# The p-values associated with the Q-statistics for lags 1, 2, …, nlags (excludes lag zero). Returned if q_stat is True.
p_value = p_values[0]
if critical_ps.left_outer < p_value and p_value < critical_ps.right_outer:
    result = "PASS"
    iid_pass_counter += 1
else:
    result = "FAIL"
print_result("Serial correlation", result, p_value)



# ============
# IID decision
#=============
print()
if iid_pass_counter == NO_IID_TESTS:
    print("SAMPLES ARE IID.")
else:
    print("SAMPLES ARE NOT IID.")
print()



# =======================
# Pure compression test.
# ======================


# Perform the test.
# Value confirmed for a 512 kB sample size.
p_value = interpolate_p_value(compression_512_x, compression_512_y, compressed_size)   # We already have compressed_size.

# Perform the test.
if critical_ps.left_inner < p_value:
    result = "PASS"
    randomness_pass_counter += 1
else:
    result = "FAIL"
print_result("Pure compression", result, p_value)



# =============================
# Chi square distribution test.
# =============================
# TODO See https://github.com/reallyreallyrandom/ent2/issues/7
# And https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html

# Perform the test.
_, counts = np.unique(samples_np, return_counts=True)
# assert counts.size == 256        # Connected to the TODO above.
test_response = chisquare(counts)
p_value = test_response.pvalue
if critical_ps.left_outer < p_value and p_value < critical_ps.right_outer:
    result = "PASS"
    randomness_pass_counter += 1
else:
    result = "FAIL"
print_result("Chi square distribution", result, p_value)



# ===========================
# Arithmetic mean value test.
# ===========================


UNIFORM_MU = 127.5             # Theoretical.
UNIFORM_SIGMA = 73.90027064    # Theoretical.

sample_mu = np.mean(samples_np)
sample_mu_sigma = UNIFORM_SIGMA / math.sqrt(samples_np.size)

# Perform the test.
z_score = (sample_mu - UNIFORM_MU) / (sample_mu_sigma)
# Has to be .cdf() to allow a 0.0 < p < 1.0 range.
p_value = scipy.stats.norm.cdf(z_score)
if critical_ps.left_outer < p_value and p_value < critical_ps.right_outer:
    result = "PASS"
    randomness_pass_counter += 1
else:
    result = "FAIL"
print_result("Arithmetic mean value", result, p_value)



# ===============================
# Monte Carlo value for Pi test.
# ===============================


PI_MU = math.pi                     # Theoretical.
PI_SIGMA = 0.0035255507775285868    # Value confirmed for a 512 kB sample size.

floaty_bytes = np.reshape(samples_np, [-1, 8])
integral = np.empty([0], dtype=float)
for i in range(int(samples_np.size / 8)):
    f = (int.from_bytes(floaty_bytes[i], "little")) / (256**8 - 1)
    y = math.sqrt(1 - (f * f))
    integral = np.append(integral, y)
pi = 4 * np.mean(integral)

# Perform the test.
z_score = (pi - PI_MU) / (PI_SIGMA)
# Has to be .cdf() to allow a 0.0 < p < 1.0 range.
p_value = scipy.stats.norm.cdf(z_score)
if critical_ps.left_outer < p_value and p_value < critical_ps.right_outer:
    result = "PASS"
    randomness_pass_counter += 1
else:
    result = "FAIL"
print_result("Monte Carlo value for Pi", result, p_value)



# =========================
# Excursion from mean test.
# =========================


sample_mu = np.mean(samples_np)
cumsum = np.cumsum(samples_np)
excursions = np.empty(samples_np.size, dtype=float)
for i in range(samples_np.size):
    running_mean = sample_mu * (i + 1)
    excursion = abs(cumsum[i] - running_mean)
    excursions[i] = excursion
max_excursion = np.max(excursions)    # Do this rather than .append for speed.

# Perform the test.
p_value = interpolate_p_value(excursion_512_x, excursion_512_y, max_excursion)
if critical_ps.left_outer < p_value and p_value < critical_ps.right_outer:
    result = "PASS"
    randomness_pass_counter += 1
else:
    result = "FAIL"
print_result("Excursion from mean", result, p_value)



# ===================
# Min. entropy test.
# ==================


_, counts = np.unique(samples_np, return_counts=True)
max_prob = np.max(counts) / samples_np.size
Hmin = -math.log(max_prob, 2)

# Calculate p value
p_value = interpolate_p_value(entropy_512_x, entropy_512_y, Hmin)

# Perform the test.
if critical_ps.left_inner < p_value:
    result = "PASS"
    randomness_pass_counter += 1
else:
    result = "FAIL"
print_result("Min. entropy", result, p_value)



# Entropy determination, with some truncation on the safe side.
# Remember we're erring on the side of security.
hmin = math.trunc(Hmin * 10 ** H_DECIMALS) / 10 ** H_DECIMALS
print()
if iid_pass_counter == NO_IID_TESTS:
    print("Min. entropy =", hmin, "bits per byte.")
else:
    print("Min. entropy <", hmin, "bits per byte.")
print()


# ===================
# Randomness decision
#====================
if iid_pass_counter == NO_IID_TESTS and randomness_pass_counter == NO_RANDOMNESS_TESTS:
    print("SAMPLES SUITABLE FOR CRYPTOGRAPHY @ α =", str(ALPHA) + ".")
else:
    print("SAMPLES UNSUITABLE FOR CRYPTOGRAPHY @ α =", str(ALPHA) + ".")
print()