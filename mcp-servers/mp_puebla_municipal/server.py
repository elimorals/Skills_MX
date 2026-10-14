"""MCP server mp_puebla_municipal."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_puebla_municipal.client import PueblaMunClient  # noqa: E402

mcp = FastMCP("puebla_mun_mcp")
_client = PueblaMunClient()


@mcp.tool(annotations={"title": "Predial Puebla (CAPTCHA: handoff o solver opt-in)", "readOnlyHint": True, "openWorldHint": True})
def puebla_mun_consultar_predial(cuenta_predial: str, delegacion: str = "", tipo: str = "PU") -> dict:
    """Predial Puebla capital. `cuenta_predial`: cuenta de 7 dígitos (con `delegacion` de 2) o línea
    de captura de 24 dígitos; `tipo` PU (urbano) o PR (rústico). El portal exige CAPTCHA: con
    PLUGINS_MX_CAPTCHA_SOLVER=2captcha consulta de verdad; si no, devuelve pasos para una persona."""
    return _client.consultar_predial(cuenta_predial, delegacion=delegacion, tipo=tipo)


if __name__ == "__main__":
    mcp.run()
