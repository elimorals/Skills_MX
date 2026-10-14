"""Tests mp_gas_natural_mx."""
from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest
import respx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import mp_gas_natural_mx.client as gas  # noqa: E402
from shared.errors import NotFoundError, UpstreamError, ValidationError  # noqa: E402

TARIFAS = "https://www.ecogas.com.mx/tarifas.php"
# Texto real extraído de los PDFs de Ecogas (2026-10-14).
PRECIO = ("Usuarios Residenciales de Mexicali\nPrecio del mes de Septiembre $8.27 del gas natural\n"
          "MXP/Gjoule $217.56\n(precio no incluye IVA)\n")
LISTA = ("Ecogas México, S. de R.L. de C.V. \nZona Geográfica Chihuahua \n"
         "LISTA DE TARIFAS MÁXIMAS AUTORIZADAS PARA 2025 \n"
         "así como al oficio\nF00.07.UH/3851/2026 de fecha 19 de febrero de 2026, por el que la Comisión "
         "Nacional de Energía aprobó a Ecogas \nMéxico, S. de R.L. de C.V., titular del permiso G/013/DIS/1997, la")


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))


def test_parse_precio_mensual():
    d = gas.parse_documento(PRECIO)
    assert d == {"tipo": "precio_mensual_residencial", "zona": "Mexicali", "mes": "Septiembre",
                 "precio_mxn_m3": 8.27, "precio_mxn_gj": 217.56, "incluye_iva": False}


def test_parse_lista_tarifas():
    d = gas.parse_documento(LISTA)
    assert d["tipo"] == "lista_tarifas_maximas" and d["zona"] == "Chihuahua"
    assert d["permiso"] == "G/013/DIS/1997"
    assert d["oficio_aprobacion"].startswith("F00.07.UH/3851/2026")


def test_parse_desconocido():
    with pytest.raises(UpstreamError):
        gas.parse_documento("otra cosa")


def test_pdf_texto_rechaza_no_pdf():
    with pytest.raises(UpstreamError):
        gas.pdf_texto(b"<html>")


@respx.mock
def test_tarifas_vigentes_filtra_zona(monkeypatch):
    respx.get(TARIFAS).mock(return_value=httpx.Response(200, text=(
        '<a href="pdf/index.php?file=preciosmexicali.pdf">M</a>'
        '<a href="pdf/index.php?file=precioschihuahua.pdf">C</a>'
        '<a href="pdf/index.php?file=abc_123.pdf">T</a>')))
    respx.get(url__regex=r".*preciosmexicali.*").mock(return_value=httpx.Response(200, content=b"P"))
    chih = respx.get(url__regex=r".*precioschihuahua.*").mock(return_value=httpx.Response(200, content=b"C"))
    respx.get(url__regex=r".*abc_123.*").mock(return_value=httpx.Response(200, content=b"L"))
    monkeypatch.setattr(gas, "pdf_texto", lambda b: PRECIO if b == b"P" else LISTA)
    r = gas.GasNaturalMxClient().tarifas_vigentes("ecogas", "mexicali")
    assert not chih.called
    assert {d["tipo"] for d in r["documentos"]} == {"precio_mensual_residencial", "lista_tarifas_maximas"}
    assert all(d["fuente"].startswith("https://www.ecogas.com.mx/pdf/") for d in r["documentos"])
    assert r["simulated"] is False


@respx.mock
def test_tarifas_upstream_caido():
    respx.get(TARIFAS).mock(return_value=httpx.Response(503))
    with pytest.raises(UpstreamError):
        gas.GasNaturalMxClient().tarifas_vigentes("ecogas")


def test_tarifas_distribuidor_sin_pagina_publica():
    with pytest.raises(UpstreamError):
        gas.GasNaturalMxClient().tarifas_vigentes("naturgy")


def test_recibo_es_handoff_login():
    r = gas.GasNaturalMxClient().consultar_recibo("naturgy", "12345678")
    assert r["requiere_humano"] is True and r["motivo"] == "login" and r["simulated"] is False


def test_recibo_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert gas.GasNaturalMxClient().consultar_recibo("naturgy", "12345678")["simulated"] is True


def test_distribuidor_invalido():
    with pytest.raises(NotFoundError):
        gas.GasNaturalMxClient().consultar_recibo("xx", "12345")


def test_contrato_corto():
    with pytest.raises(ValidationError):
        gas.GasNaturalMxClient().consultar_recibo("naturgy", "1")


def test_listar_distribuidores():
    r = gas.GasNaturalMxClient().listar_distribuidores()
    assert r["total"] == 5
    assert [d["clave"] for d in r["distribuidores"] if d["tarifas_publicas"]] == ["ecogas"]


@pytest.mark.live
def test_live_tarifas_ecogas_mexicali():
    pytest.importorskip("pypdf")
    r = gas.GasNaturalMxClient().tarifas_vigentes("ecogas", "mexicali")
    precios = [d for d in r["documentos"] if d["tipo"] == "precio_mensual_residencial"]
    assert precios and precios[0]["precio_mxn_m3"] > 0
