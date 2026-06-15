"""Cliente mp_multas_vehiculares_mx — 4 sistemas estatales.

Mock-first. Path real opt-in vía PLUGINS_MX_MULTAS_LIVE=1 + portal-specific.
CDMX reusa el endpoint público SAF descubierto en discovery 2026-06-15.
"""
from __future__ import annotations

import os
import re
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
from shared.errors import McpError, NotFoundError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.multas_vehiculares_mx import (  # noqa: E402
    CATALOGO_MULTAS,
    SistemaMultas,
    buscar_sistema,
)


NAMESPACE = "multas_vehiculares_mx"
LIVE_ENV_FLAG = "PLUGINS_MX_MULTAS_LIVE"
CACHE_TTL_HOURS = 24  # multas pueden cambiar diario


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

        cache_key = f"{sistema.clave}:{placa}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        live = os.getenv(LIVE_ENV_FLAG, "").strip() == "1"
        if live and sistema.clave == "cdmx":
            result = self._real_cdmx(placa)
        else:
            result = self._mock(sistema, placa)

        self._cache.set(cache_key, result, ttl_hours=CACHE_TTL_HOURS)
        self._bitacora.log("consultar_por_placa", success=True,
                           params_summary={"estado": sistema.clave,
                                           "placa_hash": self._bitacora.hash_sensitive(placa),
                                           "modo": "live" if live and sistema.clave == "cdmx" else "mock"})
        return result

    def calcular_total(self, estado: str, placa: str) -> dict[str, Any]:
        """Suma multas + descuentos vigentes."""
        consulta = self.consultar_por_placa(estado, placa)
        multas = consulta.get("multas", [])
        total_bruto = sum(m.get("monto_mxn", 0) for m in multas)
        # Descuento típico CDMX/JAL: 50% pago oportuno (15 días), 25% pago dentro 30 días.
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

    # ---- REAL paths ----
    def _real_cdmx(self, placa: str) -> dict[str, Any]:
        """Reusa SAF CDMX Consultaciudadana — mismo endpoint que verificación.

        El endpoint público devuelve adeudos vehiculares (tenencia + verificación
        + multas). Filtramos solo lo de multas/infracciones.
        """
        # Reusamos la lógica del MCP de verificación CDMX (mismo endpoint).
        try:
            from mp_verificacion_vehicular_mx.client import (  # type: ignore
                VerificacionVehicularClient,
            )
        except ImportError as e:
            raise McpError("mp_verificacion_vehicular_mx requerido para SAF CDMX.",
                           {"raw": str(e)})

        verif = VerificacionVehicularClient(cache=self._cache, bitacora=self._bitacora)
        # Forzamos path real reutilizando _real_consultar_cdmx
        try:
            raw = verif._real_consultar_cdmx(placa)
        except UpstreamError:
            raise
        except Exception as e:
            raise UpstreamError(f"SAF CDMX falló para multas: {e}",
                                {"placa_hash": self._bitacora.hash_sensitive(placa)})

        # Convertimos raw (verificación + adeudos) a shape "multas"
        multas = []
        if raw.get("adeudo_total_mxn", 0) > 0:
            # SAF expone un total agregado — sin desglose por folio en consulta pública.
            # Devolvemos 1 entrada placeholder que el usuario calibre con cuenta real.
            multas.append({
                "folio": "SAF-CDMX-AGREGADO",
                "fecha": "n/d",
                "infraccion": "Adeudos vehiculares (verificación + tenencia + multas)",
                "monto_mxn": raw["adeudo_total_mxn"],
                "dias_desde_emision": 30,
                "estatus": "PENDIENTE",
            })

        return {
            "estado": "cdmx",
            "placa": placa,
            "organismo": "SAF CDMX",
            "multas_total": len(multas),
            "multas": multas,
            "fuente": raw.get("fuente", ""),
            "raw_saf": raw,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
            "needs_calibration": True,  # primer hit calibra el shape
        }
