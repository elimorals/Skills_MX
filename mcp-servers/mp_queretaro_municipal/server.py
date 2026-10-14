"""MCP server mp_queretaro_municipal."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_queretaro_municipal.client import QueretaroMunClient  # noqa: E402
from shared.errors import McpError  # noqa: E402

mcp = FastMCP("queretaro_mun_mcp")
_client = QueretaroMunClient()


@mcp.tool(annotations={"title": "Predial municipio de Querétaro", "readOnlyHint": True, "openWorldHint": True})
def queretaro_mun_consultar_predial(clave_catastral: str, letras_propietario: str) -> dict:
    """Adeudo de predial del municipio de Querétaro (portal consultaLC v2).

    clave_catastral: 15 dígitos. letras_propietario: 4 letras del nombre del
    propietario, que el portal valida antes de mostrar el adeudo.
    """
    try:
        return _client.consultar_predial(clave_catastral, letras_propietario)
    except McpError as exc:
        return exc.to_dict()


if __name__ == "__main__":
    mcp.run()
