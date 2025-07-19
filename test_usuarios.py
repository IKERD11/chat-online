#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test específico para verificar la lista de usuarios
"""

import socket
import time
import threading

def test_usuarios():
    """Test para verificar la actualización de usuarios"""
    try:
        print("🧪 Test de lista de usuarios")
        
        # Cliente 1
        print("👤 Conectando Cliente 1...")
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock1.connect(("localhost", 12345))
        
        salida1 = sock1.makefile('w', encoding='utf-8', buffering=1)
        entrada1 = sock1.makefile('r', encoding='utf-8', buffering=1)
        
        # Autenticar cliente 1
        salida1.write("Usuario1\n")
        salida1.write("invitado\n")
        salida1.flush()
        
        resp1 = entrada1.readline().strip()
        print(f"✅ Cliente 1 autenticado: {resp1}")
        
        # Esperar un poco
        time.sleep(1)
        
        # Cliente 2
        print("👤 Conectando Cliente 2...")
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2.connect(("localhost", 12345))
        
        salida2 = sock2.makefile('w', encoding='utf-8', buffering=1)
        entrada2 = sock2.makefile('r', encoding='utf-8', buffering=1)
        
        # Autenticar cliente 2
        salida2.write("Usuario2\n")
        salida2.write("invitado\n")
        salida2.flush()
        
        resp2 = entrada2.readline().strip()
        print(f"✅ Cliente 2 autenticado: {resp2}")
        
        # Esperar mensajes de actualización
        print("📥 Esperando mensajes de actualización...")
        time.sleep(2)
        
        # Leer mensajes que puedan haber llegado
        def leer_mensajes(entrada, cliente_name):
            try:
                sock = entrada._sock
                sock.settimeout(1)  # Timeout corto para no bloquear
                for _ in range(10):  # Leer hasta 10 mensajes
                    try:
                        mensaje = entrada.readline().strip()
                        if mensaje:
                            print(f"📨 {cliente_name} recibió: {mensaje}")
                            if mensaje.startswith("USUARIOS:"):
                                usuarios = mensaje[8:].split(',')
                                print(f"👥 Lista de usuarios: {usuarios}")
                    except socket.timeout:
                        break
            except:
                pass
        
        print("📊 Leyendo mensajes del Cliente 1...")
        leer_mensajes(entrada1, "Cliente1")
        
        print("📊 Leyendo mensajes del Cliente 2...")
        leer_mensajes(entrada2, "Cliente2")
        
        # Desconectar clientes
        print("👋 Desconectando clientes...")
        salida1.write("/salir\n")
        salida1.flush()
        salida2.write("/salir\n")
        salida2.flush()
        
        sock1.close()
        sock2.close()
        
        print("✅ Test de usuarios completado")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🍇 Test de Lista de Usuarios")
    print("=" * 40)
    test_usuarios()
