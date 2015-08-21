import android, time
import requests
import sys

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

def print_location(data):
  prov = n['provider']
  accr_m = n['accuracy']
  accr_f = m_toft(accr_m)
  lat_dd = n['latitude']
  lon_dd = n['longitude']
  lat_dms = to_dms(lat_dd)
  lon_dms = to_dms(lon_dd)
  speed_kph = int(n['speed']) * 3.6
  speed_mph = speed_kph * 0.621
  bearing = n['bearing']
  alt_m = n['altitude']
  alt_f = format(m_toft(alt_m), '.1f')

  print('source: ' + prov)
  print('accuracy: ' + str(format(accr_m, '.1f')) + 'm / ' + str(format(accr_f, '.1f')) + 'ft')
  print('lat/lon: ' + str(format(lat_dd, '.6f')) + ', '+ str(format(lon_dd, '.6f')))
  print('         ' + lat_dms + ', ' + lon_dms)
  if prov == 'gps':
    print('speed: ' + str(format(speed_kph, '.1f')) + 'kph / ' + str(format(speed_mph, '.1f')) + 'mph')
    print('bearing: ' + str(format(bearing, '.1f')))
    print('alt: ' + str(alt_m) + 'm / ' + str(alt_f) + 'ft')

  usgs_alt(lat_dd, lon_dd)
  droid.dialogCreateAlert("Results","line1\nline2")
  droid.dialogSetPositiveButtonText("Map It")
  droid.dialogSetNeutralButtonText("Copy LatLon")
  droid.dialogSetNegativeButtonText("Quit")
  droid.dialogShow()
  response = droid.dialogGetResponse().result
  droid.dialogDismiss()
  sys.exit()

  droid.viewMap(str(lat_dd) + ',' + str(lon_dd))
#  address = droid.geocode(lat_dd, lon_dd).result
#  print(address)

def bearing_to_box(deg):
  dir = int(deg)

droid = android.Android()
droid.startLocating()
print('searching for your location')
droid.dialogCreateHorizontalProgress(
	 'Starting GPS',
	 'Please wait',
	 15
)
droid.dialogShow()
p = 1
while p < 16:
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

droid.stopLocating()
print_location(n)


sys.exit()

