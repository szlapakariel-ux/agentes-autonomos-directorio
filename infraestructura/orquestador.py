"""
ORQUESTADOR CENTRAL - Agentes Autónomos Ejecutivos
Transforma prompts en agentes que piensan y actúan de manera autónoma
Cada agente es una instancia de Claude con una "personalidad" basada en su rol
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Importar cliente apropiado según disponibilidad
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from infraestructura.loggers.jarvisz_logger import JarvisZLogger


class AgenteAutonomo:
    """Representa un agente ejecutivo autónomo (CEO, CRO, CVO, COO, CFO, JARVISZ)"""

    def __init__(
        self,
        rol: str,
        prompt_template: str,
        client,
        use_ollama: bool = False,
    ):
        self.rol = rol
        self.prompt_template = prompt_template
        self.client = client
        self.use_ollama = use_ollama
        self.ultimo_analisis = None

    def analizar(
        self,
        tema: str,
        contexto: Optional[str] = None,
        datos_previos: Optional[Dict] = None,
    ) -> str:
        """
        El agente analiza un tema desde su perspectiva de rol.
        Piensa de forma autónoma basado en su prompt.
        Funciona con Anthropic Claude o Ollama (OpenAI compatible).
        """

        # Construir el mensaje que se envía al modelo
        mensaje_sistema = self.prompt_template

        # Contexto adicional que enriquece el análisis
        contexto_adicional = f"""
CONTEXTO DEL TEMA:
{contexto or "Sin contexto adicional"}

DATOS PREVIOS (si existen):
{json.dumps(datos_previos, indent=2) if datos_previos else "Sin datos previos"}
"""

        mensaje_usuario = f"""
TEMA A ANALIZAR: {tema}

{contexto_adicional}

