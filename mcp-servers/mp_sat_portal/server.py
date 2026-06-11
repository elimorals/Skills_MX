"""mp_sat_portal — MCP para el portal SAT (verificación, listas 69/69-B, CSF, Buzón).

11 tools:
- 4 PÚBLICOS (intentan HTTP real, fallback mock):
    * sat_consultar_padron
    * sat_consultar_69b_efos
    * sat_consultar_69_incumplidos
    * sat_verificar_cfdi_uuid
- 6 con AUTH (mock por default; path real con Playwright opcional):
    * sat_descargar_csf
    * sat_descargar_buzon_tributario
    * sat_descargar_cfdi_masivo
    * sat_agendar_cita
    * sat_verificar_efirma_vigente
    * sat_descargar_acuse
- 1 de ESCRITURA (siempre simulada por seguridad):
    * sat_actualizar_obligaciones
- 1 utilitario LOCAL (validación estructural UUID, sin red):
    * sat_validar_uuid_estructura

⚠ El portal SAT cambia con frecuencia. Si los selectores rompen los tools
de auth requieren actualización del path Playwright (no incluido por default).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_sat_portal.catalogos import (  # noqa: E402
    AUTH_METHODS,
    ESTADO_69B,
    MOTIVOS_69_INCUMPLIDOS,
    STATUS_EFIRMA,
    STATUS_RFC,
    TIPOS_NOTIFICACION_BUZON,
    TIPOS_OBLIGACION,
    es_riesgo_alto_69,
    es_riesgo_alto_69b,
)
from mp_sat_portal.client import SatPortalClient  # noqa: E402
from mp_sat_portal.uuid_validator import validar_uuid as _validar_uuid  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("sat_portal_mcp")
_client = SatPortalClient()


# ---------- input models ----------


class RfcInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    rfc: str = Field(
        ...,
        description="RFC de 12 (PM) o 13 (PF) caracteres. Acepta minúsculas.",
        min_length=12,
        max_length=13,
    )

    @field_validator("rfc")
    @classmethod
    def _normalize_rfc(cls, v: str) -> str:
        return v.strip().upper()


class RfcOpcionalInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    rfc: Optional[str] = Field(
        None,
        description="RFC opcional. Si se omite, retorna conteo + muestra de la lista.",
    )

    @field_validator("rfc")
    @classmethod
    def _normalize_rfc(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().upper() if v else None


class UuidInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(
        ...,
        description="UUID (folio fiscal) de 36 chars: 8-4-4-4-12 hex.",
        min_length=1,
        max_length=50,
    )


class VerificarCfdiInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    uuid: str = Field(..., description="UUID del CFDI.", min_length=1, max_length=50)
    rfc_emisor: str = Field(..., description="RFC del emisor.", min_length=12, max_length=13)
    rfc_receptor: str = Field(..., description="RFC del receptor.", min_length=12, max_length=13)
    total: str = Field(
        ...,
        description="Total del CFDI (formato decimal; se normaliza a 6 decimales).",
    )

    @field_validator("rfc_emisor", "rfc_receptor")
    @classmethod
    def _norm_rfc(cls, v: str) -> str:
        return v.strip().upper()


class DescargaMasivaInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    rfc: str = Field(..., min_length=12, max_length=13)
    ejercicio: int = Field(..., description="Año fiscal (ej. 2026).", ge=2014, le=2100)
    mes: int = Field(..., description="Mes 1-12.", ge=1, le=12)
    tipo: Literal["emitidos", "recibidos"] = Field(
        ..., description="Tipo de CFDI a descargar."
    )

    @field_validator("rfc")
    @classmethod
    def _norm_rfc(cls, v: str) -> str:
        return v.strip().upper()


class CitaSatInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    rfc: str = Field(..., min_length=12, max_length=13)
    tipo_tramite: str = Field(
        ...,
        description="Tipo de trámite (ej. 'firma electronica', 'rfc', 'csf').",
        min_length=1,
        max_length=100,
    )
    entidad: Optional[str] = Field(None, description="Entidad federativa preferida.")

    @field_validator("rfc")
    @classmethod
    def _norm_rfc(cls, v: str) -> str:
        return v.strip().upper()


class FolioInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    folio: str = Field(..., description="Folio del acuse a descargar.", min_length=1)


class ActualizarObligacionesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    rfc: str = Field(..., min_length=12, max_length=13)
    accion: str = Field(
        ...,
        description=(
            "Acción solicitada: 'alta_obligacion', 'baja_obligacion', "
            "'cambio_regimen', 'aumento_obligaciones', 'disminucion_obligaciones'."
        ),
        min_length=1,
        max_length=100,
    )

    @field_validator("rfc")
    @classmethod
    def _norm_rfc(cls, v: str) -> str:
        return v.strip().upper()


# ---------- error helper ----------


def _wrap_errors(fn):
    """Convierte McpError a respuesta serializable y deja todo lo demás propagar."""

    async def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except McpError as exc:
            return exc.to_dict()

    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


# ---------- tools públicos ----------


@mcp.tool(
    annotations={
        "title": "Consultar RFC en padrón SAT",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sat_consultar_padron(args: RfcInput) -> dict:
    """Consulta el status del RFC en el padrón SAT (público).

    Retorna status (ACTIVO/SUSPENDIDO/CANCELADO/NO_LOCALIZADO/DESCONOCIDO),
    nombre y régimen de capital cuando aplica.

    Modo mock cuando no hay credenciales o falla la red.
    """
    try:
        return _client.consultar_padron(args.rfc)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Consultar lista 69-B (EFOS — Empresas Facturadoras de Operaciones Simuladas)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sat_consultar_69b_efos(args: RfcOpcionalInput) -> dict:
    """Consulta la lista 69-B (EFOS) del SAT.

    Sin RFC retorna conteo total + muestra. Con RFC retorna si está presente
    como PRESUNTO o DEFINITIVO (ambos riesgo alto: receptores no pueden deducir).

    Descarga ambos archivos públicos (Definitivos.csv, Presuntos.csv) con cache
    diaria. Si el endpoint público no responde, retorna mock.
    """
    try:
        result = _client.consultar_69b_efos(args.rfc)
        # Enriquecer con flag de riesgo alto si encontró
        if result.get("encontrado") and result.get("registro"):
            estado = result["registro"].get("estado_69b", "")
            result["riesgo_alto"] = es_riesgo_alto_69b(estado)
        return result
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Consultar lista 69 (incumplidos del Art. 69 CFF)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sat_consultar_69_incumplidos(args: RfcOpcionalInput) -> dict:
    """Consulta la lista 69 de incumplidos del Art. 69 del CFF.

    Distinta de la 69-B: aquí están contribuyentes con créditos firmes,
    no localizados, con sentencia, condonados, etc. La presencia en esta lista
    NO impide deducir, pero es señal de riesgo para due-diligence comercial.
    """
    try:
        result = _client.consultar_69_incumplidos(args.rfc)
        if result.get("encontrado") and result.get("registro"):
            motivo = result["registro"].get("supuesto", "")
            result["riesgo_alto"] = es_riesgo_alto_69(motivo)
        return result
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Verificar status de un CFDI por UUID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sat_verificar_cfdi_uuid(args: VerificarCfdiInput) -> dict:
    """Verifica un CFDI contra el verificador público SAT.

    Requiere los 4 datos que el portal exige: UUID, RFC emisor, RFC receptor
    y total exacto. Si falta alguno o el portal rechaza, retorna parseo_fallido.

    Útil para validar que un CFDI fue timbrado correctamente y no fue cancelado
    sin que nos enteremos (cancelación retroactiva).
    """
    try:
        return _client.verificar_cfdi_uuid(
            args.uuid, args.rfc_emisor, args.rfc_receptor, args.total
        )
    except McpError as exc:
        return exc.to_dict()


# ---------- tool utilitario LOCAL ----------


@mcp.tool(
    annotations={
        "title": "Validar estructura de un UUID CFDI (local, sin red)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sat_validar_uuid_estructura(args: UuidInput) -> dict:
    """Valida que un UUID CFDI tenga formato correcto.

    Local y determinístico — útil para validar antes de hacer una consulta
    real al SAT (evita gastar request si el UUID está mal escrito).

    Devuelve: valido, uuid_normalizado, version_uuid, es_v4_random, razon (si inválido).
    """
    return _validar_uuid(args.uuid)


# ---------- tools con auth (mock por default) ----------


@mcp.tool(
    annotations={
        "title": "Descargar Constancia de Situación Fiscal (CSF)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sat_descargar_csf(args: RfcInput) -> dict:
    """Descarga la CSF del contribuyente.

    En modo real requiere RFC + Contraseña (CIEC) o e.firma. En modo mock
    (default sin credenciales) retorna estructura plausible con `simulated: true`.
    """
    try:
        return _client.descargar_csf(args.rfc)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Descargar notificaciones del Buzón Tributario",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,  # podría llegar nueva notificación
        "openWorldHint": True,
    },
)
async def sat_descargar_buzon_tributario(args: RfcInput) -> dict:
    """Lista notificaciones pendientes del Buzón Tributario.

    Requiere e.firma vigente. Retorna folios, tipo (requerimiento/citatorio/etc.),
    fechas y urgencia. Crítico para no perder requerimientos con plazo.
    """
    try:
        return _client.descargar_buzon_tributario(args.rfc)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Solicitar descarga masiva de CFDIs (emitidos o recibidos)",
        "readOnlyHint": False,  # crea solicitud en SAT
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def sat_descargar_cfdi_masivo(args: DescargaMasivaInput) -> dict:
    """Solicita al SAT descarga masiva de CFDIs por periodo.

    El SAT procesa la solicitud asíncrona y devuelve un ZIP con metadata + XMLs
    en 1-4 horas. Esta tool registra la solicitud; la descarga del ZIP es paso
    aparte cuando esté disponible.

    Requiere e.firma.
    """
    try:
        return _client.descargar_cfdi_masivo(
            args.rfc, args.ejercicio, args.mes, args.tipo
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Buscar citas disponibles en oficinas SAT",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def sat_agendar_cita(args: CitaSatInput) -> dict:
    """Busca disponibilidad de citas SAT por tipo de trámite y entidad.

    Esta tool NO agenda — solo lista disponibilidad. Agendar requiere paso
    extra de confirmación (no implementado para evitar agendas accidentales).
    """
    try:
        return _client.agendar_cita_sat(args.rfc, args.tipo_tramite, args.entidad)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Verificar vigencia de e.firma (FIEL)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sat_verificar_efirma_vigente(args: RfcInput) -> dict:
    """Verifica el status y fecha de vencimiento de la e.firma del contribuyente.

    Crítico para mantener: una e.firma vencida bloquea descargas masivas,
    Buzón Tributario y trámites de modificación. Alerta cuando faltan < 90 días.
    """
    try:
        return _client.verificar_efirma_vigente(args.rfc)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Descargar acuse de declaración o trámite",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sat_descargar_acuse(args: FolioInput) -> dict:
    """Descarga el PDF de acuse de una declaración o trámite previamente presentado.

    Útil para reconstruir bitácora fiscal o aportar evidencia en revisión.
    """
    try:
        return _client.descargar_acuse(args.folio)
    except McpError as exc:
        return exc.to_dict()


# ---------- tool de escritura (siempre simulada por default) ----------


@mcp.tool(
    annotations={
        "title": "⚠ Actualizar obligaciones fiscales (operación de ESCRITURA)",
        "readOnlyHint": False,
        "destructiveHint": True,  # cambia padrón
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def sat_actualizar_obligaciones(args: ActualizarObligacionesInput) -> dict:
    """⚠ Modifica el padrón de contribuyentes en SAT.

    Cualquier cambio de régimen, alta/baja de obligación o aumento/disminución
    tiene consecuencias fiscales. Esta tool SIEMPRE retorna simulación por
    seguridad — el path real bloquea sin `PLUGINS_MX_SAT_PERMITIR_ESCRITURA=1`
    y aún así está marcado como "no implementado" hasta tener doble revisión.
    """
    try:
        return _client.actualizar_obligaciones(args.rfc, args.accion)
    except McpError as exc:
        return exc.to_dict()


# ---------- catálogos discovery ----------


@mcp.tool(
    annotations={
        "title": "Catálogos SAT: status RFC, motivos 69/69-B, tipos obligación",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sat_listar_catalogos() -> dict:
    """Discovery offline de catálogos usados por mp_sat_portal."""
    return {
        "status_rfc": STATUS_RFC,
        "motivos_69_incumplidos": MOTIVOS_69_INCUMPLIDOS,
        "estado_69b": ESTADO_69B,
        "tipos_obligacion": TIPOS_OBLIGACION,
        "tipos_notificacion_buzon": TIPOS_NOTIFICACION_BUZON,
        "status_efirma": STATUS_EFIRMA,
        "auth_methods": AUTH_METHODS,
        "nota": (
            "Estos catálogos son aproximados — verificar contra portal SAT vigente. "
            "Algunos campos (como motivos del Art. 69) tienen redacción específica "
            "en RMF y conviene confirmarlos antes de uso fiscal."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
