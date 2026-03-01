"""
CAPA 3: AISLAMIENTO DE AGENTES (SANDBOXING)
Cada agente tiene capabilities explícitas y recursos limitados
"""

import time
import logging
from enum import Enum
from typing import Set, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class Capability(Enum):
    """Capacidades que un agente puede tener (whitelist)"""
    READ_PROMPTS = "read_prompts"
    WRITE_LOGS = "write_logs"
    READ_MEETINGS = "read_meetings"
    WRITE_MEETINGS = "write_meetings"
    SEND_SLACK = "send_slack"
    SEND_EMAIL = "send_email"
    CREATE_FILES = "create_files"
    CALL_EXTERNAL_API = "call_external_api"
    READ_DATABASE = "read_database"
    WRITE_DATABASE = "write_database"
    PROPOSE_SPECIALIST = "propose_specialist"


# Capabilities permitidas por agente (least privilege)
AGENT_CAPABILITIES: Dict[str, Set[Capability]] = {
    "CEO": {
        Capability.READ_PROMPTS,
        Capability.READ_MEETINGS,
        Capability.WRITE_LOGS,
        Capability.PROPOSE_SPECIALIST,
    },
    "CRO": {
        Capability.READ_PROMPTS,
        Capability.READ_MEETINGS,
        Capability.WRITE_LOGS,
        Capability.PROPOSE_SPECIALIST,
    },
    "CVO": {
        Capability.READ_PROMPTS,
        Capability.READ_MEETINGS,
        Capability.WRITE_LOGS,
    },
    "COO": {
        Capability.READ_PROMPTS,
        Capability.READ_MEETINGS,
        Capability.WRITE_LOGS,
        Capability.CREATE_FILES,
    },
    "CFO": {
        Capability.READ_PROMPTS,
        Capability.READ_MEETINGS,
        Capability.WRITE_LOGS,
    },
    "JARVISZ": {
        Capability.READ_PROMPTS,
        Capability.READ_MEETINGS,
        Capability.WRITE_MEETINGS,
        Capability.WRITE_LOGS,
        Capability.READ_DATABASE,
        Capability.WRITE_DATABASE,
        Capability.PROPOSE_SPECIALIST,
    },
}

# Límites de recursos por agente
RESOURCE_LIMITS: Dict[str, Dict] = {
    "CEO":     {"max_time_s": 120, "max_tokens": 1500, "max_api_calls": 3},
    "CRO":     {"max_time_s": 120, "max_tokens": 1500, "max_api_calls": 3},
    "CVO":     {"max_time_s": 120, "max_tokens": 1500, "max_api_calls": 3},
    "COO":     {"max_time_s": 120, "max_tokens": 1500, "max_api_calls": 3},
    "CFO":     {"max_time_s": 120, "max_tokens": 1500, "max_api_calls": 3},
    "JARVISZ": {"max_time_s": 60,  "max_tokens": 500,  "max_api_calls": 1},
}


class SandboxViolation(Exception):
    """Se lanza cuando agente intenta algo fuera de su sandbox"""
    pass


class AgentSandbox:
    """
    Sandbox que controla lo que cada agente puede hacer.
    Todo lo que no esté en la whitelist está BLOQUEADO.
    """

    def __init__(self, agent_name: str):
        if agent_name not in AGENT_CAPABILITIES:
            raise ValueError(f"Agente desconocido: {agent_name}")

        self.agent_name = agent_name
        self.allowed = AGENT_CAPABILITIES[agent_name]
        self.limits = RESOURCE_LIMITS.get(agent_name, {})
        self.execution_log: list = []
        self.api_calls_this_session = 0
        self.session_start = time.time()

    def check(self, capability: Capability) -> None:
        """
        Verifica si agente tiene capability.
        Lanza SandboxViolation si no está en la whitelist.
        """
        if capability not in self.allowed:
            msg = (
                f"[SANDBOX] {self.agent_name} intentó usar '{capability.value}' "
                f"— BLOQUEADO. Capacidades permitidas: "
                f"{[c.value for c in self.allowed]}"
            )
            logger.critical(msg)
            self._log_violation(capability)
            raise SandboxViolation(msg)

    def check_resources(self) -> None:
        """Verifica que no se excedieron límites de recursos"""
        elapsed = time.time() - self.session_start

        if elapsed > self.limits.get("max_time_s", 120):
            raise SandboxViolation(
                f"{self.agent_name} excedió límite de tiempo "
                f"({self.limits['max_time_s']}s)"
            )

        if self.api_calls_this_session > self.limits.get("max_api_calls", 3):
            raise SandboxViolation(
                f"{self.agent_name} excedió límite de API calls "
                f"({self.limits['max_api_calls']})"
            )

    def record_api_call(self) -> None:
        """Registra una API call (contar contra límite)"""
        self.check_resources()
        self.api_calls_this_session += 1
        self.execution_log.append({
            "type": "api_call",
            "count": self.api_calls_this_session,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def record_action(self, capability: Capability, details: Optional[str] = None) -> None:
        """Registra una acción ejecutada (para auditoría)"""
        self.check(capability)
        self.execution_log.append({
            "type": "action",
            "capability": capability.value,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def _log_violation(self, capability: Capability) -> None:
        """Registra violación de sandbox"""
        self.execution_log.append({
            "type": "violation",
            "capability_attempted": capability.value,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def summary(self) -> Dict[str, Any]:
        """Resumen de sesión del agente"""
        return {
            "agent": self.agent_name,
            "session_duration_s": round(time.time() - self.session_start, 2),
            "api_calls": self.api_calls_this_session,
            "actions_logged": len(self.execution_log),
            "violations": sum(1 for e in self.execution_log if e["type"] == "violation"),
        }
