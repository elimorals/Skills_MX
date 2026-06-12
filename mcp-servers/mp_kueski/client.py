"""Cliente mp_kueski — mock-first."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "kueski"
CRED_VARS = ["KUESKI_API_KEY"]


class KueskiClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        if not CRED_VARS:
            return True
        return is_mock_mode(CRED_VARS)

    def listar_pagos(self, **kwargs) -> dict:
        self.bitacora.log("listar_pagos", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "listar_pagos",
                "data": {"placeholder": True, "ns": "kueski", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("listar_pagos path real no implementado — ver README", {"hint": "implementar HTTP/API real"})

    def consultar_pago(self, **kwargs) -> dict:
        self.bitacora.log("consultar_pago", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "consultar_pago",
                "data": {"placeholder": True, "ns": "kueski", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("consultar_pago path real no implementado — ver README", {"hint": "implementar HTTP/API real"})

    def cancelar_pago(self, **kwargs) -> dict:
        self.bitacora.log("cancelar_pago", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "cancelar_pago",
                "data": {"placeholder": True, "ns": "kueski", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("cancelar_pago path real no implementado — ver README", {"hint": "implementar HTTP/API real"})
