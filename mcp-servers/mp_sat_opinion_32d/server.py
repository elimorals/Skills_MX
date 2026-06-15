"""mp_sat_opinion_32d — MCP standalone para SAT Opinión 32-D Pública.

Tools:
- sat_opinion_32d_consultar(rfc, [curp, incluir_pdf])  — consulta full con PDF
- sat_opinion_32d_verificar_proveedor(rfc)             — decisión binaria B2B/B2G

Portal: https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico
Endpoint backend descubierto con Playwright MCP el 2026-06-14:
    POST /ConsultaPublico/Index (multipart FormData)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_sat_opinion_32d.client import SatOpinion32DClient  # noqa: E402


mcp = FastMCP("sat_opinion_32d")
_client = SatOpinion32DClient()


class ConsultarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(
        "",
        max_length=13,
        description="RFC del contribuyente (12 chars PM o 13 chars PF). Opcional si se da CURP.",
    )
    curp: str = Field(
        "",
        max_length=18,
        description="CURP del contribuyente (18 chars). Solo PF. Opcional si se da RFC.",
    )
    incluir_pdf: bool = Field(
        True,
        description="Si False, omite el PDF base64 firmado por SAT (respuesta más liviana).",
    )


class VerificarProveedorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(
        ...,
        min_length=12,
        max_length=13,
        description="RFC del proveedor a verificar (12 o 13 chars).",
    )


@mcp.tool(annotations={
    "title": "Consultar SAT Opinión 32-D pública",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def sat_opinion_32d_consultar(args: ConsultarInput) -> dict:
    """Consulta cumplimiento de obligaciones fiscales del contribuyente ante el SAT.

    Returns:
        {
          "rfc": str, "curp": str,
          "estado": "positiva" | "negativa" | "no_autorizado" | "no_inscrito" | "error",
          "puede_contratar_con_gobierno": bool,
          "mensaje_oficial": str (mensaje literal del SAT),
          "pdf_base64": str | None (PDF firmado por SAT, ~3KB),
          "fecha_consulta": ISO-8601 UTC,
          "fuente": URL del endpoint,
        }

    Solo aparece el resultado si el contribuyente AUTORIZÓ publicación pública en
    su Buzón Tributario. Caso contrario, estado = "no_autorizado".
    """
    return _client.consultar(
        rfc=args.rfc,
        curp=args.curp,
        incluir_pdf=args.incluir_pdf,
    )


@mcp.tool(annotations={
    "title": "Verificar proveedor (compliance Art. 32-D CFF)",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def sat_opinion_32d_verificar_proveedor(args: VerificarProveedorInput) -> dict:
    """Decisión binaria de due-diligence B2B/B2G antes de firmar contrato.

    Returns:
        {
          "rfc": str,
          "puede_contratar_con_gobierno": bool,
          "estado": str,
          "advertencias": [str],
          "detalle": {...consulta completa sin PDF...}
        }

    Si puede_contratar_con_gobierno=False: NO firmar contrato.
    El Art. 32-D del Código Fiscal de la Federación impide contratar a quien
    tenga adeudos fiscales con la APF (administración pública federal).
    """
    return _client.verificar_proveedor(args.rfc)


if __name__ == "__main__":
    mcp.run()
