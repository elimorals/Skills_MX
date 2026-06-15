"""Cliente mp_ley_silla_nom037 — checklist compliance laboral 2026."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.ley_silla_nom_mx import (  # noqa: E402
    CATALOGO_DESCONEXION_DIGITAL,
    CATALOGO_LEY_SILLA,
    CATALOGO_NOM035,
    CATALOGO_NOM037,
    UMA_2026_DIARIA,
    calcular_multa_mxn,
    obligaciones_aplicables_ley_silla,
    obligaciones_aplicables_nom035,
    obligaciones_aplicables_nom037,
    obligaciones_desconexion_digital,
)
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "ley_silla_nom037"


class LeySillaNomClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def verificar_compliance(
        self,
        rfc: str,
        num_empleados: int,
        giro: str,
        modalidad_remota: bool = False,
        faltas_marcadas: list[str] | None = None,
    ) -> dict[str, Any]:
        """Devuelve checklist consolidado de obligaciones aplicables y faltantes."""
        if not rfc or len(rfc) < 12:
            raise ValidationError(f"RFC inválido: {rfc!r}")
        if num_empleados < 1:
            raise ValidationError("num_empleados debe ser >= 1")
        if giro not in {
            "retail_comercio", "manufactura", "servicios_personales", "oficina_administrativo",
            "teletrabajo_hibrido", "almacen_logistica", "salud", "educacion", "construccion", "otro",
        }:
            raise ValidationError(f"giro inválido: {giro!r}")

        faltas_marcadas = set(faltas_marcadas or [])

        # Construir checklist completo
        checklist = []

        for o in obligaciones_aplicables_ley_silla(giro):
            checklist.append({
                "marco": "Ley Silla",
                "clave": o.clave,
                "descripcion": o.descripcion,
                "base_legal": o.base_legal,
                "severidad": o.severidad_falta,
                "cumplida": o.clave not in faltas_marcadas,
            })

        for o in obligaciones_aplicables_nom035(num_empleados):
            checklist.append({
                "marco": "NOM-035",
                "clave": o.clave,
                "descripcion": o.descripcion,
                "base_legal": o.base_legal,
                "severidad": o.severidad_falta,
                "cumplida": o.clave not in faltas_marcadas,
            })

        for o in obligaciones_aplicables_nom037(modalidad_remota):
            checklist.append({
                "marco": "NOM-037",
                "clave": o.clave,
                "descripcion": o.descripcion,
                "base_legal": o.base_legal,
                "severidad": o.severidad_falta,
                "cumplida": o.clave not in faltas_marcadas,
            })

        for o in obligaciones_desconexion_digital(giro):
            checklist.append({
                "marco": "Desconexión digital",
                "clave": o.clave,
                "descripcion": o.descripcion,
                "base_legal": o.base_legal,
                "severidad": o.severidad_falta,
                "cumplida": o.clave not in faltas_marcadas,
            })

        # Cálculo multa potencial agregada
        no_cumplidas = [c for c in checklist if not c["cumplida"]]
        multa_total_min = 0.0
        multa_total_max = 0.0
        for c in no_cumplidas:
            mn, mx = calcular_multa_mxn(c["severidad"])
            multa_total_min += mn
            multa_total_max += mx

        score = round(100 * (len(checklist) - len(no_cumplidas)) / max(len(checklist), 1))

        self._bitacora.log("verificar_compliance", success=True,
                           params_summary={"rfc_hash": self._bitacora.hash_sensitive(rfc),
                                           "giro": giro, "num_empleados": num_empleados})
        return mark_simulated({
            "rfc": rfc,
            "giro": giro,
            "num_empleados": num_empleados,
            "modalidad_remota": modalidad_remota,
            "score_compliance": score,
            "total_obligaciones": len(checklist),
            "cumplidas": len(checklist) - len(no_cumplidas),
            "no_cumplidas": len(no_cumplidas),
            "checklist": checklist,
            "multa_potencial_min_mxn": round(multa_total_min, 2),
            "multa_potencial_max_mxn": round(multa_total_max, 2),
            "riesgo_inspeccion_stps": _evaluar_riesgo(no_cumplidas),
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "disclaimer": (
                "Auditoría asistida por IA. NO sustituye revisión por abogado laboral certificado. "
                "Validar con consultor SST antes de inspección STPS."
            ),
        })

    def calcular_multa(self, severidad: str, reincidente: bool = False) -> dict[str, Any]:
        """Calcula rango multa STPS para una severidad dada."""
        if severidad not in {"leve", "media", "grave", "muy_grave"}:
            raise ValidationError(f"severidad inválida: {severidad}")
        mn, mx = calcular_multa_mxn(severidad, reincidente=reincidente)
        return {
            "severidad": severidad,
            "reincidente": reincidente,
            "multa_min_mxn": round(mn, 2),
            "multa_max_mxn": round(mx, 2),
            "uma_diaria_2026": UMA_2026_DIARIA,
            "fuente": "Tabla multas STPS LFT (UMA 2026)",
        }

    def generar_politica(
        self,
        rfc: str,
        razon_social: str,
        giro: str,
        modalidad: str,
        nombre_responsable_sst: str,
    ) -> dict[str, Any]:
        """Genera contenido de política de prevención + desconexión digital (texto Markdown)."""
        fecha_emision = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        contenido_md = _plantilla_politica(
            razon_social, rfc, giro, modalidad, nombre_responsable_sst, fecha_emision
        )
        self._bitacora.log("generar_politica", success=True,
                           params_summary={"rfc_hash": self._bitacora.hash_sensitive(rfc),
                                           "giro": giro})
        return mark_simulated({
            "rfc": rfc,
            "razon_social": razon_social,
            "fecha_emision": fecha_emision,
            "contenido_md": contenido_md,
            "longitud_chars": len(contenido_md),
            "notas": [
                "Imprimir + firmar por representante legal + responsable SST",
                "Distribuir copias a todos los trabajadores con acuse",
                "Publicar en tableros visibles del centro de trabajo",
            ],
        })

    def listar_obligaciones(self, marco: str) -> dict[str, Any]:
        """Lista todas las obligaciones de un marco (catálogo público)."""
        if marco == "ley_silla":
            items = [{"clave": o.clave, "descripcion": o.descripcion,
                      "aplica_giros": list(o.aplica_giros),
                      "severidad": o.severidad_falta, "base_legal": o.base_legal}
                     for o in CATALOGO_LEY_SILLA]
        elif marco == "nom035":
            items = [{"clave": o.clave, "descripcion": o.descripcion,
                      "aplica_si_empleados_min": o.aplica_si_empleados_min,
                      "aplica_si_empleados_max": o.aplica_si_empleados_max,
                      "severidad": o.severidad_falta, "base_legal": o.base_legal}
                     for o in CATALOGO_NOM035]
        elif marco == "nom037":
            items = [{"clave": o.clave, "descripcion": o.descripcion,
                      "severidad": o.severidad_falta, "base_legal": o.base_legal}
                     for o in CATALOGO_NOM037]
        elif marco == "desconexion_digital":
            items = [{"clave": o.clave, "descripcion": o.descripcion,
                      "severidad": o.severidad_falta, "base_legal": o.base_legal}
                     for o in CATALOGO_DESCONEXION_DIGITAL]
        else:
            raise ValidationError(f"marco inválido: {marco}")
        return {"marco": marco, "total": len(items), "obligaciones": items}


def _evaluar_riesgo(no_cumplidas: list[dict]) -> str:
    if not no_cumplidas:
        return "bajo"
    severidades = {c["severidad"] for c in no_cumplidas}
    if "muy_grave" in severidades:
        return "critico"
    if "grave" in severidades and len(no_cumplidas) >= 3:
        return "alto"
    if "grave" in severidades:
        return "medio_alto"
    return "medio"


def _plantilla_politica(razon_social: str, rfc: str, giro: str, modalidad: str,
                       responsable_sst: str, fecha: str) -> str:
    """Política consolidada Ley Silla + NOM-035 + Desconexión digital."""
    return f"""# Política de Seguridad y Salud en el Trabajo

