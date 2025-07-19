# 🚀 Chat Online - Aplicación de Chat en Tiempo Real

![Chat Online](https://img.shields.io/badge/Chat-Online-brightgreen) 
![Python](https://img.shields.io/badge/Python-3.11-blue)
![WebSocket](https://img.shields.io/badge/WebSocket-Real%20Time-orange)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue)

Una aplicación de chat moderna y completa con cliente desktop (PyQt5) y web (HTML/JS), desarrollada con Python y WebSockets para comunicación en tiempo real.

## ✨ **Características Principales**

### 🎨 **Interfaz Moderna**
- **5 temas personalizables**: Claro, Oscuro, Gris, Rosado, Verde
- **Diseño responsive** para web y desktop
- **Gradientes modernos** y animaciones suaves

### 👥 **Sistema de Usuarios**
- **Registro e inicio de sesión** automático
- **Modo invitado** para acceso rápido
- **Autenticación segura** con MySQL
- **Reconexión automática**

### 💬 **Chat en Tiempo Real**
- **WebSocket** para mensajes instantáneos
- **Salas de chat** múltiples
- **Lista de usuarios** conectados
- **Historial de mensajes**

### 🛠️ **Tecnologías**
- **Backend**: Python 3.11, WebSockets, MySQL
- **Frontend Web**: HTML5, CSS3, JavaScript vanilla
- **Cliente Desktop**: PyQt5
- **Base de Datos**: MySQL 8.0
- **Deployment**: GitHub Pages + Railway/Render

## 🖼️ **Capturas de Pantalla**

### Interfaz Web
![Web Interface](https://via.placeholder.com/800x400/667eea/ffffff?text=Chat+Web+Interface)

### Cliente Desktop
![Desktop Client](https://via.placeholder.com/800x400/764ba2/ffffff?text=PyQt5+Desktop+Client)

## 🚀 **Demo en Vivo**

- **🌐 Versión Web**: [https://tu-usuario.github.io/chat-online](https://tu-usuario.github.io/chat-online)
- **📱 Funciona en móviles** y tablets
- **⚡ Tiempo real** con WebSockets

## 📦 **Instalación Local**

### Requisitos
- Python 3.11+
- MySQL 8.0+
- Git

### Pasos Rápidos
```bash
# 1. Clonar repositorio
git clone https://github.com/TU_USUARIO/chat-online.git
cd chat-online

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar MySQL
mysql -u root -e "CREATE DATABASE chat_online;"
mysql -u root chat_online < init.sql

# 4. Iniciar servidor WebSocket
python servidor_websocket.py

# 5. Abrir cliente
# Web: Abrir web/index.html en navegador
# Desktop: python ChatCliente.py
```

## ☁️ **Desarrollo en GitHub Codespaces**

¡Desarrolla directamente en el navegador con GitHub Codespaces!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/TU_USUARIO/chat-online)

### Auto-configuración incluida:
- ✅ Python 3.11 preinstalado
- ✅ MySQL 8.0 configurado automáticamente
- ✅ Base de datos inicializada
- ✅ Dependencias instaladas
- ✅ VS Code con extensiones

## 🌐 **Deployment**

### GitHub Pages (Frontend)
El frontend se despliega automáticamente a GitHub Pages mediante GitHub Actions.

### Backend Options
- **Railway.app**: $5/mes - Recomendado
- **Render.com**: Plan gratuito disponible
- **Fly.io**: Plan gratuito generoso

## 🎯 **Uso**

### Versión Web
1. Visita la [demo en vivo](https://tu-usuario.github.io/chat-online)
2. Regístrate o usa modo invitado
3. ¡Empieza a chatear!

### Versión Desktop
```bash
python ChatCliente.py
```

## 🔧 **Configuración**

### Variables de Entorno
```bash
DB_HOST=localhost
DB_USER=admin
DB_PASSWORD=tu_password
DB_NAME=chat_online
WS_PORT=8765
```

### Personalización de Temas
Los temas se pueden personalizar editando los archivos CSS en:
- Web: `web/index.html` (estilos embebidos)
- Desktop: Métodos `aplicar_tema_*()` en `ChatCliente.py`

## 🤝 **Contribuir**

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 **Roadmap**

- [ ] **Mensajes privados** entre usuarios
- [ ] **Envío de archivos** e imágenes
- [ ] **Notificaciones push** en web
- [ ] **App móvil** con React Native
- [ ] **Moderación automática** de contenido
- [ ] **Integración con bots** de IA

## 📄 **Licencia**

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## 📧 **Contacto**

**Tu Nombre** - tu.email@ejemplo.com

**Link del Proyecto**: [https://github.com/TU_USUARIO/chat-online](https://github.com/TU_USUARIO/chat-online)

---

⭐ **¡Dale una estrella si te gustó el proyecto!** ⭐
