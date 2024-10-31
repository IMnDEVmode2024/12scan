import sqlite3

def open_connection(db_path):
    conn = sqlite3.connect(db_path)
    return conn

def fetch_events(conn, start_date, end_date):
    query = "SELECT id, longitude, latitude, title, description FROM events WHERE date BETWEEN ? AND ?"
    cur = conn.cursor()
    cur.execute(query, (start_date, end_date))
    return cur.fetchall()
