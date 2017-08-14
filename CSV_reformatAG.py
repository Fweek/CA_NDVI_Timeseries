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
    if fPtr is None: #if the file doesn't exist close out ???
      print "Error opening %s " % fn
      sys.exit(1)

    #Read in the file using csv module
    rdr= csv.reader(fPtr)
    fPtr = None

    # Create a blank list container for input
    input = []

    # In the current open CSV, keep only columns we want: DATE in column 0, NDVI in column 1, and SIMSID in column 2
    for l in rdr: #for each line in the current open CSV
      input.append((l[1],l[2],l[3]))  #take columns 1-3 and add them to the empty list container

    #Remove header
    input = input[1::] #keep all rows after header

    # Find how many unique ids we have in the new list
    simsIds = [float(i[2]) for i in input]  # create subset list that is just the 2nd column (SIMs ID column) of the new list

    # Get all the unique simsids and count them. This will be the number of rows for our final table
    uniqueIds = numpy.unique(simsIds) #count all the unique SIMS IDs in the subset list
    yDim = len(uniqueIds) + 1 #Make a new variable that is = to the # of unique IDs; adding 1 to account for new row header
    print "Number of unique sims ids %d" % yDim

    # We will always have 51 columns. 5 extra + 46 timesteps
    xDim = 51

    #Create final output array
    finalOutput = numpy.ones((yDim,xDim)) * -9999.0 #fill all cells with -9999
    tempOut = numpy.ones((len(input),3)) * -9999.0 #create a temp output array with only 3 columns and fill all cells with -9999

    print "Reformatting the array"

    #More formatting
    for i in range(0,len(input)): #for each row in the range of 0 to however long input is
        #Grab only date column
        #print input[i,0]
        inputItem = input[i] #create list with just the current row. Ex. [01/05/2016, 1536, 0.56]
        #print inputItem
        #if i > 8:
        #  sys.exit(0)
        dtStr = inputItem[0] #create new list of just 0 cell(date cell)
        #Parse out year, month, day. Ugly code but need to get this moving...
        dtStr2 = dtStr.split('-') #split the date up by the dash (-)
        yr, mm, dd = dtStr2[0], dtStr2[1], dtStr2[2] #create new variables for day, month, and year
        #Reformat date
        dtNum = (datetime.datetime(int(yr), int(mm), int(dd)) - datetime.datetime(1980, 1, 1)).days

        # Work on NDVI now
        ndvi = inputItem[1] #create new list of just the 1 cell (NDVI cell)
        ndvi2 = string.replace(ndvi, '{nd=null}', '-9999') #If the value of this cell is {nd=null} then replace it with -9999

        #Format NDVI to only numbers
        ndvi3 = string.replace(ndvi2, '{nd=', '') #get rid of the {nd= part
        ndvi4 = string.replace(ndvi3, '}', '')
        #tempOut.append((float(l[2]), float(dtNum), float(ndvi4)))
        #Now rebuild the SIMSID, date, NDVI list
        tempOut[i,0] = float(inputItem[2]) #add the SIMs ID to the 1st cell in tempOut
        tempOut[i,1] = float(dtNum) #add the new modified date to the 2nd cell in tempOut
        tempOut[i,2] = float(ndvi4) #add the new modified NDVI to the 3rd cell in tempOut
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

    #Now we work on the header which is just a range of dates. This is only for 2016
    #Create the start date and the end date
    tStart = (datetime.datetime(2016, 01, 1) - datetime.datetime(1980, 1, 1)).days
    print tStart
    tEnd = (datetime.datetime(2016, 12, 31) - datetime.datetime(1980, 1, 1)).days
    print tEnd

    #Now we'll fill in the dates inbetween
    print "Populating the date"
    indx = 5 #We're going to skip the first 5 cells which is reserved for something else
    for i in range(tStart, tEnd, 8):  #starting at tStart add 8 until we get to tEnd
        finalOutput[0, indx] = i #In the finalOutput list, fill in the specified cell with the new date
        indx += 1 #index increases incrementally each loop

    print "Adding the uniqueIds"
    finalOutput[1:yDim, 0] = uniqueIds #Now that the header row is all filled in, we're fill the header column with all the SIMs IDs
    
    print "Starting to populate array" #Now we need to populate the rest of the table with NDVI
    finalOutput = addDateNDVI.populate(yDim, finalOutput, tempOut)

    #print finalOutput

    #Write list to CSV
    output_destination = '/home/aguzman/output.csv'#+folder+'/Output/'+csvFilename
    outStrFn = 'outputFile_'
    #numpy.savetxt(outStrFn+'avgs.csv', finalOutput, delimiter=",",fmt='%.3f')
    print output_destination
    numpy.savetxt(output_destination, finalOutput, delimiter=",",fmt='%.3f')
