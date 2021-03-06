import sys,os,csv,datetime,string,numpy

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

    #Read in the file using csv module
    rdr= csv.reader(fPtr)
    fPtr = None

    #Create container for input
    input = []

    #Keep only columns we want: SIMS ID, Date, and NDVI
    for l in rdr:
      input.append((l[2],l[3],l[7]))

    #Remove header
    input = input[1::]

    #Find how many unique ids we have
    simsIds = [i[0] for i in input]

    #Get all the unique simsids and count them
    yDim = len(numpy.unique(simsIds)) + 1 #add one to account for row header
    print "Number of unique sims ids %d" % yDim

    # We will always have 5 columns + 46 timesteps
    xDim = 51

    #Create final output array
    finalOutput = numpy.ones((yDim,xDim)) * -9999.0

    #Create temp output container
    tempOut = []

    #More formatting
    for l in input:
        #Grab only date column
        dtStr = l[1]
        #Parse out year, month, day. Ugly code but need to get this moving...
        yr, mm, dd = dtStr[0:4], dtStr[5:7], dtStr[8:10]
        #Reformat date
        dtNum = (datetime.datetime(int(yr), int(mm), int(dd)) - datetime.datetime(1980, 1, 1)).days

        #Replace all {nd=null} values with -9999
        ndvi = l[2]
        ndvi2 = string.replace(ndvi, '{nd=null}', '-9999')

        #Format NDVI to only numbers
        ndvi3 = string.replace(ndvi2, '{nd=', '')
        ndvi4 = string.replace(ndvi3, '}', '')
        tempOut.append((float(l[0]), dtNum, ndvi4))

    tempOut.sort()

    #Find how many unique dates we have
    allDates = [i[1] for i in tempOut]

    #Get all unique IDs and count them
    uniqueIds = numpy.unique(simsIds)
    #print uniqueIds.shape

    #Fill in the date header based on year, assuming we're looking at 2016 data
    tStart = (datetime.datetime(2016, 01, 1) - datetime.datetime(1980, 1, 1)).days
    print tStart
    tEnd = (datetime.datetime(2016, 12, 31) - datetime.datetime(1980, 1, 1)).days
    print tEnd

    indx = 0
    for i in range(tStart, tEnd, 8): #every 8th value starting at tStart
        finalOutput[0, indx+1] = i #take that value and put it in the finalOutput array at the specified index
        indx += 1 #index increases incrementally each loop

    finalOutput[1:yDim, 0] = uniqueIds

    for row in range(1, yDim):  # for each row in the range of SIMs IDs
        simsId = finalOutput[row, 0]  # create variable called simsId, set it equal to the simsId in the [row, 0] position
        for j in tempOut:  # then in a different list
            tempOutId = float(j[0])  # make tempOutId equal to just the SIMS ID column
            # print simsId,tempOutId
            if simsId == tempOutId:  # check to see if the two SIMS ID match up
                # Check the date and add to column
                print "IDs match", simsId, tempOutId  # if they match says so
                date = j[1]  # create varaibles for each column
                ndvi = j[2]
                print date, ndvi
                # which column?
                for col in range(5, 51):  # why 5?
                    dateTemp = int(finalOutput[0, col])  # make new date variable based on header
                    dateTemp2 = dateTemp+8
                    # print dateTemp,date
                    if dateTemp <= date < dateTemp2:
                        # Most dates won't match since the overpass can fall anywhere in between the 8 day period
                        #      Have to account for this to make the code work
                        # print "Dates match"
                        print row, col, ndvi
                        finalOutput[row, col] = ndvi

    #print finalOutput

    #Write list to CSV
    outStrFn = 'outputFile_'
    numpy.savetxt(outStrFn+'_avgs.csv', finalOutput, delimiter=",",fmt='%.3f')
