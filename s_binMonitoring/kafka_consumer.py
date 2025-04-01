import asyncio
import websockets
from kafka import KafkaConsumer
import threading

# Configuração do Kafka
KAFKA_TOPIC = "bin-monitoring"
KAFKA_SERVER = "localhost:9092"

# Criar o consumidor do Kafka numa thread separada
def kafka_consumer_thread():
    """Função que roda o Kafka Consumer numa thread separada"""
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_SERVER,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="waste_group"
        )
        print("✅ Kafka Consumer conectado com sucesso!")

        for message in consumer:
            msg = message.value.decode("utf-8")
            print(f"📩 Kafka Received: {msg}")

            # Envia a mensagem para os clientes WebSocket
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(broadcast_message(msg))

    except Exception as e:
        print(f"❌ ERRO ao conectar ao Kafka: {e}")

# Lista de clientes WebSocket conectados
clients = set()

async def websocket_handler(websocket, path=None):
    """Gerencia conexões WebSocket."""
    clients.add(websocket)
    print(f"✅ Novo cliente WebSocket conectado! Total: {len(clients)}")

    try:
        async for message in websocket:
            print(f"📨 Mensagem WebSocket recebida: {message}")

    except websockets.exceptions.ConnectionClosed:
        print("❌ Cliente WebSocket desconectado.")

    finally:
        if websocket in clients:
            clients.remove(websocket)
        print(f"📢 Clientes restantes: {len(clients)}")

async def broadcast_message(msg):
    """Envia mensagens do Kafka para todos os clientes WebSocket conectados."""
    if clients:
        print(f"📤 Enviando para {len(clients)} clientes WebSocket.")
        disconnected_clients = set()

        for client in clients:
            try:
                await client.send(msg)
            except websockets.exceptions.ConnectionClosed:
                print("❌ Cliente WebSocket desconectado.")
                disconnected_clients.add(client)

        clients.difference_update(disconnected_clients)

    else:
        print("⚠️ Nenhum cliente WebSocket conectado. Mensagem não enviada.")

async def main():
    """Inicia o servidor WebSocket."""
    server = await websockets.serve(websocket_handler, "0.0.0.0", 8888)
    print("✅ Servidor WebSocket ativo em ws://0.0.0.0:8888")

    # Inicia o Kafka Consumer numa thread separada
    kafka_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
    kafka_thread.start()

    await server.wait_closed()

asyncio.run(main())
