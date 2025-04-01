from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql

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
    fill_level: str | None = None  # opcional ao criar
    
# Modelo para atualizar o nível de preenchimento
class FillLevelUpdate(BaseModel):
    fill_level: str


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
