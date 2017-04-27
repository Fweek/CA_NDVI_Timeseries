import sys,os,csv,datetime

#Test file
fn = '23means.csv'

#Open the file
fPtr = open(fn)
if fPtr is None:
  print "Error opening %s " % fn
  sys.exit(1)

#Read in the file using csv
lines = csv.reader(fPtr)

fPtr = None

#Changed this from output to input 
input = []

#Cleaning up the input
#Read in just the columns we want to process
for l in lines:
  input.append((l[2],l[3],l[5],l[7]))
