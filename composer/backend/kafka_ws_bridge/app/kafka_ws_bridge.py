# import eventlet
# eventlet.monkey_patch()

# import json
# import time
# from flask import Flask
# from flask_socketio import SocketIO
# from kafka import KafkaConsumer

# from config import KAFKA_SERVER, KAFKA_TOPICS, FLASK_HOST, FLASK_PORT, FLASK_DEBUG

# app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# def safe_deserializer(msg):
#     try:
#         return json.loads(msg.decode("utf-8"))
#     except Exception as e:
#         print(f"❌ Erro ao decodificar mensagem Kafka: {e}")
#         return {}

# def kafka_consumer_worker(topic):
#     print(f"🔁 Subscrito ao tópico Kafka: {topic}")
#     consumer = KafkaConsumer(
#         topic,
#         bootstrap_servers=KAFKA_SERVER,
#         value_deserializer=safe_deserializer,
#         auto_offset_reset="latest",
#         enable_auto_commit=True,
#         group_id=f"ws-bridge-{topic}-{int(time.time())}"
#     )

#     for msg in consumer:
#         data = msg.value
#         print(f"📥 Kafka [{topic}] => {data}")
#         socketio.emit(topic, data)
#         print(f"📤 Emitido para WebSocket: {topic} => {data}")

# @app.route("/")
# def index():
#     return "🧠 Kafka-to-WebSocket Bridge com Eventlet ativo"

# if __name__ == "__main__":
#     print("🚀 A iniciar bridge com Eventlet...")

#     for topic in KAFKA_TOPICS:
#         eventlet.spawn(kafka_consumer_worker, topic)

#     socketio.run(app, host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)

import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiokafka import AIOKafkaConsumer
from config import KAFKA_SERVER, KAFKA_TOPICS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou especifica o domínio da tua app frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
connected_websockets = set()

def safe_deserializer_sync(msg):
    try:
        return json.loads(msg.decode("utf-8"))
    except Exception as e:
        print(f"❌ Erro ao decodificar mensagem Kafka: {e}")
        return {}

@app.on_event("startup")
async def startup_event():
    app.state.consumer = AIOKafkaConsumer(
        *KAFKA_TOPICS,
        bootstrap_servers=KAFKA_SERVER,
        group_id="ws-bridge-group",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=safe_deserializer_sync
    )
    await app.state.consumer.start()
    asyncio.create_task(kafka_consumer_loop())

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.consumer.stop()

async def kafka_consumer_loop():
    consumer = app.state.consumer
    async for msg in consumer:
        data = msg.value
        # Enviar a todos os websockets conectados
        websockets_copy = connected_websockets.copy()
        for ws in websockets_copy:
            try:
                await ws.send_json({"topic": msg.topic, "data": data})
            except Exception:
                connected_websockets.remove(ws)

@app.get("/")
async def index():
    return {"message": "Kafka-to-WebSocket Bridge com FastAPI ativo"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Mantém a conexão aberta
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)
    except Exception:
        connected_websockets.remove(websocket)
