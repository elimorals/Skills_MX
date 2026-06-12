"""Cliente Rappi Partners — mock-first."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "rappi_partners"
CRED_VARS = ["RAPPI_PARTNERS_TOKEN", "RAPPI_STORE_ID"]


class RappiPartnersClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self._token = os.environ.get("RAPPI_PARTNERS_TOKEN", "")
        self._store_id = os.environ.get("RAPPI_STORE_ID", "")

    def _is_mock(self) -> bool:
        return is_mock_mode(CRED_VARS)

    def _log(self, op: str, *, success: bool, params: dict[str, Any] | None = None) -> None:
        self.bitacora.log(op, success=success, params_summary=params or {})

    # ---------- tools ----------

    def listar_ordenes(self, estado: str = "all", limite: int = 20) -> dict[str, Any]:
        self._log("listar_ordenes", success=True, params={"estado": estado, "limite": limite})
        if self._is_mock():
            now = datetime.now(timezone.utc)
            ordenes = [
                {
                    "orden_id": f"RAP-MOCK-{i:05d}",
                    "fecha": (now - timedelta(hours=i)).isoformat(),
                    "estado": "entregada" if i > 3 else "en_camino",
                    "total_mxn": str(Decimal("250.00") + Decimal(i) * Decimal("50")),
                    "items_count": (i % 5) + 1,
                    "comision_rappi_mxn": str(Decimal("75.00") + Decimal(i) * Decimal("15")),
                    "neto_mxn": str(Decimal("175.00") + Decimal(i) * Decimal("35")),
                }
                for i in range(min(limite, 10))
            ]
            if estado != "all":
                ordenes = [o for o in ordenes if o["estado"] == estado]
            return mark_simulated({"store_id_hash": Bitacora.hash_sensitive(self._store_id or "MOCK"), "total": len(ordenes), "ordenes": ordenes})
        raise McpError("Path Rappi real no implementado — requiere onboarding como Partner", {"hint": "ver mp_rappi_partners/README.md"})

    def consultar_orden(self, orden_id: str) -> dict[str, Any]:
        self._log("consultar_orden", success=True, params={"orden_id": orden_id})
        if self._is_mock():
            return mark_simulated({
                "orden_id": orden_id,
                "estado": "entregada",
                "items": [
                    {"sku": "PROD-001", "nombre": "Tacos al pastor (3)", "cantidad": 2, "precio_mxn": "120.00"},
                    {"sku": "PROD-002", "nombre": "Refresco", "cantidad": 1, "precio_mxn": "30.00"},
                ],
                "subtotal_mxn": "270.00",
                "envio_mxn": "0.00",
                "total_mxn": "270.00",
                "comision_rappi_mxn": "81.00",
                "neto_mxn": "189.00",
                "cliente_hash": Bitacora.hash_sensitive("MOCK_CLIENT"),
            })
        raise McpError("Real path no implementado", {"hint": "ver README"})

    def listar_productos_menu(self) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({
                "store_id_hash": Bitacora.hash_sensitive(self._store_id or "MOCK"),
                "productos": [
                    {"sku": "PROD-001", "nombre": "Tacos al pastor (3)", "precio_mxn": "120.00", "disponible": True, "categoria": "comida"},
                    {"sku": "PROD-002", "nombre": "Refresco 500ml", "precio_mxn": "30.00", "disponible": True, "categoria": "bebidas"},
                    {"sku": "PROD-003", "nombre": "Especial 2x1", "precio_mxn": "200.00", "disponible": False, "categoria": "promociones"},
                ],
                "total": 3,
            })
        raise McpError("Real path no implementado")

    def actualizar_disponibilidad(self, sku: str, disponible: bool) -> dict[str, Any]:
        self._log("actualizar_disponibilidad", success=True, params={"sku": sku, "disponible": disponible})
        if self._is_mock():
            return mark_simulated({"sku": sku, "disponible": disponible, "actualizado_en": datetime.now(timezone.utc).isoformat()})
        raise McpError("Real path no implementado")

    def consultar_ranking_zona(self) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({
                "store_id_hash": Bitacora.hash_sensitive(self._store_id or "MOCK"),
                "zona": "MOCK_ZONE_CDMX",
                "ranking_categoria": 7,
                "total_restaurantes_zona": 42,
                "rating_promedio": 4.6,
                "reviews_count": 234,
                "horas_pico_top": ["13:00-14:30", "20:00-22:00"],
            })
        raise McpError("Real path no implementado")

    def estimar_comisiones_mes(self, mes: str | None = None) -> dict[str, Any]:
        if self._is_mock():
            now = datetime.now(timezone.utc)
            mes = mes or now.strftime("%Y-%m")
            return mark_simulated({
                "mes": mes,
                "ordenes_count": 145,
                "gross_mxn": "62500.00",
                "comision_rappi_mxn": "18750.00",
                "comision_porcentaje": 30.0,
                "neto_mxn": "43750.00",
                "estado_facturacion": "pendiente_cfdi_rappi",
            })
        raise McpError("Real path no implementado")
