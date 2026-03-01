# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

---

## 📌 CONTEXTO

**Agentes Autónomos - Sistema de Directorio Empresarial**

Sistema de agentes IA multi-rol que simula una empresa real:
- **Directorio Ejecutivo** (C-Level): CEO, CRO, CVO, COO, CFO, Jarvisz
- **Departamento de Estructuras** (Técnico): Arquitectos, Engineers, Researchers
- **Proyectos Paralelos** (GTM Squads): Equipos de Go-to-Market por nicho

---

## 🏗️ ESTRUCTURA

```
directorio/
├── prompts/          [CRÍTICO] Prompts de cada rol
│   ├── CEO_prompt.md
│   ├── CRO_prompt.md
│   ├── CVO_prompt.md
│   ├── COO_prompt.md
│   ├── CFO_prompt.md
│   └── JARVISZ_prompt.md
└── logs/             Registros de reuniones

departamento-estructuras/   [PRÓXIMO]
proyectos/                  [PRÓXIMO]
infraestructura/            Backend & DB
```

---

## 🎯 FASE 1: DIRECTORIO EJECUTIVO

✅ Completada:
- 5 prompts C-Level (CEO, CRO, CVO, COO, CFO)
- 1 prompt Jarvisz (data warehouse)
- Estructura base

⏳ Próximos:
- Sistema de logging de Jarvisz (SQLite)
- API para ejecutar reuniones
- Primera reunión test sobre Sicologa

---

## 📋 CONCEPTOS CLAVE

**Datos por Nivel de Severidad:**
- 🔴 CRÍTICO: Bloquea decisión
- 🟡 IMPORTANTE: Mejora análisis
- 🟢 NICE-TO-HAVE: Para próxima vez

**Regla de Especialistas:**
- Solo se sugieren si patrón en 2+ reuniones
- Y ha bloqueado decisión
- Validado por CFO (ROI)

**Patrones de Razonamiento:**
- Jarvisz documenta cómo piensa cada agente
- Detecta patrones recurrentes
- Reporta evolución en el tiempo

---

**Status**: 🚀 Phase 1 In Development
**Última actualización**: 2026-02-28
