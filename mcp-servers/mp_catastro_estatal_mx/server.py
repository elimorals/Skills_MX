"""mp_catastro_estatal_mx — MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_catastro_estatal_mx.client import CatastroEstatalClient  # noqa: E402


mcp = FastMCP("catastro_estatal_mx")
_client = CatastroEstatalClient()


class ConsultarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sistema: str = Field(..., min_length=3, max_length=30,
                          description="igecem, ircep, catastro_ver, catastro_qroo, catastro_yuc")
    cuenta_catastral: str = Field(..., min_length=6, max_length=20)


@mcp.tool(annotations={"title": "Consultar valor catastral", "readOnlyHint": True, "openWorldHint": True})
def catastro_consultar_valor(args: ConsultarInput) -> dict:
    """Consulta valor catastral + superficie + uso de suelo."""
    return _client.consultar_valor(args.sistema, args.cuenta_catastral)


@mcp.tool(annotations={"title": "Listar sistemas catastrales estatales", "readOnlyHint": True, "idempotentHint": True})
def catastro_listar_sistemas() -> dict:
    """Lista los catastros estatales en el catálogo."""
    return _client.listar_sistemas()


if __name__ == "__main__":
    mcp.run()
