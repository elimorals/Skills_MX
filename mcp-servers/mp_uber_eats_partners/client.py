"""Cliente Uber Eats Partners — mock-first."""

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

NAMESPACE = "uber_eats_partners"
CRED_VARS = ["UBER_EATS_CLIENT_ID", "UBER_EATS_CLIENT_SECRET", "UBER_EATS_STORE_ID"]


class UberEatsPartnersClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self._client_id = os.environ.get("UBER_EATS_CLIENT_ID", "")
        self._store_id = os.environ.get("UBER_EATS_STORE_ID", "")

    def _is_mock(self) -> bool:
        return is_mock_mode(CRED_VARS)

    def listar_ordenes(self, estado: str = "all", limite: int = 20) -> dict[str, Any]:
        self.bitacora.log("listar_ordenes", success=True, params_summary={"estado": estado})
        if self._is_mock():
            now = datetime.now(timezone.utc)
            ordenes = [
                {
                    "orden_id": f"UE-MOCK-{i:05d}",
                    "fecha": (now - timedelta(hours=i)).isoformat(),
                    "estado": "DELIVERED" if i > 3 else "IN_PROGRESS",
                    "total_mxn": str(Decimal("220.00") + Decimal(i) * Decimal("55")),
                    "items_count": (i % 4) + 1,
                    "comision_uber_mxn": str(Decimal("66.00") + Decimal(i) * Decimal("16.5")),
                    "neto_mxn": str(Decimal("154.00") + Decimal(i) * Decimal("38.5")),
                }
                for i in range(min(limite, 10))
            ]
            if estado != "all":
                ordenes = [o for o in ordenes if o["estado"].lower() == estado.lower()]
            return mark_simulated({"store_id_hash": Bitacora.hash_sensitive(self._store_id or "MOCK"), "total": len(ordenes), "ordenes": ordenes})
        raise McpError("Path Uber Eats real no implementado — requiere Marketplace API access")

    def consultar_orden(self, orden_id: str) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({
                "orden_id": orden_id,
                "estado": "DELIVERED",
                "items": [
                    {"sku": "UE-PROD-001", "nombre": "Sushi roll especial", "cantidad": 2, "precio_mxn": "180.00"},
                ],
                "subtotal_mxn": "360.00",
                "envio_mxn": "0.00",
                "total_mxn": "360.00",
                "comision_uber_mxn": "108.00",
                "neto_mxn": "252.00",
                "cliente_hash": Bitacora.hash_sensitive("MOCK_CLIENT"),
            })
        raise McpError("Real path no implementado")

    def listar_productos_menu(self) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({
                "store_id_hash": Bitacora.hash_sensitive(self._store_id or "MOCK"),
                "productos": [
                    {"sku": "UE-PROD-001", "nombre": "Sushi roll especial", "precio_mxn": "180.00", "disponible": True},
                    {"sku": "UE-PROD-002", "nombre": "Sopa miso", "precio_mxn": "65.00", "disponible": True},
                ],
                "total": 2,
            })
        raise McpError("Real path no implementado")

    def actualizar_disponibilidad(self, sku: str, disponible: bool) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({"sku": sku, "disponible": disponible, "actualizado_en": datetime.now(timezone.utc).isoformat()})
        raise McpError("Real path no implementado")

    def consultar_ranking_zona(self) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({
                "store_id_hash": Bitacora.hash_sensitive(self._store_id or "MOCK"),
                "ranking_categoria": 5,
                "total_restaurantes_zona": 31,
                "rating_promedio": 4.7,
                "reviews_count": 412,
            })
        raise McpError("Real path no implementado")

    def estimar_comisiones_mes(self, mes: str | None = None) -> dict[str, Any]:
        if self._is_mock():
            mes = mes or datetime.now(timezone.utc).strftime("%Y-%m")
            return mark_simulated({
                "mes": mes,
                "ordenes_count": 95,
                "gross_mxn": "55300.00",
                "comision_uber_mxn": "16590.00",
                "comision_porcentaje": 30.0,
                "neto_mxn": "38710.00",
            })
        raise McpError("Real path no implementado")
