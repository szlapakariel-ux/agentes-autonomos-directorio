"""
CAPA 1: AUTENTICACIÓN & AUTORIZACIÓN
JWT + Token rotation para agentes y usuarios
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

# Configuración
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(64))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Gestiona autenticación y autorización con JWT"""

    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire = ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(
        self,
        user_id: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea JWT access token

        Args:
            user_id: ID del usuario
            role: Rol del usuario (admin, operator, viewer)
            expires_delta: Tiempo de expiración personalizado

        Returns:
            Token JWT encriptado
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire)

        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": user_id,
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)  # JWT ID para invalidación
        }

        encoded_jwt = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        return encoded_jwt

    def create_refresh_token(self, user_id: str) -> str:
        """
        Crea JWT refresh token (vive más tiempo)

        Args:
            user_id: ID del usuario

        Returns:
            Refresh token encriptado
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)

        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)
        }

        encoded_jwt = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        return encoded_jwt

    def verify_token(self, token: str) -> Dict:
        """
        Verifica y decodifica JWT token

        Args:
            token: Token a verificar

        Returns:
            Payload del token si es válido

        Raises:
            PermissionError: Si token es inválido o expirado
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            user_id: str = payload.get("sub")
            if user_id is None:
                raise PermissionError("Token inválido: sin user_id")

            return payload

        except JWTError as e:
            raise PermissionError(f"Token inválido: {str(e)}")

    def hash_password(self, password: str) -> str:
        """
        Hashea contraseña con bcrypt

        Args:
            password: Contraseña en texto plano

        Returns:
            Contraseña hasheada
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica contraseña contra hash

        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Contraseña hasheada

        Returns:
            True si coincide
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_current_user(self, token: str) -> Dict:
        """
        Obtiene usuario actual del token

        Args:
            token: JWT token

        Returns:
            Dict con user_id y role
        """
        payload = self.verify_token(token)
        return {
            "user_id": payload.get("sub"),
            "role": payload.get("role"),
            "token_type": payload.get("type")
        }

    def rotate_token(self, token: str) -> str:
        """
        Rota token (invalida el viejo, crea uno nuevo)
        Útil para refresh tokens

        Args:
            token: Token anterior

        Returns:
            Nuevo token
        """
        # Verificar token anterior
        payload = self.verify_token(token)

        # Crear nuevo token con los mismos datos
        return self.create_access_token(
            user_id=payload.get("sub"),
            role=payload.get("role")
        )


class TokenBlacklist:
    """
    Mantiene lista de tokens invalidados
    Usado cuando usuario logout o token es comprometido
    """

    def __init__(self):
        self.blacklist = set()
        self.blacklist_expires = {}  # Guardar JTI con su fecha de expiración

    def add_to_blacklist(self, token: str, jti: str, exp_time: datetime):
        """Agrega token a blacklist"""
        self.blacklist.add(jti)
        self.blacklist_expires[jti] = exp_time

    def is_blacklisted(self, jti: str) -> bool:
        """Verifica si token está en blacklist"""
        if jti not in self.blacklist:
            return False

        # Limpiar expirados
        exp_time = self.blacklist_expires.get(jti)
        if exp_time and datetime.utcnow() > exp_time:
            self.blacklist.discard(jti)
            self.blacklist_expires.pop(jti, None)
            return False

        return True

    def cleanup_expired(self):
        """Limpia tokens expirados de la blacklist"""
        now = datetime.utcnow()
        expired_jtis = [
            jti for jti, exp_time in self.blacklist_expires.items()
            if now > exp_time
        ]

        for jti in expired_jtis:
            self.blacklist.discard(jti)
            self.blacklist_expires.pop(jti, None)


# Instancia global
security_manager = SecurityManager()
token_blacklist = TokenBlacklist()
