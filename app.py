import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the new tables 
Base.prepare(engine, reflect=True)

#Save references to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)


# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes"""
    return(
        f"Welcome to the weather data for Hawaii trip<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-01-01<br/>"
        f"/api/v1.0/2017-01-01/2017-01-07"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Convert precipitation results to a Dictionary using date as key and prcp as value
    last_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_months).all()

    session.close()

    # Covert list of tuples into a normal dictionary
    results = []
    for date, prcp in query:
        climate_dict = {}
        climate_dict["date"] = date
        climate_dict["prcp"] = prcp 
        results.append(climate_dict)

    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # Convert date and tobs to a Dictionary using date as key and tobs as value
    first_date = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    final_station = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= first_date).\
        order_by(Measurement.date.desc()).all()

    session.close()

    results = []
    for date, tobs in final_station:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        results.append(tobs_dict)

    return jsonify(results)

@app.route("/api/v1.0/2017-01-01")
def start_calc_temp():
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= '2017-01-01').all()

    session.close()

    start_list = list(np.ravel(results))

    return jsonify(start_list)

@app.route("/api/v1.0/2017-01-01/2017-01-07")
def calc_temps():
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= '2017-01-01').filter(Measurement.date <= '2017-01-07').all()

    session.close()

    trip_dates = list(np.ravel(results))

    return jsonify(trip_dates)



if __name__ == '__main__':
    app.run(debug=True)
