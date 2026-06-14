"""mp_isn_mx — MCP multi-estado para Impuesto sobre Nómina (ISN) MX.

Tools:
- isn_calcular(nomina_gravable, estado)
- isn_listar_estados([solo_validados])
- isn_info_estado(estado)
- isn_generar_linea_captura(estado, periodo, rfc, nomina_gravable)
- isn_descargar_declaracion(estado, periodo, rfc)

Universo: TODA empresa formal MX con al menos 1 trabajador (~4M empresas).
8 estados validados con portal real: CDMX, JAL, NL, EdoMex, QRO, PUE, GTO, BC.
24 estados restantes con catálogo básico + URL portal.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_isn_mx.client import IsnMxClient  # noqa: E402


mcp = FastMCP("isn_mx")
_client = IsnMxClient()


# ============================================================
# Schemas
# ============================================================

class CalcularInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nomina_gravable: float = Field(..., ge=0,
                                   description="Total de erogaciones gravables del periodo (MXN).")
    estado: str = Field(..., min_length=2, max_length=20,
                        description="Clave del estado (CDMX, JAL, NL, EDOMEX, ...) o nombre completo.")


class ListarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    solo_validados: bool = Field(False,
                                  description="Si True, devuelve sólo estados con portal validado.")


class InfoEstadoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=20)


class LineaCapturaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=20)
    periodo: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
                         description="Periodo YYYY-MM (ej. '2026-05').")
    rfc: str = Field(..., min_length=12, max_length=13,
                     description="RFC del contribuyente.")
    nomina_gravable: float = Field(..., ge=0,
                                    description="Erogaciones del periodo (MXN).")


class DescargarDeclaracionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=20)
    periodo: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    rfc: str = Field(..., min_length=12, max_length=13)


# ============================================================
# Tools
# ============================================================

@mcp.tool(annotations={
    "title": "Calcular ISN del periodo (offline)",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def isn_calcular(args: CalcularInput) -> dict:
    """Calcula ISN del periodo aplicando la tasa del estado.

    No requiere acceso al portal — usa el catálogo central.

    Returns:
        {
          "nomina_gravable": float,
          "estado": str,
          "estado_clave": str,
          "tasa_pct": float,
          "isn_a_pagar": float,
          "vencimiento_dia": int,
          "portal_url": str
        }
    """
    return _client.calcular(
        nomina_gravable=args.nomina_gravable,
        estado=args.estado,
    )


@mcp.tool(annotations={
    "title": "Listar estados con ISN del catálogo",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def isn_listar_estados(args: ListarInput) -> dict:
    """Devuelve lista de los 32 estados MX con su configuración ISN."""
    return _client.listar(solo_validados=args.solo_validados)


@mcp.tool(annotations={
    "title": "Info detallada del ISN por estado",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def isn_info_estado(args: InfoEstadoInput) -> dict:
    """Devuelve configuración completa de un estado: portal, tasa, selectores DOM, notas."""
    return _client.info_estado(args.estado)


@mcp.tool(annotations={
    "title": "Generar línea de captura ISN",
    "readOnlyHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
})
def isn_generar_linea_captura(args: LineaCapturaInput) -> dict:
    """Genera línea de captura para pagar ISN del periodo.

    Mock por default. Real requiere MP_PLAYWRIGHT_PUBLIC=1 + credenciales estatales.

    Returns:
        {
          "estado": str,
          "periodo": str,
          "linea_captura": str,
          "monto_a_pagar": float,
          "tasa_aplicada_pct": float,
          "vencimiento_dia": int,
          "portal_pago": str,
          "instrucciones": str
        }
    """
    return _client.generar_linea_captura(
        estado=args.estado,
        periodo=args.periodo,
        rfc=args.rfc,
        nomina_gravable=args.nomina_gravable,
    )


@mcp.tool(annotations={
    "title": "Descargar comprobante de declaración ISN (PDF)",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def isn_descargar_declaracion(args: DescargarDeclaracionInput) -> dict:
    """Descarga el PDF de la declaración del periodo desde la bóveda estatal."""
    return _client.descargar_declaracion(
        estado=args.estado,
        periodo=args.periodo,
        rfc=args.rfc,
    )


if __name__ == "__main__":
    mcp.run()
