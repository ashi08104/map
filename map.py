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

def draw(kml_filename, data):
    '''
    draw the date to kml file
    '''
    #print repr(data).decode("unicode_escape").encode("utf-8")
    for bus_line in data:
        bus_line_info = bus_line['name'] + bus_line['time']
        for station in bus_line['station']:
            info_s = bus_line_info
            info_s += station['name']
            if u'桂林' in info_s:
                print info_s
            coord = (station['location']['lng'], station['location']['lat'])
            draw_station(info_s, coord)
        
    kml.save(kml_filename)

def draw_station(info, coord):
    kml.newpoint(name = info,
                 coords = [coord])
def main():
    #TODO read from commandline
    msg1 = "Do we have geography data in save_geo.data?"
    read_from_file = yes_or_no(msg1)

    if read_from_file == False:
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
