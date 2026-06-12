"""Cliente mp_imss_patronal — mock-first.

⚠ Path Playwright real NO implementado. IMSS IDSE requiere e.firma o
tarjeta NPIE. Construcción real ~100-150h.
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

from mp_imss_patronal import mock_data  # noqa: E402
from mp_imss_patronal.catalogos import CAUSA_BAJA, TIPOS_MOVIMIENTO_AFILIATORIO  # noqa: E402


NAMESPACE = "imss_patronal_mcp"
CRED_VARS = ["IMSS_RFC_PATRONAL", "IMSS_NPIE_PATH", "IMSS_EFIRMA_CERT"]


class ImssPatronalClient:
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
            safe["registro_patronal_hash"] = Bitacora.hash_sensitive(
                str(safe.pop("registro_patronal"))
            )
        self._bitacora.log(op, success=success, params_summary=safe)

    # ---------- tools ----------

    def consultar_avisos_pendientes(self, registro_patronal: str) -> dict[str, Any]:
        self._log("consultar_avisos", {"registro_patronal": registro_patronal})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_avisos_pendientes(registro_patronal),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def enviar_movimiento_afiliatorio(
        self,
        registro_patronal: str,
        nss: str,
        tipo_movimiento: str,
        salario_diario: float | None = None,
        causa_baja: str | None = None,
    ) -> dict[str, Any]:
        if tipo_movimiento not in TIPOS_MOVIMIENTO_AFILIATORIO:
            raise ValidationError(
                f"tipo_movimiento '{tipo_movimiento}' inválido. "
                f"Válidos: {', '.join(TIPOS_MOVIMIENTO_AFILIATORIO.keys())}"
            )
        if tipo_movimiento == "08" and salario_diario is None:
            raise ValidationError("Alta (08) requiere salario_diario")
        if tipo_movimiento == "02":
            if not causa_baja or causa_baja not in CAUSA_BAJA:
                raise ValidationError(
                    f"Baja (02) requiere causa_baja. Válidas: {list(CAUSA_BAJA.keys())}"
                )

        self._log("movimiento_afiliatorio", {
            "registro_patronal": registro_patronal,
            "nss": nss,
            "tipo": tipo_movimiento,
        })
        if self._modo() == "mock":
            if tipo_movimiento == "08":
                return mock_response_playwright(
                    mock_data.mock_alta_trabajador(registro_patronal, nss, salario_diario),  # type: ignore[arg-type]
                    portal="imss_idse",
                )
            if tipo_movimiento == "02":
                return mock_response_playwright(
                    mock_data.mock_baja_trabajador(registro_patronal, nss, causa_baja),  # type: ignore[arg-type]
                    portal="imss_idse",
                )
            return mock_response_playwright(
                {
                    "registro_patronal": registro_patronal,
                    "nss_mascarado": "**" + nss[-2:] if len(nss) > 2 else nss,
                    "tipo_movimiento": tipo_movimiento,
                    "estatus": "PROCESADO",
                    "fecha": "ya",
                },
                portal="imss_idse",
                nota_extra=f"Mock para tipo movimiento {tipo_movimiento}.",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def descargar_cedula_autodeterminacion(
        self, registro_patronal: str, bimestre: int, ejercicio: int
    ) -> dict[str, Any]:
        if bimestre < 1 or bimestre > 6:
            raise ValidationError("bimestre debe ser 1-6")
        self._log("cedula", {
            "registro_patronal": registro_patronal,
            "bimestre": bimestre, "ejercicio": ejercicio,
        })
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_cedula_autodeterminacion(registro_patronal, bimestre, ejercicio),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def consultar_emcr(
        self, registro_patronal: str, mes: int, ejercicio: int
    ) -> dict[str, Any]:
        self._log("emcr", {
            "registro_patronal": registro_patronal,
            "mes": mes, "ejercicio": ejercicio,
        })
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_emcr(registro_patronal, mes, ejercicio),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def consultar_salario_diario_integrado(
        self, registro_patronal: str, nss: str
    ) -> dict[str, Any]:
        self._log("sbc", {"registro_patronal": registro_patronal, "nss": nss})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_sbc(registro_patronal, nss),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def consultar_padron_trabajadores(
        self, registro_patronal: str
    ) -> dict[str, Any]:
        self._log("padron", {"registro_patronal": registro_patronal})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_padron_trabajadores(registro_patronal),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")
