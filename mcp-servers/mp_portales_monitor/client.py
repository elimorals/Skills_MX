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
from shared.mock import mark_simulated  # noqa: E402


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
        """Check HTTP HEAD/GET simple. Sin Playwright."""
        self._log("check_http", {"clave": clave})
        portal = next((p for p in PORTALES_CATALOGO if p["clave"] == clave), None)
        if not portal:
            raise ValidationError(f"clave no reconocida: {clave!r}")

        from shared.playwright_real import is_public_real_enabled
        if not is_public_real_enabled():
            # Mock determinístico por clave
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
                note="Mock — para check real setear MP_PLAYWRIGHT_PUBLIC=1 (usa httpx).",
            )

        # Path real con httpx (sin Playwright porque es HEAD)
        try:
            import httpx
            inicio = time.time()
            r = httpx.head(portal["url"], timeout=portal["sla_max_ms"] / 1000, follow_redirects=True)
            latencia = int((time.time() - inicio) * 1000)
            return {
                "clave": clave,
                "url": portal["url"],
                "http_status": r.status_code,
                "latencia_ms": latencia,
                "vivo": r.status_code < 400,
                "dentro_sla": latencia <= portal["sla_max_ms"],
                "criticidad": portal["criticidad"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "simulated": False,
            }
        except Exception as e:
            return {
                "clave": clave,
                "url": portal["url"],
                "vivo": False,
                "error_tipo": type(e).__name__,
                "error_msg": str(e)[:200],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "simulated": False,
            }

    def check_form_render(self, clave: str, selector: str) -> dict[str, Any]:
        """Verifica que un selector clave renderice (Playwright opt-in)."""
        self._log("check_form_render", {"clave": clave, "selector": selector})
        portal = next((p for p in PORTALES_CATALOGO if p["clave"] == clave), None)
        if not portal:
            raise ValidationError(f"clave no reconocida: {clave!r}")

        from shared.playwright_real import is_public_real_enabled
        if not is_public_real_enabled():
            h = _hash_estable(clave + selector)
            encontrado = (h % 10) > 1
            return mark_simulated(
                {
                    "clave": clave,
                    "selector": selector,
                    "encontrado": encontrado,
                    "criticidad": portal["criticidad"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                note="Mock — para path real setear MP_PLAYWRIGHT_PUBLIC=1",
            )

        from shared.playwright_real import playwright_session, with_real_or_fallback

        def _real() -> dict[str, Any]:
            with playwright_session() as page:
                page.goto(portal["url"], wait_until="domcontentloaded")
                count = page.locator(selector).count()
                return {
                    "clave": clave,
                    "selector": selector,
                    "encontrado": count > 0,
                    "ocurrencias": count,
                    "criticidad": portal["criticidad"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "simulated": False,
                }

        def _fb() -> dict[str, Any]:
            return {
                "clave": clave,
                "selector": selector,
                "encontrado": None,
                "error": "Playwright falló, devolviendo fallback",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        return with_real_or_fallback(_real, _fb, portal="portales_monitor")

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
        """Registra una alerta (mock — un servicio dedicado lo persiste en producción)."""
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
        return mark_simulated(
            {
                "alerta_id": f"alert_{_hash_estable(clave + canal + destinatario) % 1000000:06d}",
                "clave_portal": clave,
                "canal": canal,
                "destinatario_hash": Bitacora.hash_sensitive(destinatario),
                "umbral_latencia_ms": umbral,
                "criticidad_portal": portal["criticidad"],
                "estado": "activa",
                "creada_at": datetime.now(timezone.utc).isoformat(),
            },
            note="Mock — en producción persiste en sqlite del servicio.",
        )
