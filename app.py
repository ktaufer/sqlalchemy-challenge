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
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start_end"
    )

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

#__________________________________________________________________________________________________

#This is the official solution for the last two pages tweaked to eliminate errors.  
# It does not have the ability to take in a start or end date, and when run, 
# it spits out one tuple of min. temp., avg. temp., and max.temp.

# @app.route("/api/v1.0/start")
# @app.route("/api/v1.0/start_end")
# def stats(start = '', end = ''):
#     session = Session(engine)
#     sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
#     if not end:
#         results = session.query(*sel).filter(Measurement.date >= start).all()
#         temps = list(np.ravel(results))
#         return jsonify(temps)
    
#     results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
#     temps = list(np.ravel(results))
#     return jsonify(temps)
#____________________________________________________________________________________________________

#The following is my solution for the last two pages. It is ungainly, in that the input (dates) must be entered in 
# the terminal, then the result can be viewed in the browser, but it does return the desired results.
@app.route("/api/v1.0/start")
def start():
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for
#  a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal
#  to the start date.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the
#  start and end date inclusive.
    session = Session(engine)
    def daily_normals(date):
        sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs), Measurement.date]
        return session.query(*sel, Measurement.date).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    start_date = input('When will your vacation begin? (yyyy-mm-dd)')
    end_date = '2017-08-24'
    t_dates = pd.to_datetime(np.arange(start_date,end_date, dtype='datetime64'))
    tr_dates = []
    for date in t_dates:
        tr_dates.append(dt.datetime.strftime(date, "%m-%d"))
    normals = []
    for date in tr_dates:
        normals.append(daily_normals(date))
    days = []
    totals = {}
    for row in normals:
        totals['min_temp'] = row[0][0]
        totals['avg_temp'] = row[0][1]
        totals['max_temp'] = row[0][2]
        totals['date'] = row[0][3]
        days.append(totals)
    return jsonify(days)



@app.route("/api/v1.0/start_end")
def start_end():
    session = Session(engine)
    def daily_normals(date):
        sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        return session.query(*sel, Measurement.date).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    start_date = input('When will your vacation begin? (yyyy-mm-dd)')
    end_date = input('When will you return? (yyyy-mm-dd)')
    t_dates = pd.to_datetime(np.arange(start_date,end_date, dtype='datetime64'))
    tr_dates = []
    for date in t_dates:
        tr_dates.append(dt.datetime.strftime(date, "%m-%d"))
    normals = []
    for date in tr_dates:
        normals.append(daily_normals(date))
    days = []
    totals = {}
    for row in normals:
        totals['min_temp'] = row[0][0]
        totals['avg_temp'] = row[0][1]
        totals['max_temp'] = row[0][2]
        totals['date'] = row[0][3]
        days.append(totals)
    return jsonify(days)

if __name__ == '__main__':
    app.run(debug=True)

