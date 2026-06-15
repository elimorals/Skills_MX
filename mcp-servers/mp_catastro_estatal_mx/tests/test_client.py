"""Tests mp_catastro_estatal_mx."""
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
    yield


class TestCatalogo:
    def test_igecem_existe(self):
        from shared.catastro_estatal import buscar_catastro
        c = buscar_catastro("igecem")
        assert c is not None
        assert c.cobertura_muns == 125

    def test_listar_5_sistemas(self):
        from shared.catastro_estatal import listar_catastros
        assert len(listar_catastros()) >= 5


class TestConsultarValor:
    def test_igecem_ccu_valida(self):
        from mp_catastro_estatal_mx.client import CatastroEstatalClient
        c = CatastroEstatalClient()
        r = c.consultar_valor("igecem", "1234567890123456")  # 16 dígitos
        assert "valor_catastral_mxn" in r
        assert r["valor_catastral_mxn"] > 0
        assert r["simulated"] is True

    def test_igecem_ccu_invalida(self):
        from mp_catastro_estatal_mx.client import CatastroEstatalClient
        from shared.errors import ValidationError
        c = CatastroEstatalClient()
        with pytest.raises(ValidationError):
            c.consultar_valor("igecem", "123")  # menos de 16

    def test_sistema_inexistente(self):
        from mp_catastro_estatal_mx.client import CatastroEstatalClient
        from shared.errors import NotFoundError
        c = CatastroEstatalClient()
        with pytest.raises(NotFoundError):
            c.consultar_valor("xxx", "123456789012")


class TestListar:
    def test_listar_devuelve_estructura(self):
        from mp_catastro_estatal_mx.client import CatastroEstatalClient
        c = CatastroEstatalClient()
        r = c.listar_sistemas()
        assert r["total"] >= 5
        assert any(s["clave"] == "igecem" for s in r["sistemas"])
