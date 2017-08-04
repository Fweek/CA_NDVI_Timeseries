cimport cython
cimport numpy as np
import numpy as np

def populate (int yDim, np.ndarray[np.float_t, ndim=2] finalOutput, list tempOut):
    cdef int row = 0
    cdef double simsId = 0
    cdef tuple j = ()
    cdef int date = 0
    cdef double ndvi = 0
    cdef double tempOutId = 0
    cdef int col = 0
    cdef int dateTemp = 0
    cdef int dateTemp2 = 0

    for row in range(1, yDim):
        simsId = finalOutput[<unsigned int>row, 0]

        for j in tempOut:
            tempOutId = float(j[0])
            if simsId == tempOutId:
                print "IDs match", simsId, tempOutId
                cdate = j[1]
                ndvi = float(j[2])
                print date, ndvi

                for col in range(5, 51):
                    dateTemp = int(finalOutput[0, <unsigned int>col])
                    dateTemp2 = dateTemp+8

                    if dateTemp <= date < dateTemp2:
                        print row, col, ndvi
                        finalOutput[<unsigned int>row, <unsigned int>col] = ndvi
