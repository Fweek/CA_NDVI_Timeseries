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
WA_polygon = ee.Geometry.Polygon(
    [[[-123.0029296875, 48.821332549646634],
      [-123.0084228515625, 48.77429274267509],
      [-123.2720947265625, 48.680080770292875],
      [-123.233642578125, 48.552978164400706],
      [-123.1072998046875, 48.4146186174932],
      [-123.2611083984375, 48.27588152743497],
      [-123.5357666015625, 48.228332127214934],
      [-123.936767578125, 48.29415798558204],
      [-124.7882080078125, 48.49840764096434],
      [-124.7882080078125, 48.40732607972985],
      [-124.7113037109375, 48.31242790407178],
      [-124.7662353515625, 48.16974908365419],
      [-124.69482421875, 47.916342040161155],
      [-124.464111328125, 47.73932336136857],
      [-124.3597412109375, 47.36115300722623],
      [-124.3048095703125, 47.32393057095941],
      [-124.2279052734375, 46.94276208682137],
      [-124.07958984375, 46.728565825190536],
      [-124.07958984375, 46.55886030311717],
      [-124.1070556640625, 46.29001987172955],
      [-123.92578125, 46.240651955001695],
      [-123.5247802734375, 46.32417161725691],
      [-123.4918212890625, 46.1760268245766],
      [-123.3544921875, 46.126556302418514],
      [-123.2171630859375, 46.1760268245766],
      [-122.9534912109375, 46.12274903582433],
      [-122.8271484375, 45.96642454131025],
      [-122.794189453125, 45.77518618352103],
      [-122.8106689453125, 45.66012730272194],
      [-122.6458740234375, 45.59482210127054],
      [-122.4041748046875, 45.556371735883125],
      [-122.2119140625, 45.533288879467456],
      [-121.739501953125, 45.70234306798272],
      [-121.3714599609375, 45.690832836458156],
      [-121.201171875, 45.57944511437786],
      [-120.882568359375, 45.637087095718734],
      [-120.6298828125, 45.729191061299915],
      [-120.509033203125, 45.690832836458156],
      [-120.3387451171875, 45.683158032533086],
      [-119.9652099609375, 45.79816953017265],
      [-119.7564697265625, 45.832626782661535],
      [-119.5916748046875, 45.916765867649005],
      [-119.4927978515625, 45.89383147810291],
      [-119.322509765625, 45.920587344733654],
      [-119.1632080078125, 45.91294412737392],
      [-118.9654541015625, 45.97787791892827],
      [-116.8780517578125, 45.981695185122284],
      [-116.9000244140625, 46.14939437647686],
      [-116.9384765625, 46.19884437618253],
      [-116.9439697265625, 46.2824277013447],
      [-117.0263671875, 46.354510837365225],
      [-117.0098876953125, 46.46813299215553],
      [-116.9879150390625, 49.0162566577816],
      [-123.3489990234375, 49.0162566577816]]])

fields = ee.FeatureCollection("users/mhang/base13-15_wa_poly_slim")

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
# Calculate the mean value of an image for a region.
# @ param {ee.Feature} join_element - to result of an inner join operation.
# @ return {ee.Feature}

# Set to true when debugging functions running on a single element.
FUNCTION_OUTPUT = False

def calculateMean (join_element):
    #Extract information from the results of the inner join.
    matching_field = ee.Feature(join_element.get('field'))
    matching_image = ee.Image(join_element.get('image'))

    #Get the timestamp of the image.
    time_start = matching_image.get('system:time_start')

    #Calculate the spatial mean value of the feature.
    meanOfFeature = matching_image.reduceRegion(ee.Reducer.mean(), matching_field.geometry(), 30)

    #Add new attributes to the feature.
    result = matching_field.set(meanOfFeature).set({
            'image_time_start_string': ee.Date(time_start).format('YYYY-MM-dd')
            })

    # Debugging output, used when testing the function on single join results.
    if (FUNCTION_OUTPUT):
        print('join_element', join_element)
        print('matching_field', matching_field)
        print('matching_image', matching_image)
        print('meanOfFeature', meanOfFeature)
        print('result', result)

    return result


