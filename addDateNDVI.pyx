cimport cython
cimport numpy as np
import numpy as np

def populate (int yDim, np.ndarray[np.float_t, ndim=2] finalOutput, np.ndarray[np.float_t, ndim=2] tempOut):
    cdef int row = 0
    cdef double simsId = 0
    #cdef tuple j = ()
    cdef int j = 0
    cdef double date = 0
    cdef double ndvi = 0
    cdef double tempOutId = 0
    cdef int col = 0
    cdef double dateTemp = 0
    cdef double dateTemp2 = 0

    cdef int jDim = tempOut.shape[0]#0
  
    cdef int currentIndx = 0

    print yDim
    print jDim

    for row in range(1,yDim):
        print '{0}\r'.format(row),
        simsId = finalOutput[<unsigned int>row, 0]

        for j in range(0,jDim):#tempOut:
            #Get the sims IDs
            tempOutId = tempOut[<unsigned int>j,0]
            #print tempOutId,simsId
            if simsId > tempOutId:
                break
                
            if simsId == tempOutId:
                #currentIndx = j
                #we could use this to start searching at last position
                #print "IDs match", simsId, tempOutId
                date = tempOut[<unsigned int>j,1]
                ndvi = tempOut[<unsigned int>j,2]
                
                #If it's no data then move on to next row
                if ndvi > -1.0:
                  #print date, ndvi

                  #Find the colum
                  for col in range(5, 51):
                    dateTemp = int(finalOutput[0, <unsigned int>col])
                    dateTemp2 = dateTemp+8

                    if (dateTemp == date) and (date < dateTemp2):
                        #print row, col, ndvi
                        finalOutput[<unsigned int>row, <unsigned int>col] = ndvi
                
    
    return finalOutput
