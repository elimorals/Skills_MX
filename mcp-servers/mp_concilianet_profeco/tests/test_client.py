"""Tests mp_concilianet_profeco — respx + fixtures reales (PDF Concilianet, JSON Buró)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import pytest
import respx

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_concilianet_profeco.client import (  # noqa: E402
    PDFS_CONVENIO,
    URL_BURO,
    ConcilianetClient,
    parse_buro_proveedores,
)
from shared.errors import UpstreamError, ValidationError  # noqa: E402

FX = _HERE / "fixtures"
PDF_TELECOM = (FX / "concilianet_telecom.pdf").read_bytes()
BURO_PROV = json.loads((FX / "buro_proveedores_volaris.json").read_text())
BURO_QUEJAS = json.loads((FX / "buro_quejas_volaris_2019.json").read_text())


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_parse_buro_real():
    p = parse_buro_proveedores(BURO_PROV)[0]
    assert p["razon_social"] == "CONCESIONARIA VUELA COMPAÑIA DE AVIACION, SAPI DE CV"
    assert p["nombre_comercial"] == "VOLARIS"
    assert p["total_quejas"] == 2839
    assert p["token_buro"] == "23075bdbfae4fe7016374b308ea523df"


@respx.mock
def test_consultar_proveedor_real():
    pytest.importorskip("pypdf")
    for url in PDFS_CONVENIO.values():
        respx.get(url).mock(return_value=httpx.Response(200, content=PDF_TELECOM))
    respx.get(URL_BURO + "proveedores").mock(return_value=httpx.Response(200, json=BURO_PROV))
    c = ConcilianetClient()
    r = c.consultar_proveedor("Radiomóvil Dipsa")
    assert r["simulated"] is False
    assert r["tiene_convenio_concilianet"] is True
    assert r["buro_comercial"]["total"] == 4
    r2 = c.consultar_proveedor("Concesionaria Vuela")
    assert r2["tiene_convenio_concilianet"] is False
    assert "No aparece" in r2["nota_convenio"]


@respx.mock
def test_buro_quejas_real():
    respx.get(URL_BURO + "proveedores").mock(return_value=httpx.Response(200, json=BURO_PROV))

    def consulta(request):
        t = request.url.params["type"]
        if t == "anio":
            return httpx.Response(200, json={"anios": [2026, 2019]})
        if t == "edo":
            return httpx.Response(200, json={"motivos": ["Retraso de vuelo"], "ua": []})
        return httpx.Response(200, json=BURO_QUEJAS)

    respx.get(URL_BURO + "consulta").mock(side_effect=consulta)
    r = ConcilianetClient().buro_quejas("volaris", 2019)
    assert r["nacional"]["quejas_recibidas"] == 237
    assert r["nacional"]["conciliada"] == 139
    assert r["principales_motivos"] == ["Retraso de vuelo"]


@respx.mock
def test_buro_caido_es_error():
    respx.get(URL_BURO + "proveedores").mock(return_value=httpx.Response(500, text="<html>Error 500</html>"))
    with pytest.raises(UpstreamError):
        ConcilianetClient().buro_quejas("volaris")


def test_estatus_caso_handoff():
    r = ConcilianetClient().estatus_caso("PROF-123456")
    assert r["handoff_humano"] is True
    assert r["fase_actual"] is None


def test_registrar_queja_nunca_registra():
    r = ConcilianetClient().registrar_queja(None, "Volaris", "Me cancelaron el vuelo sin reembolso alguno")
    assert r["registrada"] is False
    assert "folio_queja" not in r
    with pytest.raises(ValidationError):
        ConcilianetClient().registrar_queja(None, "Volaris", "corta")


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert ConcilianetClient().consultar_proveedor("Telcel")["simulated"] is True


@pytest.mark.live
def test_live_consultar_y_buro():
    pytest.importorskip("pypdf")
    c = ConcilianetClient()
    r = c.consultar_proveedor("Radiomovil Dipsa")
    assert r["tiene_convenio_concilianet"] is True
    q = c.buro_quejas("volaris")
    assert q["encontrado"] is True
    assert q["nacional"]["quejas_recibidas"] is not None
