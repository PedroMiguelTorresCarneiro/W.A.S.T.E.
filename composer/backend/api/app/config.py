# config.py (para FastAPI)
from dotenv import load_dotenv
import os

load_dotenv()

# ---------- BASE DE DADOS ----------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3307))
DB_USER = os.getenv("DB_USER", "waste_user")
DB_PASS = os.getenv("DB_PASS", "wastepass")
DB_NAME = os.getenv("DB_NAME", "waste_db")

# ---------- UVICORN ----------
UVICORN_HOST = os.getenv("UVICORN_HOST", "0.0.0.0")
UVICORN_PORT = int(os.getenv("UVICORN_PORT", 5008))
