
#!/bin/bash
# Dump the results of many test suite runs 
# to a text file for analysis of whether
# the tests are being failed at a 5% rate.


for value in {1..10000}
do
    echo $value
    python   ent2_0.1.0.dump.py  >>  tests-dump.csv
done

echo All done
