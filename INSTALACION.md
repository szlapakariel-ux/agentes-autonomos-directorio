# 🚀 GUÍA DE INSTALACIÓN COMPLETA - AGENTES AUTÓNOMOS

**Para instalar y operar el sistema en tu máquina Windows dedicada**

---

## 📋 ÍNDICE DE INSTALACIÓN

**⚠️ IMPORTANTE**: Si eres Claude Code (abres esto en la máquina), lee primero: [INSTRUCCIONES_PARA_CLAUDE.md](./INSTRUCCIONES_PARA_CLAUDE.md)

Ese archivo tiene las **órdenes explícitas** para instalar TODO automáticamente.

---

Sigue estos pasos **EN ORDEN**:

### 1️⃣ [INSTRUCCIONES_PARA_CLAUDE.md](./INSTRUCCIONES_PARA_CLAUDE.md) ← **LEE PRIMERO**
**Órdenes explícitas para instalar Claudbot + Modelos + Seguridad**

- Instalar Claudbot
- Descargar modelos IA (Ollama)
- Configurar seguridad
- Verificar que TODO funciona
- **Tiempo**: 2-4 horas (depende de descargas)

**👉 Si eres Claude Code, EMPIEZA AQUÍ**

---

### 2️⃣ [SETUP_WINDOWS.md](./SETUP_WINDOWS.md)
**Guía detallada (manual): Instala Claudbot y dependencias Python**

- Requisitos previos (Python, Git, etc.)
- Clonar repositorio
- Virtual environment
- Instalar Claudbot
- Configurar seguridad y credenciales
- Verificar instalación
- **Tiempo**: 30-45 minutos

**👉 Haz esto PRIMERO**

---

### 2️⃣ [SETUP_MODELOS_LOCALES.md](./SETUP_MODELOS_LOCALES.md)
**Descarga modelos IA locales (Ollama)**

- Instalar Ollama
- Descargar Llama 3, Mistral, DeepSeek-Coder
- Conectar Claudbot con modelos locales
- Optimizar rendimiento
- **Tiempo**: 1-3 horas (depende de velocidad Internet y RAM)

**👉 Haz esto DESPUÉS de SETUP_WINDOWS.md**

---

### 3️⃣ PRIMERA_REUNION.md (Próximo)
**Lanza tu primer reunión piloto sobre Sicologa**

- Iniciar Claudbot
- Ejecutar Directorio
- Ver cómo razonan los agentes
- Recibir reportes de Jarvisz

---

## ⏱️ TIEMPO TOTAL ESTIMADO

| Paso | Duración |
|------|----------|
| Setup Windows + Claudbot | 30-45 min |
| Descargar modelos IA | 1-3 horas |
| Primera reunión piloto | 5-10 min |
| **TOTAL** | **2-4 horas** |

---

## 🎯 RESUMEN RÁPIDO

Si ya tienes experiencia con Windows/Linux:

```powershell
# 1. Clonar repo
git clone https://github.com/szlapakariel-ux/agentes-autonomos-directorio.git
cd agentes-autonomos-directorio

# 2. Setup Python
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install claudbot

# 3. Setup modelos locales
# Descargar Ollama: https://ollama.ai/
# ollama pull llama2
# ollama pull mistral
# ollama pull deepseek-coder:6.7b

# 4. Configurar
Copy-Item infraestructura\config\.env.example infraestructura\config\.env
# Edita .env con tus credenciales

# 5. Iniciar
claudbot start
```

---

## 🔒 SEGURIDAD - PUNTOS CRÍTICOS

✅ **ANTES DE COMENZAR:**
- [ ] Lees SETUP_WINDOWS.md completo
- [ ] Entiendes qué es un .env y por qué NO subirlo a GitHub
- [ ] Sabes dónde guardar API keys de forma segura
- [ ] Tienes permisos de administrador en tu máquina

✅ **DURANTE LA INSTALACIÓN:**
- [ ] .env está en .gitignore (protegido)
- [ ] API_KEY guardada en variable de sistema o .env local
- [ ] Permisos de archivo restringidos (solo tu usuario)
- [ ] DEBUG = False en producción
- [ ] API_HOST = 127.0.0.1 (solo local)

---

## 💾 REQUISITOS DE ESPACIO

| Componente | Espacio |
|-----------|---------|
| Repo + Python venv | 3-5 GB |
| Llama 3.8B | 4 GB |
| Mistral 7B | 5 GB |
| Llama 3.70B (opcional) | 40 GB |
| DeepSeek-Coder (opcional) | 4 GB |
| **TOTAL RECOMENDADO** | **50-100 GB** |

---

## 🎮 DESPUÉS DE INSTALAR

Una vez completados todos los pasos:

1. **Claudbot está operativo** → Sistema listo
2. **Modelos locales corriendo** → Agentes pueden trabajar offline
3. **Primera reunión** → Prueba el sistema
4. **Próxima fase** → Integración con Sicologa

---

## 🆘 PROBLEMAS?

1. **Paso 1 falla**: Ver SETUP_WINDOWS.md → Troubleshooting
2. **Paso 2 falla**: Ver SETUP_MODELOS_LOCALES.md → Problemas comunes
3. **Paso 3 falla**: Ver PRIMERA_REUNION.md (próximo documento)

---

## 📞 CONTACTO & SOPORTE

- **Repo**: https://github.com/szlapakariel-ux/agentes-autonomos-directorio
- **Documentación**: Aquí en este repo
- **Issues**: Crea un issue en GitHub si encuentras problema

---

**¿Listo para empezar?**

👉 **ABRE: [SETUP_WINDOWS.md](./SETUP_WINDOWS.md)**

---

**Status**: 🚀 Ready to Setup
**Última actualización**: 2026-02-28
