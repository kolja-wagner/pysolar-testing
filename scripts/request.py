# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 12:08:03 2023

@author: kolja
"""

URL_TEMPLATE = "https://aa.usno.navy.mil/calculated/ssconf?date=2007-02-18&time=15%3A13%3A01.000&intv_mag=1.00&intv_unit=1&reps=1&lat=42.206&lon=-71.382&label=pysolar+example&height=0&submit=Get+Data"

import urllib.request
import urllib.parse

from dataclasses import dataclass
import datetime 

from astropy.coordinates import EarthLocation,SkyCoord, AltAz
from astropy.time import Time
from astropy import units as u

from pysolar import solar


@dataclass
class Ephemeris:
    latitude: float
    longitude: float
    timestamp: datetime.datetime
    height: int = 0
    
    altitude: float =0
    azimuth:  float =0

def dict_to_query(q):
    out = []
    for k,v in q.items():
        tmp = str(k)+'='
        if  isinstance(v, str):
            tmp +=v
        else:
            tmp += v[0].replace(' ','+').replace(':','%3A')
        out.append(tmp)
    return '&'.join(out)

def generate_url(datum: Ephemeris):
    parseResult = urllib.parse.urlparse(URL_TEMPLATE)
    query = urllib.parse.parse_qs(parseResult.query)

    # update query
    query['date'] = str(datum.timestamp.date())
    query['time'] = str(datum.timestamp.time())
    query['lat'] = str(datum.latitude)
    query['lon'] = str(datum.longitude)
    query['height'] = str(datum.height)

    queryNew = dict_to_query(query)
    parseResultNew = parseResult._replace(query=queryNew)
    urlNew = urllib.parse.urlunparse(parseResultNew)
    return urlNew


def get_request(url=None):
    if url is None:
        url = URL_TEMPLATE
    
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        lines = response.readlines()

    # see whole dataset
    # import pprint
    # pprint.PrettyPrinter().pprint(lines[167:197])

    # see header and sun data
    # print(lines[181].decode('UTF-8'))
    # print(lines[184].decode('UTF-8'),'\n')

    result = lines[184].decode('UTF-8')
    # tokens = [x for x in result.split(' ') if x not in ' ']
    
    dec1 = int(  result[10:13])
    dec2 = float(result[13:17])
    
    ra1 = int(result[19:22].replace(' ',''))
    ra2 = int(result[23:26])
    
    dec = f"{dec1}h{dec2}m"
    ra = f"{ra1}°{ra2}'"

    return dec, ra



def convert_coord(lat, lon, dt, dec, ra, height=0):
    observing_location = EarthLocation(lat=lat, lon=lon, height=height*u.m)  
    observing_time = Time(dt)  
    aa = AltAz(location=observing_location, obstime=observing_time)
    coord = SkyCoord(dec, ra).transform_to(aa)
    return coord.alt.degree, coord.az.degree


def get_usno(lat: float, lon: float, dt: datetime.datetime, height: float=0):
    eph = Ephemeris(latitude=lat,
                    longitude=lon,
                    timestamp=dt,
                    height=height)
    url = generate_url(eph)
    dec, ra = get_request(url)
    alt, az = convert_coord(lat, lon, dt, dec, ra, height)
    
    eph.altitude = alt
    eph.azimuth = az
    return eph

def get_usno2(eph: Ephemeris):
    
    url = generate_url(eph)
    dec, ra = get_request(url)
    alt, az = convert_coord(eph.latitude, 
                            eph.longitude, 
                            eph.timestamp, 
                            dec, ra, 
                            eph.height)
    
    eph.altitude = alt
    eph.azimuth = az
    return eph



def main():
    latitude = 42.206
    longitude = -71.382
    height = 50 # m
    timestamp = datetime.datetime(2007, 2, 18, 15, 13, 1, 130320, tzinfo=datetime.timezone.utc)
    
    result = get_usno(latitude, longitude, timestamp, height)

    print(result)
    
    # comparison
    pyAlt =  solar.get_altitude(latitude, longitude, timestamp)
    pyAz =  solar.get_azimuth(latitude, longitude, timestamp)
    
    print(pyAlt, pyAz)

if __name__ == "__main__":
    main()
