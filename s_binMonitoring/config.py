from dotenv import load_dotenv
import os

# Carrega variáveis do ficheiro .env
load_dotenv()

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Kafka
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "iot_logs")
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")

# Flask
FLASK_PORT = int(os.getenv("FLASK_PORT", 5004))
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")

# Ficheiro de associação sensor <-> tópico
LOOKUP_FILE = os.getenv("LOOKUP_FILE", "sensor_lookup.txt")

# Autenticação básica (apenas se usado)
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER", "admin")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS", "secret")
