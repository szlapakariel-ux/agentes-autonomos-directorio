"""
CAPA 2: RATE LIMITING
Previene DoS attacks y abuso
"""

import time
from collections import defaultdict
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Control de tasas de uso para prevenir abuso y DoS"""

    def __init__(
        self,
        default_limit: int = 100,
        window_seconds: int = 3600
    ):
        """
        Args:
            default_limit: Límite por defecto (requests por ventana)
            window_seconds: Tamaño de ventana de tiempo (1 hora default)
        """

        self.default_limit = default_limit
        self.window_seconds = window_seconds

        # Contador de requests por usuario
        self.requests: Dict[str, list] = defaultdict(list)

        # Límites personalizados por usuario/acción
        self.limits = {
            "user_request": 100,           # 100 requests general
            "heartbeat_execution": 10,     # 10 ejecuciones de heartbeat
            "skill_execution": 50,         # 50 execuciones de skills
            "approval_request": 20,        # 20 solicitudes de aprobación
            "data_export": 5,              # 5 exports de datos
            "api_call": 1000,              # 1000 llamadas API
        }

    def check_rate_limit(
        self,
        user_id: str,
        action: str = "user_request"
    ) -> Tuple[bool, str, Dict]:
        """
        Verifica si usuario excedió límite de tasa

        Args:
            user_id: ID del usuario
            action: Tipo de acción (user_request, skill_execution, etc)

        Returns:
            (is_allowed, message, metadata)
        """

        limit = self.limits.get(action, self.default_limit)
        now = time.time()

        # Limpiar requests viejos (fuera de la ventana)
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window_seconds
        ]

        current_count = len(self.requests[user_id])

        # Verificar límite
        if current_count >= limit:
            reset_time = self.requests[user_id][0] + self.window_seconds

            logger.warning(
                f"Rate limit excedido para {user_id} (acción: {action}). "
                f"{current_count}/{limit} requests"
            )

            metadata = {
                "user_id": user_id,
                "action": action,
                "current_count": current_count,
                "limit": limit,
                "reset_time": reset_time,
                "blocked": True,
            }

            return False, f"Límite de tasa excedido. Reintenta en {reset_time - now:.0f}s", metadata

        # Registrar nuevo request
        self.requests[user_id].append(now)

        # Calcular metrics
        remaining = limit - current_count - 1
        reset_time = max(self.requests[user_id]) + self.window_seconds if self.requests[user_id] else now + self.window_seconds

        metadata = {
            "user_id": user_id,
            "action": action,
            "current_count": current_count + 1,
            "limit": limit,
            "remaining": remaining,
            "reset_time": reset_time,
            "blocked": False,
        }

        return True, "OK", metadata

    def reset_user(self, user_id: str):
        """
        Resetea contador para un usuario
        Útil cuando admin quiere permitir más acceso

        Args:
            user_id: ID del usuario a resetear
        """

        if user_id in self.requests:
            del self.requests[user_id]
            logger.info(f"Rate limit resetado para {user_id}")

    def set_custom_limit(self, user_id: str, action: str, limit: int):
        """
        Establece límite personalizado para un usuario/acción

        Args:
            user_id: ID del usuario
            action: Tipo de acción
            limit: Nuevo límite
        """

        # Guardar límite especial
        key = f"{user_id}:{action}"
        custom_limits = getattr(self, "custom_limits", {})
        custom_limits[key] = limit
        self.custom_limits = custom_limits

        logger.info(f"Límite personalizado para {user_id} (acción: {action}): {limit}")

    def get_user_stats(self, user_id: str) -> Dict:
        """
        Obtiene estadísticas de uso del usuario

        Args:
            user_id: ID del usuario

        Returns:
            Dict con estadísticas
        """

        now = time.time()

        # Limpiar requests viejos
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window_seconds
        ]

        return {
            "user_id": user_id,
            "total_requests": len(self.requests[user_id]),
            "limit": self.default_limit,
            "window_seconds": self.window_seconds,
            "requests": self.requests[user_id],
        }

    def get_all_stats(self) -> Dict:
        """Obtiene estadísticas globales"""

        now = time.time()
        total_users = len(self.requests)
        total_requests = 0

        for requests_list in self.requests.values():
            # Limpiar viejos
            valid = [r for r in requests_list if now - r < self.window_seconds]
            total_requests += len(valid)

        return {
            "total_users": total_users,
            "total_requests": total_requests,
            "window_seconds": self.window_seconds,
            "limit_per_user": self.default_limit,
        }


class AdaptiveRateLimiter(RateLimiter):
    """
    Rate limiter que se adapta basado en comportamiento

    Si un usuario usa responsablemente, puede obtener límites más altos
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reputation = defaultdict(float)  # 0-1 score
        self.violations = defaultdict(int)    # Número de violaciones

    def check_rate_limit_adaptive(self, user_id: str, action: str = "user_request") -> Tuple[bool, str]:
        """
        Verifica límite pero adapta basado en reputación del usuario

        Usuarios con buena reputación obtienen límites más altos
        """

        base_limit = self.limits.get(action, self.default_limit)

        # Multiplicar límite basado en reputación
        reputation_score = self.reputation.get(user_id, 0.5)
        adaptive_limit = int(base_limit * (1 + reputation_score))

        now = time.time()

        # Limpiar requests viejos
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window_seconds
        ]

        current_count = len(self.requests[user_id])

        if current_count >= adaptive_limit:
            self.violations[user_id] += 1
            return False, f"Límite de tasa excedido ({current_count}/{adaptive_limit})"

        # OK, registrar
        self.requests[user_id].append(now)

        # Mejorar reputación si usa responsablemente
        if current_count < adaptive_limit * 0.7:
            self.reputation[user_id] = min(1.0, self.reputation[user_id] + 0.01)

        return True, "OK"

    def penalize_user(self, user_id: str, reason: str):
        """
        Penaliza usuario (reduce reputación)

        Args:
            user_id: Usuario
            reason: Razón de penalización
        """

        self.reputation[user_id] = max(0, self.reputation[user_id] - 0.1)
        self.violations[user_id] += 1

        logger.warning(f"Usuario {user_id} penalizado: {reason}")

    def reward_user(self, user_id: str, reason: str = ""):
        """
        Recompensa usuario (mejora reputación)

        Args:
            user_id: Usuario
            reason: Razón de recompensa
        """

        self.reputation[user_id] = min(1.0, self.reputation[user_id] + 0.05)

        logger.info(f"Usuario {user_id} recompensado: {reason}")
