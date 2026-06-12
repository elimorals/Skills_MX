"""Cliente mp_edomex_municipal — mock-first."""

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

from mp_edomex_municipal import mock_data  # noqa: E402
from mp_edomex_municipal.catalogos import MUNICIPIOS_PREDIAL_DIGITAL  # noqa: E402


NAMESPACE = "edomex_municipal_mcp"
CRED_VARS = ["EDOMEX_USUARIO", "EDOMEX_PASSWORD"]


class EdomexMunicipalClient:
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

    def consultar_predial(self, municipio: str, cuenta_predial: str) -> dict[str, Any]:
        if not municipio:
            raise ValidationError("municipio requerido")
        self._log("predial", {"municipio": municipio, "cuenta": cuenta_predial})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_predial_edomex(municipio, cuenta_predial),
                portal=f"predial_{municipio.lower()}",
            )
        raise_playwright_real_no_implementado(f"predial_{municipio.lower()}")

    def consultar_tenencia(self, placa: str, ejercicio: int) -> dict[str, Any]:
        if not placa:
            raise ValidationError("placa requerida")
        self._log("tenencia", {"placa": placa, "ejercicio": ejercicio})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_tenencia_edomex(placa, ejercicio),
                portal="finanzas_edomex_tenencia",
            )
        raise_playwright_real_no_implementado("finanzas_edomex_tenencia")

    def consultar_multas(self, placa: str) -> dict[str, Any]:
        if not placa:
            raise ValidationError("placa requerida")
        self._log("multas", {"placa": placa})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_multas_edomex(placa),
                portal="edomex_multas",
            )
        raise_playwright_real_no_implementado("edomex_multas")

    def municipios_soportados(self) -> list[str]:
        return MUNICIPIOS_PREDIAL_DIGITAL
