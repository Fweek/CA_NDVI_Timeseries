# Import the Earth Engine Python Package
import ee, datetime, time, sys

ee.Initialize()  # Initialize the Earth Engine object, using the authentication credentials.

# Sample command line call
# time python FAM_L7_timeseries_MH.py Test_L7_timeseries 10 2016-01-01 2016-01-31 y

# Get the command line arguments
usage = "usage: WA_NDVI_Timeseries.py <Satellite: L7SR, L8SR, L7TOA, L8TOA, Sent2a> <outputNamePrefix> <startDate> <endDate> <offset: increments of 15000> <verbose(y/n)>\n" + \
        "Calculates field averages limited to number of polygons and within the date(YYYY-MM-DD format) range specified"
if len(sys.argv) < 6:
    print usage
    sys.exit(1)

bTime = datetime.datetime.now()

# --------------------------------------------------------------------------------------------------
# IMPORT Earth Engine objects
allfields = ee.FeatureCollection("users/mhang/base13-15_wa_poly_slim")
allfields_count = allfields.size()
# --------------------------------------------------------------------------------------------------
# FUNCTIONS

# function to calculate NDVI for Landsat 7 SR
def calculateNDVI_L7(image):
    ndvi = image.normalizedDifference(['B4', 'B3'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('cfmask').eq(0))
    return image.addBands(ndvi)


# function to calculate NDVI for Landsat 7 TOA
def calculateNDVI_L7_TOA(image):
    ndvi = image.normalizedDifference(['B4', 'B3'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('fmask').eq(0))
    return image.addBands(ndvi)


# function to calculate NDVI for Landsat 8 SR
def calculateNDVI_L8(image):
    ndvi = image.normalizedDifference(['B5', 'B4'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('cfmask').eq(0))
    return image.addBands(ndvi)


# function to calculate NDVI for Landsat 8 TOA
def calculateNDVI_L8_TOA(image):
    ndvi = image.normalizedDifference(['B5', 'B4'])
    # Filter the clouds
    ndvi = ndvi.updateMask(image.select('fmask').eq(0))
    return image.addBands(ndvi)


# function to calculate NDVI for Sentinel 2A (no cloudmasking yet)
def calculateNDVI_Sent2A(image):
    ndvi = image.normalizedDifference(['B8', 'B4'])
    return image.addBands(ndvi)


# function to calculate mean NDVI
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

    return result


# function to remove geometry at the end
def removeFeatureGeometry(feature):
  return ee.Feature(feature.setGeometry(None))


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
#Subset parameters
export_count = 10
export_offset = int(sys.argv[5])

#Subset all fields
fields = allfields.toList(export_count, export_offset)
fields = ee.FeatureCollection(fields)

# Set temporal and spatial parameters
tStart = sys.argv[3]  # '2016-01-01'
tEnd = sys.argv[4]  # '2016-12-31'

# Retrieve Image collection then filter,clip,calculate NDVI and filter clouds
#  Here we're filtering by the bounding block instead of by the fields
if vMode == 'y':
    print "Loading and filtering image collection using %s to %s" % (tStart, tEnd)
if sys.argv[1] == 'L7SR':
    L7_IC = ee.ImageCollection("LANDSAT/LE7_SR") #Landsat7 Surface Reflectance Image Collection
    NDVI_IC = L7_IC.filterDate(tStart, tEnd).filterBounds(fields).map(calculateNDVI_L7).select('ndvi')
elif sys.argv[1] == 'L7TOA':
    L7_IC = ee.ImageCollection("LANDSAT/LE7_L1T_TOA_FMASK")
    NDVI_IC = L7_IC.filterDate(tStart, tEnd).filterBounds(fields).map(calculateNDVI_L7_TOA).select('ndvi')
elif sys.argv[1] == 'L8SR':
    L8_IC = ee.ImageCollection("LANDSAT/LC8_SR")
    NDVI_IC = L8_IC.filterDate(tStart, tEnd).filterBounds(fields).map(calculateNDVI_L8).select('ndvi')
elif sys.argv[1] == 'L8TOA':
    L8_IC = ee.ImageCollection("LANDSAT/LC8_L1T_TOA_FMASK")
    NDVI_IC = L8_IC.filterDate(tStart, tEnd).filterBounds(fields).map(calculateNDVI_L8_TOA).select('ndvi')
elif sys.argv[1] == 'Sent2A':
    Sent2A_IC = ee.ImageCollection("COPERNICUS/S2")
    NDVI_IC = Sent2A_IC.filterDate(tStart, tEnd).filterBounds(fields).map(calculateNDVI_Sent2A).select('ndvi')


if vMode == 'y':
    print "Calculating field averages"

#Apply an inner join to intersecting features.
# spatialJoined = ee.Join.inner({'field','image', None}).apply({fields, NDVI_IC,ee.Filter.intersects({'.geo', None, '.geo', None, 10})})

spatialJoined = ee.Join.inner(
    primaryKey='field',
    secondaryKey='image'
).apply(
    primary=fields,
    secondary=NDVI_IC,
    condition=ee.Filter.intersects(
        leftField='.geo',
        rightValue=None,
        rightField='.geo',
        leftValue=None,
        maxError=10
    )
)

# Get the field averages
means = spatialJoined.map(calculateMean)

# remove geometry
means = means.map(removeFeatureGeometry)

fn = '%s_%s_%s' % ((sys.argv[2]), (export_offset+15000), (sys.argv[3]))

# Export to CSV to Google Drive
# Create export parameters
taskParams = {
    'driveFolder': 'Python EE Exports',
    'driveFileNamePrefix': fn,
    'fileFormat': 'CSV'
}

state3 = str(" u'FAILED'")
repeat = 15000 #counter

# If the export status is FAILED and the repeat counter is less than 5 then restart the export process
while state3 == str(" u'FAILED'") and repeat < allfields_count:
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

    script_split = str(Script_status).split(',')  # parsing the export status for the completed or failed status
    state = script_split[5]
    state2 = state.split(':')
    state3 = str(state2[1])

    repeat += 15000
    print "Repeat code for fields:", repeat-15000, "to", repeat

print "Start time: ", bTime
print "End time: ", datetime.datetime.now()
