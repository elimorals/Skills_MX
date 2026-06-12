import pytest

from mp_telmex_facturacion.client import TelmexFactClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in ['TELMEX_RFC', 'TELMEX_PASSWORD']:
        monkeypatch.delenv(v, raising=False)


def test_descargar_factura_mes_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = TelmexFactClient()
    r = c.descargar_factura_mes()
    assert r.get("simulated") is True
    assert r["operation"] == "descargar_factura_mes"


def test_listar_facturas_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = TelmexFactClient()
    r = c.listar_facturas()
    assert r.get("simulated") is True
    assert r["operation"] == "listar_facturas"


def test_real_path_lanza_error(monkeypatch):
    monkeypatch.setenv("TELMEX_RFC", "x")
    monkeypatch.setenv("TELMEX_PASSWORD", "x")
    c = TelmexFactClient()
    with pytest.raises(McpError):
        c.descargar_factura_mes()
