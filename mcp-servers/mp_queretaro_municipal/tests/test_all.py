import json
import os

import httpx
import pytest
import respx

from mp_queretaro_municipal.client import BASE_URL, QueretaroMunClient
from shared.errors import NotFoundError, UpstreamError, ValidationError

CLAVE = "140100100100001"


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


def _agenda(status: int) -> httpx.Response:
    return httpx.Response(200, json={"codigo": "000", "mensaje": "", "datos": json.dumps({"status": status})})


@respx.mock
def test_predial_con_adeudo():
    respx.post(BASE_URL + "agenda_digital.php").mock(return_value=_agenda(200))
    respx.get(BASE_URL + "functions.php").mock(return_value=httpx.Response(200, json={
        "periodos": ["2026-1"], "direccion": "CALLE X", "importe": "1,520.00",
        "fechavigen": "31/10/2026", "lineacap": "123",
    }))
    r = QueretaroMunClient().consultar_predial(CLAVE, "abcd")
    assert r["importe_mxn"] == 1520.0
    assert r["estatus"] == "con_adeudo"
    assert r["simulated"] is False


@respx.mock
def test_predial_propietario_no_coincide():
    respx.post(BASE_URL + "agenda_digital.php").mock(return_value=_agenda(201))
    fn = respx.get(BASE_URL + "functions.php")
    with pytest.raises(NotFoundError):
        QueretaroMunClient().consultar_predial(CLAVE, "ABCD")
    assert not fn.called  # no se salta la validación del propietario


@respx.mock
def test_predial_sin_adeudo():
    respx.post(BASE_URL + "agenda_digital.php").mock(return_value=_agenda(1))
    respx.get(BASE_URL + "functions.php").mock(return_value=httpx.Response(200, json={
        "errmsg": "La clave catastral 1 sin adeudo", "periodos": []}))
    r = QueretaroMunClient().consultar_predial(CLAVE, "ABCD")
    assert r["estatus"] == "al_corriente" and r["importe_mxn"] == 0.0


@respx.mock
def test_predial_upstream_caido():
    respx.post(BASE_URL + "agenda_digital.php").mock(return_value=httpx.Response(503))
    with pytest.raises(UpstreamError):
        QueretaroMunClient().consultar_predial(CLAVE, "ABCD")


@respx.mock
def test_predial_respuesta_no_json():
    respx.post(BASE_URL + "agenda_digital.php").mock(return_value=httpx.Response(200, text="<html>"))
    with pytest.raises(UpstreamError):
        QueretaroMunClient().consultar_predial(CLAVE, "ABCD")


def test_validacion_clave():
    with pytest.raises(ValidationError):
        QueretaroMunClient().consultar_predial("123", "ABCD")


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert QueretaroMunClient().consultar_predial(CLAVE, "ABCD")["simulated"] is True


@pytest.mark.live
def test_live_clave_inexistente():
    """Clave ficticia: el portal debe responder 'sin coincidencias' (NotFoundError)."""
    with pytest.raises(NotFoundError):
        QueretaroMunClient().consultar_predial(CLAVE, "ABCD")


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("QRO_CLAVE_CATASTRAL"), reason="exporta QRO_CLAVE_CATASTRAL y QRO_LETRAS")
def test_live_clave_real():
    r = QueretaroMunClient().consultar_predial(os.environ["QRO_CLAVE_CATASTRAL"], os.environ["QRO_LETRAS"])
    assert r["simulated"] is False and "importe_mxn" in r
