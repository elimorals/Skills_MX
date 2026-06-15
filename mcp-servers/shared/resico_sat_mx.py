"""RESICO SAT México 2026 + retenciones plataformas digitales.

Cambios 2026:
- Suprema Corte: expulsión automática sin previo aviso por 3 omisiones consecutivas
  o no presentar declaración anual.
- e.firma obligatoria para todos los contribuyentes RESICO.
- Límite ingresos anuales: $3.5M MXN (rebasar = salida automática).
- Retenciones plataformas digitales estandarizadas a 2.5% ISR.
- Devolución mes-a-mes disponible si te retienen de más.

Tasas mensuales RESICO (sin cambio vs 2025):
    Hasta $25,000        → 1.00%
    Hasta $50,000        → 1.10%
    Hasta $83,333        → 1.50%
    Hasta $208,333       → 2.00%
    Hasta $291,667       → 2.50%
Sobre el excedente del límite, sale del régimen.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


# Tope anual 2026
RESICO_TOPE_ANUAL_MXN = 3_500_000.0


@dataclass
class TramoRESICO:
    """Tramo mensual RESICO 2026."""
    limite_inferior: float
    limite_superior: float
    tasa: float


TRAMOS_RESICO_MENSUAL_2026: list[TramoRESICO] = [
    TramoRESICO(0.01, 25_000.00, 0.0100),
    TramoRESICO(25_000.01, 50_000.00, 0.0110),
    TramoRESICO(50_000.01, 83_333.33, 0.0150),
    TramoRESICO(83_333.34, 208_333.33, 0.0200),
    TramoRESICO(208_333.34, 291_666.67, 0.0250),
]


def calcular_isr_resico(ingreso_mes_mxn: float) -> dict:
    """Devuelve cálculo ISR mensual conforme tasa aplicable."""
    if ingreso_mes_mxn < 0:
        raise ValueError("ingreso negativo")
    if ingreso_mes_mxn == 0:
        return {"ingreso_mxn": 0.0, "tasa_aplicada": 0.0, "isr_mxn": 0.0,
                "tramo": None, "supera_tope_mensual": False}
    tasa = 0.025  # default último tramo
    tramo_aplicado = TRAMOS_RESICO_MENSUAL_2026[-1]
    supera = False
    if ingreso_mes_mxn > TRAMOS_RESICO_MENSUAL_2026[-1].limite_superior:
        supera = True
    else:
        for t in TRAMOS_RESICO_MENSUAL_2026:
            if ingreso_mes_mxn <= t.limite_superior:
                tasa = t.tasa
                tramo_aplicado = t
                break
    return {
        "ingreso_mxn": round(ingreso_mes_mxn, 2),
        "tasa_aplicada": tasa,
        "isr_mxn": round(ingreso_mes_mxn * tasa, 2),
        "tramo": {
            "limite_inferior": tramo_aplicado.limite_inferior,
            "limite_superior": tramo_aplicado.limite_superior,
            "tasa": tramo_aplicado.tasa,
        },
        "supera_tope_mensual": supera,
    }


# ============================================================
# Plataformas digitales — retención ISR 2.5%
# ============================================================
TASA_RETENCION_PLATAFORMAS_2026 = 0.025


@dataclass
class PlataformaDigital:
    clave: str
    nombre: str
    categoria: Literal["movilidad", "delivery", "ecommerce", "hospedaje", "freelance"]
    aplica_retencion: bool = True
    notas: str = ""


CATALOGO_PLATAFORMAS: list[PlataformaDigital] = [
    PlataformaDigital("uber", "Uber México", "movilidad"),
    PlataformaDigital("didi", "DiDi México", "movilidad"),
    PlataformaDigital("uber_eats", "Uber Eats", "delivery"),
    PlataformaDigital("rappi", "Rappi", "delivery"),
    PlataformaDigital("didi_food", "DiDi Food", "delivery"),
    PlataformaDigital("mercado_libre", "Mercado Libre", "ecommerce"),
    PlataformaDigital("amazon_mx", "Amazon México", "ecommerce"),
    PlataformaDigital("shopify_mx", "Shopify (vendedores MX)", "ecommerce"),
    PlataformaDigital("airbnb", "Airbnb", "hospedaje"),
    PlataformaDigital("booking", "Booking.com", "hospedaje"),
    PlataformaDigital("workana", "Workana", "freelance"),
    PlataformaDigital("upwork", "Upwork", "freelance"),
]


def buscar_plataforma(clave: str) -> PlataformaDigital | None:
    c = (clave or "").strip().lower()
    for p in CATALOGO_PLATAFORMAS:
        if p.clave == c:
            return p
    return None


def calcular_retencion_plataforma(plataforma_clave: str, ingreso_bruto_mxn: float) -> dict:
    p = buscar_plataforma(plataforma_clave)
    if p is None:
        raise ValueError(f"Plataforma no en catálogo: {plataforma_clave}")
    if ingreso_bruto_mxn < 0:
        raise ValueError("ingreso negativo")
    retencion = ingreso_bruto_mxn * TASA_RETENCION_PLATAFORMAS_2026
    return {
        "plataforma": p.clave,
        "nombre": p.nombre,
        "categoria": p.categoria,
        "ingreso_bruto_mxn": round(ingreso_bruto_mxn, 2),
        "tasa_retencion": TASA_RETENCION_PLATAFORMAS_2026,
        "retencion_isr_mxn": round(retencion, 2),
        "neto_recibido_mxn": round(ingreso_bruto_mxn - retencion, 2),
    }


__all__ = [
    "RESICO_TOPE_ANUAL_MXN", "TRAMOS_RESICO_MENSUAL_2026", "calcular_isr_resico",
    "TASA_RETENCION_PLATAFORMAS_2026", "CATALOGO_PLATAFORMAS",
    "PlataformaDigital", "buscar_plataforma", "calcular_retencion_plataforma",
]
