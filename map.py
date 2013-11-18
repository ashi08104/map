#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import codecs
import time
from urllib2 import urlopen
from urllib2 import quote
import json
#https://pypi.python.org/pypi/simplekml
import simplekml
import random
import cPickle
import subprocess

kml = simplekml.Kml()    

def get_coordinate(name):
    '''get name's longitude and latitude'''
    googleapi = 'http://maps.googleapis.com/maps/api/geocode/json'
    url = u'{0}?address={1}&sensor=false'.format(googleapi, name + u'+,上海')
    request = urlopen(url.encode('utf8'))
    result = json.load(request)
    #print result
    location_raw = result['results'][0]['geometry']['location']
    location = [location_raw['lng'], location_raw['lat']]
    return location

def check_location(name, location):
    url = 'http://maps.google.com/?q={0},{1}'.format(location[1], location[0])
    try:
        print(u'open location for {0}\n'
              'at latitude:{1}\t'
              ' longitude:{2}'.format(name, location[1], location[0]))
        subprocess.Popen(['xdg-open', url])
    except OSError:
        print 'Please open a browser on: '+url
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    
    save_result = False
    msg = "Is this location OK?"
    choice = raw_input("{0}(yes/no)".format(msg)).lower()
    if choice in yes:
        return True
    else:
        return False
                                                
def read_bus(filename):
    '''
    read bus infomation from file
    '''
    file = codecs.open(filename, 'r', 'utf-8')
    #check whether file read failed.
    data = []
    for line in file.readlines():
        data.append(line.split())
    return data

def draw(file_name, data):
    '''
    draw the data to map
    '''
    i = 0
    for bus in data:
        #bus info: [#no., name, time]
        bus_info = bus[:3]
        start = bus[3]
        stations = bus[4].split(',')
        if u'(直驶)' in stations:
            stations = []
        end = bus[5]
        draw_kml_bus_line(bus_info, start, end, stations)
        print i
        i = i + 1

    kml.save(file_name)    
    
def draw_kml_bus_line(info, start, end, stations):
    start_geo = [start]
    start_geo.append(get_coordinate(start))
    end_geo = [end]
    end_geo.append(get_coordinate(end))
    station_geos = []
    if stations:
        for station in stations:
            station_geo = [station]
            station_geo.append(get_coordinate(station))
            station_geos.append(station_geo)
    #draw bus line
    coords = [(start_geo[1][0], start_geo[1][1])]
    if station_geos:
        for station_geo in station_geos:
            coords.append((station_geo[1][0],
                           station_geo[1][1]))
    coords.append((end_geo[1][0], end_geo[1][1]))
    kml.newlinestring(name = info[1],
                      description = 'No.' + info[0] + ' time:' + info[2],
                      coords = coords)
    
    #draw bus stations
    kml.newpoint(name = start_geo[0],
                 coords = [(start_geo[1][0],
                            start_geo[1][1])])
    if station_geos:
        for station_geo in station_geos:
            kml.newpoint(name = station_geo[0],
                         coords = [(station_geo[1][0],
                                    station_geo[1][1])])
    kml.newpoint(name = end_geo[0],
                 coords = [(end_geo[1][0],
                            end_geo[1][1])])

def get_geo_data(data):
    '''
    geo_data format:
   [
    [
     [no., bus line name, time],
     [[station, station_geo_name, [longitude, latitude]],
      [station, station_geo_name, [longitude, latitude]],
      ...
     ]
    ],
    ...
   ]
     
    '''
    geo_data = []
    for bus in data:
        bus_line = []
        #put no. bus name and time to geo_data first
        bus_line.append(bus[0:3])
        geo_item = []
        for item in bus[3:]:
            if u'(直驶)' not in item:
                #some item include several station divided by ','
                item_sp = item.split(',')
                for station in item_sp:
                    station_geo_name = station
                    location = get_coordinate(station_geo_name)
                    #google map api would run into 'out of limit' without sleep
                    time.sleep(1)
                    while check_location(station_geo_name, location) != True:
                        msg = u'can\'t get {0}\'s location!'.format(station_geo_name) +\
                        'put in a more machine friendly location:'
                        print(msg)
                        station_geo_name = raw_input().decode('utf-8')
                        location = get_coordinate(station_geo_name)
                    geo_item.append([station, station_geo_name, location])
        bus_line.append(geo_item)
        geo_data.append(bus_line)
    return geo_data

def main():
    #TODO read from commandline
    # raw_input returns the empty string for "enter"
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    
    save_result = False
    msg = "Do we have geography data in save_geo.data?"
    choice = raw_input("{0}(yes/no)".format(msg)).lower()
    if choice in yes:
        save_result = True
    elif choice in no:
        save_result = False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")

    if save_result == False:
        data = read_bus('workbook_short.txt')
        geo_data = get_geo_data(data)
        cPickle.dump(geo_data, open('save_geo.data', 'wb')) 
    else:
        geo_data = cPickle.load(open('save_geo.data', 'rb'))
        print geo_data
    #draw('1.kml', data)

main()
