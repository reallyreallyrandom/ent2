"""
Implementation of the flawed pseudorandom number generating algorithm RANDU.
Curtesy of https://github.com/ptomato/randu.
See, for more information: http://en.wikipedia.org/wiki/RANDU

    
A 512 kB file fails all of the `ent` tests, as:-


----------------------------------------------
Entropy = 7.827023 bits per byte.

Optimum compression would reduce the size
of this 512000 byte file by 2 percent.

Chi square distribution for 512000 samples is 128779.79, and randomly
would exceed this value less than 0.01 percent of the times.

Arithmetic mean value of data bytes is 112.1283 (127.5 = random).
Monte Carlo value for Pi is 3.467451045 (error 10.37 percent).
Serial correlation coefficient is -0.052822 (totally uncorrelated = 0.0).
-----------------------------------------------
"""

# spell-checker: disable #


import random


FILENAME = "/tmp/randu.bin"
SIZE = 128_000    # x4 = 512 kB


class Randu(random.Random):
    def __init__(self, seed=[]):
        try:
            self.seed(seed)
        except TypeError:  # not hashable
            self._state = 1

    def seed(self, x):
        self._state = hash(x) % 2**31

    def getstate(self):
        return self._state

    def setstate(self, state):
        self._state = state

    def random(self):
        self._state = (65539 * self._state) % 2**31
        # / float(0x80000000)    This was from Philip Chimento's original.
        return self._state

    @staticmethod
    def check():
        """
        Check against Wikipedia's listed sequence of numbers (start and end of
        the sequence with initial seed 1):
        1, 65539, 393225, 1769499, 7077969, 26542323, ..., 2141591611,
        388843697, 238606867, 79531577, 477211307, 1
        """
        randu = Randu(2141591611)
        actual = []
        for x in range(11):
            actual.append(randu.getstate())
            randu.random()
        assert actual == [2141591611, 388843697, 238606867, 79531577, 477211307,
                          1, 65539, 393225, 1769499, 7077969, 26542323]


Randu.check()
randu = Randu(5)  # Odd seeds only!

with open(FILENAME, 'wb') as f:
    for i in range(SIZE):
        number = randu.random()
        # print(number)
        f.write(number.to_bytes(4, byteorder='little'))
