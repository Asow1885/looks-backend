import sqlite3

def get_connection():
    conn = sqlite3.connect('logisticsprime.db', check_same_thread=False)
    return conn

def match_containers_for_driver(origin, destination):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM containers
        WHERE LOWER(origin) = LOWER(?) AND LOWER(destination) = LOWER(?)
    ''', (origin.lower(), destination.lower()))
    results = cursor.fetchall()
    conn.close()
    return results
