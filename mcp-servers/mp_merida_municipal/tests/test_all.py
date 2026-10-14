import httpx
import pytest

from mp_merida_municipal.client import URL_PREDIAL, MeridaMunClient


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


def test_predial_handoff_bot_manager():
    r = MeridaMunClient().consultar_predial("60", "500")
    assert r["requiere_humano"] is True and r["motivo"] == "bot_manager"
    assert r["portal"] == URL_PREDIAL and r["simulated"] is False


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert MeridaMunClient().consultar_predial("60", "500")["simulated"] is True


@pytest.mark.live
def test_live_predial_sigue_tras_bot_manager():
    r = httpx.get(URL_PREDIAL, timeout=30, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
    assert "hcaptcha" in r.text.lower() or "perfdrive" in str(r.url)
