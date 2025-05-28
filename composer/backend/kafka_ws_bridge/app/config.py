# config.py (para Kafka → WebSocket Bridge)
from dotenv import load_dotenv
import os

load_dotenv()

# ---------- Kafka ----------
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
KAFKA_TOPICS = os.getenv("KAFKA_TOPICS", "bin_monitoring,nfc_logs,nfc-tags").split(",")

# ---------- Flask WebSocket ----------
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5006))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
