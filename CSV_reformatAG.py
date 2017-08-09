import sys,os,csv,datetime,string,numpy
import addDateNDVI

#Set working directory
#folder = 'CSVConversion'
#os.chdir("/home/go_myco/"+folder)

#Make a new directory for the output files if it does not already exist
#if not os.path.exists('Output'):
#    os.makedirs('Output',)

#Set working directory
#os.chdir('/home/aguzman/scripts/Inputs')

# Loop through every file in the current working directory.
#for csvFilename in os.listdir('/home/aguzman/scripts/Inputs/'):
fn = "/home/aguzman/scripts/inputs/L7SR_2016_meanNDVI_merged.csv"
if os.path.exists(fn) is False: #if the file stated above does not exists print Error
   print "Error no input file"
else:
    print('Modifying ' + fn + '...') #if it does start modifying it

    #Open the file
    fPtr = open(fn)
    if fPtr is None:
      print "Error opening %s " % fn
      sys.exit(1)

    #Read in the file using csv module
    rdr= csv.reader(fPtr)
    fPtr = None

    #Create container for input
    input = []

    #Keep only columns we want: DATE in column 0, NDVI in column 1, and SIMSID in column 2
    for l in rdr:
      input.append((l[1],l[2],l[3]))

    #Remove header
    input = input[1::]

    #Find how many unique ids we have
    simsIds = [i[2] for i in input] #where i is the row in input and [2] is the SIMSID column

    #Get all the unique simsids and count them. This will be the number of rows for our new table
    uniqueIds = numpy.unique(simsIds) #adding 1 to account for row header
    yDim = len(uniqueIds) + 1 
    print "Number of unique sims ids %d" % yDim

    # We will always have 51 columns. 5 extra + 46 timesteps
    xDim = 51

    #Create final output array
    finalOutput = numpy.ones((yDim,xDim)) * -9999.0 #fill all cells with -9999
    tempOut = numpy.ones((len(input),3)) * -9999.0

    print "Reformatting the array"

    #More formatting
    for i in range(0,len(input)):
        #Grab only date column
        #print input[i,0]
        inputItem = input[i]
        #print inputItem
        #if i > 8:
        #  sys.exit(0)
        dtStr = inputItem[0]
        #Parse out year, month, day. Ugly code but need to get this moving...
        dtStr2 = dtStr.split('-')
        yr, mm, dd = dtStr2[0], dtStr2[1], dtStr2[2]
        #Reformat date
        dtNum = (datetime.datetime(int(yr), int(mm), int(dd)) - datetime.datetime(1980, 1, 1)).days

        #Replace all {nd=null} values with -9999
        ndvi = inputItem[1]
        ndvi2 = string.replace(ndvi, '{nd=null}', '-9999')

        #Format NDVI to only numbers
        ndvi3 = string.replace(ndvi2, '{nd=', '')
        ndvi4 = string.replace(ndvi3, '}', '')
        #tempOut.append((float(l[2]), float(dtNum), float(ndvi4)))
        tempOut[i,0] = float(inputItem[2])
        tempOut[i,1] = float(dtNum)
        tempOut[i,2] = float(ndvi4)
        #print "tempOut",tempOut[i,0],tempOut[i,1],tempOut[i,2]
    
    tempOut = tempOut[numpy.argsort(tempOut[:, 0])]
         
    #Why Do we sort?
    #tempOut.sort()
    #print "tempOut",tempOut[10,0]
    #Find how many unique dates we have
    #Do we still need line below?
    #allDates = [i[1] for i in tempOut]

    #Get all unique IDs and count them
    #uniqueIds = numpy.unique(simsIds)
    #print uniqueIds.shape

    #Fill in the date header based on year, assuming we're looking at 2016 data
    tStart = (datetime.datetime(2016, 01, 1) - datetime.datetime(1980, 1, 1)).days
    print tStart
    tEnd = (datetime.datetime(2016, 12, 31) - datetime.datetime(1980, 1, 1)).days
    print tEnd

    print "Populating the date"
    indx = 5
    for i in range(tStart, tEnd, 8): #every 8th value starting at tStart
        finalOutput[0, indx] = i #take that value and put it in the finalOutput array at the specified index
        indx += 1 #index increases incrementally each loop

    print "Adding the uniqueIds"
    finalOutput[1:yDim, 0] = uniqueIds
    
    print "Starting to populate array"
    finalOutput = addDateNDVI.populate(yDim, finalOutput, tempOut)

    #print finalOutput

    #Write list to CSV
    output_destination = '/home/aguzman/output.csv'#+folder+'/Output/'+csvFilename
    outStrFn = 'outputFile_'
    #numpy.savetxt(outStrFn+'avgs.csv', finalOutput, delimiter=",",fmt='%.3f')
    print output_destination
    numpy.savetxt(output_destination, finalOutput, delimiter=",",fmt='%.3f')
