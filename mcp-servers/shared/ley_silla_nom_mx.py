"""Compliance Ley Silla + NOM-035 + NOM-037 + Desconexión Digital — México 2026.

Marco legal:
- Ley Silla (reforma LFT publicada DOF 17-jul-2025) — sillas ergonómicas obligatorias
- NOM-035-STPS-2018 — riesgos psicosociales (política + cuestionarios + programa)
- NOM-037-STPS-2023 — teletrabajo (sillas, equipo, smartphone si aplica)
- Reforma LFT Art. 132 marzo 2026 — desconexión digital obligatoria

Fase vigilancia STPS 2026: inspecciones con multas $29,327–$293,275 MXN
(reincidencia hasta $586,550 MXN) + suspensión operaciones.

Universo: 4M empresas formales mexicanas con trabajadores.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


# Constantes UMA 2026 (Unidad de Medida y Actualización)
UMA_2026_DIARIA = 113.07  # MXN. Actualizar cada año (Banxico/INEGI).


Severidad = Literal["leve", "media", "grave", "muy_grave"]
GiroTrabajo = Literal[
    "retail_comercio",       # tiendas, supermercados — pie prolongado
    "manufactura",           # planta, ensamble — pie prolongado
    "servicios_personales",  # estéticas, salones — pie prolongado
    "oficina_administrativo",
    "teletrabajo_hibrido",
    "almacen_logistica",
    "salud",
    "educacion",
    "construccion",
    "otro",
]


@dataclass
class ObligacionLeySilla:
    """Una obligación específica de Ley Silla por giro."""
    clave: str
    descripcion: str
    aplica_giros: list[GiroTrabajo]
    aplica_si_empleados_min: int = 1
    base_legal: str = "LFT Reforma DOF 17-jul-2025"
    severidad_falta: Severidad = "media"


@dataclass
class ObligacionNOM035:
    """Una obligación NOM-035-STPS-2018 por tramo de empleados."""
    clave: str
    descripcion: str
    aplica_si_empleados_min: int = 16
    aplica_si_empleados_max: Optional[int] = None
    base_legal: str = "NOM-035-STPS-2018"
    severidad_falta: Severidad = "media"


@dataclass
class ObligacionNOM037:
    """Una obligación NOM-037-STPS-2023 (teletrabajo)."""
    clave: str
    descripcion: str
    aplica_si_modalidad_remota: bool = True
    base_legal: str = "NOM-037-STPS-2023"
    severidad_falta: Severidad = "media"


@dataclass
class MultaSTPS:
    severidad: Severidad
    rango_min_uma: int   # en UMAS diarias
    rango_max_uma: int


# ============================================================
# CATÁLOGO LEY SILLA
# ============================================================
CATALOGO_LEY_SILLA: list[ObligacionLeySilla] = [
    ObligacionLeySilla(
        clave="silla_ergonomica_disponible",
        descripcion="Proveer silla ergonómica con respaldo a TODO trabajador cuya actividad lo permita.",
        aplica_giros=["retail_comercio", "manufactura", "servicios_personales", "oficina_administrativo", "almacen_logistica", "salud", "educacion", "otro"],
        severidad_falta="grave",
    ),
    ObligacionLeySilla(
        clave="descansos_intermitentes",
        descripcion="Establecer descansos cada 4 horas para puestos con pie prolongado.",
        aplica_giros=["retail_comercio", "manufactura", "servicios_personales", "almacen_logistica", "construccion"],
        severidad_falta="grave",
    ),
    ObligacionLeySilla(
        clave="reglamento_interior_actualizado",
        descripcion="Actualizar reglamento interior de trabajo incluyendo derecho al descanso y silla.",
        aplica_giros=["retail_comercio", "manufactura", "servicios_personales", "oficina_administrativo", "almacen_logistica", "salud", "educacion", "construccion", "otro"],
        severidad_falta="media",
    ),
    ObligacionLeySilla(
        clave="capacitacion_anual_silla",
        descripcion="Capacitación anual sobre ergonomía y uso correcto de silla.",
        aplica_giros=["retail_comercio", "manufactura", "servicios_personales", "almacen_logistica"],
        severidad_falta="leve",
    ),
    ObligacionLeySilla(
        clave="evaluacion_ergonomica_puestos",
        descripcion="Evaluación ergonómica documentada de cada puesto con pie prolongado.",
        aplica_giros=["retail_comercio", "manufactura", "almacen_logistica", "construccion"],
        severidad_falta="grave",
    ),
]


# ============================================================
# CATÁLOGO NOM-035 (riesgos psicosociales)
# ============================================================
CATALOGO_NOM035: list[ObligacionNOM035] = [
    ObligacionNOM035(
        clave="politica_prevencion_psicosociales",
        descripcion="Política documentada de prevención de riesgos psicosociales firmada por dirección.",
        aplica_si_empleados_min=1,
        severidad_falta="grave",
    ),
    ObligacionNOM035(
        clave="cuestionario_acontecimientos_traumaticos_15",
        descripcion="Aplicar cuestionario de acontecimientos traumáticos (Guía I) — empresas ≤15 empleados.",
        aplica_si_empleados_min=1,
        aplica_si_empleados_max=15,
        severidad_falta="media",
    ),
    ObligacionNOM035(
        clave="cuestionario_factores_riesgo_50",
        descripcion="Aplicar cuestionario de factores de riesgo psicosocial (Guía II) — 16-50 empleados.",
        aplica_si_empleados_min=16,
        aplica_si_empleados_max=50,
        severidad_falta="grave",
    ),
    ObligacionNOM035(
        clave="cuestionario_entorno_organizacional_50",
        descripcion="Aplicar cuestionario de entorno organizacional favorable (Guía III) — >50 empleados.",
        aplica_si_empleados_min=51,
        severidad_falta="grave",
    ),
    ObligacionNOM035(
        clave="programa_prevencion_documentado",
        descripcion="Programa de prevención de factores de riesgo psicosocial documentado.",
        aplica_si_empleados_min=51,
        severidad_falta="grave",
    ),
    ObligacionNOM035(
        clave="medidas_contra_violencia_laboral",
        descripcion="Medidas y protocolo contra violencia laboral, acoso y discriminación.",
        aplica_si_empleados_min=1,
        severidad_falta="muy_grave",
        base_legal="NOM-035 + reforma 2026 violencia laboral",
    ),
    ObligacionNOM035(
        clave="exam_medico_indicadores_riesgo",
        descripcion="Examen médico a trabajadores expuestos con indicadores de riesgo.",
        aplica_si_empleados_min=16,
        severidad_falta="grave",
    ),
    ObligacionNOM035(
        clave="capacitacion_anual_psicosocial",
        descripcion="Capacitación anual a trabajadores sobre factores psicosociales.",
        aplica_si_empleados_min=51,
        severidad_falta="media",
    ),
]


# ============================================================
# CATÁLOGO NOM-037 (teletrabajo)
# ============================================================
CATALOGO_NOM037: list[ObligacionNOM037] = [
    ObligacionNOM037(
        clave="silla_ergonomica_remota",
        descripcion="Proveer silla ergonómica al trabajador remoto (o equivalente).",
        severidad_falta="grave",
    ),
    ObligacionNOM037(
        clave="computadora_o_tableta_remota",
        descripcion="Proveer computadora o tableta para teletrabajo.",
        severidad_falta="muy_grave",
    ),
    ObligacionNOM037(
        clave="conectividad_internet",
        descripcion="Pagar o reembolsar costo proporcional de internet.",
        severidad_falta="grave",
    ),
    ObligacionNOM037(
        clave="conectividad_electricidad",
        descripcion="Pagar o reembolsar costo proporcional de electricidad.",
        severidad_falta="grave",
    ),
    ObligacionNOM037(
        clave="lista_verificacion_centro_trabajo",
        descripcion="Lista de verificación firmada del centro de trabajo remoto.",
        severidad_falta="media",
    ),
    ObligacionNOM037(
        clave="capacitacion_inicial_remota",
        descripcion="Capacitación inicial al adoptar teletrabajo sobre SST en hogar.",
        severidad_falta="media",
    ),
    ObligacionNOM037(
        clave="politica_reversibilidad",
        descripcion="Política de reversibilidad (volver a presencial sin perjuicio).",
        severidad_falta="grave",
    ),
    ObligacionNOM037(
        clave="contrato_modalidad_teletrabajo",
        descripcion="Contrato individual con modalidad de teletrabajo escrito.",
        severidad_falta="muy_grave",
    ),
]


# ============================================================
# DESCONEXIÓN DIGITAL (Reforma LFT marzo 2026 Art. 132)
# ============================================================
CATALOGO_DESCONEXION_DIGITAL: list[ObligacionLeySilla] = [
    ObligacionLeySilla(
        clave="politica_desconexion_digital",
        descripcion="Política formal de desconexión digital al término de jornada.",
        aplica_giros=["retail_comercio", "manufactura", "servicios_personales", "oficina_administrativo", "teletrabajo_hibrido", "almacen_logistica", "salud", "educacion", "construccion", "otro"],
        base_legal="LFT Art. 132 reforma marzo 2026",
        severidad_falta="grave",
    ),
    ObligacionLeySilla(
        clave="capacitacion_desconexion",
        descripcion="Capacitar a personal jerárquico sobre respetar desconexión digital.",
        aplica_giros=["retail_comercio", "manufactura", "servicios_personales", "oficina_administrativo", "teletrabajo_hibrido", "almacen_logistica", "salud", "educacion", "construccion", "otro"],
        base_legal="LFT Art. 132 reforma marzo 2026",
        severidad_falta="media",
    ),
    ObligacionLeySilla(
        clave="canal_denuncia_desconexion",
        descripcion="Canal interno para denunciar violación al derecho de desconexión.",
        aplica_giros=["retail_comercio", "manufactura", "servicios_personales", "oficina_administrativo", "teletrabajo_hibrido", "almacen_logistica", "salud", "educacion", "construccion", "otro"],
        base_legal="LFT Art. 132 reforma marzo 2026",
        severidad_falta="leve",
    ),
]


# ============================================================
# MULTAS STPS por severidad (en UMAS diarias)
# ============================================================
TABLA_MULTAS_STPS: dict[Severidad, MultaSTPS] = {
    "leve":      MultaSTPS("leve",      50,   500),    # ~$5,654 - $56,535 MXN
    "media":     MultaSTPS("media",     250,  2500),   # ~$28,267 - $282,675 MXN
    "grave":     MultaSTPS("grave",     500,  5000),   # ~$56,535 - $565,350 MXN
    "muy_grave": MultaSTPS("muy_grave", 1000, 5000),   # ~$113,070 - $565,350 MXN
}

# Reincidencia multiplica por 2 (hasta tope $586k según El Imparcial 2026)
FACTOR_REINCIDENCIA = 2.0


def calcular_multa_mxn(severidad: Severidad, reincidente: bool = False,
                        uma_diaria: float = UMA_2026_DIARIA) -> tuple[float, float]:
    """Devuelve (multa_min_mxn, multa_max_mxn)."""
    rango = TABLA_MULTAS_STPS[severidad]
    factor = FACTOR_REINCIDENCIA if reincidente else 1.0
    return (rango.rango_min_uma * uma_diaria * factor,
            rango.rango_max_uma * uma_diaria * factor)


def obligaciones_aplicables_ley_silla(giro: GiroTrabajo) -> list[ObligacionLeySilla]:
    return [o for o in CATALOGO_LEY_SILLA if giro in o.aplica_giros]


def obligaciones_aplicables_nom035(num_empleados: int) -> list[ObligacionNOM035]:
    res = []
    for o in CATALOGO_NOM035:
        if num_empleados < o.aplica_si_empleados_min:
            continue
        if o.aplica_si_empleados_max is not None and num_empleados > o.aplica_si_empleados_max:
            continue
        res.append(o)
    return res


def obligaciones_aplicables_nom037(modalidad_remota: bool) -> list[ObligacionNOM037]:
    if not modalidad_remota:
        return []
    return list(CATALOGO_NOM037)


def obligaciones_desconexion_digital(giro: GiroTrabajo) -> list[ObligacionLeySilla]:
    return [o for o in CATALOGO_DESCONEXION_DIGITAL if giro in o.aplica_giros]


__all__ = [
    "UMA_2026_DIARIA", "Severidad", "GiroTrabajo",
    "ObligacionLeySilla", "ObligacionNOM035", "ObligacionNOM037", "MultaSTPS",
    "CATALOGO_LEY_SILLA", "CATALOGO_NOM035", "CATALOGO_NOM037",
    "CATALOGO_DESCONEXION_DIGITAL", "TABLA_MULTAS_STPS",
    "calcular_multa_mxn",
    "obligaciones_aplicables_ley_silla",
    "obligaciones_aplicables_nom035",
    "obligaciones_aplicables_nom037",
    "obligaciones_desconexion_digital",
]
