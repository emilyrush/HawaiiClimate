import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import time
import datetime as dt
from dateutil.relativedelta import relativedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Let's go to Hawaii! Here are the available API Routes:<br/>"
       f"<br/>"
       f"/api/v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/>"
       f"/api/v1.0/start-date/[date]<br/>"
       f"/api/v1.0/start-date/[date]/end-date/[date]<br/>"
       f"Note: 'Date' is in YYYY-MM-DD format."
   )
#-----------------------------------------------------------------------------------------------------------------------------------------
# Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation"""
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.commit()

    # Convert list into dictionary
    prcp_dict = {date:prcp for date, prcp in results}
    time.sleep(2)

    return jsonify(prcp_dict)

#-----------------------------------------------------------------------------------------------------------------------------------------
# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Station.station).all()
    session.commit()
    time.sleep(2)

    return jsonify(station_results)
#-----------------------------------------------------------------------------------------------------------------------------------------
# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")

def tobs():
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(date[0], '%Y-%m-%d')
    last_year = last_date - relativedelta(years=1)
    tobs_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()
    session.commit()
    tobs_dict = {date:tobs for date, tobs in tobs_results}
    time.sleep(2)

    return jsonify(tobs_dict)
#-----------------------------------------------------------------------------------------------------------------------------------------
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

@app.route("/api/v1.0/start-date/<start>")
def describe_temp_start_date(start):

   result = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
   session.commit()
   time.sleep(2)
   return jsonify(result)

# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@app.route("/api/v1.0/start-date/<start>/end-date/<end>")
def calc_temps(start, end):

   result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
   session.commit()
   time.sleep(2)
   return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
