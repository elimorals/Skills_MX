"""mp_buro_credito_personal — MCP para Buró de Crédito.

⚠ OPERACIÓN LEGALMENTE SENSIBLE. Consultar reporte de OTRA persona sin
autorización formal constituye delito. Cada tool exige `autorizacion_token`
verificable.

4 tools:
- buro_consultar_score
- buro_descargar_reporte_completo
- buro_monitorear_alertas
- buro_listar_catalogos
"""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_buro_credito_personal.catalogos import (  # noqa: E402
    MARCO_LEGAL_BURO,
    NIVELES_MONITOREO,
    RANGOS_SCORE,
    STATUS_CUENTA,
    TIPO_CONSULTA,
    TIPO_CUENTA,
)
from mp_buro_credito_personal.client import BuroCreditoClient  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.playwright_stub import info_path_real  # noqa: E402


mcp = FastMCP("buro_credito_mcp")
_client = BuroCreditoClient()


class ConsultaInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    rfc: str = Field(..., min_length=12, max_length=13)
    autorizacion_token: str = Field(
        ...,
        min_length=16,
        max_length=500,
        description=(
            "Token de autorización del TITULAR del RFC consultado. "
            "Debe provenir de firma digital, click-wrap timestamped o "
            "carta firmada con verificación OCR. SIN ESTO LA CONSULTA "
            "ES UN DELITO (Art. 32 LFPDPPP + LRSIC)."
        ),
    )

    @field_validator("rfc")
    @classmethod
    def _norm(cls, v: str) -> str:
        return v.strip().upper()


@mcp.tool(
    annotations={
        "title": "⚠ Consultar score Buró (requiere autorización titular)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def buro_consultar_score(args: ConsultaInput) -> dict:
    """Score actual + categoría + tendencia 3 meses + factores.

    REQUIERE autorización formal del titular. Sin token de autorización
    válido, la consulta falla por compliance.
    """
    try:
        return _client.consultar_score(args.rfc, args.autorizacion_token)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "⚠ Reporte completo Buró (requiere autorización titular)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def buro_descargar_reporte_completo(args: ConsultaInput) -> dict:
    """Reporte completo: cuentas activas, cerradas, consultas, observaciones."""
    try:
        return _client.descargar_reporte_completo(args.rfc, args.autorizacion_token)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "⚠ Alertas de monitoreo recientes (requiere autorización)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def buro_monitorear_alertas(args: ConsultaInput) -> dict:
    """Alertas de los últimos 30 días: consultas terceros, cambios status, etc."""
    try:
        return _client.monitorear_alertas(args.rfc, args.autorizacion_token)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Catálogos Buró + marco legal",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def buro_listar_catalogos() -> dict:
    """Discovery offline + información del marco legal (LRSIC + LFPDPPP)."""
    return {
        "rangos_score": RANGOS_SCORE,
        "tipo_cuenta": TIPO_CUENTA,
        "status_cuenta": STATUS_CUENTA,
        "tipo_consulta": TIPO_CONSULTA,
        "niveles_monitoreo": NIVELES_MONITOREO,
        "marco_legal": MARCO_LEGAL_BURO,
        "path_real_info": info_path_real(),
        "advertencia_critica": (
            "Consultar Buró de OTRA persona sin autorización formal es DELITO. "
            "Multas $50k a $5M MXN + responsabilidad penal."
        ),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
