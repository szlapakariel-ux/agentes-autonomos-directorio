"""
MAIN - Punto de entrada del sistema de Agentes Autónomos
OpenClaw + 6 Skills + Seguridad en 7 capas

Uso:
    python main.py --tema "Analizar Sicologa"
    python main.py --reporte
    python main.py --validar-seguridad
"""

import os
import sys
import json
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")

# Agregar raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar skills
from skills.ceo_skill   import CEOSkill
from skills.cro_skill   import CROSkill
from skills.cvo_skill   import CVOSkill
from skills.coo_skill   import COOSkill
from skills.cfo_skill   import CFOSkill
from skills.jarvisz_skill import JARVISZSkill

# Importar seguridad
from infraestructura.security.auth            import security_manager
from infraestructura.security.rbac            import RoleBasedAccess, UserRole, Permission
from infraestructura.security.rate_limiter    import RateLimiter
from infraestructura.security.input_validation import InputValidator


# ============================================================================
# ORQUESTADOR OPENCLAW
# ============================================================================

class OpenClawOrchestrator:
    """
    Coordina los 6 agentes autónomos con seguridad completa.
    Reemplaza el orquestador original con capas de seguridad.
    """

    def __init__(self):
        logger.info("Iniciando OpenClaw Orchestrator...")

        # Seguridad
        self.rate_limiter = RateLimiter()

        # Instanciar los 6 agentes
        self.ceo     = CEOSkill()
        self.cro     = CROSkill()
        self.cvo     = CVOSkill()
        self.coo     = COOSkill()
        self.cfo     = CFOSkill()
        self.jarvisz = JARVISZSkill()

        self._agentes_ejecutivos = {
            "CEO": self.ceo,
            "CRO": self.cro,
            "CVO": self.cvo,
            "COO": self.coo,
            "CFO": self.cfo,
        }

        logger.info("✅ 6 agentes inicializados y en sandbox")

    def ejecutar_reunion(
        self,
        tema: str,
        contexto: Optional[str] = None,
        user_id: str = "system",
    ) -> Dict:
        """
        Ejecuta una reunión con todos los agentes.
        Los 5 agentes C-Level analizan en paralelo.
        JARVISZ registra todo al final.

        Args:
            tema: Tema a analizar
            contexto: Contexto adicional
            user_id: ID de quien solicita (para rate limiting)

        Returns:
            Dict con análisis, decisión y metadata
        """

        # 1. Rate limiting
        allowed, msg, meta = self.rate_limiter.check_rate_limit(
            user_id, "skill_execution"
        )
        if not allowed:
            raise PermissionError(msg)

        # 2. Validar inputs
        valid, error = InputValidator.validate_prompt(tema)
        if not valid:
            raise ValueError(f"Tema inválido: {error}")

        print(f"\n{'='*65}")
        print(f"🎯 REUNIÓN: {tema}")
        print(f"{'='*65}")

        # 3. Ejecutar agentes C-Level en paralelo
        print(f"\n📋 Ejecutando análisis de 5 agentes en paralelo...\n")
        analisis = self._ejecutar_paralelo(tema, contexto)

        # 4. Detectar conflictos
        conflictos = self._detectar_conflictos(analisis)
        if conflictos:
            print(f"  ⚠️  {len(conflictos)} conflicto(s) detectado(s)")

        # 5. Sintetizar decisión
        decision = self._sintetizar(analisis, conflictos)
        print(f"\n✅ DECISIÓN: {decision}")

        # 6. Extraer datos solicitados por los agentes
        datos_criticos   = self._extraer_datos(analisis, "CRÍTICO")
        datos_importantes = self._extraer_datos(analisis, "IMPORTANTE")

        # 7. JARVISZ registra todo
        print("\n💾 JARVISZ registrando...")
        reunion_id = self.jarvisz.registrar(
            tema=tema,
            analisis_agentes=analisis,
            datos_criticos=datos_criticos,
            datos_importantes=datos_importantes,
            decision=decision,
        )
        print(f"  ✓ Reunión #{reunion_id} registrada en SQLite")

        # 8. Proponer especialistas si hay patrones
        especialistas = self._evaluar_especialistas(analisis)

        # 9. Imprimir resumen
        self._imprimir_resumen(
            reunion_id, analisis, conflictos, datos_criticos, especialistas
        )

        return {
            "reunion_id":   reunion_id,
            "tema":         tema,
            "fecha":        datetime.utcnow().isoformat(),
            "analisis":     analisis,
            "decision":     decision,
            "conflictos":   conflictos,
            "datos_criticos": datos_criticos,
            "especialistas": especialistas,
            "sandbox_summaries": {
                name: skill.get_sandbox_summary()
                for name, skill in self._agentes_ejecutivos.items()
            },
        }

    def _ejecutar_paralelo(
        self,
        tema: str,
        contexto: Optional[str],
    ) -> Dict[str, str]:
        """Ejecuta los 5 agentes en paralelo con ThreadPoolExecutor"""

        resultados: Dict[str, str] = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futuros = {
                executor.submit(skill.analyze, tema, contexto): name
                for name, skill in self._agentes_ejecutivos.items()
            }

            for futuro in as_completed(futuros):
                name = futuros[futuro]
                try:
                    resultado = futuro.result()
                    resultados[name] = resultado
                    print(f"  ✓ {name} completó análisis")
                except Exception as e:
                    logger.error(f"{name} falló: {e}")
                    resultados[name] = f"Error: {str(e)}"
                    print(f"  ✗ {name} falló: {e}")

        return resultados

    def _detectar_conflictos(self, analisis: Dict[str, str]) -> List[Dict]:
        """Detecta conflictos entre análisis de agentes"""
        conflictos = []

        cro = (analisis.get("CRO") or "").lower()
        cvo = (analisis.get("CVO") or "").lower()
        coo = (analisis.get("COO") or "").lower()
        cfo = (analisis.get("CFO") or "").lower()

        if "riesgo" in cro and "oportunidad" in cvo:
            conflictos.append({
                "tipo": "Riesgo vs Oportunidad",
                "entre": "CRO vs CVO",
                "severidad": "Alta",
            })

        if "urgente" in coo and ("presupuesto" in cfo or "costo" in cfo):
            conflictos.append({
                "tipo": "Timeline vs Presupuesto",
                "entre": "COO vs CFO",
                "severidad": "Media",
            })

        return conflictos

    def _sintetizar(
        self, analisis: Dict[str, str], conflictos: List[Dict]
    ) -> str:
        """Genera decisión basada en análisis y conflictos"""
        conflictos_altos = [c for c in conflictos if c["severidad"] == "Alta"]

        if not conflictos:
            return "✅ APROBADO — Todos los agentes están alineados"
        elif conflictos_altos:
            return "⚠️  APROBADO CON CONDICIONES — Resolver conflictos críticos antes de ejecutar"
        else:
            return "✅ APROBADO — Proceder con mitigaciones menores"

    def _extraer_datos(
        self, analisis: Dict[str, str], severidad: str
    ) -> List[Dict]:
        """Extrae datos solicitados por los agentes con una severidad específica"""
        datos = []
        import re

        for agente, texto in analisis.items():
            lineas = (texto or "").split("\n")
            for linea in lineas:
                if severidad in linea.upper() and ":" in linea:
                    dato = linea.split(":", 1)[1].strip()
                    if len(dato) > 5:
                        datos.append({"agente": agente, "dato": dato[:200]})

        return datos

    def _evaluar_especialistas(self, analisis: Dict[str, str]) -> List[Dict]:
        """Propone especialistas basados en patrones en los análisis"""
        propuestos = []

        cro_texto = (analisis.get("CRO") or "").lower()
        cfo_texto = (analisis.get("CFO") or "").lower()

        if "regulaci" in cro_texto or "legal" in cro_texto:
            esp_id = self.jarvisz.proponer_especialista(
                nombre="Especialista en Regulación",
                especialidad="Compliance y legal risk",
                justificacion="CRO detectó riesgos regulatorios/legales",
            )
            propuestos.append({"id": esp_id, "nombre": "Especialista en Regulación"})

        if "financiamiento" in cfo_texto or "capital" in cfo_texto:
            esp_id = self.jarvisz.proponer_especialista(
                nombre="Especialista en Fundraising",
                especialidad="Capital raising",
                justificacion="CFO identificó necesidad de capital externo",
            )
            propuestos.append({"id": esp_id, "nombre": "Especialista en Fundraising"})

        return propuestos

    def _imprimir_resumen(
        self,
        reunion_id: int,
        analisis: Dict,
        conflictos: List,
        datos_criticos: List,
        especialistas: List,
    ):
        """Imprime resumen final en consola"""
        print(f"\n{'='*65}")
        print(f"📊 RESUMEN REUNIÓN #{reunion_id}")
        print(f"{'='*65}")

        print(f"\n🤖 AGENTES EJECUTADOS: {', '.join(analisis.keys())}")

        if conflictos:
            print(f"\n⚠️  CONFLICTOS ({len(conflictos)}):")
            for c in conflictos:
                print(f"   • {c['tipo']} ({c['entre']}) — Severidad: {c['severidad']}")

        if datos_criticos:
            print(f"\n🔴 DATOS CRÍTICOS FALTANTES ({len(datos_criticos)}):")
            for d in datos_criticos[:5]:
                print(f"   • {d['agente']}: {d['dato'][:80]}")

        if especialistas:
            print(f"\n🎓 ESPECIALISTAS PROPUESTOS ({len(especialistas)}):")
            for e in especialistas:
                print(f"   • {e['nombre']}")

        print(f"\n{'='*65}\n")

    def reporte_diario(self) -> Dict:
        """Genera y muestra reporte diario de Jarvisz"""
        reporte = self.jarvisz.reporte_diario()

        print(f"\n{'='*65}")
        print(f"📈 REPORTE DIARIO — JARVISZ")
        print(f"{'='*65}")
        print(f"  Reuniones hoy:          {reporte['resumen']['reuniones']}")
        print(f"  Decisiones:             {reporte['resumen']['decisiones']}")
        print(f"  Datos críticos faltantes: {reporte['resumen']['datos_faltantes_criticos']}")
        print(f"{'='*65}\n")

        return reporte


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Agentes Autónomos — Directorio Ejecutivo con OpenClaw",
    )
    parser.add_argument("--tema", "-t", help="Tema a analizar")
    parser.add_argument("--contexto", "-c", help="Contexto adicional")
    parser.add_argument("--reporte", "-r", action="store_true",
                        help="Generar reporte diario")
    parser.add_argument("--validar-seguridad", action="store_true",
                        help="Ejecutar validador de seguridad")
    parser.add_argument("--output", "-o", help="Guardar resultado en JSON")

    args = parser.parse_args()

    # Validar seguridad
    if args.validar_seguridad:
        from infraestructura.security.validator import SecurityValidator
        validator = SecurityValidator()
        is_secure, errors, warnings = validator.validate_all()
        sys.exit(0 if is_secure else 1)

    # Reporte diario
    if args.reporte:
        orq = OpenClawOrchestrator()
        orq.reporte_diario()
        return

    # Ejecutar reunión
    if not args.tema:
        parser.print_help()
        sys.exit(1)

    orq = OpenClawOrchestrator()
    resultado = orq.ejecutar_reunion(
        tema=args.tema,
        contexto=args.contexto,
        user_id="cli_user",
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)
        print(f"✅ Resultado guardado en: {args.output}")


if __name__ == "__main__":
    main()
