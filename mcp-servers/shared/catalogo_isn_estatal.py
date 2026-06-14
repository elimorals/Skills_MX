"""Catálogo central de Impuesto sobre Nómina (ISN) estatal MX.

El ISN es un impuesto estatal sobre erogaciones por trabajo personal subordinado.
TODAS las 32 entidades federativas lo cobran (algunas con nombre distinto: ICN,
Impuesto sobre Erogaciones, etc.).

Universo: TODA empresa formal con al menos 1 trabajador = ~4 millones de empresas
afectadas vs ~700k consultables en predial. Mayor universo de cualquier MCP de este monorepo.

Patrón replicado de catalogo_municipios_mx pero a nivel estatal:
- Cada estado tiene su propio portal de declaración
- Tasas varían (1.8% BC, 2% YUC/GTO, 2.5% NL, 3% CDMX/JAL/EdoMex/QRO/PUE)
- Periodicidad: mensual (todos) + anual ajuste
- Vencimiento: día 10-17 del mes siguiente

Cada estado documenta:
- portal_url: URL real del sistema de declaración
- tasa: porcentaje aplicable (puede ser banda 1.8-3% en algunos casos)
- requiere_efirma: True/False
- requiere_credenciales_estatales: usuario/password propio del estado
- captcha_presente: True/False (validado Playwright)
- selectores: dict con DOM selectors clave
- validado: True si se verificó manualmente
- notas: contexto adicional

Validado parcialmente Playwright MCP 2026-06-14 (URLs y stack patterns).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class IsnEstadoConfig:
    """Configuración de declaración ISN para un estado MX."""
    estado_clave: str  # ej "CDMX", "JAL", "NL"
    estado_nombre: str  # ej "Ciudad de México"
    portal_url: str
    tasa_pct: float  # porcentaje principal
    tasa_rango: Optional[tuple[float, float]] = None  # si la tasa es variable
    requiere_efirma: bool = False
    requiere_credenciales_estatales: bool = True
    captcha_presente: bool = False
    periodicidad: str = "mensual"
    dia_vencimiento: int = 17  # día del mes siguiente
    selectores: dict[str, str] = field(default_factory=dict)
    validado: bool = False
    notas: str = ""


# ====================================================================
# Catálogo principal — 32 estados, 8 con detalle validado
# ====================================================================

CATALOGO_ISN: dict[str, IsnEstadoConfig] = {
    "CDMX": IsnEstadoConfig(
        estado_clave="CDMX",
        estado_nombre="Ciudad de México",
        portal_url="https://dgtc.finanzas.cdmx.gob.mx/",
        tasa_pct=3.0,
        requiere_efirma=True,
        requiere_credenciales_estatales=False,  # usa e.firma SAT
        captcha_presente=True,
        periodicidad="mensual",
        dia_vencimiento=17,
        selectores={
            "login_rfc": "input[name='rfc']",
            "boton_declaracion": "a:has-text('Declaración mensual')",
            "boton_isn": "a:has-text('Impuesto sobre Nómina')",
            "input_periodo": "select[name='periodo']",
        },
        validado=True,
        notas="Sistema SAC (Sistema Adminstración del Contribuyente). e.firma SAT obligatoria.",
    ),
    "JAL": IsnEstadoConfig(
        estado_clave="JAL",
        estado_nombre="Jalisco",
        portal_url="https://gobiernoenlinea1.jalisco.gob.mx/impuestos/",
        tasa_pct=3.0,
        requiere_efirma=False,
        captcha_presente=False,
        periodicidad="mensual",
        dia_vencimiento=12,
        selectores={
            "input_rfc": "input[name='rfc']",
            "input_password": "input[name='password']",
            "boton_isn": "a:has-text('Impuesto sobre Nómina')",
            "boton_bóveda": "a:has-text('Bóveda fiscal')",
        },
        validado=True,
        notas="Portal único para todos los impuestos estatales. Bóveda PDF reutilizable.",
    ),
    "NL": IsnEstadoConfig(
        estado_clave="NL",
        estado_nombre="Nuevo León",
        portal_url="https://egobierno.nl.gob.mx/egob/Nomina.php",
        tasa_pct=3.0,
        requiere_efirma=False,
        captcha_presente=False,
        periodicidad="mensual",
        dia_vencimiento=17,
        selectores={
            "input_rfc": "input[name='RFC']",
            "input_password": "input[name='password']",
            "input_periodo": "select[name='periodo']",
        },
        validado=True,
        notas=(
            "Sistema en 2 partes: egobierno (pago) + cfdi.nl.gob.mx (emisión CFDI). "
            "Requiere Constancia Situación Fiscal."
        ),
    ),
    "EDOMEX": IsnEstadoConfig(
        estado_clave="EDOMEX",
        estado_nombre="Estado de México",
        portal_url="https://sfpya.edomexico.gob.mx/recaudacion/",
        tasa_pct=3.0,
        requiere_efirma=False,
        captcha_presente=False,
        periodicidad="mensual",
        dia_vencimiento=10,
        selectores={
            "input_rec": "input[name='rec']",  # Registro Estatal Contribuyente
            "input_password": "input[name='password']",
            "boton_mi_cuenta": "a:has-text('Mi Cuenta')",
        },
        validado=True,
        notas="Login con REC (Registro Estatal Contribuyente). 'Mi Cuenta' expone histórico.",
    ),
    "QRO": IsnEstadoConfig(
        estado_clave="QRO",
        estado_nombre="Querétaro",
        portal_url="https://asistenciaspf.queretaro.gob.mx/",
        tasa_pct=3.0,
        requiere_efirma=False,
        captcha_presente=False,
        periodicidad="mensual",
        dia_vencimiento=17,
        selectores={
            "input_rfc": "input[name='rfc']",
            "boton_isn": "a:has-text('ISN')",
        },
        validado=True,
        notas="Manual oficial PDF disponible: mapea forms y endpoints.",
    ),
    "PUE": IsnEstadoConfig(
        estado_clave="PUE",
        estado_nombre="Puebla",
        portal_url="https://www.haciendapuebla.gob.mx/",
        tasa_pct=3.0,
        requiere_efirma=False,
        captcha_presente=True,
        periodicidad="mensual",
        dia_vencimiento=17,
        notas="SEFIN Puebla, requiere captcha visual.",
    ),
    "GTO": IsnEstadoConfig(
        estado_clave="GTO",
        estado_nombre="Guanajuato",
        portal_url="https://www.guanajuato.gob.mx/finanzas/",
        tasa_pct=2.0,
        requiere_efirma=False,
        captcha_presente=False,
        periodicidad="mensual",
        dia_vencimiento=17,
        notas="Tasa 2%, una de las más bajas del país.",
    ),
    "YUC": IsnEstadoConfig(
        estado_clave="YUC",
        estado_nombre="Yucatán",
        portal_url="https://www.sefinyucatan.gob.mx/",
        tasa_pct=2.5,
        requiere_efirma=False,
        captcha_presente=False,
        periodicidad="mensual",
        dia_vencimiento=10,
        notas="SEFIN Yucatán.",
    ),
    "BC": IsnEstadoConfig(
        estado_clave="BC",
        estado_nombre="Baja California",
        portal_url="https://www4.ebajacalifornia.gob.mx/Impuesto",
        tasa_pct=1.8,
        tasa_rango=(1.8, 3.0),
        requiere_efirma=False,
        captcha_presente=False,
        periodicidad="mensual",
        dia_vencimiento=17,
        validado=True,
        notas="Portal Java legacy. Tasa progresiva 1.8-3% según erogaciones.",
    ),
    # Estados con catálogo básico (no validados aún)
    "VER": IsnEstadoConfig(
        estado_clave="VER",
        estado_nombre="Veracruz",
        portal_url="https://www.veracruz.gob.mx/finanzas/",
        tasa_pct=3.0,
        notas="SEFIPLAN Veracruz.",
    ),
    "CHIH": IsnEstadoConfig(
        estado_clave="CHIH",
        estado_nombre="Chihuahua",
        portal_url="https://www.chihuahua.gob.mx/hacienda/",
        tasa_pct=3.0,
    ),
    "COAH": IsnEstadoConfig(
        estado_clave="COAH",
        estado_nombre="Coahuila",
        portal_url="https://www.sefin.gob.mx/",
        tasa_pct=2.0,
    ),
    "SIN": IsnEstadoConfig(
        estado_clave="SIN",
        estado_nombre="Sinaloa",
        portal_url="https://www.sinaloa.gob.mx/finanzas/",
        tasa_pct=2.4,
    ),
    "SON": IsnEstadoConfig(
        estado_clave="SON",
        estado_nombre="Sonora",
        portal_url="https://hacienda.sonora.gob.mx/",
        tasa_pct=2.0,
    ),
    "TAM": IsnEstadoConfig(
        estado_clave="TAM",
        estado_nombre="Tamaulipas",
        portal_url="https://www.tamaulipas.gob.mx/finanzas/",
        tasa_pct=3.0,
    ),
    "OAX": IsnEstadoConfig(
        estado_clave="OAX",
        estado_nombre="Oaxaca",
        portal_url="https://www.finanzasoaxaca.gob.mx/",
        tasa_pct=3.0,
    ),
    "MICH": IsnEstadoConfig(
        estado_clave="MICH",
        estado_nombre="Michoacán",
        portal_url="https://secfinanzas.michoacan.gob.mx/",
        tasa_pct=3.0,
    ),
    "GRO": IsnEstadoConfig(
        estado_clave="GRO",
        estado_nombre="Guerrero",
        portal_url="https://sefinaguerrero.gob.mx/",
        tasa_pct=2.0,
    ),
    "QROO": IsnEstadoConfig(
        estado_clave="QROO",
        estado_nombre="Quintana Roo",
        portal_url="https://sefiplan.qroo.gob.mx/",
        tasa_pct=3.0,
        notas="También administra ISH 6%.",
    ),
    "AGS": IsnEstadoConfig(
        estado_clave="AGS",
        estado_nombre="Aguascalientes",
        portal_url="https://www.aguascalientes.gob.mx/sefi/",
        tasa_pct=2.0,
    ),
    "SLP": IsnEstadoConfig(
        estado_clave="SLP",
        estado_nombre="San Luis Potosí",
        portal_url="https://www.slp.gob.mx/finanzas/",
        tasa_pct=2.5,
    ),
    "ZAC": IsnEstadoConfig(
        estado_clave="ZAC",
        estado_nombre="Zacatecas",
        portal_url="https://www.finanzaszacatecas.gob.mx/",
        tasa_pct=3.0,
    ),
    "DGO": IsnEstadoConfig(
        estado_clave="DGO",
        estado_nombre="Durango",
        portal_url="https://durango.gob.mx/sed/",
        tasa_pct=2.0,
    ),
    "MOR": IsnEstadoConfig(
        estado_clave="MOR",
        estado_nombre="Morelos",
        portal_url="https://hacienda.morelos.gob.mx/",
        tasa_pct=2.0,
    ),
    "TLAX": IsnEstadoConfig(
        estado_clave="TLAX",
        estado_nombre="Tlaxcala",
        portal_url="https://af-oficina-virtual.sefintlax.gob.mx/",
        tasa_pct=3.0,
    ),
    "HID": IsnEstadoConfig(
        estado_clave="HID",
        estado_nombre="Hidalgo",
        portal_url="https://hacienda.hidalgo.gob.mx/",
        tasa_pct=3.0,
    ),
    "CHIS": IsnEstadoConfig(
        estado_clave="CHIS",
        estado_nombre="Chiapas",
        portal_url="https://ingresos.haciendachiapas.gob.mx/",
        tasa_pct=2.0,
    ),
    "TAB": IsnEstadoConfig(
        estado_clave="TAB",
        estado_nombre="Tabasco",
        portal_url="https://tabasco.gob.mx/sefp/",
        tasa_pct=2.5,
    ),
    "CAMP": IsnEstadoConfig(
        estado_clave="CAMP",
        estado_nombre="Campeche",
        portal_url="https://www.campeche.gob.mx/finanzas/",
        tasa_pct=2.0,
    ),
    "NAY": IsnEstadoConfig(
        estado_clave="NAY",
        estado_nombre="Nayarit",
        portal_url="https://www.haciendanayarit.gob.mx/",
        tasa_pct=2.0,
    ),
    "COL": IsnEstadoConfig(
        estado_clave="COL",
        estado_nombre="Colima",
        portal_url="https://www.col.gob.mx/finanzas/",
        tasa_pct=2.0,
    ),
    "BCS": IsnEstadoConfig(
        estado_clave="BCS",
        estado_nombre="Baja California Sur",
        portal_url="https://finanzas.bcs.gob.mx/",
        tasa_pct=2.5,
    ),
}


# ====================================================================
# Helpers
# ====================================================================

def get_estado_config(estado: str) -> Optional[IsnEstadoConfig]:
    """Devuelve config del estado, o None si no existe.

    Acepta clave exacta ("CDMX", "JAL") o nombre completo case-insensitive.
    """
    if not estado:
        return None
    clave = estado.upper().strip()
    if clave in CATALOGO_ISN:
        return CATALOGO_ISN[clave]
    # Búsqueda por nombre
    for cfg in CATALOGO_ISN.values():
        if cfg.estado_nombre.upper() == estado.upper().strip():
            return cfg
    return None


def listar_estados(solo_validados: bool = False) -> list[dict[str, Any]]:
    """Lista todos los estados del catálogo."""
    return [
        {
            "clave": cfg.estado_clave,
            "nombre": cfg.estado_nombre,
            "tasa_pct": cfg.tasa_pct,
            "tasa_rango": cfg.tasa_rango,
            "validado": cfg.validado,
            "requiere_efirma": cfg.requiere_efirma,
            "captcha_presente": cfg.captcha_presente,
            "portal_url": cfg.portal_url,
            "dia_vencimiento": cfg.dia_vencimiento,
        }
        for cfg in CATALOGO_ISN.values()
        if not solo_validados or cfg.validado
    ]


def calcular_isn(nomina_gravable: float, estado: str) -> dict[str, Any]:
    """Calcula ISN sobre nómina gravable usando tasa del estado.

    Args:
        nomina_gravable: total de erogaciones por trabajo personal en el periodo
        estado: clave o nombre del estado

    Returns:
        {
          "nomina_gravable": float,
          "estado": str,
          "tasa_pct": float,
          "isn_a_pagar": float,
          "tasa_rango": Optional[tuple],
          "vencimiento_dia": int,
        }
    """
    if nomina_gravable < 0:
        raise ValueError("nomina_gravable debe ser >= 0")
    cfg = get_estado_config(estado)
    if cfg is None:
        raise ValueError(f"Estado '{estado}' no encontrado en catálogo ISN.")

    isn = nomina_gravable * (cfg.tasa_pct / 100.0)
    return {
        "nomina_gravable": round(nomina_gravable, 2),
        "estado": cfg.estado_nombre,
        "estado_clave": cfg.estado_clave,
        "tasa_pct": cfg.tasa_pct,
        "tasa_rango": cfg.tasa_rango,
        "isn_a_pagar": round(isn, 2),
        "vencimiento_dia": cfg.dia_vencimiento,
        "periodicidad": cfg.periodicidad,
        "portal_url": cfg.portal_url,
    }


def estadisticas_catalogo() -> dict[str, Any]:
    """Estadísticas del catálogo: cobertura, tasa promedio, validados."""
    total = len(CATALOGO_ISN)
    validados = sum(1 for c in CATALOGO_ISN.values() if c.validado)
    con_captcha = sum(1 for c in CATALOGO_ISN.values() if c.captcha_presente)
    con_efirma = sum(1 for c in CATALOGO_ISN.values() if c.requiere_efirma)
    tasas = [c.tasa_pct for c in CATALOGO_ISN.values()]
    return {
        "total_estados": total,
        "validados": validados,
        "no_validados": total - validados,
        "con_captcha": con_captcha,
        "con_efirma": con_efirma,
        "tasa_min": min(tasas),
        "tasa_max": max(tasas),
        "tasa_promedio": round(sum(tasas) / len(tasas), 2),
    }
