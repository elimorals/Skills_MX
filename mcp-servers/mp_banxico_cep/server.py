"""mp_banxico_cep — Constancia de Pago Electrónico (SPEI) + CLABE.

Cierra el ciclo de conciliación bancaria: factura emitida → cliente paga SPEI →
cliente manda clave de rastreo por WhatsApp → este MCP confirma el pago con
Banxico → el flow marca el CFDI como cobrado.

7 tools:
- 3 locales (validar CLABE, decodificar CLABE, parsear clave rastreo) — siempre reales
- 3 remotos a Banxico (generar/validar/descargar CEP) — mock por default
- 1 catálogo (listar bancos CLABE)

⚠ Banxico no tiene API REST oficial. La integración real requiere Playwright.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_banxico_cep.catalogos import (  # noqa: E402
    BANCOS_CLABE,
    BANCOS_TODOS,
    ESTADO_CEP,
    OTROS_PARTICIPANTES_CLABE,
    TIPO_OPERACION_SPEI,
    lookup_banco,
)
from mp_banxico_cep.clabe import (  # noqa: E402
    parsear_clave_rastreo as _parsear_clave_rastreo,
    validar_clabe as _validar_clabe,
)
from mp_banxico_cep.client import BanxicoCepClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("banxico_cep_mcp")
_client = BanxicoCepClient()


# ---------- input models ----------


class ClabeInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    clabe: str = Field(
        ...,
        description="CLABE de 18 dígitos (con o sin espacios/guiones — se normaliza).",
        min_length=1,
        max_length=30,
    )


class ClaveRastreoInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    clave_rastreo: str = Field(
        ...,
        description="Clave de rastreo SPEI (alfanumérica, típicamente 8-40 chars).",
        min_length=1,
        max_length=50,
    )


class GenerarCepInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    clave_rastreo: str = Field(..., description="Clave de rastreo SPEI.", min_length=1)
    fecha_operacion: date = Field(
        ..., description="Fecha del SPEI en ISO 8601 (YYYY-MM-DD)."
    )
    banco_emisor: str = Field(
        ...,
        description="Código de 3 dígitos del banco emisor (ej. '012' = BBVA).",
        min_length=3,
        max_length=3,
    )
    banco_receptor: str = Field(
        ...,
        description="Código de 3 dígitos del banco receptor.",
        min_length=3,
        max_length=3,
    )
    monto: float = Field(..., description="Monto exacto del SPEI.", gt=0)


class CodigoBancoInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    codigo: str = Field(
        ...,
        description="Código de banco de 3 dígitos.",
        min_length=1,
        max_length=3,
    )


# ---------- tools: locales (siempre reales) ----------


@mcp.tool(
    name="banxico_cep_validar_clabe",
    annotations={
        "title": "Validar CLABE (18 dígitos + dígito control)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def banxico_cep_validar_clabe(params: ClabeInput) -> dict:
    """Valida una CLABE (Clave Bancaria Estandarizada) completa.

    Verifica:
    - 18 dígitos numéricos
    - Código de banco contra el catálogo
    - Dígito de control con algoritmo Banxico (pesos cíclicos 3,7,1)

    Devuelve componentes decodificados: banco_codigo, banco_nombre,
    plaza_codigo, cuenta_interna, dígito de control provisto vs calculado.

    100% local, sin red. Usa esto ANTES de pedir un SPEI para evitar dineros
    perdidos por CLABEs mal capturadas.
    """
    return _validar_clabe(params.clabe)


@mcp.tool(
    name="banxico_cep_decodificar_clabe",
    annotations={
        "title": "Extraer banco y plaza de una CLABE",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def banxico_cep_decodificar_clabe(params: ClabeInput) -> dict:
    """Decodifica los 3 primeros campos de una CLABE: banco, plaza, cuenta.

    Si la CLABE es estructuralmente inválida (longitud, dígito), devuelve
    error pero igual presenta los componentes parseados para debug.
    """
    r = _validar_clabe(params.clabe)
    return {
        "clabe_normalizada": r["clabe_normalizada"],
        "banco_codigo": r["banco_codigo"],
        "banco_nombre": r["banco_nombre"],
        "plaza_codigo": r["plaza_codigo"],
        "cuenta_interna": r["cuenta_interna"],
        "valida": r["valida"],
        "errores": r["errores"],
        "alertas": r["alertas"],
    }


@mcp.tool(
    name="banxico_cep_parsear_clave_rastreo",
    annotations={
        "title": "Parsear clave de rastreo SPEI",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def banxico_cep_parsear_clave_rastreo(params: ClaveRastreoInput) -> dict:
    """Identifica heurísticamente el banco emisor por el prefijo de la clave.

    Cada banco define su formato (BBVA=MBAN..., Banamex=BNET..., MP=MERPAGO...).
    Este parseo es solo informativo — NO confirma que el SPEI existe. Para eso
    llama a `banxico_cep_validar_cep` o `banxico_cep_generar_cep`.
    """
    return _parsear_clave_rastreo(params.clave_rastreo)


@mcp.tool(
    name="banxico_cep_lookup_banco",
    annotations={
        "title": "Buscar banco por su código de 3 dígitos",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def banxico_cep_lookup_banco(params: CodigoBancoInput) -> dict:
    """Devuelve el nombre del banco asociado a un código (ej. '012' → BBVA)."""
    nombre = lookup_banco(params.codigo)
    if nombre is None:
        return {
            "codigo": params.codigo,
            "nombre": None,
            "error": (
                f"Código '{params.codigo}' no está en el catálogo de bancos. "
                "Puede ser fintech nueva o código inválido."
            ),
        }
    return {"codigo": params.codigo.zfill(3), "nombre": nombre}


# ---------- tools: remotos a Banxico (mock por default) ----------


@mcp.tool(
    name="banxico_cep_generar_cep",
    annotations={
        "title": "Generar Constancia de Pago Electrónico (CEP)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_cep_generar_cep(params: GenerarCepInput) -> dict:
    """Solicita el CEP a Banxico con los datos del SPEI.

    Devuelve el documento oficial: hora exacta, ordenante, beneficiario,
    cuentas enmascaradas, monto, concepto, referencia, y URL del PDF.

    Caso de uso: confirmar que un cliente pagó la factura por SPEI con monto
    y fecha exactos antes de marcar el CFDI como cobrado.

    Cache 90 días — los SPEI ya liquidados no cambian.

    ⚠ Modo mock por default. Real requiere Playwright (TODO).
    """
    try:
        return await _client.generar_cep(
            clave_rastreo=params.clave_rastreo,
            fecha_operacion=params.fecha_operacion,
            banco_emisor=params.banco_emisor,
            banco_receptor=params.banco_receptor,
            monto=params.monto,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="banxico_cep_validar_cep",
    annotations={
        "title": "Verificar si un CEP existe (sin generar PDF)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_cep_validar_cep(params: ClaveRastreoInput) -> dict:
    """Check liviano de existencia: ¿hay CEP para esta clave?

    Más barato que `generar_cep` cuando solo necesitas yes/no. Cache 30 días.
    """
    try:
        return await _client.validar_cep(params.clave_rastreo)
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="banxico_cep_descargar_pdf",
    annotations={
        "title": "Descargar PDF oficial del CEP",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_cep_descargar_pdf(params: GenerarCepInput) -> dict:
    """Descarga el PDF firmado oficialmente por Banxico.

    Mismo input que `generar_cep`. En mock devuelve metadata con path simulado.
    """
    try:
        return await _client.descargar_pdf_cep(
            clave_rastreo=params.clave_rastreo,
            fecha_operacion=params.fecha_operacion,
            banco_emisor=params.banco_emisor,
            banco_receptor=params.banco_receptor,
            monto=params.monto,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="banxico_cep_consultar_pago_por_clave",
    annotations={
        "title": "Consulta rápida con solo clave de rastreo",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_cep_consultar_pago_por_clave(params: ClaveRastreoInput) -> dict:
    """Variante simplificada cuando solo tienes la clave de rastreo.

    En mock infiere datos plausibles desde la clave. En real, Banxico exige
    todos los campos (fecha + bancos + monto) — esta función devolverá
    `validation_error` indicando qué falta recopilar del cliente.
    """
    try:
        return await _client.consultar_pago_por_clave(params.clave_rastreo)
    except McpError as err:
        return err.to_dict()


# ---------- catálogos ----------


@mcp.tool(
    name="banxico_cep_listar_bancos",
    annotations={
        "title": "Listar bancos con sus códigos CLABE",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def banxico_cep_listar_bancos() -> dict:
    """Catálogo de bancos + casas de bolsa + fintechs con sus 3 dígitos CLABE.

    Útil para validar contra qué banco pertenece una CLABE o el código que
    aparece en un CEP.
    """
    return {
        "bancos_banca_multiple": BANCOS_CLABE,
        "otros_participantes": OTROS_PARTICIPANTES_CLABE,
        "todos": BANCOS_TODOS,
        "total": len(BANCOS_TODOS),
    }


@mcp.tool(
    name="banxico_cep_listar_catalogos",
    annotations={
        "title": "Catálogos: tipos operación SPEI, estados CEP",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def banxico_cep_listar_catalogos() -> dict:
    """Discovery offline de tipos de operación SPEI y estados de CEP."""
    return {
        "tipo_operacion_spei": TIPO_OPERACION_SPEI,
        "estado_cep": ESTADO_CEP,
        "nota": (
            "Bancos en banxico_cep_listar_bancos. Los códigos CLABE son estables "
            "desde 1996 pero fintechs nuevas se añaden periódicamente."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
