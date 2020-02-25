#Dependencies
import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#Use Flask to create web pages
app = Flask(__name__)

@app.route("/")
def welcome():
    #List all routes that are available.
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/vacation/<br>"
        f"To check vacation days for temperatures, please enter dates, e.g. /api/v1.0/vacation/start date/end date, format = (2017-mm-dd)")
        

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    #Return the JSON representation of your dictionary
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.date <= '2017-08-23')
    precipitation = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        precipitation.append(precip_dict)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    #  Return a JSON list of stations from the dataset.
    session = Session(engine)
    stations = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation)
    station_list = []
    for id, station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict['id'] = id
        station_dict['station'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation
        
        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # query for the dates and temperature observations from a year from the last data point.
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    session = Session(engine)
    temp = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').filter(Measurement.date <='2017-08-23').all()
    observations = []
    for date, station, tobs in temp:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['station'] = station
        temp_dict['temp'] = tobs
        observations.append(temp_dict)
    
    return jsonify(observations)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for
#  a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal
#  to the start date.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the
#  start and end date inclusive.

@app.route("/api/v1.0/vacation/<start>")
@app.route("/api/v1.0/vacation/<start>/<end>")
def vacation(start = '', end = ''):
    session = Session(engine)
    if end == '':
        end = '2017-08-24'
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs), Measurement.date).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all() 
    
    dailys = []
    for min_temp, avg_temp, max_temp, date in results:
        day_dict = {}
        day_dict['min_temp'] = min_temp
        day_dict['avg_temp'] = avg_temp
        day_dict['max_temp'] = max_temp
        day_dict['date'] = dt.datetime.strftime(pd.to_datetime(date), '%m-%d')
        dailys.append(day_dict)
    
    return jsonify(dailys)

if __name__ == '__main__':
    app.run(debug=True)

