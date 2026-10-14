"""Compliance Ley Silla + NOM-035 + NOM-037 (teletrabajo y desconexión) — México.

Fuentes verificadas el 2026-10-14:

- LFT, texto vigente (https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf, última reforma
  DOF 14-05-2026):
  * "Ley Silla": decreto DOF 19-12-2024 que reforma el Art. 132 fr. V (asientos o sillas con
    respaldo) y adiciona el Art. 133 fr. XVII Bis (prohibido obligar a estar de pie toda la
    jornada). Transitorios: vigor a los 180 días naturales (2025-06-17); 180 días naturales más
    para adecuar la normativa interna (2025-12-14).
  * Desconexión digital: solo existe para teletrabajo, Art. 330-E fr. VI (DOF 11-01-2021). No hay
    "reforma de marzo 2026 al Art. 132" sobre desconexión: la palabra solo aparece en el 330-E.
  * Multas (base UMA al momento de la infracción, Art. 992): Art. 994 fr. V 250-5000 UMA
    (normas de seguridad e higiene, incluye NOMs STPS); Art. 1002 50-5000 UMA (violaciones sin
    sanción específica, p. ej. Art. 132 fr. V y 133 fr. XVII Bis); reincidencia duplica la multa
    de la infracción anterior (Art. 992).
- UMA 2026: $117.31 diaria, vigente desde 2026-02-01 (INEGI, DOF 09-01-2026, nota 5778072).
- NOM-035-STPS-2018 (DOF 23-10-2018, nota 5541828), numeral 2: hasta 15 trabajadores → 5.1, 5.4,
  5.5, 5.7, 8.1, 8.2; 16-50 → 5.1, 5.2, 5.4-5.8, 7.x, Cap. 8; más de 50 → 5.1, 5.3-5.8, 7.x, Cap. 8.
  Las Guías de referencia son ejemplos, no obligatorias.
- NOM-037-STPS-2023 (DOF 08-06-2023, nota 5691672), numerales 5.1-5.14; vigor a los 180 días.
  Aplica a relaciones de teletrabajo (> 40 % del tiempo fuera, LFT Art. 330-A).

La versión anterior traía fechas, multas por "severidad", una UMA 2026 de $113.07 y obligaciones
(descansos cada 4 h, capacitación anual de silla) que no están en la ley.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

UMA_2026_DIARIA = 117.31  # INEGI, DOF 09-01-2026, vigente desde 2026-02-01
URL_LFT = "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf"
URL_NOM035 = "https://dof.gob.mx/nota_detalle.php?codigo=5541828&fecha=23/10/2018"
URL_NOM037 = "https://dof.gob.mx/nota_detalle.php?codigo=5691672&fecha=08/06/2023"

FECHA_LEY_SILLA_DOF = "2024-12-19"
FECHA_LEY_SILLA_VIGOR = "2025-06-17"          # Transitorio Primero: 180 días naturales
FECHA_LEY_SILLA_NORMATIVA_INTERNA = "2025-12-14"  # Transitorio Tercero: +180 días naturales

Severidad = Literal["leve", "media", "grave", "muy_grave"]  # prioridad interna, no es categoría legal
FundamentoMulta = Literal["lft_994_v", "lft_1002", "lft_994_vi"]
GiroTrabajo = Literal[
    "retail_comercio", "manufactura", "servicios_personales", "oficina_administrativo",
    "teletrabajo_hibrido", "almacen_logistica", "salud", "educacion", "construccion", "otro",
]

# Art. 132 fr. V: obligatorio en servicios, comercio y análogos; en industria "cuando lo permita
# la naturaleza del trabajo".
GIROS_SERVICIOS_COMERCIO: list[GiroTrabajo] = [
    "retail_comercio", "servicios_personales", "oficina_administrativo", "salud", "educacion", "otro",
]
GIROS_INDUSTRIALES: list[GiroTrabajo] = ["manufactura", "almacen_logistica", "construccion"]
TODOS_GIROS: list[GiroTrabajo] = GIROS_SERVICIOS_COMERCIO + GIROS_INDUSTRIALES + ["teletrabajo_hibrido"]


@dataclass
class MultaLFT:
    fundamento: FundamentoMulta
    rango_min_uma: int
    rango_max_uma: int
    descripcion: str


TABLA_MULTAS_LFT: dict[FundamentoMulta, MultaLFT] = {
    "lft_994_v": MultaLFT("lft_994_v", 250, 5000,
                          "Art. 994 fr. V: normas de seguridad e higiene / prevención de riesgos"),
    "lft_1002": MultaLFT("lft_1002", 50, 5000,
                         "Art. 1002: violaciones sin sanción específica en la LFT"),
    "lft_994_vi": MultaLFT("lft_994_vi", 250, 5000,
                           "Art. 994 fr. VI: discriminación, acoso u hostigamiento sexual"),
}


@dataclass
class ObligacionLeySilla:
    clave: str
    descripcion: str
    aplica_giros: list[GiroTrabajo]
    base_legal: str
    fundamento_multa: FundamentoMulta = "lft_1002"
    severidad_falta: Severidad = "media"


@dataclass
class ObligacionNOM035:
    clave: str
    descripcion: str
    aplica_si_empleados_min: int = 1
    aplica_si_empleados_max: Optional[int] = None
    base_legal: str = "NOM-035-STPS-2018"
    fundamento_multa: FundamentoMulta = "lft_994_v"
    severidad_falta: Severidad = "media"


@dataclass
class ObligacionNOM037:
    clave: str
    descripcion: str
    aplica_si_modalidad_remota: bool = True
    base_legal: str = "NOM-037-STPS-2023"
    fundamento_multa: FundamentoMulta = "lft_994_v"
    severidad_falta: Severidad = "media"


CATALOGO_LEY_SILLA: list[ObligacionLeySilla] = [
    ObligacionLeySilla(
        clave="sillas_con_respaldo_suficientes",
        descripcion=("Proveer asientos o sillas con respaldo suficientes para todas las personas "
                     "trabajadoras, para sus funciones o para el descanso periódico durante la jornada."),
        aplica_giros=GIROS_SERVICIOS_COMERCIO,
        base_legal="LFT Art. 132 fr. V (DOF 19-12-2024)",
        severidad_falta="grave",
    ),
    ObligacionLeySilla(
        clave="sillas_industria_si_lo_permite",
        descripcion=("En establecimientos industriales, proveer sillas con respaldo cuando lo permita "
                     "la naturaleza del trabajo."),
        aplica_giros=GIROS_INDUSTRIALES,
        base_legal="LFT Art. 132 fr. V, última parte (DOF 19-12-2024)",
        severidad_falta="media",
    ),
    ObligacionLeySilla(
        clave="area_descanso_con_sillas",
        descripcion="Para descansos periódicos, ubicar las sillas en áreas designadas dentro del lugar de trabajo.",
        aplica_giros=GIROS_SERVICIOS_COMERCIO + GIROS_INDUSTRIALES,
        base_legal="LFT Art. 132 fr. V, segundo párrafo",
        severidad_falta="media",
    ),
    ObligacionLeySilla(
        clave="no_obligar_estar_de_pie",
        descripcion=("No obligar a permanecer de pie toda la jornada ni prohibir tomar asiento "
                     "periódicamente durante las funciones."),
        aplica_giros=GIROS_SERVICIOS_COMERCIO + GIROS_INDUSTRIALES,
        base_legal="LFT Art. 133 fr. XVII Bis (DOF 19-12-2024)",
        severidad_falta="grave",
    ),
    ObligacionLeySilla(
        clave="normativa_interna_adecuada",
        descripcion="Adecuar la normativa interna (p. ej. reglamento interior) a la fr. V del Art. 132.",
        aplica_giros=GIROS_SERVICIOS_COMERCIO + GIROS_INDUSTRIALES,
        base_legal="Decreto DOF 19-12-2024, Transitorio Tercero (plazo 2025-12-14)",
        severidad_falta="media",
    ),
]

CATALOGO_NOM035: list[ObligacionNOM035] = [
    ObligacionNOM035("politica_prevencion_psicosociales",
                     "Política escrita de prevención de riesgos psicosociales, violencia laboral y entorno "
                     "organizacional favorable, implantada y difundida (5.1).",
                     base_legal="NOM-035-STPS-2018 5.1", severidad_falta="grave"),
    ObligacionNOM035("medidas_prevencion_control",
                     "Adoptar medidas para prevenir y controlar factores de riesgo psicosocial y atender "
                     "actos de violencia laboral (5.4, Cap. 8).",
                     base_legal="NOM-035-STPS-2018 5.4 y Cap. 8", severidad_falta="grave"),
    ObligacionNOM035("identificar_acontecimientos_traumaticos",
                     "Identificar a trabajadores sujetos a acontecimientos traumáticos severos y "
                     "canalizarlos para su atención (5.5; la Guía I es un ejemplo).",
                     base_legal="NOM-035-STPS-2018 5.5", severidad_falta="grave"),
    ObligacionNOM035("difundir_informacion",
                     "Difundir y proporcionar información a los trabajadores sobre la política, medidas y "
                     "mecanismos de quejas (5.7).",
                     base_legal="NOM-035-STPS-2018 5.7", severidad_falta="media"),
    ObligacionNOM035("identificar_factores_riesgo_16_50",
                     "Identificar y analizar los factores de riesgo psicosocial (5.2, 7.1 a; Guía II de referencia).",
                     aplica_si_empleados_min=16, aplica_si_empleados_max=50,
                     base_legal="NOM-035-STPS-2018 5.2", severidad_falta="grave"),
    ObligacionNOM035("identificar_factores_y_entorno_mas_50",
                     "Identificar y analizar factores de riesgo y evaluar el entorno organizacional "
                     "(5.3, 7.1 b; Guía III de referencia).",
                     aplica_si_empleados_min=51, base_legal="NOM-035-STPS-2018 5.3", severidad_falta="grave"),
    ObligacionNOM035("examenes_medicos_expuestos",
                     "Practicar exámenes médicos/evaluaciones psicológicas a expuestos con signos de alteración (5.6).",
                     aplica_si_empleados_min=16, base_legal="NOM-035-STPS-2018 5.6", severidad_falta="grave"),
    ObligacionNOM035("registros_resultados",
                     "Llevar registros de resultados, medidas de control y trabajadores evaluados (5.8).",
                     aplica_si_empleados_min=16, base_legal="NOM-035-STPS-2018 5.8", severidad_falta="media"),
]

CATALOGO_NOM037: list[ObligacionNOM037] = [
    ObligacionNOM037("listado_teletrabajadores", "Listado actualizado de personas en teletrabajo con los datos del 5.1.",
                     base_legal="NOM-037-STPS-2023 5.1"),
    ObligacionNOM037("politica_teletrabajo",
                     "Política de Teletrabajo escrita y difundida, que incluya horarios, pausas y desconexión (5.2).",
                     base_legal="NOM-037-STPS-2023 5.2", severidad_falta="grave"),
    ObligacionNOM037("lista_verificacion_condiciones", "Lista de verificación de condiciones de SST del lugar de teletrabajo (5.4).",
                     base_legal="NOM-037-STPS-2023 5.4"),
    ObligacionNOM037("silla_y_equipo", "Proporcionar silla ergonómica u otra apropiada y equipo de cómputo/TIC (5.7; LFT 330-E fr. I).",
                     base_legal="NOM-037-STPS-2023 5.7; LFT Art. 330-E fr. I", severidad_falta="grave"),
    ObligacionNOM037("costos_telecom_electricidad", "Asumir costos de telecomunicación y la parte proporcional de electricidad.",
                     base_legal="LFT Art. 330-E fr. III", fundamento_multa="lft_1002", severidad_falta="grave"),
    ObligacionNOM037("capacitacion_anual", "Capacitación al menos una vez al año sobre condiciones de SST en teletrabajo (5.9).",
                     base_legal="NOM-037-STPS-2023 5.9"),
    ObligacionNOM037("reversibilidad", "Mecanismos de reversibilidad a la modalidad presencial (5.10).",
                     base_legal="NOM-037-STPS-2023 5.10", severidad_falta="grave"),
    ObligacionNOM037("violencia_familiar", "Mecanismos de atención para casos de violencia familiar (5.13).",
                     base_legal="NOM-037-STPS-2023 5.13"),
    ObligacionNOM037("contrato_escrito", "Condiciones de teletrabajo por escrito en contrato (LFT Art. 330-B).",
                     base_legal="LFT Art. 330-B", fundamento_multa="lft_1002", severidad_falta="muy_grave"),
]

CATALOGO_DESCONEXION_DIGITAL: list[ObligacionLeySilla] = [
    ObligacionLeySilla(
        clave="respetar_desconexion_teletrabajo",
        descripcion="Respetar el derecho a la desconexión de las personas en teletrabajo al término de la jornada.",
        aplica_giros=TODOS_GIROS,
        base_legal="LFT Art. 330-E fr. VI (DOF 11-01-2021)",
        severidad_falta="grave",
    ),
    ObligacionLeySilla(
        clave="politica_desconexion_teletrabajo",
        descripcion=("Incluir en la Política de Teletrabajo el derecho a pausas y a la desconexión "
                     "(también de las TIC) fuera de jornada, vacaciones, permisos y licencias."),
        aplica_giros=TODOS_GIROS,
        base_legal="NOM-037-STPS-2023 5.2 e)",
        fundamento_multa="lft_994_v",
        severidad_falta="media",
    ),
]


def calcular_multa_mxn(fundamento: FundamentoMulta, reincidente: bool = False,
                       uma_diaria: float = UMA_2026_DIARIA) -> tuple[float, float]:
    """(min, max) en MXN. Reincidencia: se duplica (Art. 992 LFT)."""
    rango = TABLA_MULTAS_LFT[fundamento]
    factor = 2.0 if reincidente else 1.0
    return (rango.rango_min_uma * uma_diaria * factor, rango.rango_max_uma * uma_diaria * factor)


def obligaciones_aplicables_ley_silla(giro: GiroTrabajo) -> list[ObligacionLeySilla]:
    return [o for o in CATALOGO_LEY_SILLA if giro in o.aplica_giros]


def obligaciones_aplicables_nom035(num_empleados: int) -> list[ObligacionNOM035]:
    return [o for o in CATALOGO_NOM035
            if num_empleados >= o.aplica_si_empleados_min
            and (o.aplica_si_empleados_max is None or num_empleados <= o.aplica_si_empleados_max)]


def obligaciones_aplicables_nom037(modalidad_remota: bool) -> list[ObligacionNOM037]:
    return list(CATALOGO_NOM037) if modalidad_remota else []


def obligaciones_desconexion_digital(giro: GiroTrabajo, modalidad_remota: bool = True) -> list[ObligacionLeySilla]:
    """La desconexión legal solo aplica a teletrabajo (LFT 330-E fr. VI)."""
    if not modalidad_remota:
        return []
    return [o for o in CATALOGO_DESCONEXION_DIGITAL if giro in o.aplica_giros]


__all__ = [
    "UMA_2026_DIARIA", "URL_LFT", "URL_NOM035", "URL_NOM037",
    "FECHA_LEY_SILLA_DOF", "FECHA_LEY_SILLA_VIGOR", "FECHA_LEY_SILLA_NORMATIVA_INTERNA",
    "Severidad", "FundamentoMulta", "GiroTrabajo",
    "MultaLFT", "ObligacionLeySilla", "ObligacionNOM035", "ObligacionNOM037",
    "TABLA_MULTAS_LFT", "CATALOGO_LEY_SILLA", "CATALOGO_NOM035", "CATALOGO_NOM037",
    "CATALOGO_DESCONEXION_DIGITAL",
    "calcular_multa_mxn",
    "obligaciones_aplicables_ley_silla", "obligaciones_aplicables_nom035",
    "obligaciones_aplicables_nom037", "obligaciones_desconexion_digital",
]
