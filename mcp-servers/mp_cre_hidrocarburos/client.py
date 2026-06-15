"""Cliente mp_cre_hidrocarburos."""
from __future__ import annotations

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
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "cre_hidrocarburos"
URL_CRE = "https://www.gob.mx/cre/acciones-y-programas/obligaciones-de-los-permisionarios-de-comercializacion-de-hidrocarburos-petroliferos-y-petroquimicos"
URL_SAT_VOLUMETRICOS = "https://www.sat.gob.mx/minisitio/ControlesVolumetricos/consulta_permisos.html"

# Umbral consumo Anexo 30 SAT (litros/mes/instalación)
UMBRAL_ANEXO30_LITROS_MES = 75_714.0

TIPOS_PERMISO = {
    "comercializacion_petroliferos": "Comercialización de petrolíferos (gasolina, diésel)",
    "comercializacion_gas_lp": "Comercialización de gas LP",
    "comercializacion_gas_natural": "Comercialización de gas natural",
    "expendio_publico": "Expendio al público (gasolinera)",
    "transporte": "Transporte por ducto/auto-tanque",
    "almacenamiento": "Almacenamiento",
}

NUM_PERMISO_RE = re.compile(r"^[A-Z]{2,4}/\d{2,6}/\d{4}$|^\d{4,12}$")


class CREClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_permiso(self, identificador: str) -> dict[str, Any]:
        if not identificador or len(identificador) < 4:
            raise ValidationError(f"identificador inválido: {identificador!r}")
        last = sum(ord(c) for c in identificador) % 5
        tipos = list(TIPOS_PERMISO.keys())
        return mark_simulated({
            "identificador": identificador,
            "vigente": last != 0,
            "tipo_permiso": tipos[last % len(tipos)],
            "tipo_descripcion": TIPOS_PERMISO[tipos[last % len(tipos)]],
            "fecha_vencimiento": "2030-12-31" if last != 0 else "2024-06-30",
            "fuente": URL_CRE,
        })

    def calendar_reporte_mensual(self, anio: int, mes_actual: int) -> dict[str, Any]:
        if anio < 2020 or anio > 2099:
            raise ValidationError("anio fuera de rango")
        if mes_actual < 1 or mes_actual > 12:
            raise ValidationError("mes_actual debe ser 1-12")

        proximas = []
        cur_anio, cur_mes = anio, mes_actual
        for _ in range(12):
            if cur_mes == 12:
                rep_anio = cur_anio + 1
                rep_mes = 1
            else:
                rep_anio = cur_anio
                rep_mes = cur_mes + 1
            proximas.append({
                "periodo": f"{cur_anio}-{cur_mes:02d}",
                "vencimiento": f"{rep_anio}-{rep_mes:02d}-15 (primeros 10 días hábiles)",
                "obligacion": "Reporte mensual ventas CRE (ceros si no actividad)",
            })
            if cur_mes == 12:
                cur_anio += 1
                cur_mes = 1
            else:
                cur_mes += 1
        return {
            "anio_inicio": anio,
            "mes_inicio": mes_actual,
            "proximas_obligaciones": proximas,
            "nota": "Si no hay actividad: reportar ceros (NO está exento).",
            "fuente": URL_CRE,
        }

    def evaluar_anexo30(self, litros_mes_max: float, tiene_permiso_cre: bool) -> dict[str, Any]:
        if litros_mes_max < 0:
            raise ValidationError("litros negativos")
        aplica_anexo30 = (litros_mes_max >= UMBRAL_ANEXO30_LITROS_MES) or tiene_permiso_cre
        return {
            "litros_mes_max_consumo": litros_mes_max,
            "umbral_litros_mes": UMBRAL_ANEXO30_LITROS_MES,
            "tiene_permiso_cre": tiene_permiso_cre,
            "aplica_anexo30_sat": aplica_anexo30,
            "obligaciones_si_aplica": [
                "Controles volumétricos certificados",
                "Reporte mensual ventas CRE",
                "CFDI 4.0 con complemento Hidrocarburos y Petrolíferos",
                "Conservar reportes 5 años",
            ],
            "base_legal": "Anexo 30 RMF SAT + Ley Hidrocarburos + Resolución CRE",
            "fuente": URL_SAT_VOLUMETRICOS,
        }

    def reportar_zeros(self, num_permiso: str, periodo: str) -> dict[str, Any]:
        if not NUM_PERMISO_RE.match(num_permiso or ""):
            raise ValidationError(f"num_permiso inválido: {num_permiso!r}")
        if not re.match(r"^\d{4}-\d{2}$", periodo):
            raise ValidationError(f"periodo debe ser YYYY-MM: {periodo!r}")
        ahora = datetime.now(timezone.utc)
        return mark_simulated({
            "num_permiso": num_permiso,
            "periodo": periodo,
            "ventas_litros": 0,
            "reporte_aceptado": True,
            "folio": f"CRE-CERO-{ahora.strftime('%Y%m%d%H%M%S')}",
            "fuente": URL_CRE,
        })

    def listar_tipos_permiso(self) -> dict[str, Any]:
        return {
            "total": len(TIPOS_PERMISO),
            "tipos": [{"clave": k, "descripcion": v} for k, v in TIPOS_PERMISO.items()],
        }
