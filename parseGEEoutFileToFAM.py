import sys,os,csv,datetime,string
import numpy

#test file
fn = '23means.csv'

#Open the file
fPtr = open(fn)
if fPtr is None:
  print "Error opening %s " % fn
  sys.exit(1)

#Read in the file using csv
lines = csv.reader(fPtr)

fPtr = None


#Create container for input
input = []

#Keep only columns we want SIMS ID, Date, and NDVI
for l in lines:
   input.append((l[2],l[3],l[7]))

#Remove header
input = input[1::]
#print input

#Create container for temp output
tempOut = []
    
#How many unique ids do we have?
simsIds = [i[0] for i in input]
yDim = len(numpy.unique(simsIds))+1
print "Number of unique sims ids %d" % yDim
#We have 5 columns + 46 timesteps
xDim = 51

finalOutput = numpy.ones((yDim,51)) * -9999.0

#Changing date
for l in input:
        #Grab only date column
        dtStr = l[1]
        #Parse out year, month, day. Ugly code but need to get this moving...
        yr, mm, dd = dtStr[0:4], dtStr[5:7], dtStr[8:10]
        #print yr, mm, dd #Debug
        #Reformat date
        dtNum = (datetime.datetime(int(yr), int(mm), int(dd)) - datetime.datetime(1980, 1, 1)).days
        #print dtNum #Debug

        #Replace {nd=null} with -9999
        ndvi = l[2]
        # print ndvi #Debug
        ndvi2 = string.replace(ndvi, '{nd=null}', '-9999')
        # print ndvi2 #Debug

        tempOut.append((float(l[0]),dtNum,ndvi2))

print tempOut[0]

  

tempOut.sort()

#Find how many unique ids do we have?
simsIds = [i[0] for i in tempOut]
allDates = [i[1] for i in tempOut] 
 
#print simsIds
 
#Get all unique dates and count them
#uniqueDT =  numpy.unique(allDates)
uniqueIds =  numpy.unique(simsIds)
print uniqueIds.shape

#Fill in the date header based on year, assuming we're looking at 2016 data
tStart = (datetime.datetime(2016,01,1) - datetime.datetime(1980, 1, 1)).days
tEnd = (datetime.datetime(2016,12,31) - datetime.datetime(1980, 1, 1)).days
indx = 0
for i in range(tStart,tEnd,8):
  finalOutput[0,indx] = i
  indx += 1


finalOutput[1:yDim,0] = uniqueIds
print finalOutput[0]
    
for row in range(1,yDim):
      simsId = finalOutput[row,0]
      for j in tempOut:
        tempOutId = float(j[0])
        #print simsId,tempOutId
        if simsId == tempOutId:
           #Check the date and add to column
           print "IDs match",simsId,tempOutId
           date = j[1]
           ndvi = j[2]
           print date,ndvi
           #which column?
           for col in range(5,51):
             dateTemp = int(finalOutput[0,col])
             #print dateTemp,date
             if dateTemp == date:
               #TODO: Most dates won't match since the overpass can fall anywhere in between the 8 day period
               #      Have to account for this to make the code work

               print "Dates match"
               ndvi = numpy.random()
               print row,col,ndvi
               #Have to clean up ndvi from nd=... and turn it into a number
               finalOupt[row,col] = ndvi    
   
outStrFn = 'outputFile_'
numpy.savetxt(outStrFn+'_avgs.csv', finalOutput, delimiter=",",fmt='%.3f')
