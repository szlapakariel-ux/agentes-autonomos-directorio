# 🤖 INSTRUCCIONES PARA CLAUDE CODE - INSTALAR CLAUDBOT

**IMPORTANTE**: Este archivo contiene las ÓRDENES EXPLÍCITAS para que Claude Code instale y configure TODO automáticamente.

---

## 📋 CONTEXTO

Este repositorio es un **sistema de agentes IA autónomos** que funciona como una empresa real.

**Tu tarea como Claude Code es:**
1. Instalar Claudbot en esta máquina Windows
2. Descargar modelos IA locales (Llama, Mistral, DeepSeek)
3. Configurar seguridad y credenciales
4. Dejar el sistema **totalmente operativo**

---

## ✅ ORDEN #1: INSTALAR CLAUDBOT Y DEPENDENCIAS

**EJECUTAR EN ESTA MÁQUINA WINDOWS:**

```powershell
# 1. Verificar Python
python --version
# Esperado: Python 3.10+
# Si falta: Instalar desde https://www.python.org/downloads/

# 2. Verificar Git
git --version
# Esperado: Git 2.x+
# Si falta: Instalar desde https://git-scm.com/download/win

# 3. Crear virtual environment
python -m venv venv

# 4. Activar virtual environment
.\venv\Scripts\Activate.ps1

# 5. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 6. Instalar Claudbot
pip install claudbot

# 7. Verificar instalación
claudbot --version
python -c "import claudbot; print('✅ Claudbot importable')"
```

**RESPONSABLE**: Ejecutar estos comandos y verificar que TODO funciona.

---

## ✅ ORDEN #2: DESCARGAR MODELOS IA LOCALES

**EJECUTAR EN ESTA MÁQUINA WINDOWS:**

```powershell
# 1. Instalar Ollama (gestor de modelos)
# Descargar de: https://ollama.ai/
# Ejecutar instalador y seguir pasos

# 2. Verificar Ollama
ollama --version
# Esperado: ollama version X.X.X

# 3. Descargar modelos (EN ORDEN)

# Modelo A: Llama 3.8B (OBLIGATORIO - PISO 1)
ollama pull llama2
# Esperado: Descarga ~4GB, tiempo 10-30 min

# Modelo B: Mistral 7B (OBLIGATORIO - PISO 2)
ollama pull mistral
# Esperado: Descarga ~5GB, tiempo 15-30 min

# Modelo C: DeepSeek-Coder (OPCIONAL - SCRIPTS)
ollama pull deepseek-coder:6.7b
# Esperado: Descarga ~4GB, tiempo 10-20 min

# Modelo D: Llama 3.70B (OPCIONAL - DIRECTORIO)
# SOLO si tienes 24GB+ RAM libre
# ollama pull llama2:70b
# Esperado: Descarga ~40GB, tiempo 1-2 horas

# 4. Verificar modelos instalados
ollama list
# Esperado: Ver modelos descargados
```

**RESPONSABLE**: Ejecutar descargas y verificar que modelos están instalados.

---

## ✅ ORDEN #3: CONFIGURAR SEGURIDAD Y CREDENCIALES

**EJECUTAR EN ESTA MÁQUINA WINDOWS:**

```powershell
# 1. Crear archivo .env seguro
Copy-Item infraestructura\config\.env.example infraestructura\config\.env

# 2. Editar .env con credenciales reales
# IMPORTANTE: NO dejar valores vacíos
# Necesitas:
#   - CLAUDE_API_KEY (de https://console.anthropic.com/)
#   - DATABASE_URL (local OK)
#   - Otros valores según .env.example

# Editor recomendado: VSCode o Notepad
notepad infraestructura\config\.env

# 3. Configurar permisos de archivo .env
icacls infraestructura\config\.env /inheritance:r /grant:r "$env:USERNAME:(F)"

# 4. Crear carpeta de secretos
mkdir C:\Users\$env:USERNAME\.agentes-secrets

# 5. Configurar permisos de carpeta
icacls C:\Users\$env:USERNAME\.agentes-secrets /inheritance:r /grant:r "$env:USERNAME:(F)"

# 6. Guardar API key en variable de sistema (alternativa segura)
[Environment]::SetEnvironmentVariable("CLAUDE_API_KEY", "sk-ant-xxxxx-TU-CLAVE-AQUI", "User")

# 7. Verificar que variable de entorno se guardó
$env:CLAUDE_API_KEY
# Esperado: Ver tu API key
```

**RESPONSABLE**: Configurar credenciales de forma SEGURA. NUNCA subir a GitHub.

---

## ✅ ORDEN #4: INICIALIZAR CLAUDBOT

**EJECUTAR EN ESTA MÁQUINA WINDOWS:**

```powershell
# 1. Activar virtual environment (si no está activo)
.\venv\Scripts\Activate.ps1

# 2. Inicializar Claudbot
claudbot init

# 3. Esperado: Ver mensajes como:
# ✅ Configuration loaded
# ✅ Database initialized
# ✅ Prompts loaded (6 agents)
# ✅ Ollama connection: OK
# ✅ Ready to start

# 4. Cargar prompts del Directorio
claudbot load-prompts --path ./directorio/prompts

# 5. Verificar que agentes están cargados
claudbot list-agents
# Esperado: Ver 6 agentes (CEO, CRO, CVO, COO, CFO, JARVISZ)
```

