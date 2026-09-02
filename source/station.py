import db

#return the station ID of a station, takes the db conn and the name of a station, this will be the three letter code
def get_station_id(conn, station_name):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT station_id
        FROM station
        WHERE station_name = %s
        """,
        (station_name,)
    )

    result = cursor.fetchone()

    cursor.close()

    if result:
        return result[0]

    return None

#adds a station, takes db conn and 3 letter code for the station
def add_station(conn, name):
    try:
        with conn.cursor() as cur:

            cur.execute(
                "INSERT INTO station (station_name) VALUES (%s)",
                (name,)
            )

            conn.commit()
    except Exception as e:
        print(f"error adding station {e}")

#loops through the data and adds all stations if they don't exist
def add_stations(conn, data):
    for service in data["Services"]:
        attributes = service["serviceAttributesMetrics"]

        origin = attributes["origin_location"]
        destination = attributes["destination_location"]

        if get_station_id(conn, origin) is None:
            add_station(conn, origin)

        if get_station_id(conn, destination) is None:
            add_station(conn, destination)