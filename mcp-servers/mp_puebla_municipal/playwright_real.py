"""Playwright real Puebla — predial via catálogo central + multas Puebla estatal.

REFACTORIZADO 2026-06-13: predial apunta a srvappayt.pueblacapital.gob.mx:7016
(validado MCP — form con CAPTCHA `answer` requiere humano-en-loop).
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


CONFIG_MULTAS = PortalConfig(
    url="https://hacienda.puebla.gob.mx/multas",
    input_selectors=["input[name='placa']"],
    submit_selectors=["button[type='submit']"],
    result_selector="table",
    identificador_etiqueta="placa",
)


def predial_real(cuenta_predial: str) -> dict[str, Any]:
    """Consulta predial Puebla via catálogo central. ⚠ Tiene CAPTCHA — humano-en-loop."""
    cfg = get_municipio_config("pue", "puebla")
    if cfg is None or not cfg.portal_predial_url:
        raise UpstreamError(
            "Puebla no tiene URL de predial en catálogo.",
            {"municipio": "puebla"},
        )
    portal_cfg = cfg.to_predial_config()
    if portal_cfg is None:
        raise UpstreamError("Puebla: PortalConfig falló.", {})
    # ⚠ Puebla requiere CAPTCHA en campo 'answer' — el flujo completo no es automatizable
    # sin humano-en-loop. consulta_portal() llenará lo demás pero no podrá pasar el CAPTCHA.
    return consulta_portal(portal_cfg, cuenta_predial)


def multas_real(placa: str) -> dict[str, Any]:
    """Consulta multas Puebla (estatal)."""
    return consulta_portal(CONFIG_MULTAS, placa)
