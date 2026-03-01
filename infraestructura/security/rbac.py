"""
CAPA 1: CONTROL DE ACCESO BASADO EN ROLES (RBAC)
Define qué puede hacer cada rol
"""

from enum import Enum
from typing import Dict, List, Set


class UserRole(Enum):
    """Roles disponibles en el sistema"""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Permission(Enum):
    """Permisos granulares"""
    # Agentes
    CREATE_AGENT = "create_agent"
    DELETE_AGENT = "delete_agent"
    EXECUTE_AGENT = "execute_agent"
    VIEW_AGENT = "view_agent"

    # Ejecución
    START_HEARTBEAT = "start_heartbeat"
    STOP_HEARTBEAT = "stop_heartbeat"
    VIEW_EXECUTION = "view_execution"

    # Datos
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    DELETE_DATA = "delete_data"
    EXPORT_DATA = "export_data"

    # Aprobaciones
    APPROVE_ACTION = "approve_action"
    REJECT_ACTION = "reject_action"
    VIEW_APPROVALS = "view_approvals"

    # Administración
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_LOGS = "view_logs"
    MANAGE_SETTINGS = "manage_settings"


class RoleBasedAccess:
    """Control de acceso basado en roles"""

    # Definición de permisos por rol
    ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
        UserRole.ADMIN: {
            # Agentes
            Permission.CREATE_AGENT,
            Permission.DELETE_AGENT,
            Permission.EXECUTE_AGENT,
            Permission.VIEW_AGENT,
            # Ejecución
            Permission.START_HEARTBEAT,
            Permission.STOP_HEARTBEAT,
            Permission.VIEW_EXECUTION,
            # Datos
            Permission.READ_DATA,
            Permission.WRITE_DATA,
            Permission.DELETE_DATA,
            Permission.EXPORT_DATA,
            # Aprobaciones
            Permission.APPROVE_ACTION,
            Permission.REJECT_ACTION,
            Permission.VIEW_APPROVALS,
            # Admin
            Permission.MANAGE_USERS,
            Permission.MANAGE_ROLES,
            Permission.VIEW_LOGS,
            Permission.MANAGE_SETTINGS,
        },
        UserRole.OPERATOR: {
            # Agentes
            Permission.EXECUTE_AGENT,
            Permission.VIEW_AGENT,
            # Ejecución
            Permission.VIEW_EXECUTION,
            # Datos
            Permission.READ_DATA,
            Permission.WRITE_DATA,
            # Aprobaciones
            Permission.APPROVE_ACTION,
            Permission.VIEW_APPROVALS,
        },
        UserRole.VIEWER: {
            # Solo lectura
            Permission.VIEW_AGENT,
            Permission.VIEW_EXECUTION,
            Permission.READ_DATA,
            Permission.VIEW_APPROVALS,
        }
    }

    # Acciones que requieren aprobación por rol
    APPROVAL_REQUIRED: Dict[UserRole, Set[str]] = {
        UserRole.ADMIN: set(),  # Admin no necesita aprobación
        UserRole.OPERATOR: {
            "send_email",
            "create_file",
            "external_api_call",
            "modify_schedule",
        },
        UserRole.VIEWER: {
            "any_write_action",  # Viewers no pueden escribir sin aprobación
        }
    }

    @classmethod
    def has_permission(
        cls,
        role: UserRole,
        permission: Permission
    ) -> bool:
        """
        Verifica si un rol tiene un permiso

        Args:
            role: Rol del usuario
            permission: Permiso a verificar

        Returns:
            True si tiene permiso
        """
        permissions = cls.ROLE_PERMISSIONS.get(role, set())
        return permission in permissions

    @classmethod
    def check_permission(
        cls,
        role: UserRole,
        permission: Permission
    ) -> None:
        """
        Verifica permiso, lanza excepción si no lo tiene

        Args:
            role: Rol del usuario
            permission: Permiso a verificar

        Raises:
            PermissionError: Si no tiene permiso
        """
        if not cls.has_permission(role, permission):
            raise PermissionError(
                f"Rol '{role.value}' no tiene permiso para '{permission.value}'"
            )

    @classmethod
    def requires_approval(
        cls,
        role: UserRole,
        action: str
    ) -> bool:
        """
        Verifica si una acción requiere aprobación

        Args:
            role: Rol del usuario
            action: Acción a ejecutar

        Returns:
            True si requiere aprobación
        """
        required_actions = cls.APPROVAL_REQUIRED.get(role, set())
        return action in required_actions

    @classmethod
    def get_role_permissions(cls, role: UserRole) -> List[str]:
        """
        Obtiene lista de permisos para un rol

        Args:
            role: Rol

        Returns:
            Lista de permisos en formato string
        """
        perms = cls.ROLE_PERMISSIONS.get(role, set())
        return [p.value for p in perms]

    @classmethod
    def get_all_roles(cls) -> List[str]:
        """Retorna todos los roles disponibles"""
        return [r.value for r in UserRole]

    @classmethod
    def get_role_description(cls, role: UserRole) -> str:
        """Retorna descripción de un rol"""
        descriptions = {
            UserRole.ADMIN: "Acceso total. Puede crear/eliminar agentes y gestionar usuarios.",
            UserRole.OPERATOR: "Puede ejecutar agentes y aprobar acciones. No puede eliminar.",
            UserRole.VIEWER: "Solo lectura. Puede ver agentes y logs pero no ejecutar.",
        }
        return descriptions.get(role, "Rol desconocido")


class PolicyValidator:
    """Valida políticas de acceso (least privilege, etc)"""

    # Máximo de agentes que puede crear un operator
    MAX_AGENTS_PER_OPERATOR = 5

    # Máximo de ejecuciones por día
    MAX_EXECUTIONS_PER_DAY = {
        UserRole.ADMIN: 1000,
        UserRole.OPERATOR: 100,
        UserRole.VIEWER: 0,
    }

    # Máximo de usuarios que puede crear un admin
    MAX_USERS_PER_ADMIN = 50

    @classmethod
    def validate_resource_limit(
        cls,
        role: UserRole,
        resource_type: str,
        current_count: int
    ) -> bool:
        """
        Valida que usuario no excedió límites de recursos

        Args:
            role: Rol del usuario
            resource_type: Tipo de recurso (agents, executions, users)
            current_count: Cantidad actual

        Returns:
            True si está dentro del límite
        """
        if resource_type == "agents":
            if role == UserRole.OPERATOR:
                return current_count < cls.MAX_AGENTS_PER_OPERATOR
            return True

        if resource_type == "users":
            if role == UserRole.ADMIN:
                return current_count < cls.MAX_USERS_PER_ADMIN
            return False

        return True

    @classmethod
    def validate_execution_quota(
        cls,
        role: UserRole,
        executions_today: int
    ) -> bool:
        """
        Valida que usuario no excedió cuota diaria de ejecuciones

        Args:
            role: Rol del usuario
            executions_today: Número de ejecuciones hoy

        Returns:
            True si está dentro de cuota
        """
        max_allowed = cls.MAX_EXECUTIONS_PER_DAY.get(role, 0)
        return executions_today < max_allowed
