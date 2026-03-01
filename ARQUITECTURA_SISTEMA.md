# 🏛️ ARQUITECTURA DEL SISTEMA - Agentes Autónomos Directorio Ejecutivo

## 🎯 VISIÓN GENERAL

Un **sistema de agentes IA multi-rol** que simula un directorio ejecutivo real donde:
- Cada agente tiene una **personalidad única** basada en su rol
- Cada agente **piensa de forma autónoma** usando Claude API
- Los agentes **coordina y se confrontan** (sana tensión creativa)
- Todo queda **registrado y analizado** por Jarvisz (data warehouse)
- Se **detectan patrones** de decisión a lo largo del tiempo

---

## 📊 CAPA 1: PROMPTS DE ROLES (Personalidades)

Cada rol tiene un prompt que define SU MENTALIDAD:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIRECTORIO EJECUTIVO                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👑 CEO                 🛡️ CRO                🚀 CVO            │
│  • Visión global        • Encuentra riesgos     • Busca oportu.  │
│  • Toma decisión final  • Abogado del diablo    • Diferencial    │
│  • Comunica al board    • Paranoia = virtud     • Narrativa      │
│                                                                 │
│  ⚙️ COO                 💰 CFO                📝 JARVISZ        │
│  • Plan ejecución       • Números + números    • Registra TODO  │
│  • Timeline            • ROI/CAC/LTV           • Detecta patron │
│  • Recursos            • ¿Quemamos dinero?     • Sin opiniones  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Características por rol:**

| Rol | Mentalidad | Busca | Bloquea Si |
|-----|-----------|-------|-----------|
| **CEO** | Visionario | Oportunidades estratégicas | Falta alineación |
| **CRO** | Paranoico | Riesgos | Hay riesgo CRÍTICO sin mitigación |
| **CVO** | Creativo | Diferencial "injusto" | Idea demasiado genérica |
| **COO** | Pragmático | Timeline realista | Falta capacidad/recursos |
| **CFO** | Financiero | ROI positivo | LTV/CAC < 3:1 |
| **JARVISZ** | Observador | Patrones + tendencias | (no opina) |

---

## 🔄 CAPA 2: ORQUESTADOR (Orquestación de Agentes)

```
┌────────────────────────────────────────────────────┐
│         ORQUESTADOR                                │
│  (Coordinador Central de Agentes)                 │
└────────────────┬───────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ CARGA  │ │EJECUTA  │ │RECOLECTA│
│ PROMPTS│ │AGENTES  │ │ANÁLISIS │
└─────────┘ └─────────┘ └─────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Cada agente piensa │
        │ de forma autónoma  │
        │ (Claude API)       │
        └────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│DETECTA  │ │SINTETIZA│ │PROPONE  │
│CONFLICTO│ │DECISIÓN │ │ESPECIAL.│
└─────────┘ └─────────┘ └─────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Registra en JARVISZ│
        └────────────────────┘
```

---

## 🧠 CAPA 3: AGENTES AUTÓNOMOS (Pensamiento Independiente)

### Cómo un prompt se convierte en un agente autónomo:

```
┌─────────────────────────────────────────┐
│  PROMPT (Definición de rol)              │
│                                         │
│  "Eres CRO. Tu misión: Encontrar el    │
│   punto de quiebre de cualquier idea.  │
│   Tu paranoia es tu valor."            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  CONTEXTO DEL TEMA                      │
│                                         │
│  "Sicologa: Plataforma de telemedicina │
│   psicológica. $500K. 12 semanas."     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  CLAUDE API (Pensamiento)               │
│                                         │
│  Combina: Prompt + Contexto             │
│  Responde: Análisis fundamentado       │
│  Piensa: Como CRO lo haría             │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  ANÁLISIS AUTÓNOMO (Salida)             │
│                                         │
│  "VEREDICTO: Aprobado con condiciones  │
│   RIESGOS CRÍTICOS:                    │
│   1. Regulación de telemedicina        │
│   2. Privacidad de datos de salud      │
│   DATOS QUE NECESITO:                  │
│   🔴 Mapa regulatorio por país"        │
└─────────────────────────────────────────┘
```

