"""Cliente Soft Restaurant — POS local sin API REST.

Modo real: parsea archivos CSV exportados desde Soft Restaurant.
Mock-first sin SOFT_RESTAURANT_EXPORTS_DIR configurado.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, NotFoundError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

from mp_softrestaurant import export_parser, mock_data  # noqa: E402


NAMESPACE = "softrestaurant_mcp"
CRED_VARS = ["SOFT_RESTAURANT_EXPORTS_DIR", "SOFT_RESTAURANT_DB_URL"]


class SoftRestaurantClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._exports_dir = os.environ.get("SOFT_RESTAURANT_EXPORTS_DIR", "").strip()

    def _mock(self) -> bool:
        return is_mock_mode(CRED_VARS)

    def _exports_path(self) -> Path | None:
        if not self._exports_dir:
            return None
        p = Path(self._exports_dir).expanduser()
        return p if p.exists() else None

    def _read_export(self, filename: str) -> str | None:
        root = self._exports_path()
        if not root:
            return None
        p = root / filename
        if not p.exists():
            return None
        try:
            return p.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            return None

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    # ---------- tools ----------

    def corte_z_del_dia(self, fecha: str) -> dict[str, Any]:
        if not fecha or len(fecha) != 10:
            raise ValidationError("fecha en formato YYYY-MM-DD requerida")
        self._log("corte_z", {"fecha": fecha})

        if self._mock():
            return mark_simulated(
                mock_data.mock_corte_z(fecha),
                "Modo mock — Soft Restaurant ERP no consultado.",
            )

        contenido = self._read_export(f"corte_z_{fecha.replace('-', '')}.csv")
        if contenido is None:
            return mark_simulated(
                mock_data.mock_corte_z(fecha),
                f"Archivo corte_z_{fecha}.csv no encontrado — usando demo.",
            )

        data = export_parser.parsear_csv_corte_z(contenido)
        return {"fecha": fecha, **data, "fuente": "soft_restaurant_csv", "simulated": False}

    def ventas_periodo(self, desde: str, hasta: str) -> dict[str, Any]:
        self._log("ventas_periodo", {"desde": desde, "hasta": hasta})

        if self._mock():
            return mark_simulated(mock_data.mock_ventas_periodo(desde, hasta))

        filename = f"ventas_{desde.replace('-', '')}_{hasta.replace('-', '')}.csv"
        contenido = self._read_export(filename)
        if contenido is None:
            return mark_simulated(
                mock_data.mock_ventas_periodo(desde, hasta),
                f"Archivo {filename} no encontrado — usando demo.",
            )

        ventas = export_parser.parsear_csv_ventas_periodo(contenido)
        total = sum(float(v.get("total_mxn", "0")) for v in ventas)
        return {
            "periodo": {"desde": desde, "hasta": hasta},
            "total_ventas_mxn": str(total),
            "total_tickets": len(ventas),
            "ventas": ventas[:50],  # truncate para no devolver listas enormes
            "fuente": filename,
            "simulated": False,
        }

    def inventario_actual(self) -> dict[str, Any]:
        self._log("inventario_actual", {})
        if self._mock():
            return mark_simulated(mock_data.mock_inventario_actual())
        raise UpstreamError(
            "Inventario requiere export CSV o conexión ODBC. Configurar SOFT_RESTAURANT_EXPORTS_DIR."
        )

    def platillos_vendidos(self, periodo: str) -> dict[str, Any]:
        self._log("platillos_vendidos", {"periodo": periodo})

        if self._mock():
            return mark_simulated(mock_data.mock_platillos_vendidos(periodo))

        contenido = self._read_export(f"platillos_{periodo.replace('-', '')}.csv")
        if contenido is None:
            return mark_simulated(
                mock_data.mock_platillos_vendidos(periodo),
                "Archivo platillos no encontrado — usando demo.",
            )

        platillos = export_parser.parsear_csv_platillos_vendidos(contenido)
        platillos_ordenados = sorted(platillos, key=lambda p: -int(p.get("cantidad_vendida", 0)))
        return {
            "periodo": periodo,
            "total_platillos_distintos": len(platillos),
            "top_5_mas_vendidos": platillos_ordenados[:5],
            "top_5_menos_vendidos": platillos_ordenados[-5:] if len(platillos_ordenados) > 5 else [],
            "fuente": "soft_restaurant_csv",
            "simulated": False,
        }

    def meseros_ventas(self, fecha: str) -> dict[str, Any]:
        self._log("meseros_ventas", {"fecha": fecha})
        if self._mock():
            return mark_simulated(mock_data.mock_meseros_ventas())
        raise UpstreamError(
            "Requiere export CSV ventas por mesero. Configurar exports dir."
        )

    def mesas_estatus(self) -> dict[str, Any]:
        self._log("mesas_estatus", {})
        if self._mock():
            return mark_simulated(mock_data.mock_mesas_estatus())
        raise UpstreamError(
            "Estatus en tiempo real de mesas requiere conexión ODBC al SQL Server local."
        )

    def parsear_export(self, tipo: str, contenido_csv: str) -> dict[str, Any]:
        """Parsea contenido CSV pasado inline."""
        tipo_norm = tipo.lower().strip()
        if tipo_norm == "corte_z":
            return {"tipo": tipo_norm, "data": export_parser.parsear_csv_corte_z(contenido_csv)}
        if tipo_norm == "ventas_periodo":
            data = export_parser.parsear_csv_ventas_periodo(contenido_csv)
            return {"tipo": tipo_norm, "total": len(data), "data": data}
        if tipo_norm == "platillos_vendidos":
            data = export_parser.parsear_csv_platillos_vendidos(contenido_csv)
            return {"tipo": tipo_norm, "total": len(data), "data": data}
        raise McpError(
            f"Tipo desconocido: {tipo}. Usar: corte_z, ventas_periodo, platillos_vendidos."
        )
