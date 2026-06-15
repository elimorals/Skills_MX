"""Tests para mp_impi_marcanet.

Fixtures NDJSON capturadas con Playwright MCP el 2026-06-15 contra
el portal IMPI ViDoc real (búsqueda "TELMEX").
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_MCP_ROOT))


# ---- Fixtures: respuestas NDJSON reales del IMPI ----
# Cada línea es un JSON independiente. Estructura confirmada en discovery.

FIXTURE_NDJSON_TELMEX = """\
{"event":"processing","data":{"expedienteODocumento":"MA/M/1985/3502080","idArea":114,"area":"MARCAS","anio":2025,"isExpediente":"expediente","expediente":"3502080","tipoExpediente":"MARCA","fichaDatos":[{"descripcion":"Num. Expediente","valor":"3502080"},{"descripcion":"Expediente","valor":"3502080"},{"descripcion":"Expediente Interno","valor":"MA/M/1985/3502080"},{"descripcion":"Título o Denominación","valor":"RELLAMADO TELMEX"},{"descripcion":"Fecha","valor":"2025-11-11T14:21:29"},{"descripcion":"Titular","valor":"TELEFONOS DE MEXICO, S.A.B. DE C.V."},{"descripcion":"Nacionalidad (Titular.)","valor":"MEXICO"},{"descripcion":"Estado (Titular.)","valor":"CUAUHTEMOC, CIUDAD DE MEXICO"},{"descripcion":"Tipo Descripción","valor":"DENOMINACION"},{"descripcion":"Clase","valor":"38"}]}}
{"event":"processing","data":{"expedienteODocumento":"MA/M/2020/2199876","idArea":114,"area":"MARCAS","anio":2020,"isExpediente":"expediente","expediente":"2199876","tipoExpediente":"MARCA","fichaDatos":[{"descripcion":"Expediente","valor":"2199876"},{"descripcion":"Título o Denominación","valor":"TELMEX"},{"descripcion":"Titular","valor":"TELEFONOS DE MEXICO, S.A.B. DE C.V."},{"descripcion":"Clase","valor":"9"}]}}
"""

FIXTURE_NDJSON_EMPTY = ""


# ============================================================
# Parsing y normalización (shared/impi_vidoc.py)
# ============================================================

class TestNormalizacionFichaDatos:
    def test_mapea_descripciones_conocidas(self):
        from shared.impi_vidoc import normalizar_ficha_datos
        ficha = [
            {"descripcion": "Título o Denominación", "valor": "RELLAMADO TELMEX"},
            {"descripcion": "Titular", "valor": "TELMEX SA DE CV"},
            {"descripcion": "Clase", "valor": "38"},
        ]
        result = normalizar_ficha_datos(ficha)
        assert result == {
            "denominacion": "RELLAMADO TELMEX",
            "titular": "TELMEX SA DE CV",
            "clase_niza": "38",
        }

    def test_descripciones_desconocidas_caen_a_snake_case(self):
        from shared.impi_vidoc import normalizar_ficha_datos
        ficha = [{"descripcion": "Campo Nuevo Inesperado", "valor": "valor"}]
        result = normalizar_ficha_datos(ficha)
        assert result == {"campo_nuevo_inesperado": "valor"}

    def test_descripciones_con_acentos_y_parentesis(self):
        from shared.impi_vidoc import normalizar_ficha_datos
        ficha = [{"descripcion": "Nacionalidad (Titular.)", "valor": "MEXICO"}]
        result = normalizar_ficha_datos(ficha)
        assert result == {"titular_nacionalidad": "MEXICO"}

    def test_ignora_items_vacios(self):
        from shared.impi_vidoc import normalizar_ficha_datos
        ficha = [
            {"descripcion": "", "valor": "X"},
            {"descripcion": "Clase", "valor": ""},
            {"descripcion": "Clase", "valor": "38"},
        ]
        assert normalizar_ficha_datos(ficha) == {"clase_niza": "38"}

    def test_primer_match_gana_si_descripcion_duplicada(self):
        from shared.impi_vidoc import normalizar_ficha_datos
        ficha = [
            {"descripcion": "Clase", "valor": "38"},
            {"descripcion": "Clase", "valor": "9"},
        ]
        assert normalizar_ficha_datos(ficha) == {"clase_niza": "38"}


class TestParsearNDJSON:
    def test_parse_dos_marcas(self):
        from shared.impi_vidoc import parsear_ndjson_response
        marcas = list(parsear_ndjson_response(FIXTURE_NDJSON_TELMEX))
        assert len(marcas) == 2
        m1, m2 = marcas
        assert m1.expediente == "MA/M/1985/3502080"
        assert m1.denominacion == "RELLAMADO TELMEX"
        assert m1.titular == "TELEFONOS DE MEXICO, S.A.B. DE C.V."
        assert m1.clase_niza == "38"
        assert m2.denominacion == "TELMEX"
        assert m2.clase_niza == "9"

    def test_parse_body_vacio(self):
        from shared.impi_vidoc import parsear_ndjson_response
        assert list(parsear_ndjson_response(FIXTURE_NDJSON_EMPTY)) == []

    def test_tolera_lineas_malformadas(self):
        from shared.impi_vidoc import parsear_ndjson_response
        bad = '{"event":"processing","data":{"expedienteODocumento":"MA/X/1","fichaDatos":[]}}\nINVALID\n{"event":"processing","data":{"expedienteODocumento":"MA/Y/2","fichaDatos":[]}}'
        marcas = list(parsear_ndjson_response(bad))
        assert len(marcas) == 2

    def test_filtra_eventos_no_processing(self):
        from shared.impi_vidoc import parsear_ndjson_response
        body = (
            '{"event":"heartbeat","data":null}\n'
            '{"event":"processing","data":{"expedienteODocumento":"MA/X","fichaDatos":[]}}\n'
        )
        marcas = list(parsear_ndjson_response(body))
        assert len(marcas) == 1


class TestValidarQuery:
    def test_uppercases(self):
        from shared.impi_vidoc import validar_query
        assert validar_query("telmex") == "TELMEX"

    def test_strip(self):
        from shared.impi_vidoc import validar_query
        assert validar_query("  TELMEX  ") == "TELMEX"

    def test_corta(self):
        from shared.impi_vidoc import validar_query
        with pytest.raises(ValueError):
            validar_query("a")

    def test_larga(self):
        from shared.impi_vidoc import validar_query
        with pytest.raises(ValueError):
            validar_query("X" * 201)


# ============================================================
# Cliente (mock mode default)
# ============================================================

@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch, tmp_path):
    """Default mock + tmp dirs por test."""
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.delenv("PLUGINS_MX_IMPI_LIVE", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestImpiMarcanetClient:
    def test_buscar_devuelve_estructura_canonica(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        r = c.buscar(query="TELMEX")
        assert "query" in r
        assert r["query"] == "TELMEX"
        assert "total_encontrados" in r
        assert "devueltos" in r
        assert isinstance(r["resultados"], list)
        assert r["simulated"] is True
        assert r["modo"] == "mock"

    def test_query_corta_da_pocos_resultados(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        r = c.buscar(query="AB")  # 2 chars → 0 resultados en mock
        assert r["devueltos"] == 0

    def test_query_media_da_un_resultado(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        r = c.buscar(query="HOLA")  # 4 chars → 1 resultado en mock
        assert r["devueltos"] == 1

    def test_query_larga_da_tres_resultados(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        r = c.buscar(query="TELMEX")  # >5 chars → 3 en mock
        assert r["devueltos"] == 3

    def test_limite_recorta(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        r = c.buscar(query="TELMEX", limite=1)
        assert r["devueltos"] == 1
        assert r["total_encontrados"] == 3  # padrón completo

    def test_resultados_no_incluyen_raw_por_default(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        r = c.buscar(query="TELMEX")
        for item in r["resultados"]:
            assert "raw_ficha_normalizada" not in item

    def test_incluir_raw_lo_agrega(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        r = c.buscar(query="TELMEX", incluir_raw=True)
        assert all("raw_ficha_normalizada" in item for item in r["resultados"])

    def test_cache_hit(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        r1 = c.buscar(query="TELMEX", limite=2)
        r2 = c.buscar(query="TELMEX", limite=2)
        assert r1["devueltos"] == r2["devueltos"]
        assert r2["modo"] == "cache"

    def test_query_invalida(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        with pytest.raises(ValueError):
            c.buscar(query="x")


class TestVerificarDenominacion:
    def test_sin_coincidencias_exactas_emite_advertencia(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        # 'HOLA' (4 chars) en mock devuelve 1 resultado con denominación='HOLA'
        r = c.verificar_denominacion("HOLA")
        assert r["denominacion"] == "HOLA"
        assert r["tiene_coincidencias"] is True
        assert r["coincidencias_exactas"] >= 1
        assert any("EXACTA" in adv for adv in r["advertencias"])

    def test_estructura_respuesta(self):
        from mp_impi_marcanet.client import ImpiMarcanetClient
        c = ImpiMarcanetClient()
        r = c.verificar_denominacion("MICRO-X-LAB-9000")
        # 16 chars → genera 3 resultados en mock, ninguno exacto a "MICRO-X-LAB-9000"
        assert "tiene_coincidencias" in r
        assert "coincidencias_exactas" in r
        assert "coincidencias_similares" in r
        assert "ejemplos" in r
        assert isinstance(r["advertencias"], list)
        assert len(r["ejemplos"]) <= 5


# ============================================================
# Parsing del flujo real (normaliza NDJSON capturado)
# ============================================================

class TestNormalizarResultadoIntegracion:
    def test_pipeline_completo_ndjson_a_dict(self):
        """Simula respuesta real: NDJSON capturado del IMPI → dict del MCP."""
        from mp_impi_marcanet.client import ImpiMarcanetClient
        # _normalizar_resultado es staticmethod
        r = ImpiMarcanetClient._normalizar_resultado(
            query="TELMEX",
            limite=10,
            ndjson_body=FIXTURE_NDJSON_TELMEX,
            modo="playwright",
        )
        assert r["query"] == "TELMEX"
        assert r["total_encontrados"] == 2
        assert r["devueltos"] == 2
        assert r["modo"] == "playwright"
        assert r["simulated"] is False
        # Primer resultado normalizado correctamente
        m1 = r["resultados"][0]
        assert m1["denominacion"] == "RELLAMADO TELMEX"
        assert m1["clase_niza"] == "38"
        assert m1["titular_nacionalidad"] == "MEXICO"
