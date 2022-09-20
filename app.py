from cProfile import run
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#Database set up
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#Flask set up
app = Flask(__name__)

# import app

# print("example __name__ = %s", __name__)

# if __name__ == "__main__":
#     print("example is being run directly.")
# else:
#     print("example is being imported")

@app.route("/")

def welcome():
    return(
    '''
    Welcome to the Climate Analysis API.
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

#Create precipitation function
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Calculate previous year
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #Query for date and precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
    #Create a dictionary with the date as the key and precipitation as value
    precip = {date: prcp for date, prcp in precipitation}
    #JSONify results
    return jsonify(precip)

# Create stations route
@app.route("/api/v1.0/stations")
def stations():
    #Query for all stations
    results = session.query(Station.station).all()
    #Unravel results into a one-dimensional array
    stations = list(np.ravel(results))
    #JSONify results
    return jsonify(stations=stations)

#Create monthly temperature route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    #Calculate the date one year previous from 08/23/2017
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #Query the primary station for all the temperature observations from previous year
    #Filter by station ID and then date
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    #Unravel results into a one-dimensional array and covert array to list
    temps = list(np.ravel(results))
    #JSONify results
    return jsonify(temps=temps)

#Create statistics route - has to include start and end date
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    #Query to select min, avg, and max temps for SQLite Database
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    #If end date is not supplied
    if not end:
        #Asterisk (*) indicates there will be multiple results
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
    #If start and end date are both supplied
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    #JSONify results
    return jsonify(temps)
