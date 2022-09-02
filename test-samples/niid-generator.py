""" 
This generates a correlated file,
with a relaxation period of 3.
There will be a slight +/- half bit pseudo jitter on the correlated
bytes due to the round() function. 
"""


import random

CORRELATION = 0.5


with open('/tmp/niid3.bin', 'wb') as f:
    for i in range(170_667):      # ~512 kB
        r = random.getrandbits(8)
        x0 = r
        x1 = round(x0 * CORRELATION)  # 67% correlation
        x2 = round(x1 * CORRELATION)  # 33% correlation
        f.write(x0.to_bytes(1, byteorder='big'))
        f.write(x1.to_bytes(1, byteorder='big'))
        f.write(x2.to_bytes(1, byteorder='big'))

