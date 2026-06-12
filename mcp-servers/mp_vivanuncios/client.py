"""Cliente mp_vivanuncios — mock-first."""

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

from mp_vivanuncios import mock_data  # noqa: E402
from mp_vivanuncios.catalogos import CATEGORIAS_VIVANUNCIOS  # noqa: E402


NAMESPACE = "vivanuncios_mcp"
CRED_VARS = ["VIVANUNCIOS_USUARIO", "VIVANUNCIOS_PASSWORD"]


class VivanunciosClient:
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

    def buscar_anuncios(
        self, categoria: str, query: str, ciudad: str, limit: int = 10
    ) -> dict[str, Any]:
        if categoria not in CATEGORIAS_VIVANUNCIOS:
            raise ValidationError(
                f"categoria inválida. Válidas: {', '.join(CATEGORIAS_VIVANUNCIOS.keys())}"
            )
        if not query:
            raise ValidationError("query requerida")
        self._log("buscar", {"categoria": categoria, "query": query, "ciudad": ciudad})
        return mock_response_playwright(
            mock_data.mock_buscar_anuncios(categoria, query, ciudad, limit),
            portal="vivanuncios",
        )

    def obtener_detalle(self, id_anuncio: str) -> dict[str, Any]:
        if not id_anuncio:
            raise ValidationError("id_anuncio requerido")
        self._log("detalle", {"id": id_anuncio})
        return mock_response_playwright(
            mock_data.mock_detalle_anuncio(id_anuncio),
            portal="vivanuncios",
        )

    def publicar_anuncio(
        self, titulo: str, categoria: str, precio_mxn: float
    ) -> dict[str, Any]:
        if categoria not in CATEGORIAS_VIVANUNCIOS:
            raise ValidationError(f"categoria inválida: {categoria}")
        self._log("publicar", {"titulo": titulo, "categoria": categoria})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_publicar_anuncio(titulo, categoria, precio_mxn),
                portal="vivanuncios",
            )
        raise_playwright_real_no_implementado("vivanuncios")
