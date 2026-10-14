"""Cliente mp_multas_vehiculares_mx — 5 sistemas.

Estado real (2026-10-14): los cinco portales oficiales exigen CAPTCHA
(SAF imagen, Turnstile, reCAPTCHA v2) o no tienen flujo automatizable (ICVNL).
Cada consulta hace un GET real que confirma el portal y devuelve un handoff
humano. EdoMex y San Pedro consultan en real con solver opt-in
(shared/multas_captcha.py). Datos simulados solo con PLUGINS_MX_MOCK=1.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import NotFoundError, ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared import portal_handoff as ph  # noqa: E402
from shared.multas_captcha import con_solver, consultar_con_solver  # noqa: E402
from shared.multas_vehiculares_mx import (  # noqa: E402
    CATALOGO_MULTAS,
    SistemaMultas,
    buscar_sistema,
)


NAMESPACE = "multas_vehiculares_mx"
PORTALES = {
    "cdmx": ph.SAF_CDMX_ADEUDOS,
    "edomex": ph.EDOMEX_INFRACCIONES,
    "nl": ph.ICVNL_ESTADO_CUENTA,
    "nl_sanpedro": ph.SAN_PEDRO_MULTAS,
    "jal": ph.JALISCO_ADEUDOS,
}


def _normalizar_placa(placa: str) -> str:
    return placa.strip().upper().replace(" ", "").replace("-", "")


class MultasVehicularesMxClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_por_placa(self, estado: str, placa: str) -> dict[str, Any]:
        """Consulta lista de multas activas para un vehículo."""
        placa = _normalizar_placa(placa)
        if len(placa) < 5:
            raise ValidationError(f"Placa muy corta: {placa}")
        sistema = buscar_sistema(estado)
        if sistema is None:
            raise NotFoundError(f"Estado '{estado}' no en catálogo multas.")

        self._bitacora.log("consultar_por_placa", success=True,
                           params_summary={"estado": sistema.clave,
                                           "placa_hash": self._bitacora.hash_sensitive(placa)})
        if ph.mock_forzado():
            return self._mock(sistema, placa)
        if con_solver(sistema.clave):
            return {**consultar_con_solver(sistema.clave, placa), "organismo": sistema.organismo}
        return ph.handoff_humano(PORTALES[sistema.clave], placa=placa, organismo=sistema.organismo)

    def calcular_total(self, estado: str, placa: str) -> dict[str, Any]:
        """Suma multas + descuentos. Solo hay montos con PLUGINS_MX_MOCK=1; en real
        devuelve el handoff (los portales exigen CAPTCHA)."""
        consulta = self.consultar_por_placa(estado, placa)
        if consulta.get("status") == "requiere_humano":
            return consulta
        multas = consulta.get("multas", [])
        if any(m.get("monto_mxn") is None for m in multas):
            # Real sin monto legible: no se suma como 0.
            return {**consulta, "monto_bruto_mxn": None,
                    "nota": "El portal no dio un monto legible para todas las multas."}
        total_bruto = sum(m.get("monto_mxn", 0) for m in multas)
        # ponytail: regla de descuento ilustrativa (solo mock); no verificada por estado.
        descuento_50 = sum(m.get("monto_mxn", 0) for m in multas if m.get("dias_desde_emision", 100) <= 15)
        descuento_25 = sum(m.get("monto_mxn", 0) for m in multas
                          if 15 < m.get("dias_desde_emision", 100) <= 30)
        total_con_descuentos = (
            descuento_50 * 0.5
            + descuento_25 * 0.75
            + (total_bruto - descuento_50 - descuento_25)
        )
        return {
            "estado": estado,
            "placa": _normalizar_placa(placa),
            "multas_total": len(multas),
            "monto_bruto_mxn": round(total_bruto, 2),
            "ahorro_descuentos_mxn": round(total_bruto - total_con_descuentos, 2),
            "monto_neto_pagable_mxn": round(total_con_descuentos, 2),
            "desglose_descuentos": {
                "50pct_pagar_15d_mxn": round(descuento_50, 2),
                "25pct_pagar_30d_mxn": round(descuento_25, 2),
                "sin_descuento_mxn": round(total_bruto - descuento_50 - descuento_25, 2),
            },
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": consulta.get("simulated", False),
        }

    def listar_sistemas(self) -> dict[str, Any]:
        return {
            "total": len(CATALOGO_MULTAS),
            "sistemas": [{
                "clave": s.clave, "estado": s.nombre_estado,
                "organismo": s.organismo, "metodo": s.metodo,
                "url": s.url_consulta, "captcha_tipo": s.captcha_tipo,
                "cobertura_vehiculos": s.cobertura_vehiculos,
            } for s in CATALOGO_MULTAS],
        }

    # ---- MOCK ----
    def _mock(self, sistema: SistemaMultas, placa: str) -> dict[str, Any]:
        """Mock determinístico por último dígito de placa."""
        last_d = "0"
        for c in reversed(placa):
            if c.isdigit():
                last_d = c
                break
        n_multas = int(last_d) % 4  # 0-3 multas
        multas = []
        for i in range(n_multas):
            multas.append({
                "folio": f"MOCK-{sistema.clave.upper()}-{placa[-4:]}-{i:03d}",
                "fecha": f"2026-{(i+3):02d}-15",
                "infraccion": ["Exceso de velocidad", "Estacionamiento prohibido",
                               "No respetar luz roja"][i % 3],
                "monto_mxn": round(1500.0 + i * 850, 2),
                "dias_desde_emision": 10 + i * 15,
                "estatus": "PENDIENTE",
            })
        return mark_simulated({
            "estado": sistema.clave,
            "placa": placa,
            "organismo": sistema.organismo,
            "multas_total": n_multas,
            "multas": multas,
            "fuente": sistema.url_consulta,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

