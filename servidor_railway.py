import asyncio
import websockets
import json
import os
from datetime import datetime

# Puerto dinámico para Railway
PORT = int(os.environ.get("PORT", 8765))

# Almacenar conexiones y usuarios en memoria (sin DB por ahora)
conexiones_activas = set()
usuarios_conectados = {}
mensajes_globales = []

class ServidorWebSocketSimple:
    def __init__(self):
        self.host = "0.0.0.0"
        self.puerto = PORT

    async def manejar_conexion(self, websocket, path=None):
        """Manejar nueva conexión WebSocket"""
        conexiones_activas.add(websocket)
        print(f"✅ Nueva conexión. Total: {len(conexiones_activas)}")
        
        try:
            async for mensaje in websocket:
                try:
                    data = json.loads(mensaje)
                    await self.procesar_mensaje(websocket, data)
                except json.JSONDecodeError:
                    print("❌ Error: JSON inválido")
                except Exception as e:
                    print(f"❌ Error procesando mensaje: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Conexión cerrada")
        except Exception as e:
            print(f"❌ Error en conexión: {e}")
        finally:
            conexiones_activas.discard(websocket)
            # Remover usuario de la lista
            usuario_desconectado = None
            for usuario, ws in usuarios_conectados.items():
                if ws == websocket:
                    usuario_desconectado = usuario
                    break
            
            if usuario_desconectado:
                del usuarios_conectados[usuario_desconectado]
                await self.broadcast_usuarios_online()
            
            print(f"📊 Conexiones restantes: {len(conexiones_activas)}")

    async def procesar_mensaje(self, websocket, data):
        """Procesar diferentes tipos de mensajes"""
        tipo = data.get('tipo', '')
        
        if tipo == 'login':
            await self.manejar_login(websocket, data)
        elif tipo == 'registro':
            await self.manejar_registro(websocket, data)
        elif tipo == 'invitado':
            await self.manejar_invitado(websocket, data)
        elif tipo == 'mensaje':
            await self.manejar_mensaje(websocket, data)
        else:
            print(f"⚠️ Tipo de mensaje desconocido: {tipo}")

    async def manejar_login(self, websocket, data):
        """Manejar login de usuario (modo simple)"""
        usuario = data.get('usuario', '')
        
        # En modo simple, todos los logins son válidos
        usuarios_conectados[usuario] = websocket
        
        respuesta = {
            'tipo': 'login_exitoso',
            'usuario': usuario,
            'mensaje': f'¡Bienvenido {usuario}!'
        }
        
        await websocket.send(json.dumps(respuesta))
        await self.broadcast_usuarios_online()
        
        # Enviar mensajes anteriores
        for msg in mensajes_globales[-10:]:  # Últimos 10 mensajes
            await websocket.send(json.dumps(msg))

    async def manejar_registro(self, websocket, data):
        """Manejar registro de usuario (modo simple)"""
        usuario = data.get('usuario', '')
        
        # En modo simple, todos los registros son válidos
        usuarios_conectados[usuario] = websocket
        
        respuesta = {
            'tipo': 'registro_exitoso',
            'usuario': usuario,
            'mensaje': f'¡Usuario {usuario} registrado exitosamente!'
        }
        
        await websocket.send(json.dumps(respuesta))
        await self.broadcast_usuarios_online()

    async def manejar_invitado(self, websocket, data):
        """Manejar acceso como invitado"""
        usuario = data.get('usuario', '')
        usuarios_conectados[usuario] = websocket
        
        respuesta = {
            'tipo': 'invitado_aceptado',
            'usuario': usuario,
            'mensaje': f'¡Bienvenido {usuario}!'
        }
        
        await websocket.send(json.dumps(respuesta))
        await self.broadcast_usuarios_online()
        
        # Enviar mensajes anteriores
        for msg in mensajes_globales[-10:]:
            await websocket.send(json.dumps(msg))

    async def manejar_mensaje(self, websocket, data):
        """Manejar envío de mensajes"""
        usuario = data.get('usuario', 'Anónimo')
        mensaje = data.get('mensaje', '')
        sala = data.get('sala', 'General')
        
        if not mensaje.strip():
            return
        
        # Crear mensaje
        mensaje_data = {
            'tipo': 'mensaje',
            'usuario': usuario,
            'mensaje': mensaje,
            'sala': sala,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        
        # Guardar en memoria
        mensajes_globales.append(mensaje_data)
        
        # Mantener solo los últimos 100 mensajes
        if len(mensajes_globales) > 100:
            mensajes_globales.pop(0)
        
        # Broadcast a todos los usuarios
        await self.broadcast_mensaje(mensaje_data)

    async def broadcast_mensaje(self, mensaje):
        """Enviar mensaje a todos los usuarios conectados"""
        if conexiones_activas:
            mensaje_json = json.dumps(mensaje)
            await asyncio.gather(
                *[ws.send(mensaje_json) for ws in conexiones_activas],
                return_exceptions=True
            )

    async def broadcast_usuarios_online(self):
        """Enviar lista de usuarios online"""
        usuarios_online = {
            'tipo': 'usuarios_online',
            'usuarios': list(usuarios_conectados.keys()),
            'total': len(usuarios_conectados)
        }
        
        if conexiones_activas:
            mensaje_json = json.dumps(usuarios_online)
            await asyncio.gather(
                *[ws.send(mensaje_json) for ws in conexiones_activas],
                return_exceptions=True
            )

    async def iniciar_servidor(self):
        """Iniciar el servidor WebSocket"""
        print(f"🚀 Iniciando servidor WebSocket en puerto {self.puerto}")
        print(f"🌐 Servidor accesible en: ws://0.0.0.0:{self.puerto}")
        
        try:
            # Configuración más compatible para Railway
            servidor = await websockets.serve(
                self.manejar_conexion,
                self.host,
                self.puerto,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            
            print(f"✅ Servidor WebSocket iniciado correctamente")
            print(f"📡 Esperando conexiones...")
            
            # Mantener el servidor corriendo
            await servidor.wait_closed()
            
        except Exception as e:
            print(f"❌ Error al iniciar servidor: {e}")
            # Intentar con configuración alternativa
            try:
                print("🔄 Reintentando con configuración simplificada...")
                servidor = await websockets.serve(
                    self.manejar_conexion,
                    self.host,
                    self.puerto
                )
                print(f"✅ Servidor iniciado en modo simplificado")
                await servidor.wait_closed()
            except Exception as e2:
                print(f"❌ Error fatal: {e2}")

if __name__ == "__main__":
    print("🎯 Iniciando Chat Online - Servidor WebSocket Simple")
    print(f"🔧 Puerto configurado: {PORT}")
    print(f"🌍 Host configurado: 0.0.0.0")
    print(f"📊 Variables de entorno disponibles:")
    print(f"   - PORT: {os.environ.get('PORT', 'No definido')}")
    print(f"   - HOST: {os.environ.get('HOST', 'No definido')}")
    
    servidor = ServidorWebSocketSimple()
    
    try:
        asyncio.run(servidor.iniciar_servidor())
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
