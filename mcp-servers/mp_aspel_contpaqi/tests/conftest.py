"""Fixtures compartidos para mp_aspel_contpaqi tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    """Aisla cache/audit y default a mock."""
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("ASPEL_EXPORTS_DIR", raising=False)
    monkeypatch.delenv("CONTPAQI_AGENT_URL", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


# Constantes de prueba

CSV_POLIZAS_DEMO = """Numero,Fecha,Tipo,Concepto,Cuenta,Debe,Haber
D-001,2026-03-02,DIARIO,Renta oficina,601-001,30000.00,0.00
D-001,2026-03-02,DIARIO,Renta oficina,120-001,4800.00,0.00
D-001,2026-03-02,DIARIO,Renta oficina,102-001,0.00,34800.00
I-002,2026-03-05,INGRESOS,Cobro Tech Demo,102-001,58000.00,0.00
I-002,2026-03-05,INGRESOS,Cobro Tech Demo,401-001,0.00,50000.00
I-002,2026-03-05,INGRESOS,Cobro Tech Demo,215-001,0.00,8000.00
"""

CSV_BALANZA_DEMO = """Cuenta,Nombre,Saldo Inicial,Cargos,Abonos,Saldo Final
102-001,Bancos BBVA,350000.00,58000.00,34800.00,373200.00
401-001,Ingresos por servicios,0.00,0.00,50000.00,-50000.00
601-001,Renta oficina,0.00,30000.00,0.00,30000.00
"""

CSV_CATALOGO_DEMO = """Cuenta,Nombre,Codigo SAT,Naturaleza,Nivel
102-001,Bancos BBVA,102,DEUDORA,3
401-001,Ingresos por servicios,401,ACREEDORA,3
601-001,Renta oficina,600,DEUDORA,3
"""
