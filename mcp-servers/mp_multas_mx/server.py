"""mp_multas_mx — MCP unificado para multas vehiculares estatales MX.

Tools:
- multas_consultar(estado, placa)
- multas_estados_disponibles()

Cobertura (2026-10-14): cdmx, edomex, jal, nl, nl_sanpedro. Todos los portales
vigentes exigen CAPTCHA o consulta manual → handoff humano verificado.
Mock solo con PLUGINS_MX_MOCK=1.
"""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_multas_mx.client import MultasMxClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("multas_mx_unificado")
_client = MultasMxClient()


class ConsultarMultasInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=10,
                        description="Clave estado: cdmx, nl, jal, yuc, bc, pue, qro, edomex.")
    placa: str = Field(..., min_length=5, max_length=12,
                       description="Placa vehicular formato MX (ej. ABC-12-34 o ABC1234).")


@mcp.tool(annotations={
    "title": "Consultar multas vehiculares por estado",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def multas_consultar(args: ConsultarMultasInput) -> dict:
    """Multas por placa: GET real al portal oficial + handoff humano (CAPTCHA).

    Returns: {"status": "requiere_humano", "url_consulta_manual", "pasos", "portal_verificado", ...}
    o {"error": true, "code": "upstream_error"} si el portal está caído o cambió.
    """
    try:
        return _client.consultar_multas(estado=args.estado, placa=args.placa)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={
    "title": "Estados con multas disponibles",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def multas_estados_disponibles() -> dict:
    """Estados con portal de multas verificado, cuáles exigen CAPTCHA y los retirados."""
    return _client.estados_disponibles()


if __name__ == "__main__":
    mcp.run()
