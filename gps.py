import android, time

# Convert meters to feet
def m_toft(m):
  return format(m * 3.2808, '.2f')

# convert d.dddd to d°m's"
def to_dms(point):
    p = str(point).split(".") 
    deg = int(p[0])
    dec = int(p[1])
    min = abs(int((float(point) - deg) * 60))
    sec = (abs(float(point) - deg) - min/60) * 3600
    return str(deg) + "°" + str(min) + "\'" + str(format(sec, '.4f')) + "\""

droid = android.Android() 
droid.startLocating()

print('searching for your location')
time.sleep(15)

loc = droid.readLocation().result

if not loc:
  loc = droid.getLastKnownLocation().result
  print('using last known location')
  try:
    n = loc['gps']
  except KeyError:
    n = loc['network']

prov = n['provider']
accr_m = n['accuracy']
accr_f = m_toft(accr_m)
lat_dd = n['latitude']
lon_dd = n['longitude']
lat_dms = to_dms(lat_dd)
lon_dms = to_dms(lon_dd)
speed_kph = n['speed']
alt_m = n['altitude']
alt_f = m_toft(alt_m)

print('source: ' + str(prov))
print('accuracy: ' + str(accr_m) + 'm / ' + str(accr_f) + 'ft')
print('lat/lon: ' + str(format(lat_dd, '.6f')) + ', '+ str(format(lon_dd, '.6f')))
print('         ' + lat_dms + ', ' + lon_dms)
print('speed: ' + str(speed_kph) + 'kph / ')
print('alt: ' + str(alt_m) + 'm / ' + str(alt_f) + 'ft')
#address = droid.geocode(lat, lon).result

droid.stopLocating()
    
