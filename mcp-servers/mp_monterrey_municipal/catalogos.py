"""Catálogos Monterrey / Nuevo León."""

from __future__ import annotations

MUNICIPIOS_AMM: list[str] = [
    "Monterrey",
    "San Pedro Garza García",
    "San Nicolás de los Garza",
    "Guadalupe",
    "Apodaca",
    "Escobedo",
    "Santa Catarina",
    "García",
    "Juárez",
]

# Municipios con predial real verificado (ver README, sección "Estado real").
PREDIAL_REAL: dict[str, str] = {
    "Monterrey": "https://asp.monterrey.gob.mx/predial/",
}