# function to remove geometry at the end
def removeFeatureGeometry(feat):
  return ee.Feature(feat.setGeometry(None))

# function to dummy feature to prevent NDVI column from being ddropped
def  addDummyFeature(fc):
  dummy = ee.FeatureCollection(
    ee.Feature(None, {'image_index': 0,
                      'image_time_start': 0,
                      'image_time_start_string': 0,
                      'sims_id': 0,
                      'ndvi': 0
                      })
  )
  return dummy.merge(fc)


vMode = sys.argv[6]
if vMode == 'y':
    print "Verbose mode on"

# --------------------------------------------------------------------------------------------------

#Clip each block by the state borders
intersectBlock = dividedArea.intersection(WA_polygon)

# Load the fields by clipped block
fields_filter = fields.filterBounds(intersectBlock)

# #Simplify the geometries to try and speed things up
# maxErrorTolerance = 10
# if vMode == 'y':
#     print "Simplifying polygons with maxErrorTolerance of %d percent" % maxErrorTolerance
#
#
# def simplify(f):
#     return f.simplify(maxErrorTolerance)
#
#
# fields_simplified = fields_filter.map(simplify)

# Set temporal and spatial parameters
tStart = sys.argv[4]  # '2016-01-01'
tEnd = sys.argv[5]  # '2016-12-31'

# Retrieve Image collection then filter,clip,calculate NDVI and filter clouds
#  Here we're filtering by the bounding block instead of by the fields
if vMode == 'y':
    print "Loading and filtering image collection using %s to %s" % (tStart, tEnd)
if sys.argv[1] == 'L7SR':
    L7_IC = ee.ImageCollection("LANDSAT/LE7_SR") #Landsat7 Surface Reflectance Image Collection
    NDVI_IC = L7_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_L7).select('ndvi')
elif sys.argv[1] == 'L7TOA':
    L7_IC = ee.ImageCollection("LANDSAT/LE7_L1T_TOA_FMASK")
    NDVI_IC = L7_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_L7_TOA).select('ndvi')
elif sys.argv[1] == 'L8SR':
    L8_IC = ee.ImageCollection("LANDSAT/LC8_SR")
    NDVI_IC = L8_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_L8).select('ndvi')
elif sys.argv[1] == 'L8TOA':
    L8_IC = ee.ImageCollection("LANDSAT/LC8_L1T_TOA_FMASK")
    NDVI_IC = L8_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_L8_TOA).select('ndvi')
elif sys.argv[1] == 'Sent2A':
    Sent2A_IC = ee.ImageCollection("COPERNICUS/S2")
    NDVI_IC = Sent2A_IC.filterDate(tStart, tEnd).filterBounds(dividedArea).map(calculateNDVI_Sent2A).select('ndvi')


if vMode == 'y':
    print "Calculating field averages"

#Apply an inner join to intersecting features.
spatialJoined = ee.Join.inner({'field', 'image', None}).apply({fields, NDVI_IC, ee.Filter.intersects('.geo', None, '.geo', None, 10)})


#Calculate the mean for each join result.
features_with_stats = spatialJoined.map(calculateMean)
print(features_with_stats.first())

#Remove the geometries
removedGeo = features_with_stats.map(removeFeatureGeometry)

#Add dummy feature
finalexport = addDummyFeature(removedGeo)

fn = '%s_%s_polygons' % ((sys.argv[2]), (sys.argv[4]))

# Export to CSV to Google Drive
# Create export parameters
taskParams = {
    'driveFolder': 'Python EE Exports',
    'driveFileNamePrefix': fn,
    'fileFormat': 'CSV'
}

state3 = str(" u'FAILED'")
repeat = 0 #counter

# If the export status is FAILED and the repeat counter is less than 5 then restart the export process
while state3 == str(" u'FAILED'") and repeat < 3:
    # Status updates for export
    MyTry = ee.batch.Export.table(finalexport, str(sys.argv[2]), taskParams)
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

    script_split = str(Script_status).split(',')  # parsing the export status for the completed or failed status
    state = script_split[5]
    state2 = state.split(':')
    state3 = str(state2[1])

    repeat += 1
    print "Repeat #:", repeat

print "Start time: ", bTime
print "End time: ", datetime.datetime.now()
