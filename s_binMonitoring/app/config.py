from dotenv import load_dotenv
import os
import redis
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


import redis
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def load_lookup_file():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        print("✅ Redis ligado — a carregar sensores do ficheiro...")

        if not os.path.exists(LOOKUP_FILE):
            print(f"⚠️ Ficheiro de lookup '{LOOKUP_FILE}' não encontrado. Nenhum sensor será carregado.")
            return

        # Abrir ficheiro e acumular sensores + tópicos
        sensor_topic_map = {}
        with open(LOOKUP_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                sensor_id, topic = line.split(":", 1)
                sensor_topic_map[sensor_id.strip()] = topic.strip()

        # Carregar para o Redis
        for sensor_id, topic in sensor_topic_map.items():
            if not r.exists(sensor_id):
                r.set(sensor_id, topic)

        print(f"✅ {len(sensor_topic_map)} sensores carregados para Redis.")

        # Criar tópicos no Kafka
        existing_topics = set()
        try:
            admin = KafkaAdminClient(bootstrap_servers=KAFKA_SERVER)
            existing_topics = set(admin.list_topics())

            new_topics = []
            for topic in set(sensor_topic_map.values()):
                if topic not in existing_topics:
                    new_topics.append(NewTopic(name=topic, num_partitions=3, replication_factor=1))

            if new_topics:
                admin.create_topics(new_topics)
                print(f"✅ {len(new_topics)} tópicos criados no Kafka.")
            else:
                print("ℹ️ Todos os tópicos já existem no Kafka.")

            admin.close()
        except Exception as e:
            print(f"⚠️ Erro ao criar tópicos Kafka: {e}")

    except redis.RedisError as e:
        print(f"❌ Erro ao conectar ao Redis: {e}")


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
#LOOKUP_FILE = os.getenv("LOOKUP_FILE", "sensor_lookup.txt")
#LOOKUP_FILE = os.getenv("LOOKUP_FILE", "/data/sensor_lookup.txt")

# Autenticação básica (apenas se usado)
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER", "admin")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS", "secret")
