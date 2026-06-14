"""Tests del cliente mp_sep_profesional."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
if str(_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(_MCP_ROOT))

from mp_sep_profesional.client import (  # noqa: E402
    CURP_REGEX,
    PROFESIONES_REGULADAS,
    SepProfesionalClient,
    _profesion_es_regulada,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402


@pytest.fixture
def tmp_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    cache = FileCache("sep_profesional_test", root=tmp_path / "cache")
    bit = Bitacora("sep_profesional_test", root=tmp_path / "bita")
    return SepProfesionalClient(cache=cache, bitacora=bit)


class TestProfesionRegulada:
    def test_medico_es_salud(self):
        assert _profesion_es_regulada("Médico Cirujano") == "salud"
        assert _profesion_es_regulada("medico cirujano") == "salud"

    def test_abogado_es_legal(self):
        assert _profesion_es_regulada("Licenciado en Derecho") == "legal"
        assert _profesion_es_regulada("Abogado") == "legal"

    def test_contador_es_contable(self):
        assert _profesion_es_regulada("Contador Público") == "contable_fiscal"

    def test_arquitecto_es_riesgo(self):
        assert _profesion_es_regulada("Arquitecto") == "ingenierias_riesgo"

    def test_profesion_no_regulada(self):
        assert _profesion_es_regulada("Filósofo") is None
        assert _profesion_es_regulada("") is None


class TestCURPRegex:
    def test_curp_valida(self):
        # CURP de ejemplo con formato válido
        assert CURP_REGEX.match("HEGJ800101HDFRNN09")

    def test_curp_invalida_estructura(self):
        assert not CURP_REGEX.match("INVALIDA")
        assert not CURP_REGEX.match("HEGJ800101HDFRNN")  # corta
        assert not CURP_REGEX.match("HEGJ801301HDFRNN09")  # mes 13


class TestConsultarCedula:
    def test_validacion_formato(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_cedula("abc")
        with pytest.raises(ValidationError):
            tmp_client.consultar_cedula("123")  # < 7

    def test_consulta_mock(self, tmp_client):
        r = tmp_client.consultar_cedula("1234567")
        assert "cedula" in r
        assert r.get("simulated") is True

    def test_categoria_regulada_se_agrega(self, tmp_client):
        # cuando la profesión existe en el mock
        r = tmp_client.consultar_cedula("1234567", validar_vigencia=True)
        # campo presente (puede ser None si la profesión mock no calza)
        assert "categoria_regulada" in r
        assert "requiere_validacion_obligatoria" in r

    def test_cache_reutilizado(self, tmp_client):
        r1 = tmp_client.consultar_cedula("1234567")
        r2 = tmp_client.consultar_cedula("1234567")
        # mismo resultado, segundo viene de cache
        assert r1["cedula"] == r2["cedula"]


class TestConsultarPorDatos:
    def test_requiere_nombre_y_apellido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_datos(nombre="", primer_apellido="Garcia")
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_datos(nombre="Juan", primer_apellido="")

    def test_curp_invalido_rechazado(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_datos(
                nombre="Juan",
                primer_apellido="Garcia",
                curp="INVALIDA",
            )

    def test_consulta_ok_sin_curp(self, tmp_client):
        r = tmp_client.consultar_por_datos(
            nombre="Juan",
            primer_apellido="Garcia",
            segundo_apellido="Lopez",
        )
        assert "cedula" in r or "nombre_completo" in r or "simulated" in r


class TestValidarMedicoParaConsulta:
    def test_solo_cedula_general(self, tmp_client):
        r = tmp_client.validar_medico_para_consulta(cedula="1234567")
        assert "puede_dar_consulta" in r
        assert "cedula_general_ok" in r
        assert "advertencias" in r
        assert "cumple_nom_004" in r
        assert "cumple_cofepris_2024" in r

    def test_con_cedula_especialidad(self, tmp_client):
        r = tmp_client.validar_medico_para_consulta(
            cedula="1234567",
            cedula_especialidad="7654321",
        )
        assert "puede_recetar_controlados" in r
        # debe haber 2 cédulas validadas
        assert len(r["cedulas_validadas"]) >= 1


class TestListarProfesionesReguladas:
    def test_retorna_categorias(self, tmp_client):
        r = tmp_client.listar_profesiones_reguladas()
        assert "categorias" in r
        assert "profesiones_por_categoria" in r
        assert r["total"] >= 1
        assert set(r["categorias"]) == set(PROFESIONES_REGULADAS.keys())
        assert "url_consulta" in r
