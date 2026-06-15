"""Cliente mp_cofepris_aviso_funcionamiento.

Clasificación COFEPRIS por giro:
- A: bajo riesgo (no requiere aviso)
- B: riesgo medio (requiere Aviso de Funcionamiento)
- C: alto riesgo (requiere Aviso + responsable sanitario)
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "cofepris_aviso"
URL_COFEPRIS_AVISO = "https://www.gob.mx/cofepris/acciones-y-programas/avisos-de-funcionamiento"

GiroCOFEPRIS = Literal["A", "B", "C"]


# Catálogo simplificado (real es Anexo COFEPRIS extensa)
CLASIFICACION_GIROS: dict[str, dict] = {
    # Riesgo bajo (A): tiendas, oficinas, papelerías
    "tienda_abarrotes": {"giro_cofepris": "A", "rama": "comercio",
                          "requiere_aviso": False, "tiempo_resolucion": "N/A"},
    "oficina_administrativa": {"giro_cofepris": "A", "rama": "servicios",
                                "requiere_aviso": False, "tiempo_resolucion": "N/A"},
    "papeleria": {"giro_cofepris": "A", "rama": "comercio",
                   "requiere_aviso": False, "tiempo_resolucion": "N/A"},
    # Riesgo medio (B): restaurantes, salones, talleres, gimnasios
    "restaurante": {"giro_cofepris": "B", "rama": "alimentos",
                     "requiere_aviso": True, "tiempo_resolucion": "10 días hábiles"},
    "cafeteria": {"giro_cofepris": "B", "rama": "alimentos",
                   "requiere_aviso": True, "tiempo_resolucion": "10 días hábiles"},
    "panaderia": {"giro_cofepris": "B", "rama": "alimentos",
                   "requiere_aviso": True, "tiempo_resolucion": "10 días hábiles"},
    "carniceria": {"giro_cofepris": "B", "rama": "alimentos",
                    "requiere_aviso": True, "tiempo_resolucion": "10 días hábiles"},
    "salon_belleza": {"giro_cofepris": "B", "rama": "estetica",
                       "requiere_aviso": True, "tiempo_resolucion": "10 días hábiles"},
    "barberia": {"giro_cofepris": "B", "rama": "estetica",
                  "requiere_aviso": True, "tiempo_resolucion": "10 días hábiles"},
    "spa": {"giro_cofepris": "B", "rama": "estetica",
             "requiere_aviso": True, "tiempo_resolucion": "10 días hábiles"},
    "tatuajes_piercing": {"giro_cofepris": "B", "rama": "estetica",
                           "requiere_aviso": True, "tiempo_resolucion": "15 días hábiles"},
    "gimnasio": {"giro_cofepris": "B", "rama": "servicios",
                  "requiere_aviso": True, "tiempo_resolucion": "10 días hábiles"},
    # Riesgo alto (C): farmacias, consultorios, laboratorios, ópticas, funerarias
    "farmacia": {"giro_cofepris": "C", "rama": "salud",
                  "requiere_aviso": True, "tiempo_resolucion": "20 días hábiles",
                  "requiere_responsable_sanitario": True},
    "consultorio_medico": {"giro_cofepris": "C", "rama": "salud",
                            "requiere_aviso": True, "tiempo_resolucion": "15 días hábiles",
                            "requiere_responsable_sanitario": True},
    "consultorio_dental": {"giro_cofepris": "C", "rama": "salud",
                            "requiere_aviso": True, "tiempo_resolucion": "15 días hábiles",
                            "requiere_responsable_sanitario": True},
    "laboratorio_clinico": {"giro_cofepris": "C", "rama": "salud",
                             "requiere_aviso": True, "tiempo_resolucion": "20 días hábiles",
                             "requiere_responsable_sanitario": True},
    "optica": {"giro_cofepris": "C", "rama": "salud",
                "requiere_aviso": True, "tiempo_resolucion": "15 días hábiles",
                "requiere_responsable_sanitario": True},
    "funeraria": {"giro_cofepris": "C", "rama": "servicios",
                   "requiere_aviso": True, "tiempo_resolucion": "20 días hábiles",
                   "requiere_responsable_sanitario": True},
    "veterinaria": {"giro_cofepris": "C", "rama": "salud_animal",
                     "requiere_aviso": True, "tiempo_resolucion": "15 días hábiles",
                     "requiere_responsable_sanitario": True},
    "residencia_geriatrica": {"giro_cofepris": "C", "rama": "salud",
                                "requiere_aviso": True, "tiempo_resolucion": "30 días hábiles",
                                "requiere_responsable_sanitario": True,
                                "nom_aplicable": "NOM-167-SSA1"},
}


class COFEPRISAvisoClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def clasificar_giro(self, actividad: str) -> dict[str, Any]:
        a = (actividad or "").lower().strip().replace(" ", "_").replace("-", "_")
        if a not in CLASIFICACION_GIROS:
            return mark_simulated({
                "actividad": actividad,
                "giro_cofepris": "no_clasificado",
                "requiere_aviso": None,
                "nota": "Actividad no en catálogo simplificado. Consultar Anexo COFEPRIS oficial.",
            })
        return mark_simulated({"actividad": actividad, **CLASIFICACION_GIROS[a]})

    def requisitos_aviso(self, actividad: str, estado: str) -> dict[str, Any]:
        if not estado or len(estado) < 2:
            raise ValidationError(f"estado inválido: {estado!r}")
        a = (actividad or "").lower().strip().replace(" ", "_").replace("-", "_")
        if a not in CLASIFICACION_GIROS:
            raise ValidationError(f"actividad no en catálogo: {actividad}")
        info = CLASIFICACION_GIROS[a]
        if not info.get("requiere_aviso"):
            return mark_simulated({
                "actividad": actividad,
                "giro_cofepris": info["giro_cofepris"],
                "requiere_aviso": False,
                "nota": "Giro A — no requiere aviso COFEPRIS.",
            })

        requisitos = [
            "Acta constitutiva / Identificación PF",
            "RFC + CSF SAT",
            "Comprobante de domicilio (no mayor 3 meses)",
            "Croquis del establecimiento",
            "Aviso de uso de suelo municipal",
        ]
        if info.get("requiere_responsable_sanitario"):
            requisitos.extend([
                "Cédula profesional responsable sanitario",
                "Carta responsiva firmada",
            ])
        if info.get("nom_aplicable"):
            requisitos.append(f"Cumplimiento {info['nom_aplicable']}")

        return mark_simulated({
            "actividad": actividad,
            "estado": estado,
            "giro_cofepris": info["giro_cofepris"],
            "tiempo_resolucion": info["tiempo_resolucion"],
            "requisitos": requisitos,
            "costo_aproximado_mxn": _costo_aviso(info["giro_cofepris"]),
            "url_inicio": URL_COFEPRIS_AVISO,
        })

    def consultar_aviso(self, identificador: str) -> dict[str, Any]:
        """Mock: consulta aviso por RFC o folio."""
        if len(identificador or "") < 8:
            raise ValidationError(f"identificador inválido: {identificador!r}")
        last = sum(ord(c) for c in identificador) % 5
        vigente = last != 0
        return mark_simulated({
            "identificador": identificador,
            "vigente": vigente,
            "tipo_giro_cofepris": ["A", "B", "B", "C", "C"][last],
            "fecha_vencimiento": "2027-12-31" if vigente else "2025-08-15",
            "fuente": URL_COFEPRIS_AVISO,
        })

    def listar_giros_catalogo(self) -> dict[str, Any]:
        return {
            "total": len(CLASIFICACION_GIROS),
            "por_clasificacion": {
                "A": sum(1 for v in CLASIFICACION_GIROS.values() if v["giro_cofepris"] == "A"),
                "B": sum(1 for v in CLASIFICACION_GIROS.values() if v["giro_cofepris"] == "B"),
                "C": sum(1 for v in CLASIFICACION_GIROS.values() if v["giro_cofepris"] == "C"),
            },
            "giros": [{"actividad": k, **v} for k, v in CLASIFICACION_GIROS.items()],
        }


def _costo_aviso(giro: str) -> float:
    return {"A": 0.0, "B": 0.0, "C": 0.0}[giro]  # COFEPRIS aviso es gratuito; pago es DOF derechos si renovación
