"""Implementación Playwright REAL para portales CDMX — paths públicos.

REFACTORIZADO 2026-06-13: predial ya NO usa URL hardcoded. Consulta el catálogo
central que apunta a OVICA (validado con Playwright MCP).

Endpoints implementados (no requieren login):
- predial_real()    : Oficina Virtual del Catastro (OVICA) — Angular Material
- tenencia_real()   : tenencia/refrendo por placa — consulta pública

Endpoints NO implementados (requieren CAPTCHA o sesión):
- multas_real       : Semovi pide reCAPTCHA enterprise — bloqueado
- pagar_real        : requiere flujo de pago (fuera de scope MCP read-only)

URLs vigentes:
- Predial: https://ovica.finanzas.cdmx.gob.mx/cuenta-predial-liquidacion (validado 2026-06-13)
- Tenencia: https://servidor.finanzas.cdmx.gob.mx/sip-tenencia/ (legacy, validar)

Las consultas son públicas — basta con la cuenta predial o la placa.
NO se almacena información sensible más allá del hash en bitácora.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.catalogo_municipios_mx import get_municipio_config  # noqa: E402
from shared.errors import UpstreamError  # noqa: E402
from shared.playwright_municipal_generic import consulta_portal  # noqa: E402
from shared.playwright_real import (  # noqa: E402
    playwright_session,
    safe_text,
    parse_precio_mxn,
)


# Tenencia CDMX se mantiene aparte porque NO es portal municipal,
# es servicio estatal de finanzas vehicular.
URL_TENENCIA = "https://servidor.finanzas.cdmx.gob.mx/sip-tenencia/"


def predial_real(cuenta_predial: str) -> dict[str, Any]:
    """Consulta predial CDMX usando el catálogo central (OVICA validado).

    El catálogo apunta a https://ovica.finanzas.cdmx.gob.mx/cuenta-predial-liquidacion
    con selectores Angular Material validados con Playwright MCP el 2026-06-13.

    Flujo delegado a `consulta_portal()` del helper municipal genérico.
    """
    cfg_mun = get_municipio_config("cdmx", "ciudad_de_mexico")
    if cfg_mun is None or not cfg_mun.portal_predial_url:
        raise UpstreamError(
            "Catálogo central no tiene URL de predial CDMX. "
            "Correr scripts/descubrir-portal-municipal.py o revisar catalogo_municipios_mx.py.",
            {},
        )

    config = cfg_mun.to_predial_config()
    if config is None:
        raise UpstreamError(
            "CDMX en catálogo pero falló construcción de PortalConfig.",
            {"notas": cfg_mun.notas},
        )

    return consulta_portal(config, cuenta_predial)


def tenencia_real(placa: str) -> dict[str, Any]:
    """Consulta tenencia/refrendo vehicular CDMX por placa.

    Para CDMX la tenencia fue eliminada como impuesto local desde 2011 para
    vehículos de hasta cierto valor, pero refrendo y otros siguen aplicables.
    Esta función consulta el portal vehicular para esos cargos.
    """
    with playwright_session() as page:
        try:
            page.goto(URL_TENENCIA, wait_until="domcontentloaded")
        except Exception as e:
            raise UpstreamError(
                f"No se pudo cargar portal tenencia CDMX: {e}",
                {"url": URL_TENENCIA},
            )

        try:
            page.locator(
                "input[name='placa'], input#placa, input[name='placaVehicular'], input[type='text']"
            ).first.fill(placa)
        except Exception:
            raise UpstreamError(
                "No se encontró el campo placa en formulario tenencia.",
                {},
            )

        try:
            page.locator(
                "button[type='submit'], button:has-text('Consultar')"
            ).first.click()
        except Exception:
            page.keyboard.press("Enter")

        try:
            page.wait_for_selector("table, .resultado, [class*='result']", timeout=20000)
        except Exception as e:
            raise UpstreamError(f"Timeout esperando resultado tenencia: {e}", {})

        cargos = []
        for row in page.locator("table tr").all()[:30]:
            celdas = row.locator("td").all()
            if len(celdas) < 2:
                continue
            concepto = safe_text(celdas[0])
            monto = parse_precio_mxn(safe_text(celdas[-1]))
            if concepto and monto is not None:
                cargos.append({
                    "concepto": concepto,
                    "monto_mxn": monto,
                })

        total = sum(c["monto_mxn"] for c in cargos)

        return {
            "placa_hash": placa[:3] + "***",  # No exponer placa completa en respuesta
            "estatus": "al_corriente" if total == 0 else "con_adeudo",
            "adeudo_total_mxn": total,
            "cargos": cargos,
            "url_consultada": URL_TENENCIA,
        }
