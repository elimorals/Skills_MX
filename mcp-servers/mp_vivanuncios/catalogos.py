"""Catálogos Vivanuncios MX."""

from __future__ import annotations


CATEGORIAS_VIVANUNCIOS: dict[str, str] = {
    "inmuebles": "Inmuebles (venta + renta)",
    "vehiculos": "Vehículos (autos, motos)",
    "empleos": "Empleos",
    "servicios": "Servicios profesionales",
    "electronica": "Electrónica",
    "hogar": "Hogar y muebles",
    "moda_belleza": "Moda y belleza",
    "deportes": "Deportes y outdoor",
    "negocios_industriales": "Negocios e industriales",
    "mascotas": "Mascotas",
}


TIPO_PUBLICACION: dict[str, str] = {
    "gratuita": "Publicación gratuita básica",
    "destacada": "Destacada (paid)",
    "top": "Top de búsqueda (paid premium)",
    "renovada": "Renovada (republicación)",
}


STATUS_ANUNCIO: dict[str, str] = {
    "activo": "Publicado y visible",
    "pausado": "Pausado por anunciante",
    "vendido": "Marcado como vendido/cerrado",
    "expirado": "Expiró el periodo (45 días free, 90 días paid)",
    "moderacion": "En proceso de moderación",
    "rechazado": "Rechazado por incumplir políticas",
}


# Vivanuncios vs Inmuebles24: Vivanuncios cubre todo el mercado, no solo inmuebles
DIFERENCIAS_VS_INMUEBLES24: dict[str, str] = {
    "alcance": "Vivanuncios es multi-categoría (autos, empleos, servicios). Inmuebles24 es vertical inmuebles solamente.",
    "audiencia": "Vivanuncios más mass-market. Inmuebles24 más premium/profesional.",
    "publicacion": "Vivanuncios permite muchas publicaciones gratuitas. Inmuebles24 tiene plan free limitado.",
    "verificacion": "Inmuebles24 modera más estrictamente. Vivanuncios más permisivo.",
}
