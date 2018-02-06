#!/usr/bin/env/python
#This is a wrapper bash script that runs the following four Python scripts in sequential order. 
#This wrapper script requires two parameters to run: the directory location of the RAW input files and the year of the RAW input files.

input1=$1 #Parameter 1: directory location of the RAW input files Example: C:\Users\Michael\Desktop\FAM
input2=$2 #Parameter 2: year of the RAW input files. Example: 2013

python CSV_reformat.py $input1 $input2
python CSV_combine.py $input1
python CSV_classify.py $input1
python CSV_merge.py $input1
