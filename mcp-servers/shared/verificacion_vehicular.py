"""Verificación vehicular — Megalópolis (CDMX, EdoMex y estados de la CAMe).

Calendario 2026 (SEDEMA CDMX, Gaceta Oficial 2-ene-2026, reportado por Crónica,
ADN40, N+, Chilango; revisado 2026-10-14). Dos meses por semestre según el
color del engomado / último dígito de la placa:

  Amarillo (5, 6): ene–feb y jul–ago
  Rosa     (7, 8): feb–mar y ago–sep
  Rojo     (3, 4): mar–abr y sep–oct
  Verde    (1, 2): abr–may y oct–nov
  Azul     (9, 0): may–jun y nov–dic
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


Holograma = Literal["00", "0", "1", "2", "Exento", "Rechazo"]
ColorEngomado = Literal["amarillo", "rosa", "rojo", "verde", "azul"]

FUENTES_CALENDARIO_2026 = (
    "https://www.cronica.com.mx/metropoli/2026/01/02/anuncian-calendario-de-verificacion-vehicular-en-la-cdmx-para-enero-junio-de-2026/",
    "https://www.nmas.com.mx/ciudad-de-mexico/movilidad/calendario-verificacion-segundo-semestre-2026-cdmx-placas-engomados-fechas-limite/",
)

# Endpoint público SAF CDMX (CAPTCHA imagen → handoff humano, ver shared.portal_handoff)
URL_SAF_CDMX_CONSULTA = "https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana"


@dataclass
class ProgramaVerificacion:
    clave: str
    nombre_estado: str
    activo: bool
    portal_url: str
    portal_consulta: str = ""
    frecuencia_meses: int = 6
    costo_mxn: Optional[float] = None  # None = sin fuente 2026
    verificado_2026: bool = False
    fuentes: tuple[str, ...] = field(default_factory=tuple)
    notas: str = ""


CATALOGO_VERIFICACION: list[ProgramaVerificacion] = [
    ProgramaVerificacion(
        clave="cdmx", nombre_estado="Ciudad de México", activo=True,
        portal_url="https://www.sedema.cdmx.gob.mx/programas/programa/verificacion-vehicular",
        portal_consulta=URL_SAF_CDMX_CONSULTA,
        costo_mxn=765.45, verificado_2026=True,
        fuentes=("https://www.eluniversal.com.mx/consultas/verificacion-vehicular/",),
        notas="5.625 UMA + IVA, igual para todos los hologramas. Multa por extemporánea: 20 UMA.",
    ),
    ProgramaVerificacion(
        clave="edomex", nombre_estado="Estado de México", activo=True,
        portal_url="https://citaverificacion.edomex.gob.mx/RegistroCitas/",
        costo_mxn=469.24, verificado_2026=True,
        fuentes=("https://www.unotv.com/estados/estado-de-mexico/verificacion-vehicular-en-edomex-precio-actualizado-en-2026-tras-el-aumento-de-la-uma/",),
        notas="Costo hologramas 1 y 2. Holograma 0: ~$610; 00: ~$1,196. Multa: 30 UMA.",
    ),
    ProgramaVerificacion(clave="hgo", nombre_estado="Hidalgo", activo=True,
                         portal_url="https://www.hidalgo.gob.mx", notas="Costo 2026 sin fuente."),
    ProgramaVerificacion(clave="mor", nombre_estado="Morelos", activo=True,
                         portal_url="https://www.morelos.gob.mx", notas="Costo 2026 sin fuente."),
    ProgramaVerificacion(clave="pue", nombre_estado="Puebla", activo=True,
                         portal_url="https://www.puebla.gob.mx", notas="Costo 2026 sin fuente."),
    ProgramaVerificacion(clave="tlax", nombre_estado="Tlaxcala", activo=True,
                         portal_url="https://www.tlaxcala.gob.mx", notas="Costo 2026 sin fuente."),
    ProgramaVerificacion(clave="jal", nombre_estado="Jalisco", activo=True,
                         portal_url="https://semadet.jalisco.gob.mx",
                         notas="Programa propio (no Megalópolis): el calendario de engomados no aplica."),
]

# terminación → (color, meses de verificación del año)
_CALENDARIO: dict[int, tuple[str, list[int]]] = {
    5: ("amarillo", [1, 2, 7, 8]), 6: ("amarillo", [1, 2, 7, 8]),
    7: ("rosa", [2, 3, 8, 9]), 8: ("rosa", [2, 3, 8, 9]),
    3: ("rojo", [3, 4, 9, 10]), 4: ("rojo", [3, 4, 9, 10]),
    1: ("verde", [4, 5, 10, 11]), 2: ("verde", [4, 5, 10, 11]),
    9: ("azul", [5, 6, 11, 12]), 0: ("azul", [5, 6, 11, 12]),
}


def buscar_programa(clave: str) -> ProgramaVerificacion | None:
    cn = clave.strip().lower()
    for p in CATALOGO_VERIFICACION:
        if p.clave == cn:
            return p
    return None


def calcular_proximo_periodo(terminacion_placa: int, mes_actual: int) -> tuple[str, list[int]]:
    """(color de engomado, meses en que toca verificar) según la terminación."""
    if not (0 <= terminacion_placa <= 9):
        raise ValueError("terminacion debe ser 0-9")
    return _CALENDARIO[terminacion_placa]


def mes_proxima_verificacion(terminacion: int, mes_actual: int) -> int:
    """Siguiente mes del calendario >= mes_actual; >12 significa el año siguiente."""
    _, meses = calcular_proximo_periodo(terminacion, mes_actual)
    futuros = [m for m in meses if m >= mes_actual]
    return min(futuros) if futuros else min(meses) + 12


__all__ = ["ProgramaVerificacion", "Holograma", "ColorEngomado", "CATALOGO_VERIFICACION",
           "FUENTES_CALENDARIO_2026", "URL_SAF_CDMX_CONSULTA",
           "buscar_programa", "calcular_proximo_periodo", "mes_proxima_verificacion"]
