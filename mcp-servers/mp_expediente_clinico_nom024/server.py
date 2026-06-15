"""mp_expediente_clinico_nom024 — MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_expediente_clinico_nom024.client import ECEClient  # noqa: E402


mcp = FastMCP("ece_nom024")
_client = ECEClient()


class MedicamentoModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str
    dosis: str = ""
    via: str = ""
    frecuencia: str = ""
    duracion: str = ""
    indicaciones: str = ""


class RecetaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    medico_cedula: str = Field(..., min_length=4, max_length=12)
    medico_nombre: str = Field(..., min_length=3)
    medico_especialidad: str
    paciente_nombre: str = Field(..., min_length=3)
    paciente_edad: int = Field(..., ge=0, le=130)
    paciente_sexo: str
    paciente_curp: str | None = None
    medicamentos: list[MedicamentoModel]
    diagnostico: str = Field(..., min_length=3)
    folio: str | None = None


class CedulaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cedula: str = Field(..., min_length=4, max_length=12)


class SistemaECEInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sistema_id: str
    capacidades: list[str]


class ConsentimientoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    curp: str = Field(..., min_length=18, max_length=18)
    proposito: str = Field(..., min_length=10)


@mcp.tool(annotations={"title": "Generar receta electrónica NOM-024", "readOnlyHint": True})
def ece_generar_receta(args: RecetaInput) -> dict:
    return _client.generar_receta_electronica(
        medico_cedula=args.medico_cedula, medico_nombre=args.medico_nombre,
        medico_especialidad=args.medico_especialidad,
        paciente_nombre=args.paciente_nombre, paciente_edad=args.paciente_edad,
        paciente_sexo=args.paciente_sexo, paciente_curp=args.paciente_curp,
        medicamentos=[m.model_dump() for m in args.medicamentos],
        diagnostico=args.diagnostico, folio=args.folio,
    )


@mcp.tool(annotations={"title": "Verificar médico autorizado", "readOnlyHint": True})
def ece_verificar_medico(args: CedulaInput) -> dict:
    return _client.verificar_medico_para_receta(cedula=args.cedula)


@mcp.tool(annotations={"title": "Validar sistema ECE contra NOM-024", "readOnlyHint": True})
def ece_validar_sistema(args: SistemaECEInput) -> dict:
    return _client.validar_sistema_ece(sistema_id=args.sistema_id, capacidades=args.capacidades)


@mcp.tool(annotations={"title": "Consentimiento informado paciente", "readOnlyHint": True})
def ece_consentimiento_paciente(args: ConsentimientoInput) -> dict:
    return _client.consentimiento_paciente(curp=args.curp, proposito=args.proposito)


if __name__ == "__main__":
    mcp.run()
