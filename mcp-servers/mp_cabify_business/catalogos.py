"""Catálogos Cabify Business.

Estados de viaje según https://cabify-api.readme.io/docs/journey-states.md (2026-07).
Los productos y precios no son fijos: salen de /estimates por origen.
"""

from __future__ import annotations


ESTADOS_VIAJE: dict[str, str] = {
    "hire": "Buscando conductor",
    "hired": "Conductor asignado, en camino al origen",
    "arrived": "Conductor llegó a la parada",
    "pick up": "Pasajero a bordo",
    "drop off": "Viaje terminado en destino",
    "rider cancel": "Cancelado por el cliente",
    "driver cancel": "Cancelado por el conductor (sin costo)",
    "no show": "El pasajero no se presentó",
    "not found": "No se encontró conductor",
    "reserve": "Viaje reservado a futuro",
    "terminated": "Cerrado; ya se generaron las ventas (recibos)",
}
