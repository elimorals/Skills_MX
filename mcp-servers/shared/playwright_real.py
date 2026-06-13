"""Helpers compartidos para MCPs que SÍ implementan Playwright real.

Provee un context manager `PlaywrightSession` que centraliza:
- Lanzamiento de Chromium headless con user-agent realista
- Configuración de viewport + locale es-MX
- Timeout por operación (15s default)
- Marcado consistente de respuestas como `simulated: false` con metadata de scraping
- Manejo gracioso de errores (devuelve fallback mock si Playwright falla)

⚠ Importante: Este módulo NO importa playwright al toplevel para que el resto del
monorepo siga funcionando sin la dependencia instalada. La importación es lazy
dentro de los métodos.

Para activar:
    pip install playwright
    playwright install chromium

Env vars:
- MP_PLAYWRIGHT_PUBLIC=1   → habilita paths que NO requieren login (búsquedas públicas)
- PLUGINS_MX_PLAYWRIGHT_REAL=1 → habilita paths que SÍ requieren login (publicar, IDSE, etc)
- MP_PLAYWRIGHT_HEADLESS=0 → modo no-headless para debugging visual
- MP_PLAYWRIGHT_TIMEOUT_MS=30000 → override del timeout por operación
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Any, Callable, Generator, Optional

from shared.errors import UpstreamError


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)

DEFAULT_TIMEOUT_MS = 15000

DEFAULT_LOCALE = "es-MX"
DEFAULT_VIEWPORT = {"width": 1366, "height": 768}


def is_public_real_enabled() -> bool:
    """¿Está habilitado el path Playwright público (sin credenciales)?"""
    return os.environ.get("MP_PLAYWRIGHT_PUBLIC") == "1"


def is_auth_real_enabled() -> bool:
    """¿Está habilitado el path Playwright con auth (requiere credenciales)?"""
    return os.environ.get("PLUGINS_MX_PLAYWRIGHT_REAL") == "1"


@contextmanager
def playwright_session(headless: bool = True) -> Generator[Any, None, None]:
    """Context manager que entrega una page de Playwright lista para usar.

    Importa playwright lazy para no requerir la dependencia si no se usa.

    Uso:
        with playwright_session() as page:
            page.goto("https://example.com")
            return page.title()

    Lanza UpstreamError si playwright no está instalado o si el browser no arranca.
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError as e:
        raise UpstreamError(
            "Playwright no está instalado. Ejecuta: pip install playwright && playwright install chromium",
            {"error_tipo": "dependencia_faltante"},
        ) from e

    headless_env = os.environ.get("MP_PLAYWRIGHT_HEADLESS")
    if headless_env is not None:
        headless = headless_env != "0"

    timeout_ms = int(os.environ.get("MP_PLAYWRIGHT_TIMEOUT_MS", DEFAULT_TIMEOUT_MS))

    playwright = None
    browser = None
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )
        context = browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
            locale=DEFAULT_LOCALE,
            viewport=DEFAULT_VIEWPORT,
            timezone_id="America/Mexico_City",
        )
        context.set_default_timeout(timeout_ms)
        page = context.new_page()
        yield page
    except Exception as e:
        raise UpstreamError(
            f"Error en sesión Playwright: {type(e).__name__}: {e}",
            {"error_tipo": "playwright_runtime"},
        ) from e
    finally:
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass
        if playwright is not None:
            try:
                playwright.stop()
            except Exception:
                pass


def with_real_or_fallback(
    real_fn: Callable[[], dict[str, Any]],
    fallback_fn: Callable[[], dict[str, Any]],
    portal: str,
) -> dict[str, Any]:
    """Intenta `real_fn`. Si falla con UpstreamError, cae a `fallback_fn` con marca.

    Esto evita que un cambio en el portal rompa el MCP — devuelve mock con
    advertencia explícita en lugar de propagar la excepción.

    El caller decide cuándo usar esto vs propagar (depende de criticidad).
    """
    try:
        result = real_fn()
        result.setdefault("simulated", False)
        result.setdefault("scrape_metadata", {})
        result["scrape_metadata"]["portal"] = portal
        result["scrape_metadata"]["timestamp"] = int(time.time())
        return result
    except UpstreamError as e:
        fallback = fallback_fn()
        fallback["simulated"] = True
        fallback.setdefault("advertencias", [])
        fallback["advertencias"].append(
            f"Path Playwright real falló ({type(e).__name__}: {str(e)[:100]}). "
            f"Devolviendo mock — verificar selectores del portal {portal}."
        )
        return fallback


def safe_text(element: Any, default: str = "") -> str:
    """Extrae texto de un Playwright Locator de forma defensiva."""
    if element is None:
        return default
    try:
        text = element.text_content()
        return text.strip() if text else default
    except Exception:
        return default


def safe_attr(element: Any, attr: str, default: str = "") -> str:
    """Extrae atributo de un Locator de forma defensiva."""
    if element is None:
        return default
    try:
        value = element.get_attribute(attr)
        return value.strip() if value else default
    except Exception:
        return default


def parse_precio_mxn(texto: str) -> Optional[float]:
    """Convierte '$ 5,250,000 MXN' → 5250000.0. Retorna None si no parsea."""
    if not texto:
        return None
    digits = "".join(c for c in texto if c.isdigit() or c == ".")
    try:
        return float(digits) if digits else None
    except ValueError:
        return None
