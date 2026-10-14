"""Cliente mp_llave_mx_tracker — adopción Llave MX por dependencia.

Producto público para ATDT, IMCO y prensa: ¿qué dependencias federales y
estatales ya integraron Llave MX como SSO ciudadano? El portal no publica esta
lista — la construimos por scraping de portales gob.mx y detección heurística
del flow OAuth `llave.gob.mx/oauthV2.xhtml?client_id=...`.

Path real: `verificar_en_vivo` hace GET a la portada (httpx) y busca redirección OAuth,
enlace a llave.gob.mx o mención de "Llave MX". Snapshot del 2026-10-14 en
DETECCION_2026_10_14. Mock solo con PLUGINS_MX_MOCK=1; sin fallback a mock.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.errors import handle_httpx_error  # noqa: E402
from shared.http_helpers import build_ssl_verify  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

import re  # noqa: E402

import httpx  # noqa: E402


NAMESPACE = "llave_mx_tracker"
URL_LLAVE_OAUTH = "https://www.llave.gob.mx/oauthV2.xhtml"
URL_LLAVE_HOME = "https://www.llave.gob.mx/"

# Catálogo curado de dependencias federales + estatales monitoreadas.
# Cada entrada define `portal_url` candidato + status conocido al 2026-06-15.
# Status: "integrado", "anunciado_no_visible", "no_integrado", "desconocido".
DEPENDENCIAS_MONITOREADAS: list[dict[str, Any]] = [
    # FEDERALES — SHCP
    {"clave": "sat", "nombre": "Servicio de Administración Tributaria",
     "nivel": "federal", "sector": "fiscal",
     "portal_url": "https://www.sat.gob.mx/",
     "status_2026_06": "no_integrado",
     "nota": "SAT usa RFC+CIEC o e.firma propios — no expone Llave MX en login público."},
    {"clave": "imss", "nombre": "Instituto Mexicano del Seguro Social",
     "nivel": "federal", "sector": "salud_laboral",
     "portal_url": "https://www.imss.gob.mx/",
     "status_2026_06": "no_integrado",
     "nota": "Login ciudadano usa NSS/CURP+contraseña propia."},
    {"clave": "infonavit", "nombre": "INFONAVIT — Mi Cuenta",
     "nivel": "federal", "sector": "vivienda",
     "portal_url": "https://micuenta.infonavit.org.mx/",
     "status_2026_06": "no_integrado",
     "nota": "Login propio."},
    {"clave": "issste", "nombre": "ISSSTE",
     "nivel": "federal", "sector": "salud",
     "portal_url": "https://www.issste.gob.mx/",
     "status_2026_06": "desconocido",
     "nota": "Sin verificación reciente."},
    {"clave": "sep", "nombre": "Secretaría de Educación Pública",
     "nivel": "federal", "sector": "educacion",
     "portal_url": "https://www.gob.mx/sep",
     "status_2026_06": "desconocido"},
    {"clave": "sre_pasaporte", "nombre": "SRE — MiConsulado / Pasaporte",
     "nivel": "federal", "sector": "consular",
     "portal_url": "https://citas.sre.gob.mx/",
     "status_2026_06": "no_integrado",
     "nota": "Mexitel y MiConsulado con login propios."},
    {"clave": "ine", "nombre": "INE — Servicios Ciudadanos",
     "nivel": "federal_autonomo", "sector": "identidad",
     "portal_url": "https://portal.ine.mx/",
     "status_2026_06": "no_integrado",
     "nota": "INE no depende del ejecutivo — sin integración Llave MX."},
    {"clave": "renapo", "nombre": "RENAPO — CURP",
     "nivel": "federal", "sector": "identidad",
     "portal_url": "https://www.gob.mx/curp/",
     "status_2026_06": "anunciado_no_visible",
     "nota": "CURP biométrico anunció vinculación con Llave MX pero formulario público no la pide."},
    {"clave": "profeco", "nombre": "PROFECO — Concilianet",
     "nivel": "federal", "sector": "consumidor",
     "portal_url": "https://concilianet.profeco.gob.mx/",
     "status_2026_06": "no_integrado"},
    {"clave": "cofepris", "nombre": "COFEPRIS — Digipro",
     "nivel": "federal", "sector": "salud",
     "portal_url": "https://www.gob.mx/cofepris",
     "status_2026_06": "no_integrado",
     "nota": "Digipro con usuario+contraseña."},
    {"clave": "cre", "nombre": "Comisión Reguladora de Energía",
     "nivel": "federal", "sector": "energia",
     "portal_url": "https://www.gob.mx/cre",
     "status_2026_06": "desconocido"},
    {"clave": "conagua", "nombre": "CONAGUA — REPDA",
     "nivel": "federal", "sector": "agua",
     "portal_url": "https://www.gob.mx/conagua",
     "status_2026_06": "desconocido"},
    {"clave": "atdt", "nombre": "Agencia de Transformación Digital",
     "nivel": "federal", "sector": "transformacion_digital",
     "portal_url": "https://www.gob.mx/atdt",
     "status_2026_06": "integrado",
     "nota": "ATDT opera Llave MX — integración por definición."},
    {"clave": "gobmx", "nombre": "Portal gob.mx — Mi Cuenta",
     "nivel": "federal", "sector": "transversal",
     "portal_url": "https://www.gob.mx/",
     "status_2026_06": "integrado",
     "nota": "Portal único reconoce Llave MX para Mi Cuenta ciudadana."},
    {"clave": "bienestar", "nombre": "Secretaría de Bienestar — Programas",
     "nivel": "federal", "sector": "social",
     "portal_url": "https://www.gob.mx/bienestar",
     "status_2026_06": "desconocido"},
    # ESTATALES
    {"clave": "bc", "nombre": "Agencia Digital Baja California",
     "nivel": "estatal", "sector": "transversal",
     "portal_url": "https://www.bajacalifornia.gob.mx/",
     "status_2026_06": "no_integrado",
     "nota": ("BC tiene su propio SSO estatal (URBEM). 2026-10-14: la portada enlaza a "
              "https://www.llave.gob.mx (logo Llave MX); no se vio flujo OAuth.")},
    {"clave": "cdmx", "nombre": "Llave CDMX",
     "nivel": "estatal", "sector": "transversal",
     "portal_url": "https://llave.cdmx.gob.mx/",
     "status_2026_06": "no_integrado",
     "nota": "CDMX opera Llave CDMX (separada de Llave MX)."},
    {"clave": "edomex", "nombre": "Edoméx — Servicios",
     "nivel": "estatal", "sector": "transversal",
     "portal_url": "https://edomex.gob.mx/",
     "status_2026_06": "desconocido"},
    {"clave": "jal", "nombre": "Jalisco — Trámites en línea",
     "nivel": "estatal", "sector": "transversal",
     "portal_url": "https://www.jalisco.gob.mx/",
     "status_2026_06": "desconocido"},
    {"clave": "nl", "nombre": "Nuevo León — Portal Ciudadano",
     "nivel": "estatal", "sector": "transversal",
     "portal_url": "https://www.nl.gob.mx/",
     "status_2026_06": "desconocido"},
]

STATUS_VALIDOS = {"integrado", "anunciado_no_visible", "no_integrado", "desconocido"}

# Resultado de la detección en vivo (no prueba ausencia: solo mira la página de entrada).
DETECCION_VALIDOS = {"oauth_llave_detectado", "enlace_llave_gob_mx", "mencion_llave_mx",
                     "no_detectado_en_portada", "inaccesible"}

# Snapshot de verificar_en_vivo sobre las 20 portadas, 2026-10-14 (GET httpx, 5 s entre hosts).
DETECCION_2026_10_14: dict[str, str] = {
    "sat": "no_detectado_en_portada", "imss": "inaccesible", "infonavit": "inaccesible",
    "issste": "no_detectado_en_portada", "sep": "no_detectado_en_portada",
    "sre_pasaporte": "inaccesible", "ine": "no_detectado_en_portada",
    "renapo": "no_detectado_en_portada", "profeco": "no_detectado_en_portada",
    "cofepris": "no_detectado_en_portada", "cre": "no_detectado_en_portada",
    "conagua": "no_detectado_en_portada", "atdt": "no_detectado_en_portada",
    "gobmx": "no_detectado_en_portada", "bienestar": "no_detectado_en_portada",
    "bc": "enlace_llave_gob_mx", "cdmx": "no_detectado_en_portada",
    "edomex": "no_detectado_en_portada", "jal": "no_detectado_en_portada",
    "nl": "no_detectado_en_portada",
}

BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")


def detectar_llave(html: str, url_final: str) -> dict[str, Any]:
    """Heurística sobre la página de entrada: OAuth, enlace o mención de Llave MX."""
    low = (html or "").lower()
    url = (url_final or "").lower()
    oauth = "llave.gob.mx/oauth" in url or "llave.gob.mx/oauth" in low
    enlace = bool(re.search(r"""href=["'][^"']*llave\.gob\.mx""", low))
    mencion = bool(re.search(r"llave\s*mx", low))
    if oauth:
        deteccion = "oauth_llave_detectado"
    elif enlace:
        deteccion = "enlace_llave_gob_mx"
    elif mencion:
        deteccion = "mencion_llave_mx"
    else:
        deteccion = "no_detectado_en_portada"
    return {"deteccion": deteccion, "oauth": oauth, "enlace_llave_gob_mx": enlace, "mencion_texto": mencion}


class LlaveMxTrackerClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    def listar_dependencias(self, nivel: str | None = None) -> dict[str, Any]:
        """Lista todas las dependencias monitoreadas, filtrable por nivel."""
        self._log("listar_dependencias", {"nivel": nivel})
        items = DEPENDENCIAS_MONITOREADAS
        if nivel:
            nivel_norm = nivel.lower().strip()
            items = [d for d in items if d["nivel"] == nivel_norm]
        return {
            "total": len(items),
            "fuente_oficial_llave": URL_LLAVE_HOME,
            "dependencias": items,
            "fecha_corte": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }

    def estatus_dependencia(self, clave: str) -> dict[str, Any]:
        """Estatus actual de una dependencia específica."""
        self._log("estatus_dependencia", {"clave": clave})
        clave_norm = (clave or "").lower().strip()
        for d in DEPENDENCIAS_MONITOREADAS:
            if d["clave"] == clave_norm:
                return {
                    **d,
                    "status_curado_verificado": False,
                    "deteccion_2026_10_14": DETECCION_2026_10_14.get(d["clave"]),
                    "nota_status": ("status_2026_06 es curado a mano y no verificado; la detección "
                                    "es el snapshot en vivo de la portada. Usa verificar_en_vivo para hoy."),
                }
        raise ValidationError(
            f"clave no reconocida: {clave!r}. Usar `listar_dependencias` para ver opciones."
        )

    def estadisticas_nacionales(self) -> dict[str, Any]:
        """Métricas agregadas — qué % está integrado, por nivel y sector."""
        self._log("estadisticas_nacionales", {})
        total = len(DEPENDENCIAS_MONITOREADAS)
        counts_status: dict[str, int] = {s: 0 for s in STATUS_VALIDOS}
        counts_nivel: dict[str, dict[str, int]] = {}
        for d in DEPENDENCIAS_MONITOREADAS:
            counts_status[d["status_2026_06"]] = counts_status.get(d["status_2026_06"], 0) + 1
            nivel = d["nivel"]
            counts_nivel.setdefault(nivel, {s: 0 for s in STATUS_VALIDOS})
            counts_nivel[nivel][d["status_2026_06"]] += 1
        por_deteccion: dict[str, int] = {k: 0 for k in sorted(DETECCION_VALIDOS)}
        for d in DEPENDENCIAS_MONITOREADAS:
            por_deteccion[DETECCION_2026_10_14[d["clave"]]] += 1
        return {
            "total_dependencias_monitoreadas": total,
            "por_status_curado": counts_status,
            "por_nivel_curado": counts_nivel,
            "por_deteccion_vivo_2026_10_14": por_deteccion,
            "nota": ("El status curado no está verificado. La detección en vivo solo revisa la portada: "
                     "'no_detectado_en_portada' no prueba que no exista login con Llave MX."),
            "fecha_snapshot": "2026-10-14",
        }

    def verificar_en_vivo(self, clave: str) -> dict[str, Any]:
        """GET real a la página de entrada del portal y detección de Llave MX. Sin fallback."""
        self._log("verificar_en_vivo", {"clave": clave})
        clave_norm = (clave or "").lower().strip()
        target = next((d for d in DEPENDENCIAS_MONITOREADAS if d["clave"] == clave_norm), None)
        if not target:
            raise ValidationError(f"clave no reconocida: {clave!r}")
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({**target, "deteccion": "no_detectado_en_portada"})

        base = {**target, "verificacion_metodo": "httpx_get_portada",
                "fecha_verificacion": datetime.now(timezone.utc).isoformat(), "simulated": False}
        try:
            with httpx.Client(verify=build_ssl_verify(), timeout=30.0, follow_redirects=True,
                              headers={"User-Agent": BROWSER_UA, "Accept-Language": "es-MX,es;q=0.9"}) as c:
                r = c.get(target["portal_url"])
        except httpx.TransportError as e:
            # Portal caído o TLS roto: es el hallazgo, no un error del MCP.
            return {**base, "deteccion": "inaccesible", "error": f"{type(e).__name__}: {str(e)[:160]}"}
        except httpx.HTTPError as e:
            raise handle_httpx_error(e) from e
        if r.status_code >= 400 or "perfdrive.com" in str(r.url):
            waf = "radware" if "perfdrive.com" in str(r.url) else None
            return {**base, "deteccion": "inaccesible", "http_status": r.status_code,
                    "bloqueado_por_waf": waf}
        return {**base, "http_status": r.status_code, "url_final": str(r.url),
                **detectar_llave(r.text, str(r.url)),
                "nota": "Solo se revisa la portada; un login interno con Llave MX no se detecta así."}
