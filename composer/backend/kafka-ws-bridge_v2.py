import eventlet
eventlet.monkey_patch()

import json
import redis
from kafka import KafkaConsumer
from flask import Flask
from flask_socketio import SocketIO

# 🔧 Importar variáveis de configuração
from config import (
    KAFKA_SERVER,
    KAFKA_TOPICS,
    REDIS_HOST,
    REDIS_PORT,
    FLASK_PORT,
    FLASK_HOST,
    FLASK_DEBUG
)

# 🧠 Inicializar Flask + SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 🔗 Conexão ao Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
pubsub = r.pubsub()
pubsub.subscribe(*KAFKA_TOPICS)
print(f"📨 Subscrito aos tópicos Redis: {', '.join(KAFKA_TOPICS)} em {REDIS_HOST}:{REDIS_PORT}")

# 🔁 Configuração do Kafka Consumer
consumer = KafkaConsumer(
    *KAFKA_TOPICS,
    bootstrap_servers=KAFKA_SERVER,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
)
print(f"🔌 Ligado ao Kafka em {KAFKA_SERVER} nos tópicos: {', '.join(KAFKA_TOPICS)}")

# 🔄 Redis → WebSocket
def redis_listener():
    print("📡 Redis listener ativo...")
    for message in pubsub.listen():
        if message['type'] != 'message':
            continue
        try:
            topic = message['channel']
            data = json.loads(message['data'])
            print(f"📥 Redis => {topic}: {data}")
            socketio.emit(topic, data)
        except Exception as e:
            print(f"❌ Erro no listener Redis: {e}")

# 🔄 Kafka → Redis
def kafka_listener():
    print("📡 Kafka listener ativo...")
    for msg in consumer:
        try:
            topic = msg.topic
            data = msg.value
            print(f"📥 Kafka => {topic}: {data}")
            r.publish(topic, json.dumps(data))
        except Exception as e:
            print(f"❌ Erro no listener Kafka: {e}")

# 🔹 Rota default
@app.route("/")
def index():
    return "🧠 Kafka+Redis → WebSocket Bridge ativo"

# ▶️ Start
if __name__ == "__main__":
    print("🚀 A iniciar bridge unificada")
    eventlet.spawn(redis_listener)
    eventlet.spawn(kafka_listener)
    socketio.run(app, host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
