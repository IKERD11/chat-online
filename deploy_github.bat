@echo off
echo 🚀 Script de Deployment para GitHub Pro
echo ==========================================

echo.
echo 📋 Verificando Git...
git --version
if errorlevel 1 (
    echo ❌ Git no está instalado. Instálalo desde: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo.
echo 🔧 Configurando Git (solo si es primera vez)...
set /p nombre="Ingresa tu nombre: "
set /p email="Ingresa tu email: "
git config --global user.name "%nombre%"
git config --global user.email "%email%"

echo.
echo 📦 Inicializando repositorio...
git init
git add .
git commit -m "🚀 Chat Online - Versión inicial"

echo.
echo 🌐 IMPORTANTE: 
echo 1. Ve a github.com
echo 2. Crear nuevo repositorio llamado "chat-online"
echo 3. NO inicializar con README (ya tienes uno)
echo 4. Copia la URL del repositorio
echo.
set /p repo_url="Pega la URL del repositorio (ej: https://github.com/usuario/chat-online.git): "

echo.
echo 🔗 Conectando con GitHub...
git remote add origin %repo_url%
git branch -M main
git push -u origin main

echo.
echo ✅ ¡Código subido a GitHub!
echo.
echo 📋 Próximos pasos:
echo 1. Ve a tu repositorio en GitHub
echo 2. Settings → Pages → Source: "GitHub Actions"
echo 3. Code → Codespaces → "Create codespace on main"
echo 4. En Codespace ejecutar: ./setup_codespaces.sh
echo.
echo 🎯 URLs finales:
echo Frontend: https://TU_USUARIO.github.io/chat-online
echo Codespace: github.com/codespaces
echo.
pause
