import pytest

from mp_klap.client import KlapClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in ['KLAP_API_KEY']:
        monkeypatch.delenv(v, raising=False)


def test_listar_pagos_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = KlapClient()
    r = c.listar_pagos()
    assert r.get("simulated") is True
    assert r["operation"] == "listar_pagos"


def test_consultar_pago_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = KlapClient()
    r = c.consultar_pago()
    assert r.get("simulated") is True
    assert r["operation"] == "consultar_pago"


def test_real_path_lanza_error(monkeypatch):
    monkeypatch.setenv("KLAP_API_KEY", "x")
    c = KlapClient()
    with pytest.raises(McpError):
        c.listar_pagos()
