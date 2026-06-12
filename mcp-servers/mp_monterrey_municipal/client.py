"""Cliente mp_monterrey_municipal — mock-first."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, ValidationError  # noqa: E402
from shared.playwright_stub import (  # noqa: E402
    detectar_modo_playwright,
    mock_response_playwright,
    raise_playwright_real_no_implementado,
)

from mp_monterrey_municipal import mock_data  # noqa: E402
from mp_monterrey_municipal.catalogos import MUNICIPIOS_AMM  # noqa: E402


NAMESPACE = "monterrey_municipal_mcp"
CRED_VARS = ["NL_USUARIO", "NL_PASSWORD"]


class MonterreyMunicipalClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _modo(self) -> str:
        return detectar_modo_playwright(CRED_VARS)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        if "placa" in safe:
            safe["placa_hash"] = Bitacora.hash_sensitive(str(safe.pop("placa")))
        self._bitacora.log(op, success=True, params_summary=safe)

    def consultar_predial(self, municipio: str, cuenta: str) -> dict[str, Any]:
        if municipio not in MUNICIPIOS_AMM:
            raise ValidationError(
                f"Municipio '{municipio}' no soportado. "
                f"Soportados: {', '.join(MUNICIPIOS_AMM)}"
            )
        self._log("predial", {"municipio": municipio, "cuenta": cuenta})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_predial_nl(municipio, cuenta),
                portal=f"predial_nl_{municipio.lower().replace(' ', '_')}",
            )
        raise_playwright_real_no_implementado(f"predial_nl_{municipio}")

    def consultar_multas(self, placa: str) -> dict[str, Any]:
        if not placa:
            raise ValidationError("placa requerida")
        self._log("multas", {"placa": placa})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_multas_nl(placa),
                portal="nl_multas",
            )
        raise_playwright_real_no_implementado("nl_multas")

    def consultar_calidad_aire_nl(self, fecha: str) -> dict[str, Any]:
        self._log("calidad_aire", {"fecha": fecha})
        return mock_response_playwright(
            mock_data.mock_status_aire_nl(fecha),
            portal="aire_limpio_nl",
        )
