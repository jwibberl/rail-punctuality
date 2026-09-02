import requests
import time
from datetime import datetime

#adds a specific arrival to the DB
def add_arrival(conn, run_id, station_id, scheduled_time, actual_time, delay_minutes):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO arrival
                    (run_id, station_id, scheduled_time, actual_time, delay_minutes)
                VALUES
                    (%s, %s, %s, %s, %s)
                """,
                (run_id, station_id, scheduled_time, actual_time, delay_minutes)
            )

        conn.commit()

    except Exception as e:
        print(f"error adding arrival {e}")
        conn.rollback()

#get the details of the specified service
def get_service_details(rid, apikey):
    url = "https://api1.raildata.org.uk/1010-historical-service-performance-_hsp_v1/api/v1/serviceDetails"

    headers = {
        "x-apikey": apikey,
        "User-Agent": "curl/8.21.0"
    }

    payload = {
        "rid": rid
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return response.json()

#This function goes through all the data passed to it and adds each arrival
def add_arrivals(conn, data, apikey):
    try:
        for service in data["Services"]:

            rids = service["serviceAttributesMetrics"]["rids"]

            for rid in rids:

                #get the details of the service
                details = get_service_details(rid, apikey)

                print(f"Processing RID: {rid}")

                time.sleep(5)

                attributes = details["serviceAttributesDetails"]
                locations = attributes["locations"]

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT run_id
                        FROM service_run
                        WHERE rid = %s
                        """,
                        (rid,)
                    )

                    result = cur.fetchone()

                #if there was no data returned
                if result is None:
                    print(f"No service run found for RID {rid}")
                    continue

                run_id = result[0]

                service_date = datetime.strptime(
                    rid[:8],
                    "%Y%m%d"
                ).date()

                for location in locations:

                    station_name = location["location"]

                    scheduled_time = (
                        location["gbtt_pta"]
                        or location["gbtt_ptd"]
                    )

                    actual_time = (
                        location["actual_ta"]
                        or location["actual_td"]
                    )

                    if not scheduled_time or not actual_time:
                        continue

                    scheduled_timestamp = datetime.strptime(
                        f"{service_date} {scheduled_time}",
                        "%Y-%m-%d %H%M"
                    )

                    actual_timestamp = datetime.strptime(
                        f"{service_date} {actual_time}",
                        "%Y-%m-%d %H%M"
                    )

                    # Handle services crossing midnight.
                    if actual_timestamp < scheduled_timestamp:
                        actual_timestamp = actual_timestamp.replace(
                            day=actual_timestamp.day + 1
                        )

                    with conn.cursor() as cur:

                        cur.execute(
                            """
                            SELECT station_id
                            FROM station
                            WHERE station_name = %s
                            """,
                            (station_name,)
                        )

                        station_result = cur.fetchone()

                    if station_result is None:
                        print(f"Station not found: {station_name}")
                        continue

                    station_id = station_result[0]

                    delay_minutes = (
                        actual_timestamp - scheduled_timestamp
                    ).total_seconds() / 60

                    #add the arrival
                    add_arrival(
                        conn,
                        run_id,
                        station_id,
                        scheduled_timestamp,
                        actual_timestamp,
                        delay_minutes
                    )

    #generic exception handling
    except Exception as e:
        print(f"error adding arrivals {e}")
        conn.rollback()
        raise