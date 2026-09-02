from flask import Flask
from flask import render_template, request
import requests
import os

#the below imports are Python that I wrote
import db
import station
import service
import arrivals
import graph

from dotenv import load_dotenv
from markupsafe import escape

app = Flask(__name__)

#load DB variables and API key for HSP from .env
load_dotenv()

db_host = os.getenv("POSTGRES_HOST")
db_user = os.getenv("POSTGRES_USER")
db_name = os.getenv("POSTGRES_DB")
db_pass = os.getenv("POSTGRES_PASSWORD")

apikey = os.getenv("API_KEY")

print(f"DB_HOST: {db_host}")

#open the DB connection
conn = db.get_connection(
    db_host,
    5433,
    db_user,
    db_pass,
    db_name
)

#gets the data from HSP for a specific train, needs from and to dates, and locations. Days will be WEEKDAY or WEEKEND
def get_train_data(fromloc, fromtime, fromdate,
                   toloc, totime, todate, day_type):

    url = "https://api1.raildata.org.uk/1010-historical-service-performance-_hsp_v1/api/v1/serviceMetrics"

    headers = {
        "x-apikey": apikey,
        "User-Agent": "curl/8.21.0"
    }

    payload = {
        "from_loc": fromloc,
        "to_loc": toloc,
        "from_time": fromtime,
        "to_time": totime,
        "from_date": fromdate,
        "to_date": todate,
        "days": day_type,
        "tolerance": ["1", "2", "5"]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return response.json()
   
@app.route("/")
def index():
     return render_template("index.html")

@app.route("/gettrain", methods=["POST"])
def gettrain():
    #get parameters from the form on the web page
    fromloc = request.form.get("fromloc")
    fromtime = request.form.get("fromtime")
    fromdate = request.form.get("fromdate")

    toloc = request.form.get("toloc")
    totime = request.form.get("totime")
    todate = request.form.get("todate")

    days = request.form.get("days")

    #fetch data from HSP API
    train_data = get_train_data(
        fromloc,
        fromtime,
        fromdate,
        toloc,
        totime,
        todate,
        days
    )

    print("********************")
    print(train_data)
    print("********************")

    #add stations, services, service runs and arrivals
    station.add_stations(conn, train_data)
    service.add_services(conn, train_data)
    service.add_service_runs(conn, train_data)
    arrivals.add_arrivals(conn, train_data, apikey)

    #return(data)
    return render_template("index.html")

#route for if the user presses the reset DB button
@app.route("/resetdb", methods=["POST"])
def resetdb():
    print("resetdb")
    db.reset_db(conn)
    return render_template("index.html")

#route for the graph button
@app.route("/graphs")
def graphs():
    print("****")
    print("rendering graphs")
    print("****")

    #Render the actual graphs
    graph.render_graph(conn)
    return render_template("index.html")