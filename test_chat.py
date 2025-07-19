#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    print("Importando PyQt5...")
    from PyQt5.QtWidgets import QApplication
    print("✅ PyQt5 importado correctamente")
    
    print("Importando ChatCliente...")
    from ChatCliente import ClienteChat
    print("✅ ChatCliente importado correctamente")
    
    print("Creando aplicación...")
    import sys
    app = QApplication(sys.argv)
    print("✅ QApplication creada correctamente")
    
    print("Creando cliente...")
    cliente = ClienteChat()
    print("✅ ClienteChat creado correctamente")
    
    print("🎉 ¡Todas las importaciones y creaciones fueron exitosas!")
    print("El programa debería funcionar correctamente.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
