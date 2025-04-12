from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql
from typing import Union
from datetime import datetime

app = FastAPI()

# CORS para permitir chamadas do Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dados de conexão
conn = pymysql.connect(
    host="localhost",
    port=3307,
    user="waste_user",
    password="wastepass",
    database="waste_db",
    cursorclass=pymysql.cursors.DictCursor
)

# Modelo para os dados dos bins
class Bin(BaseModel):
    sensor_serial: str
    lat: float
    lon: float
    nfc_token: str
    topic: str
    #fill_level: str | None = None  # opcional ao criar
    fill_level: Union[str, None] = None
    
# Modelo para atualizar o nível de preenchimento
class FillLevelUpdate(BaseModel):
    fill_level: str

class User(BaseModel):
    uid: str
    role: str  # "admin" ou "user"
    imei: Union[str, None] = None

class ImeiUpdate(BaseModel):
    imei: str

class UsageIncrement(BaseModel):
    pass  # Este modelo é vazio, apenas para formalidade


# 🔹 GET /bins
@app.get("/bins")
def get_bins():
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM bins")
        return cursor.fetchall()

# 🔹 POST /bins
@app.post("/bins")
def add_bin(bin: Bin):
    with conn.cursor() as cursor:
        sql = """
        INSERT INTO bins (sensor_serial, lat, lon, nfc_token, topic)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (bin.sensor_serial, bin.lat, bin.lon, bin.nfc_token, bin.topic))
        conn.commit()
        return {"message": "Bin added successfully"}

# 🔹 PUT /bins/{id}
@app.put("/bins/{bin_id}")
def update_bin(bin_id: int, bin: Bin):
    with conn.cursor() as cursor:
        sql = """
        UPDATE bins SET sensor_serial=%s, lat=%s, lon=%s, nfc_token=%s, topic=%s WHERE id=%s
        """
        cursor.execute(sql, (bin.sensor_serial, bin.lat, bin.lon, bin.nfc_token, bin.topic, bin_id))
        conn.commit()
        return {"message": "Bin updated successfully"}

# 🔹 DELETE /bins/{id}
@app.delete("/bins/{bin_id}")
def delete_bin(bin_id: int):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM bins WHERE id = %s", (bin_id,))
        conn.commit()
        return {"message": "Bin deleted successfully"}

# 🔹 PUT /bins/fill/{sensor_serial}
@app.put("/bins/fill/{sensor_serial}")
def update_fill_level(sensor_serial: str, payload: FillLevelUpdate):
    with conn.cursor() as cursor:
        sql = "UPDATE bins SET fill_level = %s WHERE sensor_serial = %s"
        cursor.execute(sql, (payload.fill_level, sensor_serial))
        conn.commit()
        return {"message": "Fill level updated successfully"}


# Endpoints para Users
@app.get("/users")
def get_users():
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()

@app.post("/users")
def add_user(user: User):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE uid = %s", (user.uid,))
        existing = cursor.fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        sql = """
        INSERT INTO users (uid, role, imei, created_at)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (user.uid, user.role, user.imei, datetime.utcnow()))
        conn.commit()
        return {"message": "User added successfully"}

@app.put("/users/{uid}/imei")
def update_user_imei(uid: str, payload: ImeiUpdate):
    with conn.cursor() as cursor:
        sql = "UPDATE users SET imei = %s WHERE uid = %s"
        cursor.execute(sql, (payload.imei, uid))
        conn.commit()
        return {"message": "IMEI updated successfully"}

@app.post("/users/{uid}/increment_usage")
def increment_usage_count(uid: str):
    with conn.cursor() as cursor:
        sql = "UPDATE users SET usage_count = COALESCE(usage_count, 0) + 1 WHERE uid = %s"
        cursor.execute(sql, (uid,))
        conn.commit()
        return {"message": f"usage_count incremented for user {uid}"}

@app.get("/users/{uid}/usage_count")
def get_usage_count(uid: str):
    with conn.cursor() as cursor:
        cursor.execute("SELECT usage_count FROM users WHERE uid = %s", (uid,))
        result = cursor.fetchone()
        if result:
            return {"uid": uid, "usage_count": result["usage_count"]}
        else:
            raise HTTPException(status_code=404, detail="User not found")

# 🔹 GET /users/exists/{uid}
@app.get("/users/exists/{uid}")
def check_user_exists(uid: str):
    with conn.cursor() as cursor:
        cursor.execute("SELECT role FROM users WHERE uid = %s", (uid,))
        result = cursor.fetchone()
        if result:
            return {"exists": True, "role": result["role"]}
        else:
            return {"exists": False}
