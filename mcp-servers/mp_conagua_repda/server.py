"""mp_conagua_repda MCP."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_conagua_repda.client import CONAGUARepdaClient  # noqa: E402


mcp = FastMCP("conagua_repda")
_client = CONAGUARepdaClient()


class TitularInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    identificador: str = Field(..., min_length=5, max_length=120,
                               description="Nombre (parcial) del titular o número de título completo")


class ReporteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    num_titulo: str
    periodo: Literal["T1", "T2", "T3", "T4"]


class LFDInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    num_titulo: str
    m3_extraidos: float = Field(..., ge=0)
    zona_disponibilidad: int = Field(..., ge=1, le=4, description="Zona Art. 231 LFD")
    fuente: Literal["superficial", "subterranea"] = "subterranea"


class VigenciaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    num_titulo: str


class MedidorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    volumen_anual_m3: float = Field(..., ge=0)
    tipo_uso: str | None = None


@mcp.tool(annotations={"title": "Consultar titular REPDA", "readOnlyHint": True})
def repda_consultar_titular(args: TitularInput) -> dict:
    return _client.consultar_titular(identificador=args.identificador)


@mcp.tool(annotations={"title": "Calendario declaración trimestral", "readOnlyHint": True})
def repda_estado_reporte(args: ReporteInput) -> dict:
    return _client.estado_reporte_semestral(num_titulo=args.num_titulo, periodo=args.periodo)


@mcp.tool(annotations={"title": "Calcular pago LFD", "readOnlyHint": True, "idempotentHint": True})
def repda_calcular_lfd(args: LFDInput) -> dict:
    return _client.calcular_pago_lfd(num_titulo=args.num_titulo,
                                       m3_extraidos=args.m3_extraidos,
                                       zona_disponibilidad=args.zona_disponibilidad,
                                       fuente=args.fuente)


@mcp.tool(annotations={"title": "Consultar vigencia título", "readOnlyHint": True})
def repda_vigencia(args: VigenciaInput) -> dict:
    return _client.consultar_vigencia(num_titulo=args.num_titulo)


@mcp.tool(annotations={"title": "Requiere medidor obligatorio", "readOnlyHint": True, "idempotentHint": True})
def repda_requiere_medidor(args: MedidorInput) -> dict:
    return _client.requiere_medidor(volumen_anual_m3=args.volumen_anual_m3, tipo_uso=args.tipo_uso)


@mcp.tool(annotations={"title": "Tipos de uso CONAGUA", "readOnlyHint": True, "idempotentHint": True})
def repda_listar_tipos_uso() -> dict:
    return _client.listar_tipos_uso()


if __name__ == "__main__":
    mcp.run()
