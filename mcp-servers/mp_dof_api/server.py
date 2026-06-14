"""mp_dof_api — MCP Diario Oficial de la Federación.

Tools:
- dof_sumario_dia(fecha)
- dof_buscar_texto(texto, [desde, hasta, limite])
- dof_detalle_nota(codigo, fecha)
- dof_monitorear_por_keyword(keywords[], [dias_atras]) — compliance horizontal
- dof_listar_dependencias_comunes()

100% público, sin captcha, sin login. Endpoints validados Playwright MCP 2026-06-14.
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

from mp_dof_api.client import DofApiClient  # noqa: E402


mcp = FastMCP("dof_api")
_client = DofApiClient()


class SumarioDiaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fecha: str = Field(..., min_length=8, max_length=10,
                       description="Fecha en formato DD/MM/YYYY o YYYY-MM-DD.")


class BuscarTextoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    texto: str = Field(..., min_length=3, max_length=200,
                       description="Término a buscar (full-text).")
    desde: Optional[str] = Field(None, description="Fecha desde (DD/MM/YYYY). Default: hace 10 años.")
    hasta: Optional[str] = Field(None, description="Fecha hasta (DD/MM/YYYY). Default: hoy.")
    limite: int = Field(20, ge=1, le=100)


class DetalleNotaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str = Field(..., min_length=4, max_length=8, pattern=r"^\d+$",
                        description="Código de nota (4-8 dígitos).")
    fecha: str = Field(..., min_length=8, max_length=10,
                       description="Fecha de publicación DD/MM/YYYY.")


class MonitorearInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    keywords: list[str] = Field(..., min_length=1, max_length=10,
                                 description="Lista de palabras clave a monitorear.")
    dias_atras: int = Field(7, ge=1, le=365,
                             description="Días hacia atrás desde hoy (default 7).")


@mcp.tool(annotations={
    "title": "Sumario de notas publicadas un día",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def dof_sumario_dia(args: SumarioDiaInput) -> dict:
    """Devuelve todas las notas DOF publicadas en una fecha específica.

    Útil para revisión diaria/semanal de cambios regulatorios.
    """
    return _client.sumario_dia(args.fecha)


@mcp.tool(annotations={
    "title": "Búsqueda full-text en histórico DOF",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def dof_buscar_texto(args: BuscarTextoInput) -> dict:
    """Búsqueda full-text en el DOF dentro de un periodo de fechas."""
    return _client.buscar_texto(
        texto=args.texto, desde=args.desde, hasta=args.hasta, limite=args.limite,
    )


@mcp.tool(annotations={
    "title": "Detalle completo de una nota DOF",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def dof_detalle_nota(args: DetalleNotaInput) -> dict:
    """Devuelve texto completo + metadatos de una nota."""
    return _client.detalle_nota(codigo=args.codigo, fecha=args.fecha)


@mcp.tool(annotations={
    "title": "Monitor compliance horizontal por keywords",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def dof_monitorear_por_keyword(args: MonitorearInput) -> dict:
    """Monitor compliance: vigila N keywords en los últimos N días.

    Útil para:
    - Despachos legales: cambios en leyes que mencionen rubros específicos
    - Despachos contables: modificaciones a RMF/anexos/CFF
    - Áreas compliance: sanciones a contrapartes (búsqueda por RFC/razón social)
    - Áreas regulatorias: nuevas NOMs aplicables
    """
    return _client.monitorear_por_keyword(
        keywords=args.keywords, dias_atras=args.dias_atras,
    )


@mcp.tool(annotations={
    "title": "Catálogo de dependencias comunes",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def dof_listar_dependencias_comunes() -> dict:
    """Devuelve dependencias DOF más frecuentes (SAT, SHCP, BANXICO, etc.)."""
    return _client.listar_dependencias_comunes()


if __name__ == "__main__":
    mcp.run()
