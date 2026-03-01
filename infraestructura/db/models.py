"""
SQLAlchemy Models para Jarvisz Data Warehouse
Registra: reuniones, patrones, datos_faltantes, especialistas
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Reunion(Base):
    """Registro de cada reunión ejecutiva"""
    __tablename__ = "reuniones"

    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    tema = Column(String(255), nullable=False)

    # Análisis por agente
    ceo_analisis = Column(Text)
    cro_analisis = Column(Text)
    cvo_analisis = Column(Text)
    coo_analisis = Column(Text)
    cfo_analisis = Column(Text)

    # Datos que pidieron (severity level)
    datos_criticos = Column(JSON)  # [{"agente": "CRO", "dato": "...", "razón": "..."}]
    datos_importantes = Column(JSON)
    datos_nice_to_have = Column(JSON)

    # Decisión y tareas
    decision = Column(Text)
    tareas = Column(JSON)  # [{"responsable": "...", "tarea": "...", "fecha": "..."}]

    # Próxima reunión
    proxima_reunion_fecha = Column(DateTime)
    proxima_reunion_tema = Column(String(255))


class Patron(Base):
    """Patrones de razonamiento detectados en agentes"""
    __tablename__ = "patrones"

    id = Column(Integer, primary_key=True)
    fecha_detectado = Column(DateTime, default=datetime.utcnow)
    agente = Column(String(50), nullable=False)  # CEO, CRO, CVO, COO, CFO

    # Patrón identificado
    descripcion = Column(Text, nullable=False)
    ejemplo_reunion = Column(Integer)  # Foreign key a Reunion

    # Frecuencia
    numero_apariciones = Column(Integer, default=1)
    ultima_aparicion = Column(DateTime, default=datetime.utcnow)

    # Impacto
    bloquea_decision = Column(Boolean, default=False)
    recomendacion = Column(Text)


class DatoFaltante(Base):
    """Datos que faltan para decisiones"""
    __tablename__ = "datos_faltantes"

    id = Column(Integer, primary_key=True)
    fecha_reporte = Column(DateTime, default=datetime.utcnow)

    # Quién lo pidió
    agente_solicitante = Column(String(50), nullable=False)
    reunion_id = Column(Integer)  # Foreign key a Reunion

    # Qué falta
    dato_faltante = Column(Text, nullable=False)
    severidad = Column(String(20), nullable=False)  # CRÍTICO, IMPORTANTE, NICE-TO-HAVE

    # Estado
    resuelto = Column(Boolean, default=False)
    fecha_resolucion = Column(DateTime)
    como_se_resolvio = Column(Text)


class Especialista(Base):
    """Especialistas emergentes detectados por patrón"""
    __tablename__ = "especialistas"

    id = Column(Integer, primary_key=True)
    fecha_propuesta = Column(DateTime, default=datetime.utcnow)

    # Especialista
    nombre = Column(String(255), nullable=False)
    especialidad = Column(String(255), nullable=False)

    # Por qué se propone
    patron_id = Column(Integer)  # Foreign key a Patron
    justificacion = Column(Text, nullable=False)

    # Validación
    validado_por_cfo = Column(Boolean, default=False)
    roi_estimado = Column(Text)

    # Implementación
    implementado = Column(Boolean, default=False)
    fecha_implementacion = Column(DateTime)
