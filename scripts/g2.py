# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 12:08:03 2023

@author: kolja
"""

URL_TEMPLATE_OLD = "https://aa.usno.navy.mil/calculated/ssconf?date=2007-02-18&time=15%3A13%3A01.000&intv_mag=1.00&intv_unit=1&reps=1&lat=42.206&lon=-71.382&label=pysolar+example&height=0&submit=Get+Data"

URL_TEMPLATE = "https://aa.usno.navy.mil/calculated/positions/topocentric?ID=AA&task=9&body=10&date=2023-06-29&time=00%3A00%3A00.000&intv_mag=1.00&intv_unit=2&reps=24&lat=0.0000&lon=0.0000&label=&height=0&submit=Get+Data"


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
    parseResult = urllib.parse.urlparse(URL_TEMPLATE_OLD)
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
        url = URL_TEMPLATE_OLD
    
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


import urllib.request
import datetime 
import random

def generateRandomLocation():
    latitude = random.randrange(-90, 90)
    longitude = random.randrange(-180, 180)
    elevation = 50
    
    # dt = datetime.datetime(2007, 3, 18, 15, 13, 1, 130320, tzinfo=datetime.timezone.utc)

    dt = datetime.datetime(random.randrange(2005,2020),  #y
                          random.randrange(1, 13),      #m
                          random.randrange(1, 28),      #d
                          random.randrange(0, 24),      #h
                          random.randrange(0, 60),      #m
                          random.randrange(0, 60),       #s
                          tzinfo=datetime.timezone.utc) #tz
    
    eph = Ephemeris(latitude, longitude, dt, elevation)
    url = generate_url(eph)
    # print(url)
    dec, ra = get_request(url)
    # print(dec, ra)
    eph.altitude, eph.azimuth = convert_coord(latitude, 
                                              longitude, 
                                              dt, dec, ra, 
                                              elevation)
    return eph

def EphToFile(eph, filename):
    with open(filename, 'a') as log:
        log.write(f"{eph.timestamp},{eph.latitude},{eph.longitude},{eph.height},{eph.azimuth},{eph.altitude}\n")
        


def main():
    filename='log_allRandom_long.txt'
    suc, fail = 0,0
    for i in range(10):
        try:
            eph = generateRandomLocation()
            EphToFile(eph, f'scripts/{filename}.txt')
            suc +=1

        except urllib.request.HTTPError:
            fail +=1
            
        print("iteration",i, f"(sucess: {suc}/fail: {fail})")

    
if __name__ == '__main__':
    main()
