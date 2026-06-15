"""Cliente mp_expediente_clinico_nom024."""
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
    calcular_vigencia_minima,
    clasificar_medicamento,
    fecha_vencimiento_iso,
)
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402


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
        """Genera receta electrónica con validación COFEPRIS."""
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

        # Clasificación COFEPRIS por medicamento
        meds_anotados = []
        requiere_especialidad = False
        for m in medicamentos:
            clasif = clasificar_medicamento(m.get("nombre", ""))
            meds_anotados.append({
                **m,
                "fraccion_cofepris": clasif.fraccion,
                "vigencia_dias": clasif.vigencia_receta_dias,
                "requiere_especialidad": clasif.requiere_cedula_especialidad,
                "notas_clasificacion": clasif.notas,
            })
            if clasif.requiere_cedula_especialidad:
                requiere_especialidad = True

        vigencia = calcular_vigencia_minima(medicamentos)
        fecha_vence = fecha_vencimiento_iso(fecha_emision, vigencia)

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

        return mark_simulated({
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
            "requiere_cedula_especialidad": requiere_especialidad,
            "hash_payload_firmable_sha256": hash_payload,
            "valida_nom024": True,
            "base_legal": "NOM-024-SSA3-2012, NOM-004-SSA3-2012, LGS Art. 28 Bis y 226, DOF 15-ene-2026",
            "disclaimer": (
                "Receta generada digitalmente. Para ser válida ante COFEPRIS y farmacias requiere "
                "firma electrónica avanzada del médico emisor. Conservar 5 años."
            ),
        })

    def verificar_medico_para_receta(self, cedula: str) -> dict[str, Any]:
        """Reutiliza patrón mp_sep_profesional con stub local mock-first.

        Path real: invocar mp_sep_profesional para validar cédula vigente.
        Devuelve si la cédula es estructural+vigente.
        """
        cedula = _validar_cedula(cedula)
        digit_ultimo = int(cedula[-1])
        # Mock determinístico
        vigente = digit_ultimo != 0  # 90% vigentes
        result = mark_simulated({
            "cedula": cedula,
            "estructural_valida": True,
            "vigente": vigente,
            "puede_recetar": vigente,
            "fuente_path_real": "mp_sep_profesional (delegado)",
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })
        self._bitacora.log("verificar_medico_para_receta", success=True,
                           params_summary={"cedula_hash": self._bitacora.hash_sensitive(cedula)})
        return result

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
                "cumple": si_cumple,
            }
            if si_cumple:
                cumplidos.append(entry)
            else:
                faltantes.append(entry)

        obligatorios_no_cumplidos = [f for f in faltantes if f["obligatorio"]]
        score = round(100 * len(cumplidos) / len(REQUISITOS_NOM024))
        cumple_nom024 = len(obligatorios_no_cumplidos) == 0

        return mark_simulated({
            "sistema_id": sistema_id,
            "score": score,
            "cumple_nom024": cumple_nom024,
            "obligatorios_faltantes": len(obligatorios_no_cumplidos),
            "checklist": cumplidos + faltantes,
            "base_legal": "NOM-024-SSA3-2012 + DOF 15-ene-2026",
        })

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
        return mark_simulated({
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
        })
