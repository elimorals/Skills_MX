"""Cliente mp_desconexion_digital — derecho a la desconexión (teletrabajo).

Verificado 2026-10-14 contra la LFT vigente (diputados.gob.mx, última reforma DOF 14-05-2026):
no existe una "reforma LFT Art. 132 de marzo 2026" sobre desconexión digital. El único
fundamento legal es para teletrabajo (relaciones > 40 % del tiempo fuera, Art. 330-A):
- LFT Art. 330-E fr. VI (DOF 11-01-2021): respetar el derecho a la desconexión al término de la jornada.
- LFT Art. 330-B fr. VI: el contrato fija mecanismos de contacto y la duración/distribución de horarios.
- NOM-037-STPS-2023 5.2 d) y e) (DOF 08-06-2023): la Política de Teletrabajo define reglas de
  contacto que no interfieran trabajo-familia y el derecho a pausas y a la desconexión (incluida la
  de TIC) fuera de jornada, vacaciones, permisos y licencias.
Multa por incumplir: Art. 1002 LFT (50-5000 UMA) o Art. 994 fr. V si se trata de la NOM.

Los demás ítems (capacitación de mandos, canal de denuncia, auditoría) son buenas prácticas,
marcadas `obligatorio: false`.
"""
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


NAMESPACE = "desconexion_digital"


URL_LFT = "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf"
URL_NOM037 = "https://dof.gob.mx/nota_detalle.php?codigo=5691672&fecha=08/06/2023"

CHECKLIST_DESCONEXION = [
    {"clave": "respetar_desconexion_fin_jornada", "obligatorio": True,
     "descripcion": "No exigir actividad ni respuesta por medios digitales al término de la jornada.",
     "base_legal": "LFT Art. 330-E fr. VI", "severidad": "grave"},
    {"clave": "politica_teletrabajo_con_desconexion", "obligatorio": True,
     "descripcion": ("Política de Teletrabajo escrita con horario, pausas y desconexión (incluida TIC) "
                     "fuera de jornada, vacaciones, permisos y licencias."),
     "base_legal": "NOM-037-STPS-2023 5.2 e)", "severidad": "grave"},
    {"clave": "reglas_contacto_proporcionales", "obligatorio": True,
     "descripcion": "Mecanismos y reglas de contacto que no interfieran la relación trabajo-familia.",
     "base_legal": "NOM-037-STPS-2023 5.2 d)", "severidad": "media"},
    {"clave": "contrato_con_horarios_y_contacto", "obligatorio": True,
     "descripcion": "Contrato escrito con mecanismos de contacto y duración/distribución de horarios.",
     "base_legal": "LFT Art. 330-B fr. VI", "severidad": "muy_grave"},
    {"clave": "capacitacion_supervisores", "obligatorio": False,
     "descripcion": "Capacitar a mandos sobre respetar la desconexión.",
     "base_legal": None, "severidad": "media"},
    {"clave": "canal_denuncia_interno", "obligatorio": False,
     "descripcion": "Canal interno para reportar contactos fuera de jornada.",
     "base_legal": None, "severidad": "leve"},
    {"clave": "criterios_emergencia_documentados", "obligatorio": False,
     "descripcion": "Criterios de emergencia documentados (cuándo sí contactar).",
     "base_legal": None, "severidad": "leve"},
]


class DesconexionDigitalClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def checklist_cumplimiento(
        self, rfc: str, faltas_marcadas: list[str] | None = None, modalidad_teletrabajo: bool = True,
    ) -> dict[str, Any]:
        if not rfc or len(rfc) < 12:
            raise ValidationError(f"RFC inválido: {rfc!r}")
        faltas_marcadas = set(faltas_marcadas or [])

        checklist = []
        no_cumplidas = 0
        for item in CHECKLIST_DESCONEXION:
            if item["obligatorio"] and not modalidad_teletrabajo:
                continue  # sin teletrabajo no hay obligación legal de desconexión
            cumplida = item["clave"] not in faltas_marcadas
            if not cumplida:
                no_cumplidas += 1
            checklist.append({**item, "cumplida": cumplida})

        score = round(100 * (len(checklist) - no_cumplidas) / len(checklist))
        self._bitacora.log("checklist_cumplimiento", success=True,
                           params_summary={"rfc_hash": self._bitacora.hash_sensitive(rfc),
                                           "no_cumplidas": no_cumplidas})
        return {
            "rfc": rfc,
            "modalidad_teletrabajo": modalidad_teletrabajo,
            "score_cumplimiento": score,
            "total": len(checklist),
            "no_cumplidas": no_cumplidas,
            "obligatorias_incumplidas": sum(1 for c in checklist if c["obligatorio"] and not c["cumplida"]),
            "checklist": checklist,
            "base_legal": "LFT Arts. 330-B fr. VI y 330-E fr. VI; NOM-037-STPS-2023 5.2",
            "nota": (None if modalidad_teletrabajo else
                     "Sin teletrabajo (> 40 % del tiempo fuera, Art. 330-A) no hay obligación legal de "
                     "desconexión; los ítems restantes son buenas prácticas."),
            "fuentes": [URL_LFT, URL_NOM037],
            "fecha_evaluacion": datetime.now(timezone.utc).isoformat(),
        }

    def generar_politica(
        self, rfc: str, razon_social: str, jornada_inicio: str, jornada_fin: str,
        canal_denuncia_email: str | None = None,
    ) -> dict[str, Any]:
        if not rfc or len(rfc) < 12:
            raise ValidationError(f"RFC inválido: {rfc!r}")
        canal = canal_denuncia_email or f"denuncias-rh@{rfc.lower()}.mx"
        contenido = _plantilla(razon_social, rfc, jornada_inicio, jornada_fin, canal)
        return {
            "rfc": rfc,
            "razon_social": razon_social,
            "contenido_md": contenido,
            "fecha_emision": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "longitud_chars": len(contenido),
            "base_legal": "LFT Art. 330-E fr. VI; NOM-037-STPS-2023 5.2 e)",
            "nota": "Plantilla orientativa; revisar con abogado laboral.",
        }

    def template_capacitacion(self) -> dict[str, Any]:
        return {
            "titulo": "Capacitación — Desconexión digital en teletrabajo (LFT 330-E fr. VI, NOM-037)",
            "obligatoria": False,
            "nota": ("La LFT no exige esta capacitación específica; NOM-037 5.9 pide capacitación anual "
                     "en SST al personal en teletrabajo."),
            "duracion_estimada_min": 45,
            "audiencia": "Personal con mando jerárquico + RRHH",
            "agenda": [
                {"tema": "Marco legal", "minutos": 5,
                 "puntos": ["LFT Art. 330-E fr. VI y NOM-037 5.2 e)",
                             "Multas LFT: Art. 1002 (50-5000 UMA) / 994 fr. V (250-5000 UMA)",
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
            "frecuencia_sugerida": "Anual + al ingreso de cada nuevo mando",
        }


def _plantilla(razon_social: str, rfc: str, ji: str, jf: str, canal: str) -> str:
    return f"""# Política de Desconexión Digital

**Empresa:** {razon_social}
**RFC:** {rfc}
**Fundamento:** LFT Art. 330-E fr. VI; NOM-037-STPS-2023 numeral 5.2 e)

## 1. Reconocimiento del derecho

{razon_social} reconoce el derecho a la desconexión digital de las personas
trabajadoras en teletrabajo (LFT Art. 330-E fr. VI) y lo extiende como buena práctica
al resto del personal.

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
