"""Tests mp_citas_monitor."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import json

import httpx
import pytest
import respx

from mp_citas_monitor.client import (
    URL_SAT_MENU,
    CitasMonitorClient,
    PORTALES_CITAS,
    TTL_CONSENT_DIAS_MAX,
)
from shared.errors import ValidationError


CURP_DEMO = "MOMM900101HDFRRR05"
MENU = json.loads((Path(__file__).resolve().parent / "fixtures" / "sat_tc_menu.json").read_text())


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


class TestListar:
    def setup_method(self):
        self.c = CitasMonitorClient()

    def test_4_portales(self):
        r = self.c.listar_portales()
        assert r["total_portales"] == 4

    def test_etica_visible(self):
        r = self.c.listar_portales()
        assert r["etica_operacional"]["no_reserva_automatica"] is True
        assert r["etica_operacional"]["throttling_minimo_segundos"] >= 60


class TestConsentToken:
    def setup_method(self):
        self.c = CitasMonitorClient()

    def test_token_sat_efirma_ok(self):
        r = self.c.generar_consent_token(
            CURP_DEMO, "ABC010101AAA", "sat_citas", "firma_electronica_renovacion"
        )
        assert r["consent_token"].startswith("CT-")
        assert r["ttl_dias"] == 30
        assert "curp" not in r  # debe estar hasheado

    def test_portal_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.generar_consent_token(
                CURP_DEMO, None, "portal_falso", "tramite"
            )

    def test_tramite_no_en_portal_falla(self):
        with pytest.raises(ValidationError):
            self.c.generar_consent_token(
                CURP_DEMO, None, "sat_citas", "tramite_no_existe"
            )

    def test_ttl_max_60_dias(self):
        with pytest.raises(ValidationError):
            self.c.generar_consent_token(
                CURP_DEMO, None, "sat_citas", "rfc_inscripcion",
                ttl_dias=TTL_CONSENT_DIAS_MAX + 1,
            )

    def test_curp_no_aparece_en_respuesta(self):
        r = self.c.generar_consent_token(
            CURP_DEMO, None, "ine_modulos", "credencial_reposicion"
        )
        # CURP plaintext NO debe estar en la respuesta
        import json
        body = json.dumps(r)
        assert CURP_DEMO not in body
        assert "titular_curp_hash" in r


class TestAlerta:
    def setup_method(self):
        self.c = CitasMonitorClient()

    def _token(self) -> str:
        return self.c.generar_consent_token(
            CURP_DEMO, None, "sat_citas", "csf_descarga"
        )["consent_token"]

    def test_crear_alerta_whatsapp(self):
        r = self.c.crear_alerta(self._token(), "whatsapp", "+5215512345678")
        assert r["estado"] == "especificacion_no_persistida"
        assert r["auto_reserva"] is False
        assert r["polling_seconds_minimo"] >= 60
        assert r["canal"] == "whatsapp"

    def test_consent_token_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.crear_alerta("XX-abc", "email", "x@y.com")

    def test_canal_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.crear_alerta(self._token(), "telegram", "abc")

    def test_destinatario_hasheado(self):
        r = self.c.crear_alerta(self._token(), "email", "user@example.com")
        assert "user@example.com" not in str(r)
        assert "destinatario_hash" in r

    def test_fechas_invertidas_falla(self):
        with pytest.raises(ValidationError):
            self.c.crear_alerta(
                self._token(), "email", "x@y.com",
                fecha_min="2026-12-01", fecha_max="2026-06-01"
            )


class TestRevisar:
    def setup_method(self):
        self.c = CitasMonitorClient()

    def test_revisar_sat_csf_mock(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
        r = self.c.revisar_cupos("sat_citas", "csf_descarga")
        assert r["simulated"] is True
        assert "tiene_cupos" in r

    @respx.mock
    def test_revisar_sat_real_es_handoff_con_alternativas(self):
        respx.get(URL_SAT_MENU).mock(return_value=httpx.Response(200, json=MENU))
        r = self.c.revisar_cupos("sat_citas", "csf_descarga")
        assert r["tiene_cupos"] is None
        assert r["handoff_humano"] is True
        assert "401" in r["motivo"]
        assert any("Constancia de Situación Fiscal" in a["nombre"] for a in r["alternativas_digitales"])

    def test_revisar_sre_captcha_handoff(self):
        r = self.c.revisar_cupos("sre_mexitel", "pasaporte_ordinario_nuevo")
        assert "Radware" in r["motivo"]
        assert r["tiene_cupos"] is None

    def test_portal_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.revisar_cupos("xx", "tt")


class TestEstadisticas:
    def setup_method(self):
        self.c = CitasMonitorClient()

    def test_auto_reserva_off(self):
        r = self.c.estadisticas_eticas()
        assert r["auto_reserva_habilitada"] is False

    def test_compromiso_pfdc(self):
        r = self.c.estadisticas_eticas()
        assert "PFDC" in r["compromiso"]


@pytest.mark.live
def test_live_alternativas_sat():
    r = CitasMonitorClient().revisar_cupos("sat_citas", "csf_descarga")
    assert len(r["alternativas_digitales"]) > 0
