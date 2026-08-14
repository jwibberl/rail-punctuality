import db

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