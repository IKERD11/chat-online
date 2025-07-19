#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple para diagnosticar problemas de conexión
"""

import socket
import time

def test_simple():
    """Prueba muy simple de conexión"""
    try:
        print("🧪 Test simple de conexión...")
        
        # Crear socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # Timeout más largo
        
        # Conectar
        print("🔗 Conectando...")
        sock.connect(("localhost", 12345))
        
        # Crear streams
        print("📝 Creando streams...")
        salida = sock.makefile('w', encoding='utf-8', buffering=1)
        entrada = sock.makefile('r', encoding='utf-8', buffering=1)
        
        # Autenticación
        print("🔐 Enviando credenciales...")
        salida.write("TestUser\n")
        salida.flush()
        time.sleep(0.1)
        
        salida.write("invitado\n")
        salida.flush()
        time.sleep(0.1)
        
        # Leer respuesta
        print("📥 Leyendo respuesta...")
        respuesta = entrada.readline().strip()
        print(f"📨 Respuesta: '{respuesta}'")
        
        if respuesta == "ACCESO_OK":
            print("✅ Autenticación exitosa")
            
            # Mensaje simple
            print("💬 Enviando mensaje simple...")
            salida.write("Hola mundo\n")
            salida.flush()
            time.sleep(1)
            
            print("✅ Mensaje enviado exitosamente")
            
            # NO probar comandos por ahora, solo salir
            print("👋 Saliendo...")
            salida.write("/salir\n")
            salida.flush()
            time.sleep(0.5)
            
        else:
            print(f"❌ Error de autenticación: '{respuesta}'")
        
        # Cerrar
        print("🔌 Cerrando conexión...")
        salida.close()
        entrada.close()
        sock.close()
        
        print("✅ Test completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🍇 Grapes Fri Chat - Test Simple")
    print("=" * 40)
    test_simple()
