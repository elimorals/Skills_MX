"""Cliente mp_sedatu_uso_suelo."""
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
from shared.errors import ValidationError, NotFoundError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "sedatu_uso_suelo"
URL_RETYS = "https://www.gob.mx/conamer/registro-nacional-de-tramites-y-servicios"

# Catálogo de trámites más comunes por categoría (mock simplificado)
TRAMITES_CATALOGO: dict[str, dict] = {
    "licencia_uso_suelo": {
        "nombre": "Licencia de uso de suelo",
        "duracion_dias_habiles": "15-30",
        "costo_aprox_mxn": "$500 - $5,000 según municipio",
        "requisitos_base": [
            "Solicitud firmada",
            "Identificación del solicitante",
            "Comprobante de propiedad o contrato",
            "Croquis de localización",
            "Boleta predial vigente",
        ],
    },
    "licencia_construccion": {
        "nombre": "Licencia de construcción",
        "duracion_dias_habiles": "20-60",
        "costo_aprox_mxn": "Variable según m² ($20-$100 por m²)",
        "requisitos_base": [
            "Licencia de uso de suelo previa",
            "Memoria descriptiva y de cálculo estructural",
            "Planos arquitectónicos firmados por DRO",
            "Manifestación de impacto urbano (si m² > 1000)",
            "Identificación del propietario y DRO",
        ],
    },
    "anuncio_publicidad": {
        "nombre": "Permiso de anuncio publicitario",
        "duracion_dias_habiles": "10-20",
        "costo_aprox_mxn": "$1,000 - $15,000/año",
        "requisitos_base": [
            "Plano del anuncio",
            "Carta responsiva estructural si > 4m²",
            "Pago de derechos",
        ],
    },
    "subdivision_predios": {
        "nombre": "Subdivisión de predios",
        "duracion_dias_habiles": "30-90",
        "costo_aprox_mxn": "$2,000 - $30,000",
        "requisitos_base": [
            "Plano topográfico",
            "Constancia de no adeudo predial",
            "Aprobación CFE y agua",
        ],
    },
    "fusion_predios": {
        "nombre": "Fusión de predios",
        "duracion_dias_habiles": "30-60",
        "costo_aprox_mxn": "$2,000 - $20,000",
        "requisitos_base": [
            "Escrituras de los predios a fusionar",
            "Plano topográfico de conjunto",
            "Constancia de no adeudo predial",
        ],
    },
    "licencia_funcionamiento_municipal": {
        "nombre": "Licencia de funcionamiento (apertura local)",
        "duracion_dias_habiles": "10-30",
        "costo_aprox_mxn": "$500 - $5,000",
        "requisitos_base": [
            "Uso de suelo permitido",
            "Aviso COFEPRIS (si aplica)",
            "Programa Interno PC",
            "Inspección bomberos",
        ],
    },
}


# Tipos de uso de suelo más comunes
USOS_SUELO_PERMITIDOS = [
    "habitacional_unifamiliar", "habitacional_multifamiliar",
    "habitacional_mixto", "comercial", "comercio_servicios",
    "industrial_ligero", "industrial_pesado",
    "equipamiento", "areas_verdes", "areas_naturales",
    "uso_mixto_h_c", "centro_urbano", "corredor_urbano",
]


class SEDATUUsoSueloClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def buscar_tramite(self, estado: str, municipio: str, clave_tramite: str) -> dict[str, Any]:
        if not estado or not municipio:
            raise ValidationError("estado y municipio requeridos")
        if clave_tramite not in TRAMITES_CATALOGO:
            raise NotFoundError(f"Trámite no en catálogo: {clave_tramite}")
        info = TRAMITES_CATALOGO[clave_tramite]
        return mark_simulated({
            "estado": estado,
            "municipio": municipio,
            "clave_tramite": clave_tramite,
            "nombre": info["nombre"],
            "duracion_dias_habiles": info["duracion_dias_habiles"],
            "costo_aprox_mxn": info["costo_aprox_mxn"],
            "requisitos": info["requisitos_base"],
            "fuente_canonica": "RETyS — Registro Estatal de Trámites y Servicios",
            "nota": "Requisitos pueden variar por municipio. Confirmar con autoridad local.",
        })

    def consultar_uso_suelo_permitido(
        self, estado: str, municipio: str, giro_propuesto: str,
    ) -> dict[str, Any]:
        if not estado or not municipio:
            raise ValidationError("estado y municipio requeridos")
        g = (giro_propuesto or "").lower()
        # Mock heurístico: la mayoría de giros comerciales se permiten en comercio/mixto
        permitido = True
        usos_aplicables = []
        if "industrial" in g:
            usos_aplicables = ["industrial_ligero", "industrial_pesado"]
        elif "habitacional" in g or "casa" in g or "vivienda" in g:
            usos_aplicables = ["habitacional_unifamiliar", "habitacional_multifamiliar"]
        elif any(x in g for x in ["restaurante", "tienda", "oficina", "comercio", "servicio"]):
            usos_aplicables = ["comercial", "comercio_servicios", "uso_mixto_h_c", "centro_urbano"]
        else:
            usos_aplicables = ["uso_mixto_h_c"]
        return mark_simulated({
            "estado": estado,
            "municipio": municipio,
            "giro_propuesto": giro_propuesto,
            "permitido": permitido,
            "usos_suelo_compatibles": usos_aplicables,
            "verificacion_plan_desarrollo_urbano": "Requerida — consultar PDU municipal",
            "fuente": URL_RETYS,
        })

    def estimar_construccion(
        self, estado: str, municipio: str, m2_construir: float, uso: str = "habitacional",
    ) -> dict[str, Any]:
        if m2_construir <= 0:
            raise ValidationError("m2 debe ser > 0")
        if m2_construir > 10000:
            categoria = "gran_escala_requiere_MIA_EIU"
        elif m2_construir > 1000:
            categoria = "mediana_escala_requiere_MIU"
        else:
            categoria = "pequena_escala_estandar"
        costo_por_m2 = {
            "habitacional": 50, "comercial": 75, "industrial": 100,
        }.get(uso.lower(), 50)
        derechos = m2_construir * costo_por_m2
        return mark_simulated({
            "estado": estado,
            "municipio": municipio,
            "m2_construir": m2_construir,
            "uso": uso,
            "categoria_regulatoria": categoria,
            "derechos_municipales_aprox_mxn": round(derechos, 2),
            "estudios_requeridos": _estudios_para(categoria),
            "tiempo_total_estimado_dias_habiles": "30-90" if "pequena" in categoria else "90-180",
        })

    def listar_tramites(self) -> dict[str, Any]:
        return {
            "total": len(TRAMITES_CATALOGO),
            "tramites": [
                {"clave": k, "nombre": v["nombre"],
                 "duracion": v["duracion_dias_habiles"]}
                for k, v in TRAMITES_CATALOGO.items()
            ],
            "usos_suelo_catalogo": USOS_SUELO_PERMITIDOS,
            "fuente": URL_RETYS,
        }


def _estudios_para(categoria: str) -> list[str]:
    if "gran_escala" in categoria:
        return ["MIA (Manifestación Impacto Ambiental)",
                "EIU (Estudio Impacto Urbano)",
                "MIV (Movilidad)",
                "Vialidad CFE/Agua/Drenaje"]
    if "mediana_escala" in categoria:
        return ["MIU (Memoria Impacto Urbano)",
                "Carta CFE/Agua"]
    return ["Memoria de cálculo estructural", "Planos firmados DRO"]
