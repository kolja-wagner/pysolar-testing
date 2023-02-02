from scripts.request import Ephemeris, generate_url, get_request, convert_coord

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
    for i in range(10000):
        try:
            eph = generateRandomLocation()
            EphToFile(eph, f'scripts/{filename}.txt')
            suc +=1

        except urllib.request.HTTPError:
            fail +=1
            
        print("iteration",i, f"(sucess: {suc}/fail: {fail})")

    
if __name__ == '__main__':
    main()