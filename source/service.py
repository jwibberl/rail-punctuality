import db
import station
from datetime import datetime

#gets the details of a specific service. Requires station IDs of from and to stations
def get_service(conn, from_station, to_station):

    with conn.cursor() as cur:      
        cur.execute(
            """
            SELECT service_id
            FROM service
            WHERE from_station = %s
            AND to_station = %s
            """,
            (from_station, to_station)
        )

        result = cur.fetchone()

        if result:
            return result[0]
        else:
            return None

#adds a specific service, requires db conn, from and to station IDs
def add_service(conn, from_station, to_station):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO service (from_station, to_station)
                VALUES (%s, %s)
                RETURNING service_id
                """,
                (from_station, to_station)
            )

            service_id = cur.fetchone()[0]

        conn.commit()
        return service_id

    #generic exception handling
    except Exception as e:
        print(f"error adding service {e}")
        conn.rollback()
        return None

#adds a service run, this needs db conn, service id, RID and service date. The service run is an instance of a service running on the route            
def add_service_run(conn, service_id, rid, service_date):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO service_run
                    (service_id, rid, service_date)
                VALUES
                    (%s, %s, %s)
                RETURNING run_id
                """,
                (service_id, rid, service_date)
            )

            run_id = cur.fetchone()[0]

        conn.commit()
        return run_id

    #generic exception handling
    except Exception as e:
        print(f"error adding service run {e}")
        conn.rollback()
        return None

#This takes the db conn and data, and adds each service
def add_services(conn, data):
    try:
        with conn.cursor() as cur:
            for service in data["Services"]:
                attributes = service["serviceAttributesMetrics"]

                origin = attributes["origin_location"]
                destination = attributes["destination_location"]

                from_station_id = station.get_station_id(conn, origin)
                to_station_id = station.get_station_id(conn, destination)

                cur.execute(
                    """
                    INSERT INTO service (from_station, to_station)
                    VALUES (%s, %s)
                    """,
                    (from_station_id, to_station_id)
                )

        conn.commit()

    #if the service already exists, or any other exception occurs, roll back and raise an exception
    except Exception:
        conn.rollback()
        raise

#takes db conn and data, adds each service run
def add_service_runs(conn, data):
    try:
        with conn.cursor() as cur:
            for service in data["Services"]:
                attributes = service["serviceAttributesMetrics"]

                origin = attributes["origin_location"]
                destination = attributes["destination_location"]
                rids = attributes["rids"]

                from_station_id = station.get_station_id(conn, origin)
                to_station_id = station.get_station_id(conn, destination)

                cur.execute(
                    """
                    SELECT service_id
                    FROM service
                    WHERE from_station = %s
                    AND to_station = %s
                    """,
                    (from_station_id, to_station_id)
                )

                result = cur.fetchone()

                if result is None:
                    continue

                service_id = result[0]

                for rid in rids:
                    service_date = datetime.strptime(
                        rid[:8],
                        "%Y%m%d"
                    ).date()

                    cur.execute(
                        """
                        INSERT INTO service_run
                            (service_id, rid, service_date)
                        VALUES
                            (%s, %s, %s)
                        """,
                        (service_id, rid, service_date)
                    )

        conn.commit()

    #if the service run alreeady exists or any other error/exception occurs, roll back and raise an exception
    except Exception:
        conn.rollback()
        raise

