"""mp_sacpi_michoacan — MCP para Sistema SACPI del Gobierno de Michoacán.

SACPI cubre 95 municipios MICH con una sola plataforma. Esta MCP la expone como
tools invocables desde Claude:

- sacpi_consultar(municipio, cuenta_predial, [tipo, apellido])
- sacpi_listar_municipios()
- sacpi_codigo_municipio(nombre)

Cobertura: 95 muns Michoacán (ACUITZIO, APATZINGAN, HIDALGO, ZACAPU, etc.).
NO incluidos (tienen portal propio): Morelia, Uruapan, Zamora, Lázaro Cárdenas, Pátzcuaro.

Modo mock por default. Activar real con MP_PLAYWRIGHT_PUBLIC=1.
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

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import McpError, ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.playwright_real import is_public_real_enabled  # noqa: E402
from shared.plataformas_saas_mx import (  # noqa: E402
    SACPI_MICHOACAN,
    SACPI_MUNICIPIOS_MICH,
    codigo_municipio_sacpi,
    consulta_sacpi,
)


mcp = FastMCP("sacpi_michoacan")
NAMESPACE = "sacpi_michoacan"
_bitacora = Bitacora(NAMESPACE)


# ============================================================
# Schemas
# ============================================================

class SacpiConsultarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    municipio: str = Field(..., min_length=2, max_length=80,
                           description="Nombre del municipio o código INEGI 3 dígitos. "
                                       "Ej: 'Ciudad Hidalgo', 'HIDALGO', '034'.")
    cuenta_predial: str = Field(..., min_length=4, max_length=30,
                                description="Clave catastral municipal.")
    tipo: str = Field("urbano", pattern="^(urbano|rustico)$",
                      description="Predial urbano o rústico.")


class SacpiCodigoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str = Field(..., min_length=2, max_length=80,
                        description="Nombre del municipio. Acepta variantes ('Ciudad Hidalgo' → 'HIDALGO').")


# ============================================================
# Tools
# ============================================================

@mcp.tool(annotations={
    "title": "Consultar predial Michoacán vía SACPI",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def sacpi_consultar(args: SacpiConsultarInput) -> dict:
    """Consulta predial vía Sistema SACPI del Gobierno de Michoacán.

    SACPI cubre 95 municipios MICH (excepto Morelia, Uruapan, Zamora,
    Lázaro Cárdenas, Pátzcuaro que tienen portal propio).

    El municipio puede pasarse como:
    - Nombre exacto: "HIDALGO", "APATZINGAN"
    - Nombre amigable: "Ciudad Hidalgo" (auto-mapea a HIDALGO)
    - Código INEGI: "034", "006"

    Tipo:
    - "urbano" → tipo SACPI "1" (default)
    - "rustico" → tipo SACPI "2"

    Returns:
        {
          "plataforma": "SACPI",
          "estado": "mich",
          "municipio_codigo": "034",
          "municipio_nombre": "HIDALGO",
          "estatus": "al_corriente"|"con_adeudo",
          "adeudo_total_mxn": float,
          "conceptos": [{concepto, monto_mxn}],
          ...
        }
    """
    # Resolver código
    if args.municipio.isdigit() and len(args.municipio) == 3:
        codigo = args.municipio
        if codigo not in SACPI_MUNICIPIOS_MICH:
            raise ValidationError(
                f"Código SACPI '{codigo}' no encontrado en lista oficial. "
                f"Códigos válidos: {list(SACPI_MUNICIPIOS_MICH.keys())[:5]}..."
            )
    else:
        codigo = codigo_municipio_sacpi(args.municipio)
        if codigo is None:
            raise ValidationError(
                f"Municipio '{args.municipio}' no está en SACPI Michoacán. "
                f"Pueden ser portal propio (Morelia, Uruapan, Zamora, etc.) o no MICH. "
                f"Lista completa: usar sacpi_listar_municipios()."
            )

    tipo_codigo = "1" if args.tipo == "urbano" else "2"

    _bitacora.log("consultar", success=True, params_summary={
        "municipio_codigo": codigo,
        "tipo": args.tipo,
        "cuenta_hash": Bitacora.hash_sensitive(args.cuenta_predial),
    })

    # Mock si Playwright real no habilitado
    if not is_public_real_enabled():
        seed = sum(ord(c) for c in args.cuenta_predial) % 100
        adeudo = (seed * 95.0) if seed > 35 else 0
        return mark_simulated({
            "plataforma": "SACPI",
            "estado": "mich",
            "municipio_codigo": codigo,
            "municipio_nombre": SACPI_MUNICIPIOS_MICH[codigo],
            "tipo": args.tipo,
            "estatus": "al_corriente" if adeudo == 0 else "con_adeudo",
            "adeudo_total_mxn": round(adeudo, 2),
            "conceptos_pendientes": max(0, (seed - 35) // 18) if adeudo > 0 else 0,
            "url_consultada": SACPI_MICHOACAN.url_consulta,
        })

    # Real
    return consulta_sacpi(codigo, args.cuenta_predial, tipo=tipo_codigo)


@mcp.tool(annotations={
    "title": "Listar municipios SACPI Michoacán",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def sacpi_listar_municipios() -> dict:
    """Lista los 95 municipios MICH cubiertos por SACPI con sus códigos INEGI.

    Returns:
        {
          "total": 95,
          "municipios": [
            {"codigo": "001", "nombre": "ACUITZIO"},
            {"codigo": "002", "nombre": "AGUILILLA"},
            ...
          ],
          "no_cubiertos_portal_propio": ["MORELIA", "URUAPAN", "ZAMORA", "LAZARO CARDENAS", "PATZCUARO"]
        }
    """
    return {
        "total": len(SACPI_MUNICIPIOS_MICH),
        "url_consulta": SACPI_MICHOACAN.url_consulta,
        "operador": SACPI_MICHOACAN.operador,
        "municipios": [
            {"codigo": codigo, "nombre": nombre}
            for codigo, nombre in sorted(SACPI_MUNICIPIOS_MICH.items())
        ],
        "no_cubiertos_portal_propio": [
            "MORELIA", "URUAPAN", "ZAMORA", "LAZARO CARDENAS", "PATZCUARO"
        ],
    }


@mcp.tool(annotations={
    "title": "Obtener código INEGI de municipio SACPI",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def sacpi_codigo_municipio(args: SacpiCodigoInput) -> dict:
    """Resuelve nombre de municipio → código INEGI 3 dígitos para SACPI.

    Útil cuando tienes el nombre pero necesitas el código para consulta.

    Ejemplos:
    - "Ciudad Hidalgo" → "034" (HIDALGO)
    - "APATZINGAN" → "006"
    - "Zamora" → None (tiene portal propio, no en SACPI)
    """
    codigo = codigo_municipio_sacpi(args.nombre)
    if codigo is None:
        return {
            "encontrado": False,
            "nombre_consultado": args.nombre,
            "razon": "No está en lista SACPI. Puede ser portal propio o no es municipio MICH.",
            "alternativas_portal_propio": ["MORELIA", "URUAPAN", "ZAMORA", "LAZARO CARDENAS", "PATZCUARO"],
        }
    return {
        "encontrado": True,
        "codigo": codigo,
        "nombre_oficial": SACPI_MUNICIPIOS_MICH[codigo],
        "url_consulta": SACPI_MICHOACAN.url_consulta,
    }


# ============================================================
# Entrypoint
# ============================================================

if __name__ == "__main__":
    mcp.run()
