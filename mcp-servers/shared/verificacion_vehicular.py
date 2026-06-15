"""Verificación vehicular estatal — CDMX, EdoMex y 5 más.

CDMX/EdoMex/Hidalgo/Morelos/Puebla operan el programa Hoy No Circula
y verificación obligatoria cada 6 meses según engomado.

Engomados y semáforos:
  - Amarillo (terminación 5,6): Marzo, Julio, Noviembre
  - Rosa (terminación 7,8):     Abril, Agosto, Diciembre
  - Roja (terminación 3,4):     Mayo, Septiembre, Enero
  - Verde (terminación 1,2):    Junio, Octubre, Febrero
  - Azul (terminación 9,0):     Enero, Mayo, Septiembre
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Holograma = Literal["00", "0", "1", "2", "Exento", "Rechazo"]
ColorEngomado = Literal["amarillo", "rosa", "rojo", "verde", "azul"]


# Selectores reales descubiertos 2026-06-15 (Playwright) — SAF CDMX consulta adeudos
# Endpoint público, sin Llave CDMX. Útil para verificación + tenencia.
URL_SAF_CDMX_CONSULTA = "https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana"
SAF_CDMX_FIELDS = {"placa": "inputPlaca", "captcha": "captcha_code"}

# Path con Llave CDMX (OAuth2) — opcional, requiere identidad digital del usuario
URL_TRAMITES_CDMX_VERIFICACION = "https://tramites.cdmx.gob.mx/fotocivicas/public/consulta-verificacion"
URL_LLAVE_CDMX_OAUTH = "https://llave.cdmx.gob.mx/oauth.xhtml"


@dataclass
class ProgramaVerificacion:
    clave: str
    nombre_estado: str
    activo: bool
    portal_url: str
    portal_consulta: str = ""
    frecuencia_meses: int = 6
    costo_mxn: float = 0.0
    permite_holograma_00: bool = True
    notas: str = ""


CATALOGO_VERIFICACION: list[ProgramaVerificacion] = [
    ProgramaVerificacion(
        clave="cdmx",
        nombre_estado="Ciudad de México",
        activo=True,
        portal_url="https://www.semovi.cdmx.gob.mx",
        portal_consulta="https://verificentros.cdmx.gob.mx",
        frecuencia_meses=6,
        costo_mxn=621.0,
        notas="SEMOVI — citas vía app/portal. Hoy No Circula activo.",
    ),
    ProgramaVerificacion(
        clave="edomex",
        nombre_estado="Estado de México",
        activo=True,
        portal_url="https://verificacion.edomex.gob.mx",
        portal_consulta="https://verificacion.edomex.gob.mx/citas",
        frecuencia_meses=6,
        costo_mxn=549.0,
        notas="Verificarte EdoMex. Compatible con Hoy No Circula ZMVM.",
    ),
    ProgramaVerificacion(
        clave="hgo",
        nombre_estado="Hidalgo",
        activo=True,
        portal_url="https://www.hidalgo.gob.mx/verificacion",
        frecuencia_meses=6,
        costo_mxn=470.0,
    ),
    ProgramaVerificacion(
        clave="mor",
        nombre_estado="Morelos",
        activo=True,
        portal_url="https://www.morelos.gob.mx/verificacion",
        frecuencia_meses=6,
        costo_mxn=485.0,
    ),
    ProgramaVerificacion(
        clave="pue",
        nombre_estado="Puebla",
        activo=True,
        portal_url="https://www.puebla.gob.mx/verificacion",
        frecuencia_meses=6,
        costo_mxn=505.0,
    ),
    ProgramaVerificacion(
        clave="tlax",
        nombre_estado="Tlaxcala",
        activo=True,
        portal_url="https://www.tlaxcala.gob.mx/verificacion",
        frecuencia_meses=6,
        costo_mxn=445.0,
    ),
    ProgramaVerificacion(
        clave="jal",
        nombre_estado="Jalisco",
        activo=True,
        portal_url="https://semadet.jalisco.gob.mx/verificacion",
        frecuencia_meses=6,
        costo_mxn=520.0,
        notas="Programa estatal Jalisco GDL.",
    ),
]


def buscar_programa(clave: str) -> ProgramaVerificacion | None:
    cn = clave.strip().lower()
    for p in CATALOGO_VERIFICACION:
        if p.clave == cn:
            return p
    return None


def calcular_proximo_periodo(terminacion_placa: int, mes_actual: int) -> tuple[str, list[int]]:
    """Calcula color de engomado + meses de verificación.

    Args:
        terminacion_placa: último dígito de la placa (0-9).
        mes_actual: 1-12.

    Returns:
        (color, [meses_obligatorios])
    """
    if not (0 <= terminacion_placa <= 9):
        raise ValueError("terminacion debe ser 0-9")
    # Mapeo terminación → color
    if terminacion_placa in (5, 6):
        return ("amarillo", [3, 7, 11])
    if terminacion_placa in (7, 8):
        return ("rosa", [4, 8, 12])
    if terminacion_placa in (3, 4):
        return ("rojo", [5, 9, 1])
    if terminacion_placa in (1, 2):
        return ("verde", [6, 10, 2])
    return ("azul", [1, 5, 9])  # 9 y 0


def mes_proxima_verificacion(terminacion: int, mes_actual: int) -> int:
    """Devuelve el siguiente mes en que toca verificar."""
    _, meses = calcular_proximo_periodo(terminacion, mes_actual)
    # Buscar el siguiente mes >= mes_actual
    futuros = [m for m in meses if m >= mes_actual]
    return min(futuros) if futuros else min(meses) + 12  # próximo año


__all__ = ["ProgramaVerificacion", "Holograma", "ColorEngomado", "CATALOGO_VERIFICACION",
           "buscar_programa", "calcular_proximo_periodo", "mes_proxima_verificacion"]
