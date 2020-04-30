#!/usr/bin/env python3
import csv
import datetime
import json
import os.path
import numpy as np
import sqlite3

def load_csv(fname):
    """Load a csv file in."""
    with open(fname) as fp:
        csv_reader = csv.DictReader(fp)
        return [line for line in csv_reader]

def load_weather(fname):
    """Load a fixed width field."""
    with open(fname) as fp:
        # Get the header
        lines = [line.split() for line in fp]
        cols = lines[0]
        # Generate the dictionary
        #
        # Requires this long block because of inconsistencies
        # in the input format
        return [
            {
                'STN--': line[0],
                'WBAN': line[1],
                'YEARMODA': line[2],
                'TEMP': line[3],
                'DEWP': line[5],
                'SLP': line[7],
                'STP': line[9],
                'VISIB': line[11],
                'WDSP': line[13],
                'MXSPD': line[15],
                'GUST': line[16],
                'MAX': line[17],
                'MIN': line[18],
                'PRCP': line[19],
                'SNDP': line[20],
                'FRSHTT': line[21],
            }
            for line in lines[1:]
        ]

def main():
    # Load list of stations
    stations = load_csv('datasets/weather/isd-history.csv')
    stations = [s for s in stations if s['CTRY'] == 'US']

    # Load weather data
    new_stations = []
    for s in stations:
        fname = f'datasets/weather/{s["USAF"]}-{s["WBAN"]}-2018.op'
        if os.path.exists(fname):
            s['WEATHER'] = load_weather(fname)
            new_stations.append(s)
    stations = new_stations

    # Load accident data
    accidents = load_csv('datasets/accidents/ACCIDENT.csv')

    # Create the database
    con = sqlite3.connect('wcvaarr.db')
    c = con.cursor()
    c.executescript("""CREATE TABLE weather
                       (station_id text, date text, temperature text,
                        dew_point text, precipitation text, visibility text,
                        windspeed real, indicators text);
                       CREATE TABLE station
                       (id text, name text, latitude real, longitude real);
                       CREATE TABLE accident
                       (date text, latitude real, longitude real, fatals integer);""")
    con.commit()

    # Insert the accident data
    accidents = [
        {
            'DATE': '%i%.2i%.2i' % (int(accident['YEAR']),
                                    int(accident['MONTH']),
                                    int(accident['DAY'])),
            'LATITUDE': float(accident['LATITUDE']),
            'LONGITUDE': float(accident['LONGITUD']),
            'FATALS': int(accident['FATALS']),
        }
        # Excludes drunk driving
        for accident in accidents if accident['DRUNK_DR'] != '1'
    ]
    c.executemany("""INSERT INTO accident (date, latitude, longitude, fatals)
                     VALUES (:DATE, :LATITUDE, :LONGITUDE, :FATALS)""", accidents)

    # Insert the stations
    stations = [
        {
            'ID': f'{station["USAF"]}-{station["WBAN"]}',
            'NAME': station['STATION NAME'],
            'LATITUDE': station['LAT'],
            'LONGITUDE': station['LON'],
            'WEATHER': station['WEATHER'],
        }
        # Only add a station if we have weather data for it
        for station in stations if 'WEATHER' in station
    ]
    c.executemany("""INSERT INTO station (id, name, latitude, longitude)
                     VALUES (:ID, :NAME, :LATITUDE, :LONGITUDE)""", stations)

    # Insert the weather data
    weather = [
        {
            'STATION_ID': station['ID'],
            'DATE': w['YEARMODA'],
            # TODO
            'TEMPERATURE': w['TEMP'],
            'DEW_POINT': w['DEWP'],
            'PRECIPITATION': w['PRCP'],
            'VISIBILITY': w['VISIB'],
            'WINDSPEED': w['WDSP'],
            'INDICATORS': w['FRSHTT'],
        }
        for station in stations for w in station['WEATHER']
    ]
    c.executemany("""INSERT INTO weather (station_id, date, temperature,
                                          dew_point, precipitation, visibility, windspeed, indicators)
                     VALUES (:STATION_ID, :DATE, :TEMPERATURE, :DEW_POINT,
                             :PRECIPITATION, :VISIBILITY, :WINDSPEED,
                             :INDICATORS)""", weather)

    # Write the data
    con.commit()

    # Example usage of data:
    #
    con = sqlite3.connect('wcvaarr.db')
    # This is so we can access data like a dict
    con.row_factory = sqlite3.Row
    c = con.cursor()
    c.execute("""SELECT w.station_id, w.date, w.temperature, s.latitude,
                        s.longitude
                 FROM weather AS w JOIN station AS s ON w.station_id = s.id""")
    result = c.fetchall()
    result = [dict(r) for r in result]
    print('Total weather records:', len(result))
    print(json.dumps(result[:10], indent=4))

if __name__ == '__main__':
    main()
