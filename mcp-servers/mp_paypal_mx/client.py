"""Cliente mp_paypal_mx — mock-first."""

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

NAMESPACE = "paypal_mx"
CRED_VARS = ["PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET"]


class PaypalMxClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        if not CRED_VARS:
            return True
        return is_mock_mode(CRED_VARS)

    def listar_transacciones(self, **kwargs) -> dict:
        self.bitacora.log("listar_transacciones", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "listar_transacciones",
                "data": {"placeholder": True, "ns": "paypal_mx", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("listar_transacciones path real no implementado — ver README", {"hint": "implementar HTTP/API real"})

    def consultar_transaccion(self, **kwargs) -> dict:
        self.bitacora.log("consultar_transaccion", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "consultar_transaccion",
                "data": {"placeholder": True, "ns": "paypal_mx", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("consultar_transaccion path real no implementado — ver README", {"hint": "implementar HTTP/API real"})

    def balance(self, **kwargs) -> dict:
        self.bitacora.log("balance", success=True, params_summary={k: str(v)[:20] for k, v in kwargs.items()})
        if self._is_mock():
            return mark_simulated({
                "operation": "balance",
                "data": {"placeholder": True, "ns": "paypal_mx", "kwargs_received": list(kwargs.keys())},
                "real_implementation_pending": True,
            })
        raise McpError("balance path real no implementado — ver README", {"hint": "implementar HTTP/API real"})
