import pytest

from mp_paypal_mx.client import PaypalMxClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in ['PAYPAL_CLIENT_ID', 'PAYPAL_CLIENT_SECRET']:
        monkeypatch.delenv(v, raising=False)


def test_listar_transacciones_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = PaypalMxClient()
    r = c.listar_transacciones()
    assert r.get("simulated") is True
    assert r["operation"] == "listar_transacciones"


def test_consultar_transaccion_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = PaypalMxClient()
    r = c.consultar_transaccion()
    assert r.get("simulated") is True
    assert r["operation"] == "consultar_transaccion"


def test_balance_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = PaypalMxClient()
    r = c.balance()
    assert r.get("simulated") is True
    assert r["operation"] == "balance"


def test_real_path_lanza_error(monkeypatch):
    monkeypatch.setenv("PAYPAL_CLIENT_ID", "x")
    monkeypatch.setenv("PAYPAL_CLIENT_SECRET", "x")
    c = PaypalMxClient()
    with pytest.raises(McpError):
        c.listar_transacciones()
