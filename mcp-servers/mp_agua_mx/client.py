"""Cliente unificado consulta agua municipal/estatal MX.

3 modos:
  - mock (default): respuestas determinísticas por organismo
  - playwright (PLUGINS_MX_AGUA_LIVE=1): scraping real por organismo
  - cached: TTL 14 días (los recibos cambian bimestral)

Auto-routing: el cliente recibe (organismo, cuenta) y decide:
  1. Si el organismo está consultable=True → path real
  2. Si no → mock con advertencia "no implementado aún"
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import os  # noqa: E402

from shared.agua_mx import (  # noqa: E402
    CATALOGO_AGUA,
    OrganismoAgua,
    SIAPA_FIELDS,
    URL_SIAPA_CONSULTA,
    buscar_organismo,
    buscar_por_estado,
    estadisticas,
    listar_organismos,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, NotFoundError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.playwright_session import should_use_real_browser  # noqa: E402


NAMESPACE = "agua_mx"
CACHE_TTL_HOURS = 24 * 14  # 14 días — recibos bimestrales
LIVE_ENV_FLAG = "PLUGINS_MX_AGUA_LIVE"


class AguaMxClient:
    """Cliente unificado consulta agua."""

    LIVE_ENV_FLAG = "PLUGINS_MX_AGUA_LIVE"

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    # ============================================================
    # Tools
    # ============================================================

    def consultar_adeudo(
        self,
        organismo: str,
        cuenta: str,
    ) -> dict[str, Any]:
        """Consulta el adeudo actual de una cuenta de agua.

        Args:
            organismo: clave del operador (sacmex, siapa, sadm, etc.).
            cuenta: identificador del usuario (cuenta, contrato, NIS según organismo).

        Returns:
            {
              "organismo": str,
              "cuenta": str,
              "consultado": bool,
              "adeudo_mxn": float,
              "vencimiento": str,
              "estatus": "AL DIA" | "PENDIENTE" | "VENCIDO" | "NO_IMPLEMENTADO",
              "ultimo_pago": str | None,
              "consumo_m3": float | None,
              "advertencias": [str],
              "fuente": URL,
              "fecha_consulta": ISO-8601,
              "simulated": bool,
            }
        """
        org = buscar_organismo(organismo)
        if not org:
            raise NotFoundError(
                f"Organismo '{organismo}' no está en el catálogo. "
                f"Usa agua_listar_organismos() para ver opciones.",
                {"organismo_solicitado": organismo},
            )

        cuenta = cuenta.strip()
        if not cuenta:
            raise ValidationError("Cuenta requerida.")
        if not re.match(org.identificador_regex, cuenta):
            raise ValidationError(
                f"Cuenta '{cuenta}' no matchea formato esperado de {org.clave}: {org.identificador_regex}.",
                {"organismo": org.clave, "esperado": org.identificador_regex},
            )

        cache_key = f"{org.clave}:{cuenta}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        live = os.getenv(LIVE_ENV_FLAG, "").strip() == "1"
        if not org.consultable:
            result = self._not_implemented(org, cuenta)
        elif live and org.clave == "siapa":
            result = self._real_siapa(cuenta)
        elif is_mock_mode(credential_env_vars=[], default_when_no_creds=True):
            # Default mock para agua (path real requiere Playwright + portal-specific)
            result = self._mock(org, cuenta)
        else:
            # Path real — pendiente implementación específica por organismo
            result = self._real_pending(org, cuenta)

        self._cache.set(cache_key, result, ttl_hours=CACHE_TTL_HOURS)
        self._bitacora.log(
            "consultar_adeudo",
            success=True,
            params_summary={
                "organismo": org.clave,
                "cuenta_hash": self._bitacora.hash_sensitive(cuenta),
                "consultado": result.get("consultado"),
            },
        )
        return result

    def listar_organismos(self, solo_consultables: bool = False) -> dict[str, Any]:
        """Lista organismos en el catálogo."""
        orgs = listar_organismos(solo_consultables=solo_consultables)
        return {
            "total": len(orgs),
            "filtro_solo_consultables": solo_consultables,
            "organismos": [
                {
                    "clave": o.clave,
                    "nombre": o.nombre_completo,
                    "estado": o.estado,
                    "municipios_cubre": o.municipio,
                    "url_portal": o.url_portal,
                    "identificador": o.identificador_label,
                    "metodo": o.metodo,
                    "frecuencia": o.frecuencia_recibo,
                    "poblacion_aprox": o.poblacion_aprox,
                    "consultable": o.consultable,
                }
                for o in orgs
            ],
        }

    def buscar_por_estado(self, estado: str) -> dict[str, Any]:
        """Lista organismos que cubren un estado mexicano."""
        orgs = buscar_por_estado(estado)
        return {
            "estado_buscado": estado.upper(),
            "encontrados": len(orgs),
            "organismos": [{"clave": o.clave, "nombre": o.nombre_completo, "consultable": o.consultable} for o in orgs],
        }

    def estadisticas_catalogo(self) -> dict[str, Any]:
        """Stats agregadas del catálogo."""
        return estadisticas()

    # ============================================================
    # Internal paths
    # ============================================================

    def _not_implemented(self, org: OrganismoAgua, cuenta: str) -> dict[str, Any]:
        return {
            "organismo": org.clave,
            "cuenta": cuenta,
            "consultado": False,
            "adeudo_mxn": 0.0,
            "vencimiento": "",
            "estatus": "NO_IMPLEMENTADO",
            "ultimo_pago": None,
            "consumo_m3": None,
            "advertencias": [
                f"⚠️ El organismo {org.clave} ({org.nombre_completo}) está en el catálogo "
                f"pero el scraper Playwright NO está implementado aún. {org.notas}"
            ],
            "fuente": org.url_portal,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    def _real_pending(self, org: OrganismoAgua, cuenta: str) -> dict[str, Any]:
        """Placeholder para organismos sin scraper implementado todavía."""
        return self._not_implemented(org, cuenta)

    # ============================================================
    # SIAPA real path — reCAPTCHA v2 human-in-loop
    # ============================================================
    def _real_siapa(self, cuenta: str) -> dict[str, Any]:
        """Consulta SIAPA Guadalajara con Playwright.

        SIAPA usa reCAPTCHA v2 checkbox. El flujo:
          1. Abre Playwright (default headless=0 para que el humano vea checkbox).
          2. Llena cuenta_contrato y clavesiapa.
          3. Espera token reCAPTCHA — fuentes en orden:
             - env PLUGINS_MX_SIAPA_RECAPTCHA_TOKEN (pre-resuelto, single-use).
             - User interaction si headless=0 + TTY (click checkbox manualmente).
          4. Submit y parsea HTML respuesta.
        """
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:
            raise McpError(
                "Playwright requerido para SIAPA real.",
                {"hint": "pip install playwright && playwright install chromium",
                 "raw": str(e)},
            )

        clave = os.getenv("SIAPA_CLAVE", "").strip()
        if not clave:
            raise McpError(
                "SIAPA requiere 'clavesiapa' (NIP del usuario). Configurar SIAPA_CLAVE.",
                {"hint": "SIAPA muestra una clave en el recibo físico."},
            )

        # Default headless=0 porque reCAPTCHA v2 checkbox necesita interacción humana.
        headless = os.getenv("PLUGINS_MX_SIAPA_HEADLESS", "0") == "1"
        timeout_ms = int(os.getenv("PLUGINS_MX_SIAPA_TIMEOUT_MS", "120000"))
        token_env = os.getenv("PLUGINS_MX_SIAPA_RECAPTCHA_TOKEN", "").strip()

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                ctx = browser.new_context(locale="es-MX")
                page = ctx.new_page()
                page.set_default_timeout(timeout_ms)

                page.goto(URL_SIAPA_CONSULTA, wait_until="domcontentloaded")
                page.wait_for_selector(f"input#{SIAPA_FIELDS['cuenta_contrato']}",
                                       state="visible")
                page.fill(f"input#{SIAPA_FIELDS['cuenta_contrato']}", cuenta)
                page.fill(f"input#{SIAPA_FIELDS['clavesiapa']}", clave)

                if token_env:
                    # Pre-resuelto via solver service externo
                    page.evaluate(
                        "(tok) => { document.getElementById('g-recaptcha-response').value = tok; "
                        "document.getElementById('g-recaptcha-response').innerHTML = tok; }",
                        token_env,
                    )
                else:
                    # Human-in-loop: esperar a que el humano marque el checkbox.
                    # Cuando hace click, Google inyecta el token en el textarea oculto.
                    page.wait_for_function(
                        "() => { const r = document.getElementById('g-recaptcha-response'); "
                        "return r && r.value && r.value.length > 20; }",
                        timeout=timeout_ms,
                    )

                # Submit y wait
                page.click("input#enviar, input[type='submit'][name='enviar']")
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
                html = page.content()
                browser.close()

            parsed = _parse_siapa_html(html, cuenta)
            parsed["organismo"] = "siapa"
            parsed["cuenta"] = cuenta
            parsed["fuente"] = URL_SIAPA_CONSULTA
            parsed["fecha_consulta"] = datetime.now(timezone.utc).isoformat()
            parsed["simulated"] = False
            return parsed

        except McpError:
            raise
        except Exception as e:
            raise UpstreamError(
                f"SIAPA consulta falló: {type(e).__name__}: {e}",
                {"cuenta_hash": self._bitacora.hash_sensitive(cuenta)},
            )

    def _mock(self, org: OrganismoAgua, cuenta: str) -> dict[str, Any]:
        """Mock determinístico por suffix de cuenta."""
        last = cuenta[-1] if cuenta else "0"
        if last in "02468":
            adeudo = 0.0
            estatus = "AL DIA"
            consumo = 15.5
        elif last in "13579":
            # Adeudo proporcional al digit
            adeudo = float(int(last) * 145.30 + 122.50)
            estatus = "PENDIENTE" if int(last) <= 5 else "VENCIDO"
            consumo = 22.7
        else:
            adeudo = 0.0
            estatus = "AL DIA"
            consumo = 18.2

        return mark_simulated({
            "organismo": org.clave,
            "cuenta": cuenta,
            "consultado": True,
            "adeudo_mxn": adeudo,
            "vencimiento": "2026-08-15",
            "estatus": estatus,
            "ultimo_pago": "2026-04-22",
            "consumo_m3": consumo,
            "advertencias": [] if estatus == "AL DIA" else [
                f"Adeudo {estatus.lower()} — pagar antes del 15-ago para evitar recargos."
            ],
            "fuente": org.url_portal,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })


# ============================================================
# SIAPA HTML parser
# ============================================================
def _parse_siapa_html(html: str, cuenta: str) -> dict[str, Any]:
    """Extrae datos del HTML respuesta de SIAPA pago_en_linea.

    NOTA: estructura HTML real NO verificada — el form NO se envió en discovery
    para no spamear el portal con datos inválidos. Patrones genéricos que
    pueden requerir ajuste en primera consulta con cuenta válida.
    """
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    result: dict[str, Any] = {"operation": "consultar_adeudo"}

    def _grab(pattern: str) -> Optional[str]:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else None

    # Patrones esperados (a ajustar tras primera consulta real)
    adeudo = _grab(r"[Aa]deudo[^\d]{0,80}\$\s*([0-9]{1,3}(?:[,\.][0-9]{3})*[\.,][0-9]{2})")
    if not adeudo:
        adeudo = _grab(r"[Tt]otal[^\d]{0,80}\$\s*([0-9]{1,3}(?:[,\.][0-9]{3})*[\.,][0-9]{2})")
    if adeudo:
        try:
            result["adeudo_total_mxn"] = float(adeudo.replace(",", ""))
        except ValueError:
            result["adeudo_raw"] = adeudo

    consumo = _grab(r"([0-9]{1,4}(?:\.[0-9]{1,2})?)\s*m\s*3|([0-9]{1,4})\s*metros\s+c[úu]bicos")
    if consumo:
        try:
            result["consumo_m3"] = float(consumo)
        except ValueError:
            pass

    estatus = _grab(r"\b(AL\s+DIA|PENDIENTE|VENCIDO|MOROSO)\b")
    if estatus:
        result["estatus"] = re.sub(r"\s+", " ", estatus.upper())

    if "adeudo_total_mxn" not in result and "adeudo_raw" not in result:
        result["parse_partial"] = True
        result["html_snippet"] = text[:500]
        result["needs_calibration"] = True  # primer hit calibra selectores

    return result
