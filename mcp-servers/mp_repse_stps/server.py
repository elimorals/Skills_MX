"""mp_repse_stps — MCP standalone para consulta REPSE STPS.

Tools:
- repse_consultar_por_razon_social(razon_social, [limite])
- repse_consultar_por_numero_registro(numero_registro)
- repse_verificar_proveedor(razon_social, [numero_registro])  — compliance B2B

Portal: https://repse.stps.gob.mx/app/ — SIN CAPTCHA funcional, automatizable 100%.

Universo: TODA empresa MX que provee servicios especializados.
Por Art. 15 LFT, cualquier contratante DEBE validar REPSE del proveedor o
se vuelve responsable solidario laboral y fiscal.
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

from mp_repse_stps.client import RepseStpsClient  # noqa: E402


mcp = FastMCP("repse_stps")
_client = RepseStpsClient()


class ConsultarPorRazonSocialInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    razon_social: str = Field(..., min_length=3, max_length=200,
                              description="Nombre o razón social (mín 3 chars).")
    limite: int = Field(20, ge=1, le=100,
                        description="Máx resultados a devolver (1-100).")


class ConsultarPorNumeroInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    numero_registro: str = Field(..., min_length=4, max_length=7,
                                 pattern=r"^\d+$",
                                 description="Número de registro REPSE (4-7 dígitos).")


class VerificarProveedorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    razon_social: str = Field(..., min_length=3, max_length=200,
                              description="Razón social del proveedor.")
    numero_registro: Optional[str] = Field(None, min_length=4, max_length=7,
                                            pattern=r"^\d+$",
                                            description="Si lo conoces, acelera la consulta.")


@mcp.tool(annotations={
    "title": "Buscar empresa en REPSE por razón social",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def repse_consultar_por_razon_social(args: ConsultarPorRazonSocialInput) -> dict:
    """Busca empresas en REPSE por nombre o razón social (fuzzy)."""
    return _client.consultar_por_razon_social(
        razon_social=args.razon_social,
        limite=args.limite,
    )


@mcp.tool(annotations={
    "title": "Consultar detalle por número de registro REPSE",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def repse_consultar_por_numero_registro(args: ConsultarPorNumeroInput) -> dict:
    """Devuelve detalle completo del registro REPSE: vigencia, servicios autorizados."""
    return _client.consultar_por_numero_registro(args.numero_registro)


@mcp.tool(annotations={
    "title": "Verificar proveedor REPSE (compliance Art. 15 LFT)",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def repse_verificar_proveedor(args: VerificarProveedorInput) -> dict:
    """Compliance B2B: ¿este proveedor puede prestar servicios especializados legalmente?

    Cumple Art. 15 LFT (reforma 2021). Si contratas a proveedor SIN REPSE vigente,
    te vuelves RESPONSABLE SOLIDARIO laboral y fiscal de sus trabajadores.

    Returns:
        {
          "razon_social": str,
          "numero_registro": str | null,
          "registrado": bool,
          "vigente": bool,
          "puede_contratar_servicios_especializados": bool,
          "advertencias": [...],
          "detalle": {...}
        }

    Si puede_contratar_servicios_especializados=False: NO firmar contrato de
    servicios especializados — riesgo de responsabilidad solidaria masiva.
    """
    return _client.verificar_proveedor(
        razon_social=args.razon_social,
        numero_registro=args.numero_registro,
    )


if __name__ == "__main__":
    mcp.run()
