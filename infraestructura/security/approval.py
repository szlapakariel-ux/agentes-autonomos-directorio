"""
CAPA 5: HUMAN-IN-THE-LOOP
Acciones sensibles requieren aprobación antes de ejecutarse
"""

import logging
import time
from enum import Enum
from typing import Dict, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class ApprovalLevel(Enum):
    INSTANT = "instant"       # Se ejecuta sin aprobación
    MANUAL = "manual"         # Requiere confirmación humana
    ESCALATION = "escalation" # Requiere aprobación de múltiples roles


# Mapa de acción → nivel requerido
ACTION_APPROVAL: Dict[str, ApprovalLevel] = {
    "send_slack_message":    ApprovalLevel.INSTANT,
    "read_data":             ApprovalLevel.INSTANT,
    "write_log":             ApprovalLevel.INSTANT,
    "send_email":            ApprovalLevel.MANUAL,
    "create_file":           ApprovalLevel.MANUAL,
    "call_external_api":     ApprovalLevel.MANUAL,
    "modify_schedule":       ApprovalLevel.MANUAL,
    "propose_specialist":    ApprovalLevel.MANUAL,
    "delete_data":           ApprovalLevel.ESCALATION,
    "export_data":           ApprovalLevel.ESCALATION,
}

APPROVAL_TIMEOUT_S = int(900)  # 15 minutos


class PendingApproval:
    """Representa una aprobación pendiente"""

    def __init__(
        self,
        approval_id: str,
        action: str,
        agent: str,
        parameters: Dict,
        level: ApprovalLevel,
    ):
        self.approval_id = approval_id
        self.action = action
        self.agent = agent
        self.parameters = parameters
        self.level = level
        self.created_at = time.time()
        self.resolved = False
        self.approved: Optional[bool] = None
        self.resolved_by: Optional[str] = None
        self.resolution_reason: Optional[str] = None

    def is_expired(self) -> bool:
        return not self.resolved and (time.time() - self.created_at) > APPROVAL_TIMEOUT_S

    def approve(self, resolved_by: str, reason: str = ""):
        self.resolved = True
        self.approved = True
        self.resolved_by = resolved_by
        self.resolution_reason = reason

    def reject(self, resolved_by: str, reason: str = ""):
        self.resolved = True
        self.approved = False
        self.resolved_by = resolved_by
        self.resolution_reason = reason


class ApprovalManager:
    """Gestiona el flujo de aprobaciones para acciones sensibles"""

    def __init__(self):
        self._pending: Dict[str, PendingApproval] = {}
        self._notify_fn: Optional[Callable] = None  # Hook para Slack/email

    def set_notifier(self, fn: Callable):
        """
        Registra función de notificación (Slack, email, etc).

        fn(pending: PendingApproval) → None
        """
        self._notify_fn = fn

    def requires_approval(self, action: str) -> ApprovalLevel:
        """Retorna nivel requerido para una acción"""
        return ACTION_APPROVAL.get(action, ApprovalLevel.MANUAL)

    def request(
        self,
        action: str,
        agent: str,
        parameters: Dict,
        timeout: int = APPROVAL_TIMEOUT_S,
    ) -> Dict:
        """
        Solicita aprobación para una acción.

        Si el nivel es INSTANT, aprueba automáticamente.
        Si es MANUAL o ESCALATION, bloquea hasta recibir respuesta
        o hasta que expire el timeout.

        Returns:
            {"approved": bool, "reason": str}
        """
        level = self.requires_approval(action)

        # INSTANT: aprobar sin preguntar
        if level == ApprovalLevel.INSTANT:
            return {"approved": True, "reason": "Acción de bajo riesgo (instant)"}

        # Crear aprobación pendiente
        import secrets as _secrets
        approval_id = _secrets.token_urlsafe(8)

        pending = PendingApproval(
            approval_id=approval_id,
            action=action,
            agent=agent,
            parameters=parameters,
            level=level,
        )
        self._pending[approval_id] = pending

        # Notificar (Slack, log, etc)
        self._send_notification(pending)

        logger.info(
            f"[APPROVAL] #{approval_id} — {agent} quiere '{action}'. "
            f"Esperando aprobación ({level.value}, timeout {timeout}s)..."
        )

        # Esperar respuesta
        deadline = time.time() + timeout
        while time.time() < deadline:
            if pending.resolved:
                break
            time.sleep(2)

        # Timeout
        if not pending.resolved:
            pending.reject("system", "Timeout — no hubo respuesta humana")
            logger.warning(f"[APPROVAL] #{approval_id} expiró sin respuesta")

        result = {
            "approved": pending.approved,
            "approval_id": approval_id,
            "resolved_by": pending.resolved_by,
            "reason": pending.resolution_reason,
        }

        logger.info(
            f"[APPROVAL] #{approval_id} — "
            f"{'APROBADO' if pending.approved else 'RECHAZADO'} "
            f"por {pending.resolved_by}"
        )

        return result

    def resolve(
        self,
        approval_id: str,
        approved: bool,
        resolved_by: str,
        reason: str = "",
    ) -> bool:
        """
        Resuelve una aprobación pendiente (llamado por humano o sistema).

        Returns:
            True si se resolvió, False si no existe o ya expiró
        """
        pending = self._pending.get(approval_id)
        if not pending:
            logger.warning(f"Aprobación #{approval_id} no encontrada")
            return False

        if pending.is_expired():
            logger.warning(f"Aprobación #{approval_id} ya expiró")
            return False

        if approved:
            pending.approve(resolved_by, reason)
        else:
            pending.reject(resolved_by, reason)

        return True

    def list_pending(self) -> list:
        """Lista todas las aprobaciones pendientes (no resueltas, no expiradas)"""
        return [
            {
                "approval_id": p.approval_id,
                "action": p.action,
                "agent": p.agent,
                "level": p.level.value,
                "created_ago_s": round(time.time() - p.created_at),
            }
            for p in self._pending.values()
            if not p.resolved and not p.is_expired()
        ]

    def _send_notification(self, pending: PendingApproval):
        """Envía notificación al notifier registrado"""
        if self._notify_fn:
            try:
                self._notify_fn(pending)
            except Exception as e:
                logger.error(f"Error enviando notificación de aprobación: {e}")
        else:
            # Fallback: solo log
            params_summary = str(pending.parameters)[:200]
            logger.warning(
                f"\n{'='*60}\n"
                f"⚠️  APROBACIÓN REQUERIDA #{pending.approval_id}\n"
                f"   Agente: {pending.agent}\n"
                f"   Acción: {pending.action}\n"
                f"   Nivel:  {pending.level.value}\n"
                f"   Params: {params_summary}\n"
                f"{'='*60}"
            )


# Instancia global
approval_manager = ApprovalManager()
