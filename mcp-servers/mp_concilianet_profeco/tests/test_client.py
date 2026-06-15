"""Tests mp_concilianet_profeco."""
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


def test_consultar_proveedor_aeromexico():
    from mp_concilianet_profeco.client import ConcilianetClient
    c = ConcilianetClient()
    r = c.consultar_proveedor(razon_social="Aeromexico")
    assert r["tiene_convenio_concilianet"] is True


def test_consultar_proveedor_inexistente():
    from mp_concilianet_profeco.client import ConcilianetClient
    c = ConcilianetClient()
    r = c.consultar_proveedor(razon_social="Empresa Sin Convenio XYZ")
    assert r["tiene_convenio_concilianet"] is False


def test_consultar_proveedor_corto():
    from mp_concilianet_profeco.client import ConcilianetClient
    from shared.errors import ValidationError
    c = ConcilianetClient()
    with pytest.raises(ValidationError):
        c.consultar_proveedor(razon_social="x")


def test_estatus_caso_devuelve_avance():
    from mp_concilianet_profeco.client import ConcilianetClient
    c = ConcilianetClient()
    r = c.estatus_caso(folio="ABC12345")
    assert r["porcentaje_avance"] >= 20


def test_listar_proveedores_32():
    from mp_concilianet_profeco.client import ConcilianetClient
    c = ConcilianetClient()
    r = c.listar_proveedores_convenio()
    assert r["total"] >= 30


def test_registrar_queja_ok():
    from mp_concilianet_profeco.client import ConcilianetClient
    c = ConcilianetClient()
    r = c.registrar_queja(consumidor_curp_hash=None, proveedor="Telcel",
                            descripcion="Cobro indebido en plan postpago abril 2026",
                            monto_reclamado_mxn=350)
    assert r["folio_queja"].startswith("PROF-")


def test_registrar_queja_descripcion_corta():
    from mp_concilianet_profeco.client import ConcilianetClient
    from shared.errors import ValidationError
    c = ConcilianetClient()
    with pytest.raises(ValidationError):
        c.registrar_queja(consumidor_curp_hash=None, proveedor="Telcel",
                            descripcion="x")
