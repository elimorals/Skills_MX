"""Tests mp_catastro_estatal_mx."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import respx

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
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


class TestReal:
    @respx.mock
    def test_igecem_handoff(self, monkeypatch):
        from mp_catastro_estatal_mx.client import CatastroEstatalClient
        from shared.portal_handoff import IGECEM_EDOMEX
        monkeypatch.delenv("PLUGINS_MX_MOCK")
        respx.get(IGECEM_EDOMEX.url).respond(200, text="<title>IGECEM</title>")
        r = CatastroEstatalClient().consultar_valor("igecem", "1501010010010000")
        assert r["simulated"] is False
        assert r["motivo"] == "flujo_no_automatizado"

    def test_login_es_error_explicito(self, monkeypatch):
        from mp_catastro_estatal_mx.server import ConsultarInput, catastro_consultar_valor
        monkeypatch.delenv("PLUGINS_MX_MOCK")
        r = catastro_consultar_valor(ConsultarInput(sistema="ircep", cuenta_catastral="123456789012"))
        assert r["code"] == "upstream_error"

    @pytest.mark.live
    def test_live_igecem(self, monkeypatch):
        from mp_catastro_estatal_mx.client import CatastroEstatalClient
        monkeypatch.delenv("PLUGINS_MX_MOCK")
        r = CatastroEstatalClient().consultar_valor("igecem", "1501010010010000")
        assert r["portal_verificado"]["status_code"] == 200
