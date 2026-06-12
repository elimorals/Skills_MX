"""Cliente DiDi Food Partners — mock-first."""

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

NAMESPACE = "didi_food_partners"
CRED_VARS = ["DIDI_FOOD_TOKEN", "DIDI_FOOD_RESTAURANT_ID"]


class DidiFoodPartnersClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self._token = os.environ.get("DIDI_FOOD_TOKEN", "")
        self._rest_id = os.environ.get("DIDI_FOOD_RESTAURANT_ID", "")

    def _is_mock(self) -> bool:
        return is_mock_mode(CRED_VARS)

    def listar_ordenes(self, estado: str = "all", limite: int = 20) -> dict[str, Any]:
        self.bitacora.log("listar_ordenes", success=True, params_summary={"estado": estado})
        if self._is_mock():
            now = datetime.now(timezone.utc)
            ordenes = [
                {
                    "orden_id": f"DDF-MOCK-{i:05d}",
                    "fecha": (now - timedelta(hours=i)).isoformat(),
                    "estado": "entregada" if i > 2 else "preparando",
                    "total_mxn": str(Decimal("180.00") + Decimal(i) * Decimal("45")),
                    "items_count": (i % 4) + 1,
                    "comision_didi_mxn": str(Decimal("54.00") + Decimal(i) * Decimal("13.5")),
                    "neto_mxn": str(Decimal("126.00") + Decimal(i) * Decimal("31.5")),
                }
                for i in range(min(limite, 10))
            ]
            if estado != "all":
                ordenes = [o for o in ordenes if o["estado"] == estado]
            return mark_simulated({"restaurant_id_hash": Bitacora.hash_sensitive(self._rest_id or "MOCK"), "total": len(ordenes), "ordenes": ordenes})
        raise McpError("Real path no implementado — DiDi Food requiere onboarding como Partner")

    def consultar_orden(self, orden_id: str) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({
                "orden_id": orden_id,
                "estado": "entregada",
                "items": [
                    {"sku": "DDF-PROD-001", "nombre": "Hamburguesa clásica", "cantidad": 1, "precio_mxn": "150.00"},
                    {"sku": "DDF-PROD-002", "nombre": "Papas grandes", "cantidad": 1, "precio_mxn": "60.00"},
                ],
                "subtotal_mxn": "210.00",
                "envio_mxn": "0.00",
                "total_mxn": "210.00",
                "comision_didi_mxn": "63.00",
                "neto_mxn": "147.00",
                "cliente_hash": Bitacora.hash_sensitive("MOCK_CLIENT"),
            })
        raise McpError("Real path no implementado")

    def listar_productos_menu(self) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({
                "restaurant_id_hash": Bitacora.hash_sensitive(self._rest_id or "MOCK"),
                "productos": [
                    {"sku": "DDF-PROD-001", "nombre": "Hamburguesa clásica", "precio_mxn": "150.00", "disponible": True},
                    {"sku": "DDF-PROD-002", "nombre": "Papas grandes", "precio_mxn": "60.00", "disponible": True},
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
                "restaurant_id_hash": Bitacora.hash_sensitive(self._rest_id or "MOCK"),
                "ranking_categoria": 12,
                "total_restaurantes_zona": 38,
                "rating_promedio": 4.4,
                "reviews_count": 187,
            })
        raise McpError("Real path no implementado")

    def estimar_comisiones_mes(self, mes: str | None = None) -> dict[str, Any]:
        if self._is_mock():
            mes = mes or datetime.now(timezone.utc).strftime("%Y-%m")
            return mark_simulated({
                "mes": mes,
                "ordenes_count": 112,
                "gross_mxn": "48500.00",
                "comision_didi_mxn": "14550.00",
                "comision_porcentaje": 30.0,
                "neto_mxn": "33950.00",
            })
        raise McpError("Real path no implementado")
