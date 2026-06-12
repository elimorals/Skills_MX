import pytest

from mp_kueski.client import KueskiClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in ['KUESKI_API_KEY']:
        monkeypatch.delenv(v, raising=False)


def test_listar_pagos_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = KueskiClient()
    r = c.listar_pagos()
    assert r.get("simulated") is True
    assert r["operation"] == "listar_pagos"


def test_consultar_pago_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = KueskiClient()
    r = c.consultar_pago()
    assert r.get("simulated") is True
    assert r["operation"] == "consultar_pago"


def test_cancelar_pago_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = KueskiClient()
    r = c.cancelar_pago()
    assert r.get("simulated") is True
    assert r["operation"] == "cancelar_pago"


def test_real_path_lanza_error(monkeypatch):
    monkeypatch.setenv("KUESKI_API_KEY", "x")
    c = KueskiClient()
    with pytest.raises(McpError):
        c.listar_pagos()
