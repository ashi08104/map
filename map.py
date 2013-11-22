#!/usr/bin/python
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

from read_data_map import *

kml = simplekml.Kml()    

def yes_or_no(message):
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    choice = raw_input("{0}(yes/no)".format(message)).lower()

    if choice in yes:
        return True
    else:
        return False

# def draw(file_name, data):
#     '''
#     draw the data to map
#     '''
#     i = 0
#     for bus in data:
#         #bus info: [#no., name, time]
#         bus_info = bus[:3]
#         start = bus[3]
#         stations = bus[4].split(',')
#         if u'(直驶)' in stations:
#             stations = []
#         end = bus[5]
#         #draw_kml_bus_line(bus_info, start, end, stations)
#         draw_station_start(bus_info, start)
#         print i
#         i = i + 1

#     kml.save(file_name)    

def draw(kml_filename, data):
    '''
    draw the date to kml file
    '''
    for bus_line in data:
        #TODO change data to a more readable and mnemonic structure
        bus_line_info = bus_line['name'] + bus_line['time']
        for station in bus_line['station']:
            info_s = bus_line_info
            info_s += station['name']
            coord = (station['location']['lng'], station['location']['lat'])
            draw_station(info_s, coord)
        
    kml.save(kml_filename)

def draw_station(info, coord):
    kml.newpoint(name = info,
                 coords = [coord])


#this function is deprecated. we should get geo date from previous step
#not from google map online.
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

def main():
    #TODO read from commandline
    msg1 = "Do we have geography data in save_geo.data?"
    read_from_file = yes_or_no(msg1)

    if read_from_file == False:
        #TODO read data from xls by xlrd module
        data = read_data('table4.xls')
        geo_data = get_geo(data)

        msg2 = "Do we want to save geography data into locae file?"
        save_geo_data = yes_or_no(msg2)
        if save_geo_data == True:
            cPickle.dump(geo_data, open('save_geo.data', 'wb')) 
    else:
        geo_data = cPickle.load(open('save_geo.data', 'rb'))

    draw('1.kml', geo_data)

main()
