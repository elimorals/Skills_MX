"""Playwright real Querétaro — predial via catálogo central + multas estatales.

REFACTORIZADO 2026-06-13: predial consulta el catálogo central que en su FASE 13b+18
descubrió URL real `webservices.municipiodequeretaro.gob.mx/consultaLC/v2/`.
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


# Multas Querétaro: estatal (control-vehicular.queretaro.gob.mx)
CONFIG_MULTAS = PortalConfig(
    url="https://control-vehicular.queretaro.gob.mx/multas",
    input_selectors=["input[name='placa']"],
    submit_selectors=["button[type='submit']"],
    result_selector="table",
    identificador_etiqueta="placa",
)


def predial_real(cuenta_predial: str) -> dict[str, Any]:
    """Consulta predial Querétaro via catálogo central."""
    cfg = get_municipio_config("qro", "queretaro")
    if cfg is None or not cfg.portal_predial_url:
        raise UpstreamError(
            f"Querétaro no tiene URL de predial verificada en catálogo. "
            f"Notas: {cfg.notas if cfg else 'sin entry'}. "
            f"Correr scripts/descubrir-portal-municipal.py.",
            {"municipio": "queretaro"},
        )
    portal_cfg = cfg.to_predial_config()
    if portal_cfg is None:
        raise UpstreamError("Querétaro: PortalConfig falló.", {})
    return consulta_portal(portal_cfg, cuenta_predial)


def multas_real(placa: str) -> dict[str, Any]:
    """Consulta multas Querétaro (estatal)."""
    return consulta_portal(CONFIG_MULTAS, placa)
