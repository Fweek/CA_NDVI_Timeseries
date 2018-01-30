# This script takes the raw timeseries export files (Landsat7 and Landsat 8) from Google Earth Engine and combines/reformats them to match the NEX Ecocast files.
# These input files:
# 1) Must be placed within the same directory.
# 2) Must be complementary meaning it must contain both Landsat 7 and Landsat 8 files
# 3) Must be separated by satellite type i.e. Surface Reflectance (SR) and Top of Atmosphere (TOA) should not be placed within the same directory.
# 4) Can have any number of columns but DATE, mean NDVI, and SIMSID must be in columns 1, 2, and 3 (column indices 0, 1, 2).
# 5) Must have this filename structure: <prefix>_<start date>_<end date>_<satellite sensor>_<offset>.csv.
#    Prefix can be anything but the last four groups must be in the format shown in the example below
#    Example: WA_Mean_2013-01-01_2013-12-31_L8SR_15000.csv

import sys, os, os.path, csv, datetime, string, numpy, re
from dateutil.parser import parse
import addDateNDVI

#Error message: Missing arguments
usage = "Reformats the input CSV files to match NEX files\n" + \
        "usage: python CSV_reformat.py <Directory path of input files> <year>"

if len(sys.argv) < 2:  # Number of arguments required
    print usage
    sys.exit(1)

bTime = datetime.datetime.now()

#Set working directory to user input (directory path of input files)
os.chdir(sys.argv[1])

#Make a new directory for the output files if it does not already exist
if not os.path.exists('Output-Reformatted'):
    os.makedirs('Output-Reformatted', )

