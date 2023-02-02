# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 10:52:45 2023

@author: kolja
"""

from astropy.coordinates import EarthLocation,SkyCoord, AltAz
from astropy.time import Time
from astropy import units as u

from pysolar import solar
import datetime

def convert_coord(lat, lon, dt, dec, ra, height=0):
    observing_location = EarthLocation(lat=lat, lon=lon, height=height*u.m)  
    observing_time = Time(date)  
    aa = AltAz(location=observing_location, obstime=observing_time)
    coord = SkyCoord(dec, ra).transform_to(aa)
    return coord.az.degree, coord.alt.degree


latitude = 42.206
longitude = -71.382
date = datetime.datetime(2007, 2, 18, 15, 13, 1, 130320, tzinfo=datetime.timezone.utc)
declination, RA = '22h06m', '-11°37'
res = convert_coord(latitude, longitude, date, declination, RA)
print(res)

print("pysolar al",solar.get_altitude(latitude, longitude, date))
print("pysolar az",solar.get_azimuth(latitude, longitude, date))
