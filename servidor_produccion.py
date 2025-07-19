import socket
import threading
import mysql.connector
import time
import traceback
import os
import ssl
from datetime import datetime

# Configuración para producción
HOST = "0.0.0.0"  # Escuchar en todas las interfaces
PUERTO = int(os.getenv('PORT', 12345))  # Para servicios como Heroku

# Base de datos - usar variables de entorno
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'admin123'),
    'database': os.getenv('DB_NAME', 'chat_online'),
    'autocommit': True,
    'connection_timeout': 10,
    'charset': 'utf8mb4',
    'use_unicode': True
}

# Configuración global
salas = {"General": []}
clientes = {}
lock = threading.Lock()
servidor_activo = True

class ServidorChatProduccion:
    def __init__(self):
        self.host = HOST
        self.puerto = PUERTO
        self.socket_servidor = None
        self.ssl_context = None
        
    def configurar_ssl(self):
        """Configurar SSL para conexiones seguras (opcional)"""
        try:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain('cert.pem', 'key.pem')
            print("✅ SSL configurado correctamente")
        except Exception as e:
            print(f"⚠️ SSL no configurado: {e}")
            self.ssl_context = None

    def conectar_db(self):
        """Conectar a la base de datos con configuración de producción"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            return connection
        except mysql.connector.Error as e:
            print(f"❌ Error MySQL: {e}")
            return None
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return None

    def iniciar_servidor(self):
        """Iniciar servidor para producción"""
        try:
            self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_servidor.bind((self.host, self.puerto))
            self.socket_servidor.listen(100)  # Más conexiones concurrentes
            
            print(f"🚀 Servidor iniciado en {self.host}:{self.puerto}")
            print(f"📊 Configuración: {DB_CONFIG['host']}:{DB_CONFIG['database']}")
            
            while servidor_activo:
                try:
                    cliente_socket, direccion = self.socket_servidor.accept()
                    print(f"🔗 Nueva conexión desde: {direccion}")
                    
                    # Aplicar SSL si está configurado
                    if self.ssl_context:
                        cliente_socket = self.ssl_context.wrap_socket(cliente_socket, server_side=True)
                    
                    thread = threading.Thread(
                        target=self.manejar_cliente, 
                        args=(cliente_socket, direccion)
                    )
                    thread.daemon = True
                    thread.start()
                    
                except Exception as e:
                    if servidor_activo:
                        print(f"❌ Error aceptando conexión: {e}")
                        
        except Exception as e:
            print(f"❌ Error fatal del servidor: {e}")
        finally:
            if self.socket_servidor:
                self.socket_servidor.close()

    def manejar_cliente(self, cliente_socket, direccion):
        """Manejar cliente con mejor gestión de errores"""
        try:
            # Tu lógica de manejo de clientes aquí
            # (copiada del ServidorChat.py original)
            pass
        except Exception as e:
            print(f"❌ Error con cliente {direccion}: {e}")
        finally:
            try:
                cliente_socket.close()
            except:
                pass

if __name__ == "__main__":
    servidor = ServidorChatProduccion()
    
    # Configurar SSL si es necesario
    # servidor.configurar_ssl()
    
    try:
        servidor.iniciar_servidor()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        servidor_activo = False
    except Exception as e:
        print(f"❌ Error fatal: {e}")
