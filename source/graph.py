import db

#This function generates the graph that will be in Grafana
def render_graph(conn):

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT station_id, station_name
                FROM station
                ORDER BY station_name
                """
            )

            stations = cur.fetchall()

            for station_id, station_name in stations:

                cur.execute(
                    """
                    SELECT
                        COUNT(*) FILTER (WHERE delay_minutes < 1),
                        COUNT(*) FILTER (WHERE delay_minutes < 2),
                        COUNT(*) FILTER (WHERE delay_minutes < 5)
                    FROM arrival
                    WHERE station_id = %s
                    """,
                    (station_id,)
                )

                result = cur.fetchone()

                under_1 = result[0]
                under_2 = result[1]
                under_5 = result[2]

                print(
                    f"{station_name}: "
                    f"<1 min = {under_1}, "
                    f"<2 min = {under_2}, "
                    f"<5 min = {under_5}"
                )

    #generic exception handling
    except Exception as e:
        print(f"error rendering graph {e}")
        raise