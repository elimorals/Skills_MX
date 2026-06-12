"""Catálogos Monterrey / Nuevo León."""

from __future__ import annotations


PORTALES_NL: dict[str, str] = {
    "monterrey_predial": "https://www.monterrey.gob.mx/predial",
    "san_pedro_predial": "https://sanpedro.gob.mx/predial",
    "san_nicolas_predial": "https://www.sanicolas.gob.mx",
    "guadalupe_predial": "https://www.guadalupe.gob.mx",
    "transito_monterrey": "https://www.monterrey.gob.mx/transito",
    "tesoreria_nl": "https://www.nl.gob.mx/tesoreria",
}


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


# Estado de NL no maneja No Circula generalizado pero tiene programa
# Aire Limpio en contingencias.
TIPO_RESTRICCION_NL: dict[str, str] = {
    "aire_limpio_fase1": "Restricción solo para vehículos contaminantes",
    "aire_limpio_fase2": "Restricción ampliada (placas pares/impares)",
    "aire_limpio_fase3": "Restricción total — solo emergencias",
}
