# 🚀 Guía Paso a Paso - Deployment con GitHub Pro

## ✅ **Preparación Completada**

Los siguientes archivos han sido creados para GitHub:

- ✅ `.devcontainer/devcontainer.json` - Configuración Codespaces
- ✅ `.github/workflows/deploy.yml` - CI/CD automático  
- ✅ `README.md` - Documentación atractiva
- ✅ `.gitignore` - Archivos a ignorar
- ✅ `deploy_github.bat` - Script automatizado

## 🔧 **Paso 1: Instalar Git**

Si Git no está instalado:

### Opción A: Winget (Recomendado)
```powershell
winget install --id Git.Git -e --source winget
```

### Opción B: Descarga Manual
1. Ve a: https://git-scm.com/download/win
2. Descarga e instala Git for Windows
3. Reinicia PowerShell/CMD

## 📦 **Paso 2: Subir a GitHub**

### Método Automático (Recomendado)
```cmd
deploy_github.bat
```

### Método Manual
```bash
# 1. Configurar Git (primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@gmail.com"

# 2. Inicializar repo
git init
git add .
git commit -m "🚀 Chat Online - Versión inicial"

# 3. Crear repo en GitHub
# Ve a github.com → "+" → "New repository"
# Nombre: "chat-online"
# NO marcar "Initialize with README"

# 4. Conectar y subir
git remote add origin https://github.com/TU_USUARIO/chat-online.git
git branch -M main
git push -u origin main
```

## ☁️ **Paso 3: Configurar GitHub Pages**

1. Ve a tu repositorio en GitHub
2. **Settings** (pestaña)
3. **Pages** (menú izquierdo)
4. **Source**: "GitHub Actions"
5. ¡Se desplegará automáticamente!

**URL final**: `https://TU_USUARIO.github.io/chat-online`

## 🔧 **Paso 4: Crear GitHub Codespace**

1. En tu repo → botón **"Code"**
2. Pestaña **"Codespaces"**
3. **"Create codespace on main"**
4. Esperar ~3 minutos (configuración automática)
5. En terminal del Codespace:
   ```bash
   ./setup_codespaces.sh
   ./start_chat.sh
   ```

## 🚀 **Paso 5: Deploy Backend**

### Opción A: Railway.app ($5/mes)
```bash
# En Codespaces:
curl -fsSL https://railway.app/install.sh | sh
railway login
railway new
railway up
```

### Opción B: Render.com (Gratis)
1. Ve a render.com
2. Connect GitHub
3. Deploy como "Web Service"
4. Build: `pip install -r requirements.txt`
5. Start: `python servidor_websocket.py`

## 🎯 **Resultado Final**

### URLs de tu Chat:
- **🌐 Frontend**: `https://TU_USUARIO.github.io/chat-online`
- **⚡ Backend**: `https://tu-app.railway.app` o `https://tu-app.onrender.com`
- **☁️ Desarrollo**: GitHub Codespaces

### Funcionalidades:
- ✅ **Chat web** responsive
- ✅ **5 temas** personalizables
- ✅ **Registro/Login** automático
- ✅ **Tiempo real** con WebSockets
- ✅ **Cliente desktop** PyQt5
- ✅ **Base de datos** MySQL

### Costos:
- **Frontend**: Gratis (GitHub Pages)
- **Backend**: $5/mes (Railway) o Gratis (Render con limitaciones)
- **Desarrollo**: Gratis con GitHub Pro (120h Codespaces)

## 🔄 **Updates Futuros**

Para actualizar tu chat:
```bash
git add .
git commit -m "Nueva funcionalidad"
git push
```

¡Se desplegará automáticamente!

## 🆘 **Solución de Problemas**

### Git no funciona
```bash
# Verificar instalación
git --version

# Si no funciona, reiniciar terminal
# O instalar desde: https://git-scm.com/download/win
```

### GitHub Pages no se despliega
1. Verificar Actions en pestaña "Actions"
2. Verificar Pages en Settings → Pages

### WebSocket no conecta
1. Verificar URL en `web/index.html`
2. Cambiar `ws://localhost:8765` por tu URL de Railway

---

¿Estás listo para empezar? ¡Ejecuta `git --version` para verificar la instalación! 🚀
