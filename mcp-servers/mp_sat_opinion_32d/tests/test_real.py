"""Opinión 32-D: no cachear errores, opinión propia con e.firma, y tests live."""

from __future__ import annotations

import base64
import os

import pytest
import respx

from mp_sat_opinion_32d.client import SatOpinion32DClient
from shared import sat_portal_fiel
from shared.bitacora import Bitacora
from shared.cache import FileCache
from shared.errors import McpError, ValidationError
from shared.sat_opinion_32d import CONSULTA_ENDPOINT, PORTAL_URL

RFC_SAT = "SAT970701NN3"
_ENV_ORIGINAL = {v: os.environ.get(v, "") for v in ["SAT_RFC", "SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY", "SAT_EFIRMA_PASSWORD"]}


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    for v in ["PLUGINS_MX_MOCK", "SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY", "SAT_EFIRMA_PASSWORD"]:
        monkeypatch.delenv(v, raising=False)
    return SatOpinion32DClient(
        cache=FileCache("op32d_test", root=tmp_path / "cache"),
        bitacora=Bitacora("op32d_test", root=tmp_path / "bita"),
    )


@respx.mock
def test_estado_error_no_se_cachea(cliente):
    ruta = respx.post(f"{PORTAL_URL}{CONSULTA_ENDPOINT}").respond(200, content=b"?", headers={"content-type": "image/png"})
    assert cliente.consultar(rfc=RFC_SAT)["estado"] == "error"
    cliente.consultar(rfc=RFC_SAT)
    assert ruta.call_count == 2


@respx.mock
def test_http_500_levanta_error_sin_mock(cliente):
    respx.post(f"{PORTAL_URL}{CONSULTA_ENDPOINT}").respond(500)
    with pytest.raises(McpError):
        cliente.consultar(rfc=RFC_SAT)


def test_propia_sin_efirma_es_mock(cliente):
    r = cliente.descargar_propia(RFC_SAT)
    assert r["simulated"] is True


def test_propia_con_efirma(cliente, tmp_path, monkeypatch):
    pytest.importorskip("cryptography")
    from mp_sat_portal.tests.test_efirma_loader import _gen_efirma_test

    c, k, p = _gen_efirma_test(tmp_path)
    monkeypatch.setenv("SAT_EFIRMA_CERT", str(c))
    monkeypatch.setenv("SAT_EFIRMA_KEY", str(k))
    monkeypatch.setenv("SAT_EFIRMA_PASSWORD", p)

    class Sesion:
        def __init__(self, *a, **kw): ...
        def __enter__(self): return self
        def __exit__(self, *a): ...
        def descargar_opinion_32d(self): return b"%PDF-1.4 32d"

    monkeypatch.setattr(sat_portal_fiel, "SatFielSession", Sesion)
    r = cliente.descargar_propia("EKU9003173C9")
    assert r["simulated"] is False
    assert base64.b64decode(r["pdf_base64"]) == b"%PDF-1.4 32d"
    with pytest.raises(ValidationError):
        cliente.descargar_propia(RFC_SAT)  # e.firma de otro RFC


@pytest.mark.live
def test_live_consulta_publica(cliente):
    r = cliente.consultar(rfc=RFC_SAT, incluir_pdf=False)
    assert r["simulated"] is False
    assert r["estado"] in {"positiva", "negativa", "no_autorizado", "no_inscrito"}


@pytest.mark.live
def test_live_opinion_propia(cliente, monkeypatch):
    if not all(_ENV_ORIGINAL.values()):
        pytest.skip("requiere SAT_RFC y SAT_EFIRMA_*")
    for v, val in _ENV_ORIGINAL.items():
        monkeypatch.setenv(v, val)
    r = cliente.descargar_propia(_ENV_ORIGINAL["SAT_RFC"])
    assert base64.b64decode(r["pdf_base64"]).startswith(b"%PDF")

