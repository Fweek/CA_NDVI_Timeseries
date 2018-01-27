# This script merges multiple CSV files into one and removes extra headers.
# Then it double checks if extra headers exist

import glob, os, csv, sys

#Error message user receives if missing parameters
usage = "Merges all the individual CSV files into one\n" + \
        "usage: Merge_CSV.py <File directory of all CSVs> <output filename: merged.csv>"

if len(sys.argv) <1:  #Number of arguments required
    print usage
    sys.exit(1)

#Set working directory to user input (directory path of input files)
os.chdir(sys.argv[1])

#Make a new directory for the combined output files if it does not already exist
if not os.path.exists('Output-Merged'):
    os.makedirs('Output-Merged', )

#Set working directory to directory of reformatted files
os.chdir(sys.argv[1]+'/Output-Classified')

CSV_files = glob.glob("*.csv")

print "Starting merge"
header_saved = False
with open('temp.csv','wb') as fout:
    for filename in CSV_files:
        print(filename)
        with open(filename) as fin:
            header = next(fin)
            if not header_saved:
                fout.write(header)
                header_saved = True
            for line in fin:
                fout.write(line)
print "done"


print "double-checking headers were deleted"
with open('temp.csv', 'rb') as inp, open(sys.argv[2], 'wb') as out:
    reader = csv.reader(inp)
    writer = csv.writer(out)
    headers = next(reader, None)  # returns the headers or `None` if the input is empty
    if headers:
        writer.writerow(headers)
    for row in csv.reader(inp):
        if row[1] != "date":
            writer.writerow(row)
print "done"
