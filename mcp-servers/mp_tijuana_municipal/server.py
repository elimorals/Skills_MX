"""MCP server mp_tijuana_municipal."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_tijuana_municipal.client import TijuanaMunClient  # noqa: E402
from shared.errors import McpError  # noqa: E402

mcp = FastMCP("tijuana_mun_mcp")
_client = TijuanaMunClient()


@mcp.tool(annotations={"title": "Predial Tijuana (handoff: requiere login)", "readOnlyHint": True, "openWorldHint": True})
def tijuana_mun_consultar_predial(clave_catastral: str) -> dict:
    """Predial Tijuana. El portal exige cuenta del contribuyente: devuelve pasos para una persona."""
    return _client.consultar_predial(clave_catastral)


@mcp.tool(annotations={"title": "Vivienda asegurada Tijuana (Protección Ciudadana)", "readOnlyHint": True, "openWorldHint": True})
def tijuana_mun_consultar_vivienda_asegurada(clave_catastral: str) -> dict:
    """¿La vivienda con esa clave catastral está asegurada por el Programa de Protección Ciudadana?"""
    try:
        return _client.consultar_vivienda_asegurada(clave_catastral)
    except McpError as exc:
        return exc.to_dict()


if __name__ == "__main__":
    mcp.run()
