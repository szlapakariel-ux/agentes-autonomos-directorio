"""
BASE SKILL - Clase base para todos los agentes ejecutivos
Centraliza: autenticación, sandboxing, validación, logging
"""

import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import anthropic

from infraestructura.security.agent_sandbox import AgentSandbox, Capability
from infraestructura.security.input_validation import InputValidator
from infraestructura.security.secrets import get_secrets

logger = logging.getLogger(__name__)
PROMPTS_DIR = Path("./directorio/prompts")


class BaseSkill(ABC):
    """
    Clase base para todos los agentes ejecutivos.
    Cada subclase representa un rol: CEO, CRO, CVO, COO, CFO, JARVISZ
    """

    # Override en cada subclase
    agent_name: str = "UNKNOWN"
    prompt_file: str = ""

    def __init__(self):
        self.sandbox = AgentSandbox(self.agent_name)
        self.prompt_template = self._load_prompt()
        self._client: Optional[anthropic.Anthropic] = None

    def _load_prompt(self) -> str:
        """Carga el prompt del rol desde archivo"""
        self.sandbox.check(Capability.READ_PROMPTS)
        prompt_path = PROMPTS_DIR / self.prompt_file

        if not prompt_path.exists():
            logger.warning(f"Prompt no encontrado: {prompt_path}")
            return f"Eres {self.agent_name}. Analiza el tema desde tu perspectiva."

        return prompt_path.read_text(encoding="utf-8")

    def _get_client(self) -> anthropic.Anthropic:
        """Obtiene cliente Anthropic con API key del secrets manager"""
        if self._client is None:
            secrets = get_secrets()
            api_key = secrets.get("CLAUDE_API_KEY")
            if not api_key:
                raise EnvironmentError("CLAUDE_API_KEY no configurada")
            self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    def analyze(
        self,
        tema: str,
        contexto: Optional[str] = None,
        datos_previos: Optional[Dict] = None,
    ) -> str:
        """
        Analiza un tema de forma autónoma desde la perspectiva del rol.

        Args:
            tema: Tema a analizar
            contexto: Contexto adicional (opcional)
            datos_previos: Datos de reuniones anteriores (opcional)

        Returns:
            Análisis del agente en formato texto
        """

        # 1. Validar inputs
        valid, error = InputValidator.validate_prompt(tema)
        if not valid:
            raise ValueError(f"Input inválido: {error}")

        if contexto:
            valid, error = InputValidator.validate_context(contexto)
            if not valid:
                raise ValueError(f"Contexto inválido: {error}")

        # 2. Verificar recurso de API
        self.sandbox.check_resources()
        self.sandbox.record_api_call()

        # 3. Construir mensaje de usuario
        user_message = f"TEMA A ANALIZAR: {tema}"
        if contexto:
            user_message += f"\n\nCONTEXTO:\n{contexto}"
        if datos_previos:
            import json
            user_message += f"\n\nDAtos PREVIOS:\n{json.dumps(datos_previos, indent=2, ensure_ascii=False)}"

        user_message += f"\n\nResponde como {self.agent_name}. Sé específico y accionable."

        # 4. Llamar a Claude API
        client = self._get_client()
        response = client.messages.create(
            model=os.getenv("PRIMARY_MODEL", "claude-haiku-4-5-20251001"),
            max_tokens=self.sandbox.limits.get("max_tokens", 1500),
            system=self.prompt_template,
            messages=[{"role": "user", "content": user_message}],
        )

        raw_output = response.content[0].text

        # 5. Sanitizar output
        safe_output = InputValidator.sanitize_output(raw_output, self.agent_name)

        # 6. Registrar acción
        self.sandbox.record_action(
            Capability.WRITE_LOGS,
            details=f"Análisis de tema: {tema[:50]}"
        )

        logger.info(
            f"{self.agent_name} completó análisis. "
            f"API calls: {self.sandbox.api_calls_this_session}"
        )

        return safe_output

    def get_sandbox_summary(self) -> Dict[str, Any]:
        """Resumen de seguridad de la sesión"""
        return self.sandbox.summary()
