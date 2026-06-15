"""mp_desconexion_digital MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_desconexion_digital.client import DesconexionDigitalClient  # noqa: E402


mcp = FastMCP("desconexion_digital")
_client = DesconexionDigitalClient()


class ChecklistInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(..., min_length=12, max_length=13)
    faltas_marcadas: list[str] = Field(default_factory=list)


class PoliticaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(..., min_length=12, max_length=13)
    razon_social: str = Field(..., min_length=3)
    jornada_inicio: str = "09:00"
    jornada_fin: str = "18:00"
    canal_denuncia_email: str | None = None


@mcp.tool(annotations={"title": "Checklist cumplimiento desconexión digital", "readOnlyHint": True})
def desconexion_checklist(args: ChecklistInput) -> dict:
    return _client.checklist_cumplimiento(rfc=args.rfc, faltas_marcadas=args.faltas_marcadas)


@mcp.tool(annotations={"title": "Generar política desconexión digital", "readOnlyHint": True})
def desconexion_generar_politica(args: PoliticaInput) -> dict:
    return _client.generar_politica(
        rfc=args.rfc, razon_social=args.razon_social,
        jornada_inicio=args.jornada_inicio, jornada_fin=args.jornada_fin,
        canal_denuncia_email=args.canal_denuncia_email,
    )


@mcp.tool(annotations={"title": "Template capacitación desconexión", "readOnlyHint": True, "idempotentHint": True})
def desconexion_template_capacitacion() -> dict:
    return _client.template_capacitacion()


if __name__ == "__main__":
    mcp.run()
