import numpy
import os

os.chdir("/home/go_myco/CSVConversion/Output")

L7csv = numpy.genfromtxt('outputL7m.csv', delimiter= ",")
L8csv = numpy.genfromtxt('outputL8m.csv', delimiter= ",")
print L7csv[6]
print L8csv[6]

output = numpy.where(L8csv > 0, L8csv,L7csv)

output_destination = '/home/go_myco/CSVConversion/Output/combined.csv'

numpy.savetxt(output_destination, output, delimiter=",", fmt='%.3f')
