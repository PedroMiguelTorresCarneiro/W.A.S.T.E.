from flask import Flask
from flask_socketio import SocketIO
from kafka import KafkaConsumer
import json
import threading
import time
from config import KAFKA_SERVER, KAFKA_TOPICS, FLASK_HOST, FLASK_PORT, FLASK_DEBUG

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

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
    return "🧠 Kafka-to-WebSocket Bridge ativo"

if __name__ == "__main__":
    print("🚀 A iniciar o Kafka-WS bridge...")

    for topic in KAFKA_TOPICS:
        t = threading.Thread(target=kafka_consumer_worker, args=(topic,), daemon=True)
        t.start()

    socketio.run(app, host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG, use_reloader=False)
