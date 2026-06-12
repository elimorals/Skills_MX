"""Mock data Vivanuncios."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def mock_buscar_anuncios(
    categoria: str,
    query: str,
    ciudad: str,
    limit: int = 10,
) -> dict[str, Any]:
    return {
        "filtros": {"categoria": categoria, "query": query, "ciudad": ciudad},
        "total_encontrados": 184,
        "mostrados": min(limit, 3),
        "resultados": [
            {
                "id": "VIV-987654321",
                "titulo": f"{query} en {ciudad} — Excelente estado",
                "categoria": categoria,
                "precio_mxn": 12_500.00 if categoria == "vehiculos" else 350_000.00,
                "ubicacion": ciudad,
                "fecha_publicacion": (date.today() - timedelta(days=3)).isoformat(),
                "tipo_publicacion": "destacada",
                "url": f"https://www.vivanuncios.com.mx/anuncio/987654321",
            },
            {
                "id": "VIV-987654322",
                "titulo": f"{query} listo para entregar",
                "categoria": categoria,
                "precio_mxn": 9_800.00 if categoria == "vehiculos" else 280_000.00,
                "ubicacion": ciudad,
                "fecha_publicacion": (date.today() - timedelta(days=10)).isoformat(),
                "tipo_publicacion": "gratuita",
                "url": f"https://www.vivanuncios.com.mx/anuncio/987654322",
            },
            {
                "id": "VIV-987654323",
                "titulo": f"{query} premium — precio negociable",
                "categoria": categoria,
                "precio_mxn": 18_500.00 if categoria == "vehiculos" else 425_000.00,
                "ubicacion": ciudad,
                "fecha_publicacion": (date.today() - timedelta(days=1)).isoformat(),
                "tipo_publicacion": "top",
                "url": f"https://www.vivanuncios.com.mx/anuncio/987654323",
            },
        ],
    }


def mock_detalle_anuncio(id_anuncio: str) -> dict[str, Any]:
    return {
        "id": id_anuncio,
        "titulo": "Toyota Corolla 2022 SE — Único dueño",
        "categoria": "vehiculos",
        "descripcion": "Auto en excelentes condiciones. Servicios al día. Trato directo.",
        "precio_mxn": 285_000.00,
        "negociable": True,
        "ubicacion": {"ciudad": "Monterrey", "estado": "Nuevo León"},
        "vendedor": {
            "tipo": "particular",
            "nombre_oculto": "Carlos M***",
            "antiguedad_dias": 365,
            "anuncios_publicados": 4,
        },
        "fotos_count": 8,
        "fecha_publicacion": (date.today() - timedelta(days=5)).isoformat(),
        "vistas": 234,
        "favoritos": 12,
        "contactos_recibidos": 5,
        "status": "activo",
    }


def mock_publicar_anuncio(
    titulo: str, categoria: str, precio: float
) -> dict[str, Any]:
    return {
        "id_anuncio": "VIV-NEW-12345678",
        "status": "moderacion",
        "titulo": titulo,
        "categoria": categoria,
        "precio_mxn": precio,
        "tipo_publicacion": "gratuita",
        "fecha_creacion": date.today().isoformat(),
        "tiempo_estimado_moderacion_horas": 2,
        "url_pendiente": "https://www.vivanuncios.com.mx/dashboard/VIV-NEW-12345678",
        "siguientes_pasos": [
            "Esperar moderación (1-4 hrs típicamente)",
            "Una vez activo aparecerá en búsquedas y notificará interesados",
            "Puede pagar por publicación destacada para mejor ranking",
        ],
    }
