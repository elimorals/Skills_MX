"""Tests mp_gas_natural_mx."""
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


def test_naturgy_consulta():
    from mp_gas_natural_mx.client import GasNaturalMxClient
    c = GasNaturalMxClient()
    r = c.consultar_recibo("naturgy", "12345678")
    assert r["distribuidor"] == "naturgy"
    assert "consumo_m3" in r
    assert r["simulated"] is True


def test_distribuidor_invalido():
    from mp_gas_natural_mx.client import GasNaturalMxClient
    from shared.errors import NotFoundError
    c = GasNaturalMxClient()
    with pytest.raises(NotFoundError):
        c.consultar_recibo("xx", "12345")


def test_contrato_corto():
    from mp_gas_natural_mx.client import GasNaturalMxClient
    from shared.errors import ValidationError
    c = GasNaturalMxClient()
    with pytest.raises(ValidationError):
        c.consultar_recibo("naturgy", "1")


def test_listar_5_distribuidores():
    from mp_gas_natural_mx.client import GasNaturalMxClient
    c = GasNaturalMxClient()
    r = c.listar_distribuidores()
    assert r["total"] == 5
