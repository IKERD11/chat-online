# Script para configurar el proyecto en GitHub Codespaces
#!/bin/bash

echo "🚀 Configurando Chat Online en GitHub Codespaces..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar Python
log "Verificando Python..."
python3 --version || { error "Python no encontrado"; exit 1; }

# Instalar dependencias
log "Instalando dependencias Python..."
pip install -r requirements.txt || { error "Error instalando dependencias"; exit 1; }

# Configurar MySQL
log "Configurando MySQL..."
sudo service mysql start

# Crear base de datos
log "Creando base de datos..."
mysql -u root -e "CREATE DATABASE IF NOT EXISTS chat_online;" || warn "BD ya existe o error creando"

# Crear usuario
log "Creando usuario de base de datos..."
mysql -u root -e "CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'admin123';" || warn "Usuario ya existe"
mysql -u root -e "GRANT ALL PRIVILEGES ON chat_online.* TO 'admin'@'localhost';" || warn "Error otorgando permisos"
mysql -u root -e "FLUSH PRIVILEGES;" || warn "Error actualizando permisos"

# Inicializar esquema
log "Inicializando esquema de base de datos..."
mysql -u admin -padmin123 chat_online < init.sql || { error "Error inicializando BD"; exit 1; }

# Configurar variables de entorno
log "Configurando variables de entorno..."
cat > .env << EOF
DB_HOST=localhost
DB_USER=admin
DB_PASSWORD=admin123
DB_NAME=chat_online
WS_PORT=8765
PORT=8000
EOF

# Verificar instalación
log "Verificando instalación..."
python3 -c "
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='admin',
        password='admin123',
        database='chat_online'
    )
    print('✅ Conexión a BD exitosa')
    conn.close()
except Exception as e:
    print(f'❌ Error conectando a BD: {e}')
    exit(1)
"

# Verificar dependencias
log "Verificando dependencias..."
python3 -c "
import sys
required = ['mysql.connector', 'websockets', 'asyncio']
missing = []
for module in required:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)
        
if missing:
    print(f'❌ Módulos faltantes: {missing}')
    sys.exit(1)
else:
    print('✅ Todas las dependencias están instaladas')
"

# Crear script de inicio
log "Creando script de inicio..."
cat > start_chat.sh << EOF
#!/bin/bash
echo "🚀 Iniciando Chat Online..."

# Iniciar MySQL si no está corriendo
sudo service mysql start

# Iniciar servidor WebSocket en background
echo "📡 Iniciando servidor WebSocket..."
python3 servidor_websocket.py &
WS_PID=\$!

# Esperar un momento
sleep 3

# Mostrar información
echo ""
echo "✅ Chat Online iniciado correctamente!"
echo "📡 WebSocket servidor: http://localhost:8765"
echo "🌐 Interfaz web: Abre web/index.html en el navegador"
echo "💻 Cliente PyQt5: python3 ChatCliente.py"
echo ""
echo "Para detener el servidor WebSocket: kill \$WS_PID"
echo "PID del WebSocket: \$WS_PID"
EOF

chmod +x start_chat.sh

# Completado
echo ""
log "🎉 ¡Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Ejecutar: ./start_chat.sh"
echo "   2. Abrir web/index.html en el navegador"
echo "   3. ¡Empezar a chatear!"
echo ""
echo "🔧 Comandos útiles:"
echo "   - Iniciar todo: ./start_chat.sh"
echo "   - Solo WebSocket: python3 servidor_websocket.py"
echo "   - Solo cliente PyQt5: python3 ChatCliente.py"
echo "   - Ver logs MySQL: sudo tail -f /var/log/mysql/error.log"
