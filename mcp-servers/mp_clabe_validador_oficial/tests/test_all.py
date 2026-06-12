import pytest

from mp_clabe_validador_oficial.client import ClabeValidadorClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in []:
        monkeypatch.delenv(v, raising=False)


def test_validar_clabe_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = ClabeValidadorClient()
    r = c.validar_clabe()
    assert r.get("simulated") is True
    assert r["operation"] == "validar_clabe"


def test_info_banco_clabe_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = ClabeValidadorClient()
    r = c.info_banco_clabe()
    assert r.get("simulated") is True
    assert r["operation"] == "info_banco_clabe"



