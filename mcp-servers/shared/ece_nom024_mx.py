"""Expediente Clínico Electrónico (ECE) + Receta Electrónica MX — NOM-024-SSA3-2012.

Decreto DOF 15-ene-2026 hace OBLIGATORIA la digitalización del sector salud.

Marco legal:
- NOM-024-SSA3-2012 — sistemas de información en salud
- NOM-004-SSA3-2012 — expediente clínico
- Ley General de Salud Art. 28 Bis y 226 — receta electrónica
- COFEPRIS — regulación medicamentos controlados (fracciones I-V)

Compatible con `mp_sep_profesional` para validar cédula del médico.
Universo: ~70k médicos privados + ~20k clínicas + ~5k hospitales privados MX.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional


FraccionCofepris = Literal["I", "II", "III", "IV", "V", "no_controlado"]


@dataclass
class RequisitoNOM024:
    clave: str
    descripcion: str
    obligatorio: bool = True
    seccion: str = "sistema"  # sistema / receta / expediente / firma


REQUISITOS_NOM024: list[RequisitoNOM024] = [
    RequisitoNOM024("trazabilidad_completa",
                    "Trazabilidad de cada modificación (quién + cuándo + qué).",
                    seccion="sistema"),
    RequisitoNOM024("firma_electronica_avanzada",
                    "Soporte para e.firma (FIEL) del médico emisor.",
                    seccion="firma"),
    RequisitoNOM024("respaldo_seguro_5_anios",
                    "Respaldo seguro mínimo 5 años (NOM-004-SSA3).",
                    seccion="sistema"),
    RequisitoNOM024("consentimiento_paciente_documentado",
                    "Consentimiento informado del paciente para uso datos.",
                    seccion="expediente"),
    RequisitoNOM024("interoperabilidad_hl7",
                    "Interoperabilidad básica con estándar HL7 v2.5 o FHIR R4.",
                    seccion="sistema",
                    obligatorio=False),
    RequisitoNOM024("cédula_validada_médico",
                    "Validación cédula profesional SEP del médico emisor.",
                    seccion="firma"),
    RequisitoNOM024("identificador_paciente",
                    "Identificador único de paciente (CURP cuando aplique).",
                    seccion="expediente"),
    RequisitoNOM024("controles_acceso_rbac",
                    "Controles de acceso basados en roles (médico, enfermería, admin).",
                    seccion="sistema"),
    RequisitoNOM024("registro_modificaciones",
                    "Bitácora inmutable de modificaciones a registros clínicos.",
                    seccion="sistema"),
    RequisitoNOM024("anonimización_estadística",
                    "Anonimización para reportes estadísticos.",
                    seccion="sistema",
                    obligatorio=False),
]


@dataclass
class CamposReceta:
    """Campos mínimos NOM-004-SSA3 + COFEPRIS para una receta válida."""
    medico_cedula: str
    medico_nombre: str
    medico_especialidad: str
    paciente_curp: Optional[str]
    paciente_nombre: str
    paciente_edad: int
    paciente_sexo: Literal["M", "F", "ND"]
    fecha_emision: str  # ISO 8601
    medicamentos: list[dict]  # [{nombre, dosis, via, frecuencia, duracion, indicaciones}]
    diagnostico: str
    vigencia_dias: int = 30  # default genérico
    folio: Optional[str] = None
    cedula_especialidad: Optional[str] = None  # requerido para Fracciones I-III COFEPRIS


@dataclass
class MedicamentoControlado:
    """Clasificación COFEPRIS de medicamento controlado."""
    nombre: str
    fraccion: FraccionCofepris
    vigencia_receta_dias: int
    requiere_cedula_especialidad: bool
    notas: str = ""


# Catálogo demostrativo de medicamentos controlados típicos
CATALOGO_MEDICAMENTOS_CONTROLADOS: list[MedicamentoControlado] = [
    MedicamentoControlado("morfina", "I", 1, True,
                           "Fracción I: opioides mayores, receta especial barra magnética"),
    MedicamentoControlado("fentanilo", "I", 1, True, "Fracción I"),
    MedicamentoControlado("oxicodona", "I", 1, True, "Fracción I"),
    MedicamentoControlado("metadona", "I", 1, True, "Fracción I"),
    MedicamentoControlado("tramadol", "II", 30, False,
                           "Fracción II: receta surtir 1 sola vez en 30 días"),
    MedicamentoControlado("buprenorfina", "II", 30, True, "Fracción II"),
    MedicamentoControlado("alprazolam", "IV", 30, False,
                           "Fracción IV: receta surtir hasta 3 veces 6 meses"),
    MedicamentoControlado("clonazepam", "IV", 30, False, "Fracción IV"),
    MedicamentoControlado("diazepam", "IV", 30, False, "Fracción IV"),
    MedicamentoControlado("lorazepam", "IV", 30, False, "Fracción IV"),
    MedicamentoControlado("metilfenidato", "II", 30, True,
                           "Fracción II: TDAH, requiere especialidad"),
    MedicamentoControlado("fenobarbital", "III", 30, False, "Fracción III"),
]


def clasificar_medicamento(nombre: str) -> MedicamentoControlado:
    """Devuelve clasificación COFEPRIS; si no es controlado devuelve V (no_controlado)."""
    n = (nombre or "").strip().lower()
    for m in CATALOGO_MEDICAMENTOS_CONTROLADOS:
        if m.nombre in n:
            return m
    return MedicamentoControlado(nombre=nombre, fraccion="no_controlado",
                                  vigencia_receta_dias=30,
                                  requiere_cedula_especialidad=False)


def calcular_vigencia_minima(medicamentos: list[dict]) -> int:
    """Devuelve vigencia mínima en días considerando todos los medicamentos."""
    vigencias = []
    for m in medicamentos:
        clasif = clasificar_medicamento(m.get("nombre", ""))
        vigencias.append(clasif.vigencia_receta_dias)
    return min(vigencias) if vigencias else 30


def fecha_vencimiento_iso(fecha_emision_iso: str, dias: int) -> str:
    """Suma días a fecha ISO y devuelve nueva fecha ISO."""
    fmt = "%Y-%m-%d"
    base = datetime.strptime(fecha_emision_iso[:10], fmt).replace(tzinfo=timezone.utc)
    return (base + timedelta(days=dias)).strftime(fmt)


__all__ = [
    "FraccionCofepris", "RequisitoNOM024", "REQUISITOS_NOM024",
    "CamposReceta", "MedicamentoControlado", "CATALOGO_MEDICAMENTOS_CONTROLADOS",
    "clasificar_medicamento", "calcular_vigencia_minima", "fecha_vencimiento_iso",
]