---

## 💾 CAPA 4: JARVISZ (Data Warehouse + Análisis de Patrones)

```
┌──────────────────────────────────────────────┐
│              JARVISZ DATA WAREHOUSE           │
│         (SQLite + Análisis de Patrones)     │
└──────────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ TABLA: REUNIONES                        │
├─────────────────────────────────────────┤
│ ID │ Tema │ Fecha │ Análisis (5 roles)  │
│    │      │       │ Decisión │ Tareas  │
├─────────────────────────────────────────┤
│ 1  │Sicologa│01-03-26│CEO/CRO/CVO/COO/CFO│
│    │        │        │"Aprobado con..." │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ TABLA: PATRONES                         │
├─────────────────────────────────────────┤
│ ID │ Agente │ Patrón │ Apariciones │    │
├─────────────────────────────────────────┤
│ 1  │ CRO    │"Siempre prioriza│ 2     │
│    │        │ riesgos legales"        │
│ 2  │ CVO    │"Busca diferencial│ 3     │
│    │        │ narrativo"              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ TABLA: DATOS_FALTANTES                  │
├─────────────────────────────────────────┤
│ ID │ Solicitante │ Dato │ Severidad │  │
├─────────────────────────────────────────┤
│ 1  │ CRO         │"Mapa regulatorio"│🔴│
│ 2  │ CFO         │"Proyección fin."│🔴│
│ 3  │ CVO         │"Análisis compet"│🟡│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ TABLA: ESPECIALISTAS                    │
├─────────────────────────────────────────┤
│ ID │ Nombre │ Especialidad │ Patrón │  │
├─────────────────────────────────────────┤
│ 1  │ Abog. Legal│"Telemedicina"│CRO1│
│ 2  │ Product    │"Go-to-market"│CVO3│
└─────────────────────────────────────────┘
```

---

## 🔁 FLUJO COMPLETO DE UNA REUNIÓN

```
1. INICIACIÓN
   ┌─────────────────────────────┐
   │ Usuario: "Analizar Sicologa"│
   └────────────┬────────────────┘
                │
2. CARGA DE PROMPTS
   ┌─────────────────────────────┐
   │ Orquestador carga:          │
   │ • CEO_prompt.md             │
   │ • CRO_prompt.md             │
   │ • CVO_prompt.md (y más...)  │
   └────────────┬────────────────┘
                │
3. EJECUCIÓN PARALELA (teórica)
   ┌─────────────────────────────┐
   │ A la vez:                   │
   │ • CEO piensa...             │
   │ • CRO analiza riesgos...    │
   │ • CVO busca diferencial...  │
   │ • COO planifica...          │
   │ • CFO calcula números...    │
   └────────────┬────────────────┘
                │
4. RECOLECCIÓN
   ┌─────────────────────────────┐
   │ Orquestador obtiene:        │
   │ • 5 análisis (1 por agente) │
   │ • Datos que pidieron        │
   │ • Sugerencias especialistas │
   └────────────┬────────────────┘
                │
5. DETECCIÓN DE CONFLICTOS
   ┌─────────────────────────────┐
   │ Si: CRO dice "riesgo crítico│
   │ Y:  CVO dice "core oportun" │
   │                             │
   │ CONFLICTO: Riesgo vs Oportu.│
   └────────────┬────────────────┘
                │
6. SÍNTESIS
   ┌─────────────────────────────┐
   │ Decisión:                   │
   │ ✅ Aprobado con Condiciones │
   │    (resolver conflicto)      │
   └────────────┬────────────────┘
                │
7. REGISTRO
   ┌─────────────────────────────┐
   │ Jarvisz registra:           │
   │ • Reunión #1                │
   │ • Todos los análisis        │
   │ • Conflicto detectado       │
   │ • Especialista propuesto    │
   │ • Decisión tomada           │
   └────────────┬────────────────┘
                │
8. REPORTE
   ┌─────────────────────────────┐
   │ Salida:                     │
   │ {                           │
   │   "reunion_id": 1,          │
   │   "decision": "Aprobado...", │
   │   "conflictos": [...],      │
   │   "especialistas": [...]    │
   │ }                           │
   └─────────────────────────────┘
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
agentes-autonomos-directorio/
│
├── 📂 directorio/
│   └── 📂 prompts/
│       ├── CEO_prompt.md        ← Prompt "Visión global"
│       ├── CRO_prompt.md        ← Prompt "Paranoia"
│       ├── CVO_prompt.md        ← Prompt "Diferencial"
│       ├── COO_prompt.md        ← Prompt "Ejecución"
│       ├── CFO_prompt.md        ← Prompt "Números"
│       └── JARVISZ_prompt.md    ← Prompt "Observador"
│
├── 📂 infraestructura/
│   ├── 📂 api/
│   │   └── server.py            ← API FastAPI para reuniones
│   ├── 📂 db/
│   │   ├── models.py            ← Modelos SQLAlchemy (4 tablas)
│   │   └── jarvisz.db           ← Base de datos SQLite
│   ├── 📂 loggers/
│   │   └── jarvisz_logger.py    ← Logger + detección patrones
│   └── orquestador.py           ← 🎯 ORQUESTADOR CENTRAL
│
├── 📂 tests/
│   └── primera_reunion_test.py  ← Test de reunión (funciona)
│
├── ejecutar_reunion.py          ← CLI para ejecutar reuniones
│
├── ORQUESTADOR.md              ← Documentación completa
├── ARQUITECTURA_SISTEMA.md     ← Este archivo
└── README.md                    ← Índice general
```

