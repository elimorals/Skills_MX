"""Tests mp_agua_mx."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
import pytest
import respx

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_agua_mx.client import AguaMxClient, parse_jmas  # noqa: E402
from shared.errors import NotFoundError, UpstreamError, ValidationError  # noqa: E402

JMAS_URL = "https://jmasjuarez.gob.mx/v026/pago.php"
# Estructura real de pago.php (2026-10-14) con datos ficticios.
JMAS_OK = """
<p><strong>Número de Cuenta:</strong> 123</p>
<p><strong>Nombre:</strong> PERSONA FICTICIA</p>
<p><strong>Tarifa:</strong> TARIFA RESIDENCIAL</p>
<p><strong>Estado de Cuenta:</strong> ACTIVO</p>
<p><strong>Período:</strong> Año: 2026 | Mes: 10</p>
<h6>Consumo Anterior</h6>
<h3 class="text-primary">20 m³</h3>
<h6>Saldo Actual</h6>
<h3 class="text-danger">$ 1,030.14</h3>
<h6>Fecha de Vencimiento</h6>
<h3 class="text-warning">29/10/2026</h3>
<h5>Detalle del Cobro</h5>
<table><tr><th>Concepto</th><th>Monto</th></tr>
<tr><td>AGUA POTABLE DOMESTICO</td><td>$1,030.14</td></tr>
<tr><td>TOTAL</td><td>$ 1,030.14</td></tr></table>
"""
JMAS_NF = '<div class="alert alert-danger"><p>No se encontró la cuenta o no existe información disponible.</p></div>'


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))


class TestCatalogo:
    def test_catalogo_no_vacio(self):
        from shared.agua_mx import CATALOGO_AGUA
        assert len(CATALOGO_AGUA) >= 10

    def test_solo_validados_son_consultables(self):
        from shared.agua_mx import listar_organismos
        assert [o.clave for o in listar_organismos(solo_consultables=True)] == ["jmas_juarez"]

    def test_siapa_es_captcha(self):
        from shared.agua_mx import buscar_organismo
        assert buscar_organismo("siapa").metodo == "publica_captcha"

    def test_estadisticas_consistencia(self):
        from shared.agua_mx import estadisticas
        stats = estadisticas()
        assert 0 <= stats["consultables"] <= stats["total_organismos"]


class TestParserJmas:
    def test_extrae_saldo_sin_pii(self):
        r = parse_jmas(JMAS_OK)
        assert r["adeudo_mxn"] == 1030.14
        assert r["vencimiento"] == "29/10/2026"
        assert r["consumo_m3"] == 20.0
        assert r["estado_cuenta"] == "ACTIVO"
        assert r["conceptos"] == [{"concepto": "AGUA POTABLE DOMESTICO", "monto_mxn": 1030.14}]
        assert "FICTICIA" not in str(r)

    def test_no_encontrada(self):
        with pytest.raises(NotFoundError):
            parse_jmas(JMAS_NF)

    def test_estructura_desconocida(self):
        with pytest.raises(UpstreamError):
            parse_jmas("<html>mantenimiento</html>")


class TestConsultarAdeudo:
    @respx.mock
    def test_jmas_real(self):
        route = respx.get(JMAS_URL).mock(return_value=httpx.Response(200, text=JMAS_OK))
        r = AguaMxClient().consultar_adeudo("jmas_juarez", "123456")
        assert route.calls.last.request.url.params["cuenta"] == "123456"
        assert r["simulated"] is False and r["adeudo_mxn"] == 1030.14

    @respx.mock
    def test_jmas_caido(self):
        respx.get(JMAS_URL).mock(return_value=httpx.Response(502))
        with pytest.raises(UpstreamError):
            AguaMxClient().consultar_adeudo("jmas_juarez", "123456")

    def test_siapa_handoff_captcha(self):
        r = AguaMxClient().consultar_adeudo("siapa", "1234567")
        assert r["requiere_humano"] is True and r["motivo"] == "captcha"
        assert r["simulated"] is False

    @respx.mock
    def test_siapa_sigue_en_handoff_con_solver_activo(self, monkeypatch):
        # El form de SIAPA es el inicio del pago (Santander), no una consulta: no se conecta.
        monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
        monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
        r = AguaMxClient().consultar_adeudo("siapa", "12345678")
        assert r["requiere_humano"] is True and r["motivo"] == "captcha"
        assert not respx.calls  # ni 2captcha ni el portal

    def test_no_implementado_es_error_explicito(self):
        with pytest.raises(UpstreamError) as exc:
            AguaMxClient().consultar_adeudo("sacmex", "12345678901")
        assert exc.value.details["implementado"] is False

    def test_organismo_inexistente(self):
        with pytest.raises(NotFoundError):
            AguaMxClient().consultar_adeudo("inexistente", "12345678")

    def test_cuenta_formato_invalido(self):
        with pytest.raises(ValidationError):
            AguaMxClient().consultar_adeudo("sacmex", "X")

    def test_mock_solo_con_flag(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
        r = AguaMxClient().consultar_adeudo("sacmex", "12345678902")
        assert r["simulated"] is True and r["estatus"] == "AL DIA"

    def test_sin_token_recaptcha_por_env(self):
        import mp_agua_mx.client as c
        assert "RECAPTCHA_TOKEN" not in Path(c.__file__).read_text()


class TestServerTools:
    def test_listar(self):
        r = AguaMxClient().listar_organismos()
        assert r["total"] == len(r["organismos"])

    def test_buscar_por_estado_jal(self):
        r = AguaMxClient().buscar_por_estado("JAL")
        assert any(o["clave"] == "siapa" for o in r["organismos"])


@pytest.mark.live
def test_live_jmas_cuenta_inexistente():
    with pytest.raises(NotFoundError):
        AguaMxClient().consultar_adeudo("jmas_juarez", "999999999999")


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("JMAS_CUENTA"), reason="exporta JMAS_CUENTA (cuenta propia)")
def test_live_jmas_cuenta_real():
    r = AguaMxClient().consultar_adeudo("jmas_juarez", os.environ["JMAS_CUENTA"])
    assert r["simulated"] is False and r["adeudo_mxn"] >= 0


@pytest.mark.live
def test_live_siapa_sigue_con_recaptcha():
    from shared.agua_mx import URL_SIAPA_CONSULTA
    # siapa.gob.mx sirve una cadena TLS incompleta (2026-10-14); solo leemos si hay captcha.
    assert "recaptcha" in httpx.get(URL_SIAPA_CONSULTA, timeout=30, verify=False).text.lower()
