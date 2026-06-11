"""mp_curp_renapo — validación CURP + consulta RENAPO (mock).

8 tools:
- Validación estructural pura (5 tools, sin red, instantáneos)
- Generación reversa desde datos personales
- Validación batch
- Consulta RENAPO (mock por default; Playwright pendiente)

Caso de uso: colegios identifican alumnos por CURP, salud por paciente,
migración para inscribir extranjeros al SAT. La capa estructural detecta
errores de captura ANTES de pegarle a RENAPO (rate-limited).
"""

from __future__ import annotations

import sys
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_curp_renapo.catalogos import ESTADOS_CURP, SEXO_CURP  # noqa: E402
from mp_curp_renapo.renapo import RenapoClient  # noqa: E402
from mp_curp_renapo.validacion import (  # noqa: E402
    derivar_estado as _derivar_estado,
    derivar_fecha_nacimiento as _derivar_fecha_nacimiento,
    derivar_sexo as _derivar_sexo,
    generar_curp_desde_datos as _generar_curp_desde_datos,
    validar_estructura as _validar_estructura,
    validar_lote as _validar_lote,
)
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("curp_renapo_mcp")
_renapo = RenapoClient()


# ---------- enums ----------


class Sexo(str, Enum):
    H = "H"
    M = "M"


# ---------- input models ----------


class CurpInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    curp: str = Field(
        ...,
        description="CURP a procesar. Se normaliza (mayúsculas, sin acentos, sin espacios) antes de validar.",
        min_length=1,
        max_length=30,
    )


class CurpListInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    curps: list[str] = Field(
        ...,
        description="Lista de CURPs a validar en bloque.",
        min_length=1,
        max_length=500,
    )


class GenerarCurpInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    primer_apellido: str = Field(..., description="Apellido paterno.", min_length=1, max_length=50)
    segundo_apellido: str = Field(
        default="",
        description="Apellido materno. Vacío si la persona no tiene segundo apellido (extranjeros).",
        max_length=50,
    )
    nombre: str = Field(..., description="Primer nombre.", min_length=1, max_length=50)
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento en ISO 8601 (YYYY-MM-DD).")
    sexo: Sexo = Field(..., description="H = Hombre, M = Mujer.")
    estado_codigo: str = Field(
        ...,
        description="Código RENAPO del estado de nacimiento (DF, JC, NL, NE para extranjero, ...).",
        min_length=2,
        max_length=2,
    )
    char_homonimia: str = Field(
        default="0",
        description=(
            "Char de homonimia: '0' para 1900s, 'A' para 2000s por default. "
            "RENAPO asigna 1, 2, ... o B, C, ... a personas posteriores con mismos datos."
        ),
        min_length=1,
        max_length=1,
    )


# ---------- tools: validación estructural ----------


