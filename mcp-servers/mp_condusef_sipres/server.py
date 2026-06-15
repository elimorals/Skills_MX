"""mp_condusef_sipres — MCP standalone para CONDUSEF SIPRES.

Tools:
- sipres_buscar_institucion(nombre, [sector, estado, estatus, limite])
- sipres_verificar_autorizada(nombre)  — decisión binaria KYC institucional

Portal: https://webapps.condusef.gob.mx/SIPRES/jsp/pub/index.jsp
Backend: POST /SIPRES/jsp/pub/resulbusq.jsp
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

from mp_condusef_sipres.client import (  # noqa: E402
    DEFAULT_LIMITE,
    MAX_LIMITE,
    CondusefSipresClient,
)


mcp = FastMCP("condusef_sipres")
_client = CondusefSipresClient()


class BuscarInstitucionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str = Field(
        "",
        max_length=200,
        description="Nombre o denominación social. Ej. 'BANORTE', 'BBVA'.",
    )
    sector: str = Field(
        "",
        max_length=200,
        description="Sector. Ej. 'Instituciones de banca múltiple', 'SOFOM E.R.', 'IFPE'.",
    )
    estado: str = Field(
        "",
        max_length=100,
        description="Entidad federativa del domicilio. Ej. 'Ciudad de México'.",
    )
    estatus: str = Field(
        "",
        max_length=100,
        description="Filtro de status. Ej. 'En operación', 'Cancelado', 'Suspendido'.",
    )
    limite: int = Field(
        DEFAULT_LIMITE,
        ge=1,
        le=MAX_LIMITE,
        description=f"Máx resultados (1-{MAX_LIMITE}).",
    )


class VerificarAutorizadaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre comercial o razón social de la institución a verificar.",
    )


@mcp.tool(annotations={
    "title": "Buscar institución financiera en SIPRES",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def sipres_buscar_institucion(args: BuscarInstitucionInput) -> dict:
    """Busca entidades financieras autorizadas en el padrón CONDUSEF.

    Útil para KYC institucional, validación fintech, due-diligence aseguradoras.

    Returns:
        {
          "filtros": {...},
          "total_padron": int,
          "devueltos": int,
          "resultados": [
            {
              "clave_registro": "40165",
              "denominacion": "Banco Bineo, S.A., Institución de Banca Múltiple...",
              "nombre_corto": "BANCO BINEO",
              "estatus": "En operación",
              "sector": "Instituciones de banca múltiple",
              "estado": "Ciudad de México",
              "idins": "16316"
            }
          ]
        }
    """
    return _client.buscar_institucion(
        nombre=args.nombre,
        sector=args.sector,
        estado=args.estado,
        estatus=args.estatus,
        limite=args.limite,
    )


@mcp.tool(annotations={
    "title": "Verificar autorización CONDUSEF (KYC institucional)",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def sipres_verificar_autorizada(args: VerificarAutorizadaInput) -> dict:
    """Decisión binaria para KYC institucional / due-diligence fintech.

    ¿Esta institución financiera está autorizada y en operación según CONDUSEF?

    Returns:
        {
          "nombre_buscado": str,
          "encontrada": bool,
          "autorizada_en_operacion": bool,
          "coincidencias": int,
          "mejor_match": {...EntidadSIPRES...} | null,
          "advertencias": [str]
        }

    SIPRES NO incluye sancionadas/canceladas — si no aparece, NO significa
    automáticamente que sea fraudulenta. Validar también con CNBV/CNSF/CONSAR
    según el sector.
    """
    return _client.verificar_autorizada(args.nombre)


if __name__ == "__main__":
    mcp.run()
