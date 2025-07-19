import asyncio
import websockets
import json
import mysql.connector
import os
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'admin123'),
    'database': os.getenv('DB_NAME', 'chat_online'),
    'autocommit': True,
    'charset': 'utf8mb4',
    'use_unicode': True
}

# Almacenar conexiones activas
conexiones_activas = set()
usuarios_conectados = {}

class ServidorWebSocket:
    def __init__(self):
        self.host = "0.0.0.0"
        self.puerto = int(os.getenv('WS_PORT', 8765))

    def conectar_db(self):
        """Conectar a la base de datos"""
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Exception as e:
            print(f"❌ Error conectando a BD: {e}")
            return None

    async def autenticar_usuario(self, usuario, password):
        """Autenticar usuario en la base de datos"""
        try:
            db = self.conectar_db()
            if not db:
                return False
                
            cur = db.cursor()
            cur.execute("SELECT id FROM usuarios WHERE username = %s AND password_hash = MD5(%s)", 
                       (usuario, password))
            result = cur.fetchone()
            cur.close()
            db.close()
            
            return bool(result)
        except Exception as e:
            print(f"❌ Error autenticando: {e}")
            return False

    async def registrar_usuario(self, usuario, password):
        """Registrar nuevo usuario"""
        try:
            db = self.conectar_db()
            if not db:
                return False
                
            cur = db.cursor()
            
            # Verificar si existe
            cur.execute("SELECT id FROM usuarios WHERE username = %s", (usuario,))
            if cur.fetchone():
                cur.close()
                db.close()
                return False
                
            # Registrar usuario
            cur.execute("""INSERT INTO usuarios (username, email, password_hash, fecha_registro, rol) 
                           VALUES (%s, %s, MD5(%s), NOW(), 'usuario')""", 
                       (usuario, f"{usuario}@chat.com", password))
            
            cur.close()
            db.close()
            return True
        except Exception as e:
            print(f"❌ Error registrando: {e}")
            return False

    async def manejar_cliente(self, websocket, path):
        """Manejar conexión de cliente WebSocket"""
        print(f"🔗 Nueva conexión WebSocket: {websocket.remote_address}")
        conexiones_activas.add(websocket)
        
        try:
            async for mensaje in websocket:
                try:
                    data = json.loads(mensaje)
                    await self.procesar_mensaje(websocket, data)
                except json.JSONDecodeError:
                    await self.enviar_error(websocket, "Formato de mensaje inválido")
                except Exception as e:
                    print(f"❌ Error procesando mensaje: {e}")
                    await self.enviar_error(websocket, "Error procesando mensaje")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"❌ Conexión cerrada: {websocket.remote_address}")
        except Exception as e:
            print(f"❌ Error en conexión: {e}")
        finally:
            conexiones_activas.discard(websocket)
            # Remover usuario si estaba conectado
            usuario_desconectado = None
            for usuario, ws in usuarios_conectados.items():
                if ws == websocket:
                    usuario_desconectado = usuario
                    break
            if usuario_desconectado:
                del usuarios_conectados[usuario_desconectado]
                await self.notificar_usuarios_conectados()

    async def procesar_mensaje(self, websocket, data):
        """Procesar diferentes tipos de mensajes"""
        tipo = data.get('tipo')
        
        if tipo == 'login':
            await self.manejar_login(websocket, data)
        elif tipo == 'registro':
            await self.manejar_registro(websocket, data)
        elif tipo == 'invitado':
            await self.manejar_invitado(websocket, data)
        elif tipo == 'mensaje':
            await self.manejar_mensaje_chat(websocket, data)
        else:
            await self.enviar_error(websocket, "Tipo de mensaje no reconocido")

    async def manejar_login(self, websocket, data):
        """Manejar login de usuario"""
        usuario = data.get('usuario')
        password = data.get('password')
        
        if await self.autenticar_usuario(usuario, password):
            usuarios_conectados[usuario] = websocket
            await websocket.send(json.dumps({
                'tipo': 'login_exitoso',
                'usuario': usuario
            }))
            await self.notificar_usuarios_conectados()
            print(f"✅ Usuario {usuario} logueado")
        else:
            await self.enviar_error(websocket, "Credenciales incorrectas")

    async def manejar_registro(self, websocket, data):
        """Manejar registro de nuevo usuario"""
        usuario = data.get('usuario')
        password = data.get('password')
        
        if await self.registrar_usuario(usuario, password):
            usuarios_conectados[usuario] = websocket
            await websocket.send(json.dumps({
                'tipo': 'registro_exitoso',
                'usuario': usuario
            }))
            await self.notificar_usuarios_conectados()
            print(f"✅ Usuario {usuario} registrado y logueado")
        else:
            await self.enviar_error(websocket, "Error en el registro. Usuario puede existir ya.")

    async def manejar_invitado(self, websocket, data):
        """Manejar modo invitado"""
        usuario = data.get('usuario')
        usuarios_conectados[usuario] = websocket
        await websocket.send(json.dumps({
            'tipo': 'login_exitoso',
            'usuario': usuario
        }))
        await self.notificar_usuarios_conectados()
        print(f"✅ Invitado {usuario} conectado")

    async def manejar_mensaje_chat(self, websocket, data):
        """Manejar mensaje de chat y redistribuir"""
        usuario = data.get('usuario')
        mensaje = data.get('mensaje')
        sala = data.get('sala', 'General')
        
        # Verificar que el usuario está conectado
        if usuario not in usuarios_conectados:
            await self.enviar_error(websocket, "No estás conectado")
            return
        
        # Redistribuir mensaje a todos los usuarios conectados
        mensaje_broadcast = {
            'tipo': 'mensaje',
            'usuario': usuario,
            'mensaje': mensaje,
            'sala': sala,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        await self.broadcast_mensaje(mensaje_broadcast)
        print(f"💬 [{sala}] {usuario}: {mensaje}")

    async def broadcast_mensaje(self, mensaje):
        """Enviar mensaje a todos los usuarios conectados"""
        if conexiones_activas:
            await asyncio.gather(
                *[ws.send(json.dumps(mensaje)) for ws in conexiones_activas],
                return_exceptions=True
            )

    async def notificar_usuarios_conectados(self):
        """Notificar lista de usuarios conectados"""
        usuarios_lista = list(usuarios_conectados.keys())
        mensaje = {
            'tipo': 'usuarios_conectados',
            'usuarios': usuarios_lista,
            'total': len(usuarios_lista)
        }
        await self.broadcast_mensaje(mensaje)

    async def enviar_error(self, websocket, mensaje_error):
        """Enviar mensaje de error a un cliente específico"""
        try:
            await websocket.send(json.dumps({
                'tipo': 'error',
                'mensaje': mensaje_error
            }))
        except:
            pass

    async def iniciar_servidor(self):
        """Iniciar el servidor WebSocket"""
        print(f"🚀 Iniciando servidor WebSocket en {self.host}:{self.puerto}")
        
        # Iniciar servidor
        start_server = websockets.serve(
            self.manejar_cliente, 
            self.host, 
            self.puerto,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=10
        )
        
        await start_server
        print(f"✅ Servidor WebSocket activo en ws://{self.host}:{self.puerto}")
        
        # Mantener servidor corriendo
        await asyncio.Future()  # Correr indefinidamente

if __name__ == "__main__":
    servidor = ServidorWebSocket()
    
    try:
        asyncio.run(servidor.iniciar_servidor())
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
