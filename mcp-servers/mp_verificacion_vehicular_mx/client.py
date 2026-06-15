"""Cliente mp_verificacion_vehicular_mx."""
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
from shared.cache import FileCache  # noqa: E402
from shared.errors import NotFoundError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.verificacion_vehicular import (  # noqa: E402
    buscar_programa,
    calcular_proximo_periodo,
    CATALOGO_VERIFICACION,
    mes_proxima_verificacion,
)


NAMESPACE = "verificacion_vehicular"


class VerificacionVehicularClient:
    def __init__(self, cache: FileCache | None = None, bitacora: Bitacora | None = None) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_estatus(self, placa: str, estado: str) -> dict[str, Any]:
        """Consulta estatus de la última verificación del vehículo."""
        placa = placa.strip().upper().replace(" ", "").replace("-", "")
        if len(placa) < 5:
            raise ValidationError(f"Placa muy corta: {placa}")
        p = buscar_programa(estado)
        if p is None:
            raise NotFoundError(f"Estado '{estado}' no en catálogo verificación.")

        cache_key = f"{estado}:{placa}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Mock-first
        result = self._mock(p, placa)
        self._cache.set(cache_key, result, ttl_hours=24 * 30)
        self._bitacora.log("consultar_estatus", success=True,
                           params_summary={"estado": estado, "placa_hash": self._bitacora.hash_sensitive(placa)})
        return result

    def proximo_periodo(self, placa: str, estado: str = "cdmx") -> dict[str, Any]:
        """Calcula próximo periodo de verificación según color de engomado."""
        placa = placa.strip().upper().replace(" ", "").replace("-", "")
        if not placa:
            raise ValidationError("Placa requerida")
        # Último char numérico = terminación
        terminacion = None
        for c in reversed(placa):
            if c.isdigit():
                terminacion = int(c)
                break
        if terminacion is None:
            raise ValidationError(f"Placa '{placa}' sin dígitos.")
        now = datetime.now(timezone.utc)
        color, meses = calcular_proximo_periodo(terminacion, now.month)
        proximo = mes_proxima_verificacion(terminacion, now.month)
        return {
            "placa": placa,
            "estado": estado,
            "terminacion": terminacion,
            "color_engomado": color,
            "meses_obligatorios": meses,
            "proximo_mes_verificacion": proximo if proximo <= 12 else proximo - 12,
            "proximo_anio_verificacion": now.year if proximo <= 12 else now.year + 1,
            "fecha_consulta": now.isoformat(),
        }

    def listar_programas(self) -> dict[str, Any]:
        return {
            "total": len(CATALOGO_VERIFICACION),
            "programas": [{
                "clave": p.clave, "estado": p.nombre_estado, "activo": p.activo,
                "frecuencia_meses": p.frecuencia_meses, "costo_mxn": p.costo_mxn,
                "portal": p.portal_url,
            } for p in CATALOGO_VERIFICACION],
        }

    def _mock(self, p, placa: str) -> dict[str, Any]:
        # Determinístico por último digit
        last_d = "5"
        for c in reversed(placa):
            if c.isdigit():
                last_d = c; break
        hologramas = {"0": "00", "1": "0", "2": "1", "3": "2", "4": "00", "5": "0",
                       "6": "1", "7": "2", "8": "Rechazo", "9": "0"}
        h = hologramas.get(last_d, "0")
        return mark_simulated({
            "placa": placa,
            "estado": p.clave,
            "ultima_verificacion": "2026-04-15",
            "holograma_actual": h,
            "vigencia_hasta": "2026-10-15",
            "vigente": h != "Rechazo",
            "costo_proxima_verificacion_mxn": p.costo_mxn,
            "fuente": p.portal_url,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })
