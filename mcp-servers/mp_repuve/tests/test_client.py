"""Tests para mp_repuve."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_MCP_ROOT))


# ============================================================
# Validación de identificadores
# ============================================================

class TestValidarNIV:
    def test_niv_valido(self):
        from shared.repuve import validar_niv
        assert validar_niv("3VWFE21C04M000001") == "3VWFE21C04M000001"

    def test_niv_uppercase_normalize(self):
        from shared.repuve import validar_niv
        assert validar_niv("3vwfe21c04m000001") == "3VWFE21C04M000001"

    def test_niv_strip_spaces_dashes(self):
        from shared.repuve import validar_niv
        assert validar_niv("3VW-FE21C-04M-000001") == "3VWFE21C04M000001"

    def test_niv_corto(self):
        from shared.repuve import validar_niv
        with pytest.raises(ValueError):
            validar_niv("ABC123")

    def test_niv_caracteres_invalidos(self):
        from shared.repuve import validar_niv
        # I, O, Q no se permiten en VIN según ISO 3779
        with pytest.raises(ValueError):
            validar_niv("3VWFE21C04I000001")  # contiene I
        with pytest.raises(ValueError):
            validar_niv("3VWFE21C04O000001")  # contiene O
        with pytest.raises(ValueError):
            validar_niv("3VWFE21C04Q000001")  # contiene Q


class TestValidarPlaca:
    def test_placa_valida(self):
        from shared.repuve import validar_placa
        assert validar_placa("ABC-12-34") == "ABC-12-34"
        assert validar_placa("ABC1234") == "ABC1234"

    def test_placa_normalize_upper(self):
        from shared.repuve import validar_placa
        assert validar_placa("abc-1234") == "ABC-1234"

    def test_placa_vacia(self):
        from shared.repuve import validar_placa
        with pytest.raises(ValueError):
            validar_placa("")

    def test_placa_formato_invalido(self):
        from shared.repuve import validar_placa
        with pytest.raises(ValueError):
            validar_placa("XX")


# ============================================================
# Cliente (mock mode)
# ============================================================

@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.delenv("PLUGINS_MX_REPUVE_LIVE", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestRepuveClient:
    def test_consultar_niv_devuelve_vehiculo(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.consultar_niv("3VWFE21C04M000002")  # ends in 2 → sin robo
        assert r["encontrado"] is True
        assert r["vehiculo"]["niv"] == "3VWFE21C04M000002"
        assert r["vehiculo"]["tiene_reporte_robo"] is False
        assert r["simulated"] is True

    def test_consultar_niv_terminado_en_1_simula_robo(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.consultar_niv("3VWFE21C04M000001")  # ends in 1 → robo
        assert r["vehiculo"]["tiene_reporte_robo"] is True
        assert "ROBO ACTIVO" in r["vehiculo"]["estatus_robo"]

    def test_consultar_placa(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.consultar_placa("XYZ1234")
        assert r["encontrado"] is True
        assert r["vehiculo"]["placa"] == "XYZ1234"

    def test_niv_fake_devuelve_no_encontrado(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        # 17 chars con FAKE en medio
        r = c.consultar_niv("3VWFFAKE0000000001")[:17] if False else c.consultar_niv("FAKEAAA0000000000")
        assert r["encontrado"] is False
        assert r["vehiculo"] is None

    def test_cache_hit_segunda_llamada(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        c.consultar_niv("3VWFE21C04M000002")
        r2 = c.consultar_niv("3VWFE21C04M000002")
        assert r2["encontrado"] is True


class TestVerificarRobado:
    def test_robo_emite_advertencia_critica(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.verificar_robado(niv="3VWFE21C04M000001")  # robado
        assert r["tiene_reporte_robo"] is True
        assert any("ROBO ACTIVO" in adv for adv in r["advertencias"])

    def test_sin_robo_sin_advertencia_critica(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.verificar_robado(niv="3VWFE21C04M000002")
        assert r["tiene_reporte_robo"] is False

    def test_no_encontrado_emite_advertencia(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.verificar_robado(niv="FAKEAAA0000000000")
        assert r["consultado"] is False
        assert any("NO encontrado" in adv for adv in r["advertencias"])

    def test_sin_niv_ni_placa_lanza(self):
        from mp_repuve.client import RepuveClient
        from shared.errors import ValidationError
        c = RepuveClient()
        with pytest.raises(ValidationError):
            c.verificar_robado()
