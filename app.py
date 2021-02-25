import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///C:/Users/rcc_0/Documents/GitHub/sqlalchemy-challenge/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"Use YYYY-MM-DD date format to choose a start date, but do not exceed 2017-08-23.<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Use YYYY-MM-DD date format to choose start date/end date.<br/>"
        f"Do not exceed 2017-08-23 for a start date, and do not preceed 2010-01-01 for an end date."
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using `date` as the key and `prcp` as the value."""
    # Query
    sel = [measurement.date, measurement.prcp]
    annual_data = session.query(*sel).filter(measurement.date >= '2016-08-23').all()

    session.close()

    # Create a dictionary from the row data, and append to a list of precipitation
    precipitation = []
    for date, prcp in annual_data:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stat():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query
    locations = session.query(station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(locations))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data."""
    # Query
    sel = [measurement.date, measurement.tobs]
    annual_data = session.query(*sel).filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= '2016-08-18').all()

    session.close()

    # Create a dictionary from the row data, and append to a list of temperature
    temperature = []
    for date, tobs in annual_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        temperature.append(tobs_dict)

    return jsonify(temperature)

@app.route("/api/v1.0/<start>")
def temp1(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date going forward."""
    # Queries
    temp1_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()  
    
    session.close()

    # Create a dictionary from the evaluation keys and their corresponding values, and append to a list
    temp1_list = []
    for tmin, tavg, tmax in temp1_results:
        temp1_dict = {}
        temp1_dict['TMIN'] = tmin
        temp1_dict['TAVG'] = tavg
        temp1_dict['TMAX'] = tmax
        temp1_list.append(temp1_dict)

    return jsonify(temp1_list)

@app.route("/api/v1.0/<start>/<end>")
def temp2(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature between a given start and end date."""
    # Query
    temp2_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date <= end).\
        filter(measurement.date >= start).all()  
    
    session.close()

    # Create a dictionary from the evaluation keys and their corresponding values, and append to a list
    temp2_list = []
    for tmin, tavg, tmax in temp2_results:
        temp2_dict = {}
        temp2_dict['TMIN'] = tmin
        temp2_dict['TAVG'] = tavg
        temp2_dict['TMAX'] = tmax
        temp2_list.append(temp2_dict)

    return jsonify(temp2_list)   

if __name__ == '__main__':
    app.run(debug=True)
