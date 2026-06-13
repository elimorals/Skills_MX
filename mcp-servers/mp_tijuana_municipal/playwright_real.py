"""Playwright real Tijuana — predial via catálogo central + multas BC estatal.

REFACTORIZADO 2026-06-13: catálogo marca Tijuana como NO validado (URL antigua
recaudacion.tijuana.gob.mx tiene DNS muerto). Pendiente identificar URL real
desde menú dinámico www.tijuana.gob.mx.
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


# Multas Baja California estatal
CONFIG_MULTAS = PortalConfig(
    url="https://transitobc.gob.mx/multas",
    input_selectors=["input[name='placa']"],
    submit_selectors=["button[type='submit']"],
    result_selector="table",
    identificador_etiqueta="placa",
)


def predial_real(cuenta_predial: str) -> dict[str, Any]:
    """Consulta predial Tijuana via catálogo central. ⚠ Catálogo aún sin URL validada."""
    cfg = get_municipio_config("bc", "tijuana")
    if cfg is None or not cfg.portal_predial_url:
        raise UpstreamError(
            f"Tijuana no tiene URL de predial en catálogo. "
            f"Notas: {cfg.notas if cfg else 'sin entry'}. "
            f"Correr scripts/descubrir-portal-municipal.py o navegar manual.",
            {"municipio": "tijuana"},
        )
    portal_cfg = cfg.to_predial_config()
    if portal_cfg is None:
        raise UpstreamError("Tijuana: PortalConfig falló.", {})
    return consulta_portal(portal_cfg, cuenta_predial)


def multas_real(placa: str) -> dict[str, Any]:
    """Consulta multas BC (estatal)."""
    return consulta_portal(CONFIG_MULTAS, placa)
