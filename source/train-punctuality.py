from flask import Flask
from flask import render_template, request
import requests
import os

import db
import station
import service
import arrivals
import graph


from dotenv import load_dotenv

from markupsafe import escape

app = Flask(__name__)

load_dotenv()

db_host = os.getenv("POSTGRES_HOST")
db_user = os.getenv("POSTGRES_USER")
db_name = os.getenv("POSTGRES_DB")
db_pass = os.getenv("POSTGRES_PASSWORD")

apikey = os.getenv("API_KEY")

print(f"DB_HOST: {db_host}")

conn = db.get_connection(
    db_host,
    5433,
    db_user,
    db_pass,
    db_name
)

import requests

def get_train_data(fromloc, fromtime, fromdate,
                   toloc, totime, todate, days):

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
        "days": days,
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


    fromloc = request.form.get("fromloc")
    fromtime = request.form.get("fromtime")
    fromdate = request.form.get("fromdate")

    toloc = request.form.get("toloc")
    totime = request.form.get("totime")
    todate = request.form.get("todate")

    days = request.form.get("days")

    data = get_train_data(
        fromloc,
        fromtime,
        fromdate,
        toloc,
        totime,
        todate,
        days
    )

    print("********************")
    print(data)
    print("********************")

    station.add_stations(conn, data)
    service.add_services(conn, data)
    service.add_service_runs(conn, data)
    arrivals.add_arrivals(conn, data, apikey)

    #return(data)
    return render_template("index.html")

@app.route("/resetdb", methods=["POST"])
def resetdb():
    print("resetdb")
    db.reset_db(conn)
    return render_template("index.html")

@app.route("/graphs")
def graphs():
    print("****")
    print("rendering graphs")
    print("****")

    #Render the actual graphs
    graph.render_graph(conn)
    return render_template("index.html")