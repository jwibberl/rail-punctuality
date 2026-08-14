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