**RESPONSABLE**: Inicializar y verificar que TODO carga correctamente.

---

## ✅ ORDEN #5: VERIFICAR QUE CLAUDBOT ESTÁ OPERATIVO

**EJECUTAR EN ESTA MÁQUINA WINDOWS:**

```powershell
# 1. Terminal 1: Iniciar Claudbot en background
claudbot serve --host 127.0.0.1 --port 8000

# 2. Terminal 2 (nueva): Hacer requests de prueba
# Espera 5 segundos a que Claudbot inicie

# Test 1: Health check
curl http://localhost:8000/api/v1/health
# Esperado: {"status": "ok"}

# Test 2: Ver agentes
curl http://localhost:8000/api/v1/agents
# Esperado: ["CEO", "CRO", "CVO", "COO", "CFO", "JARVISZ"]

# Test 3: Ver estado de Ollama
curl http://localhost:8000/api/v1/models
# Esperado: Listar modelos disponibles

# Test 4: Iniciar mini reunión test
curl -X POST http://localhost:8000/api/v1/meeting/start -d '{
  "topic": "Test de sistema",
  "proyecto": "sicologa"
}'
# Esperado: {"status": "ok", "meeting_id": "..."}
```

**RESPONSABLE**: Verificar que Claudbot responde a requests. Si falla, revisar logs.

---

## ✅ ORDEN #6: CREAR SCRIPTS DE INICIO AUTOMÁTICO

**OPCIONAL PERO RECOMENDADO:**

```powershell
# Crear archivo start-claudbot.bat en raíz del repo
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
claudbot serve --host 127.0.0.1 --port 8000
pause

# Crear acceso directo en Escritorio para iniciar rápido
# O agregar a tareas programadas de Windows para auto-start
```

---

## 🎯 RESUMEN DE LO QUE DEBE PASAR

### **Después de completar estas 6 órdenes:**

✅ **Python 3.10+** instalado
✅ **Virtual environment** creado y activo
✅ **Claudbot** instalado y funcional
✅ **Ollama** con modelos locales corriendo
✅ **Credenciales** seguras en .env
✅ **Directorio** cargado (6 agentes listos)
✅ **API** respondiendo en http://localhost:8000
✅ **Sistema listo** para primera reunión

---

## 📋 CHECKLIST DE VERIFICACIÓN

Antes de decir "LISTO":

- [ ] `python --version` → 3.10+
- [ ] `git --version` → 2.x+
- [ ] Virtual environment activado
- [ ] `pip list` → tiene claudbot
- [ ] `ollama list` → muestra modelos
- [ ] `.env` existe y tiene credenciales
- [ ] `.env` tiene permisos restringidos
- [ ] `claudbot --version` → funciona
- [ ] `curl http://localhost:8000/api/v1/health` → OK
- [ ] `curl http://localhost:8000/api/v1/agents` → 6 agentes

---

## ⚠️ SI ALGO FALLA

### **Python no está instalado:**
```powershell
# Descargar de: https://www.python.org/downloads/
# Ejecutar instalador
# Asegurarse de checkear "Add Python to PATH"
# Reiniciar PowerShell
```

### **Claudbot falla a instalar:**
```powershell
pip install claudbot --upgrade --force
# O si está muy mal:
pip uninstall claudbot -y
pip install claudbot
```

### **Ollama no encuentra modelos:**
```powershell
# Ollama guarda modelos en:
# C:\Users\[TuUsuario]\.ollama\models
# Verificar que hay espacio (50GB mínimo disponible)
```

### **API no responde:**
```powershell
# 1. Asegúrate que claudbot serve está corriendo
# 2. Verifica que puerto 8000 no está bloqueado:
netstat -an | findstr 8000
# 3. Reinicia: Ctrl+C en terminal 1, ejecuta claudbot serve nuevamente
```

---

## 🚀 PRÓXIMAS FASES

Una vez que Claudbot esté operativo:

1. **Sistema de logging de Jarvisz** (SQLite)
2. **API para ejecutar reuniones** (FastAPI)
3. **Primera reunión piloto** sobre Sicologa
4. **Dashboard web** (próximo)

---

## 📞 REFERENCIA RÁPIDA

```powershell
# Verificar Claudbot
claudbot --version
claudbot status

# Servir Claudbot
claudbot serve --host 127.0.0.1 --port 8000

# Cargar prompts
claudbot load-prompts --path ./directorio/prompts

# Listar agentes
claudbot list-agents

# Ver logs
claudbot logs --tail 50

# Health check
curl http://localhost:8000/api/v1/health
```

---

## ✅ CHECKLIST FINAL

**Cuando todo esté listo, deberías poder:**

```powershell
# Terminal 1
claudbot serve

# Terminal 2
curl http://localhost:8000/api/v1/health
# {"status": "ok"}

curl http://localhost:8000/api/v1/agents
# ["CEO", "CRO", "CVO", "COO", "CFO", "JARVISZ"]

# ENTONCES: Sistema está 100% operativo
```

---

**RESPONSABLE**: Claude Code (tú mismo cuando abras este repo en la máquina)

**PLAZO**: Completar todas las órdenes antes de intentar primera reunión

**VALIDACIÓN**: Ejecutar checklist final para confirmar que TODO funciona

---

**Status**: 🚀 Listo para ser ejecutado
**Última actualización**: 2026-02-28