#Loop through every file in the current working directory.
for csvFilename in os.listdir('.'):
    if not csvFilename.endswith('.csv'):
        continue  # skip non-csv files

    print('REFORMATTING ' + csvFilename + '...')

    #Open the file
    fPtr = open(csvFilename)
    if fPtr is None:  # if the file doesn't exist close out ???
        print "Error opening %s " % csvFilename
        sys.exit(1)

    #Read in the file using csv module
    rdr = csv.reader(fPtr)
    fPtr = None

    #Create a blank list container for input
    input = []

    #Keep only columns we want: DATE in column 1, NDVI in column 2, and SIMSID in column 3
    for l in rdr:  # for each line in the current open CSV
        input.append((l[1], l[2], l[3]))  # take columns 1-3 and add them to the empty list container

    #Remove header
    input = input[1::]  #keep all rows but the header

    #Find how many unique ids we have
    simsIds = [float(i[2]) for i in input] # create subset list that is just the 3rd column aka the Index 2 column (SIMs ID column) of the new list

    #Get all the unique simsids and count them. This will be the number of rows for our final table
    uniqueIds = numpy.unique(simsIds)  # count all the unique SIMS IDs in the subset list
    yDim = len(uniqueIds) + 1  # Make a new variable that is = to the # of unique IDs; adding 1 to account for new row header
    #print "Number of unique sims ids %d" % yDim

    #We will always have 51 columns. 5 extra + 46 timesteps
    xDim = 51

    #Create final output array
    finalOutput = numpy.ones((yDim, xDim)) * -9999.0  #fill all cells with -9999

    #Create temp output container
    tempOut = numpy.ones(
        (len(input), 3)) * -9999.0  #create a temp output array with only 3 columns and fill all cells with -9999

    #print "Reformatting the array"

    #Function that checks if the input string is a DATE
    def is_date(string):
        try:
            parse(string)
            return True
        except ValueError:
            return False

    #More formatting
    for i in range(0, len(input)):  # for each row in the range of 0 to however long input is
        inputItem = input[i]  # create list with just the current row. Ex. [01/05/2016, 0.105264589, 290026865]
        dtStr = inputItem[0]  # create new list of just Index 0 cell (date cell)

        # If the input string is a date and the date format starts with YYYY do the following:
        if is_date(dtStr) == True and dtStr.startswith("20"):
            regx = re.compile('[-/]')
            # Parse out year, month, day.
            y, m, d = regx.split(str(dtStr))
            '/'.join(('20' + y.zfill(2), m.zfill(2), d.zfill(2) if len(y) == 2 else y))
            # Reformat date
            dtNum = (datetime.datetime(int(y), int(m), int(d)) - datetime.datetime(1980, 1, 1)).days
            # Replace all {nd=null} values with -9999
            ndvi = inputItem[1]
            # If ndvi value is in {nd=0.#####} format do the following:
            if ndvi == '':
                ndvi2 = string.replace(ndvi, '', '-9999')
                # Now rebuild the SIMSID, date, NDVI list
                tempOut[i, 0] = float(inputItem[2])  # add the SIMs ID to the 1st cell in tempOut
                tempOut[i, 1] = float(dtNum)  # add the new modified date to the 2nd cell in tempOut
                tempOut[i, 2] = float(ndvi2)  # add the new modified NDVI to the 3rd cell in tempOut
                # Otherwise if just a value do the following:
            else:
                tempOut[i, 0] = float(inputItem[2])  # add the SIMs ID to the 1st cell in tempOut
                tempOut[i, 1] = float(dtNum)  # add the date to the 2nd cell in tempOut
                tempOut[i, 2] = ndvi  # add the NDVI to the 3rd cell in tempOut

        # Otherwise if the input string is a date and the date format starts with mm do the following:
        elif is_date(dtStr) == True:
            regx = re.compile('[-/]')
            # Parse out year, month, day.
            m, d, y = regx.split(str(dtStr))
            '/'.join(('20' + y.zfill(2), m.zfill(2), d.zfill(2) if len(y) == 2 else y))
            # Reformat date
            dtNum = (datetime.datetime(int(y), int(m), int(d)) - datetime.datetime(1980, 1, 1)).days
            # Replace all {nd=null} values with -9999
            ndvi = inputItem[1]
            # If ndvi value is in {nd=0.#####} format do the following:
            if ndvi == '':
                ndvi2 = string.replace(ndvi, '', '-9999')
                # Now rebuild the SIMSID, date, NDVI list
                tempOut[i, 0] = float(inputItem[2])  # add the SIMs ID to the 1st cell in tempOut
                tempOut[i, 1] = float(dtNum)  # add the new modified date to the 2nd cell in tempOut
                tempOut[i, 2] = float(ndvi2)  # add the new modified NDVI to the 3rd cell in tempOut
                # Otherwise if just a value do the following:
            else:
                tempOut[i, 0] = float(inputItem[2])  # add the SIMs ID to the 1st cell in tempOut
                tempOut[i, 1] = float(dtNum)  # add the date to the 2nd cell in tempOut
                tempOut[i, 2] = float(ndvi)  # add the NDVI to the 3rd cell in tempOut

    tempOut = tempOut[numpy.argsort(tempOut[:, 0])]

    # Find how many unique dates we have
    # Do we still need line below?
    allDates = [i[1] for i in tempOut]

    # Get all unique IDs and count them
    uniqueIds = numpy.unique(simsIds)
    # print uniqueIds.shape

    # Now we work on the header which is just a range of dates. This is only for 2016
    # Create the start date and the end date
    tStart = (datetime.datetime(int(sys.argv[2]), 01, 1) - datetime.datetime(1980, 1, 1)).days
    #print tStart
    tEnd = (datetime.datetime(int(sys.argv[2]), 12, 31) - datetime.datetime(1980, 1, 1)).days
    #print tEnd

    # Now we'll fill in the dates inbetween
    #print "Populating the date"
    indx = 5  # We're going to skip the first 5 cells which is reserved for something else
    for i in range(tStart, tEnd, 8):  # starting at tStart add 8 until we get to tEnd
        finalOutput[0, indx] = i  # In the finalOutput list, fill in the specified cell with the new date
        indx += 1  # index increases incrementally each loop

    #print "Adding the uniqueIds"
    finalOutput[1:yDim,
    0] = uniqueIds  # Now that the header row is all filled in, we're fill the header column with all the SIMs IDs

    #print "Starting to populate array"  # Now we need to populate the rest of the table with NDVI
    finalOutput = addDateNDVI.populate(yDim, finalOutput, tempOut)

    # print finalOutput

    # Write list to CSV
    output_destination = sys.argv[1] + '/Output-Reformatted/' + 'Reformatted_' + csvFilename
    numpy.savetxt(output_destination, finalOutput, delimiter=",", fmt='%.3f')

print "REFORMATTING COMPLETE"
print "Start time: ", bTime
print "End time: ", datetime.datetime.now()
