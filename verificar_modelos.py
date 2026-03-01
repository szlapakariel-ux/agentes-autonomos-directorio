"""
VERIFICADOR DE MODELOS
Muestra qué modelos están disponibles y cuál usará cada agente.
Ejecutar después de instalar Ollama y descargar modelos.

Uso:
    python verificar_modelos.py
    python verificar_modelos.py --activar-local   # Activa Ollama como primario
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from infraestructura.model_router import list_available_models


MODELOS_RECOMENDADOS = {
    "16GB RAM":  {"modelo": "llama3",     "comando": "ollama pull llama3"},
    "32GB+ RAM": {"modelo": "llama3:70b", "comando": "ollama pull llama3:70b"},
    "8GB RAM":   {"modelo": "mistral",    "comando": "ollama pull mistral"},
}


def main():
    parser = argparse.ArgumentParser(description="Verificador de modelos IA")
    parser.add_argument(
        "--activar-local", action="store_true",
        help="Activa USE_LOCAL_MODELS=True en el entorno"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output en formato JSON"
    )
    args = parser.parse_args()

    if args.activar_local:
        import os
        os.environ["USE_LOCAL_MODELS"] = "True"
        print("✅ USE_LOCAL_MODELS=True activado para esta sesión\n")

    estado = list_available_models()

    if args.json:
        print(json.dumps(estado, indent=2))
        return

    # ---- Output visual ----
    print("\n" + "="*60)
    print("🤖 ESTADO DE MODELOS IA")
    print("="*60)

    # Ollama
    if estado["ollama_running"]:
        print("\n✅ Ollama: CORRIENDO")
        if estado["local_models"]:
            print(f"\n📦 Modelos descargados ({len(estado['local_models'])}):")
            for m in estado["local_models"]:
                print(f"   • {m}")
        else:
            print("\n⚠️  Ollama corre pero no hay modelos descargados.")
            print("   Descarga con:")
            for ram, info in MODELOS_RECOMENDADOS.items():
                print(f"   [{ram}]  {info['comando']}")
    else:
        print("\n❌ Ollama: NO DISPONIBLE")
        print(f"   Host: {__import__('os').getenv('OLLAMA_HOST','http://localhost:11434')}")
        print("\n   Para instalar: https://ollama.ai/")
        print("   Para iniciar:  ollama serve")

    # Estado por agente
    print("\n📋 MODELO ASIGNADO POR AGENTE:")
    print("-"*60)

    for agente, info in estado["agent_preferences"].items():
        icon = "🟢" if info["resolved_backend"] == "ollama" else "🔵"
        backend_label = "LOCAL (Ollama)" if info["resolved_backend"] == "ollama" else "Claude API"
        print(f"  {icon} {agente:<8} → {backend_label} ({info['resolved_model']})")
        if info["resolved_backend"] == "claude":
            print(f"           Prefiere local: {info['preferred_local']}")

    # Instrucciones según estado
    print("\n" + "="*60)

    all_local = all(
        v["resolved_backend"] == "ollama"
        for v in estado["agent_preferences"].values()
    )
    any_local = any(
        v["resolved_backend"] == "ollama"
        for v in estado["agent_preferences"].values()
    )

    if all_local:
        print("✅ TODOS LOS AGENTES USANDO MODELOS LOCALES")
        print("   Sin costo de API. Sistema completamente autónomo.")
    elif any_local:
        print("🟡 SISTEMA HÍBRIDO (parte local, parte Claude API)")
    else:
        print("🔵 TODOS LOS AGENTES USANDO CLAUDE API (fallback)")
        print("\n   Para activar modelos locales:")
        print("   1. Instala Ollama: https://ollama.ai/")
        print("   2. Inicia Ollama: ollama serve")
        print("   3. Descarga un modelo:")
        print("      ollama pull llama3        (16GB RAM)")
        print("      ollama pull llama3:70b    (32GB RAM, mejor calidad)")
        print("      ollama pull mistral        (8GB RAM, más rápido)")
        print("   4. Activa en .env:  USE_LOCAL_MODELS=True")
        print("   5. Vuelve a ejecutar: python verificar_modelos.py --activar-local")

    print("="*60 + "\n")


if __name__ == "__main__":
    main()
