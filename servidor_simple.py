import asyncio
import websockets
import json
import os
from datetime import datetime

PORT = int(os.environ.get("PORT", 8000))

# Almacenar conexiones
connections = set()
users = {}

async def handle_client(websocket):
    """Manejar cliente WebSocket - Versión ultra simple"""
    connections.add(websocket)
    print(f"Cliente conectado. Total: {len(connections)}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await process_message(websocket, data)
            except:
                print("Error procesando mensaje")
    except:
        print("Cliente desconectado")
    finally:
        connections.discard(websocket)
        # Remover usuario
        user_to_remove = None
        for user, ws in users.items():
            if ws == websocket:
                user_to_remove = user
                break
        if user_to_remove:
            del users[user_to_remove]

async def process_message(websocket, data):
    """Procesar mensaje"""
    msg_type = data.get('tipo', '')
    
    if msg_type in ['login', 'registro', 'invitado']:
        username = data.get('usuario', 'Usuario')
        users[username] = websocket
        
        response = {
            'tipo': f'{msg_type}_exitoso',
            'usuario': username,
            'mensaje': f'¡Bienvenido {username}!'
        }
        await websocket.send(json.dumps(response))
        
    elif msg_type == 'mensaje':
        username = data.get('usuario', 'Anónimo')
        message = data.get('mensaje', '')
        
        if message.strip():
            msg_data = {
                'tipo': 'mensaje',
                'usuario': username,
                'mensaje': message,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            # Enviar a todos
            if connections:
                msg_json = json.dumps(msg_data)
                await asyncio.gather(
                    *[ws.send(msg_json) for ws in connections],
                    return_exceptions=True
                )

async def main():
    print(f"🚀 Servidor iniciando en puerto {PORT}")
    
    start_server = websockets.serve(
        handle_client,
        "0.0.0.0", 
        PORT
    )
    
    print(f"✅ Servidor WebSocket corriendo en 0.0.0.0:{PORT}")
    await start_server

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
