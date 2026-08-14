import db

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

