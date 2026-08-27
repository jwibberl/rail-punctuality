import db
import station

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

    except Exception as e:
        print(f"error adding service {e}")
        conn.rollback()
        return None
            
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

    except Exception as e:
        print(f"error adding service run {e}")
        conn.rollback()
        return None

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

    except Exception:
        conn.rollback()
        raise

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

    except Exception:
        conn.rollback()
        raise

