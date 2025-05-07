from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql
from typing import Union
from datetime import datetime
from config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

app = FastAPI()

# CORS para permitir chamadas do Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Função para criar nova ligação à base de dados
def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# Modelos Pydantic
class Bin(BaseModel):
    sensor_serial: str
    lat: float
    lon: float
    nfc_token: str
    topic: str
    fill_level: Union[str, None] = None

class FillLevelUpdate(BaseModel):
    fill_level: str

class User(BaseModel):
    uid: str
    role: str
    imei: Union[str, None] = None

class ImeiUpdate(BaseModel):
    imei: str

class UsageIncrement(BaseModel):
    pass

# Endpoints Bins
@app.get("/bins")
def get_bins():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM bins")
            return cursor.fetchall()
    finally:
        conn.close()

@app.post("/bins")
def add_bin(bin: Bin):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO bins (sensor_serial, lat, lon, nfc_token, topic)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (bin.sensor_serial, bin.lat, bin.lon, bin.nfc_token, bin.topic))
        conn.commit()
        return {"message": "Bin added successfully"}
    finally:
        conn.close()

@app.put("/bins/{bin_id}")
def update_bin(bin_id: int, bin: Bin):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE bins SET sensor_serial=%s, lat=%s, lon=%s, nfc_token=%s, topic=%s WHERE id=%s
            """
            cursor.execute(sql, (bin.sensor_serial, bin.lat, bin.lon, bin.nfc_token, bin.topic, bin_id))
        conn.commit()
        return {"message": "Bin updated successfully"}
    finally:
        conn.close()

@app.delete("/bins/{bin_id}")
def delete_bin(bin_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM bins WHERE id = %s", (bin_id,))
        conn.commit()
        return {"message": "Bin deleted successfully"}
    finally:
        conn.close()

@app.put("/bins/fill/{sensor_serial}")
def update_fill_level(sensor_serial: str, payload: FillLevelUpdate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE bins SET fill_level = %s WHERE sensor_serial = %s"
            cursor.execute(sql, (payload.fill_level, sensor_serial))
        conn.commit()
        return {"message": "Fill level updated successfully"}
    finally:
        conn.close()

# Endpoints Users
@app.get("/users")
def get_users():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
    finally:
        conn.close()

@app.get("/users/{uid}")
def get_user_by_uid(uid: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT uid, role, imei, usage_count FROM users WHERE uid = %s", (uid,))
            result = cursor.fetchone()
            if result:
                return result
            else:
                raise HTTPException(status_code=404, detail="User not found")
    finally:
        conn.close()

@app.post("/users")
def add_user(user: User):
    conn = get_connection()
    try:
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
    finally:
        conn.close()

@app.put("/users/{uid}/imei")
def update_user_imei(uid: str, payload: ImeiUpdate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE users SET imei = %s WHERE uid = %s"
            cursor.execute(sql, (payload.imei, uid))
        conn.commit()
        return {"message": "IMEI updated successfully"}
    finally:
        conn.close()

@app.post("/users/{uid}/increment_usage")
def increment_usage_count(uid: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE users SET usage_count = COALESCE(usage_count, 0) + 1 WHERE uid = %s"
            cursor.execute(sql, (uid,))
        conn.commit()
        return {"message": f"usage_count incremented for user {uid}"}
    finally:
        conn.close()

@app.get("/users/{uid}/usage_count")
def get_usage_count(uid: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT usage_count FROM users WHERE uid = %s", (uid,))
            result = cursor.fetchone()
            if result:
                return {"uid": uid, "usage_count": result["usage_count"]}
            else:
                raise HTTPException(status_code=404, detail="User not found")
    finally:
        conn.close()

@app.get("/users/exists/{uid}")
def check_user_exists(uid: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT role FROM users WHERE uid = %s", (uid,))
            result = cursor.fetchone()
            if result:
                return {"exists": True, "role": result["role"]}
            else:
                return {"exists": False}
    finally:
        conn.close()

@app.get("/users/by_imei/{imei}")
def get_user_by_imei(imei: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT uid, role, imei, usage_count FROM users WHERE imei = %s", (imei,))
            result = cursor.fetchone()
            if result:
                return result
            else:
                raise HTTPException(status_code=404, detail="User not found with this IMEI")
    finally:
        conn.close()

@app.post("/users/{uid}/reset_usage")
def reset_usage_count(uid: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE users SET usage_count = 0 WHERE uid = %s"
            cursor.execute(sql, (uid,))
        conn.commit()
        return {"message": f"usage_count resetado para o user {uid}"}
    finally:
        conn.close()