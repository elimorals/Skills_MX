"""Cliente mp_infonavit_patronal — mock-first."""

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

from mp_infonavit_patronal import mock_data  # noqa: E402


NAMESPACE = "infonavit_patronal_mcp"
CRED_VARS = ["INFONAVIT_RFC_PATRONAL", "INFONAVIT_USUARIO", "INFONAVIT_PASSWORD"]


class InfonavitPatronalClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _modo(self) -> str:
        return detectar_modo_playwright(CRED_VARS)

    def _log(self, op: str, params: dict[str, Any], *, success: bool = True) -> None:
        safe = dict(params)
        if "nss" in safe and safe["nss"]:
            safe["nss_hash"] = Bitacora.hash_sensitive(str(safe.pop("nss")))
        if "registro_patronal" in safe:
            safe["rp_hash"] = Bitacora.hash_sensitive(str(safe.pop("registro_patronal")))
        self._bitacora.log(op, success=success, params_summary=safe)

    def consultar_creditos_trabajadores(self, registro_patronal: str) -> dict[str, Any]:
        self._log("creditos_trabajadores", {"registro_patronal": registro_patronal})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_creditos_trabajadores(registro_patronal),
                portal="infonavit_empresarial",
            )
        raise_playwright_real_no_implementado("infonavit_empresarial")

    def descargar_emis(
        self, registro_patronal: str, mes: int, ejercicio: int
    ) -> dict[str, Any]:
        if mes < 1 or mes > 12:
            raise ValidationError("mes debe ser 1-12")
        self._log("emis", {
            "registro_patronal": registro_patronal,
            "mes": mes, "ejercicio": ejercicio,
        })
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_emis(registro_patronal, mes, ejercicio),
                portal="infonavit_empresarial",
            )
        raise_playwright_real_no_implementado("infonavit_empresarial")

    def consultar_descuentos_mensuales(
        self, registro_patronal: str, nss: str, mes: int, ejercicio: int
    ) -> dict[str, Any]:
        self._log("descuentos_mensuales", {
            "registro_patronal": registro_patronal,
            "nss": nss, "mes": mes, "ejercicio": ejercicio,
        })
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_descuentos_mensuales(registro_patronal, nss, mes, ejercicio),
                portal="infonavit_empresarial",
            )
        raise_playwright_real_no_implementado("infonavit_empresarial")

    def consultar_avisos_pendientes(self, registro_patronal: str) -> dict[str, Any]:
        self._log("avisos", {"registro_patronal": registro_patronal})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_avisos_pendientes(registro_patronal),
                portal="infonavit_empresarial",
            )
        raise_playwright_real_no_implementado("infonavit_empresarial")
