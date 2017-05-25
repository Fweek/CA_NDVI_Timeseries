# Import the Earth Engine Python Package
import os, ee, datetime, csv, time, sys

ee.Initialize()  # Initialize the Earth Engine object, using the authentication credentials.

# Sample command line call
# time python FAM_L7_timeseries_MH.py Test_L7_timeseries 10 2016-01-01 2016-01-31 y

# Get the command line arguments
usage = "usage: FAM_L7_timeseries.py <outputFilePrefix> <numberOfPolygons> <startDate> <endDate> <verbose(y/n)>\n" + \
        "Calculates field averages limiting to number of polygons and dates(YYYY-MM-DD format) specified"
if len(sys.argv) < 6:
    print usage
    sys.exit(1)

bTime = datetime.datetime.now()

# --------------------------------------------------------------------------------------------------
# IMPORT Earth Engine objects
strSub = sys.argv[3].split(',')
dividedArea = ee.Geometry.Rectangle([float(strSub[0]),float(strSub[1]),float(strSub[2]),float(strSub[3])])

fields = ee.FeatureCollection("ft:1GE0weDX4hKp_8Lt-MRySeDktJJ-gej7czjWPmzAx") #All farm field boundaries as of June2016
SIMS_ID_basemap = ee.Image("users/mhang/ca_30m_sid_poly_b5m_2014_12152016_ag_only")

# --------------------------------------------------------------------------------------------------
# FUNCTIONS
# function to calculate mode pixel value for each feature. For attaching SIMS ID to each field
def getPixelValue(image):
    return image.reduceRegions(
        collection=fields_filter,
        reducer=ee.Reducer.mode().setOutputs(['SIMS_ID']),
        scale=30)


# function to calculate NDVI for Landsat 7
def calculateNDVI_L7(image):
    ndvi = image.normalizedDifference(['B4', 'B3'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('cfmask').eq(0))
    prop = ['system:time_start']
    return ndvi.copyProperties(image, prop)


# function to calculate NDVI for Landsat 8
def calculateNDVI_L8(image):
    ndvi = image.normalizedDifference(['B5', 'B4'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('cfmask').eq(0))
    prop = ['system:time_start']
    return ndvi.copyProperties(image, prop)


# function to calculate NDVI for Sentinel 2A (no cloudmasking yet)
def calculateNDVI_Sent2A(image):
    ndvi = image.normalizedDifference(['B8', 'B4'])
    prop = ['system:time_start']
    return ndvi.copyProperties(image, prop)


# function to calculate mean NDVI
def getMeans(image):
    def reduce(f):
        return f.set('mean', image.reduceRegion(ee.Reducer.mean(), f.geometry(), 30))

    meansPolyMeans = outputPoly.map(reduce)

    def date(f):
        return f.set('date', ee.Date(image.get('system:time_start')).format('YYYY-MM-dd'))

    meansPolyMeans = meansPolyMeans.map(date)
    return meansPolyMeans


# function to remove geometry at the end
def removeGeo(feature):
    return feature.select([".*"], None, False)  # in python false needs to be False


vMode = sys.argv[6]
if vMode == 'y':
    print "Verbose mode on"

# --------------------------------------------------------------------------------------------------

# Load the fields, this does not include SIMS ids
fields_filter = fields.filterBounds(dividedArea)

# Add SIMS ID; intersected fields does not mess up SIMS ID
fields_SIMS = getPixelValue(SIMS_ID_basemap)

# Simplify the geometries to try and speed things up
maxErrorTolerance = 20
if vMode == 'y':
    print "Simplifying polygons with maxErrorTolerance of %d percent" % maxErrorTolerance


def simplify(f):
    return f.simplify(maxErrorTolerance)


fields_simplified = fields_SIMS.map(simplify)

# Set temporal and spatial parameters
outputPoly = fields_simplified
clipPolygon = outputPoly  # ca_clip
tStart = sys.argv[4]  # '2016-01-01'
tEnd = sys.argv[5]  # '2016-12-31'

# Retrieve Image collection then filter,clip,calculate NDVI and filter clouds
if vMode == 'y':
    print "Loading and filtering image collection using %s to %s" % (tStart, tEnd)
if sys.argv[1] == 'L7SR':
    L7_IC = ee.ImageCollection("LANDSAT/LE7_SR") #Landsat7 Surface Reflectance Image Collection
    NDVI_IC = L7_IC.filterDate(tStart, tEnd).filterBounds(clipPolygon).map(calculateNDVI_L7).select('nd')
elif sys.argv[1] == 'L7TO':
    L7_IC = ee.ImageCollection("LANDSAT/LE7_L1T_TOA_FMASK")
    NDVI_IC = L7_IC.filterDate(tStart, tEnd).filterBounds(clipPolygon).map(calculateNDVI_L7).select('nd')
elif sys.argv[1] == 'L8SR':
    L8_IC = ee.ImageCollection("LANDSAT/LC8_SR")
    NDVI_IC = L8_IC.filterDate(tStart, tEnd).filterBounds(clipPolygon).map(calculateNDVI_L8).select('nd')
elif sys.argv[1] == 'L8TOA':
    L8_IC = ee.ImageCollection("LANDSAT/LC8_L1T_TOA_FMASK")
    NDVI_IC = L8_IC.filterDate(tStart, tEnd).filterBounds(clipPolygon).map(calculateNDVI_L8).select('nd')
elif sys.argv[1] == 'Sent2A':
    Sent2A_IC = ee.ImageCollection("COPERNICUS/S2")
    NDVI_IC = Sent2A_IC.filterDate(tStart, tEnd).filterBounds(clipPolygon).map(calculateNDVI_Sent2A).select('nd')


if vMode == 'y':
    print "Calculating field averages"

# Get the field averages
means = NDVI_IC.map(getMeans).flatten()

# remove geometry
means = means.map(removeGeo)

# filter
means = means.filter(ee.Filter.neq('mean', None)).sort('date')  # python uses none instead of null (JavaScript)

fn = '%s_polygons' % (sys.argv[2])

# Export to CSV
taskParams = {
    'driveFolder': 'Python EE Exports',
    'driveFileNamePrefix': fn,
    'fileFormat': 'CSV'
}

# Status updates for export
MyTry = ee.batch.Export.table(means, 'lst_timeseries', taskParams)
MyTry.start()
state = MyTry.status()['state']
counter = 0
while state in ['READY', 'RUNNING']:
    if vMode == 'y':
        print "\r" + state + '... ' + str(counter),
    time.sleep(1)
    state = MyTry.status()['state']
    counter += 1
print 'Done.', MyTry.status()
print "Start time: ", bTime
print "End time: ", datetime.datetime.now()
