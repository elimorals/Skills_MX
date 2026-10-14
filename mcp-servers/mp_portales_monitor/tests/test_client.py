"""Tests mp_portales_monitor."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import httpx
import pytest
import respx

from mp_portales_monitor.client import (
    PORTALES_CATALOGO,
    PortalesMonitorClient,
)
from shared.errors import ValidationError


class TestListar:
    def setup_method(self):
        self.c = PortalesMonitorClient()

    def test_listar_todos(self):
        r = self.c.listar_portales()
        assert r["total"] == len(PORTALES_CATALOGO)

    def test_filtrar_federal_fiscal(self):
        r = self.c.listar_portales(categoria="federal_fiscal")
        for p in r["portales"]:
            assert p["categoria"] == "federal_fiscal"

    def test_categoria_estatal_cdmx_existe(self):
        r = self.c.listar_portales(categoria="estatal_cdmx")
        assert r["total"] >= 1


class TestCheckHttp:
    def setup_method(self):
        self.c = PortalesMonitorClient(bitacora=None)

    def test_check_sat_padron_mock(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
        r = self.c.check_http("sat_padron")
        assert r["simulated"] is True
        assert "http_status" in r
        assert "latencia_ms" in r

    def test_clave_invalida_falla(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
        with pytest.raises(ValidationError):
            self.c.check_http("inexistente")

    def test_determinismo_mock(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
        r1 = self.c.check_http("sat_padron")
        r2 = self.c.check_http("sat_padron")
        assert r1["http_status"] == r2["http_status"]
        assert r1["latencia_ms"] == r2["latencia_ms"]


class TestFormRender:
    def setup_method(self):
        self.c = PortalesMonitorClient()

    def test_form_render_mock(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
        r = self.c.check_form_render("sat_padron", "#txtRFC")
        assert "encontrado" in r
        assert r["simulated"] is True

    def test_clave_invalida_falla(self):
        with pytest.raises(ValidationError):
            self.c.check_form_render("xxx", "#sel")


class TestDashboard:
    def setup_method(self):
        self.c = PortalesMonitorClient()

    def test_dashboard_suma_total(self):
        r = self.c.health_dashboard()
        assert r["total_portales_monitoreados"] == len(PORTALES_CATALOGO)
        assert r["criticidad_alta"] + r["criticidad_media"] <= len(PORTALES_CATALOGO)

    def test_canales_alerta_completos(self):
        r = self.c.health_dashboard()
        for c in ("whatsapp", "email", "slack"):
            assert c in r["alerta_canales_soportados"]


class TestAlerta:
    def setup_method(self):
        self.c = PortalesMonitorClient()

    def test_configurar_alerta_whatsapp(self):
        r = self.c.configurar_alerta(
            "sat_padron", "whatsapp", "+5215512345678"
        )
        assert r["estado"] == "especificacion_no_persistida"
        assert r["persistida"] is False
        assert "alerta_id" not in r
        assert r["canal"] == "whatsapp"
        # destinatario hasheado
        assert "+52" not in r["destinatario_hash"]

    def test_canal_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.configurar_alerta("sat_padron", "telegram", "abc")

    def test_umbral_custom_aplica(self):
        r = self.c.configurar_alerta(
            "sat_padron", "email", "ops@example.com", umbral_latencia_ms=2000
        )
        assert r["umbral_latencia_ms"] == 2000


class TestCheckHttpReal:
    """Path real (PLUGINS_MX_MOCK=0) con respx; el live va aparte."""

    def setup_method(self):
        self.c = PortalesMonitorClient()

    @respx.mock
    def test_portal_vivo(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
        url = next(p["url"] for p in PORTALES_CATALOGO if p["clave"] == "dof")
        respx.get(url).mock(return_value=httpx.Response(200, text="<html>DOF</html>"))
        r = self.c.check_http("dof")
        assert r["simulated"] is False
        assert r["http_status"] == 200
        assert r["vivo"] is True
        assert "bloqueado_por_waf" not in r

    @respx.mock
    def test_akamai_no_es_caida(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
        url = next(p["url"] for p in PORTALES_CATALOGO if p["clave"] == "conamer_catalogo")
        # Cuerpo real devuelto por catalogonacional.gob.mx a clientes no-navegador (2026-10-14)
        body = ("<HTML><HEAD><TITLE>Access Denied</TITLE></HEAD><BODY><H1>Access Denied</H1>"
                "Reference&#32;&#35;18&#46;4e66cd17<P>https&#58;&#47;&#47;errors&#46;edgesuite&#46;net"
                "</BODY></HTML>")
        respx.get(url).mock(return_value=httpx.Response(403, text=body))
        r = self.c.check_http("conamer_catalogo")
        assert r["bloqueado_por_waf"] == "akamai"
        assert r["vivo"] is None

    @respx.mock
    def test_error_de_red_es_dato(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
        url = next(p["url"] for p in PORTALES_CATALOGO if p["clave"] == "dof")
        respx.get(url).mock(side_effect=httpx.ConnectError("boom"))
        r = self.c.check_http("dof")
        assert r["vivo"] is False
        assert r["error_tipo"] == "ConnectError"
        assert r["simulated"] is False


@pytest.mark.live
def test_live_check_http_gobmx(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    r = PortalesMonitorClient().check_http("gobmx")
    assert r["simulated"] is False
    assert r["http_status"] == 200
