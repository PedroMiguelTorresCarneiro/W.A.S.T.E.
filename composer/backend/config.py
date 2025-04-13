# config.py
from dotenv import load_dotenv
import os

# 🔄 Carrega variáveis de ambiente do ficheiro .env
load_dotenv()

# ---------- BASE DE DADOS ----------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3307))
DB_USER = os.getenv("DB_USER", "waste_user")
DB_PASS = os.getenv("DB_PASS", "wastepass")
DB_NAME = os.getenv("DB_NAME", "waste_db")

# ---------- KAFKA ----------
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
KAFKA_TOPICS = os.getenv("KAFKA_TOPICS", "bin_monitoring,nfc_logs,nfc-tags").split(",")

# ---------- REDIS ----------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# ---------- FLASK WebSocket Bridge ----------
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5006))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")

# ---------- UVICORN (FastAPI opcional) ----------
UVICORN_HOST = os.getenv("UVICORN_HOST", "0.0.0.0")
UVICORN_PORT = int(os.getenv("UVICORN_PORT", 5008))
