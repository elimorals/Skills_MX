"""Tests mp_sat_ws."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_MCP_ROOT))


# ============================================================
# Validación de dataclass SolicitudDescarga
# ============================================================

class TestSolicitudDescarga:
    def test_solicitud_valida(self):
        from shared.sat_ws import SolicitudDescarga
        sol = SolicitudDescarga(
            rfc_emisor="ABC120101AB1",
            fecha_inicial="2026-01-01T00:00:00",
            fecha_final="2026-01-31T23:59:59",
        )
        sol.validar()  # no raise

    def test_rfc_invalido(self):
        from shared.sat_ws import SolicitudDescarga
        sol = SolicitudDescarga(
            rfc_emisor="invalido",
            fecha_inicial="2026-01-01T00:00:00",
            fecha_final="2026-01-31T23:59:59",
        )
        with pytest.raises(ValueError):
            sol.validar()

    def test_fecha_invalida(self):
        from shared.sat_ws import SolicitudDescarga
        sol = SolicitudDescarga(
            rfc_emisor="ABC120101AB1",
            fecha_inicial="2026-01-01",  # falta T...
            fecha_final="2026-01-31T23:59:59",
        )
        with pytest.raises(ValueError):
            sol.validar()

    def test_rango_invertido(self):
        from shared.sat_ws import SolicitudDescarga
        sol = SolicitudDescarga(
            rfc_emisor="ABC120101AB1",
            fecha_inicial="2026-02-01T00:00:00",
            fecha_final="2026-01-01T00:00:00",
        )
        with pytest.raises(ValueError):
            sol.validar()


class TestEstadoHelpers:
    def test_parsear_estado(self):
        from shared.sat_ws import parsear_estado_solicitud
        assert parsear_estado_solicitud(3) == "TERMINADA"
        assert parsear_estado_solicitud(1) == "ACEPTADA"
        assert parsear_estado_solicitud(99).startswith("DESCONOCIDO")

    def test_estado_es_terminal(self):
        from shared.sat_ws import estado_es_terminal
        assert estado_es_terminal(3) is True
        assert estado_es_terminal(2) is False
        assert estado_es_terminal(1) is False


# ============================================================
# Cliente (mock mode)
# ============================================================

@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.delenv("SAT_EFIRMA_CERT", raising=False)
    monkeypatch.delenv("SAT_EFIRMA_KEY", raising=False)
    monkeypatch.delenv("SAT_EFIRMA_PASSWORD", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestSatWsClient:
    def test_solicitar_descarga_mock(self):
        from mp_sat_ws.client import SatWsClient
        from shared.sat_ws import SolicitudDescarga
        c = SatWsClient()
        r = c.solicitar_descarga(SolicitudDescarga(
            rfc_emisor="ABC120101AB1",
            fecha_inicial="2026-01-01T00:00:00",
            fecha_final="2026-01-31T23:59:59",
        ))
        assert "id_solicitud" in r
        assert r["cod_estatus"] == 5000
        assert r["simulated"] is True

    def test_solicitar_acepta_dict(self):
        from mp_sat_ws.client import SatWsClient
        c = SatWsClient()
        r = c.solicitar_descarga({
            "rfc_emisor": "ABC120101AB1",
            "fecha_inicial": "2026-01-01T00:00:00",
            "fecha_final": "2026-01-31T23:59:59",
        })
        assert r["cod_estatus"] == 5000

    def test_verificar_solicitud_terminada(self):
        from mp_sat_ws.client import SatWsClient
        c = SatWsClient()
        # UUID que termina en char par → TERMINADA en mock
        r = c.verificar_solicitud("11111111-aaaa-bbbb-cccc-000000000002", "ABC120101AB1")
        assert r["cod_estatus_solicitud"] == 3
        assert r["estado_legible"] == "TERMINADA"
        assert r["es_terminal"] is True
        assert len(r["paquetes"]) > 0

    def test_verificar_solicitud_en_proceso(self):
        from mp_sat_ws.client import SatWsClient
        c = SatWsClient()
        r = c.verificar_solicitud("11111111-aaaa-bbbb-cccc-000000000003", "ABC120101AB1")
        assert r["cod_estatus_solicitud"] == 2
        assert r["es_terminal"] is False
        assert r["paquetes"] == []

    def test_descargar_paquete(self):
        from mp_sat_ws.client import SatWsClient
        c = SatWsClient()
        r = c.descargar_paquete("paquete_xyz_01", "ABC120101AB1")
        assert "zip_base64" in r
        assert r["simulated"] is True

    def test_verificar_sin_args_lanza(self):
        from mp_sat_ws.client import SatWsClient
        from shared.errors import ValidationError
        c = SatWsClient()
        with pytest.raises(ValidationError):
            c.verificar_solicitud("", "ABC120101AB1")
        with pytest.raises(ValidationError):
            c.verificar_solicitud("xyz", "")
