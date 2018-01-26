import sys, os.path, datetime, numpy

# Error message: Missing arguments
usage = "usage: python Combine.py <Directory path of input files>\n" + \
        "Reformats the input CSV files to match NEX files"
if len(sys.argv) < 1:  # Number of arguments required
    print usage
    sys.exit(1)

bTime = datetime.datetime.now()

print "Combining files..."

# Set working directory to user input (directory path of input files)
os.chdir(sys.argv[1])

#Make a new directory for the combined output files if it does not already exist
if not os.path.exists('Output-Combined'):
    os.makedirs('Output-Combined', )

#Count how many files are in the directory. Half of them should be L7 and the other half L8
filecount = len([f for f in os.listdir(sys.argv[1]) if os.path.isfile(f)])

#Divide the count in half
filecount_half = int(filecount/2)

#Take the first filename and parse it out
files = os.listdir(sys.argv[1]) #create list of all the filenames in the directory
filename = str(files[1]) #create string object of the first filename
filename_split = filename.split('_') #split the filename string up by _
split_length = len(filename_split) #count the number of splits

sat_index = int(split_length-2) #the split that identifies the satellite used for that file is always the second to last
sat_string = filename_split[sat_index] #create string object of the satellite sensor (L7SR, L7TOA, L8SR, L8TOA)
sat_string_split = list(sat_string) #split the string into a list of characters
sat_string_split_count = len(sat_string_split) #count the number of characters in the list
sat_type = sat_string_split[2:sat_string_split_count] #isolate the characters for the satellite type
sat_type_join =  ''.join(sat_type) #rejoin the characters for satellite type (SR, TOA)

offset_index = int(split_length-1) #the split that identifies the offset used for that file is always the last
offset_name = filename_split[offset_index] #this split still has .csv at the end so we need to split it again to get rid of .csv
offset_name_split = offset_name.split('.') #split by .
offset_value = int(offset_name_split[0])

#Rejoin the original filename
prefix = filename_split[0:sat_index]
prefix_join = '_'.join(prefix)
output_prefix = '_'.join(prefix[1:])

#Merge L7 and L8 files together while overwriting L7 values with L8 values if the L7 value is 0
for i in range(filecount_half): #loop for each pair of landsat files
    L7csv = numpy.genfromtxt(str(prefix_join)+'_L7'+str(sat_type_join)+'_'+str(offset_value)+".csv", delimiter= ",")
    L8csv = numpy.genfromtxt(str(prefix_join)+'_L8'+str(sat_type_join)+'_'+str(offset_value)+".csv", delimiter= ",")
    output = numpy.where(L8csv > 0, L8csv, L7csv)
    output_destination = sys.argv[1]+'/Output-Combined/'+'Combined_'+output_prefix+'_L7L8_'+str(offset_value)+'.csv'
    numpy.savetxt(output_destination, output, delimiter=",", fmt='%.3f')
    offset_value = offset_value+15000
