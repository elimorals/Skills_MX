"""Cliente mp_telmex_facturacion — mock-first + Playwright real path."""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.telmex_portal import (  # noqa: E402
    LIVE_ENV_FLAG,
    SESSION_TTL_HOURS,
    TELMEX_PAGO_FIELDS,
    TELMEX_RECAPTCHA_SITE_KEY,
    TelmexCredentials,
    URL_MI_TELMEX_FACTURAS,
    URL_MI_TELMEX_LOGIN,
    URL_TELMEX_PAGO_SIN_LOGIN,
    URL_TELMEX_PORTLET_POST,
    validar_telefono,
)


NAMESPACE = "telmex_fact"
CRED_VARS = ["TELMEX_TELEFONO", "TELMEX_PASSWORD"]
# Correo placeholder cuando el caller no provee uno (Telmex lo requiere para
# pago_sin_login pero no lo valida contra cuenta del usuario).
DEFAULT_CORREO_PASSLESS = "factura@example.com"


class TelmexFactClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        """Mock por default; live opt-in vía PLUGINS_MX_TELMEX_LIVE=1.

        pago_sin_login NO requiere credenciales del usuario, así que el
        flag solo es lo que decide. Mi Telmex login (futuro) sí pedirá CRED_VARS.
        """
        live = os.getenv(LIVE_ENV_FLAG, "").strip() == "1"
        return not live

    def _get_credentials(self) -> Optional[TelmexCredentials]:
        tel = os.getenv("TELMEX_TELEFONO", "").strip()
        pwd = os.getenv("TELMEX_PASSWORD", "").strip()
        if not tel or not pwd:
            return None
        try:
            return TelmexCredentials(telefono=tel, password=pwd)
        except ValueError:
            return None

    def descargar_factura_mes(self, telefono: str, periodo: str = "") -> dict[str, Any]:
        """Descarga PDF + XML de la factura del periodo (YYYY-MM)."""
        tel_norm = validar_telefono(telefono)
        cache_key = f"factura:{tel_norm}:{periodo or 'ultimo'}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if self._is_mock():
            result = self._mock_factura(tel_norm, periodo)
        else:
            result = self._real_factura(tel_norm, periodo)

        ttl = 24 * 30 if not periodo else 24 * 365
        self._cache.set(cache_key, result, ttl_hours=ttl)
        self._bitacora.log(
            "descargar_factura_mes",
            success=True,
            params_summary={
                "telefono_hash": self._bitacora.hash_sensitive(tel_norm),
                "periodo": periodo or "ultimo",
                "modo": "mock" if self._is_mock() else "live",
            },
        )
        return result

    def consumo_historico(self, telefono: str, meses: int = 6) -> dict[str, Any]:
        """Histórico de consumos por mes."""
        if not (1 <= meses <= 24):
            raise ValidationError("meses debe estar entre 1 y 24")
        tel_norm = validar_telefono(telefono)
        cache_key = f"consumo:{tel_norm}:{meses}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if self._is_mock():
            result = self._mock_consumo(tel_norm, meses)
        else:
            result = self._real_consumo(tel_norm, meses)

        self._cache.set(cache_key, result, ttl_hours=24)
        self._bitacora.log("consumo_historico", success=True,
                           params_summary={"telefono_hash": self._bitacora.hash_sensitive(tel_norm), "meses": meses})
        return result

    def listar_facturas(self, telefono: str) -> dict[str, Any]:
        """Lista facturas disponibles (últimos 12 meses)."""
        tel_norm = validar_telefono(telefono)
        cache_key = f"lista:{tel_norm}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if self._is_mock():
            result = self._mock_listado(tel_norm)
        else:
            result = self._real_listado(tel_norm)

        self._cache.set(cache_key, result, ttl_hours=12)
        self._bitacora.log("listar_facturas", success=True,
                           params_summary={"telefono_hash": self._bitacora.hash_sensitive(tel_norm)})
        return result

    # ---- MOCK paths ----
    def _mock_factura(self, telefono: str, periodo: str) -> dict[str, Any]:
        per = periodo or "2026-05"
        last = telefono[-1]
        monto = 389.00 + int(last) * 50
        return mark_simulated({
            "operation": "descargar_factura_mes",
            "telefono": telefono,
            "periodo": per,
            "monto_total_mxn": round(monto, 2),
            "fecha_emision": f"{per}-15",
            "fecha_vencimiento": f"{per}-30",
            "estatus": "PAGADA" if int(last) % 2 == 0 else "PENDIENTE",
            "url_pdf": f"https://miespacio.telmex.com/factura/{telefono}/{per}.pdf",
            "url_xml": f"https://miespacio.telmex.com/factura/{telefono}/{per}.xml",
            "uuid_cfdi": f"XXXX-MOCK-{telefono[-4:]}-{per}",
            "fuente": URL_MI_TELMEX_FACTURAS,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    def _mock_consumo(self, telefono: str, meses: int) -> dict[str, Any]:
        base = 389.0 + int(telefono[-1]) * 50
        return mark_simulated({
            "operation": "consumo_historico",
            "telefono": telefono,
            "meses": meses,
            "consumos": [
                {"periodo": f"2026-{m:02d}", "monto_mxn": round(base + m * 5.0, 2)}
                for m in range(max(1, 6 - meses + 1), 7)
            ],
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    def _mock_listado(self, telefono: str) -> dict[str, Any]:
        return mark_simulated({
            "operation": "listar_facturas",
            "telefono": telefono,
            "facturas_disponibles": [
                {"periodo": f"2026-{m:02d}", "disponible": True} for m in range(1, 7)
            ],
            "fuente": URL_MI_TELMEX_FACTURAS,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    # ---- REAL paths (Playwright) ----
    def _real_factura(self, telefono: str, periodo: str) -> dict[str, Any]:
        """Path real vía pago_sin_login.

        Estrategia: Playwright headless → llena formulario → reCAPTCHA Enterprise
        v3 invisible se resuelve solo en click → parsea respuesta con monto/
        vencimiento/RPU. Sin credenciales del usuario.
        """
        correo = os.getenv("TELMEX_CORREO_NOTIF", DEFAULT_CORREO_PASSLESS).strip()
        return self._real_factura_sin_login(telefono, correo, periodo)

    def _real_factura_sin_login(
        self, telefono: str, correo: str, periodo: str = ""
    ) -> dict[str, Any]:
        """Implementación real del flujo pago_sin_login (sin credenciales)."""
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:
            raise McpError(
                "Playwright no instalado. Ejecuta: pip install playwright && playwright install chromium",
                {"hint": str(e)},
            )

        headless = os.getenv("PLUGINS_MX_TELMEX_HEADLESS", "1") == "1"
        timeout_ms = int(os.getenv("PLUGINS_MX_TELMEX_TIMEOUT_MS", "45000"))

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                ctx = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/130.0.0.0 Safari/537.36"
                    ),
                    locale="es-MX",
                )
                page = ctx.new_page()
                page.set_default_timeout(timeout_ms)

                page.goto(URL_TELMEX_PAGO_SIN_LOGIN, wait_until="domcontentloaded")
                page.wait_for_selector(f"input#{TELMEX_PAGO_FIELDS['telefono']}",
                                       state="visible")

                page.fill(f"input#{TELMEX_PAGO_FIELDS['telefono']}", telefono)
                page.fill(f"input#{TELMEX_PAGO_FIELDS['telefono_confirm']}", telefono)
                page.fill(f"input#{TELMEX_PAGO_FIELDS['correo']}", correo)

                # Continuar — el handler dispara reCAPTCHA Enterprise v3 invisible
                page.click("button:has-text('Continuar'), input[type='submit']:visible")

                # El portlet redirige a una página con detalle de factura
                page.wait_for_load_state("networkidle", timeout=timeout_ms)

                html = page.content()
                parsed = _parse_telmex_factura_html(html, telefono)
                browser.close()

            parsed["periodo"] = periodo or parsed.get("periodo_detectado", "")
            parsed["fuente"] = URL_TELMEX_PAGO_SIN_LOGIN
            parsed["fecha_consulta"] = datetime.now(timezone.utc).isoformat()
            parsed.setdefault("simulated", False)
            return parsed

        except Exception as e:
            raise UpstreamError(
                f"Telmex pago_sin_login falló: {type(e).__name__}: {e}",
                {"telefono_hash": self._bitacora.hash_sensitive(telefono),
                 "portal": URL_TELMEX_PAGO_SIN_LOGIN},
            )

    def _real_consumo(self, telefono: str, meses: int) -> dict[str, Any]:
        # pago_sin_login expone monto del último periodo, no histórico.
        # Histórico requiere Mi Telmex login (NetIQ SSO) — fuera de scope sin creds.
        raise McpError(
            "consumo_historico real requiere Mi Telmex login (NetIQ SSO). "
            "Configura TELMEX_TELEFONO + TELMEX_PASSWORD para activar.",
            {"hint": "Por ahora usa mock (PLUGINS_MX_TELMEX_LIVE no set)."},
        )

    def _real_listado(self, telefono: str) -> dict[str, Any]:
        raise McpError(
            "listar_facturas real requiere Mi Telmex login (NetIQ SSO). Pendiente.",
            {"hint": "Usar mock por ahora."},
        )


# ============================================================
# Parser HTML — Telmex pago_sin_login response
# ============================================================
def _parse_telmex_factura_html(html: str, telefono: str) -> dict[str, Any]:
    """Extrae monto, periodo y vencimiento del HTML de respuesta de Telmex.

    El portlet renderiza un panel con clase/atributos como `monto-pagar`,
    `fecha-vencimiento`, `numero-servicio`. Si Telmex cambia la estructura,
    devolvemos lo crudo y marcamos `parse_partial: True`.
    """
    import re as _re
    # Strip HTML tags y colapsa whitespace (robusto a `<td>X</td><td>VAL</td>`)
    text = _re.sub(r"<[^>]+>", " ", html)
    text = _re.sub(r"\s+", " ", text)

    result: dict[str, Any] = {
        "operation": "descargar_factura_mes",
        "telefono": telefono,
        "modo": "pago_sin_login",
    }

    def _grab(pattern: str) -> Optional[str]:
        m = _re.search(pattern, text, _re.IGNORECASE | _re.DOTALL)
        return m.group(1).strip() if m else None

    monto_raw = _grab(r"\$\s*([0-9]{1,3}(?:[,\.][0-9]{3})*[\.,][0-9]{2})")
    if monto_raw:
        try:
            result["monto_total_mxn"] = float(monto_raw.replace(",", ""))
        except ValueError:
            result["monto_total_raw"] = monto_raw

    venc = _grab(r"[Vv]encimiento[^\d]{0,30}(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})")
    if venc:
        result["fecha_vencimiento"] = venc

    rpu = _grab(r"[Nn][úu]mero\s+(?:de\s+)?[Ss]ervicio[^\d]{0,15}(\d{4,16})")
    if rpu:
        result["numero_servicio"] = rpu

    periodo = _grab(r"[Pp]eriodo[^\d]{0,15}(\d{2,4}[\-/]\d{2}(?:[\-/]\d{2,4})?)")
    if periodo:
        result["periodo_detectado"] = periodo

    if "monto_total_mxn" not in result and "monto_total_raw" not in result:
        result["parse_partial"] = True
        result["html_snippet"] = html[:500]

    return result
