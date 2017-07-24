# Import the Earth Engine Python Package
import ee, datetime, time, sys

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
CA_polygon = ee.Geometry.Polygon(
    [[[-124.20921995521553, 41.51488654023345],
      [-124.51685417405076, 40.41129319422741],
      [-124.00036049953536, 39.823078222550436],
      [-123.76956193011677, 38.88847627801764],
      [-122.47286052275422, 37.18364615274037],
      [-122.02916445119877, 36.847001643917615],
      [-121.97835870596555, 36.294290050154316],
      [-121.6117846446461, 36.01681323341259],
      [-121.3629970594859, 35.67188786688154],
      [-120.77511692190774, 35.05358607744978],
      [-120.63225943955223, 34.475856856713534],
      [-119.70047734557852, 34.25000684388964],
      [-119.56296000213342, 33.967338619207666],
      [-118.54405910056727, 33.96984620132081],
      [-118.67351603712058, 33.5215006626617],
      [-118.48418883442054, 33.26245594789118],
      [-117.7215967190836, 33.393710104815824],
      [-117.36239521082945, 32.97811585090315],
      [-117.27261268039786, 32.508154070114315],
      [-114.50360328501665, 32.72561979918868],
      [-114.41019857596342, 32.94719720814995],
      [-114.49659401865097, 33.074907927594644],
      [-114.63603507333545, 33.113485274763924],
      [-114.59424081610251, 33.317563167841115],
      [-114.45869991405743, 33.58931452035561],
      [-114.44152000510991, 33.88783741183264],
      [-114.31953884520681, 34.09964171272725],
      [-114.06678119380615, 34.29675114909958],
      [-114.32384260586258, 34.59178992926519],
      [-114.5026648721186, 34.84985767939348],
      [-114.58046259871588, 35.022079592400864],
      [-119.9372951410673, 39.02952120857728],
      [-119.9345822965098, 42.01289938985791],
      [-122.14351910778498, 42.05955034509238],
      [-124.3520996271057, 42.05362744650692]]]);
fields = ee.FeatureCollection("users/mhang/base12_ca_poly_170613_slim") #All farm field boundaries as of June2016

# --------------------------------------------------------------------------------------------------
# FUNCTIONS

# function to calculate NDVI for Landsat 7 SR
def calculateNDVI_L7(image):
    ndvi = image.normalizedDifference(['B4', 'B3'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('cfmask').eq(0))
    prop = ['system:time_start']
    return ndvi.copyProperties(image, prop)


# function to calculate NDVI for Landsat 7 TOA
def calculateNDVI_L7_TOA(image):
    ndvi = image.normalizedDifference(['B4', 'B3'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('fmask').eq(0))
    prop = ['system:time_start']
    return ndvi.copyProperties(image, prop)


# function to calculate NDVI for Landsat 8 SR
def calculateNDVI_L8(image):
    ndvi = image.normalizedDifference(['B5', 'B4'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('cfmask').eq(0))
    prop = ['system:time_start']
    return ndvi.copyProperties(image, prop)


# function to calculate NDVI for Landsat 8 TOA
def calculateNDVI_L8_TOA(image):
    ndvi = image.normalizedDifference(['B5', 'B4'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('fmask').eq(0))
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

#Clip each block by the state borders
intersectBlock = dividedArea.intersection(CA_polygon)

# Load the fields by block
fields_filter = fields.filterBounds(intersectBlock)

# Simplify the geometries to try and speed things up
maxErrorTolerance = 20
if vMode == 'y':
    print "Simplifying polygons with maxErrorTolerance of %d percent" % maxErrorTolerance


def simplify(f):
    return f.simplify(maxErrorTolerance)


fields_simplified = fields_filter.map(simplify)

# Set temporal and spatial parameters
outputPoly = fields_simplified
tStart = sys.argv[4]  # '2016-01-01'
tEnd = sys.argv[5]  # '2016-12-31'

# Retrieve Image collection then filter,clip,calculate NDVI and filter clouds
#  Here we're filtering by the bounding block instead of by the fields
if vMode == 'y':
    print "Loading and filtering image collection using %s to %s" % (tStart, tEnd)
if sys.argv[1] == 'L7SR':
    L7_IC = ee.ImageCollection("LANDSAT/LE7_SR") #Landsat7 Surface Reflectance Image Collection
    NDVI_IC = L7_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_L7).select('nd')
elif sys.argv[1] == 'L7TOA':
    L7_IC = ee.ImageCollection("LANDSAT/LE7_L1T_TOA_FMASK")
    NDVI_IC = L7_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_L7_TOA).select('nd')
elif sys.argv[1] == 'L8SR':
    L8_IC = ee.ImageCollection("LANDSAT/LC8_SR")
    NDVI_IC = L8_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_L8).select('nd')
elif sys.argv[1] == 'L8TOA':
    L8_IC = ee.ImageCollection("LANDSAT/LC8_L1T_TOA_FMASK")
    NDVI_IC = L8_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_L8_TOA).select('nd')
elif sys.argv[1] == 'Sent2A':
    Sent2A_IC = ee.ImageCollection("COPERNICUS/S2")
    NDVI_IC = Sent2A_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_Sent2A).select('nd')


if vMode == 'y':
    print "Calculating field averages"

# Get the field averages
means = NDVI_IC.map(getMeans).flatten()

# remove geometry
means = means.map(removeGeo)

# filter
#means = means.filter(ee.Filter.neq('mean', None)).sort('date')  # python uses none instead of null (JavaScript)

fn = '%s_%s_polygons' % ((sys.argv[2]), (sys.argv[4]))

# Export to CSV to Google Drive
# Create export parameters
taskParams = {
    'driveFolder': 'Python EE Exports (column drop commented)',
    'driveFileNamePrefix': fn,
    'fileFormat': 'CSV'
}

# Status updates for export
MyTry = ee.batch.Export.table(means, str(sys.argv[2]), taskParams)
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
Script_status = MyTry.status()
print "Start time: ", bTime
print "End time: ", datetime.datetime.now()

#Automatically restart entire script is export fails.
script_split = str(Script_status).split(',') #parsing the export status for the completed or failed status
state = script_split[5]
state2 = state.split(':')
state3 = str(state2[1])
repeat = 0 #create a counter for the number of retrys before quitting.

#Restart function
def restart():
    import sys
    print("argv was", sys.argv)
    print("sys.executable was", sys.executable)
    print("restart now")

    import os
    os.execv(sys.executable, ['python'] + sys.argv)

#If the export status is FAILED and the repeat counter is less than 5 then restart the entire script.
if state3 == str(" u'FAILED'") and repeat<5:
    repeat += 1
    print repeat
    restart()
