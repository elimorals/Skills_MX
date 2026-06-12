"""Catálogos Inmuebles24."""

from __future__ import annotations


TIPO_OPERACION: dict[str, str] = {
    "venta": "Venta",
    "renta": "Renta mensual",
    "renta_temporal": "Renta temporal/vacacional",
    "traspaso": "Traspaso (negocio)",
}


TIPO_INMUEBLE: dict[str, str] = {
    "casa": "Casa",
    "departamento": "Departamento",
    "ph": "Penthouse",
    "loft": "Loft / Estudio",
    "terreno": "Terreno",
    "oficina": "Oficina",
    "local_comercial": "Local comercial",
    "bodega": "Bodega industrial",
    "edificio": "Edificio completo",
    "hotel": "Hotel",
    "quinta": "Quinta / Rancho",
}


# Estados con mayor inventario en inmuebles24
ESTADOS_TOP_INVENTARIO: list[str] = [
    "Ciudad de México",
    "Estado de México",
    "Jalisco",
    "Nuevo León",
    "Quintana Roo",
    "Querétaro",
    "Yucatán",
    "Baja California Sur",
    "Puebla",
    "Veracruz",
]


# Status del listing
STATUS_LISTING: dict[str, str] = {
    "publicado_activo": "Publicado y visible para usuarios",
    "borrador": "Guardado pero no publicado",
    "pausado": "Pausado por el vendedor",
    "vendido": "Marcado como vendido/rentado",
    "expirado": "Expiró el periodo de publicación",
    "rechazado": "Rechazado por moderación (foto, descripción, precio)",
}


# Planes de publicación
PLANES_PUBLICACION: dict[str, dict] = {
    "free": {
        "nombre": "Plan Free",
        "precio_mxn_mes": 0,
        "creditos_mes": 1,
        "destacado": False,
        "ranking_boost": 0,
    },
    "basico": {
        "nombre": "Plan Básico",
        "precio_mxn_mes": 499,
        "creditos_mes": 5,
        "destacado": False,
        "ranking_boost": 1.2,
    },
    "premium": {
        "nombre": "Plan Premium",
        "precio_mxn_mes": 1499,
        "creditos_mes": 25,
        "destacado": True,
        "ranking_boost": 2.0,
    },
    "agencia": {
        "nombre": "Plan Agencia Inmobiliaria",
        "precio_mxn_mes": 4999,
        "creditos_mes": 150,
        "destacado": True,
        "ranking_boost": 3.0,
    },
}
