#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import xlrd
import codecs
import time
from urllib2 import urlopen
from urllib2 import quote
import json
import subprocess

def yes_or_no(message):
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    choice = raw_input("{0}(yes/no)".format(message)).lower()

    if choice in yes:
        return True
    else:
        return False

def check_location(name, location):
    url = 'http://maps.google.com/?q={0},{1}'.format(location['lat'], location['lng'])
    try:
        print(u'open location for {0}\n'
              'at latitude:{1}\t'
              ' longitude:{2}'.format(name, location['lat'], location['lng']))
        ''' xdg-open is for linux, open is for mac '''
        #subprocess.Popen(['xdg-open', url])
        subprocess.Popen(['open', url])
    except OSError:
        print 'Please open a browser on: '+url
    
    return yes_or_no("Is this location OK?")

'''TODO remove some machine un-friendly character in name'''
def auto_better_name(name):
    pass

def get_coordinate(name):
    '''get name's longitude and latitude'''
    googleapi = 'http://maps.googleapis.com/maps/api/geocode/json'
    url = u'{0}?address={1}&sensor=false'.format(googleapi, name + u'+,上海')
    request = urlopen(url.encode('utf8'))
    gmap_return = json.load(request)
    #print json.dumps(result, indent=4, sort_keys=True)
    
    '''if google map return is more than one ressults, we should check the result
    '''
    location = gmap_return['results'][0]['geometry']['location']
    location['formatted_address'] = gmap_return['results'][0]['formatted_address']

    if len(gmap_return['results']) != 1:
        if not check_location(name, gmap_return['results'][0]['geometry']['location']):
            default = auto_better_name(name)
            msg = u'can\'t get {0}\'s location!'.format(name) +\
                ' put in a more machine friendly location:'
            print(msg)
            better_name = raw_input(default.encode('utf8')
                                    + chr(8) * len(default.encode('utf8'))).decode('utf-8')
            if not better_name:
                better_name = default
            return get_coordinate(better_name)
        else:
            return location
    else:
        return location

def read_data(xls_file_name):
    assert xls_file_name, "xls_file_name is empty."

    workbook = xlrd.open_workbook(xls_file_name)
    buses = []
    for worksheet_name in workbook.sheet_names():
        worksheet = workbook.sheet_by_name(worksheet_name)
        print worksheet.ncols, worksheet.nrows
        row = 1
        while row < worksheet.nrows:
            bus_line = {}
            bus_line['name'] = worksheet.cell_value(row, 1)
            bus_line['time'] = worksheet.cell_value(row, 2)
            bus_line['station'] = [worksheet.cell_value(row, 3),
                                   worksheet.cell_value(row, 4),
                                   worksheet.cell_value(row, 5)]
            buses.append(bus_line)
            row += 1
    return buses

'''
get geography data for station in bus line
'''
def get_geo(buses):
    assert buses, "input buses list is empty."

    buses_geo = []
    for bus_line in buses:
        stations = parse_station(bus_line['station'])
        station_info = {}
        station_infos = []
        for station_name in stations:
            station_info['name'] = station_name
            station_info['location'] = get_coordinate(station_name)
            station_infos.append(station_info)
        bus_line['station'] = station_infos
        buses_geo.append(bus_line)
    return buses_geo

def parse_station(stations):
    assert stations, "input stations is empty."
    
    print repr(stations).decode("unicode_escape").encode("utf-8")
    stations_parsed = []
    for s in stations:
        if s and (u'直驶' not in s):
            if u'、' not in s:
                stations_parsed.append(s)
            else:
                stations_parsed.extend(s.split(u'、'))
    print repr(stations_parsed).decode("unicode_escape").encode("utf-8")
    return stations_parsed

def main():
    buses = read_data('table1a_1.xls')
    buses_geo = get_geo(buses)

#main()
print get_coordinate(u'长阳路1681号临青路口')
