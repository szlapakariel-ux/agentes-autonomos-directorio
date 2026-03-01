"""
API FastAPI para Agentes Autónomos - Directorio Ejecutivo
Endpoints para ejecutar reuniones y obtener reportes de Jarvisz
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from infraestructura.loggers.jarvisz_logger import JarvisZLogger

# Inicializar logger
jarvisz = JarvisZLogger(
    db_path=os.getenv("JARVISZ_DB_PATH", "./infraestructura/db/jarvisz.db")
)

# Inicializar FastAPI
app = FastAPI(
    title="Agentes Autónomos - Directorio Ejecutivo",
    version="1.0.0",
    description="API para ejecutar reuniones y gestionar agentes IA",
)


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================


class AnalisReunion(BaseModel):
    """Análisis de un agente en una reunión"""

    agente: str  # CEO, CRO, CVO, COO, CFO
    analisis: Optional[str] = None
    datos_pidio: Optional[List[Dict[str, str]]] = None  # [{"dato": "...", "severidad": "..."}]


class DatoFaltante(BaseModel):
    """Dato faltante identificado"""

    agente_solicitante: str
    dato: str
    severidad: str  # CRÍTICO, IMPORTANTE, NICE-TO-HAVE


class Tarea(BaseModel):
    """Tarea asignada en reunión"""

    responsable: str
    tarea: str
    fecha_entrega: Optional[str] = None


class ReunionRequest(BaseModel):
    """Request para crear una reunión"""

    tema: str
    analisis: List[AnalisReunion]
    decision: Optional[str] = None
    tareas: Optional[List[Tarea]] = None
    proxima_reunion_fecha: Optional[str] = None
    proxima_reunion_tema: Optional[str] = None


class ReunionResponse(BaseModel):
    """Response de reunión ejecutada"""

    id: int
    fecha: str
    tema: str
    decision: Optional[str] = None
    tareas: Optional[List[Dict]] = None
    patrones_detectados: List[Dict] = []


class ReporteResponse(BaseModel):
    """Reporte diario de Jarvisz"""

    fecha: str
    resumen: Dict[str, Any]
    alertas: Dict[str, Any]
    patrones_detectados: List[Dict] = []


# ============================================================================
# ENDPOINTS - HEALTH CHECK
# ============================================================================


@app.get("/api/v1/health")
async def health_check():
    """Verifica que el sistema está operativo"""
    return {
        "status": "ok",
        "service": "Agentes Autónomos API",
        "version": "1.0.0",
    }


# ============================================================================
# ENDPOINTS - REUNIONES
# ============================================================================


@app.post("/api/v1/reuniones", response_model=ReunionResponse)
async def crear_reunion(reunion: ReunionRequest):
    """
    Ejecuta una reunión ejecutiva.

    1. Recibe análisis de los 6 agentes
    2. Jarvisz registra TODO
    3. Detecta patrones
    4. Retorna resumen
    """
    try:
        # Procesar análisis de cada agente
        datos_criticos = []
        datos_importantes = []
        datos_nice_to_have = []

        analisis_dict = {a.agente: a.analisis for a in reunion.analisis}

        # Extraer datos por severidad
        for analysis in reunion.analisis:
            if analysis.datos_pidio:
                for dato in analysis.datos_pidio:
                    dato_completo = {
                        "agente": analysis.agente,
                        "dato": dato.get("dato"),
                        "razón": dato.get("razón", ""),
                    }
                    if dato.get("severidad") == "CRÍTICO":
                        datos_criticos.append(dato_completo)
                    elif dato.get("severidad") == "IMPORTANTE":
                        datos_importantes.append(dato_completo)
                    else:
                        datos_nice_to_have.append(dato_completo)

        # Procesar tareas
        tareas_list = None
        if reunion.tareas:
            tareas_list = [
                {
                    "responsable": t.responsable,
                    "tarea": t.tarea,
                    "fecha": t.fecha_entrega,
                }
                for t in reunion.tareas
            ]

        # Registrar reunión en Jarvisz
        reunion_id = jarvisz.registrar_reunion(
            tema=reunion.tema,
            ceo_analisis=analisis_dict.get("CEO"),
            cro_analisis=analisis_dict.get("CRO"),
            cvo_analisis=analisis_dict.get("CVO"),
            coo_analisis=analisis_dict.get("COO"),
            cfo_analisis=analisis_dict.get("CFO"),
            datos_criticos=datos_criticos,
            datos_importantes=datos_importantes,
            datos_nice_to_have=datos_nice_to_have,
            decision=reunion.decision,
            tareas=tareas_list,
            proxima_reunion_fecha=datetime.fromisoformat(reunion.proxima_reunion_fecha)
            if reunion.proxima_reunion_fecha
            else None,
            proxima_reunion_tema=reunion.proxima_reunion_tema,
        )

        # Obtener detalles de la reunión registrada
        reunion_data = jarvisz.obtener_reunion(reunion_id)

        return ReunionResponse(
            id=reunion_id,
            fecha=reunion_data["fecha"],
            tema=reunion_data["tema"],
            decision=reunion_data["decision"],
            tareas=reunion_data["tareas"],
            patrones_detectados=[],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar reunión: {str(e)}")


@app.get("/api/v1/reuniones/{reunion_id}")
async def obtener_reunion(reunion_id: int):
    """Obtiene los detalles completos de una reunión"""
    reunion = jarvisz.obtener_reunion(reunion_id)
    if not reunion:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")
    return reunion


@app.get("/api/v1/reuniones")
async def listar_reuniones(limit: int = 10):
    """Lista las últimas reuniones"""
    reuniones = jarvisz.listar_reuniones(limit)
    return {"reuniones": reuniones}


# ============================================================================
# ENDPOINTS - REPORTES
# ============================================================================


@app.get("/api/v1/reportes/diario", response_model=ReporteResponse)
async def reporte_diario(fecha: Optional[str] = None):
    """Obtiene el reporte diario de Jarvisz"""
    try:
        fecha_obj = datetime.fromisoformat(fecha) if fecha else datetime.utcnow()
        reporte = jarvisz.generar_reporte_diario(fecha_obj)
        return reporte
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")


# ============================================================================
# ENDPOINTS - DATOS FALTANTES
# ============================================================================


@app.post("/api/v1/datos-faltantes")
async def registrar_dato_faltante(dato: DatoFaltante, reunion_id: Optional[int] = None):
    """Registra un dato faltante identificado en reunión"""
    try:
        dato_id = jarvisz.registrar_dato_faltante(
            agente_solicitante=dato.agente_solicitante,
            dato_faltante=dato.dato,
            severidad=dato.severidad,
            reunion_id=reunion_id,
        )
        return {"id": dato_id, "status": "registrado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/datos-faltantes/{dato_id}/resolver")
async def resolver_dato_faltante(
    dato_id: int, como_se_resolvio: str
):
    """Marca un dato faltante como resuelto"""
    try:
        if jarvisz.resolver_dato_faltante(dato_id, como_se_resolvio):
            return {"id": dato_id, "status": "resuelto"}
        else:
            raise HTTPException(status_code=404, detail="Dato faltante no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS - ESPECIALISTAS
# ============================================================================


@app.post("/api/v1/especialistas")
async def proponer_especialista(
    nombre: str,
    especialidad: str,
    justificacion: str,
    patron_id: Optional[int] = None,
):
    """Propone un especialista emergente detectado por patrón"""
    try:
        especialista_id = jarvisz.proponer_especialista(
            nombre=nombre,
            especialidad=especialidad,
            justificacion=justificacion,
            patron_id=patron_id,
        )
        return {"id": especialista_id, "status": "propuesto"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/especialistas/{especialista_id}/validar")
async def validar_especialista(
    especialista_id: int,
    validado: bool,
    roi_estimado: Optional[str] = None,
):
    """CFO valida un especialista propuesto"""
    try:
        if jarvisz.validar_especialista(especialista_id, validado, roi_estimado):
            return {"id": especialista_id, "status": "validado" if validado else "rechazado"}
        else:
            raise HTTPException(status_code=404, detail="Especialista no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS - ESTADO
# ============================================================================


@app.get("/api/v1/directorio/status")
async def directorio_status():
    """Obtiene estado del directorio ejecutivo"""
    return {
        "status": "operativo",
        "agentes": 6,
        "agentes_list": ["CEO", "CRO", "CVO", "COO", "CFO", "JARVISZ"],
        "db": "SQLite",
        "db_path": "./infraestructura/db/jarvisz.db",
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", 8000)),
    )
