"""
VALIDADOR DE SEGURIDAD
Verifica que toda la configuración de seguridad está en place
Ejecutar antes de cada deploy: python infraestructura/security/validator.py
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List

class SecurityValidator:
    """Valida configuración de seguridad"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Ejecuta todas las validaciones"""

        print("🔒 VALIDANDO CONFIGURACIÓN DE SEGURIDAD...\n")

        self._validate_secrets()
        self._validate_environment()
        self._validate_file_permissions()
        self._validate_encryption()
        self._validate_database()
        self._validate_api()
        self._validate_logging()

        # Mostrar resultados
        self._print_results()

        # Retornar status
        is_secure = len(self.errors) == 0
        return is_secure, self.errors, self.warnings

    def _validate_secrets(self):
        """Valida que secretos están configurados"""

        print("📋 Validando Secrets...")

        secrets_required = [
            "JWT_SECRET_KEY",
            "CIPHER_KEY",
            "ENCRYPTION_KEY",
            "CLAUDE_API_KEY",
        ]

        for secret in secrets_required:
            value = os.getenv(secret)

            if not value:
                self.errors.append(f"❌ {secret} no configurada")
            elif len(value) < 32:
                self.errors.append(f"❌ {secret} demasiado corta (mín 32 chars)")
            else:
                self.passed.append(f"✅ {secret} configurada")

    def _validate_environment(self):
        """Valida variables de ambiente"""

        print("📋 Validando Ambiente...")

        env = os.getenv("ENVIRONMENT", "development")

        if env == "production":
            # En producción, validaciones más estrictas
            if os.getenv("DEBUG", "False").lower() == "true":
                self.errors.append("❌ DEBUG debe ser False en producción")

            if os.getenv("API_HOST", "127.0.0.1") == "0.0.0.0":
                self.errors.append("❌ API_HOST no debe ser 0.0.0.0 en producción")

            if not os.getenv("API_SSL"):
                self.errors.append("❌ SSL/TLS debe estar habilitado en producción")

            self.passed.append("✅ Configuración de producción validada")
        else:
            self.warnings.append("⚠️ Ambiente en desarrollo (no para producción)")

    def _validate_file_permissions(self):
        """Valida permisos de archivos sensibles"""

        print("📋 Validando Permisos de Archivos...")

        sensitive_files = [
            ".env.security",
            "infraestructura/db/jarvisz.db",
            "logs/security_audit.jsonl",
        ]

        for file_path in sensitive_files:
            if os.path.exists(file_path):
                # En Unix: verificar que no es readable por otros
                stat_info = os.stat(file_path)
                mode = stat_info.st_mode

                # Verificar permisos (simplificado para Windows/Unix)
                if mode & 0o077:  # Si otros tienen permisos
                    self.warnings.append(
                        f"⚠️ {file_path} tiene permisos demasiado abiertos"
                    )
                else:
                    self.passed.append(f"✅ {file_path} con permisos restringidos")

    def _validate_encryption(self):
        """Valida que encriptación está configurada"""

        print("📋 Validando Encriptación...")

        try:
            from cryptography.fernet import Fernet

            cipher_key = os.getenv("CIPHER_KEY")
            if cipher_key:
                # Validar que es una key de Fernet válida
                try:
                    Fernet(cipher_key.encode())
                    self.passed.append("✅ Cipher key válida")
                except Exception:
                    self.errors.append("❌ Cipher key inválida (no es Fernet key)")
            else:
                self.errors.append("❌ CIPHER_KEY no configurada")

            # Validar que base de datos encriptada está habilitada
            if os.getenv("JARVISZ_ENCRYPTION") != "true":
                self.warnings.append("⚠️ Encriptación de Jarvisz no habilitada")

        except ImportError:
            self.errors.append("❌ cryptography no instalado (pip install cryptography)")

    def _validate_database(self):
        """Valida configuración de base de datos"""

        print("📋 Validando Base de Datos...")

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            self.errors.append("❌ DATABASE_URL no configurada")
        else:
            self.passed.append("✅ DATABASE_URL configurada")

        # Validar que no usa sqlite en memoria en producción
        if os.getenv("ENVIRONMENT") == "production":
            if ":memory:" in (db_url or ""):
                self.errors.append("❌ No puedes usar SQLite en memoria en producción")

    def _validate_api(self):
        """Valida configuración de API"""

        print("📋 Validando API...")

        # Rate limiting
        rate_limit = os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR")
        if not rate_limit:
            self.warnings.append("⚠️ RATE_LIMIT_REQUESTS_PER_HOUR no configurada")
        else:
            try:
                limit = int(rate_limit)
                if limit < 10:
                    self.errors.append("❌ Rate limit demasiado bajo (mín 10)")
                else:
                    self.passed.append(f"✅ Rate limiting configurado ({limit}/hora)")
            except ValueError:
                self.errors.append("❌ RATE_LIMIT_REQUESTS_PER_HOUR no es número")

        # TLS en producción
        if os.getenv("ENVIRONMENT") == "production":
            if os.getenv("API_SSL") != "true":
                self.errors.append("❌ API debe usar TLS en producción")
            else:
                # Validar certificados
                cert_path = os.getenv("API_SSL_CERT_PATH")
                key_path = os.getenv("API_SSL_KEY_PATH")

                if not os.path.exists(cert_path or ""):
                    self.errors.append(f"❌ Certificado TLS no encontrado: {cert_path}")
                if not os.path.exists(key_path or ""):
                    self.errors.append(f"❌ Key TLS no encontrada: {key_path}")

                if os.path.exists(cert_path or "") and os.path.exists(key_path or ""):
                    self.passed.append("✅ Certificados TLS validados")

    def _validate_logging(self):
        """Valida configuración de logging"""

        print("📋 Validando Logging...")

        log_file = os.getenv("SECURITY_LOG_FILE")
        if not log_file:
            self.warnings.append("⚠️ SECURITY_LOG_FILE no configurada")
        else:
            # Crear directorio si no existe
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            self.passed.append(f"✅ Security logging habilitado: {log_file}")

        # Validar retention
        retention = os.getenv("SECURITY_LOG_RETENTION_DAYS")
        if not retention:
            self.warnings.append("⚠️ SECURITY_LOG_RETENTION_DAYS no configurada")
        else:
            try:
                days = int(retention)
                if days < 30:
                    self.warnings.append(
                        f"⚠️ Retención de logs muy corta ({days} días, recomendado 90+)"
                    )
                else:
                    self.passed.append(f"✅ Log retention: {days} días")
            except ValueError:
                self.errors.append("❌ SECURITY_LOG_RETENTION_DAYS no es número")

    def _print_results(self):
        """Imprime resultados de validación"""

        print("\n" + "=" * 70)
        print("📊 RESULTADOS DE VALIDACIÓN")
        print("=" * 70)

        if self.passed:
            print(f"\n✅ PASSED ({len(self.passed)}):")
            for msg in self.passed:
                print(f"   {msg}")

        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"   {msg}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for msg in self.errors:
                print(f"   {msg}")

        print("\n" + "=" * 70)

        if self.errors:
            print("🔴 SEGURIDAD: FALLÓ - Fix errors antes de deploy")
            return_code = 1
        elif self.warnings:
            print("🟡 SEGURIDAD: ADVERTENCIAS - Revisar antes de producción")
            return_code = 0
        else:
            print("🟢 SEGURIDAD: PASÓ - Listo para deploy")
            return_code = 0

        print("=" * 70 + "\n")
        return return_code


def main():
    """Ejecuta validador"""

    validator = SecurityValidator()
    is_secure, errors, warnings = validator.validate_all()

    # Exit con código apropiado
    sys.exit(0 if is_secure else 1)


if __name__ == "__main__":
    main()
