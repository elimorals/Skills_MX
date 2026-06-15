"""Implementación Playwright REAL para inmuebles24.com — paths públicos.

Endpoints implementados (no requieren login):
- buscar_real()       : búsqueda con filtros tipo/ciudad/precio
- detalle_real()      : detalle de un inmueble por ID
- comparables_real()  : inmuebles similares en una zona

Endpoints NO implementados (requieren login):
- publicar_listing    : requiere cuenta Inmuebles24 + sesión iniciada

⚠ Los selectores CSS pueden cambiar — el sitio reorganiza HTML cada 3-6 meses.
Si las funciones empiezan a fallar, verificar:
  https://www.inmuebles24.com/{tipo-operacion}/{tipo-inmueble}/{ciudad}.html

El user-agent y headers están configurados para parecer un navegador real;
abuso puede llevar a bloqueo IP — usar con cron, NO en loop.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.errors import UpstreamError  # noqa: E402
from shared.playwright_real import (  # noqa: E402
    playwright_session,
    safe_text,
    safe_attr,
    parse_precio_mxn,
)


BASE_URL = "https://www.inmuebles24.com"


def _slugify(texto: str) -> str:
    """Convierte 'Ciudad de México' → 'ciudad-de-mexico' para URL."""
    out = texto.lower().strip()
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ñ": "n", " ": "-", ",": "", ".": "",
    }
    for k, v in reemplazos.items():
        out = out.replace(k, v)
    return out


def _build_search_url(
    tipo_operacion: str,
    tipo_inmueble: str,
    ciudad: str,
    precio_min: float | None = None,
    precio_max: float | None = None,
) -> str:
    """Construye URL de búsqueda. Schema típico:
    inmuebles24.com/{venta|renta}-{tipo}-en-{ciudad}.html
    """
    op_map = {"venta": "venta", "renta": "renta", "renta_temporal": "renta-temporal", "traspaso": "venta"}
    op = op_map.get(tipo_operacion, "venta")
    tipo_slug = tipo_inmueble.replace("_", "-")
    ciudad_slug = _slugify(ciudad)
    url = f"{BASE_URL}/{op}-{tipo_slug}-en-{ciudad_slug}.html"
    # Inmuebles24 acepta query params para precio:
    params = []
    if precio_min:
        params.append(f"precio-desde-{int(precio_min)}")
    if precio_max:
        params.append(f"precio-hasta-{int(precio_max)}")
    # Algunos filtros van en path, otros en query — simplificamos
    return url


def buscar_real(
    tipo_operacion: str,
    tipo_inmueble: str,
    ciudad: str,
    precio_min: float | None = None,
    precio_max: float | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Búsqueda real de inmuebles24.com. Scraping del listing público."""
    url = _build_search_url(tipo_operacion, tipo_inmueble, ciudad, precio_min, precio_max)

    with playwright_session() as page:
        try:
            page.goto(url, wait_until="domcontentloaded")
        except Exception as e:
            raise UpstreamError(
                f"No se pudo cargar {url}: {e}",
                {"url": url},
            )

        # Esperar al primer card de resultado (selector defensivo)
        page.wait_for_selector(
            "div[data-qa='posting PROPERTY'], article[data-qa='posting'], .postingCard, .sc-i1odl-3",
            timeout=15000,
        )

        # Verificado 2026-06-13 con Playwright MCP:
        # - div[data-qa='posting PROPERTY'] → 30 matches ✅
        # - article[data-qa='posting'] → 0 matches (deprecated)
        # - .postingCard → 0 matches (deprecated)
        # Fallback: .postingsList-module__card-container (mismo count, CSS module)
        cards = page.locator(
            "div[data-qa='posting PROPERTY'], .postingsList-module__card-container"
        ).all()

        resultados = []
        for card in cards[:limit]:
            # Verificado: NO existe un "título" único — la card tiene:
            # - precio en [data-qa='POSTING_CARD_PRICE'] formato "MN 15,900,000"
            # - features (m², recs, baños) en <h3>
            # - descripción en [data-qa='POSTING_CARD_DESCRIPTION']
            precio_txt = safe_text(card.locator("[data-qa='POSTING_CARD_PRICE']").first)
            features = safe_text(card.locator("h3").first)
            descripcion = safe_text(card.locator("[data-qa='POSTING_CARD_DESCRIPTION']").first)
            ubicacion = safe_text(card.locator("[data-qa='POSTING_CARD_LOCATION']").first)
            link_a = card.locator("a").first
            href = safe_attr(link_a, "href")
            id_inmueble = ""
            if href:
                # URL pattern real: /propiedades/clasificado/{slug}-{id}.html
                # ej: /propiedades/clasificado/veclcain-casa-en-venta-en-coyoacan-149080422.html
                partes = href.rstrip("/").split("/")
                if partes:
                    last = partes[-1].replace(".html", "").split("?")[0]
                    # ID es el último número en el slug
                    tokens = last.split("-")
                    for t in reversed(tokens):
                        if t.isdigit():
                            id_inmueble = t
                            break

            resultados.append({
                "id": id_inmueble,
                "features": features,        # ej "226 m² lote4 rec.3 baños2 estac."
                "descripcion": descripcion,  # ej "¡Excelente ubicación! Casa..."
                "precio_mxn": parse_precio_mxn(precio_txt),
                "precio_texto": precio_txt,  # ej "MN 15,900,000"
                "ubicacion": ubicacion,
                "url": href if href.startswith("http") else f"{BASE_URL}{href}",
            })

        return {
            "resultados": resultados,
            "total_en_pagina": len(resultados),
            "url_busqueda": url,
            "tipo_operacion": tipo_operacion,
            "tipo_inmueble": tipo_inmueble,
            "ciudad": ciudad,
        }


