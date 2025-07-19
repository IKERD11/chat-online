import sys
import socket
import threading
import os
import time
import hashlib
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QListWidget,
    QFileDialog, QDialog, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox, 
    QScrollArea, QWidget, QListWidgetItem, QInputDialog, QStyleFactory,
    QComboBox, QGridLayout, QGroupBox, QFrame, QSizePolicy, QScrollBar
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QTextCursor, QFont, QColor, QTextCharFormat
from PyQt5.Qt import QDesktopServices

class ClienteChat(QMainWindow):
    mensaje_recibido = pyqtSignal(str)
    actualizar_usuarios = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.servidor_host = "localhost"
        self.servidor_puerto = 12345
        self.socket = None
        self.out = None
        self.in_ = None
        self.sonido_activo = True
        self.apodo = ""
        self.sala_inicial = "General"
        self.usuario = ""
        self.contrasena = ""
        self.modo_invitado = True
        self.modo_registro = False
        self.conexion_activa = False
        self.reintentos_conexion = 0
        self.max_reintentos = 3
        self.usuario_recien_registrado = False
        self.db_connection = self.conectar_db()
        self.setup_ui()
        self.mensaje_recibido.connect(self.procesar_mensaje)
        self.actualizar_usuarios.connect(self.actualizar_lista_usuarios)
        
        # Mostrar pantalla de inicio y conectar después
        self.mostrar_pantalla_inicio()

    def conectar_db(self):
        """Conectar a la base de datos MySQL"""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='admin',
                password='admin123',
                database='chat_online'
            )
            print("✅ Conexión a base de datos exitosa")
            return connection
        except Error as e:
            print(f"⚠️ No se pudo conectar a la base de datos: {str(e)}")
            print("💡 Funcionando en modo sin base de datos")
            return None

    def registrar_usuario_db(self, username, email, password):
        """Registrar usuario en la base de datos"""
        if not self.db_connection:
            print("⚠️ Sin conexión a BD - simulando registro exitoso")
            print(f"✅ Usuario simulado {username} registrado correctamente")
            return "token_simulado"
        try:
            cursor = self.db_connection.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
            if cursor.fetchone():
                print(f"⚠️ Usuario {username} ya existe en la base de datos")
                cursor.close()
                return None
            
            # Insertar nuevo usuario
            cursor.execute("""INSERT INTO usuarios (username, email, password_hash, fecha_registro, rol) 
                           VALUES (%s, %s, MD5(%s), NOW(), 'usuario')""", 
                         (username, email, password))
            self.db_connection.commit()
            cursor.close()
            print(f"✅ Usuario {username} registrado exitosamente en la base de datos")
            print(f"🎉 Credenciales preparadas para autenticación automática")
            return "registro_exitoso"
        except Error as e:
            print(f"❌ Error MySQL registrando usuario {username}: {str(e)}")
            if "Duplicate entry" in str(e):
                QMessageBox.critical(self, "Error de Registro", 
                                   f"El usuario '{username}' ya existe.\n\n" +
                                   "Intente con un nombre de usuario diferente.")
            else:
                QMessageBox.critical(self, "Error de Registro", 
                                   f"Error en la base de datos: {str(e)}")
            return None

    def iniciar_sesion_db(self, username, password):
        """Iniciar sesión verificando credenciales en la base de datos"""
        if not self.db_connection:
            print("⚠️ Sin conexión a BD - simulando inicio de sesión exitoso")
            return (1, username, f"{username}@chat.com", "usuario")
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, username, email, rol FROM usuarios WHERE username = %s AND password_hash = MD5(%s)", 
                         (username, password))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            QMessageBox.critical(self, "Error de Autenticación", f"Error al iniciar sesión: {str(e)}")
            return None

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        self.setWindowTitle("🍇 Grapes Fri Chat")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
        # Layout principal vertical
        layout_principal = QVBoxLayout(central_widget)
        layout_principal.setSpacing(0)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        # Header del chat
        self.crear_header()
        layout_principal.addWidget(self.header_widget)
        
        # Layout del contenido principal
        layout_contenido = QHBoxLayout()
        layout_contenido.setSpacing(15)
        layout_contenido.setContentsMargins(15, 10, 15, 15)
        
        # Lista de usuarios con diseño mejorado
        self.lista_usuarios = QListWidget()
        self.lista_usuarios.setFixedWidth(240)
        self.lista_usuarios.setMinimumHeight(300)
        self.lista_usuarios.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0e6ed;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                font-size: 12pt;
                min-height: 300px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 10px;
                margin: 4px 0px;
                font-size: 12pt;
                font-weight: 500;
                min-height: 20px;
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(103, 126, 234, 0.2);
            }
            QListWidget::item:hover {
                background-color: rgba(103, 126, 234, 0.15);
                border: 1px solid rgba(103, 126, 234, 0.4);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-weight: bold;
                border: 1px solid #667eea;
            }
        """)
        self.lista_usuarios.addItem("👥 Usuarios Online")
        
        # Layout del área de chat
        layout_chat = QVBoxLayout()
        
        # Área de mensajes con diseño mejorado
        self.area_mensajes = QTextEdit()
        self.area_mensajes.setReadOnly(True)
        self.area_mensajes.setFont(QFont("Segoe UI", 12))
        self.area_mensajes.setStyleSheet("""
            QTextEdit {
                border: none;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                font-size: 12pt;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background: rgba(103, 126, 234, 0.1);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(103, 126, 234, 0.5);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(103, 126, 234, 0.7);
            }
        """)
        
        layout_chat.addWidget(self.area_mensajes, 1)
        
        # Entrada de texto con diseño mejorado
        self.entrada_texto = QLineEdit()
        self.entrada_texto.setPlaceholderText("💬 Escribe un mensaje...")
        self.entrada_texto.setFont(QFont("Segoe UI", 12))
        self.entrada_texto.setFixedHeight(60)
        self.entrada_texto.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 30px;
                padding: 20px 35px;
                font-size: 13pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e0e6ed;
                min-height: 30px;
                line-height: 1.5;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background: white;
            }
            QLineEdit:hover {
                border: 2px solid #b8c5d6;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0f0f0);
            }
        """)
        self.entrada_texto.returnPressed.connect(self.enviar_texto)
        layout_chat.addWidget(self.entrada_texto)
        
        # Botones con diseño mejorado
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(15)
        layout_botones.setContentsMargins(0, 10, 0, 0)
        
        # Crear botones con estilo mejorado
        self.boton_enviar = self.crear_boton_mejorado("📤 Enviar", "#667eea", self.enviar_texto)
        self.boton_emoji = self.crear_boton_mejorado("😊 Emoji", "#FF6B6B", self.mostrar_emojis)
        self.boton_tema = self.crear_boton_mejorado("🎨 Tema", "#4ECDC4", self.cambiar_tema)
        self.boton_salas = self.crear_boton_mejorado("🏠 Salas", "#45B7D1", self.gestionar_salas)
        self.boton_reconectar = self.crear_boton_mejorado("🔄 Reconectar", "#96CEB4", self.reconectar)
        
        layout_botones.addWidget(self.boton_enviar)
        layout_botones.addWidget(self.boton_emoji)
        layout_botones.addWidget(self.boton_tema)
        layout_botones.addWidget(self.boton_salas)
        layout_botones.addWidget(self.boton_reconectar)
        layout_botones.addStretch()
        
        layout_chat.addLayout(layout_botones)
        
        # Agregar layouts al contenido principal
        layout_contenido.addLayout(layout_chat, 1)
        layout_contenido.addWidget(self.lista_usuarios)
        
        # Agregar al layout principal
        layout_principal.addLayout(layout_contenido)

    def crear_boton_mejorado(self, texto, color, funcion):
        """Crear botón con estilo mejorado y moderno"""
        boton = QPushButton(texto)
        boton.setFont(QFont("Segoe UI", 11, QFont.Bold))
        boton.setFixedHeight(45)
        boton.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {self.oscurecer_color(color, 0.8)});
                color: white;
                border: none;
                border-radius: 22px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.aclarar_color(color, 1.1)}, stop:1 {color});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.oscurecer_color(color, 0.9)}, stop:1 {self.oscurecer_color(color, 0.7)});
            }}
        """)
        boton.clicked.connect(funcion)
        return boton

    def crear_boton(self, texto, color, funcion):
        """Crear botón con estilo personalizado (mantenido para compatibilidad)"""
        return self.crear_boton_mejorado(texto, color, funcion)

    def oscurecer_color(self, color, factor=0.9):
        """Oscurecer un color hex"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb_oscuro = tuple(int(c * factor) for c in rgb)
        return '#%02x%02x%02x' % rgb_oscuro

    def aclarar_color(self, color, factor=1.1):
        """Aclarar un color hex"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb_claro = tuple(min(255, int(c * factor)) for c in rgb)
        return '#%02x%02x%02x' % rgb_claro

    def actualizar_estado_conexion(self, conectado):
        """Actualizar el indicador de estado de conexión"""
        if conectado:
            # Actualizar estado en el header
            self.estado_header.setText("🟢 Conectado")
            self.estado_header.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.9);
                    background: rgba(76, 175, 80, 0.3);
                    padding: 10px 18px;
                    border-radius: 20px;
                    border: 1px solid rgba(76, 175, 80, 0.5);
                    min-height: 25px;
                    max-width: 150px;
                }
            """)
            
            # Actualizar información del usuario si está disponible
            if hasattr(self, 'usuario') and self.usuario:
                usuario_display = self.usuario if len(self.usuario) <= 15 else self.usuario[:12] + "..."
                self.info_usuario.setText(f"👤 {usuario_display}")
        else:
            # Actualizar estado en el header
            self.estado_header.setText("🔴 Desconectado")
            self.estado_header.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.9);
                    background: rgba(244, 67, 54, 0.3);
                    padding: 10px 18px;
                    border-radius: 20px;
                    border: 1px solid rgba(244, 67, 54, 0.5);
                    min-height: 25px;
                    max-width: 150px;
                }
            """)
            
            self.info_usuario.setText("👤 Sin conectar")

    def actualizar_info_sala(self, sala):
        """Actualizar información de la sala en el header"""
        if hasattr(self, 'info_sala'):
            sala_display = sala if len(sala) <= 20 else sala[:17] + "..."
            self.info_sala.setText(f"📍 Sala: {sala_display}")

    def mostrar_pantalla_inicio(self):
        """Mostrar pantalla de inicio de sesión"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🍇 Grapes Fri Chat - Inicio")
        dialog.setFixedSize(580, 750)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #6B73FF);
                border-radius: 20px;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                border: none;
                border-radius: 12px;
                padding: 15px 20px;
                font-size: 13pt;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                min-height: 20px;
            }
            QLineEdit:focus {
                background: white;
            }
            QPushButton {
                border: none;
                border-radius: 15px;
                padding: 18px;
                font-size: 14pt;
                font-weight: bold;
                color: white;
                min-height: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background: rgba(0, 0, 0, 0.1);
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(45, 35, 45, 35)
        
        # Título principal más grande y llamativo
        titulo = QLabel("🍇 Grapes Fri Chat")
        titulo.setFont(QFont("Segoe UI", 28, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            color: white; 
            margin-bottom: 20px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
            letter-spacing: 1px;
            padding: 15px 20px;
            min-height: 60px;
        """)
        titulo.setWordWrap(True)
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Conecta con tus amigos")
        subtitulo.setFont(QFont("Segoe UI", 14, QFont.Normal))
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 30px;
            font-style: italic;
            padding: 5px 15px;
            min-height: 25px;
        """)
        layout.addWidget(subtitulo)
        
        # Campos de entrada con mejor diseño
        lbl_apodo = QLabel("👤 Apodo:")
        lbl_apodo.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_apodo.setStyleSheet("margin-top: 8px; margin-bottom: 5px; min-height: 20px;")
        layout.addWidget(lbl_apodo)
        
        self.txt_apodo = QLineEdit()
        self.txt_apodo.setPlaceholderText("Ingresa tu apodo...")
        self.txt_apodo.setFixedHeight(50)
        layout.addWidget(self.txt_apodo)
        
        lbl_sala = QLabel("🏠 Sala:")
        lbl_sala.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_sala.setStyleSheet("margin-top: 12px; margin-bottom: 5px; min-height: 20px;")
        layout.addWidget(lbl_sala)
        
        self.txt_sala = QLineEdit("General")
        self.txt_sala.setPlaceholderText("Nombre de la sala...")
        self.txt_sala.setFixedHeight(50)
        layout.addWidget(self.txt_sala)
        
        # Espaciado antes de los botones
        layout.addSpacing(20)
        
        # Botones con mejor diseño
        btn_invitado = QPushButton("👤 Entrar como Invitado")
        btn_invitado.setFixedHeight(55)
        btn_invitado.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CBE8C, stop:1 #45A084);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 13pt;
                font-weight: bold;
                margin: 5px 0px;
                min-height: 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5DD8A6, stop:1 #4CBE8C);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45A084, stop:1 #3E8B73);
            }
        """)
        btn_invitado.clicked.connect(lambda: self.entrar_como_invitado(dialog))
        layout.addWidget(btn_invitado)
        
        btn_login = QPushButton("🔐 Iniciar Sesión")
        btn_login.setFixedHeight(55)
        btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 13pt;
                font-weight: bold;
                margin: 5px 0px;
                min-height: 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #2196F3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
            }
        """)
        btn_login.clicked.connect(lambda: self.iniciar_sesion(dialog))
        layout.addWidget(btn_login)
        
        btn_registro = QPushButton("📝 Registrarse")
        btn_registro.setFixedHeight(55)
        btn_registro.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF9800, stop:1 #F57C00);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 13pt;
                font-weight: bold;
                margin: 5px 0px;
                min-height: 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFB74D, stop:1 #FF9800);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F57C00, stop:1 #EF6C00);
            }
        """)
        btn_registro.clicked.connect(lambda: self.registrarse(dialog))
        layout.addWidget(btn_registro)
        
        dialog.exec_()
    
    def entrar_como_invitado(self, dialog):
        """Entrar como usuario invitado"""
        self.apodo = self.txt_apodo.text().strip()
        self.sala_inicial = self.txt_sala.text().strip()
        
        if not self.apodo:
            QMessageBox.warning(dialog, "⚠️ Apodo requerido", "Debes ingresar un apodo.")
            return
        
        if not self.sala_inicial:
            self.sala_inicial = "General"
            
        self.modo_invitado = True
        self.modo_registro = False
        dialog.accept()
        
        # Conectar al servidor después de configurar credenciales
        self.conectar_servidor()
    
    def iniciar_sesion(self, dialog):
        """Iniciar sesión con usuario registrado"""
        usuario, ok = QInputDialog.getText(dialog, "🔐 Iniciar sesión", "Nombre de usuario:")
        if not ok or not usuario:
            return
            
        contrasena, ok = QInputDialog.getText(dialog, "🔐 Iniciar sesión", "Contraseña:", QLineEdit.Password)
        if not ok or not contrasena:
            return
            
        self.apodo = self.txt_apodo.text().strip()
        self.sala_inicial = self.txt_sala.text().strip()
        self.usuario = usuario.strip()
        self.contrasena = contrasena.strip()
        
        if not self.apodo:
            self.apodo = self.usuario
        if not self.sala_inicial:
            self.sala_inicial = "General"
            
        # Autenticar con la base de datos primero
        resultado = self.iniciar_sesion_db(self.usuario, self.contrasena)
        if resultado:
            self.modo_invitado = False
            self.modo_registro = False
            QMessageBox.information(dialog, "✅ Inicio de sesión exitoso", 
                                  f"Bienvenido {self.usuario}!\n\n" +
                                  "Conectando al servidor...")
            dialog.accept()
            
            # Conectar al servidor después de autenticación exitosa
            self.conectar_servidor()
        else:
            QMessageBox.warning(dialog, "❌ Error de autenticación", 
                              "Usuario o contraseña incorrectos.\n\n" +
                              "Verifique sus credenciales o regístrese si es un usuario nuevo.")
    
    def registrarse(self, dialog):
        """Registrar nuevo usuario"""
        usuario, ok = QInputDialog.getText(dialog, "📝 Registrarse", "Nombre de usuario (mínimo 3 caracteres):")
        if not ok or not usuario:
            return
            
        # Validar nombre de usuario
        if len(usuario.strip()) < 3:
            QMessageBox.warning(dialog, "❌ Usuario inválido", 
                              "El nombre de usuario debe tener al menos 3 caracteres.")
            return
            
        if not usuario.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(dialog, "❌ Usuario inválido", 
                              "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.")
            return
            
        contrasena, ok = QInputDialog.getText(dialog, "📝 Registrarse", "Contraseña (mínimo 4 caracteres):", QLineEdit.Password)
        if not ok or not contrasena:
            return
            
        # Validar contraseña
        if len(contrasena.strip()) < 4:
            QMessageBox.warning(dialog, "❌ Contraseña inválida", 
                              "La contraseña debe tener al menos 4 caracteres.")
            return
            
        # Confirmar contraseña
        contrasena_confirm, ok = QInputDialog.getText(dialog, "📝 Confirmar", "Confirme su contraseña:", QLineEdit.Password)
        if not ok or contrasena != contrasena_confirm:
            QMessageBox.warning(dialog, "❌ Contraseñas no coinciden", 
                              "Las contraseñas no coinciden. Intente nuevamente.")
            return
            
        self.apodo = self.txt_apodo.text().strip()
        self.sala_inicial = self.txt_sala.text().strip()
        self.usuario = usuario.strip()
        self.contrasena = contrasena.strip()
        
        if not self.apodo:
            self.apodo = self.usuario
        if not self.sala_inicial:
            self.sala_inicial = "General"
            
        # Registrar en la base de datos primero
        token = self.registrar_usuario_db(self.usuario, f"{self.usuario}@chat.com", self.contrasena)
        if token:
            # Cambiar modo para entrada directa (no como registro en el servidor)
            self.modo_invitado = False
            self.modo_registro = False  # Cambiar a False para autenticación normal
            
            # Marcar como usuario recién registrado para mensaje especial
            self.usuario_recien_registrado = True
            
            # Mostrar mensaje de éxito
            QMessageBox.information(dialog, "✅ Registro exitoso", 
                                  f"¡Bienvenido {self.usuario}!\n\n" +
                                  "Usuario registrado correctamente.\n" +
                                  "Conectando al chat...")
            dialog.accept()
            
            # Conectar al servidor con credenciales normales
            if self.conectar_servidor():
                # Mostrar bienvenida especial para usuarios nuevos
                self.mostrar_bienvenida_nuevo_usuario()
            else:
                QMessageBox.warning(self, "⚠️ Conexión fallida", 
                                  "Tu cuenta fue creada exitosamente, pero no se pudo conectar al servidor.\n\n" +
                                  "Usa el botón 'Reconectar' para intentar conectar nuevamente.")
        else:
            QMessageBox.warning(dialog, "❌ Error de registro", 
                              f"No se pudo registrar el usuario '{self.usuario}'.\n\n" +
                              "Posibles causas:\n" +
                              "• El usuario ya existe\n" +
                              "• Error en la base de datos\n" +
                              "• Caracteres no válidos\n\n" +
                              "Intente con un nombre de usuario diferente.")

    def crear_header(self):
        """Crear header del chat con título prominente"""
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(155)
        self.header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #6B73FF);
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        layout_header = QVBoxLayout(self.header_widget)
        layout_header.setContentsMargins(20, 20, 20, 18)
        layout_header.setSpacing(15)
        
        # Título principal del chat
        self.titulo_chat = QLabel("🍇 Grapes Fri Chat")
        self.titulo_chat.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.titulo_chat.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                letter-spacing: 1px;
                padding: 12px;
                margin: 0px;
                min-height: 50px;
            }
        """)
        self.titulo_chat.setAlignment(Qt.AlignCenter)
        layout_header.addWidget(self.titulo_chat)
        
        # Información de la sala y estado
        info_layout = QHBoxLayout()
        info_layout.setSpacing(15)
        
        # Usuario conectado
        self.info_usuario = QLabel("� Sin conectar")
        self.info_usuario.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_usuario.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                background: rgba(255, 255, 255, 0.1);
                padding: 10px 18px;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                min-height: 25px;
                max-width: 150px;
            }
        """)
        
        # Información de la sala
        self.info_sala = QLabel("� Sala: General")
        self.info_sala.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_sala.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                background: rgba(255, 255, 255, 0.1);
                padding: 10px 18px;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                min-height: 25px;
                max-width: 170px;
            }
        """)
        
        # Estado de conexión en el header
        self.estado_header = QLabel("� Desconectado")
        self.estado_header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.estado_header.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                background: rgba(244, 67, 54, 0.3);
                padding: 10px 18px;
                border-radius: 20px;
                border: 1px solid rgba(244, 67, 54, 0.5);
                min-height: 25px;
                max-width: 150px;
            }
        """)
        
        info_layout.addWidget(self.info_usuario)
        info_layout.addStretch()
        info_layout.addWidget(self.info_sala)
        info_layout.addStretch()
        info_layout.addWidget(self.estado_header)
        
        layout_header.addLayout(info_layout)

    def conectar_servidor(self):
        """Conectar al servidor de chat"""
        try:
            self.agregar_mensaje_chat("🔄 [SISTEMA] Intentando conectar al servidor...")
            
            # Limpiar conexión anterior
            self.limpiar_conexion()
            
            # Crear nuevo socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Configurar opciones del socket para mayor estabilidad
            self.socket.settimeout(10.0)  # Timeout de 10 segundos para conexión
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Conectar al servidor
            self.socket.connect((self.servidor_host, self.servidor_puerto))
            self.agregar_mensaje_chat("🔗 [SISTEMA] Conexión establecida, autenticando...")
            
            # Crear streams de entrada y salida con codificación UTF-8
            self.out = self.socket.makefile('w', encoding='utf-8', errors='replace', buffering=1)
            self.in_ = self.socket.makefile('r', encoding='utf-8', errors='replace', buffering=1)
            
            # Proceso de autenticación
            if self.modo_invitado:
                self.out.write(f"{self.apodo}\n")
                self.out.write("invitado\n")
                self.out.flush()
                self.agregar_mensaje_chat(f"👤 [SISTEMA] Autenticando como invitado: {self.apodo}")
            else:
                # Usuario registrado (tanto nuevos como existentes)
                self.out.write(f"{self.usuario}\n")
                self.out.write(f"{self.contrasena}\n")
                self.out.flush()
                self.agregar_mensaje_chat(f"🔐 [SISTEMA] Autenticando usuario: {self.usuario}")
            
            # Esperar respuesta de autenticación con timeout
            self.socket.settimeout(5.0)
            respuesta = self.in_.readline().strip()
            
            if respuesta != "ACCESO_OK":
                if self.modo_invitado:
                    self.agregar_mensaje_chat("❌ [SISTEMA] Error: Credenciales de invitado incorrectas")
                    QMessageBox.warning(self, "❌ Error de autenticación", 
                                      "No se pudo acceder como invitado.\n\nVerifique el apodo e intente nuevamente.")
                else:
                    self.agregar_mensaje_chat("❌ [SISTEMA] Error: Credenciales incorrectas")
                    QMessageBox.warning(self, "❌ Error de autenticación", 
                                      "Usuario o contraseña incorrectos.\n\nVerifique sus credenciales.")
                self.limpiar_conexion()
                return False
            
            # Configurar socket para operación normal (sin timeout)
            self.socket.settimeout(None)
            self.conexion_activa = True
            self.reintentos_conexion = 0
            
            # Actualizar UI
            self.actualizar_estado_conexion(True)
            self.agregar_mensaje_chat("🎉 [SISTEMA] ¡Conectado al servidor exitosamente!")
            
            # Actualizar información del usuario en el header
            usuario_display = self.apodo if self.modo_invitado else self.usuario
            self.info_usuario.setText(f"👤 {usuario_display}")
            
            # Iniciar hilo de escucha
            threading.Thread(target=self.escuchar_servidor, daemon=True).start()
            
            # Inicializar lista de usuarios
            self.actualizar_lista_usuarios([])
            
            # Unirse a sala inicial
            if self.sala_inicial and self.sala_inicial.lower() != "general":
                time.sleep(0.1)
                self.out.write(f"/sala unir {self.sala_inicial}\n")
                self.out.flush()
            
            return True
                
        except ConnectionRefusedError:
            self.agregar_mensaje_chat("❌ [SISTEMA] Error: El servidor no está disponible")
            self.actualizar_estado_conexion(False)
            QMessageBox.critical(self, "❌ Servidor no disponible", 
                               "No se pudo conectar al servidor de chat.\n\n" +
                               "Posibles causas:\n" +
                               "• El servidor no está ejecutándose\n" +
                               "• El puerto 12345 está bloqueado\n" +
                               "• Problemas de red\n\n" +
                               "Solución: Ejecute 'python ServidorChat.Py' e intente reconectar.")
            return False
        except socket.timeout:
            self.agregar_mensaje_chat("⏱️ [SISTEMA] Error: Timeout de conexión")
            self.actualizar_estado_conexion(False)
            QMessageBox.critical(self, "⏱️ Timeout de conexión", 
                               "La conexión tardó demasiado tiempo en establecerse.\n\n" +
                               "Posibles causas:\n" +
                               "• Servidor sobrecargado\n" +
                               "• Problemas de red lentos\n" +
                               "• Firewall bloqueando la conexión\n\n" +
                               "Intente reconectar en unos momentos.")
            return False
        except Exception as e:
            error_msg = str(e)
            self.agregar_mensaje_chat(f"❌ [SISTEMA] Error de conexión: {error_msg}")
            self.actualizar_estado_conexion(False)
            
            # Mensajes de error más específicos
            if "10061" in error_msg:
                QMessageBox.critical(self, "❌ Conexión rechazada", 
                                   "El servidor rechazó la conexión.\n\n" +
                                   "Asegúrese de que:\n" +
                                   "• El servidor esté ejecutándose\n" +
                                   "• No hay otro cliente usando el mismo usuario\n" +
                                   "• El puerto 12345 esté disponible")
            elif "10060" in error_msg:
                QMessageBox.critical(self, "❌ Timeout de red", 
                                   "No se pudo establecer conexión con el servidor.\n\n" +
                                   "Verifique su conexión a internet e intente nuevamente.")
            else:
                QMessageBox.critical(self, "❌ Error de conexión", 
                                   f"No se pudo conectar al servidor:\n{error_msg}\n\n" +
                                   "Use el botón 'Reconectar' para intentar nuevamente.")
            return False

    def limpiar_conexion(self):
        """Limpiar y cerrar conexión actual"""
        self.conexion_activa = False
        try:
            if self.out:
                self.out.close()
                self.out = None
        except:
            pass
        try:
            if self.in_:
                self.in_.close()
                self.in_ = None
        except:
            pass
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
        except:
            pass

    def escuchar_servidor(self):
        """Escuchar mensajes del servidor en hilo separado"""
        while self.conexion_activa:
            try:
                if not self.socket or not self.in_:
                    break
                    
                mensaje = self.in_.readline()
                if not mensaje:
                    # Servidor cerró la conexión
                    self.mensaje_recibido.emit("🔌 [SISTEMA] El servidor cerró la conexión")
                    break
                
                mensaje = mensaje.strip()
                if mensaje:
                    self.mensaje_recibido.emit(mensaje)
                    
            except ConnectionAbortedError:
                self.mensaje_recibido.emit("⚠️ [SISTEMA] Conexión perdida [WinError 10053] - El servidor interrumpió la conexión")
                break
            except ConnectionResetError:
                self.mensaje_recibido.emit("🔄 [SISTEMA] Conexión reiniciada por el servidor")
                break
            except socket.timeout:
                # Timeout normal, continuar escuchando
                continue
            except OSError as e:
                if e.errno == 10053:
                    self.mensaje_recibido.emit("⚠️ [SISTEMA] Error de socket [10053] - Conexión interrumpida por Windows")
                elif e.errno == 10054:
                    self.mensaje_recibido.emit("⚠️ [SISTEMA] Conexión forzosamente cerrada por el host remoto")
                else:
                    self.mensaje_recibido.emit(f"🔗 [SISTEMA] Error de red: {str(e)}")
                break
            except Exception as e:
                self.mensaje_recibido.emit(f"❌ [SISTEMA] Error de comunicación: {str(e)}")
                break
        
        # Limpiar conexión y actualizar UI
        self.conexion_activa = False
        self.limpiar_conexion()
        self.actualizar_estado_conexion(False)

    def verificar_conexion(self):
        """Verificar si la conexión está activa"""
        return (self.socket is not None and 
                self.out is not None and 
                self.conexion_activa)

    def procesar_mensaje(self, mensaje):
        """Procesar mensajes recibidos del servidor"""
        try:
            if mensaje.startswith("USUARIOS:"):
                # Lista de usuarios conectados
                usuarios = mensaje[len("USUARIOS:"):].split(',')
                self.actualizar_usuarios.emit(usuarios)
            elif mensaje.startswith("SALA:"):
                # Cambio de sala
                sala = mensaje[len("SALA:"):].strip()
                self.setWindowTitle(f"🍇 Grapes Fri Chat - Sala: {sala}")
                self.actualizar_info_sala(sala)
                self.agregar_mensaje_chat(f"🏠 [SISTEMA] Te uniste a la sala: {sala}")
            elif mensaje.startswith("SALAS:"):
                # Lista de salas disponibles
                self.procesar_lista_salas(mensaje[6:])
            elif mensaje.startswith("/recibir_archivo "):
                # Recepción de archivo (deshabilitado por estabilidad)
                self.agregar_mensaje_chat("📁 [SISTEMA] Recepción de archivos deshabilitada por estabilidad")
            else:
                # Mensaje normal de chat
                self.agregar_mensaje_chat(mensaje)
        except Exception as e:
            self.agregar_mensaje_chat(f"❌ [SISTEMA] Error procesando mensaje: {str(e)}")

    def agregar_mensaje_chat(self, mensaje):
        """Agregar mensaje al área de chat con formato"""
        cursor = self.area_mensajes.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Configurar formato según el tipo de mensaje
        formato = QTextCharFormat()
        
        if "[SISTEMA]" in mensaje:
            formato.setForeground(QColor(33, 150, 243))  # Azul
            formato.setFontWeight(QFont.Bold)
        elif "<<Desconectado>>" in mensaje or "❌" in mensaje or "⚠️" in mensaje:
            formato.setForeground(QColor(244, 67, 54))  # Rojo
            formato.setFontWeight(QFont.Bold)
        elif "✅" in mensaje or "🎉" in mensaje:
            formato.setForeground(QColor(76, 175, 80))  # Verde
            formato.setFontWeight(QFont.Bold)
        elif "(privado)" in mensaje.lower() or "[privado]" in mensaje.lower():
            formato.setForeground(QColor(156, 39, 176))  # Púrpura
            formato.setFontItalic(True)
        else:
            formato.setForeground(QColor(33, 33, 33))  # Negro
        
        # Agregar timestamp
        timestamp = time.strftime("[%H:%M:%S] ")
        cursor.setCharFormat(QTextCharFormat())
        cursor.insertText(timestamp)
        
        # Agregar mensaje con formato
        cursor.setCharFormat(formato)
        cursor.insertText(mensaje + "\n")
        
        # Hacer scroll automático
        self.area_mensajes.ensureCursorVisible()

    def actualizar_lista_usuarios(self, usuarios):
        """Actualizar lista de usuarios conectados"""
        self.lista_usuarios.clear()
        
        # Filtrar usuarios válidos y contar
        usuarios_validos = []
        for usuario in usuarios:
            if usuario and usuario.strip():
                usuario_limpio = usuario.strip()
                # Evitar duplicados y no incluirse a sí mismo en la lista de "otros"
                if usuario_limpio not in usuarios_validos and usuario_limpio != self.apodo:
                    usuarios_validos.append(usuario_limpio)
        
        # Encabezado con contador
        total_usuarios = len(usuarios_validos) + 1  # +1 por el usuario actual
        self.lista_usuarios.addItem(f"👥 Usuarios Online ({total_usuarios})")
        
        # Agregar el usuario actual primero
        self.lista_usuarios.addItem(f"🟢 {self.apodo} (tú)")
        
        # Agregar otros usuarios conectados
        if usuarios_validos:
            for usuario in sorted(usuarios_validos):  # Ordenar alfabéticamente
                self.lista_usuarios.addItem(f"👤 {usuario}")
        else:
            # Si no hay otros usuarios, mostrar mensaje informativo
            self.lista_usuarios.addItem("😴 No hay otros usuarios")
        
        print(f"� Usuarios actualizados: {usuarios_validos}")

    def enviar_texto(self):
        """Enviar mensaje de texto al servidor"""
        texto = self.entrada_texto.text().strip()
        if not texto:
            return
            
        # Verificar conexión
        if not self.verificar_conexion():
            self.agregar_mensaje_chat("❌ [SISTEMA] Sin conexión al servidor. Use el botón Reconectar.")
            return
            
        try:
            # Asegurar codificación segura
            texto_seguro = texto.encode('utf-8', errors='replace').decode('utf-8')
        except:
            # Fallback a ASCII si hay problemas
            texto_seguro = ''.join(c for c in texto if ord(c) < 128)
            
        # Procesar comandos especiales
        if texto_seguro.startswith("/sala "):
            nombre_sala = texto_seguro[6:].strip()
            if nombre_sala:
                try:
                    self.out.write(f"/sala unir {nombre_sala}\n")
                    self.out.flush()
                    self.entrada_texto.clear()
                    return
                except Exception as e:
                    self.agregar_mensaje_chat(f"❌ [SISTEMA] Error enviando comando de sala: {str(e)}")
                    return
                
        elif texto_seguro.startswith("/crear "):
            nombre_sala = texto_seguro[7:].strip()
            if nombre_sala:
                try:
                    self.out.write(f"/sala crear {nombre_sala}\n")
                    self.out.flush()
                    self.entrada_texto.clear()
                    return
                except Exception as e:
                    self.agregar_mensaje_chat(f"❌ [SISTEMA] Error creando sala: {str(e)}")
                    return
        
        # Enviar mensaje normal
        try:
            self.out.write(f"{texto_seguro}\n")
            self.out.flush()
            self.entrada_texto.clear()
        except (ConnectionAbortedError, ConnectionResetError, OSError) as e:
            self.agregar_mensaje_chat(f"❌ [SISTEMA] Error de conexión [WinError 10053]: {str(e)}")
            self.agregar_mensaje_chat("🔄 [SISTEMA] Use el botón Reconectar para reestablecer la conexión")
            self.conexion_activa = False
            self.actualizar_estado_conexion(False)
        except Exception as e:
            self.agregar_mensaje_chat(f"❌ [SISTEMA] Error enviando mensaje: {str(e)}")
            self.conexion_activa = False
            self.actualizar_estado_conexion(False)
            self.actualizar_estado_conexion(False)
        except Exception as e:
            self.agregar_mensaje_chat(f"❌ [SISTEMA] Error enviando mensaje: {str(e)}")

    def mostrar_emojis(self):
        """Mostrar selector de emojis"""
        emojis = [
            "😊", "😂", "❤️", "👍", "😢", "🔥", "🎉", "🤔", 
            "👋", "🎂", "🍕", "☕", "🌟", "💻", "🎮", "🎵"
        ]
        emoji, ok = QInputDialog.getItem(
            self, "😊 Seleccionar Emoji", "Emoji:", emojis, 0, False
        )
        if ok and emoji:
            texto_actual = self.entrada_texto.text()
            self.entrada_texto.setText(texto_actual + emoji)
            self.entrada_texto.setFocus()

    def gestionar_salas(self):
        """Gestionar salas de chat"""
        try:
            if not self.verificar_conexion():
                QMessageBox.warning(self, "⚠️ Sin conexión", "No hay conexión al servidor")
                return
                
            # Solicitar lista de salas al servidor
            self.out.write("/salas\n")
            self.out.flush()
            
            # Dar tiempo para recibir respuesta
            time.sleep(0.2)
            
            # Usar salas disponibles o valores por defecto
            salas = getattr(self, 'salas_disponibles', ["General", "Desarrollo", "Soporte", "Offtopic"])
            
            # Crear diálogo de salas
            dialog = QDialog(self)
            dialog.setWindowTitle("🏠 Salas disponibles")
            dialog.setFixedSize(350, 400)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #f0f0f0;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Título
            titulo = QLabel("🏠 Salas disponibles:")
            titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
            titulo.setAlignment(Qt.AlignCenter)
            layout.addWidget(titulo)
            
            # Lista de salas
            lista_salas = QListWidget()
            lista_salas.setStyleSheet("""
                QListWidget {
                    border: 2px solid #ddd;
                    border-radius: 10px;
                    padding: 5px;
                    background-color: white;
                }
                QListWidget::item {
                    padding: 8px;
                    border-radius: 5px;
                    margin: 2px;
                }
                QListWidget::item:selected {
                    background-color: #4CBE8C;
                    color: white;
                }
            """)
            
            for sala in salas:
                lista_salas.addItem(f"🏠 {sala}")
            layout.addWidget(lista_salas)
            
            # Botones
            btn_unirse = self.crear_boton("🚪 Unirse", "#4CBE8C", lambda: self.unirse_a_sala(
                dialog, 
                lista_salas.currentItem().text().replace("🏠 ", "").split(" (")[0] if lista_salas.currentItem() else ""
            ))
            layout.addWidget(btn_unirse)
            
            btn_crear = self.crear_boton("➕ Crear nueva sala", "#2196F3", lambda: self.crear_nueva_sala(dialog))
            layout.addWidget(btn_crear)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error gestionando salas: {str(e)}")

    def unirse_a_sala(self, dialog, sala):
        """Unirse a una sala específica"""
        if sala:
            try:
                if not self.verificar_conexion():
                    QMessageBox.warning(dialog, "⚠️ Sin conexión", "No hay conexión al servidor")
                    return
                    
                self.out.write(f"/sala unir {sala}\n")
                self.out.flush()
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "❌ Error", f"Error uniéndose a la sala: {str(e)}")

    def crear_nueva_sala(self, dialog):
        """Crear una nueva sala"""
        nombre, ok = QInputDialog.getText(dialog, "➕ Crear sala", "🏠 Nombre de la nueva sala:")
        if ok and nombre.strip():
            try:
                if not self.verificar_conexion():
                    QMessageBox.warning(dialog, "⚠️ Sin conexión", "No hay conexión al servidor")
                    return
                    
                self.out.write(f"/sala crear {nombre.strip()}\n")
                self.out.flush()
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "❌ Error", f"Error creando sala: {str(e)}")

    def reconectar(self):
        """Reconectar al servidor"""
        try:
            self.reintentos_conexion += 1
            self.agregar_mensaje_chat(f"🔄 [SISTEMA] Intento de reconexión #{self.reintentos_conexion}...")
            
            # Limpiar conexión actual
            self.limpiar_conexion()
            
            # Actualizar estado
            self.actualizar_estado_conexion(False)
            
            # Verificar si tenemos credenciales para reconectar
            if not self.apodo and not self.usuario:
                QMessageBox.warning(self, "⚠️ Sin credenciales", 
                                  "No hay credenciales guardadas para reconectar.\n\n" +
                                  "Use el menú de opciones para configurar nuevas credenciales.")
                return
            
            # Intentar reconectar
            if self.conectar_servidor():
                self.agregar_mensaje_chat("✅ [SISTEMA] ¡Reconectado al servidor exitosamente!")
                self.reintentos_conexion = 0
                QMessageBox.information(self, "✅ Éxito", 
                                      "Reconexión exitosa.\n\n" +
                                      "Ya puede enviar mensajes nuevamente.")
            else:
                self.agregar_mensaje_chat(f"❌ [SISTEMA] Falló intento de reconexión #{self.reintentos_conexion}")
                
                if self.reintentos_conexion >= self.max_reintentos:
                    QMessageBox.critical(self, "❌ Reconexión fallida", 
                                       f"No se pudo reconectar después de {self.max_reintentos} intentos.\n\n" +
                                       "Posibles soluciones:\n" +
                                       "• Verificar que el servidor esté ejecutándose\n" +
                                       "• Comprobar la conexión a internet\n" +
                                       "• Reiniciar la aplicación\n" +
                                       "• Contactar al administrador del servidor")
                    self.reintentos_conexion = 0
                else:
                    QMessageBox.warning(self, "⚠️ Reconexión fallida", 
                                      f"Intento {self.reintentos_conexion} de {self.max_reintentos} falló.\n\n" +
                                      "Puede intentar reconectar nuevamente o esperar unos momentos.")
                
        except Exception as e:
            self.agregar_mensaje_chat(f"❌ [SISTEMA] Error crítico al reconectar: {str(e)}")
            QMessageBox.critical(self, "❌ Error crítico", 
                               f"Error inesperado durante la reconexión:\n{str(e)}\n\n" +
                               "Considere reiniciar la aplicación.")

    def cambiar_tema(self):
        """Cambiar tema de la aplicación"""
        temas = ["🌞 Claro", "🌙 Oscuro", "🌫️ Gris", "🌺 Rosado", "🟢 Verde"]
        tema, ok = QInputDialog.getItem(
            self, "🎨 Cambiar Tema", "Seleccione un tema:", temas, 0, False
        )
        if not ok or not tema:
            return
            
        if "Claro" in tema:
            self.aplicar_tema_claro()
        elif "Oscuro" in tema:
            self.aplicar_tema_oscuro()
        elif "Gris" in tema:
            self.aplicar_tema_gris()
        elif "Rosado" in tema:
            self.aplicar_tema_rosado()
        elif "Verde" in tema:
            self.aplicar_tema_verde()
            
        # Mostrar mensaje de confirmación
        self.agregar_mensaje_chat(f"🎨 [SISTEMA] Tema cambiado a: {tema}")
        
        # Actualizar botones según el tema
        if "Claro" in tema:
            self.actualizar_botones_tema("light", "", "white")
        elif "Oscuro" in tema:
            self.actualizar_botones_tema("dark", "", "white")
        elif "Gris" in tema:
            self.actualizar_botones_tema("#8e9aaf", "", "white")
        elif "Rosado" in tema:
            self.actualizar_botones_tema("#e91e63", "", "white")
        elif "Verde" in tema:
            self.actualizar_botones_tema("#4caf50", "", "white")

    def aplicar_tema_claro(self):
        """Aplicar tema claro - diseño original optimizado"""
        # Resetear header al estilo original
        self.header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #6B73FF);
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        # Widget central
        self.centralWidget().setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
        # Área de mensajes
        self.area_mensajes.setStyleSheet("""
            QTextEdit {
                border: none;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                font-size: 12pt;
                line-height: 1.4;
                color: #333333;
            }
            QScrollBar:vertical {
                background: rgba(103, 126, 234, 0.1);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(103, 126, 234, 0.5);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(103, 126, 234, 0.7);
            }
        """)
        
        # Campo de entrada
        self.entrada_texto.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 30px;
                padding: 20px 35px;
                font-size: 13pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e0e6ed;
                min-height: 30px;
                line-height: 1.5;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background: white;
            }
            QLineEdit:hover {
                border: 2px solid #b8c5d6;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0f0f0);
            }
        """)
        
        # Lista de usuarios
        self.lista_usuarios.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0e6ed;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                font-size: 12pt;
                min-height: 300px;
                color: #333333;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 10px;
                margin: 4px 0px;
                font-size: 12pt;
                font-weight: 500;
                min-height: 20px;
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(103, 126, 234, 0.2);
                color: #333333;
            }
            QListWidget::item:hover {
                background-color: rgba(103, 126, 234, 0.15);
                border: 1px solid rgba(103, 126, 234, 0.4);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-weight: bold;
                border: 1px solid #667eea;
            }
        """)
        
        # Actualizar botones al tema claro
        self.actualizar_botones_tema("light", "")

    def aplicar_tema_oscuro(self):
        """Aplicar tema oscuro completo"""
        # Header oscuro
        self.header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #2d2d2d, stop:1 #404040);
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        # Widget central
        self.centralWidget().setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d2d2d, stop:1 #1a1a1a);
            }
        """)
        
        # Área de mensajes
        self.area_mensajes.setStyleSheet("""
            QTextEdit {
                border: 2px solid #555555;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #0d1117);
                font-size: 12pt;
                line-height: 1.4;
                color: #ffffff;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        """)
        
        # Campo de entrada
        self.entrada_texto.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 30px;
                padding: 20px 35px;
                font-size: 13pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #404040, stop:1 #2d2d2d);
                border: 2px solid #555555;
                min-height: 30px;
                line-height: 1.5;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #6272a4;
                background: #484848;
            }
            QLineEdit:hover {
                border: 2px solid #666666;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #484848, stop:1 #3a3a3a);
            }
        """)
        
        # Lista de usuarios
        self.lista_usuarios.setStyleSheet("""
            QListWidget {
                border: 2px solid #555555;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #0d1117);
                font-size: 12pt;
                min-height: 300px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 10px;
                margin: 4px 0px;
                font-size: 12pt;
                font-weight: 500;
                min-height: 20px;
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6272a4, stop:1 #50fa7b);
                color: white;
                font-weight: bold;
                border: 1px solid #6272a4;
            }
        """)
        
        # Actualizar botones al tema oscuro
        self.actualizar_botones_tema("dark", "")

    def aplicar_tema_gris(self):
        """Aplicar tema gris elegante"""
        # Header gris
        self.header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8e9aaf, stop:0.5 #a0a0a0, stop:1 #b8b8b8);
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        # Widget central
        self.centralWidget().setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8e8e8, stop:1 #d3d3d3);
            }
        """)
        
        # Área de mensajes
        self.area_mensajes.setStyleSheet("""
            QTextEdit {
                border: 2px solid #a0a0a0;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f8f8, stop:1 #e8e8e8);
                font-size: 12pt;
                line-height: 1.4;
                color: #2c2c2c;
            }
            QScrollBar:vertical {
                background: rgba(160, 160, 160, 0.3);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(160, 160, 160, 0.6);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(160, 160, 160, 0.8);
            }
        """)
        
        # Campo de entrada
        self.entrada_texto.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 30px;
                padding: 20px 35px;
                font-size: 13pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0f0f0);
                border: 2px solid #a0a0a0;
                min-height: 30px;
                line-height: 1.5;
                color: #2c2c2c;
            }
            QLineEdit:focus {
                border: 2px solid #8e9aaf;
                background: white;
            }
            QLineEdit:hover {
                border: 2px solid #888888;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #e8e8e8);
            }
        """)
        
        # Lista de usuarios
        self.lista_usuarios.setStyleSheet("""
            QListWidget {
                border: 2px solid #a0a0a0;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f8f8, stop:1 #e8e8e8);
                font-size: 12pt;
                min-height: 300px;
                color: #2c2c2c;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 10px;
                margin: 4px 0px;
                font-size: 12pt;
                font-weight: 500;
                min-height: 20px;
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(160, 160, 160, 0.5);
                color: #2c2c2c;
            }
            QListWidget::item:hover {
                background-color: rgba(160, 160, 160, 0.3);
                border: 1px solid rgba(160, 160, 160, 0.7);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8e9aaf, stop:1 #a0a0a0);
                color: white;
                font-weight: bold;
                border: 1px solid #8e9aaf;
            }
        """)
        
        # Actualizar botones al tema gris
        self.actualizar_botones_tema("light", "")

    def aplicar_tema_rosado(self):
        """Aplicar tema rosado suave"""
        # Header rosado
        self.header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff9a9e, stop:0.5 #fecfef, stop:1 #fecfef);
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        # Widget central
        self.centralWidget().setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffeef0, stop:1 #fce4ec);
            }
        """)
        
        # Área de mensajes
        self.area_mensajes.setStyleSheet("""
            QTextEdit {
                border: 2px solid #f8bbd9;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #ffeef0);
                font-size: 12pt;
                line-height: 1.4;
                color: #4a148c;
            }
            QScrollBar:vertical {
                background: rgba(248, 187, 217, 0.3);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(248, 187, 217, 0.6);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(248, 187, 217, 0.8);
            }
        """)
        
        # Campo de entrada
        self.entrada_texto.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 30px;
                padding: 20px 35px;
                font-size: 13pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #ffeef0);
                border: 2px solid #f8bbd9;
                min-height: 30px;
                line-height: 1.5;
                color: #4a148c;
            }
            QLineEdit:focus {
                border: 2px solid #e91e63;
                background: white;
            }
            QLineEdit:hover {
                border: 2px solid #f06292;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #fce4ec);
            }
        """)
        
        # Lista de usuarios
        self.lista_usuarios.setStyleSheet("""
            QListWidget {
                border: 2px solid #f8bbd9;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #ffeef0);
                font-size: 12pt;
                min-height: 300px;
                color: #4a148c;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 10px;
                margin: 4px 0px;
                font-size: 12pt;
                font-weight: 500;
                min-height: 20px;
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(248, 187, 217, 0.5);
                color: #4a148c;
            }
            QListWidget::item:hover {
                background-color: rgba(248, 187, 217, 0.3);
                border: 1px solid rgba(248, 187, 217, 0.7);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e91e63, stop:1 #f8bbd9);
                color: white;
                font-weight: bold;
                border: 1px solid #e91e63;
            }
        """)
        
        # Actualizar botones al tema rosado
        self.actualizar_botones_tema("light", "")

    def aplicar_tema_verde(self):
        """Aplicar tema verde naturaleza"""
        # Header verde
        self.header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4caf50, stop:0.5 #66bb6a, stop:1 #81c784);
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        # Widget central
        self.centralWidget().setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f1f8e9, stop:1 #e8f5e8);
            }
        """)
        
        # Área de mensajes
        self.area_mensajes.setStyleSheet("""
            QTextEdit {
                border: 2px solid #a5d6a7;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f8e9);
                font-size: 12pt;
                line-height: 1.4;
                color: #1b5e20;
            }
            QScrollBar:vertical {
                background: rgba(165, 214, 167, 0.3);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(165, 214, 167, 0.6);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(165, 214, 167, 0.8);
            }
        """)
        
        # Campo de entrada
        self.entrada_texto.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 30px;
                padding: 20px 35px;
                font-size: 13pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f8e9);
                border: 2px solid #a5d6a7;
                min-height: 30px;
                line-height: 1.5;
                color: #1b5e20;
            }
            QLineEdit:focus {
                border: 2px solid #4caf50;
                background: white;
            }
            QLineEdit:hover {
                border: 2px solid #66bb6a;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #e8f5e8);
            }
        """)
        
        # Lista de usuarios
        self.lista_usuarios.setStyleSheet("""
            QListWidget {
                border: 2px solid #a5d6a7;
                border-radius: 15px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f8e9);
                font-size: 12pt;
                min-height: 300px;
                color: #1b5e20;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 10px;
                margin: 4px 0px;
                font-size:  12pt;
                font-weight: 500;
                min-height: 20px;
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(165, 214, 167, 0.5);
                color: #1b5e20;
            }
            QListWidget::item:hover {
                background-color: rgba(165, 214, 167, 0.3);
                border: 1px solid rgba(165, 214, 167, 0.7);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4caf50, stop:1 #a5d6a7);
                color: white;
                font-weight: bold;
                border: 1px solid #4caf50;
            }
        """)
        
        # Actualizar botones al tema verde
        self.actualizar_botones_tema("light", "")

    def actualizar_botones_tema(self, color_primario, color_secundario, color_texto="white"):
        """Actualizar estilos de botones según el tema"""
        try:
            botones = [
                (self.boton_enviar, "#667eea"),
                (self.boton_emoji, "#FF6B6B"), 
                (self.boton_tema, "#4ECDC4"),
                (self.boton_salas, "#45B7D1"),
                (self.boton_reconectar, "#96CEB4")
            ]
            
            for boton, color_original in botones:
                # Adaptar color del botón al tema
                if color_primario == "dark":
                    color_adaptado = self.oscurecer_color(color_original, 0.7)
                elif color_primario == "light":
                    color_adaptado = color_original
                else:
                    color_adaptado = color_primario
                    
                boton.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {color_adaptado}, stop:1 {self.oscurecer_color(color_adaptado, 0.8)});
                        color: {color_texto};
                        border: none;
                        border-radius: 22px;
                        padding: 12px 25px;
                        font-weight: bold;
                        font-size: 11pt;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {self.aclarar_color(color_adaptado, 1.1)}, stop:1 {color_adaptado});
                    }}
                    QPushButton:pressed {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {self.oscurecer_color(color_adaptado, 0.9)}, stop:1 {self.oscurecer_color(color_adaptado, 0.7)});
                    }}
                """)
        except Exception as e:
            print(f"Error actualizando botones: {e}")

    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        try:
            # Notificar al servidor que el usuario se desconecta
            if self.verificar_conexion():
                self.out.write("/salir\n")
                self.out.flush()
                time.sleep(0.1)  # Dar tiempo para enviar el mensaje
            
            # Limpiar conexión
            self.limpiar_conexion()
            
            # Cerrar conexión de base de datos
            if self.db_connection:
                self.db_connection.close()
                
        except Exception as e:
            print(f"Error al cerrar: {e}")
        finally:
            event.accept()

    def procesar_lista_salas(self, lista_salas):
        """Procesar lista de salas recibida del servidor"""
        try:
            self.salas_disponibles = []
            if lista_salas.strip():
                salas_info = lista_salas.split(',')
                for sala_info in salas_info:
                    if '|' in sala_info:
                        nombre, usuarios = sala_info.split('|')
                        self.salas_disponibles.append(f"{nombre} ({usuarios} usuarios)")
                    else:
                        self.salas_disponibles.append(sala_info.strip())
        except Exception as e:
            print(f"Error procesando lista de salas: {e}")

    def mostrar_bienvenida_nuevo_usuario(self):
        """Mostrar mensaje de bienvenida para usuarios recién registrados"""
        try:
            tiempo_bienvenida = time.strftime("%H:%M:%S")
            
            self.agregar_mensaje_chat("=" * 60)
            self.agregar_mensaje_chat(f"🎉 [BIENVENIDA] ¡Hola {self.usuario}! Tu cuenta ha sido creada exitosamente")
            self.agregar_mensaje_chat(f"📅 [BIENVENIDA] Registro completado el {time.strftime('%d/%m/%Y')} a las {tiempo_bienvenida}")
            self.agregar_mensaje_chat("🎯 [BIENVENIDA] ¡Ya puedes comenzar a chatear con otros usuarios!")
            self.agregar_mensaje_chat("💡 [BIENVENIDA] Comandos útiles:")
            self.agregar_mensaje_chat("   • /sala NombreSala - Cambiar de sala")
            self.agregar_mensaje_chat("   • /crear NombreSala - Crear nueva sala")
            self.agregar_mensaje_chat("   • 😊 Usa el botón Emoji para agregar emociones")
            self.agregar_mensaje_chat("=" * 60)
            
        except Exception as e:
            print(f"Error mostrando bienvenida: {e}")


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Grapes Fri Chat")
        app.setApplicationVersion("2.1")
        
        # Configurar estilo de aplicación
        app.setStyle('Fusion')
        
        cliente = ClienteChat()
        cliente.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        QMessageBox.critical(None, "❌ Error Fatal", f"No se pudo iniciar la aplicación:\n{str(e)}")
