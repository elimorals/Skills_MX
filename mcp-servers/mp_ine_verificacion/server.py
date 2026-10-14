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
    modelo: str = Field(..., min_length=1, max_length=1, description="Modelo de credencial A-J")
    autorizacion_token: str = Field(..., min_length=16, description="Token de autorización del titular")
    cic: str | None = Field(None, description="9 dígitos (modelos D-J)")
    id_ciudadano: str | None = Field(None, description="9 dígitos (modelos E-J)")
    ocr: str | None = Field(None, description="13 dígitos (modelos A-D)")
    clave_elector: str | None = Field(None, description="18 caracteres (modelos A-C)")
    numero_emision: str | None = Field(None, description="2 dígitos (modelos A-C)")


class QRInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    qr_payload: str = Field(..., min_length=32)


class VigenciaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    modelo: str = Field(..., min_length=1, max_length=1)
    anio_emision: int = Field(..., ge=1990, le=2100)


class AutorizacionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    curp: str = Field(..., min_length=18, max_length=18)
    proposito: str = Field(..., min_length=10)
    vigencia_dias: int = Field(90, ge=1, le=365)


@mcp.tool(annotations={"title": "Verificar credencial INE (reCAPTCHA; solver opt-in)", "readOnlyHint": True})
def ine_verificar_datos(args: VerifInput) -> dict:
    return _client.verificar_datos(
        modelo=args.modelo, autorizacion_token=args.autorizacion_token,
        cic=args.cic, id_ciudadano=args.id_ciudadano, ocr=args.ocr,
        clave_elector=args.clave_elector, numero_emision=args.numero_emision,
    )


@mcp.tool(annotations={"title": "Verificar QR alta densidad INE", "readOnlyHint": True})
def ine_verificar_qr(args: QRInput) -> dict:
    return _client.verificar_qr(qr_payload=args.qr_payload)


@mcp.tool(annotations={"title": "Consultar vigencia INE", "readOnlyHint": True})
def ine_consultar_vigencia(args: VigenciaInput) -> dict:
    return _client.consultar_vigencia(modelo=args.modelo, anio_emision=args.anio_emision)


@mcp.tool(annotations={"title": "Plantilla de autorización del titular", "readOnlyHint": True})
def ine_generar_autorizacion(args: AutorizacionInput) -> dict:
    return _client.generar_autorizacion(curp=args.curp, proposito=args.proposito,
                                          vigencia_dias=args.vigencia_dias)


@mcp.tool(annotations={"title": "Listar modelos credencial INE", "readOnlyHint": True, "idempotentHint": True})
def ine_listar_modelos() -> dict:
    return _client.listar_modelos_credencial()


if __name__ == "__main__":
    mcp.run()
