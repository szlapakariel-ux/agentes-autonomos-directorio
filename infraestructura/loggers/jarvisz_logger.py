"""
Jarvisz Logger - Observador y Registrador de Reuniones
Registra TODO sin opinar.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import json

from infraestructura.db.models import Base, Reunion, Patron, DatoFaltante, Especialista


class JarvisZLogger:
    """Sistema central de logging y observación de reuniones"""

    def __init__(self, db_path: str = "./infraestructura/db/jarvisz.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def registrar_reunion(
        self,
        tema: str,
        ceo_analisis: Optional[str] = None,
        cro_analisis: Optional[str] = None,
        cvo_analisis: Optional[str] = None,
        coo_analisis: Optional[str] = None,
        cfo_analisis: Optional[str] = None,
        datos_criticos: Optional[List[Dict]] = None,
        datos_importantes: Optional[List[Dict]] = None,
        datos_nice_to_have: Optional[List[Dict]] = None,
        decision: Optional[str] = None,
        tareas: Optional[List[Dict]] = None,
        proxima_reunion_fecha: Optional[datetime] = None,
        proxima_reunion_tema: Optional[str] = None,
    ) -> int:
        """Registra una reunión completa. Retorna ID de la reunión."""
        session = self.Session()
        try:
            reunion = Reunion(
                tema=tema,
                ceo_analisis=ceo_analisis,
                cro_analisis=cro_analisis,
                cvo_analisis=cvo_analisis,
                coo_analisis=coo_analisis,
                cfo_analisis=cfo_analisis,
                datos_criticos=datos_criticos or [],
                datos_importantes=datos_importantes or [],
                datos_nice_to_have=datos_nice_to_have or [],
                decision=decision,
                tareas=tareas or [],
                proxima_reunion_fecha=proxima_reunion_fecha,
                proxima_reunion_tema=proxima_reunion_tema,
            )
            session.add(reunion)
            session.commit()
            reunion_id = reunion.id

            # Detectar patrones después de registrar
            self._detectar_patrones(reunion_id, session)

            return reunion_id
        finally:
            session.close()

    def _detectar_patrones(self, reunion_id: int, session) -> None:
        """Detecta patrones de razonamiento de cada agente"""
        reunion = session.query(Reunion).filter(Reunion.id == reunion_id).first()

        patrones_detectados = []

        # Patrón CRO: ¿siempre prioriza riesgos legales?
        if "riesgo" in (reunion.cro_analisis or "").lower():
            patrones_detectados.append(
                {
                    "agente": "CRO",
                    "descripcion": "Prioriza riesgos (especialmente legales)",
                    "bloquea_decision": "riesgo crítico" in (reunion.cro_analisis or "").lower(),
                }
            )

        # Patrón CVO: ¿busca diferencial injusto primero?
        if "diferencial" in (reunion.cvo_analisis or "").lower() or "narrativa" in (
            reunion.cvo_analisis or ""
        ).lower():
            patrones_detectados.append(
                {
                    "agente": "CVO",
                    "descripcion": "Busca diferencial narrativo/injusto",
                    "bloquea_decision": False,
                }
            )

        # Patrón COO: ¿siempre pide timeline?
        if "timeline" in (reunion.coo_analisis or "").lower() or "plan" in (
            reunion.coo_analisis or ""
        ).lower():
            patrones_detectados.append(
                {
                    "agente": "COO",
                    "descripcion": "Solicita timeline y plan detallado",
                    "bloquea_decision": "timeline crítico" in (reunion.coo_analisis or "").lower(),
                }
            )

        # Patrón CFO: ¿siempre pide números?
        if "número" in (reunion.cfo_analisis or "").lower() or "presupuesto" in (
            reunion.cfo_analisis or ""
        ).lower():
            patrones_detectados.append(
                {
                    "agente": "CFO",
                    "descripcion": "Solicita números y análisis financiero",
                    "bloquea_decision": "presupuesto crítico" in (reunion.cfo_analisis or "").lower(),
                }
            )

        # Guardar patrones
        for patron_data in patrones_detectados:
            # Verificar si ya existe este patrón
            patron_existente = session.query(Patron).filter(
                and_(
                    Patron.agente == patron_data["agente"],
                    Patron.descripcion == patron_data["descripcion"],
                )
            ).first()

            if patron_existente:
                # Incrementar contador
                patron_existente.numero_apariciones += 1
                patron_existente.ultima_aparicion = datetime.utcnow()
            else:
                # Crear nuevo patrón
                patron = Patron(
                    agente=patron_data["agente"],
                    descripcion=patron_data["descripcion"],
                    ejemplo_reunion=reunion_id,
                    bloquea_decision=patron_data["bloquea_decision"],
                )
                session.add(patron)

        session.commit()

    def registrar_dato_faltante(
        self,
        agente_solicitante: str,
        dato_faltante: str,
        severidad: str,  # CRÍTICO, IMPORTANTE, NICE-TO-HAVE
        reunion_id: Optional[int] = None,
    ) -> int:
        """Registra un dato faltante. Retorna ID del registro."""
        session = self.Session()
        try:
            dato = DatoFaltante(
                agente_solicitante=agente_solicitante,
                dato_faltante=dato_faltante,
                severidad=severidad,
                reunion_id=reunion_id,
            )
            session.add(dato)
            session.commit()
            return dato.id
        finally:
            session.close()

    def resolver_dato_faltante(
        self, dato_id: int, como_se_resolvio: str
    ) -> bool:
        """Marca un dato como resuelto."""
        session = self.Session()
        try:
            dato = session.query(DatoFaltante).filter(DatoFaltante.id == dato_id).first()
            if dato:
                dato.resuelto = True
                dato.fecha_resolucion = datetime.utcnow()
                dato.como_se_resolvio = como_se_resolvio
                session.commit()
                return True
            return False
        finally:
            session.close()

    def proponer_especialista(
        self,
        nombre: str,
        especialidad: str,
        justificacion: str,
        patron_id: Optional[int] = None,
    ) -> int:
        """Propone un especialista emergente. Retorna ID."""
        session = self.Session()
        try:
            especialista = Especialista(
                nombre=nombre,
                especialidad=especialidad,
                justificacion=justificacion,
                patron_id=patron_id,
            )
            session.add(especialista)
            session.commit()
            return especialista.id
        finally:
            session.close()

    def validar_especialista(
        self, especialista_id: int, validado: bool, roi_estimado: Optional[str] = None
    ) -> bool:
        """CFO valida un especialista propuesto."""
        session = self.Session()
        try:
            especialista = session.query(Especialista).filter(
                Especialista.id == especialista_id
            ).first()
            if especialista:
                especialista.validado_por_cfo = validado
                especialista.roi_estimado = roi_estimado
                session.commit()
                return True
            return False
        finally:
            session.close()

    def generar_reporte_diario(self, fecha: Optional[datetime] = None) -> Dict[str, Any]:
        """Genera reporte diario del tipo:
        📊 REPORTE - [FECHA]
        🎯 RESUMEN: Reuniones, Decisiones, Datos faltantes críticos
        🚨 ALERTAS: Conflictos, Datos críticos, Especialistas emergentes
        """
        if fecha is None:
            fecha = datetime.utcnow()

        session = self.Session()
        try:
            # Reuniones del día
            reuniones_hoy = session.query(Reunion).filter(
                Reunion.fecha >= fecha.replace(hour=0, minute=0, second=0)
            ).all()

            # Datos faltantes críticos sin resolver
            datos_criticos_sin_resolver = session.query(DatoFaltante).filter(
                and_(
                    DatoFaltante.severidad == "CRÍTICO",
                    DatoFaltante.resuelto == False,
                )
            ).all()

            # Patrones detectados (más de 1 aparición)
            patrones_frecuentes = session.query(Patron).filter(
                Patron.numero_apariciones > 1
            ).all()

            # Especialistas propuestos
            especialistas_emergentes = session.query(Especialista).filter(
                Especialista.implementado == False
            ).all()

            # Detectar conflictos (si dos agentes tienen análisis contradictorios)
            conflictos = self._detectar_conflictos(reuniones_hoy)

            reporte = {
                "fecha": fecha.isoformat(),
                "resumen": {
                    "reuniones": len(reuniones_hoy),
                    "decisiones": sum(1 for r in reuniones_hoy if r.decision),
                    "datos_faltantes_criticos": len(datos_criticos_sin_resolver),
                },
                "alertas": {
                    "conflictos_no_resueltos": conflictos,
                    "datos_criticos_faltantes": [
                        {
                            "dato": d.dato_faltante,
                            "solicitante": d.agente_solicitante,
                            "reunión": d.reunion_id,
                        }
                        for d in datos_criticos_sin_resolver
                    ],
                    "especialistas_emergentes": [
                        {
                            "nombre": e.nombre,
                            "especialidad": e.especialidad,
                            "patrón": e.patron_id,
                            "validado": e.validado_por_cfo,
                        }
                        for e in especialistas_emergentes
                    ],
                },
                "patrones_detectados": [
                    {
                        "agente": p.agente,
                        "descripcion": p.descripcion,
                        "apariciones": p.numero_apariciones,
                        "bloquea_decision": p.bloquea_decision,
                    }
                    for p in patrones_frecuentes
                ],
            }

            return reporte
        finally:
            session.close()

    def _detectar_conflictos(self, reuniones: List[Reunion]) -> List[Dict]:
        """Detecta conflictos entre análisis de agentes"""
        conflictos = []
        for reunion in reuniones:
            # Lógica básica: si hay palabras de conflicto en análisis diferentes
            analisis_list = [
                (reunion.cro_analisis, "CRO"),
                (reunion.cvo_analisis, "CVO"),
                (reunion.coo_analisis, "COO"),
                (reunion.cfo_analisis, "CFO"),
            ]

            for i, (analisis1, agente1) in enumerate(analisis_list):
                for analisis2, agente2 in analisis_list[i + 1 :]:
                    if analisis1 and analisis2:
                        if "riesgo" in analisis1.lower() and "riesgo" not in analisis2.lower():
                            if "oportunidad" in analisis2.lower():
                                conflictos.append(
                                    {
                                        "entre": f"{agente1} vs {agente2}",
                                        "reunion_id": reunion.id,
                                        "tipo": "Riesgo vs Oportunidad",
                                    }
                                )

        return conflictos

    def obtener_reunion(self, reunion_id: int) -> Optional[Dict]:
        """Obtiene los detalles de una reunión"""
        session = self.Session()
        try:
            reunion = session.query(Reunion).filter(Reunion.id == reunion_id).first()
            if reunion:
                return {
                    "id": reunion.id,
                    "fecha": reunion.fecha.isoformat(),
                    "tema": reunion.tema,
                    "ceo_analisis": reunion.ceo_analisis,
                    "cro_analisis": reunion.cro_analisis,
                    "cvo_analisis": reunion.cvo_analisis,
                    "coo_analisis": reunion.coo_analisis,
                    "cfo_analisis": reunion.cfo_analisis,
                    "datos_criticos": reunion.datos_criticos,
                    "decision": reunion.decision,
                    "tareas": reunion.tareas,
                }
            return None
        finally:
            session.close()

    def listar_reuniones(self, limit: int = 10) -> List[Dict]:
        """Lista las últimas reuniones"""
        session = self.Session()
        try:
            reuniones = (
                session.query(Reunion)
                .order_by(Reunion.fecha.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": r.id,
                    "fecha": r.fecha.isoformat(),
                    "tema": r.tema,
                    "decision": r.decision,
                }
                for r in reuniones
            ]
        finally:
            session.close()
