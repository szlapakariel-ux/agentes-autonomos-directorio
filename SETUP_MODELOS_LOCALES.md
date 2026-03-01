# 🤖 INSTALAR MODELOS IA LOCALES - WINDOWS

Guía completa para descargar e instalar modelos IA locales en tu máquina Windows.

Esto permite que los agentes trabajen **sin depender completamente de Claude API** (ahorra tokens y costo).

---

## 📊 MODELOS RECOMENDADOS

Basados en tu arquitectura de agentes:

| Modelo | Tamaño | Uso | Velocidad | Inteligencia |
|--------|--------|-----|-----------|--------------|
| **Llama 3.8B** | 8 GB RAM | Piso 1 (Hunter/Closer) | ⚡⚡⚡ Rápido | ⭐⭐⭐ |
| **Llama 3.70B** | 40 GB RAM | Directorio + Estructuras | ⚡ Lento | ⭐⭐⭐⭐⭐ Excelente |
| **Mistral 7B** | 4 GB RAM | Piso 2 (Operaciones) | ⚡⚡⚡ Rápido | ⭐⭐⭐⭐ Muy bueno |
| **DeepSeek-Coder** | 6 GB RAM | Scripts/Automatizaciones | ⚡⚡⚡ Rápido | ⭐⭐⭐⭐ Código |

---

## 🎯 RECOMENDACIÓN PARA TU SETUP

**Máquina con 16GB RAM (típica):**
- ✅ Llama 3.8B (siempre corriendo)
- ✅ Mistral 7B (para cálculos)
- ⏱️ Llama 3.70B (bajo demanda)

**Máquina con 32GB+ RAM:**
- ✅ Llama 3.70B (permanente)
- ✅ Llama 3.8B
- ✅ Mistral 7B
- ✅ DeepSeek-Coder

---

## 📥 PASO 1: INSTALAR OLLAMA (Gestor de modelos)

**Ollama** es la forma más fácil de instalar y ejecutar modelos locales en Windows.

### Descargar e Instalar

1. Ve a https://ollama.ai/
2. Descarga "Ollama for Windows"
3. Ejecuta el instalador
4. Sigue los pasos (instala por defecto en `C:\Users\[Tu usuario]\AppData\Local\Ollama`)

### Verificar Instalación

```powershell
# Abre PowerShell
ollama --version
# Esperado: ollama version X.X.X
```

---

## 🚀 PASO 2: DESCARGAR MODELOS

**Nota**: La primera descarga tarda tiempo (depende de tu velocidad de internet y tamaño del modelo).

### Opción A: Llama 3.8B (RECOMENDADO PARA EMPEZAR)

```powershell
# Descargar e instalar
ollama pull llama2

# O la versión más nueva (si está disponible)
ollama pull llama2:latest

# Esperado: Descarga ~4GB
# Tiempo: 10-30 minutos (depende de tu velocidad)
```

### Opción B: Mistral 7B (MÁS RÁPIDO)

```powershell
ollama pull mistral

# Esperado: Descarga ~5GB
# Tiempo: 15-30 minutos
```

### Opción C: Llama 3.70B (MÁS INTELIGENTE - PARA DIRECTORIO)

```powershell
# Nota: Requiere al menos 40GB de espacio en disco y 24GB RAM disponible

ollama pull llama2:70b

# Esperado: Descarga ~40GB
# Tiempo: 1-2 horas (depende de velocidad)
```

### Opción D: DeepSeek-Coder (PARA SCRIPTS)

```powershell
ollama pull deepseek-coder:6.7b

# Esperado: Descarga ~4GB
# Tiempo: 10-20 minutos
```

---

## ✅ PASO 3: VERIFICAR DESCARGAS

```powershell
# Listar modelos instalados
ollama list

# Esperado:
# NAME            	ID          	SIZE  	MODIFIED
# llama2:latest   	xxxxxxxxxx  	4.0GB 	X minutes ago
```

---

## 🧪 PASO 4: PROBAR MODELOS

### Ejecutar un modelo (modo interactivo)

```powershell
# Ejecutar Llama
ollama run llama2

# Te abre un chat. Escribe preguntas:
# > ¿Cuáles son los riesgos de una multa por cancelación en psicología?
#
# El modelo responde...
#
# > exit   (para salir)
```

### Ejecutar en background (para API)

```powershell
# Terminal 1: Inicia Ollama en background
ollama serve

# Terminal 2: Haz requests
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "¿Cuáles son los riesgos legales de una multa del 10%?",
  "stream": false
}'

# Respuesta esperada:
# {
#   "response": "Los riesgos legales incluyen...",
#   "model": "llama2",
#   "created_at": "2026-02-28T..."
# }
```

---

## 🔗 PASO 5: CONECTAR CLAUDBOT CON MODELOS LOCALES

Edita tu `.env`:

```env
# ========== MODELOS LOCALES ==========

# Usar Ollama (local) en lugar de Claude API para ciertos agentes
USE_LOCAL_MODELS=True
OLLAMA_HOST=http://localhost:11434

# Asignación de modelos por agente:

# DIRECTORIO (C-Level) - Usa modelo más inteligente
DIRECTORIO_MODEL=llama2:70b
DIRECTORIO_FALLBACK=claude-3-5-sonnet-20241022

# PISO 1 (Hunter/Closer) - Usa modelo rápido
PISO1_MODEL=mistral
PISO1_FALLBACK=llama2

# PISO 2 (Operaciones) - Usa modelo equilibrado
PISO2_MODEL=mistral
PISO2_FALLBACK=claude-3-5-sonnet-20241022

# SCRIPTS/CÓDIGO - Usa DeepSeek-Coder
SCRIPTS_MODEL=deepseek-coder:6.7b
SCRIPTS_FALLBACK=llama2

# ========== FALLBACK A CLAUDE API ==========
# Si modelo local falla, usa Claude API
FALLBACK_TO_CLAUDE=True
CLAUDE_API_KEY=sk-ant-xxxxx...
```

