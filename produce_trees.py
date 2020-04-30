
import json
import math
import random
import sys
import sqlite3

import kdtree


def load_data(db_file):
    """Load the data in from the SQLite DB."""
    con = sqlite3.connect('wcvaarr.db')
    con.row_factory = sqlite3.Row
    c = con.cursor()
    c.execute("""SELECT s.latitude, s.longitude, w.date, w.temperature,
                        w.dew_point, w.precipitation, w.visibility, w.windspeed,
                        w.indicators
                 FROM weather AS w JOIN station AS s ON w.station_id = s.id""")
    weather_result = c.fetchall()
    weather_result = [
        {
            'latitude': float(res['latitude']),
            'longitude': float(res['latitude']),
            'date': int(res['date']),
            'temperature': float(res['temperature']),
            'dew_point': float(res['dew_point']),
            # Precipitation is separated into a tuple for easier usage
            'precipitation': (res['precipitation'][:-1], res['precipitation'][-1:]),
            'visibility': float(res['visibility']),
            'windspeed': float(res['windspeed']),
            'indicators': res['indicators']
        }
        for res in weather_result
    ]
    c.execute('SELECT latitude, longitude, date, fatals FROM accident')
    accident_result = c.fetchall()
    accident_result = [
        {
            'latitude': float(res['latitude']),
            'longitude': float(res['longitude']),
            'date': int(res['date']),
            'fatals': int(res['fatals']),
        }
        for res in accident_result
    ]
    return (weather_result, accident_result)

def main():
    # Calculate risk analysis
    weather_data, accident_data = load_data('wcvaarr.db')
    print('PRIMA')
    weather_tree = kdtree.KDTree(points=weather_data,
                                 features=['latitude', 'longitude', 'date'])
    accident_tree = kdtree.KDTree(points=accident_data,
                                  features=['latitude', 'longitude', 'date'])
    # Write the data out to file
    data = weather_tree.root.flatten()
    with open('weather.json', 'w') as fp:
        json.dump(data, fp)
    data = accident_tree.root.flatten()
    with open('accident.json', 'w') as fp:
        json.dump(data, fp)

if __name__ == '__main__':
    main()