Por favor, proporciona tu análisis desde la perspectiva de {self.rol}.
Sé específico, accionable y fundamentado en datos o lógica clara.
"""

        try:
            if self.use_ollama:
                # Usar OpenAI client (Ollama compatible)
                respuesta = self.client.chat.completions.create(
                    model="llama3",  # Modelo disponible en Ollama
                    max_tokens=1500,
                    messages=[
                        {
                            "role": "system",
                            "content": mensaje_sistema,
                        },
                        {
                            "role": "user",
                            "content": mensaje_usuario,
                        }
                    ],
                )
                analisis = respuesta.choices[0].message.content
            else:
                # Usar Anthropic Claude API
                respuesta = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[
                        {
                            "role": "user",
                            "content": mensaje_usuario,
                        }
                    ],
                    system=mensaje_sistema,
                )
                analisis = respuesta.content[0].text

            self.ultimo_analisis = analisis
            return analisis

        except Exception as e:
            raise Exception(f"Error en análisis de {self.rol}: {str(e)}")

    def extraer_datos_solicitados(self, analisis: str) -> Dict[str, List]:
        """
        Extrae del análisis qué datos solicita el agente (CRÍTICO, IMPORTANTE, NICE-TO-HAVE)
        """
        datos = {
            "CRÍTICO": [],
            "IMPORTANTE": [],
            "NICE-TO-HAVE": [],
        }

        # Buscar en el análisis menciones de datos necesarios
        lineas = analisis.split("\n")
        for linea in lineas:
            if "CRÍTICO" in linea.upper():
                # Extraer lo que viene después
                if ":" in linea:
                    dato = linea.split(":", 1)[1].strip()
                    if dato:
                        datos["CRÍTICO"].append(dato)
            elif "IMPORTANTE" in linea.upper():
                if ":" in linea:
                    dato = linea.split(":", 1)[1].strip()
                    if dato:
                        datos["IMPORTANTE"].append(dato)
            elif "NICE-TO-HAVE" in linea.upper():
                if ":" in linea:
                    dato = linea.split(":", 1)[1].strip()
                    if dato:
                        datos["NICE-TO-HAVE"].append(dato)

        return datos


class Orquestador:
    """
    Coordinador central que:
    1. Carga prompts de cada rol
    2. Ejecuta agentes autónomos en paralelo
    3. Recolecta análisis
    4. Registra en Jarvisz
    5. Detecta conflictos y patrones
    6. Sugiere decisiones

    Soporta: Anthropic Claude o Ollama (OpenAI compatible)
    """

    def __init__(
        self,
        prompts_dir: str = "./directorio/prompts",
        db_path: str = "./infraestructura/db/jarvisz.db",
        api_key: Optional[str] = None,
        ollama_url: str = "http://127.0.0.1:11434/v1",
    ):
        self.prompts_dir = Path(prompts_dir)
        self.jarvisz = JarvisZLogger(db_path)

        # Determinar qué cliente usar
        self.use_ollama = False
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if self.api_key and HAS_ANTHROPIC:
            # Usar Anthropic
            print("🔌 Usando Anthropic Claude API")
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.use_ollama = False
        elif HAS_OPENAI:
            # Usar Ollama (OpenAI compatible)
            print(f"🔌 Usando Ollama en {ollama_url}")
            self.client = OpenAI(
                base_url=ollama_url,
                api_key="ollama"  # Dummy key para Ollama
            )
            self.use_ollama = True
        else:
            raise RuntimeError("❌ No hay cliente disponible. Instala 'anthropic' o 'openai'")

        self.agentes: Dict[str, AgenteAutonomo] = {}

        # Cargar prompts y crear agentes
        self._inicializar_agentes()

    def _inicializar_agentes(self):
        """Carga prompts y crea agentes autónomos"""
        roles_esperados = ["CEO", "CRO", "CVO", "COO", "CFO", "JARVISZ"]

        for rol in roles_esperados:
            archivo_prompt = self.prompts_dir / f"{rol}_prompt.md"

            if archivo_prompt.exists():
                with open(archivo_prompt, "r", encoding="utf-8") as f:
                    prompt_content = f.read()

                agente = AgenteAutonomo(
                    rol,
                    prompt_content,
                    self.client,
                    use_ollama=self.use_ollama
                )
                self.agentes[rol] = agente
                print(f"✓ Agente {rol} inicializado")
            else:
                print(f"⚠ No se encontró prompt para {rol}")

    def ejecutar_reunion(
        self,
        tema: str,
        contexto: Optional[str] = None,
        datos_previos: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Ejecuta una reunión ejecutiva automatizada:
        1. Cada agente analiza el tema de forma autónoma
        2. Se recolectan análisis
        3. Se detectan conflictos
        4. Se registra en Jarvisz
        5. Se genera reporte
        """

        print(f"\n{'='*70}")
        print(f"🎯 EJECUTANDO REUNIÓN: {tema}")
        print(f"{'='*70}")

        # Fase 1: Ejecutar agentes
        print(f"\n📋 Fase 1: Análisis de agentes...")
        analisis_agentes = {}
        datos_solicitados_total = {
            "CRÍTICO": [],
            "IMPORTANTE": [],
            "NICE-TO-HAVE": [],
        }

        for rol, agente in self.agentes.items():
            if rol == "JARVISZ":
                # Jarvisz se ejecuta después, no analiza directamente
                continue

            print(f"  → {rol} analizando...", end=" ", flush=True)
            try:
                analisis = agente.analizar(tema, contexto, datos_previos)
                analisis_agentes[rol] = analisis
                print("✓")

                # Extraer datos solicitados
                datos = agente.extraer_datos_solicitados(analisis)
                for severidad, lista in datos.items():
                    datos_solicitados_total[severidad].extend(
                        [{"agente": rol, "dato": d} for d in lista]
                    )

            except Exception as e:
                print(f"✗ Error: {str(e)}")
                analisis_agentes[rol] = f"Error: {str(e)}"

        # Fase 2: Detectar conflictos
        print(f"\n🔍 Fase 2: Detectando conflictos...")
        conflictos = self._detectar_conflictos(analisis_agentes)
        if conflictos:
            print(f"  ⚠️ {len(conflictos)} conflicto(s) detectado(s)")
        else:
            print(f"  ✓ Sin conflictos significativos")

        # Fase 3: Sintetizar decisión (puede ser automática o requerir CEO)
        print(f"\n✅ Fase 3: Sintetizando decisión...")
        decision = self._sintetizar_decision(analisis_agentes, conflictos)

        # Fase 4: Registrar en Jarvisz
        print(f"\n💾 Fase 4: Registrando en Jarvisz...")
        reunion_id = self.jarvisz.registrar_reunion(
            tema=tema,
            ceo_analisis=analisis_agentes.get("CEO"),
            cro_analisis=analisis_agentes.get("CRO"),
            cvo_analisis=analisis_agentes.get("CVO"),
            coo_analisis=analisis_agentes.get("COO"),
            cfo_analisis=analisis_agentes.get("CFO"),
            datos_criticos=[d for d in datos_solicitados_total["CRÍTICO"]],
            datos_importantes=[d for d in datos_solicitados_total["IMPORTANTE"]],
            datos_nice_to_have=[d for d in datos_solicitados_total["NICE-TO-HAVE"]],
            decision=decision,
            proxima_reunion_fecha=datetime.utcnow() + timedelta(days=7),
            proxima_reunion_tema=f"Seguimiento: {tema}",
        )
        print(f"  ✓ Reunión {reunion_id} registrada")

        # Fase 5: Proponer especialistas si se detectan patrones
        print(f"\n🎓 Fase 5: Evaluando especialistas emergentes...")
        especialistas_propuestos = self._evaluar_especialistas(
            analisis_agentes, reunion_id
        )

        # Resultado final
        resultado = {
            "reunion_id": reunion_id,
            "tema": tema,
            "fecha": datetime.utcnow().isoformat(),
            "analisis": analisis_agentes,
            "decision": decision,
            "conflictos": conflictos,
            "datos_solicitados": datos_solicitados_total,
            "especialistas_propuestos": especialistas_propuestos,
        }

        # Mostrar resumen
        self._mostrar_resumen(resultado)

        return resultado

    def _detectar_conflictos(self, analisis: Dict[str, str]) -> List[Dict]:
        """Detecta conflictos entre análisis de diferentes agentes"""
        conflictos = []

        # Comparar CRO (riesgos) vs CVO (oportunidades)
        if "CRO" in analisis and "CVO" in analisis:
            analisis_cro = analisis["CRO"].lower()
            analisis_cvo = analisis["CVO"].lower()

            if (
                "riesgo crítico" in analisis_cro
                and "oportunidad core" in analisis_cvo
            ):
                conflictos.append(
                    {
                        "tipo": "Riesgo vs Oportunidad",
                        "entre": "CRO vs CVO",
                        "severidad": "Alta",
                        "descripcion": "CRO ve riesgos críticos que CVO considera oportunidades core",
                    }
                )

        # Comparar COO (timeline) vs CFO (presupuesto)
        if "COO" in analisis and "CFO" in analisis:
            analisis_coo = analisis["COO"].lower()
            analisis_cfo = analisis["CFO"].lower()

            if (
                "corto plazo" in analisis_coo
                and "presupuesto limitado" in analisis_cfo
            ):
                conflictos.append(
                    {
                        "tipo": "Timeline vs Presupuesto",
                        "entre": "COO vs CFO",
                        "severidad": "Media",
                        "descripcion": "COO necesita ejecución rápida pero CFO reporta presupuesto limitado",
                    }
                )

        return conflictos

    def _sintetizar_decision(
        self, analisis: Dict[str, str], conflictos: List[Dict]
    ) -> str:
        """
        Sintetiza una decisión basada en los análisis.
        En una versión más avanzada, podría usar un agente "CEO virtual" para decidir.
        """

        # Lógica básica: si no hay conflictos críticos y todos aprueban, avanzar
        if not conflictos:
            return "✅ APROBADO: Proceder con la iniciativa. Todos los agentes están alineados."
        else:
            conflictos_altos = [c for c in conflictos if c["severidad"] == "Alta"]
            if conflictos_altos:
                return "⚠️ APROBADO CON CONDICIONES: Resolver conflictos de riesgo vs oportunidad antes de ejecutar."
            else:
                return "✅ APROBADO: Proceder con mitigaciones de riesgos menores."

    def _evaluar_especialistas(self, analisis: Dict[str, str], reunion_id: int) -> List:
        """Propone especialistas basados en patrones detectados"""
        especialistas_propuestos = []

        # Patrón: Si CRO menciona "regulación" o "legal" → Abogado especialista
        if "CRO" in analisis and (
            "regulación" in analisis["CRO"].lower()
            or "legal" in analisis["CRO"].lower()
        ):
            esp_id = self.jarvisz.proponer_especialista(
                nombre="Especialista Legal en Regulación",
                especialidad="Cumplimiento normativo y legal risk",
                justificacion="CRO identificó riesgos regulatorios/legales. Patrón: CRO siempre prioriza riesgos.",
                patron_id=None,
            )
            especialistas_propuestos.append(
                {
                    "id": esp_id,
                    "nombre": "Especialista Legal en Regulación",
                    "estado": "propuesto",
                }
            )

        # Patrón: Si CFO menciona "financiamiento" → Fundraiser
        if "CFO" in analisis and "financiamiento" in analisis["CFO"].lower():
            esp_id = self.jarvisz.proponer_especialista(
                nombre="Especialista en Fundraising",
                especialidad="Capital raising y estructuración financiera",
                justificacion="CFO identifica necesidad de financiamiento externo.",
            )
            especialistas_propuestos.append(
                {
                    "id": esp_id,
                    "nombre": "Especialista en Fundraising",
                    "estado": "propuesto",
                }
            )

        return especialistas_propuestos

    def _mostrar_resumen(self, resultado: Dict):
        """Muestra un resumen visual de la reunión"""
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN DE REUNIÓN #{resultado['reunion_id']}")
        print(f"{'='*70}")
        print(f"\n📌 Tema: {resultado['tema']}")
        print(f"📅 Fecha: {resultado['fecha']}")
        print(f"\n✅ DECISIÓN:\n{resultado['decision']}")

        if resultado["conflictos"]:
            print(f"\n⚠️ CONFLICTOS DETECTADOS ({len(resultado['conflictos'])}):")
            for conf in resultado["conflictos"]:
                print(f"   • {conf['tipo']} ({conf['entre']}): {conf['descripcion']}")

        print(f"\n📋 DATOS SOLICITADOS:")
        for severidad in ["CRÍTICO", "IMPORTANTE", "NICE-TO-HAVE"]:
            datos = resultado["datos_solicitados"][severidad]
            if datos:
                print(f"   {severidad} ({len(datos)}):")
                for d in datos[:3]:  # Mostrar primeros 3
                    print(f"     - {d.get('agente', '?')}: {d.get('dato', 'N/A')[:60]}...")

        if resultado["especialistas_propuestos"]:
            print(
                f"\n🎓 ESPECIALISTAS PROPUESTOS ({len(resultado['especialistas_propuestos'])}):"
            )
            for esp in resultado["especialistas_propuestos"]:
                print(f"   • {esp['nombre']}")

        print(f"\n{'='*70}\n")

    def generar_reporte_diario(self) -> Dict:
        """Genera reporte diario consolidado por Jarvisz"""
        return self.jarvisz.generar_reporte_diario()


def main():
    """Ejemplo de uso: ejecutar una reunión sobre un proyecto"""

    orquestador = Orquestador()

    # Tema a analizar
    tema = "Sicologa: Plataforma de telemedicina psicológica"
    contexto = """
    Sicologa es una startup de salud mental digital.
    Propuesta: App de telemedicina que conecta usuarios con psicólogos certificados.
    Mercado objetivo: América Latina (inicialmente México y Colombia)
    Presupuesto disponible: $500K
    Timeline: MVP en 12 semanas
    """

    # Ejecutar reunión
    resultado = orquestador.ejecutar_reunion(tema, contexto)

    # Generar reporte diario
    reporte = orquestador.generar_reporte_diario()
    print(f"\n📈 REPORTE DIARIO JARVISZ:")
    print(json.dumps(reporte, indent=2))

    return resultado


if __name__ == "__main__":
    main()
