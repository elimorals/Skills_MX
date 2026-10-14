import httpx
import pytest

from mp_guadalajara_municipal.client import URL_PREDIAL, URL_VEHICULAR_JAL, GuadalajaraMunClient


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


def test_predial_handoff_captcha():
    r = GuadalajaraMunClient().consultar_predial("123456")
    assert r["requiere_humano"] is True and r["motivo"] == "captcha"
    assert r["url"] == URL_PREDIAL and r["simulated"] is False


def test_multas_handoff_captcha():
    r = GuadalajaraMunClient().consultar_adeudos_vehiculares("JAL1234")
    assert r["requiere_humano"] is True and r["url"] == URL_VEHICULAR_JAL


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert GuadalajaraMunClient().consultar_predial("1")["simulated"] is True


@pytest.mark.live
def test_live_predial_sigue_con_recaptcha():
    """Si el portal quita el reCAPTCHA, este test falla: hay que implementar la consulta directa."""
    js = httpx.get(URL_PREDIAL + "main.js", timeout=30).text
    assert "consulta_adeudo" in js and "grecaptcha" in js


@pytest.mark.live
def test_live_vehicular_sigue_con_recaptcha():
    html = httpx.get(URL_VEHICULAR_JAL, timeout=30).text.lower()
    assert "recaptcha" in html
