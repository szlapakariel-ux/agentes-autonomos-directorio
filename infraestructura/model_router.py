"""
MODEL ROUTER
Decide automáticamente qué modelo usar por agente:
  - Local (Ollama) si está disponible y configurado
  - Claude API como fallback

Configuración via .env:
  USE_LOCAL_MODELS=True
  OLLAMA_HOST=http://localhost:11434
  DIRECTORIO_MODEL=llama3:70b
  DIRECTORIO_FALLBACK=claude-3-5-sonnet-20241022
"""

import os
import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ModelBackend(Enum):
    CLAUDE  = "claude"
    OLLAMA  = "ollama"


# Mapa agente → modelo local preferido
AGENT_MODEL_MAP = {
    "CEO":     os.getenv("DIRECTORIO_MODEL", "llama3:70b"),
    "CRO":     os.getenv("DIRECTORIO_MODEL", "llama3:70b"),
    "CVO":     os.getenv("DIRECTORIO_MODEL", "llama3:70b"),
    "COO":     os.getenv("DIRECTORIO_MODEL", "llama3:70b"),
    "CFO":     os.getenv("DIRECTORIO_MODEL", "llama3:70b"),
}

# Fallback Claude por agente
AGENT_FALLBACK_MAP = {
    "CEO":     os.getenv("DIRECTORIO_FALLBACK", "claude-haiku-4-5-20251001"),
    "CRO":     os.getenv("DIRECTORIO_FALLBACK", "claude-haiku-4-5-20251001"),
    "CVO":     os.getenv("DIRECTORIO_FALLBACK", "claude-haiku-4-5-20251001"),
    "COO":     os.getenv("DIRECTORIO_FALLBACK", "claude-haiku-4-5-20251001"),
    "CFO":     os.getenv("DIRECTORIO_FALLBACK", "claude-haiku-4-5-20251001"),
}


def _ollama_available() -> bool:
    """Verifica si Ollama está corriendo en localhost"""
    try:
        import httpx
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        r = httpx.get(f"{host}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _ollama_has_model(model: str) -> bool:
    """Verifica si Ollama tiene el modelo descargado"""
    try:
        import httpx
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        r = httpx.get(f"{host}/api/tags", timeout=2)
        models = [m["name"] for m in r.json().get("models", [])]
        return any(model.split(":")[0] in m for m in models)
    except Exception:
        return False


def get_backend(agent_name: str) -> tuple[ModelBackend, str]:
    """
    Decide qué backend y modelo usar para un agente.

    Lógica:
    1. Si USE_LOCAL_MODELS=True Y Ollama disponible Y modelo descargado → Ollama
    2. Caso contrario → Claude API (fallback)

    Returns:
        (backend, model_name)
    """
    use_local = os.getenv("USE_LOCAL_MODELS", "False").lower() == "true"

    if use_local:
        preferred_model = AGENT_MODEL_MAP.get(agent_name, "llama3")

        if _ollama_available():
            if _ollama_has_model(preferred_model):
                logger.info(f"{agent_name} → Ollama ({preferred_model})")
                return ModelBackend.OLLAMA, preferred_model
            else:
                logger.warning(
                    f"{agent_name}: modelo '{preferred_model}' no descargado aún. "
                    f"Usando fallback Claude."
                )
        else:
            logger.warning(
                f"{agent_name}: Ollama no disponible en "
                f"{os.getenv('OLLAMA_HOST', 'localhost:11434')}. "
                f"Usando fallback Claude."
            )

    # Fallback: Claude API
    fallback = AGENT_FALLBACK_MAP.get(agent_name, "claude-haiku-4-5-20251001")
    logger.info(f"{agent_name} → Claude API ({fallback})")
    return ModelBackend.CLAUDE, fallback


def call_model(
    backend: ModelBackend,
    model: str,
    system_prompt: str,
    user_message: str,
    max_tokens: int = 1500,
) -> str:
    """
    Llama al backend correcto con la misma interfaz.

    Args:
        backend:        OLLAMA o CLAUDE
        model:          Nombre del modelo
        system_prompt:  Prompt de sistema (rol del agente)
        user_message:   Mensaje del usuario
        max_tokens:     Máximo de tokens en respuesta

    Returns:
        Respuesta del modelo como texto
    """

    if backend == ModelBackend.OLLAMA:
        return _call_ollama(model, system_prompt, user_message)

    return _call_claude(model, system_prompt, user_message, max_tokens)


def _call_ollama(model: str, system_prompt: str, user_message: str) -> str:
    """Llama a modelo local via Ollama"""
    import ollama

    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    response = ollama.Client(host=host).chat(
        model=model,
        messages=[
            {"role": "system",    "content": system_prompt},
            {"role": "user",      "content": user_message},
        ],
    )

    return response["message"]["content"]


def _call_claude(
    model: str,
    system_prompt: str,
    user_message: str,
    max_tokens: int,
) -> str:
    """Llama a Claude API"""
    import anthropic
    from infraestructura.security.secrets import get_secrets

    api_key = get_secrets().get("CLAUDE_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return response.content[0].text


def list_available_models() -> dict:
    """
    Lista modelos disponibles (local + Claude).
    Útil para debug y verificación.
    """
    result = {
        "ollama_running": _ollama_available(),
        "local_models": [],
        "claude_fallback": list(AGENT_FALLBACK_MAP.values()),
        "agent_preferences": {},
    }

    if result["ollama_running"]:
        try:
            import httpx
            host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            r = httpx.get(f"{host}/api/tags", timeout=2)
            result["local_models"] = [m["name"] for m in r.json().get("models", [])]
        except Exception:
            pass

    for agent, model in AGENT_MODEL_MAP.items():
        backend, resolved_model = get_backend(agent)
        result["agent_preferences"][agent] = {
            "preferred_local": model,
            "resolved_backend": backend.value,
            "resolved_model": resolved_model,
        }

    return result
