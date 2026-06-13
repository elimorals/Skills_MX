"""Playwright real Mérida — predial via catálogo central + multas Yucatán estatal.

REFACTORIZADO 2026-06-13: predial usa OVICA equivalente isla.merida.gob.mx
(validado MCP, Radware perfdrive pasa con sesión real).
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


# Multas Yucatán es ESTATAL
CONFIG_MULTAS = PortalConfig(
    url="https://transito.yucatan.gob.mx/multas",
    input_selectors=["input[name='placa']"],
    submit_selectors=["button[type='submit']"],
    result_selector="table",
    identificador_etiqueta="placa",
)


def predial_real(cuenta_predial: str) -> dict[str, Any]:
    """Consulta predial Mérida via catálogo central (busca por dirección física, no cuenta)."""
    cfg = get_municipio_config("yuc", "merida")
    if cfg is None or not cfg.portal_predial_url:
        raise UpstreamError(
            "Mérida no tiene URL de predial en catálogo.",
            {"municipio": "merida"},
        )
    portal_cfg = cfg.to_predial_config()
    if portal_cfg is None:
        raise UpstreamError("Mérida: PortalConfig falló.", {})
    return consulta_portal(portal_cfg, cuenta_predial)


def multas_real(placa: str) -> dict[str, Any]:
    """Consulta multas Yucatán (estatal)."""
    return consulta_portal(CONFIG_MULTAS, placa)
