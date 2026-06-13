"""Cliente mp_inmuebles24 — mock-first."""

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

from mp_inmuebles24 import mock_data  # noqa: E402
from mp_inmuebles24 import playwright_real  # noqa: E402
from mp_inmuebles24.catalogos import TIPO_INMUEBLE, TIPO_OPERACION  # noqa: E402


NAMESPACE = "inmuebles24_mcp"
CRED_VARS = ["INMUEBLES24_USUARIO", "INMUEBLES24_PASSWORD"]


class Inmuebles24Client:
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
        self._bitacora.log(op, success=True, params_summary=params)

    def buscar_inmuebles(
        self,
        tipo_operacion: str,
        tipo_inmueble: str,
        ciudad: str,
        precio_min: float | None = None,
        precio_max: float | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        if tipo_operacion not in TIPO_OPERACION:
            raise ValidationError(f"tipo_operacion inválido: {tipo_operacion}")
        if tipo_inmueble not in TIPO_INMUEBLE:
            raise ValidationError(f"tipo_inmueble inválido: {tipo_inmueble}")
        if precio_min and precio_max and precio_min > precio_max:
            raise ValidationError("precio_min > precio_max")

        self._log("buscar", {
            "tipo_operacion": tipo_operacion,
            "tipo_inmueble": tipo_inmueble,
            "ciudad": ciudad,
        })
        # Búsqueda es pública — usa Playwright real si MP_PLAYWRIGHT_PUBLIC=1
        if is_public_real_enabled():
            return with_real_or_fallback(
                real_fn=lambda: playwright_real.buscar_real(
                    tipo_operacion, tipo_inmueble, ciudad, precio_min, precio_max, limit
                ),
                fallback_fn=lambda: mock_data.mock_buscar_inmuebles(
                    tipo_operacion, tipo_inmueble, ciudad, precio_min, precio_max, limit
                ),
                portal="inmuebles24",
            )
        return mock_response_playwright(
            mock_data.mock_buscar_inmuebles(
                tipo_operacion, tipo_inmueble, ciudad, precio_min, precio_max, limit
            ),
            portal="inmuebles24",
        )

    def obtener_detalle(self, id_inmueble: str) -> dict[str, Any]:
        if not id_inmueble:
            raise ValidationError("id_inmueble requerido")
        self._log("detalle", {"id": id_inmueble})
        if is_public_real_enabled():
            return with_real_or_fallback(
                real_fn=lambda: playwright_real.detalle_real(id_inmueble),
                fallback_fn=lambda: mock_data.mock_detalle_inmueble(id_inmueble),
                portal="inmuebles24",
            )
        return mock_response_playwright(
            mock_data.mock_detalle_inmueble(id_inmueble),
            portal="inmuebles24",
        )

    def buscar_comparables_zona(
        self,
        ubicacion: str,
        tipo_inmueble: str,
        metros_min: int = 50,
        metros_max: int = 500,
    ) -> dict[str, Any]:
        if tipo_inmueble not in TIPO_INMUEBLE:
            raise ValidationError(f"tipo_inmueble inválido: {tipo_inmueble}")
        self._log("comparables", {
            "ubicacion": ubicacion, "tipo": tipo_inmueble,
        })
        if is_public_real_enabled():
            return with_real_or_fallback(
                real_fn=lambda: playwright_real.comparables_real(
                    ubicacion, tipo_inmueble, metros_min, metros_max
                ),
                fallback_fn=lambda: mock_data.mock_comparables_zona(
                    ubicacion, tipo_inmueble, metros_min, metros_max
                ),
                portal="inmuebles24",
            )
        return mock_response_playwright(
            mock_data.mock_comparables_zona(ubicacion, tipo_inmueble, metros_min, metros_max),
            portal="inmuebles24",
        )

    def publicar_listing(
        self,
        titulo: str,
        precio_mxn: float,
        tipo_operacion: str,
        tipo_inmueble: str,
    ) -> dict[str, Any]:
        if tipo_operacion not in TIPO_OPERACION:
            raise ValidationError(f"tipo_operacion inválido: {tipo_operacion}")
        if tipo_inmueble not in TIPO_INMUEBLE:
            raise ValidationError(f"tipo_inmueble inválido: {tipo_inmueble}")
        self._log("publicar", {"titulo": titulo, "precio": precio_mxn})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_publicar_listing(
                    titulo, precio_mxn, tipo_operacion, tipo_inmueble
                ),
                portal="inmuebles24",
            )
        raise_playwright_real_no_implementado("inmuebles24")
