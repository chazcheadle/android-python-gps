import android
import time
import requests
import sys
import gpxpy
import gpxpy.gpx

droid = android.Android()

# Time in seconds to warm up GPS
warm_up = 15

def m_toft(m):
  return m * 3.2808

# convert d.dddd to d°m's"
def to_dms(point):
    p = str(point).split(".") 
    deg = int(p[0])
    dec = int(p[1])
    min = abs(int((float(point) - deg) * 60))
    sec = (abs(float(point) - deg) - min/60) * 3600
    return str(deg) + "°" + str(min) + "\'" + str(format(sec, '.4f')) + "\""

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

    alt = data['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']
    print('USGS alt: ' + str(format(alt, '.1f')) + 'm / ' + str(format(m_toft(alt), '.1f')) + 'ft')

class Data(object):
  def __init__(self, loc):
    self.prov = loc['provider']
    self.accr_m = loc['accuracy']
    self.accr_f = m_toft(self.accr_m)
    self.lat_dd = loc['latitude']
    self.lon_dd = loc['longitude']
    self.lat_dms = to_dms(self.lat_dd)
    self.lon_dms = to_dms(self.lon_dd)
    self.speed_kph = int(loc['speed']) * 3.6
    self.speed_mph = self.speed_kph * 0.621
    self.bearing = loc['bearing']
    self.alt_m = loc['altitude']
    self.alt_f = format(m_toft(self.alt_m), '.1f')

def print_location(loc):
  data = Data(loc)
  accr_m = loc['accuracy']
  accr_f = m_toft(accr_m)
  lat_dd = loc['latitude']
  lon_dd = loc['longitude']
  lat_dms = to_dms(lat_dd)
  lon_dms = to_dms(lon_dd)
  speed_kph = int(loc['speed']) * 3.6
  speed_mph = speed_kph * 0.621
  bearing = loc['bearing']
  alt_m = loc['altitude']
  alt_f = format(m_toft(alt_m), '.1f')

  print('source: ' + data.prov)
  print('accuracy: ' + str(format(accr_m, '.1f')) + 'm / ' + str(format(accr_f, '.1f')) + 'ft')
  print('lat/lon: ' + str(format(lat_dd, '.6f')) + ', '+ str(format(lon_dd, '.6f')))
  print('         ' + lat_dms + ', ' + lon_dms)
  if data.prov == 'gps':
    print('speed: ' + str(format(speed_kph, '.1f')) + 'kph / ' + str(format(speed_mph, '.1f')) + 'mph')
    print('bearing: ' + str(format(bearing, '.1f')))
    print('alt: ' + str(alt_m) + 'm / ' + str(alt_f) + 'ft')

  usgs_alt(lat_dd, lon_dd)

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
      write_gpx(data)
    if result == 'negative':
      sys.exit()

#  address = droid.geocode(lat_dd, lon_dd).result
#  print(address)
  
def bearing_to_box(deg):
  dir = int(deg)

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
  loc = droid.readLocation().result

  if not loc:
    loc = droid.getLastKnownLocation().result
    print('        using last known location')
  try:
    n = loc['gps']
  except KeyError:
    n = loc['network']
  return n

def write_gpx(data):

  gpx_file = open('/mnt/sdcard/test.gpx', 'w')

  gpx = gpxpy.gpx.GPX()

  # Create first track in our GPX:
  gpx_track = gpxpy.gpx.GPXTrack()
  gpx.tracks.append(gpx_track)

  # Create first segment in our GPX track:
  gpx_segment = gpxpy.gpx.GPXTrackSegment()
  gpx_track.segments.append(gpx_segment)

  # Create points:
  gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(data.lat_dd, data.lon_dd, elevation=data.alt_m))

  gpx_file.write(gpx.to_xml())

  gpx_file.close()


loc = start_gps(warm_up)
droid.stopLocating()
print_location(loc)


sys.exit()
    
