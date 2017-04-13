!/bin/bash

echo 'Testing GEE performance using 10,100,1k,5k,1k and 15k'

time python FAM_L7_timeseries_MH.py Test_L7_timeseries 10 2016-01-01 2016-12-31 y > out_10.out 2> err_10.err

time python FAM_L7_timeseries_MH.py Test_L7_timeseries 100 2016-01-01 2016-12-31 y > out_100.out 2> err_100.err

time python FAM_L7_timeseries_MH.py Test_L7_timeseries 1000 2016-01-01 2016-12-31 y > out_1000.out 2> err_1000.err

time python FAM_L7_timeseries_MH.py Test_L7_timeseries 5000 2016-01-01 2016-12-31 y > out_5000.out 2> err_5000.err

time python FAM_L7_timeseries_MH.py Test_L7_timeseries 10000 2016-01-01 2016-12-31 y > out_10000.out 2> err_10000.err

time python FAM_L7_timeseries_MH.py Test_L7_timeseries 15000 2016-01-01 2016-12-31 y > out_15000.out 2> err_15000.err

echo 'Done'

