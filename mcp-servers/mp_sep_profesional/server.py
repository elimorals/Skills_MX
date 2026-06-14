"""mp_sep_profesional — MCP standalone para validación de cédulas profesionales SEP.

Tools:
- sep_consultar_cedula(cedula, [validar_vigencia])
- sep_consultar_por_datos(nombre, primer_apellido, [segundo_apellido, curp])
- sep_validar_medico_para_consulta(cedula, [cedula_especialidad]) — telemedicina-mx
- sep_listar_profesiones_reguladas()

Portal: https://cedulaprofesional.sep.gob.mx/ (SIN CAPTCHA — automatizable 100%).

Crítico para verticales:
- telemedicina-mx (NOM-004 obligatoria)
- consultorio-especialista-mx
- clinica-salud-mx, psicoterapia-mx
- despacho-legal-mx, despacho-contable-mx

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

from mp_sep_profesional.client import SepProfesionalClient  # noqa: E402


mcp = FastMCP("sep_profesional")
_client = SepProfesionalClient()


# ============================================================
# Schemas
# ============================================================

class ConsultarCedulaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cedula: str = Field(..., min_length=7, max_length=8,
                        description="Número de cédula profesional (7-8 dígitos).")
    validar_vigencia: bool = Field(True,
                                   description="Si True, marca si es profesión regulada (salud/legal/etc).")


class ConsultarPorDatosInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str = Field(..., min_length=2, max_length=50,
                        description="Nombre(s) del profesionista.")
    primer_apellido: str = Field(..., min_length=2, max_length=50,
                                 description="Apellido paterno.")
    segundo_apellido: Optional[str] = Field(None, max_length=50,
                                            description="Apellido materno.")
    curp: Optional[str] = Field(None, min_length=18, max_length=18,
                                description="CURP (18 chars).")


class ValidarMedicoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cedula: str = Field(..., min_length=7, max_length=8,
                        description="Cédula profesional general del médico.")
    cedula_especialidad: Optional[str] = Field(None, min_length=7, max_length=8,
                                                description="Cédula de especialidad (requerida para recetar controlados).")


# ============================================================
# Tools
# ============================================================

@mcp.tool(annotations={
    "title": "Consultar cédula profesional SEP",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def sep_consultar_cedula(args: ConsultarCedulaInput) -> dict:
    """Consulta cédula profesional por número en el Registro Nacional de Profesionistas.

    Útil cuando ya tienes el número de cédula del profesionista.

    Returns:
        {
          "cedula": "1234567",
          "nombre_completo": "JUAN PEREZ GARCIA",
          "profesion": "Médico Cirujano",
          "institucion": "Universidad Nacional Autónoma de México",
          "fecha_expedicion": "2015-06-15",
          "vigente": true,
          "categoria_regulada": "salud" | "legal" | "contable_fiscal" | "ingenierias_riesgo" | "educacion" | null,
          "requiere_validacion_obligatoria": true | false,
          "simulated": bool
        }
    """
    return _client.consultar_cedula(
        cedula=args.cedula,
        validar_vigencia=args.validar_vigencia,
    )


@mcp.tool(annotations={
    "title": "Consultar cédula por datos (nombre+apellidos)",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def sep_consultar_por_datos(args: ConsultarPorDatosInput) -> dict:
    """Consulta cédula cuando NO se tiene el número, solo nombre y apellidos.

    Útil para verificar profesionista en cobranza/onboarding sin pedirle su número.

    Returns: misma estructura que sep_consultar_cedula.
    """
    return _client.consultar_por_datos(
        nombre=args.nombre,
        primer_apellido=args.primer_apellido,
        segundo_apellido=args.segundo_apellido,
        curp=args.curp,
    )


@mcp.tool(annotations={
    "title": "Validar médico para consulta telemedicina (NOM-004 + COFEPRIS 2024)",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def sep_validar_medico_para_consulta(args: ValidarMedicoInput) -> dict:
    """Validación específica para telemedicina-mx: ¿puede este médico dar consulta?

    Cumple NOM-004-SSA3-2012 (expediente clínico) + Acuerdo COFEPRIS 28-mar-2024 (telemedicina).

    Reglas:
    1. Cédula general DEBE estar vigente Y ser de salud (Médico Cirujano u homólogo).
    2. Si va a recetar medicamentos controlados (Fracciones I-V), DEBE tener cédula de especialidad vigente.
    3. Sin cédula especialidad: puede dar consulta pero NO recetar controlados.

    Returns:
        {
          "puede_dar_consulta": true | false,
          "cedula_general_ok": bool,
          "cedula_especialidad_ok": bool,
          "puede_recetar_controlados": bool,
          "advertencias": [...],
          "cedulas_validadas": [{"tipo", "cedula", "vigente", "profesion", "ok"}],
          "cumple_nom_004": bool,
          "cumple_cofepris_2024": bool,
          "nombre_titular": "JUAN PEREZ GARCIA"
        }

    Si puede_dar_consulta=False: ABORTAR consulta de telemedicina, sería ejercicio
    ilegal de la profesión (delito CFF Art. 250).
    """
    return _client.validar_medico_para_consulta(
        cedula=args.cedula,
        cedula_especialidad=args.cedula_especialidad,
    )


@mcp.tool(annotations={
    "title": "Listar profesiones reguladas que requieren cédula",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def sep_listar_profesiones_reguladas() -> dict:
    """Devuelve catálogo de profesiones que por ley requieren validación de cédula.

    Categorías cubiertas:
    - salud (médicos, dentistas, psicólogos, nutriólogos, etc.)
    - legal (abogados)
    - contable_fiscal (contadores)
    - ingenierias_riesgo (civiles, arquitectos, químicos)
    - educacion (pedagogos, lic. educación)
    """
    return _client.listar_profesiones_reguladas()


if __name__ == "__main__":
    mcp.run()
