import pytest

from mp_cfe_facturacion.client import CfeFactClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in ['CFE_RPU', 'CFE_PASSWORD']:
        monkeypatch.delenv(v, raising=False)


def test_descargar_factura_mes_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = CfeFactClient()
    r = c.descargar_factura_mes()
    assert r.get("simulated") is True
    assert r["operation"] == "descargar_factura_mes"


def test_consumo_historico_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = CfeFactClient()
    r = c.consumo_historico()
    assert r.get("simulated") is True
    assert r["operation"] == "consumo_historico"


def test_real_path_lanza_error(monkeypatch):
    monkeypatch.setenv("CFE_RPU", "x")
    monkeypatch.setenv("CFE_PASSWORD", "x")
    c = CfeFactClient()
    with pytest.raises(McpError):
        c.descargar_factura_mes()
