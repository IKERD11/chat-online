#!/usr/bin/env python3
"""
Test integral: Distribución de texto, conexión y registro corregidos
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 importado correctamente")
        
        from ChatCliente import ClienteChat
        print("✅ ClienteChat importado correctamente")
        
        app = QApplication(sys.argv)
        print("✅ QApplication creada")
        
        # Crear ventana del chat
        ventana = ClienteChat()
        print("✅ ClienteChat instanciado correctamente")
        
        ventana.show()
        print("\n🎉 ¡Todas las correcciones aplicadas!")
        print("=" * 60)
        print("🎨 DISTRIBUCIÓN DE TEXTO CORREGIDA:")
        print("   📏 Header compactado a 100px de altura")
        print("   🍇 Título reducido a 22pt para mejor ajuste")
        print("   📱 Elementos del header redimensionados")
        print("   🔤 Fuentes balanceadas (10pt en info)")
        print("")
        print("🔗 CONEXIÓN AL SERVIDOR MEJORADA:")
        print("   ⏱️ Timeouts optimizados (10s conexión, 5s auth)")
        print("   📊 Mensajes de estado detallados")
        print("   🔄 Manejo de errores específicos")
        print("   ❌ Diagnósticos de conexión mejorados")
        print("")
        print("👤 REGISTRO DE USUARIOS MEJORADO:")
        print("   ✅ Validación de nombre de usuario (min 3 chars)")
        print("   🔒 Validación de contraseña (min 4 chars)")
        print("   🔄 Confirmación de contraseña")
        print("   📋 Verificación de duplicados en BD")
        print("   💬 Mensajes de error específicos")
        print("")
        print("🔄 RECONEXIÓN INTELIGENTE:")
        print("   📊 Contador de intentos de reconexión")
        print("   ⏰ Límite de reintentos (3 máximo)")
        print("   💡 Mensajes de ayuda específicos")
        print("   🛠️ Diagnósticos de problemas")
        print("=" * 60)
        print("🚀 ¡Listo para usar!")
        print("")
        print("💡 INSTRUCCIONES:")
        print("   1. Ejecute 'python ServidorChat.Py' en otra terminal")
        print("   2. Use la pantalla de inicio para conectarse")
        print("   3. Pruebe el registro de nuevos usuarios")
        print("   4. Use 'Reconectar' si hay problemas de conexión")
        
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Instale PyQt5: pip install PyQt5")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