@mcp.tool(
    name="curp_validar_estructura",
    annotations={
        "title": "Validar CURP estructuralmente (sin red)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def curp_validar_estructura(params: CurpInput) -> dict:
    """Valida formato, regex por posición, fecha embebida y dígito verificador.

    Devuelve payload estructurado con `valido_estructura: bool`, todos los
    componentes decodificados (fecha, sexo, estado, consonantes, homonimia),
    y listas de `errores`/`alertas`. Esta función es 100% local: no toca red.

    Una CURP que pasa esta validación NO está confirmada en RENAPO — usa
    `curp_consultar_renapo` para eso. Pero una CURP que falla aquí va a fallar
    también en RENAPO, así que valida antes de gastar consultas.
    """
    return _validar_estructura(params.curp)


@mcp.tool(
    name="curp_derivar_fecha_nacimiento",
    annotations={
        "title": "Extraer fecha de nacimiento embebida en la CURP",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def curp_derivar_fecha_nacimiento(params: CurpInput) -> dict:
    """Decodifica fecha de nacimiento. Usa char homonimia para determinar siglo."""
    fecha = _derivar_fecha_nacimiento(params.curp)
    if fecha is None:
        return {
            "fecha_nacimiento": None,
            "error": "No se pudo decodificar la fecha — formato CURP inválido o fecha imposible.",
        }
    return {"fecha_nacimiento": fecha.isoformat(), "siglo": (fecha.year // 100) * 100}


@mcp.tool(
    name="curp_derivar_sexo",
    annotations={
        "title": "Decodificar sexo (H/M) de la CURP",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def curp_derivar_sexo(params: CurpInput) -> dict:
    sexo = _derivar_sexo(params.curp)
    if sexo is None:
        return {"sexo": None, "error": "Char 11 no es ni 'H' ni 'M'."}
    return {"sexo": sexo, "descripcion": SEXO_CURP[sexo]}


@mcp.tool(
    name="curp_derivar_estado",
    annotations={
        "title": "Decodificar estado de nacimiento de la CURP",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def curp_derivar_estado(params: CurpInput) -> dict:
    estado = _derivar_estado(params.curp)
    if estado is None:
        return {
            "estado_codigo": None,
            "estado_nombre": None,
            "error": "Código de estado en chars 12-13 no es reconocido.",
        }
    return {"estado_codigo": estado[0], "estado_nombre": estado[1]}


@mcp.tool(
    name="curp_validar_lote",
    annotations={
        "title": "Validar lote de CURPs (hasta 500)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def curp_validar_lote(params: CurpListInput) -> dict:
    """Valida estructuralmente una lista de CURPs. Útil para limpiar bases
    de alumnos/pacientes/empleados antes de migrar a un nuevo sistema.

    Devuelve {total, validos, invalidos, detalle: [...]}.
    """
    return _validar_lote(params.curps)


@mcp.tool(
    name="curp_generar_desde_datos",
    annotations={
        "title": "Generar CURP esperada desde datos personales",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def curp_generar_desde_datos(params: GenerarCurpInput) -> dict:
    """Genera la CURP que correspondería a los datos personales.

    Útil para:
    - Validar que la CURP recibida en un formulario coincide con los datos.
    - Sugerir una CURP a alguien que no la recuerda.

    El char homonimia NO se puede derivar — RENAPO lo asigna según orden de
    registro. Si la CURP generada no matchea, probar siguientes valores del
    char (1, 2, ... o B, C, ...).
    """
    return _generar_curp_desde_datos(
        primer_apellido=params.primer_apellido,
        segundo_apellido=params.segundo_apellido,
        nombre=params.nombre,
        fecha_nacimiento=params.fecha_nacimiento,
        sexo=params.sexo.value,
        estado_codigo=params.estado_codigo,
        char_homonimia=params.char_homonimia,
    )


# ---------- tools: RENAPO (con red) ----------


@mcp.tool(
    name="curp_consultar_renapo",
    annotations={
        "title": "Consultar CURP en padrón RENAPO oficial",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def curp_consultar_renapo(params: CurpInput) -> dict:
    """Verifica si la CURP existe en el padrón RENAPO.

    Devuelve estado (VIGENTE/DUPLICADO/etc.) y datos de la persona.

    ⚠ En modo mock (default): devuelve datos plausibles derivados de la propia
    CURP. En modo real: requiere Playwright integrado con bypass CAPTCHA
    (todavía no implementado — devuelve `not_implemented_error`).

    Cache 90 días — los datos del padrón cambian raramente.
    """
    try:
        return await _renapo.consultar(params.curp)
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="curp_descargar_constancia_renapo",
    annotations={
        "title": "Descargar constancia CURP oficial (PDF)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def curp_descargar_constancia_renapo(params: CurpInput) -> dict:
    """Descarga el PDF oficial de constancia de la CURP.

    Mismo backend que `curp_consultar_renapo`: mock por default, Playwright
    pendiente. En mock devuelve metadata con path simulado.
    """
    try:
        return await _renapo.descargar_constancia(params.curp)
    except McpError as err:
        return err.to_dict()


# ---------- catálogos ----------


@mcp.tool(
    name="curp_listar_catalogos",
    annotations={
        "title": "Catálogos: estados, códigos de sexo",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def curp_listar_catalogos() -> dict:
    """Discovery sin red de los catálogos RENAPO."""
    return {
        "estados": ESTADOS_CURP,
        "sexo": SEXO_CURP,
        "nota_homonimia": (
            "El char 17 codifica el siglo: dígito 0-9 = 1900s, letra A-Z = 2000s. "
            "Además sirve para desambiguar homónimos (mismo nombre + fecha)."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
