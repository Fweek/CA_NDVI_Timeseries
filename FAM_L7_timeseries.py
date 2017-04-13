# Import the Earth Engine Python Package
import os, ee, datetime, csv, time, sys

ee.Initialize() # Initialize the Earth Engine object, using the authentication credentials.


#Sample command line call
#time python FAM_L7_timeseries_MH.py Test_L7_timeseries 10 2016-01-01 2016-01-31 y

#Get the command line arguments
usage = "usage: FAM_L7_timeseries.py <outputFilePrefix> <numberOfPolygons> <startDate> <endDate> <verbose(y/n)>\n"+\
            "Calculates field averages limiting to number of polygons and dates(YYYY-MM-DD format) specified"
if len(sys.argv)<6:
   print usage
   sys.exit(1)


#--------------------------------------------------------------------------------------------------
#IMPORT
L7_SR_IC = ee.ImageCollection("LANDSAT/LE7_SR")
ca_clip = ee.Geometry.Polygon(
  [[[-124.4970703125, 41.91862886518304],
          [-124.5849609375, 40.41349604970198],
          [-123.77197265625, 38.548165423046584],
          [-122.01416015625, 36.20882309283712],
          [-120.8935546875, 34.59704151614417],
          [-120.5419921875, 34.252676117101515],
          [-117.79541015625, 32.95336814579932],
          [-117.13623046875, 32.11980111179328],
          [-114.08203125, 32.491230287947594],
          [-113.8623046875, 34.63320791137959],
          [-119.4873046875, 38.97649248553942],
          [-119.68505859375, 42.24478535602799],
          [-124.62890625, 42.32606244456202]]])

SouthValley = ee.Geometry.Polygon(
  [[[-119.86907958984375, 36.3369974283575],
          [-119.84710693359375, 35.91326583518851],
          [-119.4818115234375, 35.922163226259755],
          [-119.49005126953125, 36.33920989465195]]])

biggerArea = ee.Geometry.Polygon(
        [[[-120.45581817626953, 36.47028821197103],
          [-120.4482650756836, 36.16433387083854],
          [-120.21514892578125, 35.96034644747928],
          [-118.94421931130796, 36.00319596735811],
          [-118.91910552978516, 36.51196631988228]]])

fields = ee.FeatureCollection("ft:1GE0weDX4hKp_8Lt-MRySeDktJJ-gej7czjWPmzAx")
SIMS_ID_basemap = ee.Image("users/mhang/ca_30m_sid_poly_b5m_2014_12152016_ag_only")


#--------------------------------------------------------------------------------------------------
#FUNCTIONS
#function to calculate mode pixel value for each feature for SIMS ID
def getPixelValue(image):
  return image.reduceRegions(
    collection=fields_filter,
    reducer=ee.Reducer.mode().setOutputs(['SIMS_ID']),
    scale=30)

#function to calcualte NDVI
def calculateNDVI_L7(image):
  ndvi = image.normalizedDifference(['B4','B3'])
  #Filter the clouds
  ndvi = ndvi.updateMask(image.select('cfmask').eq(0))
  prop = ['system:time_start']
  return ndvi.copyProperties(image,prop)

#function to calculate mean NDVI
def getMeans(image):
  def reduce(f):
    return f.set('mean', image.reduceRegion(ee.Reducer.mean(), f.geometry(), 30))
  meansPolyMeans = outputPoly.map(reduce)

  def date(f):
    return f.set('date', ee.Date(image.get('system:time_start')).format('YYYY-MM-dd'))
  meansPolyMeans = meansPolyMeans.map(date)
  return meansPolyMeans

#function to filter clouds out
def filterClouds(image):
  #We just want the clear(zero value) pixels
  return image.updateMask(image.select('cfmask').eq(0))

#function to remove geometry at the end
def removeGeo(feature):
  return feature.select([".*"], None, False) #in python false needs to be False


vMode = sys.argv[5] 
if vMode == 'y':
  print "Verbose mode on"

#--------------------------------------------------------------------------------------------------

#Load the fields, this does not include SIMS ids
fieldsNum = int(sys.argv[2])
if vMode == 'y':
  print "Loading,clipping and limiting to %d fields." % fieldsNum

fields_filter = fields.filterBounds(biggerArea)
fields_filter = fields_filter.limit(fieldsNum)


#Add SIMS ID; intersected fields does not mess up SIMS ID
fields_SIMS = getPixelValue(SIMS_ID_basemap)

#Simplify the geometries to try and speed things up
maxErrorTolerance = 20
if vMode == 'y':
    print "Simplifying polygons with maxErrorTolerance of %d percent" % maxErrorTolerance
def simplify(f):
  return f.simplify(maxErrorTolerance)

fields_simplified = fields_SIMS.map(simplify)

#Set temporal and spatial parameters
outputPoly = fields_simplified
clipPolygon = outputPoly #ca_clip
tStart = sys.argv[3] #'2016-01-01'
tEnd = sys.argv[4] #'2016-12-31'

#Retrieve Image collection then filter,clip,calculate NDVI and filter clouds
if vMode == 'y':
  print "Loading and filtering image collection using %s to %s" % (tStart,tEnd)
L7_SR_NDVI = L7_SR_IC.filterDate(tStart, tEnd).filterBounds(clipPolygon).map(calculateNDVI_L7).select('nd')

#Filter the clouds
#L7_SR_NDVI = L7_SR_NDVI.map(filterClouds);


if vMode == 'y':
  print "Calculating field averages"
 
#Get the field averages
means = L7_SR_NDVI.map(getMeans).flatten()

#remove geometry
means = means.map(removeGeo)

#filter
means = means.filter(ee.Filter.neq('mean', None)).sort('date') #python uses none instead of null

fn = '%s_%d_polygons' % (sys.argv[1],fieldsNum)

#Export to CSV
taskParams = {
    'driveFolder' : 'Python EE Exports',
    'driveFileNamePrefix': fn,
    'fileFormat' : 'CSV'
}

#Status updates for export
MyTry = ee.batch.Export.table(means, 'lst_timeseries', taskParams)
MyTry.start()
state = MyTry.status()['state']
counter = 0
while state in ['READY', 'RUNNING']:
  if vMode == 'y':
    print "\r"+state + '... ' + str(counter),
  time.sleep(1)
  state = MyTry.status()['state']
  counter += 1
print 'Done.', MyTry.status()

