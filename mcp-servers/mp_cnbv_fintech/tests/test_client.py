"""Tests mp_cnbv_fintech."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
if str(_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(_MCP_ROOT))

from mp_cnbv_fintech.client import (  # noqa: E402
    ITF_AUTORIZADAS_SNAPSHOT,
    CnbvFintechClient,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402


@pytest.fixture
def tmp_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    cache = FileCache("cnbv_fintech_test", root=tmp_path / "cache")
    bit = Bitacora("cnbv_fintech_test", root=tmp_path / "bita")
    return CnbvFintechClient(cache=cache, bitacora=bit)


class TestSnapshot:
    def test_ifpe_no_vacio(self):
        assert len(ITF_AUTORIZADAS_SNAPSHOT["ifpe"]) >= 5

    def test_ifc_no_vacio(self):
        assert len(ITF_AUTORIZADAS_SNAPSHOT["ifc"]) >= 3

    def test_estructura_completa(self):
        for tipo in ["ifpe", "ifc"]:
            for item in ITF_AUTORIZADAS_SNAPSHOT[tipo]:
                assert "rfc" in item and "nombre" in item
                assert "marca" in item and "estado" in item
                assert "fecha_autorizacion" in item


class TestConsultarItf:
    def test_sin_rfc_ni_nombre(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_itf()

    def test_rfc_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_itf(rfc="INVALIDO")

    def test_buscar_por_marca_conocida(self, tmp_client):
        r = tmp_client.consultar_itf(nombre="Bitso")
        assert r["encontrada"] is True
        assert r["tipo"] == "ifpe"
        assert r["puede_operar_legalmente"] is True

    def test_buscar_por_marca_crowdfunding(self, tmp_client):
        r = tmp_client.consultar_itf(nombre="Doopla")
        assert r["encontrada"] is True
        assert r["tipo"] == "ifc"

    def test_no_encontrada(self, tmp_client):
        r = tmp_client.consultar_itf(nombre="EMPRESA QUE NO EXISTE XYZ")
        assert r["encontrada"] is False
        assert r["puede_operar_legalmente"] is False


class TestListados:
    def test_listar_ifpe(self, tmp_client):
        r = tmp_client.listar_ifpe()
        assert r["tipo"] == "ifpe"
        assert r["total"] >= 5

    def test_listar_ifc(self, tmp_client):
        r = tmp_client.listar_ifc()
        assert r["tipo"] == "ifc"
        assert r["total"] >= 3

    def test_modelos_novedosos(self, tmp_client):
        r = tmp_client.listar_modelos_novedosos()
        assert "modelos" in r
        assert "base_legal" in r


class TestVerificarContraparte:
    def test_rfc_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.verificar_contraparte(rfc="INVALIDO")

    def test_ifpe_compatible_con_pagos(self, tmp_client):
        # Usar RFC del snapshot — BITSO IFPE
        rfc = ITF_AUTORIZADAS_SNAPSHOT["ifpe"][0]["rfc"]
        r = tmp_client.verificar_contraparte(rfc=rfc, tipo_operacion="fondos_pago")
        assert r["puede_operar"] is True
        assert r["tipo_itf"] == "ifpe"

    def test_ifpe_incompatible_con_crowdfunding(self, tmp_client):
        rfc = ITF_AUTORIZADAS_SNAPSHOT["ifpe"][0]["rfc"]
        r = tmp_client.verificar_contraparte(rfc=rfc, tipo_operacion="crowdfunding")
        assert r["puede_operar"] is False

    def test_no_itf_no_puede_operar(self, tmp_client):
        r = tmp_client.verificar_contraparte(
            rfc="XYZ010101AB1", tipo_operacion="cualquiera",
        )
        assert r["puede_operar"] is False
        assert "Art. 5 Ley Fintech" in r["razon"]
