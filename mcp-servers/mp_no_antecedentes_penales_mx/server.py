"""mp_no_antecedentes_penales_mx — MCP standalone."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient  # noqa: E402


mcp = FastMCP("no_antecedentes_penales_mx")
_client = NoAntecedentesClient()


class VerificarConstanciaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    curp: str = Field(..., min_length=18, max_length=18)
    folio: str = Field(..., min_length=4, max_length=50)
    entidad: str = Field(..., pattern="^(cdmx|edomex|CDMX|EdoMex|EDOMEX)$")


class VerificarAptoInput(VerificarConstanciaInput):
    pass


@mcp.tool(annotations={"title": "Verificar constancia no antecedentes (CDMX/EdoMex)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
def noantecedentes_verificar_constancia(args: VerificarConstanciaInput) -> dict:
    """Verifica que una constancia de no antecedentes sea auténtica y vigente."""
    return _client.verificar_constancia(args.curp, args.folio, args.entidad)


@mcp.tool(annotations={"title": "Verificar candidato apto para contratación", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
def noantecedentes_verificar_apto(args: VerificarAptoInput) -> dict:
    """Decisión binaria RRHH: ¿este candidato es apto para contratar?

    Devuelve apto_para_contratacion: bool + razón legible para auditoría.
    """
    return _client.verificar_apto_contratacion(args.curp, args.folio, args.entidad)


if __name__ == "__main__":
    mcp.run()
