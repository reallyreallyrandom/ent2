"""
This generates a perfect iid file from /dev/urandom, 
but only n (n < 8) bits deep!
"""


import secrets as s

EN = 7

with open('iid-7bits.bin', 'wb') as f:
    for i in range(512_000):
        r = s.randbits(EN)      
        f.write(r.to_bytes(1, byteorder='big'))

