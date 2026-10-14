"""Camino real (httpx) del CEP con respuestas reales capturadas del portal Banxico."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest
import respx

from mp_banxico_cep import spei
from mp_banxico_cep.client import BanxicoCepClient
from shared.errors import UpstreamError

FX = Path(__file__).parent / "fixtures"
BASE = spei.BASE_URL


@pytest.fixture
def real(monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    return BanxicoCepClient()


def _mock_portal(valida_fixture: str) -> respx.MockRouter:
    router = respx.mock(assert_all_called=False)
    router.get(BASE).respond(200, text=(FX / "cep_form_2026-10-14.html").read_text())
    router.get(f"{BASE}instituciones.do").respond(
        200, content=(FX / "instituciones_2026-10-10.json").read_bytes(),
        headers={"content-type": "application/json"},
    )
    router.post(f"{BASE}valida.do").respond(
        200, text=(FX / valida_fixture).read_text(encoding="utf-8")
    )
    return router


def test_mapeo_clabe_a_participante() -> None:
    import json

    cat = [
        {"clave": c, "nombre": n}
        for c, n in json.loads((FX / "instituciones_2026-10-10.json").read_text())["instituciones"]
    ]
    assert spei.clave_participante(cat, "012")["clave"] == "40012"
    assert spei.clave_participante(cat, "002")["nombre"] == "BANAMEX"
    assert spei.clave_participante(cat, "999") is None


def test_captcha_oculto_en_formulario_real() -> None:
    assert spei.captcha_visible((FX / "cep_form_2026-10-14.html").read_text()) is False
    visible = '<div id="captchaInput" class="entrada" style="">'
    assert spei.captcha_visible(visible) is True


@pytest.mark.asyncio
async def test_validar_cep_no_encontrado(real) -> None:
    with _mock_portal("valida_no_encontrada_2026-10-14.html") as router:
        r = await real.validar_cep("MBAN01002610100012345678", date(2026, 10, 10), "012", "014")
        sent = router.calls[-1].request.content.decode()
    assert r["estado"] == "no_encontrado"
    assert r["existe_en_banxico"] is False
    assert r["simulated"] is False
    assert "emisor=40012" in sent and "receptor=40014" in sent and "captcha=c" in sent


@pytest.mark.asyncio
async def test_generar_cep_error_be(real) -> None:
    with _mock_portal("valida_error_BE_2026-10-14.html"):
        r = await real.generar_cep(
            "CUENCA1555093850", date(2026, 10, 10), "646", "002", 0.01,
            cuenta_beneficiaria="002180700845152894",
        )
    assert r["estado"] == "no_encontrado"
    assert r["cep_disponible"] is False


@pytest.mark.asyncio
async def test_captcha_visible_devuelve_handoff(real) -> None:
    with respx.mock() as router:
        router.get(BASE).respond(200, text='<div id="captchaInput" class="entrada">')
        r = await real.validar_cep("MBAN0100X1234567", date(2026, 10, 10), "012", "014")
    assert r["requiere_humano"] is True
    assert r["url"] == BASE
    assert r["campos_prellenados"]["clave_rastreo"] == "MBAN0100X1234567"


@pytest.mark.asyncio
async def test_portal_caido_es_upstream_error(real) -> None:
    with respx.mock() as router:
        router.get(BASE).respond(503)
        with pytest.raises(UpstreamError):
            await real.validar_cep("MBAN0100X1234567", date(2026, 10, 10), "012", "014")


def test_parsear_xml_cep_estructura() -> None:
    # XML sintético con la estructura SPEI_Tercero (sin datos de personas reales).
    xml = (
        b'<SPEI_Tercero FechaOperacion="2026-10-10" Hora="12:00:00" ClaveSPEI="40014" '
        b'numeroCertificado="00001"><Beneficiario BancoReceptor="SANTANDER" Nombre="EMPRESA PRUEBA" '
        b'TipoCuenta="40" Cuenta="014180000000000001" RFC="XAXX010101000" Concepto="PAGO" '
        b'IVA="0.00" MontoPago="100.00"/><Ordenante BancoEmisor="BBVA MEXICO" Nombre="ORDENANTE PRUEBA" '
        b'TipoCuenta="40" Cuenta="012180000000000002" RFC="XAXX010101000"/></SPEI_Tercero>'
    )
    r = spei.parsear_xml_cep(xml)
    assert r["monto"] == 100.0
    assert r["beneficiario"]["cuenta_enmascarada"] == "**** 0001"
    with pytest.raises(UpstreamError):
        spei.parsear_xml_cep(b"<html>no</html")


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_consulta_estado_banxico(real) -> None:
    """Golpea banxico.org.mx/cep con una clave inexistente: debe responder 'no encontrado'."""
    ayer = date.today() - timedelta(days=1)
    r = await real.validar_cep("MBAN01002610100099999999", ayer, "012", "014")
    assert r.get("requiere_humano") or r["estado"] == "no_encontrado"
