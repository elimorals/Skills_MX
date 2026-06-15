"""Cliente mp_cfe_interconexion_solar.

Trámite interconexión solar prosumidor con CFE:
1. Solicitud (gratis) con diagrama eléctrico + specs
2. Evaluación CFE de red local
3. Instalación
4. Inspección CFE
5. Medidor bidireccional
6. Contrato prosumidor

Cambios 2026: net metering 1:1 → autoconsumo inteligente (energía exportada vale menos).
"""
from __future__ import annotations

import hashlib
import re
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


NAMESPACE = "cfe_interconexion_solar"
URL_INTERCONEXION_CFE = "https://www.cfe.mx/casa/contratacion-distribuida/Pages/contratacion-distribuida.aspx"


# Tarifas residenciales/PyME relevantes para autoconsumo (CFE 2026)
TARIFAS_APLICABLES: dict[str, dict] = {
    "DAC":      {"nombre": "Doméstica de Alto Consumo", "costo_kwh_promedio_mxn": 5.20},
    "PDBT":     {"nombre": "Pequeña Demanda Baja Tensión (PyME)", "costo_kwh_promedio_mxn": 4.80},
    "GDMTH":    {"nombre": "Gran Demanda Media Tensión Horaria", "costo_kwh_promedio_mxn": 3.20},
    "GDMTO":    {"nombre": "Gran Demanda Media Tensión Ordinaria", "costo_kwh_promedio_mxn": 3.10},
    "1":        {"nombre": "Tarifa 1 doméstica básica", "costo_kwh_promedio_mxn": 0.95},
}

TipoSistema = Literal["fotovoltaico", "eolico", "biogas", "geotermia", "mixto"]
EstatusSolicitud = Literal["registrada", "en_revision", "aprobada", "rechazada",
                            "inspeccion_programada", "medidor_instalado", "contrato_firmado"]


RPU_RE = re.compile(r"^\d{6,16}$")


class CFEInterconexionClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def solicitar_interconexion(
        self,
        rpu: str,
        kw_instalados: float,
        tarifa_actual: str,
        tipo_sistema: str = "fotovoltaico",
        tension: str = "baja",
    ) -> dict[str, Any]:
        rpu = (rpu or "").strip()
        if not RPU_RE.match(rpu):
            raise ValidationError(f"RPU inválido: {rpu!r}")
        if kw_instalados <= 0 or kw_instalados > 500:
            raise ValidationError(f"kw_instalados fuera de rango: {kw_instalados}")
        if tarifa_actual not in TARIFAS_APLICABLES:
            raise ValidationError(f"tarifa no soportada: {tarifa_actual}. "
                                   f"Válidas: {list(TARIFAS_APLICABLES.keys())}")
        if tipo_sistema not in {"fotovoltaico", "eolico", "biogas", "geotermia", "mixto"}:
            raise ValidationError(f"tipo_sistema inválido: {tipo_sistema}")

        ahora = datetime.now(timezone.utc)
        folio = "SOL-" + hashlib.sha256(
            f"{rpu}|{ahora.isoformat()}|cfe".encode("utf-8")
        ).hexdigest()[:12].upper()

        # Categoría regulatoria por tamaño
        if kw_instalados <= 0.5:
            categoria = "Pequeña escala (≤0.5 MW) — interconexión simplificada"
            tiempo_dias = "30-45 días"
        elif kw_instalados <= 100:  # 100 kW = simplificado en tensión < 1kV
            categoria = "PyME generación distribuida"
            tiempo_dias = "45-60 días"
        else:
            categoria = "Mediana generación distribuida"
            tiempo_dias = "60-90 días"

        self._bitacora.log("solicitar_interconexion", success=True,
                           params_summary={"rpu_hash": self._bitacora.hash_sensitive(rpu),
                                           "kw": kw_instalados})
        return mark_simulated({
            "folio": folio,
            "rpu_hash": self._bitacora.hash_sensitive(rpu),
            "kw_instalados": kw_instalados,
            "tipo_sistema": tipo_sistema,
            "tarifa_actual": tarifa_actual,
            "tarifa_descripcion": TARIFAS_APLICABLES[tarifa_actual]["nombre"],
            "tension": tension,
            "categoria_regulatoria": categoria,
            "tiempo_estimado_resolucion": tiempo_dias,
            "costo_solicitud": 0.0,
            "documentos_requeridos": [
                "Diagrama eléctrico unifilar",
                "Especificaciones técnicas equipos (inversor, paneles, protecciones)",
                "Plan de protecciones",
                "Certificados NMX-J-643 / IEC del inversor",
                "Identificación oficial del titular del servicio",
            ],
            "estatus": "registrada",
            "url_seguimiento": f"https://www.cfe.mx/interconexion/{folio}",
            "fecha_solicitud": ahora.isoformat(),
            "fuente": URL_INTERCONEXION_CFE,
        })

    def consultar_estatus_solicitud(self, folio: str) -> dict[str, Any]:
        if not folio or not folio.startswith("SOL-"):
            raise ValidationError(f"folio inválido: {folio!r}")
        # Mock determinístico por suffix folio
        last = folio[-1]
        estatus_map = {
            "0": "registrada", "1": "en_revision", "2": "aprobada",
            "3": "inspeccion_programada", "4": "medidor_instalado",
            "5": "contrato_firmado", "6": "registrada", "7": "en_revision",
            "8": "aprobada", "9": "medidor_instalado",
            "A": "aprobada", "B": "contrato_firmado", "C": "en_revision",
            "D": "inspeccion_programada", "E": "medidor_instalado",
            "F": "registrada",
        }
        estatus = estatus_map.get(last.upper(), "registrada")
        return mark_simulated({
            "folio": folio,
            "estatus": estatus,
            "porcentaje_avance": _porcentaje_avance(estatus),
            "siguiente_paso": _siguiente_paso(estatus),
        })

    def simular_ahorro_prosumidor(
        self, tarifa_actual: str, kwh_consumo_promedio_mensual: float,
        kwh_generacion_solar_estimada: float,
    ) -> dict[str, Any]:
        if tarifa_actual not in TARIFAS_APLICABLES:
            raise ValidationError(f"tarifa no soportada: {tarifa_actual}")
        if kwh_consumo_promedio_mensual < 0 or kwh_generacion_solar_estimada < 0:
            raise ValidationError("kwh no puede ser negativo")

        costo_kwh = TARIFAS_APLICABLES[tarifa_actual]["costo_kwh_promedio_mxn"]
        # Ahorro = energía solar autoconsumida * costo - excedente * factor_exportación
        autoconsumo_kwh = min(kwh_consumo_promedio_mensual, kwh_generacion_solar_estimada)
        exportacion_kwh = max(0, kwh_generacion_solar_estimada - autoconsumo_kwh)
        # Cambio 2026: exportación vale ~70% de lo importado (autoconsumo inteligente)
        factor_exportacion = 0.70
        ahorro_autoconsumo = autoconsumo_kwh * costo_kwh
        valor_exportacion = exportacion_kwh * costo_kwh * factor_exportacion
        ahorro_mensual = ahorro_autoconsumo + valor_exportacion
        ahorro_anual = ahorro_mensual * 12

        return mark_simulated({
            "tarifa_actual": tarifa_actual,
            "costo_kwh_mxn": costo_kwh,
            "kwh_consumo_mensual": kwh_consumo_promedio_mensual,
            "kwh_generacion_solar": kwh_generacion_solar_estimada,
            "autoconsumo_kwh": round(autoconsumo_kwh, 2),
            "exportacion_kwh": round(exportacion_kwh, 2),
            "factor_exportacion_2026": factor_exportacion,
            "ahorro_mensual_mxn": round(ahorro_mensual, 2),
            "ahorro_anual_mxn": round(ahorro_anual, 2),
            "nota_2026": "CFE pasó de net metering 1:1 a autoconsumo inteligente. "
                          "Exportación vale ~70% vs consumo evitado.",
        })

    def listar_tarifas(self) -> dict[str, Any]:
        return {
            "total": len(TARIFAS_APLICABLES),
            "tarifas": [{"clave": k, **v} for k, v in TARIFAS_APLICABLES.items()],
            "nota_compatibilidad": "Todas son compatibles con autoconsumo. "
                                    "Tarifas industriales (HM/HS) ya son intrínsecamente horarias.",
        }


def _porcentaje_avance(estatus: str) -> int:
    return {
        "registrada": 15, "en_revision": 35, "aprobada": 60,
        "inspeccion_programada": 75, "medidor_instalado": 90,
        "contrato_firmado": 100, "rechazada": 0,
    }.get(estatus, 0)


def _siguiente_paso(estatus: str) -> str:
    return {
        "registrada": "Esperar evaluación CFE (45 días hábiles típicos)",
        "en_revision": "Atender requerimientos CFE si los hay",
        "aprobada": "Agendar inspección CFE",
        "inspeccion_programada": "Realizar inspección + correcciones",
        "medidor_instalado": "Firmar contrato prosumidor",
        "contrato_firmado": "Operar normalmente",
        "rechazada": "Subir requerimientos faltantes",
    }.get(estatus, "Consultar CFE")
