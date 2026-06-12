"""Cliente mp_buro_credito_personal.

⚠ Cualquier consulta requiere TOKEN DE AUTORIZACIÓN previo registrado.
Sin este token la operación se bloquea independientemente del modo.
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

from mp_buro_credito_personal import mock_data  # noqa: E402


NAMESPACE = "buro_credito_mcp"
CRED_VARS = ["BURO_API_KEY", "BURO_USUARIO", "BURO_PASSWORD"]


class BuroAutorizacionError(McpError):
    """Falta token/autorización del titular para consultar su reporte."""

    code = "buro_autorizacion_faltante"


class BuroCreditoClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _modo(self) -> str:
        return detectar_modo_playwright(CRED_VARS)

    def _validar_autorizacion(self, autorizacion_token: str | None) -> None:
        """Verifica que se pasó un token de autorización del titular.

        En producción, este token vendría de:
        - Firma digital del titular (e.firma o Mifiel)
        - Click-wrap agreement con timestamp + IP + RFC del titular
        - Carta firmada digitalizada con OCR validado
        """
        if not autorizacion_token or len(autorizacion_token) < 16:
            raise BuroAutorizacionError(
                "Consultar Buró sin autorización del titular es DELITO (Art. 32 LFPDPPP + LRSIC). "
                "Debe pasar un token de autorización válido (firma digital, click-wrap, etc.)."
            )

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        # Todo sensible se hashea SIEMPRE
        if "rfc" in safe:
            safe["rfc_hash"] = Bitacora.hash_sensitive(str(safe.pop("rfc")))
        if "autorizacion_token" in safe:
            # No logear el token completo (sensible)
            safe["autorizacion_token_hash"] = Bitacora.hash_sensitive(
                str(safe.pop("autorizacion_token"))
            )
        self._bitacora.log(op, success=True, params_summary=safe)

    # ---------- tools ----------

    def consultar_score(
        self, rfc: str, autorizacion_token: str
    ) -> dict[str, Any]:
        self._validar_autorizacion(autorizacion_token)
        if not rfc or len(rfc) < 12:
            raise ValidationError("RFC inválido")

        self._log("consultar_score", {
            "rfc": rfc, "autorizacion_token": autorizacion_token,
        })
        rfc_hash = Bitacora.hash_sensitive(rfc) or ""

        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_score(rfc_hash),
                portal="buro_credito",
                nota_extra="Token de autorización registrado en bitácora (hash).",
            )
        raise_playwright_real_no_implementado("buro_credito")

    def descargar_reporte_completo(
        self, rfc: str, autorizacion_token: str
    ) -> dict[str, Any]:
        self._validar_autorizacion(autorizacion_token)
        if not rfc or len(rfc) < 12:
            raise ValidationError("RFC inválido")

        self._log("reporte_completo", {
            "rfc": rfc, "autorizacion_token": autorizacion_token,
        })
        rfc_hash = Bitacora.hash_sensitive(rfc) or ""

        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_reporte_completo(rfc_hash),
                portal="buro_credito",
                nota_extra="Reporte personal — manejar con confidencialidad.",
            )
        raise_playwright_real_no_implementado("buro_credito")

    def monitorear_alertas(
        self, rfc: str, autorizacion_token: str
    ) -> dict[str, Any]:
        self._validar_autorizacion(autorizacion_token)
        if not rfc or len(rfc) < 12:
            raise ValidationError("RFC inválido")

        self._log("monitorear_alertas", {
            "rfc": rfc, "autorizacion_token": autorizacion_token,
        })
        rfc_hash = Bitacora.hash_sensitive(rfc) or ""

        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_alertas_recientes(rfc_hash),
                portal="buro_credito",
            )
        raise_playwright_real_no_implementado("buro_credito")
