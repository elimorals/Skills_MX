"""Cliente mp_resico_sat."""
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
from shared.resico_sat_mx import (  # noqa: E402
    CATALOGO_PLATAFORMAS,
    RESICO_TOPE_ANUAL_MXN,
    TRAMOS_RESICO_MENSUAL_2026,
    calcular_isr_resico,
    calcular_retencion_plataforma,
)


NAMESPACE = "resico_sat"


class RESICOClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def calcular_isr_mes(self, ingreso_mes_mxn: float) -> dict[str, Any]:
        if ingreso_mes_mxn < 0:
            raise ValidationError("ingreso negativo")
        r = calcular_isr_resico(ingreso_mes_mxn)
        r["fecha_calculo"] = datetime.now(timezone.utc).isoformat()
        r["base_legal"] = "RESICO 2026 — Art. 113-E LISR + RMF 2026"
        return mark_simulated(r)

    def evaluar_estatus(
        self, rfc: str, periodos_omitidos: int, declaracion_anual_presentada: bool,
        ingresos_anuales_mxn: float, e_firma_vigente: bool = True,
    ) -> dict[str, Any]:
        """Devuelve estatus respecto a expulsión automática."""
        if not rfc or len(rfc) < 12:
            raise ValidationError(f"RFC inválido: {rfc!r}")
        if periodos_omitidos < 0:
            raise ValidationError("periodos_omitidos negativo")
        if ingresos_anuales_mxn < 0:
            raise ValidationError("ingresos_anuales negativos")

        causas: list[str] = []
        if periodos_omitidos >= 3:
            causas.append(
                "Tres o más omisiones de pago mensual consecutivas (SCJN 2026 — expulsión automática)."
            )
        if not declaracion_anual_presentada:
            causas.append("Declaración anual no presentada (causal de expulsión).")
        if ingresos_anuales_mxn > RESICO_TOPE_ANUAL_MXN:
            causas.append(
                f"Ingresos anuales ${ingresos_anuales_mxn:,.2f} rebasan tope "
                f"${RESICO_TOPE_ANUAL_MXN:,.2f}."
            )
        if not e_firma_vigente:
            causas.append("e.firma no vigente (requisito obligatorio 2026).")

        if causas:
            estatus = "expulsion_automatica"
            score_riesgo = 100
        elif periodos_omitidos == 2:
            estatus = "en_riesgo_expulsion"
            score_riesgo = 80
        elif periodos_omitidos == 1:
            estatus = "alerta_temprana"
            score_riesgo = 40
        else:
            estatus = "al_corriente"
            score_riesgo = 0

        # Sugerencia de acción
        if estatus == "expulsion_automatica":
            accion = "Migrar al régimen general (Art. 109 LISR) y regularizar adeudos."
        elif estatus == "en_riesgo_expulsion":
            accion = "URGENTE: presentar pago del mes pendiente HOY."
        elif estatus == "alerta_temprana":
            accion = "Presentar pago del mes pendiente esta semana."
        else:
            accion = "Continuar cumpliendo declaraciones mensuales antes del día 17."

        self._bitacora.log("evaluar_estatus", success=True,
                           params_summary={"rfc_hash": self._bitacora.hash_sensitive(rfc),
                                           "estatus": estatus})
        return mark_simulated({
            "rfc": rfc,
            "estatus": estatus,
            "score_riesgo": score_riesgo,
            "causas_expulsion": causas,
            "accion_recomendada": accion,
            "ingresos_anuales_mxn": round(ingresos_anuales_mxn, 2),
            "tope_anual_mxn": RESICO_TOPE_ANUAL_MXN,
            "periodos_omitidos": periodos_omitidos,
            "e_firma_vigente": e_firma_vigente,
            "base_legal": "SCJN 2026: expulsión automática sin previo aviso por 3 omisiones",
            "fecha_evaluacion": datetime.now(timezone.utc).isoformat(),
        })

    def calendario_declaraciones(self, anio: int, mes_actual: int) -> dict[str, Any]:
        """Devuelve calendario de próximas 12 declaraciones mensuales."""
        if anio < 2020 or anio > 2099:
            raise ValidationError("anio fuera de rango")
        if mes_actual < 1 or mes_actual > 12:
            raise ValidationError("mes_actual debe ser 1-12")

        proximas = []
        cur_anio, cur_mes = anio, mes_actual
        for _ in range(12):
            # Declaración del mes M se presenta antes del día 17 del mes M+1
            if cur_mes == 12:
                vence_anio = cur_anio + 1
                vence_mes = 1
            else:
                vence_anio = cur_anio
                vence_mes = cur_mes + 1
            proximas.append({
                "periodo": f"{cur_anio}-{cur_mes:02d}",
                "vencimiento": f"{vence_anio}-{vence_mes:02d}-17",
                "concepto": "Pago provisional ISR + IVA RESICO",
            })
            # avanzar
            if cur_mes == 12:
                cur_anio += 1
                cur_mes = 1
            else:
                cur_mes += 1

        return {
            "anio_inicio": anio,
            "mes_inicio": mes_actual,
            "proximas_declaraciones": proximas,
            "nota": "Presentar antes del día 17 del mes siguiente para evitar omisión.",
        }

    def retencion_plataforma(self, plataforma: str, ingreso_bruto_mxn: float) -> dict[str, Any]:
        try:
            r = calcular_retencion_plataforma(plataforma, ingreso_bruto_mxn)
        except ValueError as e:
            raise ValidationError(str(e))
        r["nota"] = "Tasa estandarizada 2.5% ISR 2026 (RMF 2026 plataformas digitales)."
        return mark_simulated(r)

    def solicitar_devolucion_mensual(
        self, rfc: str, periodo: str, monto_solicitado_mxn: float,
        plataforma: str | None = None,
    ) -> dict[str, Any]:
        """Genera referencia de solicitud devolución mes-a-mes (cambio 2026)."""
        if not rfc or len(rfc) < 12:
            raise ValidationError(f"RFC inválido: {rfc!r}")
        if monto_solicitado_mxn <= 0:
            raise ValidationError("monto_solicitado debe ser > 0")
        if not periodo or len(periodo) != 7 or periodo[4] != "-":
            raise ValidationError(f"periodo debe ser YYYY-MM, recibido: {periodo!r}")

        ahora = datetime.now(timezone.utc)
        folio = f"DEV-{ahora.strftime('%Y%m%d%H%M%S')}-{rfc[:4]}"

        self._bitacora.log("solicitar_devolucion_mensual", success=True,
                           params_summary={"rfc_hash": self._bitacora.hash_sensitive(rfc),
                                           "periodo": periodo,
                                           "monto": monto_solicitado_mxn})
        return mark_simulated({
            "folio_solicitud": folio,
            "rfc": rfc,
            "periodo": periodo,
            "monto_solicitado_mxn": round(monto_solicitado_mxn, 2),
            "plataforma": plataforma,
            "tipo_forma": "Forma 41 (PF) / Forma 14 (PM)",
            "estatus": "registrada_mock",
            "fecha_solicitud": ahora.isoformat(),
            "tiempo_estimado_resolucion_dias": "10-40 días hábiles",
            "url_seguimiento": f"https://www.sat.gob.mx/devoluciones/{folio}",
            "base_legal": "RMF 2026 — devolución mes-a-mes para retención plataformas",
        })

    def listar_tasas(self) -> dict[str, Any]:
        tramos = [{
            "limite_inferior": t.limite_inferior,
            "limite_superior": t.limite_superior,
            "tasa": t.tasa,
            "tasa_pct": f"{t.tasa * 100:.2f}%",
        } for t in TRAMOS_RESICO_MENSUAL_2026]
        return {
            "tope_anual_mxn": RESICO_TOPE_ANUAL_MXN,
            "tasa_retencion_plataformas": 0.025,
            "tramos_mensuales": tramos,
            "vigencia": "2026",
            "base_legal": "RESICO Art. 113-E LISR + RMF 2026",
        }

    def listar_plataformas(self) -> dict[str, Any]:
        return {
            "total": len(CATALOGO_PLATAFORMAS),
            "tasa_unica": 0.025,
            "plataformas": [{
                "clave": p.clave, "nombre": p.nombre, "categoria": p.categoria,
                "aplica_retencion": p.aplica_retencion,
            } for p in CATALOGO_PLATAFORMAS],
        }
