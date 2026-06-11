"""Banxico SIE series codes used by mp-banxico.

Source: https://www.banxico.org.mx/SieAPIRest/service/v1/

These are the official series IDs Banxico publishes. They are stable —
in 20+ years they've added series but rarely renamed existing ones.

⚠ Validate before production: confirm series IDs against
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarSeries
since this skill's training data may be slightly stale.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Serie:
    """A Banxico SIE time series."""

    code: str  # e.g., "SF63528"
    label: str  # human-readable name
    par: str | None = None  # for currency pairs: "USD/MXN" etc.
    publication: str = "diaria"  # "diaria", "mensual", "anual"
    fuente: str = "Banxico"


# Currency exchange rates (FIX rates for obligaciones)
TC_USD_MXN_FIX = Serie(
    code="SF63528",
    label="Tipo de cambio FIX para solventar obligaciones en USD/MXN",
    par="USD/MXN",
    publication="diaria",
)

TC_USD_MXN_PARA_OBLIGACIONES = Serie(
    code="SF60653",
    label="Tipo de cambio para obligaciones denominadas en USD",
    par="USD/MXN",
    publication="diaria",
)

TC_EUR_MXN = Serie(
    code="SF46410",
    label="Tipo de cambio EUR/MXN",
    par="EUR/MXN",
    publication="diaria",
)

TC_GBP_MXN = Serie(
    code="SF46406",
    label="Tipo de cambio GBP/MXN",
    par="GBP/MXN",
    publication="diaria",
)

TC_CAD_MXN = Serie(
    code="SF60632",
    label="Tipo de cambio CAD/MXN",
    par="CAD/MXN",
    publication="diaria",
)

TC_JPY_MXN = Serie(
    code="SF46411",
    label="Tipo de cambio JPY/MXN",
    par="JPY/MXN",
    publication="diaria",
)

# Reference rates
TIIE_28 = Serie(
    code="SF43783",
    label="TIIE a 28 días",
    publication="diaria",
)

# Indices
INPC = Serie(
    code="SP74625",
    label="Índice Nacional de Precios al Consumidor",
    publication="mensual",
)

# UMA
UMA_DIARIA = Serie(
    code="SP74660",
    label="Unidad de Medida y Actualización (diaria)",
    publication="anual",
)


def serie_for_par(par: str) -> Serie | None:
    """Look up the FIX series for a currency pair like 'USD/MXN'."""
    par = par.upper()
    mapping = {
        "USD/MXN": TC_USD_MXN_FIX,
        "EUR/MXN": TC_EUR_MXN,
        "GBP/MXN": TC_GBP_MXN,
        "CAD/MXN": TC_CAD_MXN,
        "JPY/MXN": TC_JPY_MXN,
    }
    return mapping.get(par)


def supported_pares() -> list[str]:
    """All currency pairs this MCP can resolve."""
    return ["USD/MXN", "EUR/MXN", "GBP/MXN", "CAD/MXN", "JPY/MXN"]
