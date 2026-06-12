"""Cliente mp_puebla_municipal — mock-first."""

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

NAMESPACE = "puebla_mun"
CRED_VARS = []


class PueblaMunClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        if not CRED_VARS:
            return True
        return is_mock_mode(CRED_VARS)

    def consultar_multas(self, **kwargs) -> dict:
        self.bitacora.log("consultar_multas", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "consultar_multas",
                "data": {"placeholder": True, "ns": "puebla_mun", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("consultar_multas path real no implementado — ver README", {"hint": "implementar HTTP/API real"})

    def consultar_predial(self, **kwargs) -> dict:
        self.bitacora.log("consultar_predial", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "consultar_predial",
                "data": {"placeholder": True, "ns": "puebla_mun", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("consultar_predial path real no implementado — ver README", {"hint": "implementar HTTP/API real"})
