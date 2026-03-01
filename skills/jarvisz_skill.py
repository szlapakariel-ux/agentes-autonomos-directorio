"""
JARVISZ - Escribano / Data Warehouse Central
NO opina. Solo registra, detecta patrones, reporta.
"""

import logging
from typing import Dict, List, Optional, Any

from infraestructura.security.agent_sandbox import AgentSandbox, Capability
from infraestructura.loggers.jarvisz_logger import JarvisZLogger

logger = logging.getLogger(__name__)


class JARVISZSkill:
    """
    Jarvisz no llama a la API de Claude.
    Solo registra en DB, detecta patrones y genera reportes.
    Es el guardián silencioso.
    """

    agent_name = "JARVISZ"

    def __init__(self, db_path: str = "./infraestructura/db/jarvisz.db"):
        self.sandbox = AgentSandbox("JARVISZ")
        self.db = JarvisZLogger(db_path)

    def registrar(
        self,
        tema: str,
        analisis_agentes: Dict[str, str],
        datos_criticos: Optional[List[Dict]] = None,
        datos_importantes: Optional[List[Dict]] = None,
        decision: Optional[str] = None,
        tareas: Optional[List[Dict]] = None,
    ) -> int:
        """
        Registra una reunión completa en la base de datos.
        Retorna el ID de la reunión.
        """
        self.sandbox.check(Capability.WRITE_MEETINGS)

        reunion_id = self.db.registrar_reunion(
            tema=tema,
            ceo_analisis=analisis_agentes.get("CEO"),
            cro_analisis=analisis_agentes.get("CRO"),
            cvo_analisis=analisis_agentes.get("CVO"),
            coo_analisis=analisis_agentes.get("COO"),
            cfo_analisis=analisis_agentes.get("CFO"),
            datos_criticos=datos_criticos or [],
            datos_importantes=datos_importantes or [],
            decision=decision,
            tareas=tareas or [],
        )

        self.sandbox.record_action(
            Capability.WRITE_DATABASE,
            details=f"Reunión #{reunion_id} registrada — {tema[:50]}"
        )

        logger.info(f"JARVISZ: Reunión #{reunion_id} registrada")
        return reunion_id

    def reporte_diario(self) -> Dict[str, Any]:
        """Genera reporte diario sin llamar a Claude API"""
        self.sandbox.check(Capability.READ_DATABASE)
        return self.db.generar_reporte_diario()

    def proponer_especialista(
        self,
        nombre: str,
        especialidad: str,
        justificacion: str,
    ) -> int:
        """Propone especialista basado en patrón detectado"""
        self.sandbox.check(Capability.PROPOSE_SPECIALIST)
        esp_id = self.db.proponer_especialista(nombre, especialidad, justificacion)
        logger.info(f"JARVISZ: Especialista '{nombre}' propuesto (ID: {esp_id})")
        return esp_id
