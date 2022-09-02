"""
This program checks whether there is any noticeable error 
in converting random 8 bit bytes to a float on [0, 1].
It seems to be adequate for ent_v2.
"""

# spell-checker: disable #


import matplotlib.pyplot as plt
import random
import numpy as np


NO_POINTS = 100_000
MAX_INT = 2**32 - 1


def make_samples(n):
    for _ in range(n):
        yield random.getrandbits(8)


def make_float():
    f = (int.from_bytes(make_samples(4), "little")) / (MAX_INT)  
    return f


x_values = np.empty([0], dtype=float)
for i in range(NO_POINTS):
    floatie = make_float()
    x_values = np.append(x_values, floatie)


y_values = np.empty([0], dtype=float)
for i in range(NO_POINTS):
    floatie = make_float()
    y_values = np.append(y_values, floatie)


plt.scatter(x_values, y_values)
plt.show()
