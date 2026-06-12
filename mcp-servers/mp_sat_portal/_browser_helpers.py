"""Helpers reusables para Playwright en el cliente SAT.

Abstrae:
- Setup/teardown del browser context con context manager.
- Login con e.firma (flujo común a todas las operaciones).
- Captura de screenshot + HTML snapshot al fallar (para debugging).
- Retry con backoff exponencial.

Esto permite que cada `_real_*` del `SatPlaywrightClient` se enfoque en su
flujo específico, sin duplicar la lógica de browser management.
"""

from __future__ import annotations

import contextlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterator

from shared.errors import AuthError, UpstreamError

if TYPE_CHECKING:
    from mp_sat_portal.efirma_loader import EfirmaLoader
    from mp_sat_portal.selectors import SelectorsV1


DEFAULT_FAILURE_DUMP_DIR = Path("~/.cache/plugins-mx/sat_portal/failures").expanduser()


class LoginFailedError(AuthError):
    """Login con e.firma falló en el portal SAT."""

    code = "login_failed"


@contextlib.contextmanager
def browser_context(
    *,
    headless: bool = True,
    user_agent: str | None = None,
    slow_mo_ms: int = 0,
) -> Iterator[Any]:
    """Context manager que abre Playwright + chromium + context + page.

    Yield: tupla (browser, context, page) lista para usar.

    Cierra todo en orden inverso al salir, incluso si hay excepción.

    Uso:
        with browser_context(headless=False) as (browser, ctx, page):
            page.goto("https://...")
            ...

    Raises:
        ImportError: si Playwright no está instalado.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise ImportError(
            "Playwright no instalado. Ejecutar: "
            "`pip install playwright && playwright install chromium`"
        ) from exc

    pw = sync_playwright().start()
    browser = None
    context = None
    page = None
    try:
        browser = pw.chromium.launch(headless=headless, slow_mo=slow_mo_ms)
        context_kwargs: dict[str, Any] = {}
        if user_agent:
            context_kwargs["user_agent"] = user_agent
        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        yield browser, context, page
    finally:
        if page is not None:
            with contextlib.suppress(Exception):
                page.close()
        if context is not None:
            with contextlib.suppress(Exception):
                context.close()
        if browser is not None:
            with contextlib.suppress(Exception):
                browser.close()
        with contextlib.suppress(Exception):
            pw.stop()


def login_efirma(
    page: Any,
    *,
    efirma: "EfirmaLoader",
    selectors: "SelectorsV1",
) -> None:
    """Ejecuta el flujo de login con e.firma en el portal SAT.

    Sube .cer + .key + password y espera a que el login sea exitoso.

    Args:
        page: instancia de `playwright.sync_api.Page`.
        efirma: e.firma cargada con cert/key paths + password.
        selectors: registry vigente de selectores.

    Raises:
        LoginFailedError: si el login no completa exitosamente.
    """
    page.goto(selectors.login_url, timeout=selectors.timeout_navigation_ms)

    # Validar que estamos en la página correcta
    page.wait_for_selector(
        selectors.login_input_cer,
        timeout=selectors.timeout_action_ms,
    )

    # Subir archivos
    page.set_input_files(selectors.login_input_cer, str(efirma.cert_path))
    page.set_input_files(selectors.login_input_key, str(efirma.key_path))

    # Llenar password
    page.fill(selectors.login_input_password, efirma._password)  # noqa: SLF001

    # Submit
    page.click(selectors.login_button_submit)

    # Esperar a uno de los dos: éxito o error
    try:
        page.wait_for_selector(
            f"{selectors.login_success_indicator}, {selectors.login_error_indicator}",
            timeout=selectors.timeout_navigation_ms,
        )
    except Exception as exc:
        raise LoginFailedError(
            "Timeout esperando respuesta del portal SAT tras submit del login. "
            "Posible cambio de selectores o caída del portal."
        ) from exc

    # Decidir si fue éxito o error mirando cuál selector aparece
    if page.locator(selectors.login_error_indicator).count() > 0:
        error_text = page.locator(selectors.login_error_indicator).first.inner_text()
        raise LoginFailedError(
            f"Portal SAT rechazó login: {error_text[:200]}",
            {"rfc": efirma.metadata().rfc},
        )


def wait_for_no_loading(page: Any, selectors: "SelectorsV1") -> None:
    """Espera a que el spinner global del portal desaparezca.

    Útil después de cada acción que dispara request al backend.
    Si no aparece spinner, sale en <1s sin error.
    """
    with contextlib.suppress(Exception):
        page.wait_for_selector(
            selectors.loading_spinner,
            state="hidden",
            timeout=selectors.timeout_action_ms,
        )


def dump_failure_artifacts(
    page: Any,
    *,
    operation: str,
    dump_dir: Path | None = None,
) -> dict[str, str]:
    """Al fallar, captura screenshot + HTML para debugging post-mortem.

    Returns:
        dict con paths de los artifacts generados.
    """
    target_dir = dump_dir or DEFAULT_FAILURE_DUMP_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    base = target_dir / f"{operation}_{timestamp}"

    screenshot_path = f"{base}.png"
    html_path = f"{base}.html"

    artifacts: dict[str, str] = {}
    with contextlib.suppress(Exception):
        page.screenshot(path=screenshot_path, full_page=True)
        artifacts["screenshot"] = screenshot_path
    with contextlib.suppress(Exception):
        Path(html_path).write_text(page.content(), encoding="utf-8")
        artifacts["html"] = html_path
    return artifacts


def with_retry(
    fn: Callable[[], Any],
    *,
    max_attempts: int = 3,
    backoff_seconds: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (UpstreamError,),
) -> Any:
    """Ejecuta `fn` con reintentos exponenciales.

    Sólo reintentan excepciones en `retryable_exceptions`. AuthError no se
    reintenta — si las credenciales fallaron, no van a funcionar después.
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except retryable_exceptions as exc:
            last_exc = exc
            if attempt == max_attempts:
                break
            time.sleep(backoff_seconds * (2 ** (attempt - 1)))
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("with_retry: estado imposible (max_attempts <= 0?)")
