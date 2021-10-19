# Call related dependencies
from logging import debug, lastResort
from re import M
import  numpy as np
import sqlalchemy
from sqlalchemy import engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import timedelta, datetime

from sqlalchemy.sql.selectable import LABEL_STYLE_DISAMBIGUATE_ONLY


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///resources/hawaii.sqlite")

# Reflect the database into a model
Base = automap_base()

# Reflect the tables in the database
Base.prepare(engine, reflect=True)

# Put the reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Create Flask routes
# Home page
@app.route("/")
def home():
    '''Available API Routes for Webpage'''
    return (
            f"<h1>Welcome to Climate API service App!!</h1>"
            f"<br/>"
            f"<hr>"
            f"<h3>These are available routes:</h3><br/>"
           
            f"/api/v1.0/precipitation "
            f"<br/>"
            f"/api/v1.0/stations"
            f"<br/>"
            f"/api/v1.0/tobs"
            f"<br/>"
            f"/api/v1.0/start"
            f"<br/>"
            f"/api/v1.0/start/end"
            f"<br/>"
            f"<hr>"
            )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of all dates and precipitation"""
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_yr_ago_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    first_date = one_yr_ago_date.strftime("%Y-%m-%d") 

    one_year = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= first_date).all()
    
    session.close()
    prcp_all = []
    for row in one_year:
        prcp_dict = {}
        prcp_dict[row.date] = row.prcp
        prcp_all.append(prcp_dict)

    return jsonify(prcp_all)

@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    '''Return stations data in JSON format'''
    station_data = session.query(Station.station, Station.name, 
                    Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    st_all = []
    for st, name, lat, long, elv in station_data:
        station_dict = {}
        station_dict["station"] = st
        station_dict["name"] = name
        station_dict["latitude"] = lat
        station_dict["longitude"] = long
        station_dict["elevation"] = elv
        st_all.append(station_dict)
    return jsonify(st_all)

@app.route("/api/v1.0/tobs")
def temperature():
     # Create our session (link) from Python to the DB
    session = Session(engine)
    '''Return 12 months data from the recent data point in JSON format'''
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_yr_ago_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    first_date = one_yr_ago_date.strftime("%Y-%m-%d") 
    temp_yr = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date >= first_date).all()
    session.close()
    return jsonify(temp_yr)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    '''Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start or start-end range'''
    results = session.query(func.min(Measurement.tobs),\
                func.max(Measurement.tobs),\
                    func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    temp_all = []
    for temp_min, temp_max, temp_avg in results:
        temp_dict = {}
        temp_dict["Start Date"] = start
        temp_dict["Last Date"] = last_date
        temp_dict["Temp Min"] = temp_min
        temp_dict["Temp Max"] = temp_max
        temp_dict["Temp Avg"] = temp_avg
        temp_all.append(temp_dict)

    return jsonify(temp_all)

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
     # Create our session (link) from Python to the DB
    session = Session(engine)
    '''Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start or start-end range'''
    results = session.query(func.min(Measurement.tobs),\
                func.max(Measurement.tobs),\
                    func.avg(Measurement.tobs)).\
                        filter(Measurement.date >= start, Measurement.date <= end).all()
    
    session.close()
    temp_all = []
    for temp_min, temp_max, temp_avg in results:
        temp_dict = {}
        temp_dict["Start Date"] = start
        temp_dict["Last Date"] = end
        temp_dict["Temp Min"] = temp_min
        temp_dict["Temp Max"] = temp_max
        temp_dict["Temp Avg"] = temp_avg
        temp_all.append(temp_dict)

    return jsonify(temp_all)

if __name__ == "__main__":
    app.run(debug=False)
