import socket
import threading
import mysql.connector
import time
import traceback
from datetime import datetime

HOST = "0.0.0.0"
PUERTO = 12345

# Configuración global
salas = {"General": []}  # Cambiar de set() a lista para permitir diccionarios
clientes = {}  # socket -> client info
lock = threading.Lock()
servidor_activo = True

def conectar_db():
    """Conectar a la base de datos con manejo robusto de errores"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="admin123",
            database="chat_online",
            autocommit=True,
            connection_timeout=10,
            charset='utf8mb4',
            use_unicode=True
        )
        return connection
    except mysql.connector.Error as e:
        print(f"❌ Error MySQL conectando a la base de datos: {e}")
        return None
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def autenticar_usuario(usuario, password):
    """Autenticar usuario con manejo robusto de errores"""
    try:
        db = conectar_db()
        if not db:
            print(f"⚠️ Sin conexión a BD para autenticar {usuario}")
            return False
            
        cur = db.cursor()
        cur.execute("SELECT id FROM usuarios WHERE username = %s AND password_hash = MD5(%s)", 
                   (usuario, password))
        result = cur.fetchone()
        cur.close()
        db.close()
        
        if result:
            print(f"✅ Usuario {usuario} autenticado exitosamente")
            return True
        else:
            print(f"❌ Credenciales incorrectas para {usuario}")
            return False
            
    except mysql.connector.Error as e:
        print(f"❌ Error MySQL autenticando usuario {usuario}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error autenticando usuario {usuario}: {e}")
        return False

def registrar_usuario(usuario, password):
    """Registrar nuevo usuario con validación"""
    try:
        db = conectar_db()
        if not db:
            print(f"⚠️ Sin conexión a BD para registrar {usuario}")
            return None
            
        cur = db.cursor()
        
        # Verificar si el usuario ya existe
        cur.execute("SELECT id FROM usuarios WHERE username = %s", (usuario,))
        if cur.fetchone():
            print(f"⚠️ Usuario {usuario} ya existe")
            cur.close()
            db.close()
            return None
            
        # Insertar nuevo usuario
        cur.execute("""INSERT INTO usuarios (username, email, password_hash, fecha_registro, rol) 
                       VALUES (%s, %s, MD5(%s), NOW(), 'usuario')""", 
                   (usuario, f"{usuario}@chat.com", password))
        
        cur.close()
        db.close()
        print(f"✅ Usuario {usuario} registrado exitosamente")
        return "registro_exitoso"
        
    except mysql.connector.IntegrityError:
        print(f"⚠️ Usuario {usuario} ya existe (error de integridad)")
        return None
    except mysql.connector.Error as e:
        print(f"❌ Error MySQL registrando usuario {usuario}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error registrando usuario {usuario}: {e}")
        return None

def broadcast(sala_nombre, mensaje):
    """Enviar mensaje a todos los usuarios de una sala con manejo de errores mejorado"""
    if not sala_nombre or not mensaje:
        return
        
    with lock:
        destinatarios = list(salas.get(sala_nombre, []))
    
    clientes_desconectados = []
    
    for cli in destinatarios:
        try:
            if cli and cli.get("sock") and cli.get("salida"):
                # Usar el stream de salida directo para mejor control
                salida = cli.get("salida")
                if salida:
                    salida.write(mensaje + "\n")
                    salida.flush()
                else:
                    # Fallback al método anterior si no hay stream de salida
                    mensaje_encoded = (mensaje + "\n").encode('utf-8', errors='replace')
                    cli["sock"].sendall(mensaje_encoded)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            print(f"🔌 Cliente {cli.get('nombre', 'desconocido')} desconectado durante broadcast")
            clientes_desconectados.append(cli["sock"])
        except (OSError, socket.error) as e:
            print(f"🔗 Error de socket enviando a {cli.get('nombre', 'desconocido')}: {e}")
            clientes_desconectados.append(cli["sock"])
        except Exception as e:
            print(f"❌ Error inesperado enviando mensaje a {cli.get('nombre', 'desconocido')}: {e}")
            clientes_desconectados.append(cli["sock"])
    
    # Limpiar clientes desconectados
    for sock in clientes_desconectados:
        desconectar(sock)

def actualizar_usuarios(sala_nombre):
    """Actualizar lista de usuarios en una sala"""
    try:
        with lock:
            lista = [c["nombre"] for c in salas.get(sala_nombre, []) if c and c.get("nombre")]
        
        if lista:
            mensaje_usuarios = "USUARIOS:" + ",".join(lista)
            print(f"📊 Enviando lista de usuarios para sala {sala_nombre}: {lista}")
            broadcast(sala_nombre, mensaje_usuarios)
        else:
            print(f"⚠️ No hay usuarios en sala {sala_nombre} para actualizar")
    except Exception as e:
        print(f"❌ Error actualizando usuarios en sala {sala_nombre}: {e}")

def enviar_mensaje_seguro(sock, mensaje):
    """Enviar mensaje a un socket específico de forma segura"""
    try:
        if sock and mensaje:
            mensaje_encoded = (mensaje + "\n").encode('utf-8', errors='replace')
            sock.sendall(mensaje_encoded)
            return True
    except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
        print("🔌 Cliente desconectado durante envío")
        return False
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False
    return False

def manejar_cliente(sock, addr):
    """Manejar conexión de cliente individual con manejo robusto de errores"""
    client = None
    usuario = None
    entrada = None
    salida = None
    
    try:
        # Configurar timeout inicial para autenticación
        sock.settimeout(30)  # 30 segundos para autenticación
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Configurar TCP_NODELAY para evitar buffering de paquetes pequeños
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        print(f"🔗 Nuevo cliente conectado desde {addr}")
        
        # Crear streams con buffering apropiado
        entrada = sock.makefile("r", encoding='utf-8', errors='replace', buffering=1)
        salida = sock.makefile("w", encoding='utf-8', errors='replace', buffering=1)
        
        # Leer credenciales con manejo robusto
        try:
            u = entrada.readline()
            if not u:
                print(f"❌ No se recibió usuario de {addr}")
                return
            u = u.strip()
            
            p = entrada.readline()
            if not p:
                print(f"❌ No se recibió contraseña de {addr}")
                return
            p = p.strip()
            
        except socket.timeout:
            print(f"⏱️ Timeout leyendo credenciales de {addr}")
            return
        except Exception as e:
            print(f"❌ Error leyendo credenciales de {addr}: {e}")
            return

        if not u or not p:
            print(f"❌ Credenciales vacías de {addr}")
            salida.write("ACCESO_DENEGADO\n")
            salida.flush()
            return
        
        # Proceso de autenticación mejorado
        if u.startswith("/registrar "):
            nuevo = u.split(" ", 1)[1].strip()
            if not nuevo or len(nuevo) < 3:
                print(f"❌ Nombre de usuario inválido: {nuevo}")
                salida.write("ACCESO_DENEGADO\n")
                salida.flush()
                return
                
            token = registrar_usuario(nuevo, p)
            if token:
                salida.write("ACCESO_OK\n")
                salida.flush()
                usuario = nuevo
                print(f"✅ Usuario {nuevo} registrado y conectado desde {addr}")
            else:
                salida.write("ACCESO_DENEGADO\n")
                salida.flush()
                return
                
        elif p == "invitado":
            if not u or len(u.strip()) < 2:
                print(f"❌ Apodo de invitado inválido: {u}")
                salida.write("ACCESO_DENEGADO\n")
                salida.flush()
                return
            salida.write("ACCESO_OK\n")
            salida.flush()
            usuario = u.strip()
            print(f"👤 Usuario invitado {usuario} conectado desde {addr}")
            
        else:
            if not autenticar_usuario(u, p):
                print(f"❌ Autenticación fallida para {u} desde {addr}")
                salida.write("ACCESO_DENEGADO\n")
                salida.flush()
                return
            salida.write("ACCESO_OK\n")
            salida.flush()
            usuario = u.strip()
            print(f"🔐 Usuario {usuario} autenticado desde {addr}")

        # Crear objeto cliente
        client = {
            "nombre": usuario,
            "sock": sock,
            "sala": "General",
            "addr": addr,
            "conectado": True,
            "salida": salida
        }
        
        # Registrar cliente
        with lock:
            if "General" not in salas:
                salas["General"] = []
            salas["General"].append(client)
            clientes[sock] = client

        # Configurar timeout para operaciones normales (sin timeout bloqueante)
        sock.settimeout(None)
        
        # Notificar sala y usuarios
        salida.write("SALA:General\n")
        salida.flush()
        broadcast("General", f"🎉 [SISTEMA] {usuario} se unió a la sala")
        actualizar_usuarios("General")

        # Bucle principal de mensajes con manejo mejorado
        while servidor_activo and client.get("conectado", False):
            try:
                # Leer mensaje sin timeout para evitar interrupciones
                linea = entrada.readline()
                
                if not linea:
                    print(f"🔌 Cliente {usuario} desconectado (EOF)")
                    break
                    
                msg = linea.strip()
                if not msg:
                    continue

                print(f"📨 Mensaje de {usuario}: {msg}")  # Debug

                # Procesar comandos
                if msg.startswith("/salir"):
                    print(f"👋 Cliente {usuario} salió voluntariamente")
                    break
                    
                elif msg.startswith("/salas"):
                    try:
                        with lock:
                            salas_info = []
                            for sala_nombre, usuarios in salas.items():
                                if usuarios:  # Solo salas con usuarios
                                    salas_info.append(f"{sala_nombre}|{len(usuarios)}")
                            listado = ",".join(salas_info) if salas_info else "General|0"
                        salida.write(f"SALAS:{listado}\n")
                        salida.flush()
                        print(f"📝 Lista de salas enviada a {usuario}: {listado}")
                    except Exception as e:
                        print(f"❌ Error listando salas para {usuario}: {e}")
                        try:
                            salida.write("SALAS:General|1\n")
                            salida.flush()
                        except:
                            pass
                        
                elif msg.startswith("/sala crear "):
                    try:
                        ns = msg.split(" ", 2)[2].strip()
                        if ns and len(ns) > 0:
                            with lock:
                                if ns not in salas:
                                    salas[ns] = []
                            print(f"🏠 Sala '{ns}' creada por {usuario}")
                            cambiar_sala(client, ns)
                        else:
                            salida.write("[SISTEMA] Nombre de sala inválido\n")
                            salida.flush()
                    except (IndexError, ValueError):
                        salida.write("[SISTEMA] Comando inválido\n")
                        salida.flush()
                        
                elif msg.startswith("/sala unir "):
                    try:
                        ns = msg.split(" ", 2)[2].strip()
                        with lock:
                            if ns in salas:
                                cambiar_sala(client, ns)
                            else:
                                salida.write(f"[SISTEMA] Sala '{ns}' no existe\n")
                                salida.flush()
                    except (IndexError, ValueError):
                        salida.write("[SISTEMA] Comando inválido\n")
                        salida.flush()
                        
                elif msg.startswith("/file "):
                    # Transferencia de archivos deshabilitada por estabilidad
                    salida.write("[SISTEMA] ⚠️ Transferencia de archivos deshabilitada por estabilidad\n")
                    salida.flush()
                    
                else:
                    # Mensaje normal de chat
                    if len(msg) > 1000:  # Limitar longitud de mensajes
                        msg = msg[:1000] + "..."
                    hora = datetime.now().strftime("%H:%M")
                    broadcast(client["sala"], f"[{hora}] {usuario}: {msg}")

            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                print(f"🔌 Cliente {usuario} desconectado abruptamente")
                break
            except Exception as e:
                print(f"❌ Error procesando mensaje de {usuario}: {e}")
                # Solo romper el bucle si es un error crítico
                if "closed" in str(e).lower() or "broken" in str(e).lower():
                    break
                # Para otros errores, continuar

    except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
        print(f"🔌 Cliente desde {addr} desconectado durante handshake")
    except socket.timeout:
        print(f"⏱️ Timeout de cliente desde {addr}")
    except Exception as e:
        print(f"❌ Error manejando cliente desde {addr}: {e}")
        print(traceback.format_exc())
    finally:
        # Limpiar conexión
        if client:
            client["conectado"] = False
        
        # Cerrar streams de forma segura
        try:
            if salida:
                salida.close()
        except:
            pass
        try:
            if entrada:
                entrada.close()
        except:
            pass
            
        desconectar(sock)

def cambiar_sala(client, nueva):
    """Cambiar usuario de sala con manejo de errores mejorado"""
    try:
        if not client or not nueva:
            return
            
        old = client.get("sala", "General")
        usuario = client.get("nombre", "Usuario")
        salida = client.get("salida")
        
        # Remover de sala anterior
        with lock:
            if old in salas and client in salas[old]:
                salas[old].remove(client)
        
        broadcast(old, f"👋 [SISTEMA] {usuario} salió de la sala")
        actualizar_usuarios(old)

        # Agregar a nueva sala
        client["sala"] = nueva
        with lock:
            if nueva not in salas:
                salas[nueva] = []
            salas[nueva].append(client)
        
        # Notificar cambio de sala usando stream directo
        try:
            if salida:
                salida.write(f"SALA:{nueva}\n")
                salida.flush()
                broadcast(nueva, f"🎉 [SISTEMA] {usuario} se unió a la sala")
                actualizar_usuarios(nueva)
                print(f"🏠 {usuario} cambió de sala {old} -> {nueva}")
            else:
                print(f"❌ Error: No hay stream de salida para {usuario}")
        except Exception as e:
            print(f"❌ Error notificando cambio de sala a {usuario}: {e}")
            
    except Exception as e:
        print(f"❌ Error cambiando sala: {e}")

def desconectar(sock):
    """Desconectar cliente y limpiar recursos"""
    try:
        with lock:
            client = clientes.pop(sock, None)
            
        if client:
            usuario = client.get("nombre", "Usuario")
            sala = client.get("sala", "General")
            
            # Marcar como desconectado
            client["conectado"] = False
            
            # Remover de sala
            with lock:
                if sala in salas and client in salas[sala]:
                    salas[sala].remove(client)
            
            # Notificar desconexión
            broadcast(sala, f"👋 [SISTEMA] {usuario} salió del chat")
            actualizar_usuarios(sala)
            print(f"🔌 {usuario} desconectado")
        
        # Cerrar socket
        try:
            sock.close()
        except:
            pass
            
    except Exception as e:
        print(f"❌ Error desconectando cliente: {e}")

def iniciar_servidor():
    """Iniciar servidor con manejo robusto de errores y configuración optimizada"""
    global servidor_activo
    srv = None
    
    try:
        # Crear socket del servidor con configuración robusta
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Configuraciones importantes para estabilidad
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) if hasattr(socket, 'SO_REUSEPORT') else None
        
        # Configurar timeout para accept() no bloqueante
        srv.settimeout(1.0)
        
        # Configurar el tamaño del buffer de recepción y envío
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 32768)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 32768)
        
        # Bind y listen
        srv.bind((HOST, PUERTO))
        srv.listen(20)  # Aumentar la cola de conexiones pendientes
        
        print(f"🚀 Servidor iniciado exitosamente")
        print(f"🌐 Escuchando en {HOST}:{PUERTO}")
        print(f"📊 Base de datos: {'✅ Conectada' if conectar_db() else '❌ Sin conexión'}")
        print(f"⚙️ Configuración optimizada para estabilidad")
        print("-" * 50)
        
        while servidor_activo:
            try:
                conn, addr = srv.accept()
                
                # Configurar socket del cliente con opciones robustas
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Configurar TCP_NODELAY para evitar delay de Nagle
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
                # Configurar buffers del cliente
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
                
                # Crear hilo para manejar cliente con configuración optimizada
                hilo_cliente = threading.Thread(
                    target=manejar_cliente, 
                    args=(conn, addr), 
                    daemon=True,
                    name=f"Cliente-{addr[0]}:{addr[1]}"
                )
                hilo_cliente.start()
                
                print(f"👥 Cliente {addr} atendido por hilo {hilo_cliente.name}")
                
            except socket.timeout:
                # Timeout normal del accept(), continuar
                continue
            except OSError as e:
                if servidor_activo:
                    print(f"❌ Error de socket aceptando conexión: {e}")
                    time.sleep(0.1)
            except Exception as e:
                if servidor_activo:
                    print(f"❌ Error inesperado aceptando conexión: {e}")
                    time.sleep(0.1)
                
    except PermissionError:
        print(f"❌ Error: Puerto {PUERTO} en uso o sin permisos")
    except OSError as e:
        print(f"❌ Error de sistema del servidor: {e}")
    except Exception as e:
        print(f"❌ Error fatal del servidor: {e}")
        print(traceback.format_exc())
    finally:
        servidor_activo = False
        if srv:
            try:
                srv.close()
                print("🔌 Servidor cerrado")
            except:
                pass
            
        # Estadísticas finales
        with lock:
            total_clientes = len(clientes)
        print(f"📊 Clientes conectados al cierre: {total_clientes}")

def shutdown_servidor():
    """Cerrar servidor gracefalmente"""
    global servidor_activo
    servidor_activo = False
    print("⏹️ Cerrando servidor...")
    
    # Desconectar todos los clientes
    with lock:
        clientes_copy = list(clientes.keys())
    
    for sock in clientes_copy:
        try:
            enviar_mensaje_seguro(sock, "[SISTEMA] Servidor cerrando...")
            sock.close()
        except:
            pass

if __name__ == "__main__":
    try:
        print("🍇 Grapes Fri Chat Server v2.0")
        print("=" * 50)
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\n⏹️ Servidor interrumpido por usuario")
        shutdown_servidor()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        print(traceback.format_exc())
    finally:
        print("👋 Servidor terminado")
