from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from kafka import KafkaProducer
import json
import os

# Configuração de variáveis (podes usar .env se quiseres depois)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

# Inicializar produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# App FastAPI com root_path para Kong
app = FastAPI(
    title="Posting API",
    description="API para publicar dados de sensores e interações NFC no Kafka.",
    version="1.0.0",
    root_path="/v1/posting",
    docs_url="/docs",
    redoc_url=None
)

# --- Schemas ---

class SensorData(BaseModel):
    serial: str
    fill_level: int

class NFCData(BaseModel):
    imei: str
    serial: str
    timestamp: datetime

# --- Função auxiliar para publicar no Kafka ---

def publish_to_kafka(topic: str, message: dict):
    try:
        producer.send(topic, value=message)
        producer.flush()
    except Exception as e:
        print(f"Erro ao enviar para Kafka: {e}")

# --- Endpoints ---

@app.post("/sensors", summary="Enviar dados do sensor", tags=["Sensores"])
async def post_sensor_data(sensor: SensorData):
    message = {
        "serial": sensor.serial,
        "fill_level": sensor.fill_level
    }
    publish_to_kafka("iot_logs", message)
    return {"status": "ok", "posted_to": "iot_logs", "message": message}

@app.post("/nfc", summary="Enviar interação NFC", tags=["NFC"])
async def post_nfc_data(nfc: NFCData):
    message = {
        "imei": nfc.imei,
        "serial": nfc.serial,
        "timestamp": nfc.timestamp.isoformat()
    }
    publish_to_kafka("nfc_logs", message)
    return {"status": "ok", "posted_to": "nfc_logs", "message": message}
