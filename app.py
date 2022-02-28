#!/usr/bin/env python
# coding: utf-8

# Import Dependencies
import pandas as pd
import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import asc, desc
from flask import Flask, jsonify

# Create an engine for the chinook.sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for all precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation data
    all_precipitation = {}
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.update(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for all stations
    station = session.query(Station.station).all()

    session.close()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for most recent date in the data set
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    # Calculate the date one year from the most recent date in the data set
    twelve_months_ago = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days = 365)

    # List the stations and the row counts in descending order
    records_per_station = session.query(Measurement.station, func.count(Measurement.station)).\
                      group_by(Measurement.station).order_by(desc(func.count(Measurement.station))).all()

    most_active_station = records_per_station[0][0]

    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station
    last_year_data = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                 filter(Measurement.station == most_active_station).filter(Measurement.date >= twelve_months_ago).all()
    
    session.close()
    
    # Convert list of tuples into normal list
    last_year_tobs = list(np.ravel(last_year_data))
    
    return jsonify(last_year_tobs)


@app.route("/api/v1.0/<start>")
def date_greater_than(start):

    """Calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date variable supplied by the user"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    right_start_date_format = dt.datetime.strptime(start, '%Y-%m-%d')

    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= right_start_date_format).all()
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= right_start_date_format).all()
    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= right_start_date_format).all()  

    session.close()

    return jsonify(f"Start Date: {right_start_date_format}, Minimum Temp is {TMIN[0][0]}, Average Temp is {TAVG[0][0]}, Max Temp is {TMAX[0][0]}")

@app.route("/api/v1.0/<start>/<end>")
def date_start(start, end):

    """Calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    right_start_date_format = dt.datetime.strptime(start, '%Y-%m-%d')
    right_end_date_format = dt.datetime.strptime(end, '%Y-%m-%d')

    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= right_start_date_format).\
            filter(Measurement.date <= right_end_date_format).all()
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= right_start_date_format).\
            filter(Measurement.date <= right_end_date_format).all()
    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= right_start_date_format).\
            filter(Measurement.date <= right_end_date_format).all()  

    session.close()

    return jsonify(f"Start Date: {right_start_date_format}, End Date: {right_end_date_format}, Minimum Temp is {TMIN[0][0]}, Average Temp is {TAVG[0][0]}, Max Temp is {TMAX[0][0]}")

if __name__ == '__main__':
    app.run(debug=True)
