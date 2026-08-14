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

print(f"DB_HOST: {db_host}")

conn = db.get_connection(
    db_host,
    5433,
    db_user,
    db_pass,
    db_name
)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/gettrain", methods=["POST"])

lds = station.get_station_id(conn, "lds")
bdi = station.get_station_id(conn, "bdi")

if lds is None:
    lds = station.add_station(conn, "lds")

if bdi is None:
    bdi = station.add_station(conn, "bdi")


service_id = service.get_service(conn, lds, bdi)

if service_id is None:
    print("adding service")
    service_id = service.add_service(conn, lds, bdi)


run_id = service.add_service_run(
    conn,
    service_id,
    "rid",
    "2026-08-10"
)

print(f"Service ID: {service_id}")
print(f"Run ID: {run_id}")


arrivals.add_arrival(
    conn,
    run_id,
    lds,
    "2026-08-10 09:22:00",
    "2026-08-10 09:22:00",
    0
)