**Empresa:** {razon_social}
**RFC:** {rfc}
**Giro:** {giro}
**Modalidad:** {modalidad}
**Responsable SST:** {responsable_sst}
**Fecha de emisión:** {fecha}

## 1. Declaración de principios

{razon_social} reconoce que la salud, seguridad y bienestar integral de sus colaboradores
constituyen un valor estratégico de la organización. La presente política da cumplimiento
a las disposiciones de la Ley Federal del Trabajo (reforma DOF 17-jul-2025, Ley Silla;
reforma marzo 2026, Art. 132 desconexión digital), la NOM-035-STPS-2018 sobre factores
de riesgo psicosocial y la NOM-037-STPS-2023 sobre teletrabajo cuando aplique.

## 2. Prohibición de violencia laboral

Esta empresa NO TOLERA bajo ninguna circunstancia el acoso laboral, hostigamiento sexual,
discriminación, ni ninguna forma de violencia entre colaboradores o de superiores hacia
subordinados. Las denuncias se atenderán de forma confidencial por el responsable de SST.

## 3. Derecho a silla (Ley Silla)

Todo trabajador cuya actividad lo permita tendrá acceso permanente a una silla
ergonómica con respaldo. Para puestos con permanencia de pie prolongada se establecen
descansos cada 4 horas como mínimo.

## 4. Riesgos psicosociales (NOM-035)

- Se aplicarán cuestionarios oficiales de identificación de factores de riesgo
  conforme al número de trabajadores.
- Se ejecutará programa anual de prevención.
- Se brindará capacitación documentada al menos una vez al año.

## 5. Desconexión digital (LFT Art. 132 reforma marzo 2026)

Se respeta el derecho del trabajador a no ser contactado por medios digitales fuera de
su jornada laboral, salvo emergencia documentada. El personal con mando jerárquico
recibirá capacitación específica. Se habilita el correo `denuncias-sst@{rfc.lower()}.mx`
como canal interno para reportar violaciones.

## 6. Teletrabajo (NOM-037, cuando aplique)

Para colaboradores en modalidad remota, la empresa proveerá silla ergonómica, equipo
de cómputo y reembolsará proporcionalmente internet y electricidad conforme a contrato
individual escrito.

## 7. Capacitación

Se impartirá capacitación inicial y refrescamiento anual sobre los temas anteriores con
evidencia documental (listas de asistencia firmadas).

## 8. Sanciones internas

El incumplimiento por parte de personal con mando jerárquico se sancionará conforme al
reglamento interior de trabajo. Las denuncias se resolverán en máximo 10 días hábiles.

## 9. Revisión

La presente política se revisará al menos cada 12 meses y tras cualquier reforma legal
relevante.

---

**Firma representante legal:** ________________________  Fecha: __________

**Firma responsable SST ({responsable_sst}):** ________________________  Fecha: __________
"""
