"""Cliente mp_expediente_clinico_nom024 — receta y SIRES con reglas LGS/NOM verificadas.

Ver fuentes y fechas en shared/ece_nom024_mx.py. La validación de cédula contra el Registro
Nacional de Profesionistas no se hace aquí (handoff a mp_sep_profesional): antes se decidía
"vigente" con el último dígito.
"""
from __future__ import annotations

import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.ece_nom024_mx import (  # noqa: E402
    REQUISITOS_NOM024,
    URL_LGS,
    URL_NOM024,
    calcular_vigencia_minima,
    clasificar_medicamento,
    fecha_vencimiento_iso,
)
from shared.errors import ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "ece_nom024"


CURP_RE = re.compile(r"^[A-Z][AEIOU][A-Z]{2}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[HM][A-Z]{5}[A-Z0-9]\d$")
CEDULA_RE = re.compile(r"^\d{4,12}$")


def _validar_curp(curp: str) -> str:
    curp = (curp or "").strip().upper()
    if not CURP_RE.match(curp):
        raise ValidationError(f"CURP inválida: {curp!r}")
    return curp


def _validar_cedula(cedula: str) -> str:
    cedula = (cedula or "").strip()
    if not CEDULA_RE.match(cedula):
        raise ValidationError(f"Cédula profesional inválida: {cedula!r}")
    return cedula


class ECEClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def generar_receta_electronica(
        self,
        medico_cedula: str,
        medico_nombre: str,
        medico_especialidad: str,
        paciente_nombre: str,
        paciente_edad: int,
        paciente_sexo: str,
        medicamentos: list[dict],
        diagnostico: str,
        paciente_curp: str | None = None,
        folio: str | None = None,
    ) -> dict[str, Any]:
        """Arma la receta y anota reglas de venta (LGS Art. 226 y listas 234/245) por medicamento."""
        medico_cedula = _validar_cedula(medico_cedula)
        if paciente_sexo not in ("M", "F", "ND"):
            raise ValidationError(f"paciente_sexo inválido: {paciente_sexo}")
        if paciente_edad < 0 or paciente_edad > 130:
            raise ValidationError("paciente_edad fuera de rango")
        if not medicamentos:
            raise ValidationError("Debe incluir al menos 1 medicamento")
        if paciente_curp:
            paciente_curp = _validar_curp(paciente_curp)

        ahora = datetime.now(timezone.utc)
        fecha_emision = ahora.strftime("%Y-%m-%d")
        folio = folio or f"RX-{ahora.strftime('%Y%m%d%H%M%S')}"

        # Clasificación por las listas de la LGS (Arts. 226, 234, 245)
        meds_anotados = []
        recetario_especial = False
        for m in medicamentos:
            clasif = clasificar_medicamento(m.get("nombre", ""))
            meds_anotados.append({
                **m,
                "categoria_lgs": clasif.categoria,
                "fraccion_venta_art226": clasif.fraccion,
                "vigencia_dias": clasif.vigencia_receta_dias,
                "vigencia_meses": clasif.vigencia_meses,
                "surtidos_max": clasif.surtidos_max,
                "regla": clasif.regla,
                "fundamento": clasif.fundamento,
            })
            if clasif.categoria == "estupefaciente_art234":
                recetario_especial = True

        vigencia = calcular_vigencia_minima(medicamentos)
        meses = [x["vigencia_meses"] for x in meds_anotados if x["vigencia_meses"]]
        if vigencia is not None:
            fecha_vence = fecha_vencimiento_iso(fecha_emision, dias=vigencia)
        elif meses:
            fecha_vence = fecha_vencimiento_iso(fecha_emision, meses=min(meses))
        else:
            fecha_vence = None

        # Hash del payload firmable (lo que firma la e.firma del médico)
        payload_firmable = (
            f"folio={folio}|cedula={medico_cedula}|paciente_hash="
            f"{self._bitacora.hash_sensitive(paciente_curp or paciente_nombre)}|"
            f"meds={'+'.join(m.get('nombre','') for m in medicamentos)}|"
            f"emision={fecha_emision}"
        )
        hash_payload = hashlib.sha256(payload_firmable.encode("utf-8")).hexdigest()

        self._bitacora.log("generar_receta_electronica", success=True,
                           params_summary={"medico_cedula_hash": self._bitacora.hash_sensitive(medico_cedula),
                                           "paciente_hash": self._bitacora.hash_sensitive(paciente_curp or paciente_nombre),
                                           "folio": folio, "n_medicamentos": len(medicamentos)})

        return {
            "folio": folio,
            "fecha_emision": fecha_emision,
            "fecha_vencimiento": fecha_vence,
            "vigencia_dias": vigencia,
            "medico": {
                "cedula": medico_cedula,
                "nombre": medico_nombre,
                "especialidad": medico_especialidad,
            },
            "paciente": {
                "curp_hash": self._bitacora.hash_sensitive(paciente_curp) if paciente_curp else None,
                "nombre": paciente_nombre,
                "edad": paciente_edad,
                "sexo": paciente_sexo,
            },
            "diagnostico": diagnostico,
            "medicamentos": meds_anotados,
            "requiere_recetario_especial_codigo_barras": recetario_especial,
            "advertencias": (["Contiene estupefacientes: debe expedirse en recetario especial con código "
                              "de barras de la SSA (LGS Art. 241); esta receta electrónica no lo sustituye."]
                             if recetario_especial else []),
            "prescribir_denominacion_generica": "Obligatorio (LGS Art. 226, párrafo adicionado DOF 30-03-2022)",
            "hash_payload_firmable_sha256": hash_payload,
            "base_legal": "LGS Arts. 226, 234, 240-241, 245, 251-252; NOM-004-SSA3-2012; NOM-024-SSA3-2012",
            "fuente": URL_LGS,
            "disclaimer": (
                "Borrador generado digitalmente: requiere firma del médico. No certifica cumplimiento "
                "de la NOM-024 ni del Reglamento de Insumos para la Salud (no cotejado)."
            ),
        }

    def verificar_medico_para_receta(self, cedula: str) -> dict[str, Any]:
        """Valida el formato de la cédula; la vigencia se consulta con mp_sep_profesional."""
        cedula = _validar_cedula(cedula)
        self._bitacora.log("verificar_medico_para_receta", success=True,
                           params_summary={"cedula_hash": self._bitacora.hash_sensitive(cedula)})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"cedula": cedula, "estructural_valida": True, "vigente": True})
        return {
            "cedula": cedula,
            "estructural_valida": True,
            "vigente": None,
            "puede_recetar": None,
            "verificar_con": "mp_sep_profesional (Registro Nacional de Profesionistas, SEP)",
            "nota": "Estupefacientes: solo médicos cirujanos, cirujanos dentistas y veterinarios (LGS Art. 240).",
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    def validar_sistema_ece(self, sistema_id: str, capacidades: list[str]) -> dict[str, Any]:
        """Verifica que un sistema cumpla con requisitos NOM-024."""
        if not sistema_id:
            raise ValidationError("sistema_id requerido")
        capacidades_set = set(capacidades or [])

        cumplidos = []
        faltantes = []
        for req in REQUISITOS_NOM024:
            si_cumple = req.clave in capacidades_set
            entry = {
                "clave": req.clave,
                "descripcion": req.descripcion,
                "obligatorio": req.obligatorio,
                "seccion": req.seccion,
                "fundamento": req.fundamento,
                "cumple": si_cumple,
            }
            if si_cumple:
                cumplidos.append(entry)
            else:
                faltantes.append(entry)

        obligatorios_no_cumplidos = [f for f in faltantes if f["obligatorio"]]
        score = round(100 * len(cumplidos) / len(REQUISITOS_NOM024))
        cumple_nom024 = len(obligatorios_no_cumplidos) == 0

        return {
            "sistema_id": sistema_id,
            "score": score,
            "cumple_nom024": cumple_nom024,
            "obligatorios_faltantes": len(obligatorios_no_cumplidos),
            "checklist": cumplidos + faltantes,
            "base_legal": "NOM-024-SSA3-2012 (DOF 30-11-2012) y NOM-004-SSA3-2012 5.4",
            "fuente": URL_NOM024,
            "nota": ("Autoevaluación con las capacidades declaradas; la conformidad formal la certifica "
                     "la DGIS (NOM-024 cap. 7)."),
        }

    def consentimiento_paciente(self, curp: str, proposito: str) -> dict[str, Any]:
        """Genera token de consentimiento informado paciente (template)."""
        curp = _validar_curp(curp)
        if not proposito or len(proposito) < 10:
            raise ValidationError("Propósito debe explicarse (mínimo 10 caracteres)")
        ahora = datetime.now(timezone.utc)
        payload = f"curp_hash={self._bitacora.hash_sensitive(curp)}|prop={proposito}|emit={ahora.isoformat()}"
        token = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]

        self._bitacora.log("consentimiento_paciente", success=True,
                           params_summary={"curp_hash": self._bitacora.hash_sensitive(curp),
                                           "proposito": proposito[:60]})
        return {
            "curp_hash": self._bitacora.hash_sensitive(curp),
            "proposito": proposito,
            "token_consentimiento": token,
            "fecha_emision": ahora.isoformat(),
            "valido_hasta": (ahora.replace(year=ahora.year + 1)).isoformat(),
            "texto_consentimiento": (
                f"Por medio del presente otorgo mi consentimiento informado para que mis datos "
                f"clínicos sean tratados con el propósito de: {proposito}. Mis derechos ARCO "
                f"están protegidos conforme a LFPDPPP. Puedo revocar este consentimiento en "
                f"cualquier momento."
            ),
            "nota": "Plantilla orientativa (NOM-024 6.6.6 pide controlar consentimientos).",
        }
