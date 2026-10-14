"""Cliente mp_cfe_interconexion_solar — generación distribuida (prosumidor) con CFE.

Verificado 2026-10-14 contra la Ley del Sector Eléctrico (LSE, "Nueva Ley DOF 18-03-2025",
https://www.diputados.gob.mx/LeyesBiblio/pdf/LSE.pdf):
- Art. 19: centrales con capacidad ≥ 0.7 MW requieren permiso; < 0.7 MW son Generadoras Exentas.
- Arts. 3 fr. XXII y 25: Generación Distribuida = Generadora Exenta (< 0.7 MW) interconectada a
  un circuito de distribución con alta concentración de Centros de Carga.
- Art. 27: puede vender energía a la Suministradora de Servicios Básicos; la CNE emite modelos de
  contrato y metodologías de contraprestación.
- Art. 30: autoconsumo (≥ 0.7 MW) requiere permiso; entre 0.7 y 20 MW, trámite simplificado.

Lo que se retiró por no tener fuente: folios y estatus de solicitud inventados (la solicitud la
presenta el titular ante CFE; este MCP es de solo lectura), costos por kWh "promedio" por tarifa,
el umbral de 0.5 (que además comparaba kW contra MW) y el "factor de exportación 0.70 de 2026".
El simulador ahora exige el costo por kWh del recibo y el esquema de compensación del contrato.
CFE responde 403 a clientes no-navegador (www.cfe.mx → www.cfe.gob.mx, 2026-10-14).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Literal

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402


NAMESPACE = "cfe_interconexion_solar"
URL_CFE = "https://www.cfe.gob.mx/"
URL_LSE = "https://www.diputados.gob.mx/LeyesBiblio/pdf/LSE.pdf"
UMBRAL_GENERADORA_EXENTA_KW = 700.0  # LSE Art. 19: < 0.7 MW
UMBRAL_AUTOCONSUMO_SIMPLIFICADO_KW = 20_000.0  # LSE Art. 30: 0.7-20 MW

# Nombres de tarifas CFE (sin precios: dependen de región, mes y bloque de consumo).
TARIFAS_APLICABLES: dict[str, dict] = {
    "1": {"nombre": "Doméstica (tarifa 1 y regionales 1A-1F)"},
    "DAC": {"nombre": "Doméstica de Alto Consumo"},
    "PDBT": {"nombre": "Pequeña Demanda Baja Tensión"},
    "GDBT": {"nombre": "Gran Demanda Baja Tensión"},
    "GDMTO": {"nombre": "Gran Demanda Media Tensión Ordinaria"},
    "GDMTH": {"nombre": "Gran Demanda Media Tensión Horaria"},
}

Esquema = Literal["medicion_neta", "facturacion_neta"]
RPU_RE = re.compile(r"^\d{6,16}$")


def clasificar_central(kw_instalados: float) -> dict[str, Any]:
    if kw_instalados <= 0:
        raise ValidationError("kw_instalados debe ser > 0")
    if kw_instalados < UMBRAL_GENERADORA_EXENTA_KW:
        return {"categoria": "generacion_distribuida_exenta", "requiere_permiso_cne": False,
                "fundamento": "LSE Arts. 3 fr. XXII, 19 y 25 (< 0.7 MW)"}
    if kw_instalados <= UMBRAL_AUTOCONSUMO_SIMPLIFICADO_KW:
        return {"categoria": "autoconsumo_permiso_simplificado", "requiere_permiso_cne": True,
                "fundamento": "LSE Arts. 19 y 30 (0.7-20 MW, trámite simplificado)"}
    return {"categoria": "central_con_permiso", "requiere_permiso_cne": True,
            "fundamento": "LSE Art. 19 (≥ 0.7 MW)"}


class CFEInterconexionClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def solicitar_interconexion(self, rpu: str, kw_instalados: float, tarifa_actual: str,
                                tipo_sistema: str = "fotovoltaico", tension: str = "baja") -> dict[str, Any]:
        """Clasifica la central y devuelve los pasos: nunca presenta la solicitud."""
        rpu = (rpu or "").strip()
        if not RPU_RE.match(rpu):
            raise ValidationError(f"RPU inválido: {rpu!r}")
        if tarifa_actual not in TARIFAS_APLICABLES:
            raise ValidationError(f"tarifa no soportada: {tarifa_actual}. Válidas: {list(TARIFAS_APLICABLES)}")
        if tipo_sistema not in {"fotovoltaico", "eolico", "biogas", "geotermia", "mixto"}:
            raise ValidationError(f"tipo_sistema inválido: {tipo_sistema}")
        clasif = clasificar_central(kw_instalados)
        self._bitacora.log("solicitar_interconexion_handoff", success=True,
                           params_summary={"rpu_hash": self._bitacora.hash_sensitive(rpu), "kw": kw_instalados})
        return {
            "rpu_hash": self._bitacora.hash_sensitive(rpu),
            "kw_instalados": kw_instalados,
            "tipo_sistema": tipo_sistema,
            "tarifa_actual": tarifa_actual,
            "tension": tension,
            **clasif,
            "enviada": False,
            "handoff_humano": True,
            "motivo": "La solicitud de interconexión la presenta el titular del servicio ante CFE.",
            "pasos": [
                "Reunir diagrama unifilar y fichas técnicas de inversor/módulos/protecciones (lista orientativa; "
                "confirmar la vigente con CFE Distribución).",
                "Presentar la solicitud de interconexión en el centro de atención o canal digital de CFE.",
                "Tras la inspección, firmar el contrato de interconexión y obtener medidor bidireccional.",
            ],
            "url": URL_CFE,
            "fuente_legal": URL_LSE,
        }

    def consultar_estatus_solicitud(self, folio: str) -> dict[str, Any]:
        """No hay consulta pública del estatus: handoff (antes el estatus salía del último carácter)."""
        if not folio or len(folio) < 4:
            raise ValidationError(f"folio inválido: {folio!r}")
        return {
            "folio": folio,
            "estatus": None,
            "handoff_humano": True,
            "pasos": ["Consultar el folio con CFE (centro de atención o 071)."],
            "url": URL_CFE,
        }

    def simular_ahorro_prosumidor(self, costo_kwh_mxn: float, kwh_consumo_promedio_mensual: float,
                                  kwh_generacion_solar_estimada: float, esquema: str = "medicion_neta",
                                  precio_exportacion_mxn_kwh: float | None = None) -> dict[str, Any]:
        """Modelo mensual simple con el costo marginal del recibo del usuario.

        - medicion_neta: lo exportado compensa kWh consumidos en el periodo; el excedente sobre el
          consumo no tiene valor monetario en el mes (queda como saldo de energía).
        - facturacion_neta: lo exportado se paga a `precio_exportacion_mxn_kwh` (del contrato).
        """
        if costo_kwh_mxn <= 0:
            raise ValidationError("costo_kwh_mxn debe venir del recibo (> 0)")
        if kwh_consumo_promedio_mensual < 0 or kwh_generacion_solar_estimada < 0:
            raise ValidationError("kwh no puede ser negativo")
        if esquema not in ("medicion_neta", "facturacion_neta"):
            raise ValidationError("esquema debe ser medicion_neta o facturacion_neta")
        if esquema == "facturacion_neta" and (precio_exportacion_mxn_kwh is None or precio_exportacion_mxn_kwh < 0):
            raise ValidationError("facturacion_neta requiere precio_exportacion_mxn_kwh del contrato")

        consumo, gen = kwh_consumo_promedio_mensual, kwh_generacion_solar_estimada
        if esquema == "medicion_neta":
            compensado = min(consumo, gen)
            excedente = max(0.0, gen - consumo)
            ahorro = compensado * costo_kwh_mxn
            detalle = {"kwh_compensados": round(compensado, 2), "kwh_saldo_a_favor": round(excedente, 2)}
        else:
            autoconsumo = min(consumo, gen)  # supuesto: generación y consumo simultáneos
            exportado = max(0.0, gen - autoconsumo)
            ahorro = autoconsumo * costo_kwh_mxn + exportado * precio_exportacion_mxn_kwh
            detalle = {"kwh_autoconsumo": round(autoconsumo, 2), "kwh_exportados": round(exportado, 2),
                       "precio_exportacion_mxn_kwh": precio_exportacion_mxn_kwh}
        return {
            "esquema": esquema,
            "costo_kwh_mxn": costo_kwh_mxn,
            "kwh_consumo_mensual": consumo,
            "kwh_generacion_solar": gen,
            **detalle,
            "ahorro_mensual_mxn": round(ahorro, 2),
            "ahorro_anual_mxn": round(ahorro * 12, 2),
            "supuestos": [
                "Costo por kWh constante (en tarifas escalonadas el kWh evitado es el del bloque más alto).",
                "No incluye cargos fijos, IVA, DAP ni cambio de tarifa (p. ej. salir de DAC).",
                "El esquema y precios de compensación los fija el contrato de interconexión (LSE Art. 27, CNE).",
            ],
        }

    def listar_tarifas(self) -> dict[str, Any]:
        return {
            "total": len(TARIFAS_APLICABLES),
            "tarifas": [{"clave": k, **v} for k, v in TARIFAS_APLICABLES.items()],
            "nota": "Sin precios: varían por región, mes y bloque; usar el costo por kWh del recibo.",
            "fuente": URL_CFE,
        }
