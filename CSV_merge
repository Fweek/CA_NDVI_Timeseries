# This script merges multiple CSV files into one and removes extra headers.
# Then it double checks if extra headers exist

import glob, os, csv

#Set working directory
folder = 'CSVConversion/Merge'
os.chdir("C:/Users\Michael/Desktop/"+folder)

CSV_files = glob.glob("*.csv")

print "Starting merge"
header_saved = False
with open('output.csv','wb') as fout:
    for filename in CSV_files:
        with open(filename) as fin:
            header = next(fin)
            if not header_saved:
                fout.write(header)
                header_saved = True
            for line in fin:
                fout.write(line)
print "done"


print "double-checking headers deleted"
with open('output.csv', 'rb') as inp, open('new_output.csv', 'wb') as out:
    reader = csv.reader(inp)
    writer = csv.writer(out)
    headers = next(reader, None)  # returns the headers or `None` if the input is empty
    if headers:
        writer.writerow(headers)
    for row in csv.reader(inp):
        if row[1] != "date":
            writer.writerow(row)
print "done"
