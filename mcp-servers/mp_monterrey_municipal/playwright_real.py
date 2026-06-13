"""Playwright real Monterrey — predial AMM + multas NL.

REFACTORIZADO 2026-06-13: ya NO mantiene URLs hardcoded. Consulta
`shared.catalogo_municipios_mx` para predial y configura multas NL aparte
(es estatal, no municipal).

⚠ Catálogo actual marca Monterrey como NO validado: la URL antigua
/predial-en-linea regresa 404. Pendiente identificar URL real desde menú.
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
from shared.playwright_municipal_generic import (  # noqa: E402
    PortalConfig,
    consulta_portal,
)


# Multas Nuevo León es ESTATAL — no municipal. Se mantiene aparte del catálogo central.
CONFIG_MULTAS_NL = PortalConfig(
    url="https://www.nl.gob.mx/tramites-y-servicios/multas",
    input_selectors=["input[name='placa']", "input#placa"],
    submit_selectors=["button:has-text('Consultar')"],
    result_selector="table",
    identificador_etiqueta="placa",
)


def predial_real(cuenta_predial: str) -> dict[str, Any]:
    """Consulta predial Monterrey usando el catálogo central."""
    cfg = get_municipio_config("nl", "monterrey")
    if cfg is None or not cfg.portal_predial_url:
        raise UpstreamError(
            f"Monterrey no tiene URL de predial verificada en catálogo. "
            f"Notas: {cfg.notas if cfg else 'sin entry'}. "
            f"Correr scripts/descubrir-portal-municipal.py.",
            {"municipio": "monterrey"},
        )
    portal_cfg = cfg.to_predial_config()
    if portal_cfg is None:
        raise UpstreamError("Monterrey: catálogo tiene URL pero falló PortalConfig.", {})
    return consulta_portal(portal_cfg, cuenta_predial)


def multas_nl_real(placa: str) -> dict[str, Any]:
    """Consulta multas vehiculares NL (estatal, no municipal)."""
    return consulta_portal(CONFIG_MULTAS_NL, placa)
