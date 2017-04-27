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

output = []

#Remove header
input = input[1::]

for l in input:
  #Get the date and change it from YYYY-MM-DD to 
  dtStr = l[1]
  #Ugly code but need to get this moving...
  yr,mm,dd = dtStr[0:4],dtStr[5:7],dtStr[8::]
  #Debug
  print yr,mm,dd
  dtNum = (datetime.datetime(int(yr),int(mm),int(dd)) - datetime.datetime(1980, 1, 1)).days
  #Debug
  print dtNum

  #clean up the ndvi column, need to get rid of nulls and 'nd' and just get the numbers


  #Push data to output list
