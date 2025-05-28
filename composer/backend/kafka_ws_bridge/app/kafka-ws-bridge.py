import eventlet
eventlet.monkey_patch()

import json
import time
from flask import Flask
from flask_socketio import SocketIO
from kafka import KafkaConsumer

from config import KAFKA_SERVER, KAFKA_TOPICS, FLASK_HOST, FLASK_PORT, FLASK_DEBUG

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

def safe_deserializer(msg):
    try:
        return json.loads(msg.decode("utf-8"))
    except Exception as e:
        print(f"❌ Erro ao decodificar mensagem Kafka: {e}")
        return {}

def kafka_consumer_worker(topic):
    print(f"🔁 Subscrito ao tópico Kafka: {topic}")
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=safe_deserializer,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=f"ws-bridge-{topic}-{int(time.time())}"
    )

    for msg in consumer:
        data = msg.value
        print(f"📥 Kafka [{topic}] => {data}")
        socketio.emit(topic, data)
        print(f"📤 Emitido para WebSocket: {topic} => {data}")

@app.route("/")
def index():
    return "🧠 Kafka-to-WebSocket Bridge com Eventlet ativo"

if __name__ == "__main__":
    print("🚀 A iniciar bridge com Eventlet...")

    for topic in KAFKA_TOPICS:
        eventlet.spawn(kafka_consumer_worker, topic)

    socketio.run(app, host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)