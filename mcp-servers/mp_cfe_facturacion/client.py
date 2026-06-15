"""Cliente mp_cfe_facturacion — Playwright + human-in-loop para CAPTCHA.

CFE Mi Espacio requiere: usuario + password + CAPTCHA. NO existe API pública.
La única forma de automatizar es:
  1. Playwright HEADED (no headless) — abre el browser para que el humano vea el CAPTCHA
  2. Humano resuelve el CAPTCHA manualmente, presiona login
  3. Script captura cookies de sesión y las cachea (TTL 30 min — vida típica)
  4. Llamadas subsecuentes usan las cookies cacheadas → sin re-login

3 modos:
  - mock (default): respuestas determinísticas
  - human_loop (PLUGINS_MX_CFE_LIVE=1): Playwright headed, humano resuelve CAPTCHA
  - api_session (PLUGINS_MX_CFE_COOKIES=<json>): re-usa cookies inyectadas

Universo: 42M usuarios CFE. Caso de uso típico:
  - Hogares: descargar recibo mensual + tracking de consumo
  - PyMEs: facturación mensual + detección de anomalías
  - Property managers: 5-20 inmuebles, conciliación
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    ConfigError,
    McpError,
    UpstreamError,
    ValidationError,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "cfe_fact"
CRED_VARS = ["CFE_RPU", "CFE_PASSWORD"]
SESSION_TTL_MINUTES = 30  # CFE Mi Espacio expira sesión a los 10-30 min de inactividad
LIVE_ENV_FLAG = "PLUGINS_MX_CFE_LIVE"

# Validado Playwright MCP 2026-06-13:
URL_CFE_MIESPACIO_LOGIN = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Login.aspx"
URL_CFE_MIESPACIO_HOME = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Default.aspx"
URL_CFE_MIESPACIO_FACTURA = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Pagar.aspx"
URL_CFE_MIESPACIO_CONSUMO = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/HistorialConsumo.aspx"

SELECTORES_CFE_LOGIN = {
    "usuario": "input[name='ctl00$MainContent$txtUsuario']",
    "password": "input[name='ctl00$MainContent$txtPassword']",
    "captcha": "input[name='ctl00$MainContent$txtCaptcha']",
    "submit": "input[name='ctl00$MainContent$btnIngresar']",
    "captcha_img": "img[id*='Captcha']",
}
# Re-confirmado 2026-06-15 vía Playwright. ASP.NET WebForms con __VIEWSTATE +
# __EVENTVALIDATION ocultos; CAPTCHA alfanumérico de imagen (no reCAPTCHA).
# Ver docs/discovery-portales-2026-06-15.md.

# RPU = Registro Permanente Único (identificador de servicio CFE)
# Formato: 12 dígitos típicamente (no estricto — algunos servicios viejos pueden ser menos)
RPU_PATTERN = re.compile(r"^\d{6,16}$")


def validar_rpu(rpu: str) -> str:
    """Valida RPU del servicio CFE."""
    rpu = (rpu or "").strip().replace(" ", "").replace("-", "")
    if not RPU_PATTERN.match(rpu):
        raise ValidationError(
            f"RPU '{rpu}' inválido. Debe ser 6-16 dígitos numéricos.",
            {"rpu_recibido": rpu, "esperado": "6-16 dígitos"},
        )
    return rpu


class CfeFactClient:
    """Cliente CFE Mi Espacio con session caching y human-in-loop."""

    def __init__(
        self,
        bitacora: Bitacora | None = None,
        cache: FileCache | None = None,
    ) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self.cache = cache or FileCache(NAMESPACE)

    def _is_mock(self) -> bool:
        """CFE necesita credenciales — usa default_when_no_creds=True (mock)."""
        return is_mock_mode(CRED_VARS, default_when_no_creds=True)

    # ============================================================
    # Tools
    # ============================================================

    def descargar_factura_mes(
        self,
        rpu: str,
        periodo: str = "",
    ) -> dict[str, Any]:
        """Descarga el recibo CFE del mes en curso o de un periodo específico.

        Args:
            rpu: Registro Permanente Único (12 dígitos).
            periodo: opcional "YYYY-MM" (mes a descargar). Default: último mes.

        Returns:
            {
              "rpu": str,
              "periodo": str,
              "monto_total": float,
              "consumo_kwh": int,
              "vencimiento": str,
              "pdf_base64": str | None,
              "estatus": "PAGADA" | "PENDIENTE" | "VENCIDA",
              "session_used": "cached" | "fresh_login" | "mock",
              "simulated": bool,
            }
        """
        rpu = validar_rpu(rpu)
        if periodo and not re.match(r"^\d{4}-\d{2}$", periodo):
            raise ValidationError(f"Periodo debe ser YYYY-MM, recibido: {periodo}")

        self.bitacora.log(
            "descargar_factura_mes",
            success=True,
            params_summary={
                "rpu_hash": self.bitacora.hash_sensitive(rpu),
                "periodo": periodo or "ultimo",
            },
        )

        if self._is_mock():
            return self._mock_factura(rpu, periodo)
        return self._real_factura(rpu, periodo)

    def consumo_historico(
        self,
        rpu: str,
        meses: int = 12,
    ) -> dict[str, Any]:
        """Consulta el histórico de consumo (kWh) por mes.

        Args:
            rpu: Registro Permanente Único.
            meses: cantidad de meses históricos a regresar (1-24).

        Returns:
            {
              "rpu": str,
              "meses_solicitados": int,
              "consumo_kwh_por_mes": [{"mes": "2026-04", "kwh": 245, "monto": 612.50}, ...],
              "promedio_kwh_mensual": float,
              "tendencia": "ESTABLE" | "AUMENTO" | "DISMINUCION",
              "anomalia_detectada": bool,
              "session_used": str,
              "simulated": bool,
            }
        """
        rpu = validar_rpu(rpu)
        if not 1 <= meses <= 24:
            raise ValidationError(f"meses debe estar entre 1 y 24, recibido: {meses}")

        self.bitacora.log(
            "consumo_historico",
            success=True,
            params_summary={
                "rpu_hash": self.bitacora.hash_sensitive(rpu),
                "meses": meses,
            },
        )

        if self._is_mock():
            return self._mock_consumo(rpu, meses)
        return self._real_consumo(rpu, meses)

    def validar_session(self, rpu: str) -> dict[str, Any]:
        """Verifica si hay una sesión válida cacheada para este RPU.

        Útil para que el caller decida si ejecutar human-in-loop o reusar cookies.

        Returns:
            {
              "rpu": str,
              "session_cached": bool,
              "expires_at": ISO-8601 | None,
              "minutes_until_expiry": int,
            }
        """
        rpu = validar_rpu(rpu)
        session_key = f"session:{rpu}"
        cached = self.cache.get(session_key)
        if cached is None:
            return {
                "rpu": rpu,
                "session_cached": False,
                "expires_at": None,
                "minutes_until_expiry": 0,
            }
        expires_at = cached.get("expires_at", "")
        try:
            exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            mins = max(0, int((exp_dt - now).total_seconds() / 60))
        except Exception:
            mins = 0
        return {
            "rpu": rpu,
            "session_cached": mins > 0,
            "expires_at": expires_at,
            "minutes_until_expiry": mins,
        }

    # ============================================================
    # Real path (Playwright + human-in-loop)
    # ============================================================

    def _real_factura(self, rpu: str, periodo: str) -> dict[str, Any]:
        """Path real — requiere PLUGINS_MX_CFE_LIVE + credenciales en env."""
        cookies = self._get_or_create_session(rpu)
        if not cookies:
            raise UpstreamError(
                "No fue posible obtener sesión CFE. Verifica CFE_RPU + CFE_PASSWORD "
                "y que el humano completó el CAPTCHA durante el flow.",
                {"hint": "Setea PLUGINS_MX_CFE_LIVE=1 para activar Playwright headed."},
            )

        html = self._fetch_with_cookies(cookies, URL_CFE_MIESPACIO_FACTURA)
        parsed = _parse_cfe_factura_html(html, rpu)
        parsed["periodo"] = periodo or parsed.get("periodo_detectado", "")
        parsed["session_used"] = "cached"
        parsed["fecha_consulta"] = datetime.now(timezone.utc).isoformat()
        parsed["fuente"] = URL_CFE_MIESPACIO_FACTURA
        parsed["simulated"] = False
        return parsed

    def _real_consumo(self, rpu: str, meses: int) -> dict[str, Any]:
        cookies = self._get_or_create_session(rpu)
        if not cookies:
            raise UpstreamError("No fue posible obtener sesión CFE.")
        html = self._fetch_with_cookies(cookies, URL_CFE_MIESPACIO_CONSUMO)
        parsed = _parse_cfe_consumo_html(html, rpu, meses)
        parsed["session_used"] = "cached"
        parsed["fecha_consulta"] = datetime.now(timezone.utc).isoformat()
        parsed["fuente"] = URL_CFE_MIESPACIO_CONSUMO
        parsed["simulated"] = False
        return parsed

    def _fetch_with_cookies(self, cookies: list[dict], url: str) -> str:
        """Reabre Playwright con cookies cacheadas y descarga HTML de la página."""
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:
            raise ConfigError("Playwright no disponible.", {"raw": str(e)})

        headless = os.getenv("PLUGINS_MX_CFE_HEADLESS", "1") == "1"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            ctx = browser.new_context(locale="es-MX")
            # Las cookies de Playwright tienen formato distinto; convertimos
            ctx.add_cookies([{
                "name": c.get("name", ""),
                "value": c.get("value", ""),
                "domain": c.get("domain", "app.cfe.mx"),
                "path": c.get("path", "/"),
            } for c in cookies if c.get("name")])
            page = ctx.new_page()
            page.set_default_timeout(45000)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=30000)
            html = page.content()
            browser.close()
            return html

    def _get_or_create_session(self, rpu: str) -> Optional[list[dict]]:
        """Obtiene cookies de sesión cacheadas o lanza human-in-loop para crear."""
        session_key = f"session:{rpu}"
        cached = self.cache.get(session_key)
        if cached and self._session_aun_viva(cached):
            return cached.get("cookies")

        # Path human-in-loop con Playwright headed
        try:
            from shared.playwright_session import PortalSession  # noqa
        except ImportError as e:
            raise ConfigError(
                "Playwright no disponible. Instala: pip install playwright && playwright install chromium",
                {"raw": str(e)},
            ) from e

        password = os.environ.get("CFE_PASSWORD", "")
        if not password:
            raise ConfigError(
                "CFE_PASSWORD no está en env. Para path real CFE necesitas: "
                "CFE_RPU + CFE_PASSWORD + PLUGINS_MX_CFE_LIVE=1.",
                {"env_vars_requeridas": CRED_VARS},
            )

        cookies = self._human_in_loop_login(rpu, password)
        if cookies:
            self.cache.set(
                session_key,
                {
                    "cookies": cookies,
                    "rpu": rpu,
                    "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=SESSION_TTL_MINUTES)).isoformat(),
                },
                ttl_hours=SESSION_TTL_MINUTES / 60.0,
            )
        return cookies

    def _human_in_loop_login(self, rpu: str, password: str) -> Optional[list[dict]]:
        """Lanza Playwright para login con CAPTCHA human-in-loop.

        Flujo:
          1. Abre Chromium (headless o headed según PLUGINS_MX_CFE_HEADLESS).
          2. Navega a Login.aspx, prellenado usuario+password.
          3. Captura screenshot del CAPTCHA imagen.
          4. Resuelve captcha vía cascada:
             - env PLUGINS_MX_CFE_CAPTCHA (single-use), o
             - input() interactivo si stdin es TTY, o
             - falla con McpError.
          5. Click btnIngresar, verifica redirect a Default.aspx (sesión válida).
          6. Extrae cookies del contexto y las devuelve.
        """
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:
            raise ConfigError(
                "Playwright requerido para login CFE.",
                {"hint": "pip install playwright && playwright install chromium",
                 "raw": str(e)},
            )

        headless = os.getenv("PLUGINS_MX_CFE_HEADLESS", "1") == "1"
        timeout_ms = int(os.getenv("PLUGINS_MX_CFE_TIMEOUT_MS", "90000"))
        captcha_dir = Path(os.getenv("PLUGINS_MX_CAPTCHA_DIR", "/tmp/plugins_mx_captcha"))
        captcha_dir.mkdir(parents=True, exist_ok=True)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                ctx = browser.new_context(locale="es-MX")
                page = ctx.new_page()
                page.set_default_timeout(timeout_ms)

                page.goto(URL_CFE_MIESPACIO_LOGIN, wait_until="domcontentloaded")
                page.wait_for_selector(SELECTORES_CFE_LOGIN["usuario"], state="visible")
                page.fill(SELECTORES_CFE_LOGIN["usuario"], rpu)
                page.fill(SELECTORES_CFE_LOGIN["password"], password)

                captcha_path = captcha_dir / f"cfe_{rpu}_{int(datetime.now(timezone.utc).timestamp())}.png"
                page.locator(SELECTORES_CFE_LOGIN["captcha_img"]).first.screenshot(path=str(captcha_path))

                code = _resolve_cfe_captcha(captcha_path, rpu)
                if not code:
                    raise McpError(
                        "Captcha CFE no resuelto — proporcionar via PLUGINS_MX_CFE_CAPTCHA "
                        "o ejecutar interactivamente.",
                        {"captcha_path": str(captcha_path)},
                    )
                page.fill(SELECTORES_CFE_LOGIN["captcha"], code)
                page.click(SELECTORES_CFE_LOGIN["submit"])

                # Login OK redirige a Default.aspx. Si falla, queda en Login.aspx con mensaje.
                try:
                    page.wait_for_url(re.compile(r"/Default\.aspx", re.I), timeout=20000)
                except Exception:
                    err = ""
                    try:
                        err = page.locator(".lblError, [id*='Error']").first.inner_text(timeout=2000)
                    except Exception:
                        pass
                    raise UpstreamError(
                        f"Login CFE falló (URL no llegó a Default.aspx): {err or 'razón no detectada'}",
                        {"hint": "Captcha incorrecto o credenciales inválidas."},
                    )

                cookies = ctx.cookies()
                browser.close()
                return cookies

        except (McpError, UpstreamError):
            raise
        except Exception as e:
            raise UpstreamError(
                f"CFE login Playwright falló: {type(e).__name__}: {e}",
                {"rpu_hash": self.bitacora.hash_sensitive(rpu)},
            )

    def _session_aun_viva(self, cached: dict) -> bool:
        try:
            exp = datetime.fromisoformat(cached["expires_at"].replace("Z", "+00:00"))
            return exp > datetime.now(timezone.utc)
        except Exception:
            return False

    # ============================================================
    # Mock layer
    # ============================================================

    def _mock_factura(self, rpu: str, periodo: str) -> dict[str, Any]:
        periodo = periodo or datetime.now(timezone.utc).strftime("%Y-%m")
        # Determinístico por último char del RPU
        last = rpu[-1]
        kwh = 200 + int(last) * 30
        monto = round(kwh * 2.85, 2)
        estatus_map = {"0": "PAGADA", "1": "PENDIENTE", "2": "PAGADA", "3": "VENCIDA"}
        estatus = estatus_map.get(last, "PAGADA")
        return mark_simulated({
            "rpu": rpu,
            "periodo": periodo,
            "monto_total": monto,
            "consumo_kwh": kwh,
            "vencimiento": "2026-08-15",
            "pdf_base64": "JVBERi0xLjQK<<MOCK_PDF>>",
            "estatus": estatus,
            "tarifa": "01" if int(last) < 5 else "DAC",
            "session_used": "mock",
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": URL_CFE_MIESPACIO_LOGIN,
        })

    def _mock_consumo(self, rpu: str, meses: int) -> dict[str, Any]:
        last = rpu[-1]
        base = 200 + int(last) * 30
        meses_data = []
        suma = 0
        now = datetime.now(timezone.utc)
        for i in range(meses):
            kwh = base + ((i * 7) % 80) - 40  # variación pseudo-aleatoria
            kwh = max(50, kwh)
            mes = (now.year - (i // 12), (now.month - i - 1) % 12 + 1)
            meses_data.append({
                "mes": f"{mes[0]}-{mes[1]:02d}",
                "kwh": kwh,
                "monto": round(kwh * 2.85, 2),
            })
            suma += kwh
        promedio = round(suma / meses, 1) if meses else 0
        # Tendencia: comparar primer vs último mes
        primer = meses_data[-1]["kwh"] if meses_data else 0
        ultimo = meses_data[0]["kwh"] if meses_data else 0
        delta_pct = ((ultimo - primer) / max(primer, 1)) * 100
        if delta_pct > 25:
            tendencia = "AUMENTO"
        elif delta_pct < -25:
            tendencia = "DISMINUCION"
        else:
            tendencia = "ESTABLE"
        anomalia = any(m["kwh"] > promedio * 1.5 for m in meses_data)
        return mark_simulated({
            "rpu": rpu,
            "meses_solicitados": meses,
            "consumo_kwh_por_mes": meses_data,
            "promedio_kwh_mensual": promedio,
            "tendencia": tendencia,
            "anomalia_detectada": anomalia,
            "session_used": "mock",
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": URL_CFE_MIESPACIO_LOGIN,
        })


# ============================================================
# Captcha resolver + HTML parsers
# ============================================================
def _resolve_cfe_captcha(captcha_path: Path, rpu: str) -> Optional[str]:
    """Cascada: env → TTY → None.

    1. PLUGINS_MX_CFE_CAPTCHA (single-use por ejecución).
    2. input() interactivo si stdin es TTY.
    3. None (caller debe lanzar McpError con captcha_path para inspección).
    """
    env_code = os.getenv("PLUGINS_MX_CFE_CAPTCHA", "").strip()
    if env_code:
        return env_code

    import sys as _sys
    if _sys.stdin.isatty():
        try:
            print(f"\n[plugins-mx] CAPTCHA CFE para RPU {rpu[:4]}...{rpu[-4:]}")
            print(f"  Imagen guardada en: {captcha_path}")
            return input("  Código: ").strip() or None
        except (EOFError, KeyboardInterrupt):
            return None
    return None


def _strip_html(html: str) -> str:
    """Strip tags y colapsa whitespace para parseo robusto."""
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text)


def _parse_cfe_factura_html(html: str, rpu: str) -> dict[str, Any]:
    """Extrae datos de Pagar.aspx — monto, kWh, vencimiento, estatus."""
    text = _strip_html(html)
    result: dict[str, Any] = {
        "operation": "descargar_factura_mes",
        "rpu": rpu,
    }

    def _grab(pattern: str) -> Optional[str]:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else None

    monto = _grab(r"[Tt]otal\s+a\s+pagar[^\d]{0,80}\$\s*([0-9]{1,3}(?:[,\.][0-9]{3})*[\.,][0-9]{2})")
    if not monto:
        monto = _grab(r"\$\s*([0-9]{1,3}(?:[,\.][0-9]{3})*[\.,][0-9]{2})")
    if monto:
        try:
            result["monto_total_mxn"] = float(monto.replace(",", ""))
        except ValueError:
            result["monto_total_raw"] = monto

    consumo = _grab(r"([0-9]{1,5})\s*kWh")
    if consumo:
        result["consumo_kwh"] = int(consumo)

    venc = _grab(r"[Vv]encimiento[^\d]{0,80}(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})")
    if venc:
        result["vencimiento"] = venc

    estatus = _grab(r"\b(PAGADA|PENDIENTE|VENCIDA|EN\s+TR[ÁA]MITE)\b")
    if estatus:
        result["estatus"] = estatus.upper()

    periodo = _grab(r"[Pp]eriodo[^\d]{0,30}(\d{4}-\d{2}|[A-Za-z]+\s+\d{4})")
    if periodo:
        result["periodo_detectado"] = periodo

    if "monto_total_mxn" not in result and "monto_total_raw" not in result:
        result["parse_partial"] = True
        result["html_snippet"] = text[:500]
    return result


def _parse_cfe_consumo_html(html: str, rpu: str, meses: int) -> dict[str, Any]:
    """Extrae histórico kWh de HistorialConsumo.aspx.

    El portal renderiza una tabla con columnas: mes, kWh, monto. Buscamos
    todas las parejas (mes, kwh) y devolvemos hasta `meses` entradas.
    """
    text = _strip_html(html)
    # Patrones flexibles: "Mayo 2026 ... 245 kWh ... $ 698.25"
    rows = re.findall(
        r"([A-Za-z]{3,12}\s+\d{4})\s+([0-9]{1,5})\s*kWh\s*[\$\s]*([0-9]{1,3}(?:[,\.][0-9]{3})*[\.,][0-9]{2})?",
        text,
    )
    consumo_kwh_por_mes: list[dict[str, Any]] = []
    for mes, kwh, monto in rows[:meses]:
        entry: dict[str, Any] = {"mes": mes, "kwh": int(kwh)}
        if monto:
            try:
                entry["monto_mxn"] = float(monto.replace(",", ""))
            except ValueError:
                pass
        consumo_kwh_por_mes.append(entry)

    promedio = (
        round(sum(e["kwh"] for e in consumo_kwh_por_mes) / len(consumo_kwh_por_mes), 1)
        if consumo_kwh_por_mes else 0.0
    )
    return {
        "operation": "consumo_historico",
        "rpu": rpu,
        "meses_solicitados": meses,
        "consumo_kwh_por_mes": consumo_kwh_por_mes,
        "promedio_kwh_mensual": promedio,
        "parse_partial": len(consumo_kwh_por_mes) == 0,
    }
