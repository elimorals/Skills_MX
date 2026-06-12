import pytest

from mp_didi_partners.client import DidiPartnersClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in ['DIDI_DRIVER_TOKEN']:
        monkeypatch.delenv(v, raising=False)


def test_listar_viajes_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = DidiPartnersClient()
    r = c.listar_viajes()
    assert r.get("simulated") is True
    assert r["operation"] == "listar_viajes"


def test_consultar_viaje_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = DidiPartnersClient()
    r = c.consultar_viaje()
    assert r.get("simulated") is True
    assert r["operation"] == "consultar_viaje"


def test_comisiones_mes_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = DidiPartnersClient()
    r = c.comisiones_mes()
    assert r.get("simulated") is True
    assert r["operation"] == "comisiones_mes"


def test_real_path_lanza_error(monkeypatch):
    monkeypatch.setenv("DIDI_DRIVER_TOKEN", "x")
    c = DidiPartnersClient()
    with pytest.raises(McpError):
        c.listar_viajes()
