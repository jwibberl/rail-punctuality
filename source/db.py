import psycopg2
def get_connection(hostname, port, user, thepassword, db):
    conn = psycopg2.connect(
        host=hostname,
        port=port,
        database=db,
        user=user,
        password=thepassword)
    return conn

def reset_db(conn):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE TABLE
                    arrival,
                    service_run,
                    service,
                    station
                RESTART IDENTITY CASCADE
                """
            )

        conn.commit()

    except Exception as e:
        print(f"error resetting database {e}")
        conn.rollback()