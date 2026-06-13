"""Playwright real Querétaro — predial + multas.

Portales:
- Predial: https://recaudacion.queretaro.gob.mx/predial
- Multas: https://control-vehicular.queretaro.gob.mx/multas

⚠ Selectores experimentales.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.playwright_municipal_generic import (  # noqa: E402
    PortalConfig,
    consulta_portal,
)


CONFIG_PREDIAL = PortalConfig(
    url="https://recaudacion.queretaro.gob.mx/predial",
    input_selectors=["input[name='cuenta']", "input[type='text']"],
    submit_selectors=["button[type='submit']", "button:has-text('Consultar')"],
    result_selector="table, .resultado",
    identificador_etiqueta="cuenta_predial",
)

CONFIG_MULTAS = PortalConfig(
    url="https://control-vehicular.queretaro.gob.mx/multas",
    input_selectors=["input[name='placa']"],
    submit_selectors=["button[type='submit']"],
    result_selector="table",
    identificador_etiqueta="placa",
)


def predial_real(cuenta_predial: str) -> dict[str, Any]:
    return consulta_portal(CONFIG_PREDIAL, cuenta_predial)


def multas_real(placa: str) -> dict[str, Any]:
    return consulta_portal(CONFIG_MULTAS, placa)
