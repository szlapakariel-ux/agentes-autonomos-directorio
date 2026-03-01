"""
CAPA 2: VALIDACIÓN DE ENTRADA
Previene prompt injection, XSS, y otros ataques
"""

import re
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Valida y sanitiza inputs para prevenir injection attacks"""

    # Patrones peligrosos que pueden indicar intentos de ataque
    DANGEROUS_PATTERNS = [
        # Code injection
        r"(?i)(bash|sh|shell|exec|system|__import__|eval|compile)",
        r"(?i)(subprocess|popen|spawn|fork)",
        # SQL injection (aunque usamos ORM, es buena práctica)
        r"(?i)(drop\s+table|delete\s+from|truncate|exec|xp_)",
        # File operations
        r"(?i)(open\(|read\(|write\(|rm\s+-|rmdir)",
        # Import statements
        r"(?i)(import\s+os|from\s+os|import\s+sys|from\s+sys)",
    ]

    # Patrones que indican jailbreak attempts
    JAILBREAK_PATTERNS = [
        r"(?i)(ignore.*your.*instruction|forget.*your.*prompt)",
        r"(?i)(disregard.*security|override.*constraint)",
        r"(?i)(pretend.*you.*are|act.*as.*if)",
        r"(?i)(don't.*follow|don't.*obey)",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
    ]

    # Límites
    MAX_PROMPT_LENGTH = 5000
    MAX_CONTEXT_LENGTH = 20000
    MAX_TOKENS_PER_REQUEST = 10000
    MAX_OUTPUT_LENGTH = 50000

    @classmethod
    def validate_prompt(cls, prompt: str) -> Tuple[bool, str]:
        """
        Valida un prompt para prevenir injection y ataques

        Args:
            prompt: Texto del prompt

        Returns:
            (is_valid, error_message)
        """

        if not prompt or not isinstance(prompt, str):
            return False, "Prompt inválido o vacío"

        # 1. Revisar longitud
        if len(prompt) > cls.MAX_PROMPT_LENGTH:
            return False, f"Prompt demasiado largo (máx {cls.MAX_PROMPT_LENGTH} chars)"

        # 2. Revisar patrones peligrosos
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, prompt):
                logger.warning(f"Patrón peligroso detectado en prompt: {pattern}")
                return False, "Patrón sospechoso detectado en el prompt"

        # 3. Revisar XSS
        for xss_pattern in cls.XSS_PATTERNS:
            if re.search(xss_pattern, prompt, re.IGNORECASE):
                return False, "Intento de XSS/HTML injection detectado"

        # 4. Revisar jailbreak attempts
        for jailbreak_pattern in cls.JAILBREAK_PATTERNS:
            if re.search(jailbreak_pattern, prompt):
                logger.critical(f"Intento de jailbreak detectado")
                return False, "Intento de ignorar instrucciones de seguridad detectado"

        # 5. Revisar null bytes (bypass tricks)
        if "\x00" in prompt:
            return False, "Null bytes detectados"

        # 6. Revisar combinaciones sospechosas
        if cls._check_suspicious_combinations(prompt):
            return False, "Combinación de características sospechosas"

        return True, ""

    @classmethod
    def validate_context(cls, context: str) -> Tuple[bool, str]:
        """
        Valida contexto (similar a prompt pero con límite diferente)

        Args:
            context: Texto de contexto

        Returns:
            (is_valid, error_message)
        """

        if len(context or "") > cls.MAX_CONTEXT_LENGTH:
            return False, f"Contexto demasiado largo (máx {cls.MAX_CONTEXT_LENGTH} chars)"

        # Reutilizar validación de prompt
        return cls.validate_prompt(context)

    @classmethod
    def sanitize_output(cls, text: str, agent_name: str) -> str:
        """
        Sanitiza output del agente

        Previene que un agente comprometido/jailbroken
        pueda ejecutar código malicioso

        Args:
            text: Output del agente
            agent_name: Nombre del agente que lo generó

        Returns:
            Texto sanitizado
        """

        if not text:
            return ""

        # Patrones que NO queremos en output
        dangerous_outputs = [
            (r"(?i)system\(", "system() call"),
            (r"(?i)os\.system", "os.system() call"),
            (r"(?i)subprocess\.", "subprocess call"),
            (r"(?i)exec\(", "exec() call"),
            (r"(?i)eval\(", "eval() call"),
        ]

        for pattern, description in dangerous_outputs:
            if re.search(pattern, text):
                logger.critical(
                    f"Salida peligrosa de {agent_name}: {description}"
                )
                # Remover la línea sospechosa
                text = re.sub(
                    rf".*{pattern[:-1]}.*$",
                    "[CONTENIDO BLOQUEADO POR SEGURIDAD]",
                    text,
                    flags=re.MULTILINE | re.IGNORECASE
                )

        # Limitar longitud de output
        if len(text) > cls.MAX_OUTPUT_LENGTH:
            text = text[:cls.MAX_OUTPUT_LENGTH] + "\n[OUTPUT TRUNCADO POR LÍMITE]"

        return text

    @classmethod
    def _check_suspicious_combinations(cls, text: str) -> bool:
        """
        Detecta combinaciones sospechosas de características

        Ejemplo: "import os" + "system" = potencial ataque
        """

        # Contar características sospechosas
        suspicious_count = 0

        if re.search(r"(?i)import\s+(os|sys)", text):
            suspicious_count += 1
        if re.search(r"(?i)(system|exec|eval|subprocess)", text):
            suspicious_count += 1
        if re.search(r"(?i)(ignore|disregard|override)", text):
            suspicious_count += 1

        # Si hay demasiadas características sospechosas juntas = riesgo
        return suspicious_count >= 2

    @classmethod
    def extract_safe_keywords(cls, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extrae palabras clave seguras del texto

        Útil para logging y análisis sin revelar contenido sensible

        Args:
            text: Texto a extraer de
            max_keywords: Máximo de keywords

        Returns:
            Lista de palabras clave
        """

        # Remover patrones peligrosos primero
        sanitized = text

        for pattern in cls.DANGEROUS_PATTERNS + cls.XSS_PATTERNS:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        # Extraer palabras clave (palabras > 5 chars, alfanuméricas)
        words = re.findall(r"\b\w{5,}\b", sanitized, re.UNICODE)

        # Remover palabras comunes
        stopwords = {"which", "would", "about", "where", "there", "their"}

        filtered = [w for w in words if w.lower() not in stopwords]

        return filtered[:max_keywords]

    @classmethod
    def log_suspicious_input(cls, user_id: str, input_text: str, reason: str):
        """
        Registra input sospechoso para análisis de seguridad

        Args:
            user_id: Usuario que envió
            input_text: Texto sospechoso (primeros 200 chars)
            reason: Razón por la que es sospechoso
        """

        logger.warning(
            f"Input sospechoso de {user_id}: {reason}\n"
            f"Content: {input_text[:200]}"
        )

        # TODO: Enviar a SIEM/security monitoring system


class TextSanitizer:
    """Limpia y normaliza texto"""

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normaliza espacios en blanco"""
        return " ".join(text.split())

    @staticmethod
    def remove_special_chars(text: str, keep_alphanumeric: bool = True) -> str:
        """
        Remueve caracteres especiales

        Args:
            text: Texto a limpiar
            keep_alphanumeric: Si mantener letras y números

        Returns:
            Texto limpio
        """

        if keep_alphanumeric:
            return re.sub(r"[^a-zA-Z0-9\s\-._]", "", text)
        else:
            return re.sub(r"[^a-zA-Z0-9\s]", "", text)

    @staticmethod
    def truncate_safely(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Trunca texto de forma segura

        No corta en medio de palabra

        Args:
            text: Texto a truncar
            max_length: Máxima longitud
            suffix: Sufijo a agregar

        Returns:
            Texto truncado
        """

        if len(text) <= max_length:
            return text

        # Cortar en el último espacio antes del límite
        truncated = text[:max_length].rsplit(" ", 1)[0]

        return truncated + suffix
