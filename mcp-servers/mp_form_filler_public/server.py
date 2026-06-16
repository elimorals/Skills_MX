"""mp_form_filler_public MCP — autollenado formularios públicos gob.mx."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_form_filler_public.client import FormFillerPublicClient  # noqa: E402


mcp = FastMCP("form_filler_public")
_client = FormFillerPublicClient()


class ListarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sin_captcha: bool = Field(False, description="Solo formularios sin CAPTCHA.")


class ValidarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave: str = Field(..., min_length=3, max_length=40)
    datos: dict[str, str] = Field(..., min_length=1, max_length=20)


class LlenarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave: str = Field(..., min_length=3, max_length=40)
    datos: dict[str, str] = Field(..., min_length=1, max_length=20)
    screenshot: bool = Field(False, description="Adjunta screenshot base64 a la respuesta.")


@mcp.tool(annotations={"title": "Listar formularios públicos soportados", "readOnlyHint": True, "idempotentHint": True})
def form_listar_formularios(args: ListarInput) -> dict:
    return _client.listar_formularios(sin_captcha=args.sin_captcha)


@mcp.tool(annotations={"title": "Pre-flight validación inputs (local)", "readOnlyHint": True, "idempotentHint": True})
def form_validar_inputs(args: ValidarInput) -> dict:
    return _client.validar_inputs(args.clave, args.datos)


@mcp.tool(annotations={"title": "Llenar formulario público (Playwright opt-in)", "readOnlyHint": False})
def form_llenar(args: LlenarInput) -> dict:
    return _client.llenar(args.clave, args.datos, screenshot=args.screenshot)


if __name__ == "__main__":
    mcp.run()
