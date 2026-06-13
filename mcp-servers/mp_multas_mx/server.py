"""mp_multas_mx — MCP unificado para multas vehiculares estatales MX.

Tools:
- multas_consultar(estado, placa)
- multas_estados_disponibles()

Cobertura: 8 estados (cdmx, nl, jal, yuc, bc, pue, qro, edomex).
CDMX requiere CAPTCHA (humano-en-loop).

Modo mock por default. Activar real con MP_PLAYWRIGHT_PUBLIC=1.
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
    """Consulta multas pendientes para una placa en un estado.

    Cobertura: CDMX, NL, JAL, YUC, BC, PUE, QRO, EdoMex.

    ⚠ CDMX requiere CAPTCHA reCAPTCHA Enterprise — devuelve {status: "requiere_humano"}
    con URL para que el usuario complete manualmente.

    Otros estados: consulta automatizada via Playwright cuando MP_PLAYWRIGHT_PUBLIC=1.

    Returns:
        {
          "estado": "jal",
          "placa_hash": "ABC***",
          "estatus": "al_corriente" | "con_multas" | "requiere_humano",
          "total_multas_pendientes": N,
          "adeudo_total_mxn": float,
          "multas": [{folio, fecha, motivo, monto_mxn}],
          ...
        }
    """
    return _client.consultar_multas(estado=args.estado, placa=args.placa)


@mcp.tool(annotations={
    "title": "Estados con multas disponibles",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def multas_estados_disponibles() -> dict:
    """Lista estados con multas vehiculares consultables + cuáles requieren CAPTCHA.

    Returns:
        {
          "soportados": ["cdmx", "nl", "jal", ...],
          "total": 8,
          "requieren_captcha": ["cdmx"],
          "notas_por_estado": {...}
        }
    """
    return _client.estados_disponibles()


if __name__ == "__main__":
    mcp.run()
