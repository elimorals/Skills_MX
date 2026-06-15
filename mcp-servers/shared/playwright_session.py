"""Sesión Playwright reusable para portales con reCAPTCHA v3 + XSRF.

Aplicable a portales mexicanos que requieren browser real (no httpx-only):
- IMPI ViDoc (búsqueda de marcas)
- CONDUSEF SIPRES (entidades financieras)
- COFEPRIS Visor (medicamentos)
- REPUVE (NIV/placa robados)
- Tribunales electrónicos
- no-antecedentes-penales (CDMX/EdoMex con SSO)

Patrón de uso:
    from shared.playwright_session import PortalSession

    sess = PortalSession(
        portal_url="https://vidoc.impi.gob.mx/busc",
        api_url_pattern=r"/api/BusquedaDocumentos/getBusquedaSimpleNdjson",
    )
    result = sess.query(
        fill_action=lambda page: page.fill('input[type="search"]', "TELMEX"),
        submit_action=lambda page: page.click('button[aria-label="Search"]'),
        wait_after_submit_ms=4000,
    )
    # result.body es el response del XHR interceptado

Modo opcional 2captcha:
    Si TWOCAPTCHA_API_KEY está set, podemos saltar el browser y obtener token
    reCAPTCHA v3 vía API solver. NO implementado aquí (requiere requests al
    solver + integración específica por portal). Documentado como hook
    para futuras extensiones.

Modo mock:
    Si playwright no está instalado o PLUGINS_MX_MOCK=1, la sesión NO se crea
    y los callers deben usar el camino mock-determinístico.

Lifecycle:
    Browser se abre lazy en la primera query y se reusa para queries subsecuentes
    en el mismo proceso. Reduce latencia de ~3s (cold) a ~500ms (warm).
"""
from __future__ import annotations

import os
import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class CapturedResponse:
    """Una respuesta XHR interceptada del portal."""
    url: str
    status: int
    content_type: str
    body: str  # decoded text
    request_headers: dict[str, str] = field(default_factory=dict)
    request_body: Optional[str] = None


class PlaywrightNotAvailable(RuntimeError):
    """Playwright no instalado o navegador no descargado."""


