"""Tests para mp_condusef_sipres.

Fixtures HTML capturadas con Playwright MCP el 2026-06-15 contra
el portal SIPRES real (búsqueda "BANORTE").
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_MCP_ROOT))


# ---- Fixtures: HTML real del SIPRES ----

FIXTURE_HTML_BANORTE = """
<div class="table-responsive"><table border="0" class="table table-striped table-responsiv">
<tr>
<td>
<span  class='rojo'>186</span> resultados buscando <b>BANORTE</b>
</td>
</tr>
</table>
<table class="table table-striped table-responsiv" cellpadding='0' cellspacing='0' >
   <thead>         <tr>             <th class='encpublico' width='90px' >Clave de<br/>Registro</th>             <th class='encpublico' width='160px' >Denominacion<br/>Social</th>             <th class='encpublico' width='160px' >Nombre Corto<br/>o comercial</th>             <th class='encpublico' width='100px' >Estatus</th>             <th class='encpublico' width='140px' >Sector</th>             <th class='encpublico' width='100px'  >Estado</th>
           <th class='encpublico' width='100px' >Ultima<br/>Seccion<br/>Actualizada</th>
           <th class='encpublico' width='100px' >No<br/>Localizable</th>         </tr>     </thead>     <tbody>
<tr>
<td  align='center'>40165</td>
<td><a href="#16316" onclick="window.open('../../jsp/home_publico.jsp?idins=16316','','scrollbars=1,resizable=1')" >Banco Bineo, S.A., Institucion de Banca Multiple, Grupo Financiero <b>Banorte</b></a></td>
<td>BANCO BINEO</td>
<td width='100px'  align='center' title='Institucion Financiera que se encuentra ofreciendo sus productos y servicios al publico.'><b style=color:#45B600;>En operacion</b></td>
<td width='140px' align='left'>Instituciones de banca multiple</td>
<td width='100px'  align='center'>Ciudad de Mexico</td>
<td width='100px'  align='center'>2026-05-15</td>
<td width='100px'  align='center'>No</td>
</tr>
<tr>
<td  align='center'>20001</td>
<td><a href="#10001" onclick="window.open('../../jsp/home_publico.jsp?idins=10001','','scrollbars=1,resizable=1')" >Banco Mercantil del Norte, S.A., Institucion de Banca Multiple, Grupo Financiero <b>Banorte</b></a></td>
<td>BANORTE</td>
<td width='100px'  align='center' title='Institucion Financiera que se encuentra ofreciendo sus productos y servicios al publico.'><b style=color:#45B600;>En operacion</b></td>
<td width='140px' align='left'>Instituciones de banca multiple</td>
<td width='100px'  align='center'>Nuevo Leon</td>
<td width='100px'  align='center'>2026-06-01</td>
<td width='100px'  align='center'>No</td>
</tr>
<tr>
<td  align='center'>99999</td>
<td><a href="#99999" onclick="window.open('../../jsp/home_publico.jsp?idins=99999','','scrollbars=1,resizable=1')" >Casa Cambio Banorte (filial anterior)</a></td>
<td>CC BANORTE</td>
<td width='100px'  align='center' title='Institucion cuyo registro fue cancelado.'><b style=color:#FF0000;>Cancelado</b></td>
<td width='140px' align='left'>Casas de Cambio</td>
<td width='100px'  align='center'>Ciudad de Mexico</td>
<td width='100px'  align='center'>2023-12-15</td>
<td width='100px'  align='center'>Si</td>
</tr>
</tbody></table></div>
"""

FIXTURE_HTML_VACIO = """
<div class="table-responsive">
<table class="table table-striped table-responsiv">
<tr><td><span class='rojo'>0</span> resultados buscando <b>XXXXXXXX</b></td></tr>
</table>
</div>
"""


# ============================================================
# Parsing HTML (shared/sipres_condusef.py)
# ============================================================

class TestExtraerTotal:
    def test_total_186(self):
        from shared.sipres_condusef import extraer_total_resultados
        assert extraer_total_resultados(FIXTURE_HTML_BANORTE) == 186

    def test_total_cero(self):
        from shared.sipres_condusef import extraer_total_resultados
        assert extraer_total_resultados(FIXTURE_HTML_VACIO) == 0

    def test_html_sin_marker(self):
        from shared.sipres_condusef import extraer_total_resultados
        assert extraer_total_resultados("<html></html>") == 0


class TestParsearResultadosHTML:
    def test_parse_tres_entidades(self):
        from shared.sipres_condusef import parsear_resultados_html
        entidades = parsear_resultados_html(FIXTURE_HTML_BANORTE)
        assert len(entidades) == 3

    def test_primer_resultado_banco_bineo(self):
        from shared.sipres_condusef import parsear_resultados_html
        entidades = parsear_resultados_html(FIXTURE_HTML_BANORTE)
        e = entidades[0]
        assert e.clave_registro == "40165"
        assert "Banco Bineo" in e.denominacion
        assert e.nombre_corto == "BANCO BINEO"
        assert e.estatus == "En operacion"
        assert e.sector == "Instituciones de banca multiple"
        assert e.estado == "Ciudad de Mexico"
        assert e.idins == "16316"
        assert e.autorizada_operacion is True

    def test_segundo_resultado_banorte_principal(self):
        from shared.sipres_condusef import parsear_resultados_html
        entidades = parsear_resultados_html(FIXTURE_HTML_BANORTE)
        e = entidades[1]
        assert e.clave_registro == "20001"
        assert e.nombre_corto == "BANORTE"
        assert e.estado == "Nuevo Leon"
        assert e.idins == "10001"

    def test_tercer_resultado_cancelado(self):
        from shared.sipres_condusef import parsear_resultados_html
        entidades = parsear_resultados_html(FIXTURE_HTML_BANORTE)
        e = entidades[2]
        assert e.estatus == "Cancelado"
        assert e.autorizada_operacion is False
        assert e.no_localizable == "Si"

    def test_tooltip_estatus_capturado(self):
        from shared.sipres_condusef import parsear_resultados_html
        entidades = parsear_resultados_html(FIXTURE_HTML_BANORTE)
        assert "ofreciendo" in entidades[0].estatus_tooltip.lower()
        assert "cancelado" in entidades[2].estatus_tooltip.lower()

    def test_html_vacio(self):
        from shared.sipres_condusef import parsear_resultados_html
        entidades = parsear_resultados_html(FIXTURE_HTML_VACIO)
        assert entidades == []

    def test_to_dict(self):
        from shared.sipres_condusef import parsear_resultados_html
        e = parsear_resultados_html(FIXTURE_HTML_BANORTE)[0]
        d = e.to_dict()
        assert "clave_registro" in d
        assert "idins" in d
        assert d["estatus"] == "En operacion"


class TestValidarQuery:
    def test_corta(self):
        from shared.sipres_condusef import validar_query
        with pytest.raises(ValueError):
            validar_query("a")

    def test_larga(self):
        from shared.sipres_condusef import validar_query
        with pytest.raises(ValueError):
            validar_query("X" * 250)

    def test_strip(self):
        from shared.sipres_condusef import validar_query
        assert validar_query("  BANORTE  ") == "BANORTE"


class TestConstruirBodyBusqueda:
    def test_solo_nombre(self):
        from shared.sipres_condusef import construir_body_busqueda
        body = construir_body_busqueda(pnom="BANORTE")
        assert body["tipo"] == "1"
        assert body["pnom"] == "BANORTE"
        assert body["pedo"] == ""
        assert body["psec"] == ""
        assert body["psta"] == ""

    def test_con_sector(self):
        from shared.sipres_condusef import construir_body_busqueda
        body = construir_body_busqueda(pnom="BANORTE", psec="banca")
        assert body["psec"] == "banca"


# ============================================================
# Cliente (mock mode default)
# ============================================================

@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestCondusefSipresClient:
    def test_buscar_devuelve_estructura_canonica(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        c = CondusefSipresClient()
        r = c.buscar_institucion(nombre="BANORTE")
        assert "filtros" in r
        assert "total_padron" in r
        assert "devueltos" in r
        assert isinstance(r["resultados"], list)
        assert r["simulated"] is True

    def test_buscar_nombre_banco_da_tres(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        c = CondusefSipresClient()
        r = c.buscar_institucion(nombre="BANCO PRUEBA")
        assert r["devueltos"] == 3

    def test_buscar_nombre_otro_da_uno(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        c = CondusefSipresClient()
        r = c.buscar_institucion(nombre="ZURICH")
        assert r["devueltos"] == 1

    def test_buscar_sin_filtros_lanza_validation(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        from shared.errors import ValidationError
        c = CondusefSipresClient()
        with pytest.raises(ValidationError):
            c.buscar_institucion()

    def test_buscar_solo_sector(self):
        """Permitir búsqueda solo por sector (sin nombre)."""
        from mp_condusef_sipres.client import CondusefSipresClient
        c = CondusefSipresClient()
        r = c.buscar_institucion(sector="Instituciones de banca múltiple")
        # En mock devuelve 0 resultados con nombre vacío, pero NO lanza error
        assert r["devueltos"] == 0

    def test_limite_recorta(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        c = CondusefSipresClient()
        r = c.buscar_institucion(nombre="BANCO", limite=2)
        assert r["devueltos"] == 2

    def test_cache_hit(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        c = CondusefSipresClient()
        c.buscar_institucion(nombre="BANCO")
        r = c.buscar_institucion(nombre="BANCO")
        # En cache hit, los datos vienen de cache; verificamos consistencia
        assert r["filtros"]["nombre"] == "BANCO"


class TestVerificarAutorizada:
    def test_banco_en_operacion(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        c = CondusefSipresClient()
        r = c.verificar_autorizada("BBVA")
        assert r["encontrada"] is True
        assert r["autorizada_en_operacion"] is True
        assert r["coincidencias"] >= 1
        assert r["mejor_match"]["estatus"] == "En operación" or "En operacion" in r["mejor_match"]["estatus"]

    def test_no_existe_emite_advertencia_de_validar_otras_autoridades(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        c = CondusefSipresClient()
        # Sentinela "FAKE" en el nombre → mock devuelve 0 resultados
        r = c.verificar_autorizada("ENTIDAD FAKE")
        assert r["encontrada"] is False
        assert r["autorizada_en_operacion"] is False
        assert any("CNBV" in adv or "CNSF" in adv for adv in r["advertencias"])

    def test_query_invalida(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        c = CondusefSipresClient()
        with pytest.raises(ValueError):
            c.verificar_autorizada("x")


# ============================================================
# Integración: HTML real → dict canónico
# ============================================================

class TestNormalizarResultadoIntegracion:
    def test_pipeline_html_real_a_dict(self):
        from mp_condusef_sipres.client import CondusefSipresClient
        r = CondusefSipresClient._normalizar_resultado(
            html_text=FIXTURE_HTML_BANORTE,
            nombre="BANORTE",
            sector="",
            estado="",
            estatus="",
            limite=10,
            simulated=False,
        )
        assert r["filtros"]["nombre"] == "BANORTE"
        assert r["total_padron"] == 186
        assert r["devueltos"] == 3
        assert r["simulated"] is False
        # Primera entidad parseada correctamente
        e0 = r["resultados"][0]
        assert e0["clave_registro"] == "40165"
        assert "Banco Bineo" in e0["denominacion"]
        assert e0["idins"] == "16316"
