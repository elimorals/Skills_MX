"""Cliente orquestador para portales bancarios MX (mock-first).

⚠ Path real con Playwright NO implementado. Cada banco requiere
60-100h de scraping + tests + mantenimiento mensual. Sin credenciales
corre 100% mock con datos plausibles.
"""

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

from mp_bancos_mx import mock_data  # noqa: E402
from mp_bancos_mx.catalogos import (  # noqa: E402
    BANCOS_SOPORTADOS,
    banco_info,
)


NAMESPACE = "bancos_mx_mcp"

# Credenciales: BANCOS_MX_USUARIO + BANCOS_MX_PASSWORD por banco (override
# por código bancario, ej. BBVA_USUARIO, BBVA_PASSWORD).
CRED_VARS_GENERICAS = ["BANCOS_MX_USUARIO", "BANCOS_MX_PASSWORD"]


class BancosMxClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _modo(self, banco: str) -> str:
        # Cred override por banco
        banco_upper = banco.upper()
        cred_vars = [
            f"{banco_upper}_USUARIO",
            f"{banco_upper}_PASSWORD",
            *CRED_VARS_GENERICAS,
        ]
        return detectar_modo_playwright(cred_vars)

    def _log(self, op: str, params: dict[str, Any], *, success: bool = True) -> None:
        safe = dict(params)
        if "cuenta" in safe and safe["cuenta"]:
            safe["cuenta_hash"] = Bitacora.hash_sensitive(str(safe.pop("cuenta")))
        self._bitacora.log(op, success=success, params_summary=safe)

    def _validar_banco(self, banco: str) -> None:
        if banco.lower() not in BANCOS_SOPORTADOS:
            raise ValidationError(
                f"Banco '{banco}' no soportado. "
                f"Soportados: {', '.join(BANCOS_SOPORTADOS.keys())}"
            )

    # ---------- tools ----------

    def listar_bancos_soportados(self) -> dict[str, Any]:
        """Discovery offline: lista todos los bancos + estado del path real."""
        return {
            "total": len(BANCOS_SOPORTADOS),
            "bancos": BANCOS_SOPORTADOS,
            "path_real_implementado_en_algun_banco": False,
            "modo_default": "mock",
        }

    def descargar_estado_cuenta(
        self,
        banco: str,
        cuenta: str,
        ejercicio: int,
        mes: int,
        formato: str = "pdf",
    ) -> dict[str, Any]:
        self._validar_banco(banco)
        self._log("descargar_estado_cuenta", {
            "banco": banco, "cuenta": cuenta,
            "ejercicio": ejercicio, "mes": mes, "formato": formato,
        })
        modo = self._modo(banco)

        if modo == "mock":
            return mock_response_playwright(
                mock_data.mock_estado_cuenta(banco, cuenta, ejercicio, mes),
                portal=f"banca_{banco}",
            )
        raise_playwright_real_no_implementado(f"banco_{banco}")

    def listar_movimientos(
        self,
        banco: str,
        cuenta: str,
        dias: int = 30,
    ) -> dict[str, Any]:
        self._validar_banco(banco)
        if dias < 1 or dias > 365:
            raise ValidationError("dias debe estar entre 1 y 365")

        self._log("listar_movimientos", {
            "banco": banco, "cuenta": cuenta, "dias": dias,
        })
        modo = self._modo(banco)

        if modo == "mock":
            return mock_response_playwright(
                mock_data.mock_movimientos(banco, cuenta, dias),
                portal=f"banca_{banco}",
            )
        raise_playwright_real_no_implementado(f"banco_{banco}")

    def verificar_pago_por_referencia(
        self,
        banco: str,
        referencia: str,
        monto: float,
    ) -> dict[str, Any]:
        self._validar_banco(banco)
        self._log("verificar_pago_por_referencia", {
            "banco": banco, "referencia": referencia, "monto": monto,
        })
        modo = self._modo(banco)

        if modo == "mock":
            return mock_response_playwright(
                mock_data.mock_verificar_pago(banco, referencia, monto),
                portal=f"banca_{banco}",
            )
        raise_playwright_real_no_implementado(f"banco_{banco}")
