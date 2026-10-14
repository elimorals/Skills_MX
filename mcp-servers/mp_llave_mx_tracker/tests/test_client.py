"""Tests mp_llave_mx_tracker."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import httpx
import pytest
import respx

from mp_llave_mx_tracker.client import (
    DEPENDENCIAS_MONITOREADAS,
    DETECCION_2026_10_14,
    LlaveMxTrackerClient,
    STATUS_VALIDOS,
    detectar_llave,
)

# Fragmento real de https://www.bajacalifornia.gob.mx/ (2026-10-14)
BC_HTML = ('<a href="https://www.llave.gob.mx" target="_blank"><img alt="Llave MX" '
           'class="img-fluid" src="../Recursos/Imagenes/llave.png"></a>')


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
from shared.errors import ValidationError


class TestListar:
    def setup_method(self):
        self.c = LlaveMxTrackerClient()

    def test_listar_todas(self):
        r = self.c.listar_dependencias()
        assert r["total"] == len(DEPENDENCIAS_MONITOREADAS)
        assert "fuente_oficial_llave" in r

    def test_filtrar_federal(self):
        r = self.c.listar_dependencias(nivel="federal")
        for d in r["dependencias"]:
            assert d["nivel"] == "federal"

    def test_filtrar_estatal(self):
        r = self.c.listar_dependencias(nivel="estatal")
        for d in r["dependencias"]:
            assert d["nivel"] == "estatal"


class TestEstatusDependencia:
    def setup_method(self):
        self.c = LlaveMxTrackerClient()

    def test_atdt_integrado(self):
        r = self.c.estatus_dependencia("atdt")
        assert r["status_2026_06"] == "integrado"
        assert r["status_curado_verificado"] is False
        assert r["deteccion_2026_10_14"] == "no_detectado_en_portada"

    def test_sat_no_integrado(self):
        r = self.c.estatus_dependencia("sat")
        assert r["status_2026_06"] == "no_integrado"

    def test_clave_invalida_falla(self):
        with pytest.raises(ValidationError):
            self.c.estatus_dependencia("inexistente")


class TestEstadisticas:
    def setup_method(self):
        self.c = LlaveMxTrackerClient()

    def test_estadisticas_suman_total(self):
        r = self.c.estadisticas_nacionales()
        assert r["total_dependencias_monitoreadas"] == len(DEPENDENCIAS_MONITOREADAS)
        assert sum(r["por_status_curado"].values()) == r["total_dependencias_monitoreadas"]
        assert sum(r["por_deteccion_vivo_2026_10_14"].values()) == r["total_dependencias_monitoreadas"]

    def test_sin_meta_inventada(self):
        assert "meta_lnetb_2030_pct" not in self.c.estadisticas_nacionales()

    def test_status_validos_completos(self):
        r = self.c.estadisticas_nacionales()
        for s in STATUS_VALIDOS:
            assert s in r["por_status_curado"]

    def test_snapshot_cubre_todas(self):
        assert set(DETECCION_2026_10_14) == {d["clave"] for d in DEPENDENCIAS_MONITOREADAS}


class TestVerificarEnVivo:
    def setup_method(self):
        self.c = LlaveMxTrackerClient()

    def test_mock_solo_con_flag(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
        assert self.c.verificar_en_vivo("sat")["simulated"] is True

    def test_detectar_enlace_real_bc(self):
        assert detectar_llave(BC_HTML, "https://www.bajacalifornia.gob.mx/")["deteccion"] == "enlace_llave_gob_mx"
        assert detectar_llave("", "https://www.llave.gob.mx/oauthV2.xhtml?client_id=1")["deteccion"] == "oauth_llave_detectado"
        assert detectar_llave("<p>Inicia con Llave MX</p>", "https://x")["deteccion"] == "mencion_llave_mx"

    @respx.mock
    def test_verificar_real_bc(self):
        respx.get("https://www.bajacalifornia.gob.mx/").mock(return_value=httpx.Response(200, text=BC_HTML))
        r = self.c.verificar_en_vivo("bc")
        assert r["simulated"] is False
        assert r["deteccion"] == "enlace_llave_gob_mx"

    @respx.mock
    def test_portal_403_es_inaccesible(self):
        respx.get("https://www.imss.gob.mx/").mock(return_value=httpx.Response(403))
        assert self.c.verificar_en_vivo("imss")["deteccion"] == "inaccesible"

    def test_clave_invalida_falla(self):
        with pytest.raises(ValidationError):
            self.c.verificar_en_vivo("inexistente")


@pytest.mark.live
def test_live_verificar_bc():
    r = LlaveMxTrackerClient().verificar_en_vivo("bc")
    assert r["simulated"] is False
    assert r["http_status"] == 200
