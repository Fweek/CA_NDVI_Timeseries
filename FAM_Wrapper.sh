#!/usr/bin/env/python

input1=$1
input2=$2

python CSV_reformat.py $input1 $input2
python CSV_combine.py $input1
python CSV_classify.py $input1
python CSV_merge.py $input1
