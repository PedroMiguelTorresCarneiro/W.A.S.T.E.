from dotenv import load_dotenv
import os

# Carrega as variáveis do ficheiro .env
load_dotenv()

# Define as variáveis como constantes
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "admin")
DB_NAME = os.getenv("DB_NAME", "routes_service")

OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org")

FLASK_PORT = int(os.getenv("FLASK_PORT", 5002))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")  # default alterado para estar pronto para produção
