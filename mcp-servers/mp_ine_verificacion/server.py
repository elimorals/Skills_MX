"""mp_ine_verificacion MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_ine_verificacion.client import INEVerificacionClient  # noqa: E402


mcp = FastMCP("ine_verificacion")
_client = INEVerificacionClient()


class VerifInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cic: str = Field(..., min_length=13, max_length=13)
    clave_elector: str = Field(..., min_length=18, max_length=18)
    anio_emision: int = Field(..., ge=2008, le=2099)
    autorizacion_token: str = Field(..., min_length=16, description="Token autorización titular LFPDPPP")


class QRInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    qr_payload: str = Field(..., min_length=32)


class VigenciaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cic: str = Field(..., min_length=13, max_length=13)
    autorizacion_token: str = Field(..., min_length=16)


class AutorizacionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    curp: str = Field(..., min_length=18, max_length=18)
    proposito: str = Field(..., min_length=10)
    vigencia_dias: int = Field(90, ge=1, le=365)


@mcp.tool(annotations={"title": "Verificar datos INE", "readOnlyHint": True})
def ine_verificar_datos(args: VerifInput) -> dict:
    return _client.verificar_datos(
        cic=args.cic, clave_elector=args.clave_elector,
        anio_emision=args.anio_emision, autorizacion_token=args.autorizacion_token,
    )


@mcp.tool(annotations={"title": "Verificar QR alta densidad INE", "readOnlyHint": True})
def ine_verificar_qr(args: QRInput) -> dict:
    return _client.verificar_qr(qr_payload=args.qr_payload)


@mcp.tool(annotations={"title": "Consultar vigencia INE", "readOnlyHint": True})
def ine_consultar_vigencia(args: VigenciaInput) -> dict:
    return _client.consultar_vigencia(cic=args.cic, autorizacion_token=args.autorizacion_token)


@mcp.tool(annotations={"title": "Generar autorización LFPDPPP", "readOnlyHint": True})
def ine_generar_autorizacion(args: AutorizacionInput) -> dict:
    return _client.generar_autorizacion(curp=args.curp, proposito=args.proposito,
                                          vigencia_dias=args.vigencia_dias)


@mcp.tool(annotations={"title": "Listar modelos credencial INE", "readOnlyHint": True, "idempotentHint": True})
def ine_listar_modelos() -> dict:
    return _client.listar_modelos_credencial()


if __name__ == "__main__":
    mcp.run()
