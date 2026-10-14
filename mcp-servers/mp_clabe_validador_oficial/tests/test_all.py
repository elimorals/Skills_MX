from pathlib import Path

import pytest
import respx

from mp_banxico_cep import spei
from mp_banxico_cep.clabe import calcular_digito_control_clabe
from mp_clabe_validador_oficial.client import ClabeValidadorClient
from shared.errors import UpstreamError, ValidationError

# Respuesta real de instituciones.do capturada 2026-10-14 (catálogo público SPEI).
FX = Path(__file__).resolve().parents[2] / "mp_banxico_cep/tests/fixtures/instituciones_2026-10-10.json"
INST = f"{spei.BASE_URL}instituciones.do"


def _clabe(base17: str) -> str:
    return base17 + str(calcular_digito_control_clabe(base17))


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "a"))
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    return ClabeValidadorClient()


@respx.mock
def test_clabe_valida_banco_participante(client):
    respx.get(INST).respond(200, content=FX.read_bytes(), headers={"content-type": "application/json"})
    r = client.validar_clabe(_clabe("00218000000000000"))
    assert r["valida"] is True
    assert r["participante_spei"] is True
    assert r["institucion_spei"]["nombre"] == "BANAMEX"
    assert r["simulated"] is False


@respx.mock
def test_clabe_digito_incorrecto(client):
    respx.get(INST).respond(200, content=FX.read_bytes(), headers={"content-type": "application/json"})
    base = "00218000000000000"
    malo = base + str((calcular_digito_control_clabe(base) + 1) % 10)
    r = client.validar_clabe(malo)
    assert r["valida"] is False


@respx.mock
def test_banco_no_participante(client):
    respx.get(INST).respond(200, content=FX.read_bytes(), headers={"content-type": "application/json"})
    r = client.validar_clabe(_clabe("99918000000000000"))
    assert r["valida"] is False
    assert r["participante_spei"] is False


@respx.mock
def test_banxico_caido_upstream_error(client):
    respx.get(INST).respond(500)
    with pytest.raises(UpstreamError):
        client.info_banco_clabe("012")


def test_info_banco_input_invalido(client):
    with pytest.raises(ValidationError):
        client.info_banco_clabe("12")


def test_mock_explicito(client, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert client.info_banco_clabe("012")["simulated"] is True


@pytest.mark.live
def test_live_catalogo_spei(client):
    r = client.info_banco_clabe("012")
    assert r["participante_spei"] is True
    assert "BBVA" in r["institucion_spei"]["nombre"]
