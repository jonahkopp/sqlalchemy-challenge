# Import the dependencies.
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# I will open and close the sessions individually depending on the end point that is called.

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp This will return the latest 12 months of precipitation by day as a dictionary.<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp This will return all weather monitoring stations represented in this data.<br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp This will return the most recent year of temperature data from the most active station.<br/><br/>"
        f"/api/v1.0/start_date<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp This will return the minimum, average, and maximum temperature over a time range spanning<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp the user-specified start_date to the last date in the data. As an example, you could type the following endpoint:<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp /api/v1.0/2016-08-23<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp to get the minimum, average, and maximum temperatures from 2016-08-23 to the last date.<br/><br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp This works exactly as the above end point, except you also specificy an end date instead of<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp defaulting to the last date in the data.<br/><br/>"
        f"/api/v1.0/all_dates/start_date<br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp This is not a question in the module, but this end point returns the mininum, average, and maximum <br/>"
        f"&nbsp&nbsp&nbsp&nbsp&nbsp termperatures for EVERY day starting with the start date and ending with the last date in the data.<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    max_date = dt.datetime(2017,8,23)
    min_date = max_date - dt.timedelta(days=366)

    session = Session(engine)
    results_df = pd.DataFrame(session.query(measurement.date,measurement.prcp).filter(measurement.date >= min_date, measurement.date <= max_date).all())
    session.close()

    results_dict = {results_df['date'][i]:results_df['prcp'][i] for i in range(len(results_df['date']))}

    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_result = session.query(station.station).all()
    session.close()

    station_list = [station[0] for station in station_result]

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    max_date = dt.datetime(2017,8,23)
    min_date = max_date - dt.timedelta(days=366)

    session = Session(engine)
    temp_results = session.query(measurement.date,measurement.tobs).filter(measurement.date >= min_date, measurement.date <= max_date, measurement.station == 'USC00519281').all()
    session.close()

    temp_results_df = pd.DataFrame(temp_results,columns=['date','tobs'])

    temp_list = list(temp_results_df['tobs'])

    return jsonify(temp_list)


@app.route("/api/v1.0/<start_date>")
def temps_w_start(start_date):

    # I think I overcomplicated this part-- this returns the min, average, and max temp for EVERY date after the start date,
    # but I think the question just wants the aggregates across all dates. I will re-map this to a new endpoint.

    session = Session(engine)
    data = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
                   filter(measurement.date>=start_date).all()
    session.close()

    return jsonify(list(data[0]))


@app.route("/api/v1.0/<start>/<end>")
def temps_w_start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    data = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
                   filter(measurement.date>=start, measurement.date<=end).all()
    session.close()

    return jsonify(list(data[0]))



@app.route("/api/v1.0/all_dates/<start_date>")
def temps_w_start_details(start_date):

    # This was not part of the assignment, but I initially mis-interpreted the prompt and created this.
    # This endpoint gets the min, avg, and max temp for EVERY date after the <start_date> specified.

    session = Session(engine)
    data = session.query(measurement.date,func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
                   filter(measurement.date>=start_date).\
                   group_by(measurement.date).all()
    session.close()

    data_dict = {d[0]:[d[1],d[2],d[3]] for d in data}

    return jsonify(data_dict)


if __name__ == '__main__':
    app.run(debug=True)