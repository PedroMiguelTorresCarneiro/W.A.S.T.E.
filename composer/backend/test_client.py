# import socketio

# # Instância do cliente Socket.IO com logs ativos
# sio = socketio.Client(logger=True, engineio_logger=True)

# # Evento de conexão
# @sio.on('connect')
# def on_connect():
#     print('✅ Conectado ao WebSocket!')

# # Evento de desconexão
# @sio.on('disconnect')
# def on_disconnect():
#     print('❌ Desconectado do WebSocket.')

# # Evento para escutar mensagens do tópico "bin_monitoring"
# @sio.on('bin_monitoring')
# def on_bin_monitoring(data):
#     print(f'📥 Mensagem recebida [bin_monitoring]: {data}')

# # Conectar ao WebSocket (porta 5006 da bridge)
# try:
#     print("🔌 A tentar conectar ao WebSocket...")
#     sio.connect('wss://grupo2-egs-deti.ua.pt/ws', transports=['websocket'])
#     sio.wait()
# except Exception as e:
#     print(f'⚠️ Erro ao conectar: {e}')

import asyncio
import websockets

async def test():
    uri = "ws://grupo2-egs-deti.ua.pt/ws"  # ou wss:// se usares HTTPS
    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            print("Recebido:", msg)

asyncio.run(test())