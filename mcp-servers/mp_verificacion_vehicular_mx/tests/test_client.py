"""Tests mp_verificacion_vehicular_mx."""
from __future__ import annotations

import pytest
import respx

from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
from mp_verificacion_vehicular_mx.server import ConsultarInput, verificacion_consultar_estatus
from shared.errors import NotFoundError, UpstreamError, ValidationError
from shared.portal_handoff import SAF_CDMX_ADEUDOS
from shared.verificacion_vehicular import calcular_proximo_periodo, mes_proxima_verificacion


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))


@pytest.fixture
def c() -> VerificacionVehicularClient:
    return VerificacionVehicularClient()


@pytest.mark.parametrize("term,color,meses", [
    (5, "amarillo", [1, 2, 7, 8]),
    (8, "rosa", [2, 3, 8, 9]),
    (3, "rojo", [3, 4, 9, 10]),
    (1, "verde", [4, 5, 10, 11]),
    (0, "azul", [5, 6, 11, 12]),
])
def test_calendario_2026(term, color, meses) -> None:
    assert calcular_proximo_periodo(term, 1) == (color, meses)


def test_proximo_mes_cruza_anio() -> None:
    assert mes_proxima_verificacion(5, 10) == 13  # amarillo: siguiente es enero
    assert mes_proxima_verificacion(0, 10) == 11


def test_terminacion_invalida() -> None:
    with pytest.raises(ValueError):
        calcular_proximo_periodo(15, 6)


def test_proximo_periodo_fuera_de_megalopolis(c) -> None:
    with pytest.raises(ValidationError):
        c.proximo_periodo("ABC1235", "jal")


def test_proximo_periodo_real(c) -> None:
    r = c.proximo_periodo("ABC1235", "cdmx")
    assert r["color_engomado"] == "amarillo"
    assert r["simulated"] is False
    assert r["fuentes"]


@respx.mock
def test_estatus_cdmx_handoff(c) -> None:
    respx.get(SAF_CDMX_ADEUDOS.url).respond(200, text='<input id="captcha_code">')
    r = c.consultar_estatus("ABC-1234", "cdmx")
    assert r["status"] == "requiere_humano"
    assert r["placa"] == "ABC1234"


@respx.mock
def test_estatus_cdmx_portal_caido(c) -> None:
    respx.get(SAF_CDMX_ADEUDOS.url).respond(503)
    with pytest.raises(UpstreamError):
        c.consultar_estatus("ABC1234", "cdmx")


def test_estatus_otro_estado_error_explicito(c) -> None:
    with pytest.raises(UpstreamError):
        c.consultar_estatus("ABC1234", "edomex")


def test_estatus_mock_con_flag(c, monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert c.consultar_estatus("ABC1234", "cdmx")["simulated"] is True


def test_validaciones(c) -> None:
    with pytest.raises(NotFoundError):
        c.consultar_estatus("ABC1234", "xx")
    with pytest.raises(ValidationError):
        c.consultar_estatus("A1", "cdmx")


def test_programas_costos_con_fuente(c) -> None:
    for p in c.listar_programas()["programas"]:
        if p["costo_mxn"] is not None:
            assert p["fuentes"], p["clave"]


def test_tool_devuelve_error_dict() -> None:
    r = verificacion_consultar_estatus(ConsultarInput(placa="ABC1234", estado="edomex"))
    assert r["code"] == "upstream_error"


@pytest.mark.live
def test_live_saf_handoff(c) -> None:
    assert c.consultar_estatus("ABC1234", "cdmx")["portal_verificado"]["status_code"] == 200
