"""
CAPA 4: SECRETS MANAGEMENT
Encriptación y acceso seguro a credenciales
"""

import os
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Gestiona credenciales de forma segura.
    Nunca expone valores en logs o errores.
    """

    def __init__(self):
        raw_key = os.getenv("CIPHER_KEY")

        if not raw_key:
            # En desarrollo: generar clave temporal (nunca en producción)
            if os.getenv("ENVIRONMENT", "development") == "development":
                raw_key = Fernet.generate_key().decode()
                logger.warning(
                    "⚠️  CIPHER_KEY no configurada. Usando clave temporal. "
                    "Configura CIPHER_KEY en .env.security para producción."
                )
            else:
                raise EnvironmentError(
                    "CIPHER_KEY no configurada. "
                    "El sistema no puede iniciar sin encriptación."
                )

        try:
            self._cipher = Fernet(raw_key.encode())
        except Exception:
            raise ValueError("CIPHER_KEY inválida. Debe ser una clave Fernet válida.")

    def get(self, key: str) -> Optional[str]:
        """
        Obtiene secreto desencriptado.

        Busca primero en env ENCRYPTED_<KEY>,
        luego en env <KEY> (para desarrollo).
        """
        # Primero buscar versión encriptada
        encrypted_value = os.getenv(f"ENCRYPTED_{key}")
        if encrypted_value:
            try:
                return self._cipher.decrypt(encrypted_value.encode()).decode()
            except InvalidToken:
                logger.error(f"No se pudo desencriptar {key} — token inválido")
                return None

        # Fallback: valor plano en env (solo desarrollo)
        plain_value = os.getenv(key)
        if plain_value:
            if os.getenv("ENVIRONMENT") == "production":
                logger.critical(
                    f"⚠️ SECRET '{key}' está en texto plano en producción. "
                    "Encripta con secrets_manager.store() urgente."
                )
            return plain_value

        return None

    def store(self, key: str, value: str) -> None:
        """
        Encripta y guarda secreto en variable de entorno.
        """
        encrypted = self._cipher.encrypt(value.encode()).decode()
        os.environ[f"ENCRYPTED_{key}"] = encrypted
        logger.info(f"Secret '{key}' almacenado de forma encriptada.")

    def rotate(self, key: str, new_value: str) -> None:
        """Rota (reemplaza) un secreto"""
        self.store(key, new_value)
        logger.info(f"Secret '{key}' rotado exitosamente.")

    @staticmethod
    def generate_key() -> str:
        """Genera una nueva clave Fernet segura"""
        return Fernet.generate_key().decode()


# Instancia global (lazy init)
_secrets_manager: Optional[SecretsManager] = None


def get_secrets() -> SecretsManager:
    """Obtiene la instancia global del secrets manager"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager
