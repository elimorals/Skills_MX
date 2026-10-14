"""MCP server mp_guadalajara_municipal."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_guadalajara_municipal.client import GuadalajaraMunClient  # noqa: E402

mcp = FastMCP("guadalajara_mun_mcp")
_client = GuadalajaraMunClient()


@mcp.tool(annotations={"title": "Predial Guadalajara (handoff: reCAPTCHA)", "readOnlyHint": True, "openWorldHint": True})
def guadalajara_mun_consultar_predial(cuenta_predial: str) -> dict:
    """Predial Guadalajara. El portal exige reCAPTCHA: devuelve pasos para que una persona consulte."""
    return _client.consultar_predial(cuenta_predial)


@mcp.tool(annotations={"title": "Adeudos vehiculares Jalisco (handoff: reCAPTCHA)", "readOnlyHint": True, "openWorldHint": True})
def guadalajara_mun_consultar_multas(placa: str) -> dict:
    """Adeudos vehiculares estatales de Jalisco. El portal exige reCAPTCHA: devuelve pasos para una persona."""
    return _client.consultar_adeudos_vehiculares(placa)


if __name__ == "__main__":
    mcp.run()