class PortalSession:
    """Sesión reusable contra un portal con reCAPTCHA v3.

    Args:
        portal_url: URL inicial del portal (donde Angular/React carga + emite token).
        api_url_pattern: regex que matchea el endpoint backend a interceptar
            (ej. r"/api/BusquedaDocumentos/getBusquedaSimpleNdjson").
        ready_selector: CSS selector que confirma que la SPA terminó de cargar
            (ej. 'input[type="search"]'). Espera por este antes de hacer fill/submit.
        headless: True en producción, False para debug visual.
        timeout_ms: timeout por operación individual.
    """

    def __init__(
        self,
        portal_url: str,
        api_url_pattern: str,
        ready_selector: Optional[str] = None,
        headless: bool = True,
        timeout_ms: int = 30000,
    ) -> None:
        self.portal_url = portal_url
        self.api_url_pattern = re.compile(api_url_pattern)
        self.ready_selector = ready_selector
        self.headless = headless
        self.timeout_ms = timeout_ms

        # Lazy-instantiated state
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._loaded = False

    # ============================================================
    # Lifecycle
    # ============================================================

    def _ensure_browser(self) -> None:
        """Inicia Playwright lazy. Idempotente."""
        if self._page is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise PlaywrightNotAvailable(
                "playwright no está instalado. "
                "Instala con: pip install playwright && playwright install chromium"
            ) from e

        self._playwright = sync_playwright().start()
        try:
            self._browser = self._playwright.chromium.launch(headless=self.headless)
        except Exception as e:
            self._playwright.stop()
            self._playwright = None
            raise PlaywrightNotAvailable(
                f"No se pudo lanzar Chromium: {e}. "
                "Probable causa: navegador no descargado. Ejecuta `playwright install chromium`."
            ) from e

        self._context = self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            ),
            locale="es-MX",
        )
        self._page = self._context.new_page()
        self._page.set_default_timeout(self.timeout_ms)

    def _ensure_portal_loaded(self) -> None:
        """Navega al portal una vez por sesión y espera a que cargue."""
        if self._loaded:
            return
        self._ensure_browser()
        self._page.goto(self.portal_url, wait_until="domcontentloaded")
        if self.ready_selector:
            self._page.wait_for_selector(self.ready_selector, state="visible")
        self._loaded = True

    def close(self) -> None:
        """Limpia recursos. Idempotente."""
        try:
            if self._page is not None:
                self._page.close()
        except Exception:
            pass
        try:
            if self._context is not None:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser is not None:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright is not None:
                self._playwright.stop()
        except Exception:
            pass
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None
        self._loaded = False

    def __enter__(self) -> "PortalSession":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    # ============================================================
    # Core API
    # ============================================================

    def query(
        self,
        fill_action: Callable[[Any], None],
        submit_action: Callable[[Any], None],
        wait_after_submit_ms: int = 4000,
        reset_form: bool = True,
    ) -> list[CapturedResponse]:
        """Ejecuta una query interceptando el endpoint backend del portal.

        Args:
            fill_action: callable que recibe `page` y llena los inputs.
            submit_action: callable que recibe `page` y dispara el submit.
            wait_after_submit_ms: tiempo a esperar después del submit para que
                el XHR backend complete y se capture.
            reset_form: si True, recarga la página antes de la query para evitar
                state contamination de queries previas. False = más rápido (reusa
                token reCAPTCHA si Angular lo refresca), pero arriesgado.

        Returns:
            Lista de CapturedResponse — todos los XHR que matchearon el pattern.
        """
        self._ensure_portal_loaded()

        if reset_form:
            # Recarga la página para emitir token reCAPTCHA fresco
            self._page.goto(self.portal_url, wait_until="domcontentloaded")
            if self.ready_selector:
                self._page.wait_for_selector(self.ready_selector, state="visible")

        captured: list[CapturedResponse] = []

        def on_response(response):
            url = response.url
            if not self.api_url_pattern.search(url):
                return
            try:
                body = response.text()
            except Exception:
                body = ""
            try:
                req = response.request
                req_body = req.post_data
            except Exception:
                req_body = None
            captured.append(CapturedResponse(
                url=url,
                status=response.status,
                content_type=response.headers.get("content-type", ""),
                body=body,
                request_headers=dict(response.request.headers) if response.request else {},
                request_body=req_body,
            ))

        self._page.on("response", on_response)
        try:
            fill_action(self._page)
            submit_action(self._page)
            # Espera fija — reCAPTCHA v3 + XSRF + NDJSON streaming necesita tiempo
            self._page.wait_for_timeout(wait_after_submit_ms)
        finally:
            self._page.remove_listener("response", on_response)

        return captured


# ============================================================
# Helpers de conveniencia
# ============================================================

def is_playwright_available() -> bool:
    """True si playwright está instalado (no garantiza que el browser esté)."""
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def should_use_real_browser(env_flag: str) -> bool:
    """Decide si activar Playwright real basado en env vars.

    Reglas:
        - PLUGINS_MX_MOCK=1 → siempre mock
        - {env_flag}=1 + playwright instalado → real
        - default → mock

    Args:
        env_flag: nombre de la env var específica del MCP
            (ej. PLUGINS_MX_IMPI_LIVE, PLUGINS_MX_CONDUSEF_LIVE).
    """
    if os.environ.get("PLUGINS_MX_MOCK") == "1":
        return False
    if os.environ.get(env_flag) != "1":
        return False
    return is_playwright_available()


__all__ = [
    "PortalSession",
    "CapturedResponse",
    "PlaywrightNotAvailable",
    "is_playwright_available",
    "should_use_real_browser",
]
