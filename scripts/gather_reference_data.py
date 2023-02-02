# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 20:52:18 2023

@author: kolja
"""

URL_TEMPLATE = "https://aa.usno.navy.mil/calculated/positions/topocentric?ID=AA&task=9&body=10&date=2023-06-29&time=00%3A00%3A00.000&intv_mag=1.00&intv_unit=2&reps=24&lat=0.0000&lon=0.0000&label=&height=0&submit=Get+Data"


## todo: query flexibility for ranges
## handle timezone, expects utc

import urllib.parse
import urllib.request
import urllib.error 
from dataclasses import dataclass

import datetime
import pandas as pd 

import csv
import pathlib
PATH_DATA = pathlib.Path('../data/')


@dataclass
class InputData:
    latitude: float
    longitude: float
    timestamp: datetime.datetime
    height: int = 0
    
    altitude: float = None
    azimuth:  float = None


def get_template_query() -> dict:
    parseResults = urllib.parse.urlparse(URL_TEMPLATE)
    query = urllib.parse.parse_qs(parseResults.query)
    return query


def build_query(param: InputData) -> dict:
    query = get_template_query()
    query['date'] = str(param.timestamp.date())
    query['time'] = str(param.timestamp.time())
    query['lat'] = str(param.latitude)
    query['lon'] = str(param.longitude)
    query['height'] = str(param.height)
    for k,v in query.items():
        if isinstance(v, list):
            query[k] = v[0]
    return query


def build_url(query: dict) -> str:
    parse =  urllib.parse.urlparse(URL_TEMPLATE)
    newQuery = urllib.parse.urlencode(query)
    newParse = parse._replace(query=newQuery)
    return urllib.parse.urlunparse(newParse)


def get_response(url) -> list[str]:
    if url is None:
        url=URL_TEMPLATE
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        lines = response.readlines()
    result = [l.decode("UTF-8") for l in lines[167:203]]
    return result


def deg_to_dec(deg: float, minute: float,second: float)-> float:
    deg = int(deg)
    minute=int(minute)
    second= float(second)
    return deg + minute/60 + second/3600
    

def parse_latLon(string: str):
    sign = (-1 if ((string[0] == "W") or (string[0]== "S")) else 1)
    magnitude = deg_to_dec(*string[1:].strip().split(' '))
    return sign*magnitude
                           
def parse_location(line: str) -> tuple[float, float]:
    # Example location:
    # Location:     0°00&#39;00.0&#34;,   0°00&#39;00.0&#34;,     0m             
    line = line.replace('&#39;',' ').replace('&#34;,',' ').replace('°',' ').strip()
    longitude = parse_latLon(line[11:23])
    latitude  = parse_latLon(line[25:36])
    height = int(line[37:-1])
    return {'latitude':latitude, 'longitude': longitude, 'height':height}

def parse_line(line: str)-> dict:
    # EXAMPLELINE: 
    # Datetime                    Zenith         Azimuth         Distance AU
    # 2020 Jun 10 12:00:00.0      23 03 55.4     359 44 17.9     1.015278962
    
    step = line.split('     ')
    dt = datetime.datetime.strptime(step[0]+'+0000',"%Y %b %d %X.%f%z")
    zenith = deg_to_dec(*step[1].strip().split(' '))
    azimuth = deg_to_dec(*step[2].strip().split(' '))
    return {"timestamp":dt, "zenith":zenith, "azimuth":azimuth}


def parse_response(result: list[str])-> list[dict]:
    data = []
    
    # parse header
    for line in result:
        if "Location:" in line:
            break
    coords = parse_location(line)
    
    # parse data
    header = '   Date        Time          Zenith          Azimuth         Distance\n'
    startIndex = result.index(header)+3    
    for line in result[startIndex:]:
        data.append(coords | parse_line(line))
        
    return data
    

def get_reference_data(lat: float, lon: float,
                       dt: datetime.datetime, height:int=0):
    params = InputData(lat, lon, dt, height)
    return get_reference(params)
    
def get_reference(params: InputData):
    query = build_query(params)
    url = build_url(query)
    response = get_response(url)
    data = parse_response(response)
    return data
    

def create_file(filename: pathlib.Path, data):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    

def save_data(filepath: pathlib.Path, data):
    if not filepath.is_file():
        create_file(filepath, data)
        return
                
    with open(filepath, 'a',newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerows(data)
  
    
def load_data(filepath: pathlib.Path):
    if not filepath.is_file():
        return None
    
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)
    
    
import random 
def generate_random_location(latitude=None, longitude=None, height=0):    
    if latitude is None:
        latitude = random.randrange(-90, 90)
    if longitude is None:
        longitude = random.randrange(-180, 180)
        
    dt = datetime.datetime(random.randrange(2010,2021), # year
                           random.randrange(1,13),        # month
                           random.randrange(1,29),          # day
                           0,#random.randrange(0,24),       # hour
                           0,#random.randrange(0,60)        # minute
                           0,#random.randrange(0,60)        # second
                           tzinfo=datetime.timezone.utc) #tz

    return InputData(latitude, longitude, dt, height)

    
def run_test():    
    test = InputData(30,161,datetime.datetime(2020,10,7,0,0))    
    data = get_reference(test)
    path = pathlib.Path('reference_test.csv')
    save_data(path, data)
    df = pd.DataFrame(load_data(path))
    # df.info()
    # print(df.head()) 

def run_random():
    path = PATH_DATA / 'log_rLoc_allHour.csv'
    fails = 0
    for i in range(5000):
        try:
            params= generate_random_location()
            data = get_reference(params)
            save_data(path, data)
            print(f'iteration {i}, ({params.latitude: 4.3f},{params.longitude: 4.2f}), {params.timestamp.date()}')
        except (urllib.request.HTTPError, urllib.error.URLError):
            fails += 1
            print(f'iteration {i}, failed {fails} times')

def main():
    # run_test()
    
    # run_random()

if __name__ == '__main__':
    main()
