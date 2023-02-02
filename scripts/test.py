# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 14:25:21 2023

@author: kolja
"""

from scripts.request import Ephemeris
import datetime

PATH_LOG = 'scripts/log.txt'

import csv 
import pandas as pd

def read_testdata(path):
    with open(PATH_LOG) as file:
        fieldnames = file.readline().strip().split(',')
        data=[]
        reader = csv.DictReader(file, delimiter=',', fieldnames=fieldnames)
        for row in reader:
            dt = row.pop('timestamp')
            for k,v in row.items():
                row[k] = float(v)
            row['timestamp'] = datetime.datetime.fromisoformat(dt)
            data.append(row)
    return data

data = read_testdata(PATH_LOG)
eph = Ephemeris(**data[0])



df = pd.read_csv(PATH_LOG)