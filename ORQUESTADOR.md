# 🤖 ORQUESTADOR - Agentes Autónomos Ejecutivos

## ¿Cómo funciona la transformación de prompts a agentes autónomos?

### Concepto Central

Un **agente autónomo** es una instancia de Claude que:
1. **Carga un rol específico** (CEO, CRO, CVO, COO, CFO)
2. **Recibe contexto** sobre un tema/proyecto
3. **Piensa de forma independiente** desde su perspectiva única
4. **Genera análisis fundamentado** basado en su mentalidad de rol
5. **Solicita datos específicos** que necesita para decidir
6. **Participa en coordina­ción** con otros agentes

---

## 🏗️ ARQUITECTURA

```
┌─────────────────────────────────────────────────────┐
│           ORQUESTADOR (Coordinador Central)          │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
    ┌───▼──┐      ┌───▼──┐      ┌──▼────┐
    │ CEO  │      │ CRO  │      │ CVO   │
    │      │      │      │      │       │
    │Piensa│      │Analiza│     │Busca  │
    │globalmente  │riesgos│     │opor-  │
    │            │        │     │tunida│
    └───┬──┘      └───┬──┘      └──┬────┘
        │             │             │
        │             │             │
    ┌───▼──┐      ┌───▼──┐      ┌──▼────┐
    │ COO  │      │ CFO  │      │JARVISZ│
    │      │      │      │      │       │
    │Planes│      │Numeros│     │Registra│
    │tiempo│      │números│     │TODO   │
    └──────┘      └──────┘      └───────┘

    ↓ Cada agente usa Claude API ↓

┌──────────────────────────────────┐
│    Claude 3.5 Sonnet (6 veces)   │
│  Cada una es una instancia única │
│  con su propia "personalidad"    │
└──────────────────────────────────┘
        ↓ Resultados ↓
    ┌───────────────────┐
    │ Jarvisz Logger    │
    │ (SQLite)          │
    │ Registra TODO     │
    └───────────────────┘
```

---

## 🔄 FLUJO DE UNA REUNIÓN

### Paso 1: Iniciación
```python
orquestador = Orquestador()  # Carga los 6 prompts
reunion = orquestador.ejecutar_reunion(
    tema="Validación de Sicologa",
    contexto="Startup de telemedicina psicológica..."
)
```

### Paso 2: Análisis Autónomo
Cada agente recibe:
```
SISTEMA (Prompt del rol):
"Eres CRO. Tu misión: Encontrar el punto de quiebre de cualquier idea.
Analiza riesgos 🔴 CRÍTICO, 🟡 ALTO, 🟢 MEDIO..."

USUARIO:
"TEMA: Validación de Sicologa
[contexto sobre el proyecto]
Proporciona tu análisis desde la perspectiva de CRO."

↓ Claude piensa de forma autónoma ↓

RESPUESTA:
"VEREDICTO: Aprobado con condiciones
RIESGOS CRÍTICOS:
1. Regulación de telemedicina (varía por país)
2. Privacidad de datos de salud (HIPAA, GDPR)
..."
```

### Paso 3: Recolección
Orquestador recolecta 6 análisis:
- `CEO`: Visión global, viabilidad estratégica
- `CRO`: Riesgos y condiciones de aprobación
- `CVO`: Oportunidades y diferencial competitivo
- `COO`: Timeline, recursos, plan de ejecución
- `CFO`: Números, ROI, presupuesto
- `JARVISZ`: Observa TODO, documenta patrones

### Paso 4: Síntesis
```python
if not conflictos:
    decision = "✅ APROBADO"
elif conflictos_altos:
    decision = "⚠️ APROBADO CON CONDICIONES"
else:
    decision = "✅ APROBADO con mitigaciones"
```

