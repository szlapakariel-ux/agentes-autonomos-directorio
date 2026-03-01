"""
BASE SKILL - Clase base para todos los agentes ejecutivos
Centraliza: autenticación, sandboxing, validación, logging
"""

import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

from infraestructura.security.agent_sandbox import AgentSandbox, Capability
from infraestructura.security.input_validation import InputValidator
from infraestructura.security.secrets import get_secrets
from infraestructura.model_router import get_backend, call_model

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

    def _load_prompt(self) -> str:
        """Carga el prompt del rol desde archivo"""
        self.sandbox.check(Capability.READ_PROMPTS)
        prompt_path = PROMPTS_DIR / self.prompt_file

        if not prompt_path.exists():
            logger.warning(f"Prompt no encontrado: {prompt_path}")
            return f"Eres {self.agent_name}. Analiza el tema desde tu perspectiva."

        return prompt_path.read_text(encoding="utf-8")

    def analyze(
        self,
        tema: str,
        contexto: Optional[str] = None,
        datos_previos: Optional[Dict] = None,
    ) -> str:
        """
        Analiza un tema de forma autónoma desde la perspectiva del rol.
        Usa modelo local (Ollama) si está disponible, Claude API como fallback.
        """

        # 1. Validar inputs
        valid, error = InputValidator.validate_prompt(tema)
        if not valid:
            raise ValueError(f"Input inválido: {error}")

        if contexto:
            valid, error = InputValidator.validate_context(contexto)
            if not valid:
                raise ValueError(f"Contexto inválido: {error}")

        # 2. Verificar recursos del sandbox
        self.sandbox.check_resources()
        self.sandbox.record_api_call()

        # 3. Construir mensaje de usuario
        user_message = f"TEMA A ANALIZAR: {tema}"
        if contexto:
            user_message += f"\n\nCONTEXTO:\n{contexto}"
        if datos_previos:
            import json
            user_message += f"\n\nDATOS PREVIOS:\n{json.dumps(datos_previos, indent=2, ensure_ascii=False)}"

        user_message += f"\n\nResponde como {self.agent_name}. Sé específico y accionable."

        # 4. Resolver backend (Ollama local o Claude API)
        backend, model = get_backend(self.agent_name)

        # 5. Llamar al modelo
        raw_output = call_model(
            backend=backend,
            model=model,
            system_prompt=self.prompt_template,
            user_message=user_message,
            max_tokens=self.sandbox.limits.get("max_tokens", 1500),
        )

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
