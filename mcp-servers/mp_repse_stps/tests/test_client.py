"""Tests del cliente mp_repse_stps."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
if str(_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(_MCP_ROOT))

from mp_repse_stps.client import RepseStpsClient  # noqa: E402
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.repse_stps import (  # noqa: E402
    normalizar_razon_social,
    parsear_aviso_registro,
    parsear_entidad_municipio,
)


@pytest.fixture
def tmp_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    cache = FileCache("repse_stps_test", root=tmp_path / "cache")
    bit = Bitacora("repse_stps_test", root=tmp_path / "bita")
    return RepseStpsClient(cache=cache, bitacora=bit)


class TestNormalizacion:
    def test_uppercase_y_trim(self):
        assert normalizar_razon_social("  manpower  ") == "MANPOWER"

    def test_quita_puntuacion(self):
        assert normalizar_razon_social("MANPOWER, S.A. DE C.V.") == "MANPOWER S A DE C V"

    def test_strings_vacios(self):
        assert normalizar_razon_social("") == ""
        assert normalizar_razon_social("   ") == ""


class TestParsearAviso:
    def test_formato_estandar(self):
        ar, fecha = parsear_aviso_registro("AR6169 / 2024-06-12")
        assert ar == "AR6169"
        assert fecha == "2024-06-12"

    def test_formato_invalido(self):
        ar, fecha = parsear_aviso_registro("texto cualquiera")
        assert ar is None
        assert fecha is None

    def test_vacio(self):
        ar, fecha = parsear_aviso_registro("")
        assert ar is None
        assert fecha is None


class TestParsearEntidad:
    def test_estandar(self):
        ent, mun = parsear_entidad_municipio("Ciudad de México / Benito Juárez")
        assert ent == "Ciudad de México"
        assert mun == "Benito Juárez"

    def test_solo_entidad(self):
        ent, mun = parsear_entidad_municipio("Jalisco")
        assert ent == "Jalisco"
        assert mun is None


class TestConsultarPorRazonSocial:
    def test_min_chars(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_razon_social("ab")

    def test_limite_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_razon_social("MANPOWER", limite=0)
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_razon_social("MANPOWER", limite=200)

    def test_busqueda_ok(self, tmp_client):
        r = tmp_client.consultar_por_razon_social("MANPOWER")
        assert "encontrados" in r
        assert len(r["encontrados"]) >= 1
        assert r.get("simulated") is True
        assert r["url_consultado"].startswith("https://repse.stps.gob.mx")

    def test_cache_reutilizado(self, tmp_client):
        r1 = tmp_client.consultar_por_razon_social("MANPOWER")
        r2 = tmp_client.consultar_por_razon_social("manpower")  # case-insensitive cache
        assert r1["razon_social_buscada"] == r2["razon_social_buscada"]


class TestConsultarPorNumero:
    def test_numero_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_numero_registro("ABC")
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_numero_registro("12")  # muy corto

    def test_detalle_ok(self, tmp_client):
        r = tmp_client.consultar_por_numero_registro("669356")
        assert r["numero_registro"] == "669356"
        assert "folio" in r
        assert "vigencia" in r
        assert "servicios" in r
        assert len(r["servicios"]) >= 1
        assert r.get("simulated") is True


class TestVerificarProveedor:
    def test_con_numero_registro(self, tmp_client):
        r = tmp_client.verificar_proveedor(
            razon_social="MANPOWER",
            numero_registro="669356",
        )
        assert "puede_contratar_servicios_especializados" in r
        assert "registrado" in r
        assert "vigente" in r
        assert "advertencias" in r

    def test_solo_razon_social(self, tmp_client):
        r = tmp_client.verificar_proveedor(razon_social="MANPOWER")
        assert r["registrado"] is True
        assert "detalle" in r

    def test_vigencia_pasada(self, tmp_client, monkeypatch):
        """Si vigencia es pasada, puede_contratar debe ser False."""
        # Simulamos respuesta con vigencia vencida sobreescribiendo el mock interno
        def mock_detalle(*args, **kwargs):
            return {
                "numero_registro": "999999",
                "folio": "1",
                "razon_social": "VENCIDA SA",
                "vigencia": "2020-01-01",  # pasado
                "servicios": [],
            }
        monkeypatch.setattr(tmp_client, "consultar_por_numero_registro", mock_detalle)
        r = tmp_client.verificar_proveedor(
            razon_social="VENCIDA",
            numero_registro="999999",
        )
        assert r["vigente"] is False
        assert r["puede_contratar_servicios_especializados"] is False
        assert len(r["advertencias"]) >= 1


class TestEsVigente:
    def test_futura_es_vigente(self):
        manana = (date.today() + timedelta(days=1)).isoformat()
        assert RepseStpsClient._es_vigente(manana) is True

    def test_pasada_no_vigente(self):
        ayer = (date.today() - timedelta(days=1)).isoformat()
        assert RepseStpsClient._es_vigente(ayer) is False

    def test_none_no_vigente(self):
        assert RepseStpsClient._es_vigente(None) is False

    def test_invalida_no_vigente(self):
        assert RepseStpsClient._es_vigente("no-es-fecha") is False
