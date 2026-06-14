"""mp_cnbv_fintech — MCP padrón ITF Ley Fintech CNBV.

Tools:
- cnbv_fintech_consultar_itf(rfc | nombre)
- cnbv_fintech_listar_ifpe()
- cnbv_fintech_listar_ifc()
- cnbv_fintech_listar_modelos_novedosos()
- cnbv_fintech_verificar_contraparte(rfc, tipo_operacion)

⚠ Validación Playwright MCP 2026-06-14:
- Portal cnbv.gob.mx/SECTORES-SUPERVISADOS/Fintech/ → redirige a landing genérica gob.mx
- Portafolio de Información: `portafolioinfo.cnbv.gob.mx` requiere login
- Padrón ITF NO publicado como dataset descargable público
- Fuente alternativa: DOF — cada autorización ITF se publica en DOF como Oficio.
  Usar mp_dof_api para complementar.

Catálogo curado snapshot basado en autorizaciones DOF + SIPRES histórico.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_cnbv_fintech.client import CnbvFintechClient  # noqa: E402


mcp = FastMCP("cnbv_fintech")
_client = CnbvFintechClient()


class ConsultarItfInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: Optional[str] = Field(None, min_length=12, max_length=13,
                                description="RFC de la entidad (opcional si pasa nombre).")
    nombre: Optional[str] = Field(None, min_length=2, max_length=200,
                                   description="Nombre o marca comercial (opcional si pasa rfc).")


class VerificarContraparteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(..., min_length=12, max_length=13)
    tipo_operacion: Literal["fondos_pago", "crowdfunding", "cualquiera"] = Field(
        "cualquiera",
        description="Tipo de operación que se va a realizar con la contraparte.",
    )


@mcp.tool(annotations={
    "title": "Consultar ITF (Ley Fintech) por RFC o nombre",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def cnbv_fintech_consultar_itf(args: ConsultarItfInput) -> dict:
    """Verifica si una entidad es ITF autorizada bajo Ley Fintech.

    Returns: encontrada, tipo (ifpe/ifc), rfc, nombre, marca, estado, etc.
    """
    return _client.consultar_itf(rfc=args.rfc, nombre=args.nombre)


@mcp.tool(annotations={
    "title": "Listar IFPE autorizadas (Inst. Fondos Pago Electrónico)",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def cnbv_fintech_listar_ifpe() -> dict:
    """Lista IFPE autorizadas. Snapshot curado de DOF + SIPRES."""
    return _client.listar_ifpe()


@mcp.tool(annotations={
    "title": "Listar IFC autorizadas (Inst. Financiamiento Colectivo / crowdfunding)",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def cnbv_fintech_listar_ifc() -> dict:
    """Lista IFC autorizadas (crowdfunding). Snapshot curado de DOF + SIPRES."""
    return _client.listar_ifc()


@mcp.tool(annotations={
    "title": "Listar modelos novedosos (Sandbox Art. 80)",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def cnbv_fintech_listar_modelos_novedosos() -> dict:
    """Sandbox regulatorio Art. 80 Ley Fintech."""
    return _client.listar_modelos_novedosos()


@mcp.tool(annotations={
    "title": "Verificar contraparte para operación fintech",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def cnbv_fintech_verificar_contraparte(args: VerificarContraparteInput) -> dict:
    """Compliance: ¿esta contraparte puede operar legalmente el tipo de operación solicitado?

    Reglas:
    - fondos_pago → solo IFPE pueden operar
    - crowdfunding → solo IFC pueden operar
    - cualquiera → ambas valen

    Si puede_operar=False: NO firmar contrato — Art. 5 Ley Fintech (reservado solo a ITF).
    """
    return _client.verificar_contraparte(
        rfc=args.rfc, tipo_operacion=args.tipo_operacion,
    )


if __name__ == "__main__":
    mcp.run()
