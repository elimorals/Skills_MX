"""Tests mp_cre_hidrocarburos."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_consultar_permiso():
    from mp_cre_hidrocarburos.client import CREClient
    c = CREClient()
    r = c.consultar_permiso(identificador="CRE/100/2024")
    assert "tipo_permiso" in r


def test_consultar_permiso_corto():
    from mp_cre_hidrocarburos.client import CREClient
    from shared.errors import ValidationError
    c = CREClient()
    with pytest.raises(ValidationError):
        c.consultar_permiso(identificador="x")


def test_calendar_12_obligaciones():
    from mp_cre_hidrocarburos.client import CREClient
    c = CREClient()
    r = c.calendar_reporte_mensual(anio=2026, mes_actual=6)
    assert len(r["proximas_obligaciones"]) == 12


def test_anexo30_aplica_alto_consumo():
    from mp_cre_hidrocarburos.client import CREClient
    c = CREClient()
    r = c.evaluar_anexo30(litros_mes_max=80_000, tiene_permiso_cre=False)
    assert r["aplica_anexo30_sat"] is True


def test_anexo30_no_aplica_bajo_consumo():
    from mp_cre_hidrocarburos.client import CREClient
    c = CREClient()
    r = c.evaluar_anexo30(litros_mes_max=5_000, tiene_permiso_cre=False)
    assert r["aplica_anexo30_sat"] is False


def test_anexo30_aplica_si_tiene_permiso():
    from mp_cre_hidrocarburos.client import CREClient
    c = CREClient()
    r = c.evaluar_anexo30(litros_mes_max=100, tiene_permiso_cre=True)
    assert r["aplica_anexo30_sat"] is True


def test_reportar_zeros_ok():
    from mp_cre_hidrocarburos.client import CREClient
    c = CREClient()
    r = c.reportar_zeros(num_permiso="CRE/100/2024", periodo="2026-05")
    assert r["ventas_litros"] == 0
    assert r["reporte_aceptado"] is True


def test_reportar_zeros_periodo_invalido():
    from mp_cre_hidrocarburos.client import CREClient
    from shared.errors import ValidationError
    c = CREClient()
    with pytest.raises(ValidationError):
        c.reportar_zeros(num_permiso="CRE/100/2024", periodo="2026/05")


def test_listar_tipos_permiso():
    from mp_cre_hidrocarburos.client import CREClient
    c = CREClient()
    r = c.listar_tipos_permiso()
    assert r["total"] >= 6