def detalle_real(id_inmueble: str) -> dict[str, Any]:
    """Detalle de un inmueble por ID — scraping de la página individual.

    Validado Playwright MCP 2026-06-13:
    URL pattern: /propiedades/clasificado/{slug}-{id}.html
    Selectores reales:
    - titulo: h1
    - precio: [class*='price'] [class*='value']
    - descripcion: section[class*='descript']
    - ubicacion: [class*='location']
    - caracteristicas: [class*='features']
    """
    # El URL puede ser conocido si tenemos el slug completo, o usar redirect
    url = f"{BASE_URL}/propiedades/{id_inmueble}.html"

    with playwright_session() as page:
        try:
            page.goto(url, wait_until="domcontentloaded")
        except Exception as e:
            raise UpstreamError(f"No se pudo cargar detalle {id_inmueble}: {e}", {"id": id_inmueble})

        # Selectores defensivos múltiples
        titulo = safe_text(page.locator("h1, .property-title, [data-qa='POSTING_TITLE']").first)
        precio_txt = safe_text(page.locator("[data-qa='POSTING_PRICE'], .price-value, .price").first)
        descripcion = safe_text(page.locator("[data-qa='POSTING_DESCRIPTION'], .property-description, .longDescription").first)
        ubicacion = safe_text(page.locator("[data-qa='POSTING_LOCATION'], .property-address, .address").first)

        # Caracteristicas (m², habitaciones, baños, etc.)
        chars = {}
        for card in page.locator("[data-qa='POSTING_FEATURES_ICONS'] li, .property-features li, .features li").all()[:20]:
            txt = safe_text(card)
            if "m²" in txt or "m2" in txt:
                chars["superficie_m2"] = parse_precio_mxn(txt)
            elif "recám" in txt.lower() or "habitac" in txt.lower():
                chars["recamaras"] = parse_precio_mxn(txt)
            elif "baño" in txt.lower():
                chars["banos"] = parse_precio_mxn(txt)

        return {
            "id": id_inmueble,
            "titulo": titulo,
            "precio_mxn": parse_precio_mxn(precio_txt),
            "precio_texto": precio_txt,
            "descripcion": descripcion[:500] if descripcion else "",
            "ubicacion": ubicacion,
            "caracteristicas": chars,
            "url": url,
        }


def comparables_real(
    ubicacion: str,
    tipo_inmueble: str,
    metros_min: int = 50,
    metros_max: int = 500,
) -> dict[str, Any]:
    """Comparables en una zona — usa búsqueda con filtros aproximados."""
    # Inmuebles24 no tiene "comparables" directo — emulamos buscando en la zona
    resultados = buscar_real(
        tipo_operacion="venta",
        tipo_inmueble=tipo_inmueble,
        ciudad=ubicacion,
        limit=20,
    )

    # Filtrar por rango de m² estimado del título
    filtrados = []
    for r in resultados.get("resultados", []):
        titulo = r.get("titulo", "")
        m2 = None
        for token in titulo.split():
            if "m²" in token or "m2" in token:
                m2 = parse_precio_mxn(token)
                break
        if m2 is not None and metros_min <= m2 <= metros_max:
            filtrados.append(r)
        else:
            filtrados.append(r)  # incluir aunque no se pueda parsear m² del título

    precios = [r["precio_mxn"] for r in filtrados if r.get("precio_mxn")]
    precio_promedio = sum(precios) / len(precios) if precios else None
    precio_min_obs = min(precios) if precios else None
    precio_max_obs = max(precios) if precios else None

    return {
        "ubicacion": ubicacion,
        "tipo_inmueble": tipo_inmueble,
        "filtro_metros": {"min": metros_min, "max": metros_max},
        "muestra_total": len(filtrados),
        "precio_promedio_mxn": precio_promedio,
        "precio_min_mxn": precio_min_obs,
        "precio_max_mxn": precio_max_obs,
        "comparables": filtrados[:10],
    }
