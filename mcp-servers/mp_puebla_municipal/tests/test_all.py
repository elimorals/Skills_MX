import httpx
import pytest

from mp_puebla_municipal.client import URL_PREDIAL, PueblaMunClient


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


def test_predial_handoff_captcha():
    r = PueblaMunClient().consultar_predial("1234567")
    assert r["requiere_humano"] is True and r["motivo"] == "captcha"
    assert r["url"] == URL_PREDIAL and r["simulated"] is False


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert PueblaMunClient().consultar_predial("1")["simulated"] is True


@pytest.mark.live
def test_live_predial_sigue_con_captcha():
    html = httpx.get(URL_PREDIAL, timeout=30).text
    assert 'name="answer"' in html and "captcha" in html.lower()
