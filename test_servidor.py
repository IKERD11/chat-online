#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el servidor de chat
"""

import socket
import time
import threading

def test_conexion():
    """Probar conexión básica al servidor"""
    try:
        # Crear socket de prueba
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        print("🧪 Probando conexión al servidor...")
        sock.connect(("localhost", 12345))
        
        # Crear streams
        salida = sock.makefile('w', encoding='utf-8', buffering=1)
        entrada = sock.makefile('r', encoding='utf-8', buffering=1)
        
        # Enviar credenciales de prueba
        print("📨 Enviando credenciales...")
        salida.write("TestUser\n")
        salida.write("invitado\n")
        salida.flush()
        
        # Leer respuesta
        print("📥 Esperando respuesta del servidor...")
        respuesta = entrada.readline().strip()
        print(f"📨 Respuesta recibida: {respuesta}")
        
        if respuesta == "ACCESO_OK":
            print("✅ Conexión exitosa al servidor")
            
            # Simular actividad de usuario
            print("💬 Enviando mensaje de prueba...")
            salida.write("Hola servidor, este es un mensaje de prueba\n")
            salida.flush()
            
            # Esperar un poco más para simular uso real
            print("⏳ Simulando actividad del usuario...")
            time.sleep(2)
            
            # Probar comando de salas
            print("🏠 Probando comando de salas...")
            salida.write("/salas\n")
            salida.flush()
            time.sleep(1)
            
            # Salir correctamente
            print("👋 Cerrando conexión...")
            salida.write("/salir\n")
            salida.flush()
            
        else:
            print(f"❌ Error de autenticación: {respuesta}")
            
        sock.close()
        print("🔌 Conexión cerrada exitosamente")
        
    except ConnectionRefusedError:
        print("❌ El servidor no está ejecutándose en localhost:12345")
        print("💡 Asegúrate de ejecutar 'python ServidorChat.Py' primero")
    except Exception as e:
        print(f"❌ Error de prueba: {e}")

def test_multiple_connections():
    """Probar múltiples conexiones simultáneas"""
    print("\n🧪 Probando múltiples conexiones...")
    
    def cliente_simulado(id_cliente):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("localhost", 12345))
            
            salida = sock.makefile('w', encoding='utf-8', buffering=1)
            entrada = sock.makefile('r', encoding='utf-8', buffering=1)
            
            # Credenciales únicas para cada cliente
            salida.write(f"Cliente{id_cliente}\n")
            salida.write("invitado\n")
            salida.flush()
            
            respuesta = entrada.readline().strip()
            if respuesta == "ACCESO_OK":
                print(f"✅ Cliente {id_cliente} conectado")
                
                # Enviar mensaje
                salida.write(f"Hola, soy el cliente {id_cliente}\n")
                salida.flush()
                
                time.sleep(1)
                
                # Salir
                salida.write("/salir\n")
                salida.flush()
                
            sock.close()
            print(f"🔌 Cliente {id_cliente} desconectado")
            
        except Exception as e:
            print(f"❌ Error en cliente {id_cliente}: {e}")
    
    # Crear 3 clientes simultáneos
    hilos = []
    for i in range(3):
        hilo = threading.Thread(target=cliente_simulado, args=(i+1,))
        hilos.append(hilo)
        hilo.start()
        time.sleep(0.5)  # Pequeña pausa entre conexiones
    
    # Esperar a que terminen todos
    for hilo in hilos:
        hilo.join()
    
    print("✅ Prueba de múltiples conexiones completada")

if __name__ == "__main__":
    print("🍇 Grapes Fri Chat - Test de Servidor Completo")
    print("=" * 50)
    
    # Prueba básica
    test_conexion()
    
    # Prueba de múltiples conexiones
    test_multiple_connections()
    
    print("\n🎉 Todas las pruebas completadas")
