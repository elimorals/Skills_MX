"""mp_facturama_extendido — wrapper extendido sobre Facturama PAC API.

Cubre el flujo CFDI 4.0 completo: validación local pre-timbrado, timbrado
real o mock, cancelación con motivos 01-04, consulta de estatus, búsqueda
y descarga de XML/PDF.

Diferencia clave vs el MCP oficial Facturama: validación local rica que
atrapa los errores comunes ANTES de gastar costo PAC, con explicaciones
accionables en español.

Sin credenciales corre en modo mock con UUIDs y sellos sintéticos plausibles.
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Make sibling packages importable regardless of cwd
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_facturama_extendido.catalogos import (  # noqa: E402
    EXPORTACION,
    FORMA_PAGO,
    METODO_PAGO,
    MOTIVOS_CANCELACION,
    REGIMEN_FISCAL,
    TIPO_COMPROBANTE,
    USO_CFDI,
)
from mp_facturama_extendido.client import FacturamaClient  # noqa: E402
from mp_facturama_extendido.validator import (  # noqa: E402
    validate_cancelacion,
    validate_cfdi_payload,
)
from shared.errors import McpError  # noqa: E402


# ---------- server init ----------

mcp = FastMCP("facturama_mcp")
_client = FacturamaClient()


# ---------- enums ----------


class TipoComprobante(str, Enum):
    """Tipos de comprobante CFDI."""

    I = "I"  # Ingreso
    E = "E"  # Egreso
    T = "T"  # Traslado
    N = "N"  # Nómina
    P = "P"  # Pago


class MotivoCancelacion(str, Enum):
    """Motivos de cancelación SAT."""

    ERROR_CON_RELACION = "01"
    ERROR_SIN_RELACION = "02"
    NO_OPERACION = "03"
    OPERACION_NOMINATIVA_GLOBAL = "04"


# ---------- input models ----------


class ValidarPayloadInput(BaseModel):
    """Input para validar un payload CFDI sin timbrar."""

    model_config = ConfigDict(extra="allow")

    payload: dict[str, Any] = Field(
        ...,
        description="Payload completo del CFDI 4.0 a validar. Debe incluir "
        "emisor, receptor, comprobante (con tipo_comprobante, metodo_pago, "
        "forma_pago, exportacion), y conceptos.",
    )


class TimbrarCfdiInput(BaseModel):
    """Input para timbrar un CFDI 4.0."""

    model_config = ConfigDict(extra="allow")

    payload: dict[str, Any] = Field(
        ...,
        description="Payload completo del CFDI 4.0. Estructura mínima: "
        "{emisor: {rfc, razon_social, regimen_fiscal, cp_lugar_expedicion}, "
        "receptor: {rfc, nombre, regimen_fiscal, cp_domicilio, uso_cfdi}, "
        "comprobante: {tipo_comprobante, moneda, metodo_pago, forma_pago, exportacion}, "
        "conceptos: [{clave_prod_serv, descripcion, clave_unidad, cantidad, valor_unitario, importe, objeto_imp}]}",
    )
    skip_local_validation: bool = Field(
        default=False,
        description="Si True, omite la validación local pre-timbrado. NO recomendado "
        "para producción — la validación local atrapa el 95% de errores comunes y "
        "evita costos PAC innecesarios.",
    )


class CancelarCfdiInput(BaseModel):
    """Input para cancelar un CFDI existente."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID (folio fiscal) del CFDI a cancelar. Formato 8-4-4-4-12 hex.",
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    )
    motivo: MotivoCancelacion = Field(
        ...,
        description="Motivo de cancelación SAT: 01 (error con relación, requiere folio_sustituto), "
        "02 (error sin relación), 03 (no se llevó a cabo), 04 (operación nominativa global).",
    )
    folio_sustituto: Optional[str] = Field(
        default=None,
        description="UUID del CFDI sustituto. Obligatorio solo cuando motivo=01.",
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    )


class UuidInput(BaseModel):
    """Input genérico que solo requiere UUID."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID (folio fiscal) del CFDI.",
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    )


class BuscarCfdisInput(BaseModel):
    """Input para búsqueda de CFDIs con filtros."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    rfc_receptor: Optional[str] = Field(
        default=None,
        description="Filtrar por RFC del receptor.",
        pattern=r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$",
    )
    rfc_emisor: Optional[str] = Field(
        default=None,
        description="Filtrar por RFC del emisor.",
        pattern=r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$",
    )
    folio: Optional[str] = Field(
        default=None, description="Filtrar por folio interno del emisor."
    )
    fecha_desde: Optional[str] = Field(
        default=None,
        description="Fecha mínima ISO 'YYYY-MM-DD'.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    fecha_hasta: Optional[str] = Field(
        default=None,
        description="Fecha máxima ISO 'YYYY-MM-DD'.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    tipo: Optional[TipoComprobante] = Field(
        default=None, description="Filtrar por TipoDeComprobante (I, E, T, N, P)."
    )
    limit: int = Field(default=20, ge=1, le=100, description="Máximo de resultados.")


