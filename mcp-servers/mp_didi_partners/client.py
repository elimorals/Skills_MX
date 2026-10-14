"""Cliente mp_didi_partners — mock-first."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ConfigError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

SIN_API_PUBLICA = 'DiDi no publica API para conductores.'
ALTERNATIVA = 'Descarga el resumen de ganancias desde la app DiDi Conductor o tus CFDI de retenciones en el SAT.'
NAMESPACE = "didi_partners"
CRED_VARS = ["DIDI_DRIVER_TOKEN"]


class DidiPartnersClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        if not CRED_VARS:
            return True
        return is_mock_mode(CRED_VARS)

    def listar_viajes(self, **kwargs) -> dict:
        self.bitacora.log("listar_viajes", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "listar_viajes",
                "data": {"placeholder": True, "ns": "didi_partners", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise ConfigError(SIN_API_PUBLICA, {"motivo": "sin_api_publica", "alternativa": ALTERNATIVA})

    def consultar_viaje(self, **kwargs) -> dict:
        self.bitacora.log("consultar_viaje", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "consultar_viaje",
                "data": {"placeholder": True, "ns": "didi_partners", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise ConfigError(SIN_API_PUBLICA, {"motivo": "sin_api_publica", "alternativa": ALTERNATIVA})

    def comisiones_mes(self, **kwargs) -> dict:
        self.bitacora.log("comisiones_mes", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "comisiones_mes",
                "data": {"placeholder": True, "ns": "didi_partners", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise ConfigError(SIN_API_PUBLICA, {"motivo": "sin_api_publica", "alternativa": ALTERNATIVA})
