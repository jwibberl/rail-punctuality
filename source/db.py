import psycopg2
def get_connection(hostname, port, user, thepassword, db):
    conn = psycopg2.connect(
        host=hostname,
        port=port,
        database=db,
        user=user,
        password=thepassword)
    return conn