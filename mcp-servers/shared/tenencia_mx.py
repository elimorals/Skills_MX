"""Catálogo unificado de Tenencia / Refrendo vehicular estatal MX.

La tenencia federal se eliminó en 2012, pero **algunos estados** la mantienen
con nombre y tasa propios. Universo: ~46M vehículos registrados en MX.

Estados que cobran tenencia/control vehicular 2026:
  - CDMX (no — solo refrendo placas anual)
  - EdoMex — tenencia + reemplaca + refrendo
  - Jalisco — refrendo + tenencia para autos > 250K
  - Nuevo León — solo refrendo placas
  - Querétaro — control vehicular anual
  - Oaxaca — tenencia
  - Sonora — emplacamiento + refrendo
  - Veracruz — refrendo + control
  - Chihuahua — refrendo
  - Sinaloa — refrendo
  - Tabasco, Tlaxcala, Hidalgo, Aguascalientes — refrendo

Cálculo de tenencia (cuando aplica):
  base = valor_factura × factor_depreciación(años)
  tenencia = base × tasa_estado  (0.5% - 3% típico)
  + derecho_refrendo placas (fijo $700-$1,500 MXN)
  + verificación (cuando obligatoria)

Subsidios comunes: < $300K MXN factura → exento o reducción 100% en muchos estados.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# Frecuencia de cobro
Frecuencia = Literal["anual", "bienal", "ninguna"]

# Método de consulta del portal
MetodoConsulta = Literal["publica", "publica_captcha", "login", "no_implementado"]


@dataclass
class EstadoTenencia:
    """Configuración por estado para tenencia/refrendo vehicular."""
    clave: str                # "edomex", "jal", "qro", etc.
    nombre_estado: str
    cobra_tenencia: bool      # True si aplica impuesto sobre valor
    cobra_refrendo: bool      # True si tiene refrendo anual de placas
    cobra_control_vehicular: bool = False
    tasa_tenencia_pct: float = 0.0   # % sobre valor depreciado (si aplica)
    costo_refrendo_mxn: float = 0.0  # costo fijo refrendo anual
    umbral_exencion_factura: float = 0.0  # autos debajo de este valor exentos
    portal_url: str = ""
    portal_consulta_url: str = ""
    frecuencia: Frecuencia = "anual"
    metodo: MetodoConsulta = "no_implementado"
    notas: str = ""


# Tasas y costos vigentes 2026 (verificables en SHCP estatal)
CATALOGO_TENENCIA: list[EstadoTenencia] = [
    EstadoTenencia(
        clave="edomex",
        nombre_estado="Estado de México",
        cobra_tenencia=True,
        cobra_refrendo=True,
        tasa_tenencia_pct=3.0,  # autos > $400K MXN factura
        costo_refrendo_mxn=940.0,
        umbral_exencion_factura=400000.0,
        portal_url="https://sfpya.edomexico.gob.mx/recaudacion",
        portal_consulta_url="https://sfpya.edomexico.gob.mx/recaudacion/tenencia",
        metodo="publica",
        notas="Subsidio 100% para autos < $400K. Tarifa progresiva por valor.",
    ),
    EstadoTenencia(
        clave="jal",
        nombre_estado="Jalisco",
        cobra_tenencia=True,
        cobra_refrendo=True,
        tasa_tenencia_pct=2.6,
        costo_refrendo_mxn=720.0,
        umbral_exencion_factura=250000.0,
        portal_url="https://sepaf.jalisco.gob.mx",
        portal_consulta_url="https://sepaf.jalisco.gob.mx/recaudaciondigital/refrendo",
        metodo="publica",
        notas="Subsidio < $250K. Refrendo + tenencia en un solo pago.",
    ),
    EstadoTenencia(
        clave="nl",
        nombre_estado="Nuevo León",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=782.0,
        portal_url="https://www.nl.gob.mx/finanzas",
        portal_consulta_url="https://www.nl.gob.mx/es/nlinea/refrendo-vehicular",
        metodo="publica",
        notas="Sin tenencia. Refrendo placas anual obligatorio.",
    ),
    EstadoTenencia(
        clave="qro",
        nombre_estado="Querétaro",
        cobra_tenencia=False,
        cobra_refrendo=True,
        cobra_control_vehicular=True,
        costo_refrendo_mxn=850.0,
        portal_url="https://sfqro.gob.mx",
        portal_consulta_url="https://sfqro.gob.mx/control-vehicular",
        metodo="publica",
        notas="Sin tenencia. Control Vehicular anual + refrendo.",
    ),
    EstadoTenencia(
        clave="oax",
        nombre_estado="Oaxaca",
        cobra_tenencia=True,
        cobra_refrendo=True,
        tasa_tenencia_pct=2.5,
        costo_refrendo_mxn=650.0,
        umbral_exencion_factura=150000.0,
        portal_url="https://www.finanzasoaxaca.gob.mx",
        metodo="publica_captcha",
    ),
    EstadoTenencia(
        clave="son",
        nombre_estado="Sonora",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=890.0,
        portal_url="https://hacienda.sonora.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="ver",
        nombre_estado="Veracruz",
        cobra_tenencia=False,
        cobra_refrendo=True,
        cobra_control_vehicular=True,
        costo_refrendo_mxn=720.0,
        portal_url="https://www.veracruz.gob.mx/finanzas",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="chih",
        nombre_estado="Chihuahua",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=685.0,
        portal_url="https://www.chihuahua.gob.mx/hacienda",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="sin",
        nombre_estado="Sinaloa",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=720.0,
        portal_url="https://saf.sinaloa.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="tam",
        nombre_estado="Tamaulipas",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=780.0,
        portal_url="https://finanzas.tamaulipas.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="ags",
        nombre_estado="Aguascalientes",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=695.0,
        portal_url="https://eservicios2.aguascalientes.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="hgo",
        nombre_estado="Hidalgo",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=665.0,
        portal_url="https://sefinanzas.hidalgo.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="bc",
        nombre_estado="Baja California",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=815.0,
        portal_url="https://www.bajacalifornia.gob.mx/finanzas",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="bcs",
        nombre_estado="Baja California Sur",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=720.0,
        portal_url="https://finanzasbcs.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="cam",
        nombre_estado="Campeche",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=650.0,
        portal_url="https://finanzas.campeche.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="yuc",
        nombre_estado="Yucatán",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=765.0,
        portal_url="https://www.yucatan.gob.mx/saf",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="mich",
        nombre_estado="Michoacán",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=720.0,
        portal_url="https://secfinanzas.michoacan.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="mor",
        nombre_estado="Morelos",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=695.0,
        portal_url="https://hacienda.morelos.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="slp",
        nombre_estado="San Luis Potosí",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=685.0,
        portal_url="https://finanzas.slp.gob.mx",
        metodo="publica",
    ),
    EstadoTenencia(
        clave="gto",
        nombre_estado="Guanajuato",
        cobra_tenencia=False,
        cobra_refrendo=True,
        costo_refrendo_mxn=720.0,
        portal_url="https://finanzas.guanajuato.gob.mx",
        metodo="publica",
    ),
]


# Factores de depreciación oficiales (años desde adquisición)
# Tabla SHCP típica: depreciación lineal hasta 9 años
FACTOR_DEPRECIACION: dict[int, float] = {
    0: 1.00,
    1: 0.85,
    2: 0.70,
    3: 0.60,
    4: 0.50,
    5: 0.40,
    6: 0.30,
    7: 0.20,
    8: 0.10,
    9: 0.10,  # > 9 años queda en 10%
}


def buscar_estado(clave: str) -> EstadoTenencia | None:
    """Busca un estado por clave."""
    clave_norm = clave.strip().lower()
    for e in CATALOGO_TENENCIA:
        if e.clave == clave_norm:
            return e
    return None


def listar_estados(solo_con_tenencia: bool = False) -> list[EstadoTenencia]:
    """Lista todos los estados o solo los que cobran tenencia."""
    if solo_con_tenencia:
        return [e for e in CATALOGO_TENENCIA if e.cobra_tenencia]
    return list(CATALOGO_TENENCIA)


def calcular_tenencia(
    estado_clave: str,
    valor_factura: float,
    anio_modelo: int,
    anio_actual: int | None = None,
) -> dict:
    """Calcula tenencia + refrendo proyectado.

    Args:
        estado_clave: ej. "edomex", "jal", "nl"
        valor_factura: valor original del vehículo (precio factura)
        anio_modelo: año del modelo (ej. 2020)
        anio_actual: año actual para depreciación (default: 2026)

    Returns:
        {
          "estado": str, "tenencia_mxn": float, "refrendo_mxn": float,
          "subtotal_mxn": float, "exento": bool, "factor_depreciacion": float,
          "valor_depreciado": float, "tasa_pct": float,
        }
    """
    from datetime import datetime
    if anio_actual is None:
        anio_actual = datetime.now().year
    estado = buscar_estado(estado_clave)
    if estado is None:
        raise ValueError(f"Estado '{estado_clave}' no en catálogo.")
    if valor_factura < 0:
        raise ValueError("valor_factura no puede ser negativo.")
    if anio_modelo > anio_actual + 1 or anio_modelo < 1970:
        raise ValueError(f"anio_modelo fuera de rango: {anio_modelo}")

    antiguedad = max(0, anio_actual - anio_modelo)
    factor = FACTOR_DEPRECIACION.get(antiguedad, 0.10)
    valor_depreciado = valor_factura * factor

    # ¿Aplica tenencia?
    exento = False
    tenencia = 0.0
    if estado.cobra_tenencia:
        if valor_factura < estado.umbral_exencion_factura:
            exento = True
        else:
            tenencia = round(valor_depreciado * estado.tasa_tenencia_pct / 100, 2)

    refrendo = estado.costo_refrendo_mxn if estado.cobra_refrendo else 0.0
    subtotal = round(tenencia + refrendo, 2)

    return {
        "estado": estado.clave,
        "estado_nombre": estado.nombre_estado,
        "anio_modelo": anio_modelo,
        "anio_actual": anio_actual,
        "antiguedad_anios": antiguedad,
        "valor_factura": valor_factura,
        "valor_depreciado": round(valor_depreciado, 2),
        "factor_depreciacion": factor,
        "tasa_tenencia_pct": estado.tasa_tenencia_pct,
        "cobra_tenencia": estado.cobra_tenencia,
        "cobra_refrendo": estado.cobra_refrendo,
        "umbral_exencion_factura": estado.umbral_exencion_factura,
        "exento_de_tenencia": exento,
        "tenencia_mxn": tenencia,
        "refrendo_mxn": refrendo,
        "subtotal_mxn": subtotal,
        "fuente": estado.portal_url,
    }


__all__ = [
    "EstadoTenencia",
    "Frecuencia",
    "MetodoConsulta",
    "CATALOGO_TENENCIA",
    "FACTOR_DEPRECIACION",
    "buscar_estado",
    "listar_estados",
    "calcular_tenencia",
]
