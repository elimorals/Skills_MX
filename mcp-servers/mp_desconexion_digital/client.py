"""Cliente mp_desconexion_digital — Reforma LFT Art. 132 marzo 2026."""
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
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "desconexion_digital"


CHECKLIST_REFORMA_2026 = [
    {"clave": "politica_formal_publicada",
     "descripcion": "Política formal de desconexión digital publicada en tableros.",
     "severidad": "grave"},
    {"clave": "incluida_reglamento_interior",
     "descripcion": "Incluida en reglamento interior de trabajo.",
     "severidad": "media"},
    {"clave": "capacitacion_supervisores",
     "descripcion": "Personal con mando jerárquico capacitado documentadamente.",
     "severidad": "grave"},
    {"clave": "canal_denuncia_interno",
     "descripcion": "Canal interno (email/buzón) para denunciar violaciones.",
     "severidad": "media"},
    {"clave": "evidencias_no_comunicacion_fuera_jornada",
     "descripcion": "Evidencias de NO comunicación digital fuera de jornada.",
     "severidad": "grave"},
    {"clave": "criterios_emergencia_documentados",
     "descripcion": "Criterios de emergencia documentados (cuándo SÍ contactar).",
     "severidad": "media"},
    {"clave": "horarios_jornada_claros_contrato",
     "descripcion": "Horarios de jornada claramente definidos en contrato individual.",
     "severidad": "muy_grave"},
    {"clave": "auditoria_anual",
     "descripcion": "Auditoría interna anual de cumplimiento.",
     "severidad": "leve"},
]


class DesconexionDigitalClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def checklist_cumplimiento(
        self, rfc: str, faltas_marcadas: list[str] | None = None,
    ) -> dict[str, Any]:
        if not rfc or len(rfc) < 12:
            raise ValidationError(f"RFC inválido: {rfc!r}")
        faltas_marcadas = set(faltas_marcadas or [])

        checklist = []
        no_cumplidas = 0
        for item in CHECKLIST_REFORMA_2026:
            cumplida = item["clave"] not in faltas_marcadas
            if not cumplida:
                no_cumplidas += 1
            checklist.append({**item, "cumplida": cumplida})

        score = round(100 * (len(checklist) - no_cumplidas) / len(checklist))
        self._bitacora.log("checklist_cumplimiento", success=True,
                           params_summary={"rfc_hash": self._bitacora.hash_sensitive(rfc),
                                           "no_cumplidas": no_cumplidas})
        return mark_simulated({
            "rfc": rfc,
            "score_cumplimiento": score,
            "total": len(checklist),
            "no_cumplidas": no_cumplidas,
            "checklist": checklist,
            "base_legal": "LFT Art. 132 reforma marzo 2026",
            "fecha_evaluacion": datetime.now(timezone.utc).isoformat(),
        })

    def generar_politica(
        self, rfc: str, razon_social: str, jornada_inicio: str, jornada_fin: str,
        canal_denuncia_email: str | None = None,
    ) -> dict[str, Any]:
        if not rfc or len(rfc) < 12:
            raise ValidationError(f"RFC inválido: {rfc!r}")
        canal = canal_denuncia_email or f"denuncias-rh@{rfc.lower()}.mx"
        contenido = _plantilla(razon_social, rfc, jornada_inicio, jornada_fin, canal)
        return mark_simulated({
            "rfc": rfc,
            "razon_social": razon_social,
            "contenido_md": contenido,
            "fecha_emision": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "longitud_chars": len(contenido),
            "base_legal": "LFT Art. 132 reforma marzo 2026",
        })

    def template_capacitacion(self) -> dict[str, Any]:
        return mark_simulated({
            "titulo": "Capacitación obligatoria — Desconexión Digital LFT Art. 132 (Reforma marzo 2026)",
            "duracion_estimada_min": 45,
            "audiencia": "Personal con mando jerárquico + RRHH",
            "agenda": [
                {"tema": "Marco legal", "minutos": 5,
                 "puntos": ["LFT Art. 132 reforma marzo 2026",
                             "Sanciones STPS (50-5000 UMAs)",
                             "Cómo se evalúa la violación"]},
                {"tema": "Política interna", "minutos": 10,
                 "puntos": ["Texto política", "Jornadas claras",
                             "Excepciones por emergencia documentadas"]},
                {"tema": "Buenas prácticas operativas", "minutos": 20,
                 "puntos": ["NO enviar emails/WA fuera jornada",
                             "Programar entregas con tiempo razonable",
                             "Respetar vacaciones y días libres",
                             "Estados ausentes en herramientas (Slack, Teams)"]},
                {"tema": "Canal de denuncia interno", "minutos": 5,
                 "puntos": ["Cómo denunciar", "Confidencialidad",
                             "Plazo de respuesta (10 días hábiles)"]},
                {"tema": "Q&A + firma asistencia", "minutos": 5, "puntos": []},
            ],
            "evidencias_a_conservar": [
                "Lista asistencia firmada",
                "Material capacitación",
                "Examen final corregido",
                "Constancia individual entregada",
            ],
            "frecuencia_minima": "Anual + al ingreso de cada nuevo mando",
        })


def _plantilla(razon_social: str, rfc: str, ji: str, jf: str, canal: str) -> str:
    return f"""# Política de Desconexión Digital

**Empresa:** {razon_social}
**RFC:** {rfc}
**Vigencia:** Reforma LFT Art. 132 marzo 2026

## 1. Reconocimiento del derecho

{razon_social} reconoce el derecho de todas las personas trabajadoras a la
desconexión digital, conforme al Art. 132 de la Ley Federal del Trabajo
(reforma marzo 2026).

## 2. Horario laboral establecido

La jornada laboral inicia a las {ji} hrs y concluye a las {jf} hrs en días
hábiles, salvo lo pactado individualmente en cada contrato.

## 3. Obligación patronal

Fuera del horario laboral, días de descanso, vacaciones e incapacidades:
- NO se enviarán correos electrónicos, mensajes de WhatsApp, llamadas u otras
  comunicaciones digitales relacionadas con el trabajo.
- NO se exigirá respuesta inmediata.
- Las herramientas digitales (Slack, Teams, Workplace, Asana, etc.) podrán ser
  silenciadas por el trabajador sin sanción.

## 4. Excepciones por emergencia

Sólo en caso de **emergencia documentada** (incidente que ponga en riesgo
operación crítica, salud o seguridad) se podrá contactar fuera de jornada.
Cada excepción debe registrarse con: motivo, hora, persona contactada y
duración. Estas excepciones NO sustituyen el descanso obligatorio.

## 5. Capacitación a mandos

Personal con mando jerárquico recibirá capacitación inicial al ingreso y
refrescamiento anual. La asistencia se documenta y conserva por 5 años.

## 6. Canal de denuncia interno

Cualquier trabajador que considere violado este derecho puede reportarlo a:
**{canal}**

Las denuncias se atienden de forma confidencial en máximo 10 días hábiles.

## 7. Sanciones internas

El incumplimiento por parte de personal con mando se sanciona conforme al
Reglamento Interior de Trabajo, sin perjuicio de las sanciones que pudiera
imponer la STPS al patrón.

## 8. Vigencia y revisión

Esta política entra en vigor a partir de su publicación y se revisará al menos
una vez al año o tras cualquier reforma legal relevante.

---

**Representante legal:** ____________________  Fecha: __________

**Responsable de RRHH:** ____________________  Fecha: __________
"""
