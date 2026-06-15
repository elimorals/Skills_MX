"""Llave MX — identidad digital ciudadana unificada gob.mx.

SSO ciudadano vinculado a CURP. Reemplaza claves separadas por dependencia.
Catálogo curado de trámites disponibles a través de Portal Unificado.
"""
from __future__ import annotations

from dataclasses import dataclass


URL_PORTAL_UNIFICADO = "https://www.gob.mx/tramites"
URL_LLAVE_MX = "https://www.llave.gob.mx"


@dataclass
class TramiteLlaveMX:
    clave: str
    nombre: str
    dependencia: str
    categoria: str
    requiere_e_firma: bool = False
    requiere_cita_presencial: bool = False
    url_directa: str = ""


# Catálogo demostrativo de trámites ciudadanos accesibles con Llave MX
CATALOGO_TRAMITES_LLAVE_MX: list[TramiteLlaveMX] = [
    TramiteLlaveMX("curp_consulta", "Consulta y descarga CURP", "RENAPO", "identidad",
                    url_directa="https://www.gob.mx/curp"),
    TramiteLlaveMX("curp_certificada", "CURP certificada con QR", "RENAPO", "identidad",
                    requiere_e_firma=True),
    TramiteLlaveMX("acta_nacimiento", "Acta de nacimiento en línea", "Registro Civil", "identidad",
                    url_directa="https://www.gob.mx/ActasRC"),
    TramiteLlaveMX("constancia_no_inhabilitacion", "Constancia no inhabilitación SFP",
                    "SFP", "compliance", requiere_e_firma=True),
    TramiteLlaveMX("no_antecedentes_penales", "Carta no antecedentes penales federal",
                    "FGR", "compliance"),
    TramiteLlaveMX("opinion_cumplimiento_32d", "Opinión 32-D cumplimiento SAT",
                    "SAT", "fiscal", requiere_e_firma=True),
    TramiteLlaveMX("constancia_situacion_fiscal", "CSF SAT", "SAT", "fiscal",
                    requiere_e_firma=True),
    TramiteLlaveMX("alta_rfc_pf", "Alta RFC PF", "SAT", "fiscal", requiere_cita_presencial=True),
    TramiteLlaveMX("imss_numero_seguridad", "Número de Seguridad Social", "IMSS", "salud"),
    TramiteLlaveMX("imss_constancia_semanas", "Semanas cotizadas IMSS", "IMSS", "salud"),
    TramiteLlaveMX("infonavit_constancia", "Constancia INFONAVIT", "INFONAVIT", "vivienda"),
    TramiteLlaveMX("infonavit_precalifica", "Precalifica crédito INFONAVIT", "INFONAVIT", "vivienda"),
    TramiteLlaveMX("pasaporte", "Cita pasaporte SRE", "SRE", "viaje", requiere_cita_presencial=True),
    TramiteLlaveMX("licencia_conducir", "Licencia conducir (depende del estado)",
                    "Movilidad estatal", "movilidad", requiere_cita_presencial=True),
    TramiteLlaveMX("becas_benito_juarez", "Becas Benito Juárez", "Bienestar", "becas"),
    TramiteLlaveMX("cedula_profesional", "Cédula profesional SEP", "SEP", "profesional"),
    TramiteLlaveMX("titulo_electronico", "Título profesional electrónico", "SEP", "profesional"),
    TramiteLlaveMX("repuve_consulta", "REPUVE consulta vehicular", "REPUVE", "vehicular"),
    TramiteLlaveMX("repep_inscripcion", "Inscripción REPEP no-llamadas", "PROFECO", "consumidor"),
    TramiteLlaveMX("denuncia_profeco", "Denuncia ciudadana PROFECO", "PROFECO", "consumidor"),
]


CATEGORIAS_LLAVE_MX = [
    "identidad", "fiscal", "salud", "vivienda", "viaje", "movilidad", "becas",
    "profesional", "vehicular", "consumidor", "compliance",
]


def listar_categorias() -> list[str]:
    return list(CATEGORIAS_LLAVE_MX)


def tramites_por_categoria(categoria: str) -> list[TramiteLlaveMX]:
    c = (categoria or "").lower()
    return [t for t in CATALOGO_TRAMITES_LLAVE_MX if t.categoria == c]


def tramites_por_dependencia(dependencia: str) -> list[TramiteLlaveMX]:
    d = (dependencia or "").upper()
    return [t for t in CATALOGO_TRAMITES_LLAVE_MX if t.dependencia.upper() == d]


def buscar_tramite(clave: str) -> TramiteLlaveMX | None:
    c = (clave or "").lower()
    for t in CATALOGO_TRAMITES_LLAVE_MX:
        if t.clave == c:
            return t
    return None


__all__ = [
    "URL_PORTAL_UNIFICADO", "URL_LLAVE_MX", "TramiteLlaveMX",
    "CATALOGO_TRAMITES_LLAVE_MX", "CATEGORIAS_LLAVE_MX",
    "listar_categorias", "tramites_por_categoria",
    "tramites_por_dependencia", "buscar_tramite",
]