### Paso 5: Registro en Jarvisz
```
TABLA: reuniones
- ID, Fecha, Tema
- Análisis de cada agente
- Datos que pidieron (por severidad)
- Decisión final
- Tareas asignadas

TABLA: patrones
- ¿CRO siempre prioriza riesgos legales?
- ¿CVO busca diferencial injusto primero?
- Frecuencia de aparición

TABLA: datos_faltantes
- Qué información necesitan para decidir
- Severidad (CRÍTICO, IMPORTANTE, NICE-TO-HAVE)
- Estado (resuelto/pendiente)

TABLA: especialistas
- Quién propone especialista (basado en patrón)
- Validación por CFO
- ROI estimado
```

---

## 🧠 ¿Cómo piensa un agente autónomo?

### Ejemplo: CRO Analizando Sicologa

**Paso 1: Inyección de rol (Prompt)**
```markdown
# 🛡️ CRO - CHIEF RISK OFFICER
## Abogado del Diablo

Tu misión: Encontrar el punto de quiebre de cualquier idea.

## PROTOCOLO
1. ANÁLISIS ESTRUCTURADO
   - 🔴 CRÍTICO (Bloquea la decisión)
   - 🟡 ALTO (Requiere plan de mitigación)
   - 🟢 MEDIO (Monitorear)

2. DATOS QUE NECESITO
   - 🔴 CRÍTICO (sin esto NO voto)
   - 🟡 IMPORTANTE (mejora análisis)
   - 🟢 NICE-TO-HAVE (anoto para después)
```

**Paso 2: Contexto del Proyecto**
```
TEMA: Sicologa - Plataforma de telemedicina psicológica
- Mercado: América Latina
- Presupuesto: $500K
- Timeline: 12 semanas
- Usuarios objetivo: Personas con ansiedad/depresión
```

**Paso 3: Claude procesa y responde COMO CRO**
```
VEREDICTO: Aprobado con condiciones

RIESGOS CRÍTICOS:
1. 🔴 Regulación de telemedicina
   - Varía MUCHO por país (México vs Colombia vs Perú)
   - Requiere licencias médicas
   - Sin esto, no podemos operar legalmente

2. 🔴 Privacidad de datos de salud
   - HIPAA (USA), GDPR (EU), pero ¿LATAM?
   - Los datos de salud mental son ultra-sensibles
   - Una breach = juicio + cierre regulatorio

3. 🟡 Licencias de psicólogos
   - ¿Son válidas las licencias de México en Colombia?
   - Requiere actualización por país

DATOS QUE NECESITO (SIN ESTOS NO VOTO):
🔴 CRÍTICO:
   - Mapa regulatorio por país (telemedicina legal)
   - Plan de cumplimiento HIPAA/GDPR por país
   - Validación de licencias con regulador

🟡 IMPORTANTE:
   - Análisis de competencia regulatoria
   - Seguros para cobertura de liability médica

🟢 NICE-TO-HAVE:
   - Histórico de regulación en startups similares

CONDICIONES DE APROBACIÓN:
1. Comisionar análisis legal profundo antes de MVP
2. Implementar compliance by design (no add-on)
3. Presupuesto para abogada especialista
```

**Paso 4: Orquestador extrae "datos solicitados"**
- CRÍTICO: 3 datos (regulación, compliance, licencias)
- IMPORTANTE: 2 datos
- NICE-TO-HAVE: 1 dato

---

## 🤝 ¿Cómo interactúan los agentes?

### Conflicto: CRO vs CVO

**CRO dice:**
```
🔴 CRÍTICO: Regulación de telemedicina es bloqueante
Riesgo de cierre regulatorio = $500K perdidos
```

**CVO dice:**
```
🔴 CORE: "Psicología asequible para generación digital"
Este es el diferencial que nadie más ofrece
Riesgo < Oportunidad
```

**Orquestador detecta el conflicto:**
```python
if "riesgo crítico" in cro_analysis and "core" in cvo_analysis:
    conflictos.append({
        "tipo": "Riesgo vs Oportunidad",
        "entre": "CRO vs CVO",
        "severidad": "Alta"
    })
```

