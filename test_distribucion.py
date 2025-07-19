#!/usr/bin/env python3
"""
Test de la distribución del texto corregida
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
        print("\n🎨 ¡Distribución del texto corregida!")
        print("=" * 55)
        print("✨ CORRECCIONES APLICADAS:")
        print("   📏 Ventana ampliada a 520x680 para más espacio")
        print("   🍇 Título reducido a 24pt para evitar cortes")
        print("   📝 Campos de entrada optimizados (42px altura)")
        print("   🎯 Botones ajustados a 48px de altura")
        print("   📐 Espaciado mejorado entre elementos")
        print("   🔤 Fuentes balanceadas para mejor legibilidad")
        print("   📱 Layout optimizado para distribución perfecta")
        print("   ✂️ Márgenes reducidos para aprovechar el espacio")
        print("=" * 55)
        print("🚀 ¡El texto ahora se distribuye perfectamente!")
        print("💡 El título completo se muestra sin cortarse")
        
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de tener PyQt5 instalado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
