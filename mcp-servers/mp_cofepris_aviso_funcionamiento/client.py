"""Cliente mp_cofepris_aviso_funcionamiento — licencia sanitaria vs aviso de funcionamiento.

Base legal (Ley General de Salud, texto vigente en
https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf, últimas reformas DOF 15-01-2026,
consultado 2026-10-14):

- Art. 198: requieren **autorización (licencia) sanitaria** los establecimientos dedicados a
  I. proceso de medicamentos con estupefacientes/psicotrópicos, vacunas, hemoderivados…;
  II. fabricación de medicamentos, plaguicidas, sustancias tóxicas; III. aplicación de plaguicidas;
  IV. fuentes de radiación con fines médicos o de diagnóstico; V. actos quirúrgicos u obstétricos
  y hemodiálisis; VI. centros de mezcla parenteral. Antes de iniciar actividades.
- Art. 197: "proceso" incluye el expendio o suministro al público → una farmacia que vende
  estupefacientes/psicotrópicos cae en Art. 198 fr. I (y Art. 258).
- Art. 200 Bis: **aviso de funcionamiento** para los establecimientos que no requieran licencia
  y que determine el Acuerdo de la SSA (clasificación por actividad, publicado en DOF); se presenta
  ≥ 30 días antes de iniciar, con los datos de las fracciones I-VI.
- Art. 260 fr. IV: boticas y farmacias solo dan aviso de responsable sanitario si expenden
  estupefacientes o psicotrópicos.

La antigua clasificación "giro A/B/C", los tiempos de resolución y la consulta de vigencia por
RFC eran inventados: no existen en la ley ni hay consulta pública de avisos (datos.gob.mx no tiene
datasets de COFEPRIS, revisado 2026-10-14). La consulta pasa a handoff humano.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.portal_handoff import armar_handoff  # noqa: E402


NAMESPACE = "cofepris_aviso"
URL_COFEPRIS = "https://www.gob.mx/cofepris"
URL_LGS = "https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf"

LICENCIA = "licencia_sanitaria"
AVISO = "aviso_funcionamiento"
VERIFICAR = "verificar_acuerdo_ssa"

# Cada giro con su fundamento. "aviso" = no está en Art. 198; si el Acuerdo SSA lo lista,
# requiere aviso (Art. 200 Bis). Los giros sin insumos para la salud quedan en "verificar".
CLASIFICACION_GIROS: dict[str, dict[str, Any]] = {
    # Art. 198 → licencia sanitaria
    "hospital_quirurgico": {"tramite": LICENCIA, "fundamento": "Art. 198 fr. V LGS (actos quirúrgicos u obstétricos)"},
    "hemodialisis": {"tramite": LICENCIA, "fundamento": "Art. 198 fr. V LGS"},
    "gabinete_rayos_x": {"tramite": LICENCIA, "fundamento": "Art. 198 fr. IV LGS (radiación con fines de diagnóstico)"},
    "consultorio_dental_con_rayos_x": {"tramite": LICENCIA, "fundamento": "Art. 198 fr. IV LGS"},
    "fumigadora": {"tramite": LICENCIA, "fundamento": "Art. 198 fr. III LGS (aplicación de plaguicidas)"},
    "fabrica_medicamentos": {"tramite": LICENCIA, "fundamento": "Art. 198 fr. II LGS; Art. 258"},
    "farmacia_con_controlados": {"tramite": LICENCIA, "responsable_sanitario": True,
                                 "fundamento": "Arts. 197, 198 fr. I y 258 LGS; responsable Art. 260 fr. IV"},
    # Sin licencia → aviso de funcionamiento si el Acuerdo SSA los clasifica (Art. 200 Bis)
    "farmacia_sin_controlados": {"tramite": AVISO, "responsable_sanitario": False,
                                 "fundamento": "Art. 200 Bis LGS; Art. 260 fr. IV (sin aviso de responsable)"},
    "consultorio_medico": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "consultorio_dental": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS (sin equipo de rayos X)"},
    "laboratorio_clinico": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "optica": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "restaurante": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "cafeteria": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "panaderia": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "carniceria": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "salon_belleza": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "barberia": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "spa": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "tatuajes_piercing": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "funeraria": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "residencia_geriatrica": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    "veterinaria": {"tramite": AVISO, "fundamento": "Art. 200 Bis LGS"},
    # Sin relación directa con insumos de salud: depende del Acuerdo / regulación local
    "tienda_abarrotes": {"tramite": VERIFICAR, "fundamento": "Art. 200 Bis LGS (si vende alimentos/bebidas, revisar el Acuerdo)"},
    "gimnasio": {"tramite": VERIFICAR, "fundamento": "Art. 200 Bis LGS"},
    "papeleria": {"tramite": VERIFICAR, "fundamento": "Art. 200 Bis LGS"},
    "oficina_administrativa": {"tramite": VERIFICAR, "fundamento": "Art. 200 Bis LGS"},
}

REQUISITOS_AVISO_ART_200_BIS = [
    "Nombre y domicilio de la persona física o moral propietaria",
    "Domicilio del establecimiento y fecha de inicio de operaciones",
    "Procesos utilizados y línea(s) de productos",
    "Declaración bajo protesta de decir verdad de cumplimiento",
    "Clave de la actividad del establecimiento",
    "Número de cédula profesional del responsable sanitario, en su caso",
]


def _norm(actividad: str) -> str:
    return (actividad or "").lower().strip().replace(" ", "_").replace("-", "_")


class COFEPRISAvisoClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def clasificar_giro(self, actividad: str) -> dict[str, Any]:
        a = _norm(actividad)
        if a not in CLASIFICACION_GIROS:
            return {
                "actividad": actividad,
                "tramite": None,
                "nota": "Actividad fuera del catálogo; revisar Art. 198 LGS y el Acuerdo SSA de aviso.",
                "fuente": URL_LGS,
            }
        info = CLASIFICACION_GIROS[a]
        return {
            "actividad": actividad,
            **info,
            "requiere_licencia": info["tramite"] == LICENCIA,
            "requiere_aviso": True if info["tramite"] == AVISO else (None if info["tramite"] == VERIFICAR else False),
            "fuente": URL_LGS,
        }

    def requisitos_aviso(self, actividad: str, estado: str) -> dict[str, Any]:
        if not estado or len(estado) < 2:
            raise ValidationError(f"estado inválido: {estado!r}")
        a = _norm(actividad)
        if a not in CLASIFICACION_GIROS:
            raise ValidationError(f"actividad no en catálogo: {actividad}")
        info = CLASIFICACION_GIROS[a]
        if info["tramite"] == LICENCIA:
            return {"actividad": actividad, "estado": estado, "tramite": LICENCIA,
                    "requiere_aviso": False,
                    "nota": "Requiere licencia sanitaria previa al inicio de actividades (Art. 198 LGS), no aviso.",
                    "fundamento": info["fundamento"], "fuente": URL_LGS}
        return {
            "actividad": actividad,
            "estado": estado,
            "tramite": info["tramite"],
            "requiere_aviso": info["tramite"] == AVISO or None,
            "plazo": "Al menos 30 días antes de iniciar operaciones (Art. 200 Bis LGS)",
            "presentar_ante": "Secretaría de Salud (COFEPRIS) o el gobierno de la entidad federativa",
            "requisitos": REQUISITOS_AVISO_ART_200_BIS,
            "fundamento": info["fundamento"],
            "fuente": URL_LGS,
        }

    def consultar_aviso(self, identificador: str) -> dict[str, Any]:
        """No hay consulta pública de avisos: handoff humano (antes inventaba vigencia por hash)."""
        if len(identificador or "") < 8:
            raise ValidationError(f"identificador inválido: {identificador!r}")
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"identificador": identificador, "vigente": True})
        return armar_handoff(
            motivo="sin_consulta_publica",
            detalle="COFEPRIS no publica una consulta de avisos de funcionamiento por RFC o folio.",
            url=URL_COFEPRIS,
            pasos=[
                "Pedir al establecimiento el acuse del aviso o la licencia sanitaria.",
                "O consultar a COFEPRIS / la autoridad sanitaria estatal con el número de ingreso.",
            ],
            identificador=identificador,
            vigente=None,
        )

    def listar_giros_catalogo(self) -> dict[str, Any]:
        por_tramite: dict[str, int] = {}
        for v in CLASIFICACION_GIROS.values():
            por_tramite[v["tramite"]] = por_tramite.get(v["tramite"], 0) + 1
        return {
            "total": len(CLASIFICACION_GIROS),
            "por_tramite": por_tramite,
            "giros": [{"actividad": k, **v} for k, v in CLASIFICACION_GIROS.items()],
            "fuente": URL_LGS,
        }
