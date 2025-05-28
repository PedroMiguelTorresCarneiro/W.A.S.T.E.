import mariadb
import json
import datetime
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT

# Database Configuration
DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASS,
    "database": DB_NAME,
    "port": DB_PORT
}

def setup_database():
    """Ensures the database and table exist before running the service."""
    conn = mariadb.connect(host=DB_CONFIG["host"], user=DB_CONFIG["user"], password=DB_CONFIG["password"], port=DB_CONFIG["port"])
    cur = conn.cursor()

    try:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
        cur.execute(f"USE {DB_NAME};")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                route_id VARCHAR(255) PRIMARY KEY,
                coordinates TEXT NOT NULL,
                day INT NOT NULL,
                month INT NOT NULL,
                year INT NOT NULL,
                truck_id VARCHAR(255) DEFAULT NULL,
                distance_km FLOAT DEFAULT NULL,         -- ✅ NOVO
                duration_min FLOAT DEFAULT NULL         -- ✅ NOVO
            );
        """)
        conn.commit()
        print("✅ Database and table are ready!")
    except mariadb.Error as e:
        print(f"❌ Error setting up database: {e}")
    finally:
        cur.close()
        conn.close()

def connect_db():
    """Ensures the database is set up and establishes a connection."""
    setup_database()
    try:
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def create_route(route_id, coordinates, truck_id=None, distance_km=None, duration_min=None):  # ✅ NOVOS PARAMS
    """
    Stores a new route in the database.
    """
    conn = connect_db()
    if not conn:
        return {"error": "Database connection failed"}

    cur = conn.cursor()
    now = datetime.datetime.now()

    try:
        cur.execute("""
            INSERT INTO routes (route_id, coordinates, day, month, year, truck_id, distance_km, duration_min)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            route_id,
            json.dumps(coordinates),
            now.day,
            now.month,
            now.year,
            truck_id,
            distance_km,
            duration_min
        ))

        conn.commit()
        return {"message": "Route stored successfully"}
    except mariadb.Error as e:
        return {"error": f"Failed to store route: {e}"}
    finally:
        cur.close()
        conn.close()

def get_route(route_id):
    """
    Retrieves a specific route from the database.
    """
    conn = connect_db()
    if not conn:
        return {"error": "Database connection failed"}

    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM routes WHERE route_id = ?", (route_id,))
        row = cur.fetchone()

        if row:
            return {
                "route_id": row[0],
                "coordinates": json.loads(row[1]),
                "day": row[2],
                "month": row[3],
                "year": row[4],
                "truck_id": row[5],
                "distance_km": row[6],     # ✅ NOVO
                "duration_min": row[7]     # ✅ NOVO
            }
        return {"error": "Route not found"}
    finally:
        cur.close()
        conn.close()

def get_routes_history(day=None, month=None, year=None, truck_id=None):
    """
    Retrieves stored routes with optional filtering.
    """
    conn = connect_db()
    if not conn:
        return {"error": "Database connection failed"}

    cur = conn.cursor()

    query = "SELECT * FROM routes WHERE 1=1"
    params = []

    if day:
        query += " AND day = ?"
        params.append(day)
    if month:
        query += " AND month = ?"
        params.append(month)
    if year:
        query += " AND year = ?"
        params.append(year)
    if truck_id:
        query += " AND truck_id = ?"
        params.append(truck_id)

    try:
        cur.execute(query, params)
        rows = cur.fetchall()

        if not rows:
            return {"error": "No routes found"}

        routes = []
        for row in rows:
            routes.append({
                "route_id": row[0],
                "coordinates": json.loads(row[1]),
                "day": row[2],
                "month": row[3],
                "year": row[4],
                "truck_id": row[5],
                "distance_km": row[6],     # ✅ NOVO
                "duration_min": row[7]     # ✅ NOVO
            })
        return routes
    finally:
        cur.close()
        conn.close()

def delete_route(route_id):
    """
    Deletes a stored route from the database.
    """
    conn = connect_db()
    if not conn:
        return {"error": "Database connection failed"}

    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM routes WHERE route_id = ?", (route_id,))
        conn.commit()

        if cur.rowcount > 0:
            return {"message": "Route deleted successfully"}
        return {"error": "Route not found"}
    finally:
        cur.close()
        conn.close()
