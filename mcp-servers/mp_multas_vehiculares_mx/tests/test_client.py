"""Tests mp_multas_vehiculares_mx."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import respx

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    yield


class TestCatalogo:
    def test_catalogo_4_sistemas(self):
        from shared.multas_vehiculares_mx import CATALOGO_MULTAS
        assert len(CATALOGO_MULTAS) == 5
        claves = {s.clave for s in CATALOGO_MULTAS}
        assert claves == {"cdmx", "edomex", "nl", "nl_sanpedro", "jal"}

    def test_cobertura_total_22M(self):
        from shared.multas_vehiculares_mx import CATALOGO_MULTAS
        total = sum(s.cobertura_vehiculos for s in CATALOGO_MULTAS)
        assert total > 20_000_000


class TestConsultaMock:
    def test_consultar_cdmx_mock(self):
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        c = MultasVehicularesMxClient()
        r = c.consultar_por_placa("cdmx", "ABC1235")
        assert r["simulated"] is True
        assert r["estado"] == "cdmx"
        assert "multas" in r

    def test_consultar_edomex_mock(self):
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        c = MultasVehicularesMxClient()
        r = c.consultar_por_placa("edomex", "XYZ9876")
        assert r["simulated"] is True
        assert r["estado"] == "edomex"

    def test_placa_corta_lanza(self):
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        from shared.errors import ValidationError
        c = MultasVehicularesMxClient()
        with pytest.raises(ValidationError):
            c.consultar_por_placa("cdmx", "AB1")

    def test_estado_invalido(self):
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        from shared.errors import NotFoundError
        c = MultasVehicularesMxClient()
        with pytest.raises(NotFoundError):
            c.consultar_por_placa("xxx", "ABC1234")


class TestCalculoTotal:
    def test_calcular_total_estructura(self):
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        c = MultasVehicularesMxClient()
        r = c.calcular_total("jal", "ABC1239")  # último dígito 9 → 1 multa
        assert "monto_bruto_mxn" in r
        assert "monto_neto_pagable_mxn" in r
        assert "ahorro_descuentos_mxn" in r
        assert "desglose_descuentos" in r

    def test_descuento_50_pago_oportuno(self):
        """Multa con días <= 15 debe tener 50% descuento."""
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        c = MultasVehicularesMxClient()
        r = c.calcular_total("cdmx", "ABC1231")  # mock genera 1 multa con dias=10 (≤15)
        if r["monto_bruto_mxn"] > 0:
            assert r["desglose_descuentos"]["50pct_pagar_15d_mxn"] > 0


class TestListar:
    def test_listar_devuelve_5(self):
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        c = MultasVehicularesMxClient()
        r = c.listar_sistemas()
        assert r["total"] == 5
        assert len(r["sistemas"]) == 5

    def test_san_pedro_descubierto(self):
        """NL San Pedro Garza García descubierto en sesión calibración 2026-06-15."""
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        c = MultasVehicularesMxClient()
        r = c.listar_sistemas()
        spgg = next((s for s in r["sistemas"] if s["clave"] == "nl_sanpedro"), None)
        assert spgg is not None
        assert spgg["captcha_tipo"] == "recaptcha_v2"

    def test_metadata_captcha_documentado(self):
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        c = MultasVehicularesMxClient()
        r = c.listar_sistemas()
        jal = next(s for s in r["sistemas"] if s["clave"] == "jal")
        assert jal["captcha_tipo"] == "recaptcha_v2"
        edomex = next(s for s in r["sistemas"] if s["clave"] == "edomex")
        assert edomex["captcha_tipo"] == "turnstile"


class TestReal:
    """Sin PLUGINS_MX_MOCK: GET real (respx) + handoff humano, nunca mock."""

    @pytest.mark.parametrize("estado", ["cdmx", "edomex", "nl", "nl_sanpedro", "jal"])
    @respx.mock
    def test_handoff_por_estado(self, monkeypatch, estado):
        from mp_multas_vehiculares_mx.client import PORTALES, MultasVehicularesMxClient
        monkeypatch.delenv("PLUGINS_MX_MOCK")
        portal = PORTALES[estado]
        html = {"imagen": 'id="captcha_code"', "turnstile": "challenges.cloudflare.com/turnstile",
                "recaptcha_v2": "g-recaptcha"}.get(portal.captcha_tipo, "Instituto de Control Vehicular")
        respx.get(portal.url).respond(200, text=html)
        r = MultasVehicularesMxClient().consultar_por_placa(estado, "ABC-1234")
        assert r["simulated"] is False
        assert r["status"] == "requiere_humano"
        assert r["url_consulta_manual"] == portal.url

    @respx.mock
    def test_portal_caido_es_error(self, monkeypatch):
        from mp_multas_vehiculares_mx.server import ConsultaInput, multas_calcular_total
        from shared.portal_handoff import JALISCO_ADEUDOS
        monkeypatch.delenv("PLUGINS_MX_MOCK")
        respx.get(JALISCO_ADEUDOS.url).respond(503)
        r = multas_calcular_total(ConsultaInput(estado="jal", placa="ABC1234"))
        assert r["code"] == "upstream_error"

    @pytest.mark.live
    def test_live_handoffs(self, monkeypatch):
        import time
        from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
        monkeypatch.delenv("PLUGINS_MX_MOCK")
        c = MultasVehicularesMxClient()
        for i, estado in enumerate(["cdmx", "edomex", "nl", "nl_sanpedro", "jal"]):
            if i:
                time.sleep(5)
            assert c.consultar_por_placa(estado, "ABC1234")["portal_verificado"]["status_code"] == 200
