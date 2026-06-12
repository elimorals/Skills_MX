"""Fixtures mp_softrestaurant."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("SOFT_RESTAURANT_EXPORTS_DIR", raising=False)
    monkeypatch.delenv("SOFT_RESTAURANT_DB_URL", raising=False)


CSV_CORTE_Z_DEMO = """Fecha,Metodo_Pago,Categoria,Importe
2026-03-15,efectivo,fuertes_carne,5800.00
2026-03-15,tarjeta_credito,fuertes_carne,2700.00
2026-03-15,efectivo,bebidas_frias,2400.00
2026-03-15,tarjeta_credito,postres,1200.00
"""

CSV_PLATILLOS_DEMO = """Platillo,Categoria,Cantidad,Precio,Total
Tacos al pastor,fuertes_carne,312,145,45240.00
Pizza Margherita,pastas,189,200,37800.00
Margarita,bebidas_frias,156,100,15600.00
Pozole,fuertes_pollo,12,195,2340.00
"""
