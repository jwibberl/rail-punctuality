from flask import Flask
from flask import render_template, request
import requests
import os

import db
import station
import service
import arrivals


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

    #url = "https://hsp-prod.rockshore.net/api/v1/serviceMetrics"
    url = "https://api1.raildata.org.uk/1010-historical-service-performance-_hsp_v1/api/v1/serviceMetrics"

    query = {
        "from_loc": fromloc,
        "to_loc": toloc,
        "from_time": fromtime,
        "to_time": totime,
        "from_date": fromdate,
        "to_date": todate,
        "days": days
    }

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
    
    #print(data)

    station.add_stations(conn, data)
    service.add_services(conn, data)

    return(data)

@app.route("/resetdb")
def resetdb():
    print("resetdb")

@app.route("/graphs")
def graphs():
    print("graphs")