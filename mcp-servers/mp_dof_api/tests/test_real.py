"""Path real DOF (API SIDOF) con respuestas reales capturadas 2026-10-14."""

import re
from datetime import date, timedelta
from pathlib import Path

import pytest
import respx

from mp_dof_api.client import SIDOF_API, DofApiClient
from shared.errors import NotFoundError, UpstreamError, ValidationError

FX = Path(__file__).parent / "fixtures"
SUMARIO = (FX / "sidof_notas_13-10-2026.json").read_bytes()
NOTA = (FX / "sidof_nota_5800977.json").read_bytes()
VACIO = b'{"messageCode":200,"response":"OK","NotasMatutinas":[],"NotasVespertinas":[],"NotasExtraordinarias":[]}'
JSON = {"content-type": "application/json"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "a"))
    return DofApiClient()


def test_sumario_real(client):
    with respx.mock() as router:
        router.get(f"{SIDOF_API}/13-10-2026").respond(200, content=SUMARIO, headers=JSON)
        r = client.sumario_dia("13/10/2026")
    assert r["simulated"] is False
    assert r["total_notas"] == 10
    n = r["notas"][0]
    assert n["codigo"] == "5800977"
    assert n["dependencia"] == "PRESIDENCIA DE LA REPUBLICA"
    assert n["url_detalle"].endswith("codigo=5800977&fecha=13/10/2026")


def test_detalle_real(client):
    with respx.mock() as router:
        router.get(f"{SIDOF_API}/nota/5800977").respond(200, content=NOTA, headers=JSON)
        r = client.detalle_nota("5800977", "13/10/2026")
    assert r["titulo"].startswith("Decreto por el que se modifica la Tarifa")
    assert "<" not in r["texto_completo"][:200]
    assert r["longitud_texto"] > 1000


def test_detalle_sin_nota(client):
    with respx.mock() as router:
        router.get(f"{SIDOF_API}/nota/1234567").respond(200, json={"messageCode": 200, "Nota": None})
        with pytest.raises(NotFoundError):
            client.detalle_nota("1234567", "13/10/2026")


def test_busqueda_recorre_dias(client):
    with respx.mock() as router:
        router.get(f"{SIDOF_API}/13-10-2026").respond(200, content=SUMARIO, headers=JSON)
        router.get(url__regex=re.escape(SIDOF_API) + r"/\d\d-\d\d-\d{4}$").respond(200, content=VACIO, headers=JSON)
        r = client.buscar_texto("tarifa de la ley", desde="11/10/2026", hasta="13/10/2026")
    assert r["total_resultados"] == 1
    assert r["resultados"][0]["codigo"] == "5800977"


def test_busqueda_rango_maximo(client):
    with pytest.raises(ValidationError):
        client.buscar_texto("decreto", desde="01/01/2026", hasta="13/10/2026")


def test_sidof_caido(client):
    with respx.mock() as router:
        router.get(f"{SIDOF_API}/13-10-2026").respond(500)
        with pytest.raises(UpstreamError):
            client.sumario_dia("13/10/2026")


@pytest.mark.live
def test_live_sumario_reciente(client):
    # El DOF no publica algunos días; busca el último día hábil con notas en la última semana.
    for i in range(1, 8):
        r = client.sumario_dia((date.today() - timedelta(days=i)).strftime("%d/%m/%Y"))
        if r["total_notas"]:
            break
    assert r["total_notas"] > 0
    assert r["simulated"] is False
