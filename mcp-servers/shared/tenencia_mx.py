"""Catálogo tenencia / refrendo vehicular estatal MX — datos 2026.

Revisado 2026-10-14 (grupo E1). Reglas:
- Solo se publica un monto si hay fuente 2026 citada; si no, el campo va en
  `None` y `verificado_2026=False`. Nada de tasas planas inventadas.
- La tenencia por encima del umbral de subsidio se calcula con la tarifa
  progresiva de cada código fiscal estatal; no se reproduce aquí (no se verificó
  el texto legal 2026), así que `tenencia_mxn=None` + `requiere_calculo_oficial`.
- Fuentes: notas de prensa 2026 que citan a las secretarías de finanzas
  (confianza "media"); no se localizó el acuerdo de subsidio en gaceta.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

MetodoConsulta = Literal["publica", "publica_captcha", "login", "no_implementado"]
Confianza = Literal["alta", "media", "baja"]


@dataclass
class EstadoTenencia:
    clave: str
    nombre_estado: str
    cobra_tenencia: bool
    cobra_refrendo: bool
    refrendo_mxn: Optional[float] = None  # automóvil particular, 2026
    umbral_subsidio_100_mxn: Optional[float] = None  # valor factura con IVA
    condiciones_subsidio: str = ""
    portal_url: str = ""
    metodo: MetodoConsulta = "no_implementado"
    verificado_2026: bool = False
    confianza: Confianza = "baja"
    fuentes: tuple[str, ...] = field(default_factory=tuple)
    notas: str = ""


_INFOBAE = "https://www.infobae.com/mexico/2026/03/31/tenencia-2026-fecha-limite-para-pagar-en-cdmx-edomex-puebla-y-queretaro/"
_UNOTV = "https://www.unotv.com/nacional/precio-del-refrendo-o-control-vehicular-en-todo-mexico-para-este-2026/"

CATALOGO_TENENCIA: list[EstadoTenencia] = [
    EstadoTenencia(
        clave="cdmx", nombre_estado="Ciudad de México",
        cobra_tenencia=True, cobra_refrendo=True, refrendo_mxn=760.0,
        umbral_subsidio_100_mxn=638_000.0,
        condiciones_subsidio="Sin adeudos de años anteriores, tarjeta de circulación vigente, pago en el plazo del subsidio.",
        portal_url="https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana",
        metodo="publica_captcha", verificado_2026=True, confianza="media",
        fuentes=(_INFOBAE, "https://www.record.com.mx/contra/cdmx-2026-subsidio-la-tenencia-sera-para-autos-de-hasta-638-mil-pesos-de-valor"),
    ),
    EstadoTenencia(
        clave="edomex", nombre_estado="Estado de México",
        cobra_tenencia=True, cobra_refrendo=True, refrendo_mxn=990.0,
        umbral_subsidio_100_mxn=638_000.0,
        condiciones_subsidio="Placas 2021 o posteriores (50% con placas 2020), registro estatal y sin adeudos.",
        portal_url="https://pagosytramites.edomex.gob.mx/recaudacion/",
        metodo="no_implementado", verificado_2026=True, confianza="media",
        fuentes=("https://www.nmas.com.mx/estado-de-mexico/cual-es-el-costo-refrendo-edomex-2026-como-obtener-subsidio-100-tenencia/",),
        notas="Otras notas reportan refrendo $960; se usa $990 (mayoría de fuentes).",
    ),
    EstadoTenencia(
        clave="qro", nombre_estado="Querétaro",
        cobra_tenencia=True, cobra_refrendo=True, refrendo_mxn=None,
        umbral_subsidio_100_mxn=800_000.0,
        condiciones_subsidio="'Cero Tenencia': refrendo pagado ene–mar, sin adeudos; motos excluidas.",
        verificado_2026=True, confianza="media",
        fuentes=("https://elcongresista.mx/politica/queretaro/queretaro-mantendra-cero-tenencia-en-2026-para-vehiculos-menores-a-800-mil", _INFOBAE),
        notas="Refrendo 2026 varía con el valor del vehículo ($760–$1,300).",
    ),
    EstadoTenencia(
        clave="jal", nombre_estado="Jalisco",
        cobra_tenencia=False, cobra_refrendo=True, refrendo_mxn=1000.0,
        portal_url="https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos",
        metodo="publica_captcha", verificado_2026=True, confianza="baja",
        fuentes=("https://www.adn40.mx/tramites/2026-03-03/adios-al-descuento-del-refrendo-vehicular-en-jalisco-esto-es-lo-que-desde-marzo-pagaran-los-conductores/",),
        notas="UnoTV reporta $1,100; fuentes en conflicto.",
    ),
    EstadoTenencia(
        clave="nl", nombre_estado="Nuevo León",
        cobra_tenencia=False, cobra_refrendo=True, refrendo_mxn=None,
        portal_url="https://www.icvnl.gob.mx/estadodecuenta",
        verificado_2026=False, confianza="baja", fuentes=(_UNOTV,),
        notas="Control vehicular depende del año modelo (UnoTV: 2015–2025 = $3,368). Confirmar en ICVNL.",
    ),
    EstadoTenencia(
        clave="pue", nombre_estado="Puebla", cobra_tenencia=False, cobra_refrendo=True,
        refrendo_mxn=700.0, verificado_2026=False, confianza="baja", fuentes=(_UNOTV, _INFOBAE),
        notas="Fuentes en conflicto sobre tenencia y monto (otra nota: $825).",
    ),
    EstadoTenencia(
        clave="mor", nombre_estado="Morelos", cobra_tenencia=False, cobra_refrendo=True,
        refrendo_mxn=814.0, verificado_2026=False, confianza="baja", fuentes=(_UNOTV,),
        notas="Estatus de tenencia no confirmado.",
    ),
    EstadoTenencia(
        clave="hgo", nombre_estado="Hidalgo", cobra_tenencia=False, cobra_refrendo=True,
        refrendo_mxn=None, verificado_2026=False, confianza="baja", fuentes=(_UNOTV,),
        notas="Solo hay monto 2025 ($1,177); 2026 no verificado.",
    ),
    EstadoTenencia(
        clave="oax", nombre_estado="Oaxaca", cobra_tenencia=False, cobra_refrendo=True,
        refrendo_mxn=None, verificado_2026=False, confianza="baja", fuentes=(_UNOTV,),
        notas="Sin información pública de monto 2026.",
    ),
    EstadoTenencia(
        clave="tlax", nombre_estado="Tlaxcala", cobra_tenencia=False, cobra_refrendo=True,
        refrendo_mxn=None, verificado_2026=False, confianza="baja", fuentes=(_UNOTV,),
        notas="Solo hay monto 2025 ($452); 2026 no verificado.",
    ),
]


def buscar_estado(clave: str) -> EstadoTenencia | None:
    clave_norm = clave.strip().lower()
    for e in CATALOGO_TENENCIA:
        if e.clave == clave_norm:
            return e
    return None


def listar_estados(solo_con_tenencia: bool = False) -> list[EstadoTenencia]:
    if solo_con_tenencia:
        return [e for e in CATALOGO_TENENCIA if e.cobra_tenencia]
    return list(CATALOGO_TENENCIA)


def calcular_tenencia(
    estado_clave: str,
    valor_factura: float,
    anio_modelo: int,
    anio_actual: int | None = None,
) -> dict:
    """Tenencia + refrendo 2026 con lo que hay verificado; `None` donde no.

    `valor_factura` es el valor de la factura con IVA (base del subsidio).
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

    advertencias: list[str] = []
    subsidio = False
    tenencia: Optional[float] = 0.0
    if estado.cobra_tenencia:
        umbral = estado.umbral_subsidio_100_mxn
        if umbral is not None and valor_factura <= umbral:
            subsidio = True
        else:
            tenencia = None
            advertencias.append(
                "Valor arriba del umbral de subsidio: la tenencia sigue la tarifa progresiva "
                "del código fiscal estatal, no verificada aquí. Consulta el monto en el portal oficial."
            )
    refrendo = estado.refrendo_mxn if estado.cobra_refrendo else 0.0
    if estado.cobra_refrendo and refrendo is None:
        advertencias.append("Refrendo 2026 no verificado para este estado.")
    if anio_actual != 2026:
        advertencias.append("Los montos del catálogo son de 2026.")
    if not estado.verificado_2026:
        advertencias.append("Datos de este estado sin verificación 2026 confiable.")

    subtotal = None if tenencia is None or refrendo is None else round(tenencia + refrendo, 2)
    return {
        "estado": estado.clave,
        "estado_nombre": estado.nombre_estado,
        "anio_modelo": anio_modelo,
        "anio_actual": anio_actual,
        "antiguedad_anios": max(0, anio_actual - anio_modelo),
        "valor_factura": valor_factura,
        "cobra_tenencia": estado.cobra_tenencia,
        "cobra_refrendo": estado.cobra_refrendo,
        "umbral_subsidio_100_mxn": estado.umbral_subsidio_100_mxn,
        "subsidio_100_elegible": subsidio,  # si cumple condiciones_subsidio
        "condiciones_subsidio": estado.condiciones_subsidio or None,
        "tenencia_mxn": tenencia,
        "refrendo_mxn": refrendo,
        "subtotal_mxn": subtotal,
        "requiere_calculo_oficial": subtotal is None,
        "portal_url": estado.portal_url or None,
        "verificado_2026": estado.verificado_2026,
        "confianza": estado.confianza,
        "fuentes": list(estado.fuentes),
        "advertencias": advertencias,
        "simulated": False,
    }


__all__ = [
    "EstadoTenencia", "MetodoConsulta", "CATALOGO_TENENCIA",
    "buscar_estado", "listar_estados", "calcular_tenencia",
]
