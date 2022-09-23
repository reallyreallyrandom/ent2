"""
Checks to see if the lzma algorithm is actually a file archiver and suffers
from the thing that happens in Python.

Yes it does in that the output stream is 'fitted' into 4 byte units. Also
the length of the output does not vary for the pseudo random data generated
below. So the length of compressed permuted samples can vary by 3 bytes and 
not be noticed external to the algorithm.

 3 bytes out of a target 512,000 is only 0.00059% error though!

 But, if you use the FORMAT_RAW option with a filter chain, it does not!
 See the code below.
"""


# spell-checker: disable #

import bz2
import lzma
import os
import random


def make_samples(n):
    return os.urandom(n)


my_filters = [
    {"id": lzma.FILTER_DELTA, "dist": 1},
    {"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME},
]


for i in range(20):
    samples = bytearray(make_samples(100_000))
    bz2_compressed_size = len(bz2.compress(samples, compresslevel=9))
    lzma_compressed_size = len(lzma.compress(samples, format=lzma.FORMAT_RAW, filters=my_filters))
    print(bz2_compressed_size, lzma_compressed_size)


for i in range(20):
    samples = bytearray(make_samples(100_000))
    bz2_compressed_size = len(bz2.compress(samples))
    lzma_compressed_size = len(lzma.compress(samples))
    print(bz2_compressed_size, lzma_compressed_size)

