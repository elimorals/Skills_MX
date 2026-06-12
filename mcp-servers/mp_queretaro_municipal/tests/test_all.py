import pytest

from mp_queretaro_municipal.client import QueretaroMunClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in []:
        monkeypatch.delenv(v, raising=False)


def test_consultar_multas_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = QueretaroMunClient()
    r = c.consultar_multas()
    assert r.get("simulated") is True
    assert r["operation"] == "consultar_multas"


def test_consultar_predial_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = QueretaroMunClient()
    r = c.consultar_predial()
    assert r.get("simulated") is True
    assert r["operation"] == "consultar_predial"



