"""mp_ley_silla_nom037 — MCP server."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_ley_silla_nom037.client import LeySillaNomClient  # noqa: E402


mcp = FastMCP("ley_silla_nom037")
_client = LeySillaNomClient()


class VerificarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(..., min_length=12, max_length=13)
    num_empleados: int = Field(..., ge=1, le=1000000)
    giro: str
    modalidad_remota: bool = False
    faltas_marcadas: list[str] = Field(default_factory=list)


class MultaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    severidad: str
    reincidente: bool = False


class PoliticaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(..., min_length=12, max_length=13)
    razon_social: str = Field(..., min_length=3)
    giro: str
    modalidad: str = "presencial"
    nombre_responsable_sst: str = Field(..., min_length=3)


class ListarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    marco: str = Field(..., pattern="^(ley_silla|nom035|nom037|desconexion_digital)$")


@mcp.tool(annotations={"title": "Verificar compliance Ley Silla + NOM-035/037", "readOnlyHint": True})
def silla_verificar_compliance(args: VerificarInput) -> dict:
    """Genera checklist + multa potencial + score."""
    return _client.verificar_compliance(
        rfc=args.rfc, num_empleados=args.num_empleados, giro=args.giro,
        modalidad_remota=args.modalidad_remota, faltas_marcadas=args.faltas_marcadas,
    )


@mcp.tool(annotations={"title": "Calcular multa STPS", "readOnlyHint": True, "idempotentHint": True})
def silla_calcular_multa(args: MultaInput) -> dict:
    """Rango multa MXN por severidad + reincidencia."""
    return _client.calcular_multa(severidad=args.severidad, reincidente=args.reincidente)


@mcp.tool(annotations={"title": "Generar política SST consolidada", "readOnlyHint": True})
def silla_generar_politica(args: PoliticaInput) -> dict:
    """Política de prevención + desconexión digital en Markdown firmable."""
    return _client.generar_politica(
        rfc=args.rfc, razon_social=args.razon_social, giro=args.giro,
        modalidad=args.modalidad, nombre_responsable_sst=args.nombre_responsable_sst,
    )


@mcp.tool(annotations={"title": "Listar obligaciones por marco", "readOnlyHint": True, "idempotentHint": True})
def silla_listar_obligaciones(args: ListarInput) -> dict:
    """Catálogo completo de obligaciones por marco legal."""
    return _client.listar_obligaciones(marco=args.marco)


if __name__ == "__main__":
    mcp.run()
