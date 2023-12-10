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
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    max_date = dt.datetime(2017,8,23)
    min_date = max_date - dt.timedelta(days=366)
    results_df = pd.DataFrame(session.query(measurement.date,measurement.prcp).filter(measurement.date >= min_date, measurement.date <= max_date).all())

    session.close()

    results_dict = {results_df['date'][i]:results_df['prcp'][i] for i in range(len(results_df['date']))}

    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    station_result = session.query(station.station).all()

    session.close()

    station_list = [station[0] for station in station_result]

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    return jsonify()


@app.route("/api/v1.0/<start>")
def temps_w_start():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    return jsonify()


@app.route("/api/v1.0/<start>/<end>")
def temps_w_start_end():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    return jsonify()


if __name__ == '__main__':
    app.run(debug=True)