**Síntesis:**
```
✅ APROBADO CON CONDICIONES:
   Resolver conflicto CRO/CVO:
   Proceder CON análisis legal profundo (mitiga CRO)
   MANTENIENDO diferencial (respeta CVO)
```

---

## 📊 Ejemplo Completo: Reunión sobre Sicologa

```bash
python ejecutar_reunion.py \
  --tema "Sicologa: Plataforma de telemedicina" \
  --contexto "Startup conecta usuarios con psicólogos. América Latina. $500K."
```

**Output:**

```
======================================================================
🎯 EJECUTANDO REUNIÓN: Sicologa: Plataforma de telemedicina
======================================================================

📋 Fase 1: Análisis de agentes...
  → CEO analizando... ✓
  → CRO analizando... ✓
  → CVO analizando... ✓
  → COO analizando... ✓
  → CFO analizando... ✓

🔍 Fase 2: Detectando conflictos...
  ⚠️ 1 conflicto(s) detectado(s)

✅ Fase 3: Sintetizando decisión...

💾 Fase 4: Registrando en Jarvisz...
  ✓ Reunión 1 registrada

🎓 Fase 5: Evaluando especialistas emergentes...

======================================================================
📊 RESUMEN DE REUNIÓN #1
======================================================================

📌 Tema: Sicologa: Plataforma de telemedicina
📅 Fecha: 2026-03-01T04:30:00

✅ DECISIÓN:
⚠️ APROBADO CON CONDICIONES: Resolver conflictos de riesgo vs
   oportunidad antes de ejecutar.

⚠️ CONFLICTOS DETECTADOS (1):
   • Riesgo vs Oportunidad (CRO vs CVO): CRO ve riesgos críticos
     que CVO considera oportunidades core

📋 DATOS SOLICITADOS:
   CRÍTICO (3):
     - CRO: Mapa de regulación por país (telemedicina)
     - CRO: Cumplimiento HIPAA/GDPR por país
     - CFO: Proyección financiera (3 escenarios)

   IMPORTANTE (2):
     - CVO: Análisis de diferencial vs competencia
     - COO: Timeline detallado por fase

🎓 ESPECIALISTAS PROPUESTOS (1):
   • Especialista Legal en Regulación

======================================================================
```

---

## 🔧 API de Uso

### 1. Ejecutar reunión programáticamente

```python
from infraestructura.orquestador import Orquestador

orq = Orquestador()

resultado = orq.ejecutar_reunion(
    tema="Mi proyecto",
    contexto="Descripción del proyecto...",
    datos_previos={"clientes": 100, "revenue": "$50K"}
)

print(resultado["decision"])
print(resultado["conflictos"])
print(resultado["especialistas_propuestos"])
```

### 2. Usar vía CLI

```bash
# Ejecutar reunión
python ejecutar_reunion.py \
  --tema "Validación de Mercado" \
  --contexto "Context here..." \
  --output resultado.json

# Ver reporte diario
python ejecutar_reunion.py --reporte

# Usar DB personalizado
python ejecutar_reunion.py \
  --tema "Mi tema" \
  --db-path "./custom/db/path.db"
```

### 3. Usar vía API FastAPI

```bash
# Iniciar servidor
python infraestructura/api/server.py

# Ejecutar reunión vía API
curl -X POST http://localhost:8000/api/v1/reuniones \
  -H "Content-Type: application/json" \
  -d '{
    "tema": "Sicologa",
    "analisis": [...]
  }'

# Ver reporte
curl http://localhost:8000/api/v1/reportes/diario
```

---

## 🎯 Próximos Pasos

- [ ] Ejecutar orquestador con tema real
- [ ] Validar que patrones se detectan correctamente
- [ ] Agregar feedback loop (si usuario rechaza decisión → explicar por qué)
- [ ] Crear dashboard visual de reuniones
- [ ] Integrar con Slack/email para notificaciones
- [ ] Machine learning para mejorar síntesis de decisiones

---

**Status**: ✅ Orquestador Implementado
**Última actualización**: 2026-03-01