# ---------- tools ----------


@mcp.tool(
    name="facturama_validar_payload_local",
    annotations={
        "title": "Validar payload CFDI 4.0 localmente (sin timbrar)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def facturama_validar_payload_local(params: ValidarPayloadInput) -> dict:
    """Valida un payload CFDI 4.0 contra reglas SAT sin llamar a Facturama.

    Atrapa el 95% de errores que el PAC rechazaría:
    - RFC con formato inválido, CP faltante, régimen no existe
    - MetodoPago ↔ FormaPago inconsistente (PUE+99, PPD+específico)
    - UsoCFDI incompatible con tipo de persona del receptor
    - Totales que no cuadran (subtotal + IVA − retenciones ≠ total)
    - Fechas fuera de ±72h
    - Falta de Exportacion (obligatorio en 4.0)
    - ObjetoImp por concepto

    Returns:
        {
            "is_valid": bool,
            "errors_count": int,
            "warnings_count": int,
            "errors": [{severity, code, message, path}],
            "warnings": [{severity, code, message, path}]
        }

    Usa esta tool ANTES de timbrar para evitar gastos PAC innecesarios.
    También útil para validar payloads generados por skills sin llamar al PAC.
    """
    report = validate_cfdi_payload(params.payload)
    return report.to_dict()


@mcp.tool(
    name="facturama_timbrar_cfdi",
    annotations={
        "title": "Timbrar CFDI 4.0 (con validación local automática)",
        "readOnlyHint": False,
        "destructiveHint": False,  # crea CFDI pero no destruye nada
        "idempotentHint": False,  # cada llamada genera un UUID nuevo
        "openWorldHint": True,
    },
)
async def facturama_timbrar_cfdi(params: TimbrarCfdiInput) -> dict:
    """Timbra un CFDI 4.0 contra Facturama (sandbox o producción).

    Por default ejecuta validación local pre-timbrado para evitar costos PAC
    en payloads inválidos. Si la validación local encuentra errores, retorna
    el reporte SIN llamar a Facturama.

    En modo mock (sin FACTURAMA_USER configurado), devuelve UUID + sello
    sintéticos plausibles con `simulated: true`.

    Args:
        params (TimbrarCfdiInput):
            - payload: dict CFDI 4.0 completo
            - skip_local_validation: bool, default False

    Returns:
        Caso éxito:
        {
            "ok": true,
            "uuid": "abc-...", "fecha_timbrado": "...",
            "sello_sat": "...", "cadena_original_complemento": "...",
            "simulated": bool, "advertencias": [...]
        }

        Caso validación local falla:
        {
            "ok": false,
            "validacion_local_failed": true,
            "errors": [...],
            "warnings": [...]
        }

        Caso error PAC/red:
        {
            "error": true, "code": "...", "message": "..."
        }
    """
    # 1. Validación local (a menos que se omita explícitamente)
    if not params.skip_local_validation:
        report = validate_cfdi_payload(params.payload)
        if not report.is_valid:
            return {
                "ok": False,
                "validacion_local_failed": True,
                "errors_count": len(report.errors),
                "warnings_count": len(report.warnings),
                "errors": [
                    {"severity": e.severity, "code": e.code, "message": e.message, "path": e.path}
                    for e in report.errors
                ],
                "warnings": [
                    {"severity": w.severity, "code": w.code, "message": w.message, "path": w.path}
                    for w in report.warnings
                ],
                "advertencias": ["Pre-validación local falló. NO se llamó al PAC para evitar costos."],
            }

    # 2. Timbrado
    try:
        response = await _client.timbrar_cfdi(params.payload)
        return {"ok": True, **response}
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="facturama_cancelar_cfdi",
    annotations={
        "title": "Cancelar CFDI con motivo SAT (01-04)",
        "readOnlyHint": False,
        "destructiveHint": True,  # cancelar es destructivo
        "idempotentHint": True,  # cancelar dos veces es no-op
        "openWorldHint": True,
    },
)
async def facturama_cancelar_cfdi(params: CancelarCfdiInput) -> dict:
    """Cancela un CFDI por UUID con un motivo SAT específico.

    Motivos válidos:
    - 01: Comprobante emitido con errores con relación → requiere folio_sustituto
    - 02: Comprobante emitido con errores sin relación
    - 03: No se llevó a cabo la operación
    - 04: Operación nominativa relacionada en una factura global

    Reglas SAT 2022+:
    - Si el CFDI tiene >72h o monto >$1,000 MXN, requiere aceptación del
      receptor (proceso asíncrono vía Buzón Tributario, 3 días hábiles para
      responder; sin respuesta = aceptada).
    - Motivo 01 obliga a especificar folio_sustituto (UUID del CFDI nuevo).

    Returns:
        {
            "uuid": "...", "motivo": "01", "estatus": "...",
            "fecha_solicitud": "...", "requiere_aceptacion_receptor": bool,
            "simulated": bool
        }
    """
    # 1. Validación local
    motivo_str = params.motivo.value if isinstance(params.motivo, MotivoCancelacion) else params.motivo
    report = validate_cancelacion(params.uuid, motivo_str, params.folio_sustituto)
    if not report.is_valid:
        return {
            "ok": False,
            "validacion_local_failed": True,
            "errors": [
                {"severity": e.severity, "code": e.code, "message": e.message, "path": e.path}
                for e in report.errors
            ],
        }

    # 2. Cancelación
    try:
        result = await _client.cancelar_cfdi(params.uuid, motivo_str, params.folio_sustituto)
        return {"ok": True, **result}
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="facturama_consultar_estatus",
    annotations={
        "title": "Consultar estatus actual de un CFDI",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def facturama_consultar_estatus(params: UuidInput) -> dict:
    """Consulta el estatus actual de un CFDI: Vigente, Cancelado, En proceso.

    Cache: 15 min — evita consultas repetidas innecesarias.

    Returns:
        {"uuid": "...", "estatus": "Vigente" | "Cancelado" | "...", "consultado_en": "..."}
    """
    try:
        return await _client.consultar_estatus(params.uuid)
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="facturama_descargar_xml",
    annotations={
        "title": "Descargar XML de un CFDI por UUID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def facturama_descargar_xml(params: UuidInput) -> dict:
    """Descarga el XML completo de un CFDI timbrado.

    Returns:
        {"uuid": "...", "xml": "<?xml ...>", "size_bytes": int, "simulated": bool}
    """
    try:
        return await _client.descargar_xml(params.uuid)
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="facturama_descargar_pdf",
    annotations={
        "title": "Descargar PDF de representación impresa de un CFDI",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def facturama_descargar_pdf(params: UuidInput) -> dict:
    """Descarga el PDF de representación impresa de un CFDI timbrado.

    Returns:
        {"uuid": "...", "pdf_base64": "...", "simulated": bool}

    Decodificar con base64.b64decode() para guardar como archivo .pdf.
    """
    try:
        return await _client.descargar_pdf(params.uuid)
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="facturama_buscar_cfdis",
    annotations={
        "title": "Buscar CFDIs con filtros",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def facturama_buscar_cfdis(params: BuscarCfdisInput) -> dict:
    """Busca CFDIs por filtros: RFC receptor/emisor, folio, fechas, tipo.

    Returns:
        {"cfdis": [...], "total": int, "filtros_aplicados": {...}}
    """
    try:
        return await _client.buscar_cfdis(
            rfc_receptor=params.rfc_receptor,
            rfc_emisor=params.rfc_emisor,
            folio=params.folio,
            fecha_desde=params.fecha_desde,
            fecha_hasta=params.fecha_hasta,
            tipo=params.tipo.value if params.tipo else None,
            limit=params.limit,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="facturama_listar_catalogos",
    annotations={
        "title": "Listar catálogos SAT incluidos (UsoCFDI, FormaPago, etc.)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def facturama_listar_catalogos() -> dict:
    """Retorna los catálogos SAT que este MCP conoce.

    Útil para discovery del agente: qué claves UsoCFDI/FormaPago/etc. son
    válidas según el Anexo 20 vigente.

    ⚠ Estos catálogos pueden estar desactualizados — el SAT actualiza
    periódicamente. Validar contra el portal SAT si surge una clave dudosa.
    """
    return {
        "tipo_comprobante": TIPO_COMPROBANTE,
        "uso_cfdi": USO_CFDI,
        "forma_pago": FORMA_PAGO,
        "metodo_pago": METODO_PAGO,
        "regimen_fiscal": REGIMEN_FISCAL,
        "exportacion": EXPORTACION,
        "motivos_cancelacion": MOTIVOS_CANCELACION,
        "advertencia_vigencia": (
            "Catálogos extraídos al momento del training del modelo. "
            "Verificar contra el portal SAT (https://www.sat.gob.mx) antes de uso productivo."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
