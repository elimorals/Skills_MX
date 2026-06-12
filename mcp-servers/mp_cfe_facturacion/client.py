"""Cliente mp_cfe_facturacion — mock-first."""

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

NAMESPACE = "cfe_fact"
CRED_VARS = ["CFE_RPU", "CFE_PASSWORD"]


class CfeFactClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        if not CRED_VARS:
            return True
        return is_mock_mode(CRED_VARS)

    def descargar_factura_mes(self, **kwargs) -> dict:
        self.bitacora.log("descargar_factura_mes", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "descargar_factura_mes",
                "data": {"placeholder": True, "ns": "cfe_fact", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("descargar_factura_mes path real no implementado — ver README", {"hint": "implementar HTTP/API real"})

    def consumo_historico(self, **kwargs) -> dict:
        self.bitacora.log("consumo_historico", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "consumo_historico",
                "data": {"placeholder": True, "ns": "cfe_fact", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("consumo_historico path real no implementado — ver README", {"hint": "implementar HTTP/API real"})
