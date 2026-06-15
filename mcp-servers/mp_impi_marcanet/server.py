"""mp_impi_marcanet — MCP standalone para IMPI ViDoc (búsqueda marcas).

Tools:
- impi_buscar(query, [limite, incluir_raw])              — búsqueda libre
- impi_verificar_denominacion(denominacion)              — para legaltech / startups

Portal: https://vidoc.impi.gob.mx/busc (reemplazó MARCANET descontinuado).
Backend: POST /api/BusquedaDocumentos/getBusquedaSimpleNdjson — requiere
reCAPTCHA v3 + XSRF token → MCP usa Playwright en modo real.
"""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_impi_marcanet.client import (  # noqa: E402
    DEFAULT_LIMITE,
    MAX_LIMITE,
    ImpiMarcanetClient,
)


mcp = FastMCP("impi_marcanet")
_client = ImpiMarcanetClient()


class BuscarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Término a buscar (marca, denominación, titular).",
    )
    limite: int = Field(
        DEFAULT_LIMITE,
        ge=1,
        le=MAX_LIMITE,
        description=f"Máx resultados (1-{MAX_LIMITE}).",
    )
    incluir_raw: bool = Field(
        False,
        description="Si True, incluye fichaDatos completa por cada resultado.",
    )


class VerificarDenominacionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    denominacion: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre comercial que se quiere registrar como marca.",
    )


@mcp.tool(annotations={
    "title": "Buscar marcas en IMPI ViDoc",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def impi_buscar(args: BuscarInput) -> dict:
    """Busca expedientes IMPI (marcas, patentes, diseños) por término libre.

    Returns:
        {
          "query": str (normalizado upper),
          "total_encontrados": int,
          "devueltos": int,
          "resultados": [
            {
              "expediente": "MA/M/1985/3502080",
              "denominacion": "RELLAMADO TELMEX",
              "titular": "TELEFONOS DE MEXICO, S.A.B. DE C.V.",
              "clase_niza": "38",
              ...
            }
          ],
          "fuente": URL portal,
          "modo": "mock" | "playwright" | "cache",
        }
    """
    return _client.buscar(
        query=args.query,
        limite=args.limite,
        incluir_raw=args.incluir_raw,
    )


@mcp.tool(annotations={
    "title": "Verificar disponibilidad de denominación (legaltech)",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def impi_verificar_denominacion(args: VerificarDenominacionInput) -> dict:
    """Evalúa si una denominación tiene coincidencias en el padrón IMPI.

    Útil para legaltech, agencias creativas y startups que evalúan
    si un nombre comercial es registrable antes de pagar el trámite.

    Returns:
        {
          "denominacion": str,
          "tiene_coincidencias": bool,
          "coincidencias_exactas": int,
          "coincidencias_similares": int,
          "ejemplos": [...top 5],
          "advertencias": [str]
        }

    NOTA: IMPI evalúa similitud fonética/gráfica/conceptual, no solo exactitud.
    Resultado "sin coincidencias" NO garantiza registrabilidad.
    """
    return _client.verificar_denominacion(args.denominacion)


if __name__ == "__main__":
    mcp.run()
