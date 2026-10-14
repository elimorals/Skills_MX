"""Cliente mp_portales_monitor — monitor continuo de portales gob.mx.

Pone a un servicio común (estatales/municipales con bajo presupuesto IT) sobre
sus 50+ portales: ¿están vivos? ¿responden con 200? ¿el último deploy rompió
formularios? Producto pensado para licitación menor MIPYME via ComprasMX.

Modos:
- `check_http` — HEAD/GET simple (sin Playwright)
- `check_form_render` — verifica que el formulario clave renderice (Playwright opt-in)
- `check_critical_flow` — flow de extremo a extremo (Playwright + auth opt-in)
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.http_helpers import build_ssl_verify  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

import httpx  # noqa: E402


NAMESPACE = "portales_monitor"

# Catálogo de portales clave a monitorear — heredados del repo
# (extraídos del shared/catalogo_municipios_mx + portales gob.mx top demanda)
PORTALES_CATALOGO: list[dict[str, Any]] = [
    # FEDERALES TOP DEMANDA
    {"clave": "sat_padron", "nombre": "SAT — Consulta RFC",
     "url": "https://siat.sat.gob.mx/PTSC/IdentificacionContribuyentes/secuencia.html",
     "criticidad": "alta", "categoria": "federal_fiscal",
     "sla_max_ms": 5000},
    {"clave": "sat_verificacfdi", "nombre": "SAT — Verifica CFDI",
     "url": "https://verificacfdi.facturaelectronica.sat.gob.mx/",
     "criticidad": "alta", "categoria": "federal_fiscal",
     "sla_max_ms": 5000},
    {"clave": "imss_idse", "nombre": "IMSS — IDSE",
     "url": "https://idse.imss.gob.mx/",
     "criticidad": "alta", "categoria": "federal_laboral",
     "sla_max_ms": 8000},
    {"clave": "imss_semanas", "nombre": "IMSS — Semanas cotizadas",
     "url": "https://serviciosdigitales.imss.gob.mx/semanascotizadas/",
     "criticidad": "alta", "categoria": "federal_laboral",
     "sla_max_ms": 8000},
    {"clave": "infonavit_micuenta", "nombre": "INFONAVIT — Mi Cuenta",
     "url": "https://micuenta.infonavit.org.mx/",
     "criticidad": "alta", "categoria": "federal_vivienda",
     "sla_max_ms": 8000},
    {"clave": "renapo_curp", "nombre": "RENAPO — Consulta CURP",
     "url": "https://www.gob.mx/curp/",
     "criticidad": "alta", "categoria": "federal_identidad",
     "sla_max_ms": 5000},
    {"clave": "ine_portal", "nombre": "INE — Portal ciudadano",
     "url": "https://portal.ine.mx/",
     "criticidad": "media", "categoria": "federal_identidad",
     "sla_max_ms": 5000},
    {"clave": "sre_pasaporte", "nombre": "SRE — Citas pasaporte",
     "url": "https://citas.sre.gob.mx/",
     "criticidad": "alta", "categoria": "federal_consular",
     "sla_max_ms": 8000},
    {"clave": "profeco_repep", "nombre": "PROFECO — REPEP",
     "url": "https://repep.profeco.gob.mx/",
     "criticidad": "media", "categoria": "federal_consumidor",
     "sla_max_ms": 5000},
    {"clave": "profeco_buro", "nombre": "PROFECO — Buró Comercial",
     "url": "https://burocomercial.profeco.gob.mx/",
     "criticidad": "media", "categoria": "federal_consumidor",
     "sla_max_ms": 5000},
    {"clave": "stps_repse", "nombre": "STPS — REPSE",
     "url": "https://repse.stps.gob.mx/",
     "criticidad": "alta", "categoria": "federal_laboral",
     "sla_max_ms": 5000},
    {"clave": "conamer_catalogo", "nombre": "CONAMER — Catálogo Nacional",
     "url": "https://catalogonacional.gob.mx/",
     "criticidad": "media", "categoria": "federal_transversal",
     "sla_max_ms": 5000},
    {"clave": "llave_mx", "nombre": "Llave MX",
     "url": "https://www.llave.gob.mx/",
     "criticidad": "alta", "categoria": "federal_identidad",
     "sla_max_ms": 5000},
    {"clave": "dof", "nombre": "Diario Oficial de la Federación",
     "url": "https://www.dof.gob.mx/",
     "criticidad": "media", "categoria": "federal_transversal",
     "sla_max_ms": 5000},
    {"clave": "gobmx", "nombre": "Portal gob.mx",
     "url": "https://www.gob.mx/",
     "criticidad": "media", "categoria": "federal_transversal",
     "sla_max_ms": 5000},
    # ESTATALES — capitales + portales clave
    {"clave": "cdmx_finanzas", "nombre": "CDMX — Finanzas SAF",
     "url": "https://data.finanzas.cdmx.gob.mx/",
     "criticidad": "alta", "categoria": "estatal_cdmx",
     "sla_max_ms": 5000},
    {"clave": "cdmx_semovi", "nombre": "CDMX — SEMOVI",
     "url": "https://www.semovi.cdmx.gob.mx/",
     "criticidad": "media", "categoria": "estatal_cdmx",
     "sla_max_ms": 5000},
    {"clave": "edomex_portal", "nombre": "Edoméx — Portal único",
     "url": "https://edomex.gob.mx/",
     "criticidad": "alta", "categoria": "estatal",
     "sla_max_ms": 5000},
    {"clave": "nl_portal", "nombre": "Nuevo León — Portal",
     "url": "https://www.nl.gob.mx/",
     "criticidad": "alta", "categoria": "estatal",
     "sla_max_ms": 5000},
    {"clave": "jal_portal", "nombre": "Jalisco — Portal",
     "url": "https://www.jalisco.gob.mx/",
     "criticidad": "alta", "categoria": "estatal",
     "sla_max_ms": 5000},
    {"clave": "qro_portal", "nombre": "Querétaro — Portal",
     "url": "https://www.queretaro.gob.mx/",
     "criticidad": "media", "categoria": "estatal",
     "sla_max_ms": 5000},
    {"clave": "yuc_portal", "nombre": "Yucatán — Portal",
     "url": "https://www.yucatan.gob.mx/",
     "criticidad": "media", "categoria": "estatal",
     "sla_max_ms": 5000},
    {"clave": "bc_portal", "nombre": "Baja California — Portal",
     "url": "https://www.bajacalifornia.gob.mx/",
     "criticidad": "media", "categoria": "estatal",
     "sla_max_ms": 5000},
    # MUNICIPALES TOP
    {"clave": "monterrey_predial", "nombre": "Monterrey — Predial",
     "url": "https://www.monterrey.gob.mx/",
     "criticidad": "media", "categoria": "municipal",
     "sla_max_ms": 5000},
    {"clave": "guadalajara_predial", "nombre": "Guadalajara — Predial",
     "url": "https://visorurbano.com/", "criticidad": "media",
     "categoria": "municipal", "sla_max_ms": 5000},
]


BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)


def _portal(clave: str) -> dict[str, Any]:
    portal = next((p for p in PORTALES_CATALOGO if p["clave"] == clave), None)
    if not portal:
        raise ValidationError(f"clave no reconocida: {clave!r}")
    return portal


def _detectar_waf(r: httpx.Response) -> str | None:
    """Reconoce bloqueos de WAF (Akamai / Cloudflare) vistos en portales gob.mx."""
    if r.status_code not in (403, 429, 503):
        return None
    body = r.text[:2000]
    if "edgesuite.net" in body or ("Access Denied" in body and "Reference" in body):
        return "akamai"
    if "Just a moment" in body or r.headers.get("cf-mitigated") or "cloudflare" in (r.headers.get("server") or "").lower():
        return "cloudflare"
    return None


def _hash_estable(s: str) -> int:
    """Hash determinístico para tests."""
    import hashlib
    return int(hashlib.sha256(s.encode()).hexdigest(), 16)


class PortalesMonitorClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    def listar_portales(self, categoria: str | None = None) -> dict[str, Any]:
        """Lista portales monitoreados, filtrable por categoria."""
        self._log("listar_portales", {"categoria": categoria})
        items = PORTALES_CATALOGO
        if categoria:
            cat = categoria.lower().strip()
            items = [p for p in items if p["categoria"] == cat]
        return {
            "total": len(items),
            "portales": items,
        }

    def check_http(self, clave: str) -> dict[str, Any]:
        """GET real con latencia + SLA. Mock solo con PLUGINS_MX_MOCK=1.

        Un portal caído o bloqueado es un resultado legítimo del monitor
        (vivo=False), no un error del MCP.
        """
        self._log("check_http", {"clave": clave})
        portal = _portal(clave)

        if is_mock_mode([], default_when_no_creds=False):
            h = _hash_estable(clave)
            status = 200 if (h % 10) > 0 else 503
            latencia = (h % 4000) + 500
            return mark_simulated(
                {
                    "clave": clave,
                    "url": portal["url"],
                    "http_status": status,
                    "latencia_ms": latencia,
                    "vivo": status < 400,
                    "dentro_sla": latencia <= portal["sla_max_ms"],
                    "criticidad": portal["criticidad"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                note="PLUGINS_MX_MOCK=1 — check simulado.",
            )

        base = {
            "clave": clave,
            "url": portal["url"],
            "criticidad": portal["criticidad"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }
        # GET y no HEAD: varios servidores gob.mx responden 405/404 a HEAD.
        # Timeout holgado (30 s) para poder medir "fuera de SLA" en vez de cortar.
        inicio = time.monotonic()
        try:
            with httpx.Client(
                verify=build_ssl_verify(),
                timeout=30.0,
                follow_redirects=True,
                headers={"User-Agent": BROWSER_UA, "Accept-Language": "es-MX,es;q=0.9"},
            ) as client:
                r = client.get(portal["url"])
        except httpx.HTTPError as e:
            return {**base, "vivo": False, "error_tipo": type(e).__name__,
                    "error_msg": str(e)[:200]}
        latencia = int((time.monotonic() - inicio) * 1000)
        waf = _detectar_waf(r)
        out = {
            **base,
            "url_final": str(r.url),
            "http_status": r.status_code,
            "latencia_ms": latencia,
            "vivo": r.status_code < 400,
            "dentro_sla": latencia <= portal["sla_max_ms"],
        }
        if waf:
            # 403 de un WAF ≠ portal caído: el sitio responde, pero bloquea clientes no-navegador.
            out["bloqueado_por_waf"] = waf
            out["vivo"] = None
            out["nota"] = (f"{waf} bloqueó el cliente HTTP; usar portales_check_form_render "
                           "(navegador real) para confirmar disponibilidad.")
        return out

    def check_form_render(self, clave: str, selector: str) -> dict[str, Any]:
        """Verifica con Chromium real que `selector` renderice. Sin fallback a mock."""
        self._log("check_form_render", {"clave": clave, "selector": selector})
        portal = _portal(clave)

        if is_mock_mode([], default_when_no_creds=False):
            h = _hash_estable(clave + selector)
            return mark_simulated(
                {
                    "clave": clave,
                    "selector": selector,
                    "encontrado": (h % 10) > 1,
                    "criticidad": portal["criticidad"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                note="PLUGINS_MX_MOCK=1 — render simulado.",
            )

        from shared.playwright_real import playwright_session

        with playwright_session() as page:  # UpstreamError si Playwright no está o falla
            inicio = time.monotonic()
            resp = page.goto(portal["url"], wait_until="domcontentloaded")
            latencia = int((time.monotonic() - inicio) * 1000)
            # Akamai a veces sirve un challenge JS que recarga la página: esperar al selector.
            try:
                page.wait_for_selector(selector, timeout=15000)
            except Exception:  # timeout = el selector no renderizó; es el dato que medimos
                pass
            count = page.locator(selector).count()
            waf = None
            if resp is not None and resp.status == 403 and "Access Denied" in page.content():
                waf = "akamai"
            out = {
                "clave": clave,
                "url": portal["url"],
                "url_final": page.url,
                "selector": selector,
                "http_status": resp.status if resp else None,
                "latencia_ms": latencia,
                "encontrado": count > 0,
                "ocurrencias": count,
                "criticidad": portal["criticidad"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "simulated": False,
            }
            if waf:
                # Verificado 2026-10-14: Akamai bloquea Chromium headless pero no con ventana.
                out["bloqueado_por_waf"] = waf
                out["nota"] = "Akamai bloquea Chromium headless; reintentar con MP_PLAYWRIGHT_HEADLESS=0."
            return out

    def health_dashboard(self) -> dict[str, Any]:
        """Dashboard agregado: health % por categoría."""
        self._log("health_dashboard", {})
        por_categoria: dict[str, dict[str, int]] = {}
        for p in PORTALES_CATALOGO:
            cat = p["categoria"]
            if cat not in por_categoria:
                por_categoria[cat] = {"total": 0, "criticidad_alta": 0, "criticidad_media": 0}
            por_categoria[cat]["total"] += 1
            if p["criticidad"] == "alta":
                por_categoria[cat]["criticidad_alta"] += 1
            elif p["criticidad"] == "media":
                por_categoria[cat]["criticidad_media"] += 1
        return {
            "total_portales_monitoreados": len(PORTALES_CATALOGO),
            "criticidad_alta": sum(1 for p in PORTALES_CATALOGO if p["criticidad"] == "alta"),
            "criticidad_media": sum(1 for p in PORTALES_CATALOGO if p["criticidad"] == "media"),
            "por_categoria": por_categoria,
            "frecuencia_check_default": "cada 5 min para criticidad alta, cada 30 min para media",
            "alerta_canales_soportados": ["whatsapp", "email", "slack", "webhook_pagerduty"],
        }

    def configurar_alerta(
        self,
        clave: str,
        canal: str,
        destinatario: str,
        umbral_latencia_ms: int | None = None,
    ) -> dict[str, Any]:
        """Valida y devuelve la especificación de una alerta (no la persiste)."""
        self._log("configurar_alerta", {
            "clave": clave, "canal": canal,
            "destinatario_hash": Bitacora.hash_sensitive(destinatario),
        })
        canales_validos = {"whatsapp", "email", "slack", "webhook_pagerduty"}
        if canal not in canales_validos:
            raise ValidationError(f"canal inválido. Válidos: {sorted(canales_validos)}")
        portal = next((p for p in PORTALES_CATALOGO if p["clave"] == clave), None)
        if not portal:
            raise ValidationError(f"clave no reconocida: {clave!r}")
        umbral = umbral_latencia_ms or portal["sla_max_ms"]
        # Este MCP no tiene servicio de persistencia/envío de alertas: devolvemos la
        # especificación para que el orquestador la guarde. No se inventa un id.
        return {
            "clave_portal": clave,
            "canal": canal,
            "destinatario_hash": Bitacora.hash_sensitive(destinatario),
            "umbral_latencia_ms": umbral,
            "criticidad_portal": portal["criticidad"],
            "estado": "especificacion_no_persistida",
            "persistida": False,
            "nota": "Persistir y programar con tu scheduler; este MCP solo ejecuta checks.",
            "creada_at": datetime.now(timezone.utc).isoformat(),
        }
