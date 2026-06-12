"""Mock data Inmuebles24."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def mock_buscar_inmuebles(
    tipo_operacion: str,
    tipo_inmueble: str,
    ciudad: str,
    precio_min: float | None = None,
    precio_max: float | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    return {
        "filtros": {
            "tipo_operacion": tipo_operacion,
            "tipo_inmueble": tipo_inmueble,
            "ciudad": ciudad,
            "precio_min": precio_min,
            "precio_max": precio_max,
        },
        "total_encontrados": 247,  # mock — número plausible
        "mostrados": min(limit, 3),
        "resultados": [
            {
                "id": "MLM-INM24-1234567",
                "titulo": f"{tipo_inmueble.title()} en {ciudad}",
                "precio_mxn": 4_500_000.00,
                "metros_cuadrados": 120,
                "habitaciones": 3,
                "baños": 2,
                "ubicacion": f"Col. Demo, {ciudad}",
                "fecha_publicacion": (date.today() - timedelta(days=5)).isoformat(),
                "url": f"https://www.inmuebles24.com/propiedades/demo-1234567.html",
                "destacado": True,
            },
            {
                "id": "MLM-INM24-1234568",
                "titulo": f"{tipo_inmueble.title()} amueblado",
                "precio_mxn": 3_850_000.00,
                "metros_cuadrados": 105,
                "habitaciones": 2,
                "baños": 2,
                "ubicacion": f"Col. Centro, {ciudad}",
                "fecha_publicacion": (date.today() - timedelta(days=12)).isoformat(),
                "url": f"https://www.inmuebles24.com/propiedades/demo-1234568.html",
                "destacado": False,
            },
            {
                "id": "MLM-INM24-1234569",
                "titulo": f"{tipo_inmueble.title()} con vista panorámica",
                "precio_mxn": 5_900_000.00,
                "metros_cuadrados": 150,
                "habitaciones": 4,
                "baños": 3,
                "ubicacion": f"Polanco, {ciudad}",
                "fecha_publicacion": (date.today() - timedelta(days=3)).isoformat(),
                "url": f"https://www.inmuebles24.com/propiedades/demo-1234569.html",
                "destacado": True,
            },
        ],
    }


def mock_detalle_inmueble(id_inmueble: str) -> dict[str, Any]:
    return {
        "id": id_inmueble,
        "titulo": "Casa moderna en colonia residencial",
        "descripcion": "Hermosa casa de 3 plantas con jardín, terraza, estudio y cuarto de servicio. Acabados de primera. Ideal para familia con niños.",
        "tipo_operacion": "venta",
        "tipo_inmueble": "casa",
        "precio_mxn": 5_850_000.00,
        "metros_cuadrados_terreno": 220,
        "metros_cuadrados_construidos": 280,
        "habitaciones": 4,
        "baños": 3,
        "medio_baños": 1,
        "estacionamientos": 2,
        "antiguedad_años": 8,
        "ubicacion": {
            "colonia": "Lomas de Chapultepec",
            "ciudad": "Ciudad de México",
            "estado": "CDMX",
            "cp": "11000",
        },
        "amenidades": ["alberca", "gimnasio", "salón_eventos", "seguridad_24/7"],
        "fotos_count": 18,
        "publicado_por": {
            "tipo": "agencia",
            "nombre": "Inmobiliaria Demo SA de CV",
        },
        "fecha_publicacion": (date.today() - timedelta(days=10)).isoformat(),
        "vistas": 1247,
        "favoritos": 23,
        "contactos_recibidos": 18,
    }


def mock_comparables_zona(
    ubicacion: str,
    tipo_inmueble: str,
    metros_min: int,
    metros_max: int,
) -> dict[str, Any]:
    return {
        "ubicacion_consultada": ubicacion,
        "tipo_inmueble": tipo_inmueble,
        "rango_metros": f"{metros_min}-{metros_max}",
        "muestra_total": 24,
        "estadisticas_precio_mxn": {
            "p25": 3_850_000,
            "mediana": 4_700_000,
            "p75": 5_900_000,
            "promedio": 4_850_000,
            "min": 2_950_000,
            "max": 7_200_000,
        },
        "precio_por_m2_mxn": {
            "p25": 38_500,
            "mediana": 47_000,
            "p75": 59_000,
        },
        "dias_promedio_en_mercado": 38,
    }


def mock_publicar_listing(
    titulo: str,
    precio: float,
    tipo_operacion: str,
    tipo_inmueble: str,
) -> dict[str, Any]:
    return {
        "id_listing": "MLM-INM24-NUEVO123456",
        "status": "borrador",
        "titulo": titulo,
        "precio_mxn": precio,
        "tipo_operacion": tipo_operacion,
        "tipo_inmueble": tipo_inmueble,
        "fecha_creacion": date.today().isoformat(),
        "url_borrador": "https://www.inmuebles24.com/dashboard/nuevo/MLM-INM24-NUEVO123456",
        "siguientes_pasos": [
            "Agregar al menos 5 fotos",
            "Completar descripción (mínimo 200 caracteres)",
            "Validar ubicación con marcador en mapa",
            "Activar publicación (consume 1 crédito del plan)",
        ],
    }
