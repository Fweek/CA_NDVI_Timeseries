import sys,os,csv,datetime,string
import numpy

#Set working directory
os.chdir('C:\Users\Michael\Desktop\CSVprep')

#Make a new directory for the output files if it does not already exist
if not os.path.exists('Output'):
    os.makedirs('Output',)

# Loop through every file in the current working directory.
for csvFilename in os.listdir('.'):
    if not csvFilename.endswith('.csv'):
        continue # skip non-csv files

    print('Modifying ' + csvFilename + '...')

    #Open the file
    fPtr = open(csvFilename)
    if fPtr is None:
      print "Error opening %s " % csvFilename
      sys.exit(1)

    #Read in the file using csv
    rdr= csv.reader(fPtr)
    fPtr = None

    #Create container for input
    input = []

    #Keep only columns we want SIMS ID, Date, and NDVI
    for l in rdr:
      input.append((l[2],l[3],l[7]))

    #Remove header
    input = input[1::]
    print input

    #Create container for final output
    output = []
    
    #How many unique ids do we have?
    simsIds = [i[0] for i in input]
    yDim = numpy.count_nonzero(simsIds)
    print "Number of unique sims ids %d" % yDim

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

        output.append((l[0],dtNum,ndvi2))
    print output

    #Write list to CSV
    #Results = open(os.path.join('Output', csvFilename),"wb")
    #wtr= csv.writer(Results)

    #for i in output:
    #    wtr.writerow(i)

    #Get all the unique simsids
    #uniqueIds = getUnique...
   
    #for simdsId in uniqueIds:
    #  for o in output:
    #    tempOutId = o[0]
    #    if simsId  == tempOutId:
    #       #Check the date and add to column
    #       output[15,20] = ndvi
    #    else:
    #       continue    
