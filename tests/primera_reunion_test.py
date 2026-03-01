"""
TEST: Primera reunión piloto sobre Sicologa
Simula una reunión del Directorio Ejecutivo analizando el proyecto Sicologa
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infraestructura.loggers.jarvisz_logger import JarvisZLogger


def test_primera_reunion_sicologa():
    """Ejecuta la primera reunión test"""

    # Inicializar Jarvisz Logger
    jarvisz = JarvisZLogger("./infraestructura/db/jarvisz_test.db")

    print("\n" + "=" * 70)
    print("🎯 PRIMERA REUNIÓN PILOTO - SICOLOGA")
    print("=" * 70)

    # Datos de la reunión
    reunion_data = {
        "tema": "Análisis Inicial - Proyecto Sicologa",
        "ceo_analisis": """
        Sicologa es una oportunidad de mercado en salud mental digital.
        Necesitamos validar: ¿hay demanda real? ¿dónde están los clientes?
        Presupuesto indicativo: $500K para MVP + equipo.
        """,
        "cro_analisis": """
        RIESGOS CRÍTICO IDENTIFICADOS:
        1. Regulación de telemedicina (varía por país) - CRÍTICO
        2. Privacidad de datos de salud (HIPAA, GDPR) - CRÍTICO
        3. Licencias médicas de los psicólogos - IMPORTANTE

        DATOS NECESARIOS:
        - Jurisdicciones donde operar (definir primero)
        - Cumplimiento regulatorio por país
        - Análisis de competencia regulatoria
        """,
        "cvo_analisis": """
        DIFERENCIAL NARRATIVO:
        - "Psicología asequible para la generación digital" vs competencia
        - Ángulo: salud mental como derecho, no lujo
        - Diferencial injusto: comunidad de psicólogos validada (no agentes IA solos)

        DATOS NECESARIOS:
        - Mapeo de segmentos emocionales (qué problemas resuelve)
        - Historias de usuarios ideales
        - Diferencial vs Talkspace, BetterHelp
        """,
        "coo_analisis": """
        PLAN OPERATIVO:
        1. Validación de mercado (4 semanas)
           - Encuestas: 500+ usuarios potenciales
           - Entrevistas: 20+ psicólogos
        2. MVP v1 (8 semanas)
           - App básica + matching + sesiones
           - Testing con cohorte de 50 usuarios
        3. Go-to-market (6 semanas)

        DATOS NECESARIOS:
        - Timeline detallado (hito por semana)
        - Recursos humanos requeridos
        - Infraestructura tecnológica
        """,
        "cfo_analisis": """
        ANÁLISIS FINANCIERO INICIAL:
        - CAC estimado: $50-100 por usuario
        - LTV estimado: $1,200-2,000 por usuario (basado en Talkspace)
        - Runway: $500K = ~12 meses (asumiendo 25 usuarios por mes)

        DATOS NECESARIOS:
        - Presupuesto desglosado por equipo
        - Proyección de ingresos (suscripción vs comisión)
        - Break-even analysis
        - Seasonal patterns en salud mental
        """,
    }

    # Registrar la reunión
    print("\n📝 Registrando análisis de 5 agentes...")
    reunion_id = jarvisz.registrar_reunion(
        tema=reunion_data["tema"],
        ceo_analisis=reunion_data["ceo_analisis"],
        cro_analisis=reunion_data["cro_analisis"],
        cvo_analisis=reunion_data["cvo_analisis"],
        coo_analisis=reunion_data["coo_analisis"],
        cfo_analisis=reunion_data["cfo_analisis"],
        datos_criticos=[
            {
                "agente": "CRO",
                "dato": "Regulación de telemedicina por país",
                "razón": "Define viabilidad del proyecto",
            },
            {
                "agente": "CRO",
                "dato": "Cumplimiento HIPAA/GDPR",
                "razón": "Dato de salud es crítico en regulación",
            },
            {
                "agente": "CFO",
                "dato": "Proyección financiera detallada",
                "razón": "Define viabilidad de runway",
            },
        ],
        datos_importantes=[
            {
                "agente": "CVO",
                "dato": "Análisis de diferencial vs competencia",
                "razón": "Valida la propuesta de valor",
            },
            {
                "agente": "COO",
                "dato": "Timeline detallado por fase",
                "razón": "Coordina ejecución",
            },
        ],
        decision="Aprobar fase de validación de mercado con presupuesto de $50K",
        tareas=[
            {
                "responsable": "CEO",
                "tarea": "Presentar a inversores el proyecto",
                "fecha": "2026-03-15",
            },
            {
                "responsable": "CRO",
                "tarea": "Análisis regulatorio por país (3 primeras jurisdicciones)",
                "fecha": "2026-03-22",
            },
            {
                "responsable": "CVO",
                "tarea": "Definir narrativa de marca y diferencial",
                "fecha": "2026-03-15",
            },
            {
                "responsable": "COO",
                "tarea": "Planificar validación de mercado (encuestas + entrevistas)",
                "fecha": "2026-03-22",
            },
            {
                "responsable": "CFO",
                "tarea": "Proyección financiera detallada (3 escenarios)",
                "fecha": "2026-03-22",
            },
        ],
        proxima_reunion_fecha=datetime.utcnow() + timedelta(days=7),
        proxima_reunion_tema="Validación de Mercado - Resultados Iniciales",
    )

    print(f"✅ Reunión registrada con ID: {reunion_id}")

    # Obtener detalles
    print("\n📊 Detalles de la reunión registrada:")
    reunion = jarvisz.obtener_reunion(reunion_id)
    print(f"   Tema: {reunion['tema']}")
    print(f"   Fecha: {reunion['fecha']}")
    print(f"   Decisión: {reunion['decision']}")
    print(f"   Tareas asignadas: {len(reunion['tareas'])}")

    # Registrar algunos datos faltantes adicionales
    print("\n⚠️ Registrando datos faltantes detectados...")
    dato_id_1 = jarvisz.registrar_dato_faltante(
        agente_solicitante="CRO",
        dato_faltante="Mapa de regulación por país (telemedicina)",
        severidad="CRÍTICO",
        reunion_id=reunion_id,
    )
    print(f"   ✓ Dato crítico registrado (ID: {dato_id_1})")

    dato_id_2 = jarvisz.registrar_dato_faltante(
        agente_solicitante="CFO",
        dato_faltante="Proyección financiera (3 escenarios)",
        severidad="CRÍTICO",
        reunion_id=reunion_id,
    )
    print(f"   ✓ Dato crítico registrado (ID: {dato_id_2})")

    # Proponer especialista basado en patrón detectado
    print("\n🎯 Proponiendo especialista emergente...")
    especialista_id = jarvisz.proponer_especialista(
        nombre="Abogada Especialista en Telemedicina",
        especialidad="Regulación sanitaria y compliance telemédico",
        justificacion="""
        CRO identificó regulación como riesgo CRÍTICO en 2 ocasiones.
        Patrón detectado: CRO siempre prioriza riesgos legales.
        Se propone especialista para análisis profundo pre-inversión.
        """,
        patron_id=None,
    )
    print(f"   ✓ Especialista propuesto (ID: {especialista_id})")

    # Validar especialista por CFO
    print("\n✅ CFO valida especialista...")
    jarvisz.validar_especialista(
        especialista_id,
        validado=True,
        roi_estimado="$20K por análisis profundo, evita riesgos de $500K+",
    )
    print(f"   ✓ Especialista validado")

    # Generar reporte diario
    print("\n📈 Generando reporte diario de Jarvisz...")
    reporte = jarvisz.generar_reporte_diario()

    print("\n" + "=" * 70)
    print("📊 REPORTE DIARIO - JARVISZ")
    print("=" * 70)
    print(f"Fecha: {reporte['fecha']}")
    print(f"\n🎯 RESUMEN:")
    print(f"   • Reuniones: {reporte['resumen']['reuniones']}")
    print(f"   • Decisiones: {reporte['resumen']['decisiones']}")
    print(f"   • Datos críticos faltantes: {reporte['resumen']['datos_faltantes_criticos']}")

    print(f"\n🚨 ALERTAS:")
    print(f"   • Conflictos no resueltos: {len(reporte['alertas']['conflictos_no_resueltos'])}")
    print(f"   • Datos críticos faltantes: {len(reporte['alertas']['datos_criticos_faltantes'])}")
    for dato in reporte['alertas']['datos_criticos_faltantes']:
        print(f"     - {dato['dato']} (solicitado por {dato['solicitante']})")

    print(f"\n   • Especialistas emergentes: {len(reporte['alertas']['especialistas_emergentes'])}")
    for esp in reporte['alertas']['especialistas_emergentes']:
        print(f"     - {esp['nombre']} ({esp['especialidad']})")
        print(f"       Validado por CFO: {esp['validado']}")

    print(f"\n🔍 PATRONES DETECTADOS:")
    for patron in reporte['patrones_detectados']:
        print(f"   • {patron['agente']}: {patron['descripcion']}")
        print(f"     - Apariciones: {patron['apariciones']}")
        print(f"     - Bloquea decisión: {patron['bloquea_decision']}")

    print("\n" + "=" * 70)
    print("✅ PRIMERA REUNIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)

    return {
        "reunion_id": reunion_id,
        "reporte": reporte,
        "status": "success",
    }


if __name__ == "__main__":
    result = test_primera_reunion_sicologa()
    print(f"\n\n📌 Resultado: {result['status']}")
    print(f"ID Reunión: {result['reunion_id']}")
