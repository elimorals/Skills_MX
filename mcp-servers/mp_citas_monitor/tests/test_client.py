"""Tests mp_citas_monitor."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

from mp_citas_monitor.client import (
    CitasMonitorClient,
    PORTALES_CITAS,
    TTL_CONSENT_DIAS_MAX,
)
from shared.errors import ValidationError


CURP_DEMO = "MOMM900101HDFRRR05"


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
        assert r["estado"] == "activa"
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
        monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
        r = self.c.revisar_cupos("sat_citas", "csf_descarga")
        assert r["simulated"] is True
        assert "tiene_cupos" in r

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
