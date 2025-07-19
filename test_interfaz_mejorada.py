#!/usr/bin/env python3
"""
Test mejorado de la interfaz del chat con mejoras de diseño
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
        print("\n🎨 ¡Interfaz mejorada cargada!")
        print("=" * 50)
        print("✨ MEJORAS APLICADAS:")
        print("   🍇 Título del chat más visible y prominente")
        print("   📏 Ventana de inicio más ancha (500x650)")
        print("   🎯 Botones con gradientes y efectos hover")
        print("   📝 Campos de entrada más grandes y cómodos")
        print("   🎨 Espaciado mejorado entre elementos")
        print("   💫 Efectos de sombra y transiciones suaves")
        print("   🏠 Header con información en tiempo real")
        print("   👥 Lista de usuarios rediseñada")
        print("=" * 50)
        print("🚀 ¡Listo! Prueba la nueva interfaz")
        
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de tener PyQt5 instalado: pip install PyQt5")
        print("💡 O ejecuta: python -m pip install PyQt5")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
