# 🔧 SETUP CLAUDBOT EN WINDOWS - MÁQUINA AUTÓNOMA

Esta guía te ayudará a instalar y configurar Claudbot en tu máquina Windows dedicada para operar el sistema de agentes autónomos.

---

## 📋 REQUISITOS PREVIOS

**Hardware:**
- Mínimo: CPU 4-cores, 8GB RAM, 50GB SSD libre
- Recomendado: CPU 8-cores, 16GB+ RAM, 100GB SSD

**Software:**
- Windows 10 / Windows 11
- Python 3.10+ (https://www.python.org/downloads/)
- Git for Windows (https://git-scm.com/download/win)
- Visual Studio Build Tools (para compilar C extensions)

---

## ✅ PASO 1: VERIFICAR REQUISITOS

### Abre PowerShell como Administrador y ejecuta:

```powershell
# Verificar Python
python --version
# Esperado: Python 3.10+

# Verificar Git
git --version
# Esperado: git version 2.x+

# Verificar espacio libre en disco
(Get-Volume).SizeRemaining | Format-FileSize
# Esperado: mínimo 50GB
```

Si algo falta, instálalo desde los links de arriba.

---

## 📦 PASO 2: CLONAR REPOSITORIO

```powershell
# Ubicación recomendada: C:\Agentes (fácil de navegar)
cd C:\
git clone https://github.com/szlapakariel-ux/agentes-autonomos-directorio.git Agentes
cd Agentes

# Verificar que clonó correctamente
git log --oneline
# Deberías ver los commits
```

---

## 🐍 PASO 3: INSTALAR PYTHON DEPENDENCIES

```powershell
# Crear virtual environment (aislado)
python -m venv venv

# Activar virtual environment
.\venv\Scripts\Activate.ps1

# Si obtienes error de ejecución, ejecuta:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalación
pip list
```

---

## 🤖 PASO 4: INSTALAR CLAUDBOT

Claudbot es el **orquestador central** que ejecutará todos los agentes.

### Opción A: Instalar desde PyPI (Recomendado)

```powershell
# Instalar Claudbot
pip install claudbot

# Verificar instalación
claudbot --version
```

### Opción B: Instalar desde fuente (Si necesitas desarrollo)

```powershell
# Clonar Claudbot repo
git clone https://github.com/anthropics/claudbot.git claudbot-src
cd claudbot-src

# Instalar en modo desarrollo
pip install -e .

cd ..  # Volver al directorio de agentes
```

---

## 🔐 PASO 5: CONFIGURAR SEGURIDAD Y CREDENCIALES

### 🚨 IMPORTANTE: Credenciales Seguras

**NUNCA** guardes API keys en archivos de texto sin encriptación.

#### 5.1: Crear archivo .env local (NO en GitHub)

```powershell
# Copiar template
Copy-Item infraestructura\config\.env.example infraestructura\config\.env

# Editar con tu editor (Notepad, VSCode, etc.)
notepad infraestructura\config\.env
```

**Qué poner en .env:**
```env
# OBLIGATORIO - Credenciales Claude API (si las usarás)
CLAUDE_API_KEY=sk-ant-xxxxx... # Tu clave API real

# SEGURIDAD - Puerto y host
API_HOST=127.0.0.1  # Solo local (NO 0.0.0.0 en prod)
API_PORT=8000

# BASE DE DATOS
DATABASE_URL=sqlite:///./infraestructura/db/agentes.db

# JARVISZ DATA WAREHOUSE
JARVISZ_DB_PATH=./infraestructura/db/jarvisz.db

# PROYECTO
PROYECTO_ACTUAL=sicologa
ENVIRONMENT=development
DEBUG=False  # Cambiar a False en producción
```

#### 5.2: Configurar permisos de archivo .env

```powershell
# Solo tu usuario puede leer .env
icacls infraestructura\config\.env /inheritance:r /grant:r "$env:USERNAME:(F)"

# Verificar que solo tú tienes acceso
icacls infraestructura\config\.env
```

#### 5.3: Crear carpeta segura para secretos

```powershell
# Crear carpeta
mkdir C:\Agentes\secrets

# Configurar permisos (solo lectura para administrador)
icacls C:\Agentes\secrets /inheritance:r /grant:r "SYSTEM:(F)" "$env:USERNAME:(F)"
```

---

## 🔑 PASO 6: GENERAR Y GUARDAR API KEYS (Si usarás Claude API)

### Obtener API Key de Anthropic:

1. Ve a https://console.anthropic.com/
2. Crea una cuenta (si no tienes)
3. Genera una API Key
4. **GUARDA EN LUGAR SEGURO** (NO en repo)

### Almacenar de forma segura:

**Opción A: Variables de entorno del sistema (Recomendado)**

```powershell
# Ejecutar como Administrador:
[Environment]::SetEnvironmentVariable("CLAUDE_API_KEY", "sk-ant-xxxxx", "User")

# Verificar
$env:CLAUDE_API_KEY
```

**Opción B: En archivo .env local (con permisos restringidos)**

```powershell
# Ya hecho en PASO 5.2
# Solo el archivo .env tiene credenciales
# Nunca se sube a GitHub (.gitignore lo protege)
```

---

## 🧪 PASO 7: VERIFICAR INSTALACIÓN

```powershell
# Activar venv si no está activo
.\venv\Scripts\Activate.ps1

# Verificar dependencias
python -c "import fastapi; import sqlalchemy; import anthropic; print('✅ Dependencias OK')"

# Verificar Claudbot
claudbot --help
# Deberías ver el menú de ayuda

# Verificar que archivos de configuración existen
Test-Path infraestructura\config\.env
Test-Path infraestructura\db\
```

---

## 🚀 PASO 8: INICIAR CLAUDBOT (PRIMERA VEZ)

```powershell
# Activar venv
.\venv\Scripts\Activate.ps1

# Inicializar Claudbot
claudbot init

# Claudbot debería:
# 1. Crear estructura de directorios
# 2. Validar credenciales
# 3. Conectar con bases de datos
# 4. Cargar prompts del directorio

# Esperado:
# ✅ Configuration loaded
# ✅ Database initialized
# ✅ Prompts loaded (6 agents)
# ✅ Ready to start
```

---

## 🔗 PASO 9: CONECTAR CLAUDBOT CON TU REPO LOCAL

```powershell
# Claudbot necesita saber dónde están los prompts
# Edita infraestructura\config\.env:

PROMPTS_PATH=C:\Agentes\directorio\prompts
LOGS_PATH=C:\Agentes\directorio\logs
DB_PATH=C:\Agentes\infraestructura\db

# O Claudbot puede auto-detectar si lo ejecutas desde el repo
cd C:\Agentes
claudbot load-prompts
```

---

## 🎮 PASO 10: ARRANCAR EL SISTEMA

### Opción A: CLI (Command Line)

```powershell
cd C:\Agentes
.\venv\Scripts\Activate.ps1

claudbot start
# El sistema está listo para recibir comandos
```

### Opción B: API Server (Para futuros dashboards web)

```powershell
cd C:\Agentes
.\venv\Scripts\Activate.ps1

python infraestructura\api\server.py
# Accede a http://localhost:8000/api/v1/health
# Esperado: {"status": "ok", "agents": 6}
```

---

## 🔒 SEGURIDAD - CHECKLIST

- [ ] .env está en .gitignore
- [ ] .env tiene permisos restringidos (solo tu usuario)
- [ ] API_HOST = 127.0.0.1 (NO 0.0.0.0)
- [ ] DEBUG = False en producción
- [ ] API_KEY guardada en variable de entorno del sistema (NO en repo)
- [ ] Base de datos SQLite en disco local (NO en red sin encriptación)
- [ ] Logs en carpeta protegida
- [ ] Firewall permite solo puerto necesario (8000 local)

---

## ⚠️ TROUBLESHOOTING

### Problema: "ModuleNotFoundError: No module named 'claudbot'"

```powershell
# Solución:
.\venv\Scripts\Activate.ps1
pip install claudbot --upgrade
```

### Problema: "Permission denied" en .env

```powershell
# Solución:
icacls infraestructura\config\.env /reset /grant:r "$env:USERNAME:(F)"
```

### Problema: "API_KEY not found"

```powershell
# Solución:
# 1. Verifica que .env existe
# 2. Verifica que CLAUDE_API_KEY está en .env
# 3. Verifica permisos: icacls infraestructura\config\.env
# 4. Si usas variable de sistema: [Environment]::GetEnvironmentVariable("CLAUDE_API_KEY")
```

### Problema: "Cannot connect to database"

```powershell
# Solución:
# 1. Verifica que carpeta infraestructura\db\ existe
mkdir infraestructura\db -Force
# 2. Verifica DATABASE_URL en .env
# 3. Asegúrate que ruta es correcta: ./infraestructura/db/agentes.db
```

---

## 📊 VERIFICAR QUE CLAUDBOT ESTÁ OPERATIVO

```powershell
# En otra PowerShell (mantener Claudbot corriendo):

# 1. Verificar que responde
curl http://localhost:8000/api/v1/health
# Esperado: {"status": "ok"}

# 2. Cargar directorio
curl http://localhost:8000/api/v1/directorio/status
# Esperado: {"agents": 6, "status": "ready"}

# 3. Listar agentes
curl http://localhost:8000/api/v1/agents
# Esperado: ["CEO", "CRO", "CVO", "COO", "CFO", "JARVISZ"]
```

---

## 🎯 SIGUIENTE: PRIMERA REUNIÓN PILOTO

Una vez que Claudbot esté operativo:

1. Crea primera reunión sobre Sicologa
2. Claudbot carga los prompts del Directorio
3. Cada agente analiza el proyecto desde su rol
4. Jarvisz registra todo
5. Recibes reporte diario

👉 **Ver**: `PRIMERA_REUNION.md`

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisa logs: `directorio\logs\`
2. Verifica .env: `infraestructura\config\.env`
3. Mira este archivo nuevamente (troubleshooting)
4. Contacta al equipo técnico

---

**Status**: 🚀 Ready to Setup
**Última actualización**: 2026-02-28
