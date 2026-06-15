"""Cliente mp_verificacion_vehicular_mx."""
from __future__ import annotations

import base64
import os
import re
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
from shared.errors import McpError, NotFoundError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.verificacion_vehicular import (  # noqa: E402
    buscar_programa,
    calcular_proximo_periodo,
    CATALOGO_VERIFICACION,
    mes_proxima_verificacion,
    SAF_CDMX_FIELDS,
    URL_SAF_CDMX_CONSULTA,
)


NAMESPACE = "verificacion_vehicular"
LIVE_ENV_FLAG = "PLUGINS_MX_VERIFICACION_LIVE"


class VerificacionVehicularClient:
    def __init__(self, cache: FileCache | None = None, bitacora: Bitacora | None = None) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_estatus(self, placa: str, estado: str) -> dict[str, Any]:
        """Consulta estatus de la última verificación del vehículo."""
        placa = placa.strip().upper().replace(" ", "").replace("-", "")
        if len(placa) < 5:
            raise ValidationError(f"Placa muy corta: {placa}")
        p = buscar_programa(estado)
        if p is None:
            raise NotFoundError(f"Estado '{estado}' no en catálogo verificación.")

        cache_key = f"{estado}:{placa}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        live = os.getenv(LIVE_ENV_FLAG, "").strip() == "1"
        if live and estado == "cdmx":
            try:
                result = self._real_consultar_cdmx(placa)
            except (McpError, UpstreamError):
                raise
        else:
            result = self._mock(p, placa)

        self._cache.set(cache_key, result, ttl_hours=24 * 30)
        self._bitacora.log("consultar_estatus", success=True,
                           params_summary={"estado": estado, "placa_hash": self._bitacora.hash_sensitive(placa),
                                           "modo": "live" if live and estado == "cdmx" else "mock"})
        return result

    def proximo_periodo(self, placa: str, estado: str = "cdmx") -> dict[str, Any]:
        """Calcula próximo periodo de verificación según color de engomado."""
        placa = placa.strip().upper().replace(" ", "").replace("-", "")
        if not placa:
            raise ValidationError("Placa requerida")
        # Último char numérico = terminación
        terminacion = None
        for c in reversed(placa):
            if c.isdigit():
                terminacion = int(c)
                break
        if terminacion is None:
            raise ValidationError(f"Placa '{placa}' sin dígitos.")
        now = datetime.now(timezone.utc)
        color, meses = calcular_proximo_periodo(terminacion, now.month)
        proximo = mes_proxima_verificacion(terminacion, now.month)
        return {
            "placa": placa,
            "estado": estado,
            "terminacion": terminacion,
            "color_engomado": color,
            "meses_obligatorios": meses,
            "proximo_mes_verificacion": proximo if proximo <= 12 else proximo - 12,
            "proximo_anio_verificacion": now.year if proximo <= 12 else now.year + 1,
            "fecha_consulta": now.isoformat(),
        }

    def listar_programas(self) -> dict[str, Any]:
        return {
            "total": len(CATALOGO_VERIFICACION),
            "programas": [{
                "clave": p.clave, "estado": p.nombre_estado, "activo": p.activo,
                "frecuencia_meses": p.frecuencia_meses, "costo_mxn": p.costo_mxn,
                "portal": p.portal_url,
            } for p in CATALOGO_VERIFICACION],
        }

    def _mock(self, p, placa: str) -> dict[str, Any]:
        # Determinístico por último digit
        last_d = "5"
        for c in reversed(placa):
            if c.isdigit():
                last_d = c; break
        hologramas = {"0": "00", "1": "0", "2": "1", "3": "2", "4": "00", "5": "0",
                       "6": "1", "7": "2", "8": "Rechazo", "9": "0"}
        h = hologramas.get(last_d, "0")
        return mark_simulated({
            "placa": placa,
            "estado": p.clave,
            "ultima_verificacion": "2026-04-15",
            "holograma_actual": h,
            "vigencia_hasta": "2026-10-15",
            "vigente": h != "Rechazo",
            "costo_proxima_verificacion_mxn": p.costo_mxn,
            "fuente": p.portal_url,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    # ============================================================
    # REAL path — SAF CDMX (consulta pública con CAPTCHA imagen)
    # ============================================================
    def _real_consultar_cdmx(self, placa: str) -> dict[str, Any]:
        """Consulta SAF CDMX con human-in-loop para CAPTCHA.

        Flujo:
          1. Abre Playwright (headed por default).
          2. Navega a data.finanzas.cdmx.gob.mx/sma/Consultaciudadana.
          3. Llena `inputPlaca` con la placa.
          4. Captura screenshot del CAPTCHA y lo guarda en disco.
          5. Solicita el código vía:
             - callback registrado en el cliente (`captcha_resolver`), o
             - var de entorno `PLUGINS_MX_VERIFICACION_CAPTCHA` (single-use), o
             - input() interactivo si stdin es TTY.
          6. Llena `captcha_code` y envía.
          7. Parsea la página de resultados.
        """
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:
            raise McpError(
                "Playwright requerido para path real CDMX.",
                {"hint": "pip install playwright && playwright install chromium"},
            )

        headless = os.getenv("PLUGINS_MX_VERIFICACION_HEADLESS", "1") == "1"
        timeout_ms = int(os.getenv("PLUGINS_MX_VERIFICACION_TIMEOUT_MS", "60000"))
        captcha_dir = Path(os.getenv("PLUGINS_MX_CAPTCHA_DIR", "/tmp/plugins_mx_captcha"))
        captcha_dir.mkdir(parents=True, exist_ok=True)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                ctx = browser.new_context(locale="es-MX")
                page = ctx.new_page()
                page.set_default_timeout(timeout_ms)

                page.goto(URL_SAF_CDMX_CONSULTA, wait_until="domcontentloaded")
                page.wait_for_selector(f"input#{SAF_CDMX_FIELDS['placa']}",
                                       state="visible")
                page.fill(f"input#{SAF_CDMX_FIELDS['placa']}", placa)

                captcha_path = captcha_dir / f"saf_cdmx_{placa}_{int(datetime.now(timezone.utc).timestamp())}.png"
                captcha_img = page.locator("img[id*='captcha'], img[src*='captcha']").first
                captcha_img.screenshot(path=str(captcha_path))

                code = _resolve_captcha(captcha_path, placa)
                if not code:
                    raise McpError(
                        "Captcha SAF CDMX no resuelto — proporcionar via "
                        "PLUGINS_MX_VERIFICACION_CAPTCHA o resolver interactivamente.",
                        {"captcha_path": str(captcha_path)},
                    )

                page.fill(f"input#{SAF_CDMX_FIELDS['captcha']}", code)
                page.click("button[type='submit'], input[type='submit'][name*='uscar']")
                page.wait_for_load_state("networkidle", timeout=timeout_ms)

                html = page.content()
                parsed = _parse_saf_cdmx_html(html, placa)
                browser.close()

            parsed["placa"] = placa
            parsed["estado"] = "cdmx"
            parsed["fuente"] = URL_SAF_CDMX_CONSULTA
            parsed["fecha_consulta"] = datetime.now(timezone.utc).isoformat()
            parsed["simulated"] = False
            return parsed

        except McpError:
            raise
        except Exception as e:
            raise UpstreamError(
                f"SAF CDMX consulta falló: {type(e).__name__}: {e}",
                {"placa_hash": self._bitacora.hash_sensitive(placa)},
            )


def _resolve_captcha(captcha_path: Path, placa: str) -> Optional[str]:
    """Resuelve CAPTCHA imagen:
    1. Si PLUGINS_MX_VERIFICACION_CAPTCHA está set → úsalo (single-use).
    2. Si stdin es TTY → input() interactivo.
    3. Si no → None (caller debe configurar resolver).
    """
    env_code = os.getenv("PLUGINS_MX_VERIFICACION_CAPTCHA", "").strip()
    if env_code:
        return env_code

    import sys as _sys
    if _sys.stdin.isatty():
        try:
            print(f"\n[plugins-mx] CAPTCHA SAF CDMX para placa {placa}")
            print(f"  Imagen guardada en: {captcha_path}")
            return input("  Código: ").strip() or None
        except (EOFError, KeyboardInterrupt):
            return None
    return None


def _parse_saf_cdmx_html(html: str, placa: str) -> dict[str, Any]:
    """Extrae datos de verificación/adeudos del HTML SAF CDMX.

    El portal renderiza una tabla con: placa, modelo, marca, holograma,
    fecha última verificación, vigencia, adeudo total.
    Strip de tags HTML antes del regex para tolerar `<td>X</td><td>VALOR</td>`.
    """
    # Strip HTML tags y colapsa whitespace para parseo robusto
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    result: dict[str, Any] = {
        "operation": "consultar_estatus_cdmx",
        "placa": placa,
    }

    def _grab(pattern: str) -> Optional[str]:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else None

    # Patrones tolerantes a HTML (tags entre keyword y valor)
    holograma = _grab(r"[Hh]olograma[^A-Za-z0-9]{0,80}(00|0|1|2|Exento|Rechazo)\b")
    if holograma:
        result["holograma_actual"] = holograma

    ultima = _grab(r"[ÚU]ltima\s+verificaci[óo]n[^\d]{0,80}(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})")
    if ultima:
        result["ultima_verificacion"] = ultima

    vigencia = _grab(r"[Vv]igencia\s+hasta[^\d]{0,80}(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})")
    if vigencia:
        result["vigencia_hasta"] = vigencia

    adeudo = _grab(r"[Aa]deudo[^\d]{0,80}\$\s*([0-9]{1,3}(?:[,\.][0-9]{3})*[\.,][0-9]{2})")
    if adeudo:
        try:
            result["adeudo_total_mxn"] = float(adeudo.replace(",", ""))
        except ValueError:
            result["adeudo_raw"] = adeudo

    if "holograma_actual" not in result:
        result["parse_partial"] = True
        result["html_snippet"] = html[:500]

    result["vigente"] = result.get("holograma_actual") not in (None, "Rechazo")
    return result
