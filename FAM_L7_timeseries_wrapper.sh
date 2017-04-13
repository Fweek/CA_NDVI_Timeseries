#!/bin/bash

echo 'Testing GEE performance using 10,100,1k,5k,1k and 15k'

mkdir outLogs

time python FAM_L7_timeseries.py Test_L7_timeseries 10 2016-01-01 2016-12-31 n > ./outLogs/out_10.out 2>&1

time python FAM_L7_timeseries.py Test_L7_timeseries 100 2016-01-01 2016-12-31 n > ./outLogs/out_100.out 2>&1

time python FAM_L7_timeseries.py Test_L7_timeseries 1000 2016-01-01 2016-12-31 n > ./outLogs/out_1000.out 2>&1

time python FAM_L7_timeseries.py Test_L7_timeseries 5000 2016-01-01 2016-12-31 n > ./outLogs/out_5000.out 2>&1

time python FAM_L7_timeseries.py Test_L7_timeseries 10000 2016-01-01 2016-12-31 n > ./outLogs/out_10000.out 2>&1

time python FAM_L7_timeseries.py Test_L7_timeseries 15000 2016-01-01 2016-12-31 n > ./outLogs/out_15000.out 2>&1

echo 'Done'
