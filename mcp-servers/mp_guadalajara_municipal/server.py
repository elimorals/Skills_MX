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


@mcp.tool(annotations={"title": "Predial Guadalajara (reCAPTCHA: solver opt-in o handoff)", "readOnlyHint": True, "openWorldHint": True})
def guadalajara_mun_consultar_predial(cuenta_predial: str, recaudadora: str | None = None, tipo: str | None = None) -> dict:
    """Predial Guadalajara (cuenta de 6 dígitos, recaudadora 1-4, tipo U/R).

    Con solver de CAPTCHA opt-in y recaudadora+tipo consulta el adeudo; si no, devuelve
    pasos para que una persona consulte."""
    return _client.consultar_predial(cuenta_predial, recaudadora, tipo)


@mcp.tool(annotations={"title": "Adeudos vehiculares Jalisco (reCAPTCHA: solver opt-in o handoff)", "readOnlyHint": True, "openWorldHint": True})
def guadalajara_mun_consultar_multas(placa: str, numero_serie: str | None = None,
                                     nombre_propietario: str | None = None,
                                     numero_motor: str | None = None) -> dict:
    """Adeudos vehiculares estatales de Jalisco (datos tal cual la tarjeta de circulación).

    Con solver de CAPTCHA opt-in y al menos 5 caracteres de serie consulta el portal;
    si no, devuelve pasos para una persona."""
    return _client.consultar_adeudos_vehiculares(placa, numero_serie, nombre_propietario, numero_motor)


if __name__ == "__main__":
    mcp.run()
