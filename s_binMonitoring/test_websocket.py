import asyncio
import websockets

async def echo(websocket, path=None):  # <-- Definir `path=None` para evitar erros
    print("✅ Cliente conectado!")
    try:
        async for message in websocket:
            print(f"📨 Mensagem recebida: {message}")
            await websocket.send(f"Recebido: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("❌ Cliente desconectado.")

async def main():
    server = await websockets.serve(echo, "0.0.0.0", 8888)  # <-- O WebSocket Server ainda está na porta 8888
    print("✅ Servidor WebSocket ativo em ws://0.0.0.0:8888")
    await server.wait_closed()

asyncio.run(main())
