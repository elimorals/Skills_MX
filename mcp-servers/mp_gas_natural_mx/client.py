"""Cliente mp_gas_natural_mx."""
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
from shared.cache import FileCache  # noqa: E402
from shared.errors import NotFoundError, ValidationError  # noqa: E402
from shared.gas_natural_mx import CATALOGO_GAS_NATURAL, buscar_distribuidor  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "gas_natural_mx"


class GasNaturalMxClient:
    def __init__(self, cache: FileCache | None = None, bitacora: Bitacora | None = None) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_recibo(self, distribuidor: str, contrato: str) -> dict[str, Any]:
        """Consulta recibo mensual (mock-first; path real requiere login)."""
        d = buscar_distribuidor(distribuidor)
        if d is None:
            raise NotFoundError(f"Distribuidor '{distribuidor}' no en catálogo.")
        contrato = contrato.strip()
        if len(contrato) < 4:
            raise ValidationError("contrato muy corto")

        cache_key = f"{d.clave}:{contrato}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        result = self._mock(d, contrato)
        self._cache.set(cache_key, result, ttl_hours=24 * 30)
        self._bitacora.log("consultar_recibo", success=True,
                           params_summary={"distribuidor": d.clave, "contrato_hash": self._bitacora.hash_sensitive(contrato)})
        return result

    def listar_distribuidores(self) -> dict[str, Any]:
        return {
            "total": len(CATALOGO_GAS_NATURAL),
            "distribuidores": [{
                "clave": d.clave, "nombre": d.nombre, "zona": d.zona,
                "portal": d.url_portal, "metodo": d.metodo,
                "poblacion_aprox": d.poblacion_aprox,
            } for d in CATALOGO_GAS_NATURAL],
        }

    def _mock(self, d, contrato: str) -> dict[str, Any]:
        last = contrato[-1] if contrato[-1].isdigit() else "5"
        consumo_m3 = 15 + int(last) * 8
        monto = round(consumo_m3 * 14.50, 2)
        return mark_simulated({
            "distribuidor": d.clave,
            "contrato": contrato,
            "periodo": "2026-05",
            "consumo_m3": consumo_m3,
            "monto_mxn": monto,
            "vencimiento": "2026-08-20",
            "estatus": "PENDIENTE" if int(last) % 2 == 1 else "PAGADA",
            "fuente": d.url_portal,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })
