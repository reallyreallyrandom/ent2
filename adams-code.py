
'''
Run with filename as first argument.
e.g python3 entv2.py myfile.rand
'''

import scipy.stats
import statsmodels.api as sm
import sys

#def ljungbox_correlation_test(b):
#  res = sm.stats.diagnostic.acorr_ljungbox(list(b))
  

def lagrange_correlation_test(b):
  res = sm.stats.diagnostic.acorr_lm(list(b))
  return res[1]

  print(res[0])
  print(res[1])
  print(res[2])
  print(res[3])

def arithmetic_sum(b):
    s = sum(b)
    n = len(b)
    mean = s / n

    # parameters of dist
    mu = 127.5
    sigma = ( (256**2 - 1)/12 ) ** .5

    # get p-value
    z_score = (mean - mu) / (sigma / n**.5)
    p_value = scipy.stats.norm.sf(z_score)

    return mean, p_value, z_score

def uniform_test(b, N=int(1e7), bytes_per_num=4):
    
    # get uniform numbers from bytes
    uniform_nums = []
    for i in range(min(N, len(b) // bytes_per_num)):
        curr_bytes = b[i * bytes_per_num : (i+1) * bytes_per_num]
        u = int.from_bytes(curr_bytes, byteorder='little') / (256**bytes_per_num)   # Should there be a -1 in this divisor?
        uniform_nums.append(u)

    # do uniformity test
    _, p_value = scipy.stats.kstest(uniform_nums, scipy.stats.uniform().cdf)
    return p_value

if __name__ == '__main__':
  # read in file
  inf = sys.argv[1]
  f = open(inf, 'rb')
  b = f.read()
  f.close()

  # do arithmetic sum
  mean, p_value, z_score = arithmetic_sum(b)
  print('--- arithmetic mean test ---')
  print('total bytes: {}'.format(len(b)))
  print('arithmetic mean: {}'.format(round(mean, 6)))
  print('p-value: {}'.format(round(p_value, 6)))
  print('z-score: {}'.format(round(z_score, 6)))


  # do uniform
  p_value = uniform_test(b)
  print()
  print('--- uniform numbers in unit interval test with 32-bit numbers ---')
  print('uniform numbers in [0, 1) p-value: {}'.format(round(p_value, 4)))

  # do uniform
  p_value = uniform_test(b, bytes_per_num=8)
  print()
  print('--- uniform numbers in unit interval test with 64-bit numbers ---')
  print('uniform numbers in [0, 1) p-value: {}'.format(round(p_value, 4)))

  # do lagrange correlation
  p_value = lagrange_correlation_test(b)
  print()
  print('--- Lagrange multiplier test for auto-correlation ---')
  print('p-value: {}'.format(round(p_value, 6)))

  # do Ljung-box test 
  # haven't gotten this to work yet
  #print('--- Ljung Box test for autocorrelation ---')
  #p_value = ljungbox_correlation_test(b)






