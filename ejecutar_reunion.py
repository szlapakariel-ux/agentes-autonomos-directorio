#!/usr/bin/env python3
"""
EJECUTOR DE REUNIONES - CLI
Interfaz para ejecutar reuniones automáticas del Directorio Ejecutivo

Uso:
    python ejecutar_reunion.py "Tema de la reunión" "Contexto opcional"
    python ejecutar_reunion.py --tema "Sicologa" --contexto "Startup de salud mental"
    python ejecutar_reunion.py --reporte  # Ver último reporte
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from infraestructura.orquestador import Orquestador


def main():
    parser = argparse.ArgumentParser(
        description="Ejecutor de Reuniones del Directorio Ejecutivo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Ejecutar reunión simple
  python ejecutar_reunion.py --tema "Validación de Mercado"

  # Ejecutar con contexto
  python ejecutar_reunion.py --tema "Sicologa" --contexto "Plataforma de telemedicina"

  # Ver reporte diario
  python ejecutar_reunion.py --reporte

  # Ejecutar y guardar resultado
  python ejecutar_reunion.py --tema "Mi proyecto" --output resultado.json
        """,
    )

    parser.add_argument(
        "--tema", "-t", type=str, help="Tema de la reunión a analizar"
    )
    parser.add_argument(
        "--contexto", "-c", type=str, help="Contexto adicional (opcional)"
    )
    parser.add_argument(
        "--reporte",
        "-r",
        action="store_true",
        help="Mostrar reporte diario de Jarvisz",
    )
    parser.add_argument(
        "--output", "-o", type=str, help="Guardar resultado en archivo JSON"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="./infraestructura/db/jarvisz.db",
        help="Ruta a base de datos Jarvisz",
    )
    parser.add_argument(
        "--prompts-dir",
        type=str,
        default="./directorio/prompts",
        help="Directorio con prompts de agentes",
    )

    args = parser.parse_args()

    # Inicializar orquestador
    print("\n🚀 Inicializando Orquestador...\n")
    orquestador = Orquestador(
        prompts_dir=args.prompts_dir, db_path=args.db_path
    )

    # Mostrar reporte si se solicita
    if args.reporte:
        print("\n📊 REPORTE DIARIO - JARVISZ\n")
        reporte = orquestador.generar_reporte_diario()
        print(json.dumps(reporte, indent=2, ensure_ascii=False))
        return

    # Validar que hay tema
    if not args.tema:
        print("❌ Error: Se requiere --tema")
        print("Usa 'python ejecutar_reunion.py --help' para ver opciones")
        sys.exit(1)

    # Ejecutar reunión
    print(f"📋 Tema: {args.tema}")
    if args.contexto:
        print(f"📝 Contexto: {args.contexto[:60]}...")

    resultado = orquestador.ejecutar_reunion(args.tema, args.contexto)

    # Guardar si se solicita
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n✅ Resultado guardado en: {args.output}")

    # Mostrar resumen
    print(f"\n✅ Reunión completada (ID: {resultado['reunion_id']})")


if __name__ == "__main__":
    main()
