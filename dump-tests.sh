
#!/bin/bash
# Dump the results of many test suite runs 
# to a text file for analysis of whether
# the tests are being failed at a 5% rate.


for value in {1..10000}
do
    echo $value
    python   ent2_0.0.1.py  >>  tests-dump.csv
done

echo All done
