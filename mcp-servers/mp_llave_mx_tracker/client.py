"""Cliente mp_llave_mx_tracker — adopción Llave MX por dependencia.

Producto público para ATDT, IMCO y prensa: ¿qué dependencias federales y
estatales ya integraron Llave MX como SSO ciudadano? El portal no publica esta
lista — la construimos por scraping de portales gob.mx y detección heurística
del flow OAuth `llave.gob.mx/oauthV2.xhtml?client_id=...`.

Path real: visita cada portal candidato con Playwright y busca redirección o
botón "Iniciar sesión con Llave MX". Mock por default.
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
from shared.mock import mark_simulated  # noqa: E402


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
     "nota": "BC tiene su propio SSO estatal (URBEM)."},
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
                return mark_simulated(
                    {**d, "fecha_corte": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
                    note="Status curado al 2026-06-15. Path real verifica login Llave MX en vivo.",
                )
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
        pct_integrado = round(counts_status["integrado"] / total * 100, 1)
        return {
            "total_dependencias_monitoreadas": total,
            "por_status": counts_status,
            "por_nivel": counts_nivel,
            "porcentaje_integrado": pct_integrado,
            "porcentaje_no_integrado": round(counts_status["no_integrado"] / total * 100, 1),
            "porcentaje_desconocido": round(counts_status["desconocido"] / total * 100, 1),
            "meta_lnetb_2030_pct": 80.0,
            "brecha_vs_meta_pct": round(80.0 - pct_integrado, 1),
            "fuente_legal": "Lineamientos Llave MX SIDOF 2025 + LNETB DOF 16-jul-2025",
            "fecha_corte": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }

    def verificar_en_vivo(self, clave: str) -> dict[str, Any]:
        """Path real Playwright — visita el portal candidato y detecta Llave MX.

        Sin Playwright instalado retorna mock con shape de respuesta real.
        Detección heurística:
            1. Visita portal_url
            2. Busca texto "Llave MX" o "Iniciar sesión con Llave"
            3. Busca redirección a llave.gob.mx/oauthV2.xhtml
            4. Marca integrado / no_integrado según hallazgo
        """
        self._log("verificar_en_vivo", {"clave": clave})
        clave_norm = (clave or "").lower().strip()
        target = next((d for d in DEPENDENCIAS_MONITOREADAS if d["clave"] == clave_norm), None)
        if not target:
            raise ValidationError(f"clave no reconocida: {clave!r}")

        from shared.playwright_real import is_public_real_enabled
        if not is_public_real_enabled():
            return mark_simulated(
                {
                    **target,
                    "verificacion_metodo": "mock",
                    "detecciones": {
                        "texto_llave_encontrado": None,
                        "redireccion_oauth_detectada": None,
                    },
                    "fecha_verificacion": datetime.now(timezone.utc).isoformat(),
                },
                note="Mock — para path real setear MP_PLAYWRIGHT_PUBLIC=1",
            )

        # Path real: importación lazy
        from shared.playwright_real import playwright_session, with_real_or_fallback

        def _real() -> dict[str, Any]:
            with playwright_session() as page:
                page.goto(target["portal_url"], wait_until="domcontentloaded")
                body = (page.content() or "").lower()
                texto_llave = "llave mx" in body or "iniciar sesión con llave" in body
                # Detección de redirect oauth: inspeccionar URL final o links
                current_url = page.url
                oauth_detect = "llave.gob.mx/oauth" in current_url
                if not oauth_detect:
                    # Buscar enlaces a llave.gob.mx/oauth
                    links = page.eval_on_selector_all(
                        "a[href*='llave.gob.mx']",
                        "els => els.map(e => e.getAttribute('href'))",
                    )
                    oauth_detect = any("oauth" in (l or "").lower() for l in links or [])
                inferido = "integrado" if (texto_llave or oauth_detect) else "no_integrado"
                return {
                    **target,
                    "status_inferido_vivo": inferido,
                    "verificacion_metodo": "playwright_real",
                    "detecciones": {
                        "texto_llave_encontrado": texto_llave,
                        "redireccion_oauth_detectada": oauth_detect,
                        "url_final": current_url,
                    },
                    "fecha_verificacion": datetime.now(timezone.utc).isoformat(),
                    "simulated": False,
                }

        def _fb() -> dict[str, Any]:
            return {
                **target,
                "verificacion_metodo": "fallback_mock_tras_error",
                "fecha_verificacion": datetime.now(timezone.utc).isoformat(),
            }

        return with_real_or_fallback(_real, _fb, portal="llave_mx_tracker")
