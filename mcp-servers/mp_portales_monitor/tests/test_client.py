"""Tests mp_portales_monitor."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

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
        monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
        r = self.c.check_http("sat_padron")
        assert r["simulated"] is True
        assert "http_status" in r
        assert "latencia_ms" in r

    def test_clave_invalida_falla(self, monkeypatch):
        monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
        with pytest.raises(ValidationError):
            self.c.check_http("inexistente")

    def test_determinismo_mock(self, monkeypatch):
        monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
        r1 = self.c.check_http("sat_padron")
        r2 = self.c.check_http("sat_padron")
        assert r1["http_status"] == r2["http_status"]
        assert r1["latencia_ms"] == r2["latencia_ms"]


class TestFormRender:
    def setup_method(self):
        self.c = PortalesMonitorClient()

    def test_form_render_mock(self, monkeypatch):
        monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
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
        assert r["estado"] == "activa"
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
