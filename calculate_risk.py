"""
Main risk analysis application.
"""

import flask
import json
import jinja2
import math
import random
import re
import sqlite3
import string
import sys

import kdtree


app = flask.Flask(__name__)

# Load the trees
try:
    print('Loading trees...', end='')
    sys.stdout.flush()
    weather_tree = kdtree.KDTree(features=['latitude', 'longitude', 'date'],
                                 json_file='json/weather.json')
    accident_tree = kdtree.KDTree(features=['latitude', 'longitude', 'date'],
                                  json_file='json/accident.json')
    print('done', end='\n\n')
except:
    print('Unable to load trees. "json/accident.json" or "json/weather.json" may not exist.', file=sys.stderr)
    sys.exit(1)

def convert_from_dms(degree, minute, second, direction):
    """
    Convert from degrees-minute-second form to decimal form and return it.
    """
    return direction * (degree + (1.0 / 60.0) * minute + (1.0 / 3600.0) * second)

def calculate_risk(latitude, longitude, month, day, k=10):
    """
    Calculate and return the risk for a given vehicle route. Returns a tuple of
    the form (weather_point, accident_point, risk).
    """
    # Setup the query point
    date = '2018%.2i%.2i' % (month, day)
    point = {
        'latitude': latitude,
        'longitude': longitude,
        'date': int(date),
    }
    # Initialize the risk
    risk = 0.0
    # Do the weather NN search
    weather_point = weather_tree.nns(point)
    accident_point = accident_tree.nns(point)
    # Set the accident data -- only give it a weight of 1/2 (50%)
    risk += (accident_point['fatals'] / 3) / 2
    # Add in the weather parameters
    if weather_point['windspeed'] != 999.9 and weather_point['windspeed'] > 20.0:
        risk += 0.1
    # Add in the precipitation factors
    if float(weather_point['precipitation'][0]) > 0.1:
        risk += 0.1
    # Add in the indicator parameters
    # Fog
    if weather_point['indicators'][0] == '1':
        risk += 0.1
    # Snow or Ice Pellets
    if weather_point['indicators'][2] == '1':
        risk += 0.1
    # Tornado or Funnel Cloud
    if weather_point['indicators'][5] == '1':
        risk += 0.1
    # Return the normalized risk
    return weather_point, accident_point, risk

def render(args={'title': 'Risk Analysis', 'result': ''}):
    """Return the rendered display page."""
    # Read in the display file
    with open('display.html') as fp:
        template = jinja2.Template(fp.read())
    return template.render(args)

@app.route('/', methods=('GET', 'POST'))
def view():
    """Main view."""
    if flask.request.method == 'GET':
        return render()
    # On POST
    # Do the actual risk calculation
    latitude = convert_from_dms(int(flask.request.form['latitude_degree']),
                                int(flask.request.form['latitude_minute']),
                                int(flask.request.form['latitude_second']),
                                int(flask.request.form['latitude_direction']))
    longitude = convert_from_dms(int(flask.request.form['longitude_degree']),
                                 int(flask.request.form['longitude_minute']),
                                 int(flask.request.form['longitude_second']),
                                 int(flask.request.form['longitude_direction']))
    month = flask.request.form['month']
    day = flask.request.form['day']
    print('Calculating risk for', latitude, '(latitude) and', longitude, '(longitude).')
    weather_point, accident_point, risk_value = calculate_risk(
        float(latitude),
        float(longitude),
        int(month),
        int(day),
    )
    # Load and render the template
    return render({
            'title': 'Risk Analysis Result',
            'latitude': latitude,
            'longitude': longitude,
            'month': month,
            'day': day,
            # Return the risk as a percentage value.
            'result': int(risk_value * 100),
    })

def main():
    # Start Flask on port 8080
    app.run(port=8080)

if __name__ == '__main__':
    main()
