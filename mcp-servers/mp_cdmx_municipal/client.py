"""Cliente mp_cdmx_municipal — mock-first."""

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
from shared.playwright_real import (  # noqa: E402
    is_public_real_enabled,
    with_real_or_fallback,
)
from shared.playwright_stub import (  # noqa: E402
    detectar_modo_playwright,
    mock_response_playwright,
    raise_playwright_real_no_implementado,
)

from mp_cdmx_municipal import mock_data  # noqa: E402
from mp_cdmx_municipal import playwright_real  # noqa: E402


NAMESPACE = "cdmx_municipal_mcp"
CRED_VARS = ["CDMX_USUARIO", "CDMX_PASSWORD"]


class CdmxMunicipalClient:
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
        if "placa" in safe:
            safe["placa_hash"] = Bitacora.hash_sensitive(str(safe.pop("placa")))
        self._bitacora.log(op, success=success, params_summary=safe)

    def consultar_predial(self, cuenta_predial: str) -> dict[str, Any]:
        if not cuenta_predial or len(cuenta_predial) < 5:
            raise ValidationError("cuenta_predial debe tener al menos 5 caracteres")
        self._log("predial", {"cuenta_predial": cuenta_predial})
        # La consulta predial es PÚBLICA — solo requiere el número de cuenta
        if is_public_real_enabled():
            return with_real_or_fallback(
                real_fn=lambda: playwright_real.predial_real(cuenta_predial),
                fallback_fn=lambda: mock_data.mock_predial(cuenta_predial),
                portal="finanzas_cdmx_predial",
            )
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_predial(cuenta_predial),
                portal="finanzas_cdmx_predial",
            )
        raise_playwright_real_no_implementado("finanzas_cdmx_predial")

    def consultar_tenencia(self, placa: str) -> dict[str, Any]:
        if not placa or len(placa) < 5:
            raise ValidationError("placa requerida")
        self._log("tenencia", {"placa": placa})
        # Consulta tenencia/refrendo es PÚBLICA por placa
        if is_public_real_enabled():
            return with_real_or_fallback(
                real_fn=lambda: playwright_real.tenencia_real(placa),
                fallback_fn=lambda: mock_data.mock_tenencia(placa),
                portal="finanzas_cdmx_tenencia",
            )
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_tenencia(placa),
                portal="finanzas_cdmx_tenencia",
            )
        raise_playwright_real_no_implementado("finanzas_cdmx_tenencia")

    def consultar_multas(self, placa: str) -> dict[str, Any]:
        if not placa or len(placa) < 5:
            raise ValidationError("placa requerida")
        self._log("multas", {"placa": placa})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_multas(placa),
                portal="semovi_cdmx_multas",
            )
        raise_playwright_real_no_implementado("semovi_cdmx_multas")

    def consultar_calendario_hoy_no_circula(self, fecha: str) -> dict[str, Any]:
        self._log("hoy_no_circula", {"fecha": fecha})
        # Este es informativo — siempre disponible como conocimiento local
        return mock_response_playwright(
            mock_data.mock_calendario_hoy_no_circula(fecha),
            portal="semovi_cdmx_hoynocirucla",
            nota_extra="Reglas actualizadas a 2025. Verificar para 2026.",
        )
