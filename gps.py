import android
import time
import requests
import sys
import gpxpy
import gpxpy.gpx

droid = android.Android()

# Time in seconds to warm up GPS
warm_up = 1

# convert meters to feet
def m_toft(m):
  return float(m) * 3.2808

# convert d.dddd to d°m's"
def to_dms(point):
    p = str(point).split(".") 
    deg = int(p[0])
    dec = int(p[1])
    min = abs(int((float(point) - deg) * 60))
    sec = (abs(float(point) - deg) - min/60) * 3600
    return str(deg) + "°" + str(min) + "\'" + str(format(sec, '.4f')) + "\""

# retrieve USGS altitude
def usgs_alt(lat, lon):
  url = 'http://nationalmap.gov/epqs/pqs.php'
  params = {'x':lon, 'y':lat, 'units':'Meters', 'output':'json'}
  try:
    r = requests.get(url, params=params)
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  if (r.status_code == 200):
    try:
      data = r.json()
    except e:
      print(e)
      sys.exit(1)

    alt = float(data['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation'])
#    print('USGS alt: ' + str(format(alt, '.1f')) + 'm / ' + str(format(m_toft(alt), '.1f')) + 'ft')
    return alt

# create class to store location data
class Data(object):
  def __init__(self, loc):
    self.prov = loc['provider']
    self.accr_m = format(loc['accuracy'], '.1f')
    self.accr_f = format(m_toft(self.accr_m), '.1f')
    self.lat_dd = format(loc['latitude'], '.6f')
    self.lon_dd = format(loc['longitude'], '.6f')
    self.lat_dms = to_dms(self.lat_dd)
    self.lon_dms = to_dms(self.lon_dd)
    self.speed_kph = format(int(loc['speed']) * 3.6, '.1f')
    self.speed_mph = format(float(self.speed_kph) * 0.621, '.1f')
    self.bearing = loc['bearing']
    self.direction = ''
    self.alt_m = loc['altitude']
    self.alt_f = format(m_toft(self.alt_m), '.1f')
    self.usgs_alt_m = format(usgs_alt(self.lat_dd, self.lon_dd), '.1f')
    self.usgs_alt_f = format(m_toft(self.usgs_alt_m), '.1f')

# format and print location
def print_location(data):
#  data = Data(loc)

  print('source: ' + data.prov)
  print('accuracy: ' + str(data.accr_m) + 'm / ' + str(data.accr_f) + 'ft')
  print('lat/lon: ' + str(data.lat_dd) + ', '+ str(data.lon_dd))
  print('         ' + data.lat_dms + ', ' + data.lon_dms)
  if data.prov == 'gps':
    print('speed: ' + str(data.speed_kph) + 'kph / ' + str(data.speed_mph) + 'mph')
    print('bearing: ' + str(data.bearing))
    print('alt: ' + str(data.alt_m) + 'm / ' + str(data.alt_f) + 'ft')

#  usgs_alt(data.lat_dd, data.lon_dd)

  droid.dialogCreateAlert("Results","line1\nline2")
  droid.dialogSetPositiveButtonText("Map")
  droid.dialogSetNeutralButtonText("Copy Lat/Lon")
  droid.dialogSetNegativeButtonText("Quit")
  droid.dialogShow()
  response = droid.dialogGetResponse().result
  droid.dialogDismiss()

  if 'which' in response:
    result = response['which']
    if result == 'positive':
      droid.viewMap(str(lat_dd) + ',' + str(lon_dd))  
    if result == 'neutral':
      # copy
      droid.setClipboard( str(lat_dd) + ',' + str(lon_dd))
#      write_gpx(data)
    if result == 'negative':
      sys.exit()

#  address = droid.geocode(lat_dd, lon_dd).result
#  print(address)
  
def bearing_to_box(deg):
  dir = int(deg)
  if dir >= 337.5 and dir <= 22.5:
    direction = 'North'
  if dir > 22.5 and dir <= 67.5:
    direction = 'Northeast'
  if dir > 67.5 and dir <= 112.5:
    direction = 'North'
  if dir > 112.5 and dir <= 157.5:
    direction = 'North'
  if dir > 157.5 and dir <= 202.5:
    direction = 'North'
  if dir > 247.5 and dir <= 292.5:
    direction = 'North'
  if dir > 292.5 and dir <= 337.5:
    direction = 'North'
  if dir > 325 and dir <= 22.5:
    direction = 'North'

  return direction

def start_gps(warm_up):
  droid.startLocating()
  print('searching for your location')
  droid.dialogCreateHorizontalProgress(
    'Starting GPS',
  	 'Please wait',
  	 warm_up
  )
  droid.dialogShow()
  p = 1
  while p <= warm_up:
    time.sleep(1)
    droid.dialogSetCurrentProgress(p)
    p+=1
  droid.dialogDismiss()

def get_location():
  result = droid.readLocation().result

  if not result:
    result = droid.getLastKnownLocation().result
  try:
    loc = result['gps']
  except KeyError:
    loc = result['network']

  data = Data(loc)
  return data

def write_gpx(data):

  gpx_file = open('/mnt/sdcard/test.gpx', 'w')

  gpx = gpxpy.gpx.GPX()

#  gpx = gpxpy.parse(gpx_file)

  gpx_track = gpxpy.gpx.GPXTrack()
  gpx.tracks.append(gpx_track)

  gpx_segment = gpxpy.gpx.GPXTrackSegment()
  gpx_track.segments.append(gpx_segment)

  gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(data.lat_dd, data.lon_dd, elevation=data.alt_m))

  gpx_file.write(gpx.to_xml())
  gpx_file.close()


start_gps(warm_up)
data = get_location()
droid.stopLocating()
print_location(data)

sys.exit()
    