---

## 🚀 CÓMO EJECUTAR

### Opción 1: CLI (Desde terminal)
```bash
# Ejecutar una reunión
python ejecutar_reunion.py \
  --tema "Análisis de Sicologa" \
  --contexto "Plataforma telemedicina psicológica..."

# Ver reporte diario
python ejecutar_reunion.py --reporte
```

### Opción 2: API (Desde servidor web)
```bash
# Iniciar servidor
python infraestructura/api/server.py

# Hacer request
curl -X POST http://localhost:8000/api/v1/reuniones \
  -H "Content-Type: application/json" \
  -d '{"tema": "...", "analisis": [...]}'
```

### Opción 3: Programáticamente (En código)
```python
from infraestructura.orquestador import Orquestador

orq = Orquestador()
resultado = orq.ejecutar_reunion("Mi tema", "Mi contexto")
print(resultado["decision"])
```

---

## 🔑 PUNTOS CLAVE

✅ **Cada agente piensa de forma autónoma**
- Recibe el prompt de su rol
- Recibe el contexto del tema
- Claude API genera análisis único
- NO es un chatbot preprogramado

✅ **Los agentes se confrontan (sana tensión)**
- CRO vs CVO → Riesgos vs Oportunidades
- COO vs CFO → Timeline vs Presupuesto
- El orquestador detecta conflictos

✅ **Todo queda registrado y analizado**
- Jarvisz ve cada reunión
- Detecta patrones recurrentes
- Propone especialistas

✅ **Escalable a más agentes**
- Agregar un nuevo rol = agregar un nuevo prompt
- El orquestador lo integra automáticamente

---

## 🎯 PRÓXIMOS PASOS

1. ✅ Orquestador básico → Implementado
2. ✅ Jarvisz Logger → Implementado
3. ✅ API FastAPI → Implementada
4. ⏳ Dashboard visual (React)
5. ⏳ Feedback loop (usuario rechaza decisión)
6. ⏳ Integración Slack/Email
7. ⏳ ML para mejorar síntesis

---

**Status**: 🚀 ARQUITECTURA COMPLETADA
**Versión**: 1.0.0
**Última actualización**: 2026-03-01