---

## 🎯 PASO 6: INTEGRAR EN CLAUDBOT

```powershell
cd C:\Agentes
.\venv\Scripts\Activate.ps1

# Instalar cliente Ollama para Python
pip install ollama

# Configurar Claudbot para usar modelos locales
claudbot config --local-models enabled
claudbot config --ollama-host http://localhost:11434

# Verificar configuración
claudbot config show
```

---

## 📊 GESTIÓN DE ESPACIO EN DISCO

### Dónde se descargan los modelos

```powershell
# Por defecto en:
C:\Users\[Tu usuario]\.ollama\models

# Verificar espacio usado
Get-ChildItem -Path "C:\Users\$env:USERNAME\.ollama\models" -Recurse | Measure-Object -Property Length -Sum | Select-Object @{Name="TotalSizeGB";Expression={[math]::Round(($_.Sum / 1GB), 2)}}
```

### Limpiar espacio (si necesitas)

```powershell
# ⚠️ ADVERTENCIA: Esto borra modelos descargados

# Listar modelos
ollama list

# Borrar un modelo
ollama rm llama2:70b

# Borrar todos los modelos
# (usar con cuidado - tendrás que descargar de nuevo)
```

---

## ⚡ PASO 7: OPTIMIZAR RENDIMIENTO

### Ejecutar Ollama en background automáticamente

**Opción A: Crear shortcut en Inicio**

```powershell
# Crear archivo .bat
@echo off
start "" "C:\Users\[Tu usuario]\AppData\Local\Ollama\ollama" serve

# Guardar como: C:\Users\[Tu usuario]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\ollama-start.bat
```

**Opción B: Tarea programada**

```powershell
# Crear tarea que inicie Ollama al startup
$taskAction = New-ScheduledTaskAction -Execute "C:\Users\$env:USERNAME\AppData\Local\Ollama\ollama" -Argument "serve"
$taskTrigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -Action $taskAction -Trigger $taskTrigger -TaskName "Ollama" -Description "Start Ollama server" -RunLevel Highest
```

---

## 🔧 PROBLEMAS COMUNES

### Problema: "ollama: command not found"

```powershell
# Solución: Reinstala Ollama desde https://ollama.ai/
# O agrega a PATH:
$env:Path += ";C:\Users\$env:USERNAME\AppData\Local\Ollama"
```

### Problema: "CUDA out of memory"

```powershell
# Significa que el modelo es demasiado grande para tu GPU
# Soluciones:
# 1. Usa modelo más pequeño (llama2:8b en lugar de 70b)
# 2. Aumenta RAM virtual en Windows
# 3. Usa modo CPU (más lento pero posible)
```

### Problema: "Connection refused localhost:11434"

```powershell
# Solución: Ollama no está corriendo
# 1. Abre PowerShell
# 2. Ejecuta: ollama serve
# 3. Mantén la terminal abierta
```

### Problema: Modelo responde muy lento

```powershell
# Soluciones (por orden):
# 1. Usa modelo más pequeño (mistral, llama2:8b)
# 2. Desactiva otros programas
# 3. Aumenta RAM disponible
# 4. Considera usar Claude API para Directorio (es más rápido)
```

---

## 📈 MONITOREO DE RECURSOS

Mientras un modelo está ejecutándose:

```powershell
# Terminal separada: Ver CPU, RAM, GPU en tiempo real
while ($true) {
    Get-Process | Where-Object {$_.Name -like "ollama*"} | Select-Object Name, CPU, @{Name="RAM (MB)";Expression={[math]::Round($_.WorkingSet/1MB)}}
    Start-Sleep -Seconds 2
}
```

---

## 🎯 CONFIGURACIÓN RECOMENDADA POR TIPO DE MÁQUINA

### Máquina "Básica" (8GB RAM)
```env
# Solo modelos pequeños
DIRECTORIO_MODEL=mistral          # Fallback: Claude API
PISO1_MODEL=mistral
PISO2_MODEL=mistral
SCRIPTS_MODEL=deepseek-coder:6.7b
```

### Máquina "Estándar" (16GB RAM)
```env
# Mix de modelos
DIRECTORIO_MODEL=llama2           # Fallback: Claude API
PISO1_MODEL=mistral
PISO2_MODEL=mistral
SCRIPTS_MODEL=deepseek-coder:6.7b
```

### Máquina "Potente" (32GB+ RAM)
```env
# Todos los modelos
DIRECTORIO_MODEL=llama2:70b
PISO1_MODEL=llama2
PISO2_MODEL=mistral
SCRIPTS_MODEL=deepseek-coder:6.7b
```

---

## 📞 SIGUIENTE

Una vez tengas modelos instalados y corriendo:

1. Verifica que Claudbot puede conectar: `claudbot health`
2. Ve a `SETUP_WINDOWS.md` para terminar setup
3. Ve a `PRIMERA_REUNION.md` para lanzar reunión piloto

---

**Status**: 🚀 Ready to Download Models
**Última actualización**: 2026-02-28
