"""mp_predial_mx — MCP unificado para consulta predial municipal MX.

Tools expuestos:
- predial_consultar(estado, municipio, cuenta_predial, [tipo, direccion])
- predial_listar_municipios([estado], [solo_validados])
- predial_buscar_municipio(query)
- predial_estadisticas_catalogo()

Cobertura: 209 municipios en catálogo + 95 via SACPI Michoacán = 304 municipios accesibles.
Validados con URL real: 33. Cobertura poblacional validada: 31.4M (24% nacional).

Modo mock por default. Activar consultas reales con env var MP_PLAYWRIGHT_PUBLIC=1.
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

from mp_predial_mx.client import PredialMxClient  # noqa: E402


mcp = FastMCP("predial_mx_unificado")
_client = PredialMxClient()


# ============================================================
# Schemas
# ============================================================

class ConsultarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=10,
                        description="Clave estado: 'cdmx', 'jal', 'mich', 'nl', etc.")
    municipio: str = Field(..., min_length=2, max_length=80,
                           description="Clave municipio del catálogo (normalizada o nombre exacto).")
    cuenta_predial: str = Field(..., min_length=4, max_length=30,
                                description="Clave catastral del municipio.")
    tipo: str = Field("urbano", pattern="^(urbano|rustico)$",
                      description="Solo aplica para SACPI Michoacán.")
    direccion: Optional[str] = Field(None, max_length=200,
                                      description="Requerido para Mérida (busca por calle+numero).")


class ListarMunicipiosInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: Optional[str] = Field(None, description="Filtrar por estado (opcional).")
    solo_validados: bool = Field(False, description="Solo municipios con URL real verificada.")


class BuscarMunicipioInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(..., min_length=2, max_length=80, description="Texto a buscar.")


# ============================================================
# Tools
# ============================================================

@mcp.tool(annotations={
    "title": "Consultar predial municipal MX (unificado)",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def predial_consultar(args: ConsultarInput) -> dict:
    """Consulta predial unificado: cualquier municipio del catálogo central MX.

    Cobertura:
    - 33 municipios con URL + selectores DOM verificados
    - 95 municipios MICH via SACPI (plataforma estatal)
    - 209 municipios totales en catálogo (con notas para los no validados)

    Auto-routing por (estado, municipio):
    1. Si tiene plataforma_saas='SACPI' → invoca SACPI Michoacán
    2. Si tiene portal_predial_url + selectores → consulta directa via Playwright
    3. Si solo tiene URL sin selectores → fallback con selectores universales
    4. Sin URL ni SaaS → error con instrucciones

    Modo mock activo si MP_PLAYWRIGHT_PUBLIC != 1.

    Casos especiales:
    - Mérida (yuc/merida): busca por calle+numero, pasar `direccion`
    - Puebla (pue/puebla): requiere CAPTCHA — solo prepara form, no resuelve
    - SACPI MICH: pasar `tipo=urbano` o `tipo=rustico`
    """
    return _client.consultar(
        estado=args.estado,
        municipio=args.municipio,
        cuenta_predial=args.cuenta_predial,
        tipo=args.tipo,
        direccion=args.direccion,
    )


@mcp.tool(annotations={
    "title": "Listar municipios del catálogo MX",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def predial_listar_municipios(args: ListarMunicipiosInput) -> dict:
    """Lista municipios soportados en el catálogo, opcionalmente filtrados.

    Returns:
        {
          "total": N,
          "por_estado": {
            "jal": [
              {"clave": "guadalajara", "nombre": "Guadalajara", "validado": true,
               "tiene_url": true, "tiene_saas": false, "poblacion_aprox": 1385629},
              ...
            ],
            ...
          }
        }
    """
    return _client.listar_municipios(
        estado=args.estado,
        solo_validados=args.solo_validados,
    )


@mcp.tool(annotations={
    "title": "Buscar municipio en catálogo MX",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def predial_buscar_municipio(args: BuscarMunicipioInput) -> dict:
    """Búsqueda fuzzy de municipios por nombre o clave parcial.

    Ejemplos:
    - "guadal" → encuentra "guadalajara" en jal
    - "monterrey" → encuentra "monterrey" en nl
    - "iztapa" → encuentra "iztapalapa" en cdmx

    Returns:
        {"resultados": [{"estado": "jal", "clave": "guadalajara", "nombre": "Guadalajara", ...}]}
    """
    return {"resultados": _client.buscar_municipio(args.query)}


@mcp.tool(annotations={
    "title": "Estadísticas del catálogo predial MX",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def predial_estadisticas_catalogo() -> dict:
    """Devuelve cobertura del catálogo: total municipios, validados, SaaS, población.

    Útil para diagnosticar capacidad antes de armar carteras grandes.

    Returns:
        {
          "estados_cubiertos": 32,
          "municipios_totales": 209,
          "municipios_validados": 33,
          "cobertura_poblacional_aprox": 88339613,
          "saas": {
            "plataformas_validadas": 1,
            "municipios_cubiertos_via_saas": 95,
            "estados_con_saas": ["mich"]
          },
          "cobertura_efectiva": 128
        }
    """
    return _client.estadisticas_catalogo()


# ============================================================
# Entrypoint
# ============================================================

if __name__ == "__main__":
    mcp.run()
