"""Tests SACPI Michoacán (lógica subyacente — sin FastMCP)."""

from __future__ import annotations

import pytest

from shared.plataformas_saas_mx import (
    SACPI_MICHOACAN,
    SACPI_MUNICIPIOS_MICH,
    codigo_municipio_sacpi,
    plataforma_para_municipio,
)


# ============================================================
# Catálogo
# ============================================================

def test_sacpi_tiene_95_municipios():
    assert len(SACPI_MUNICIPIOS_MICH) == 95


def test_sacpi_estados_cubiertos():
    assert "mich" in SACPI_MICHOACAN.estados_cubiertos


def test_sacpi_url_valida():
    assert SACPI_MICHOACAN.url_consulta.startswith("http")
    assert "sacpi" in SACPI_MICHOACAN.url_consulta.lower()


def test_sacpi_validado():
    assert SACPI_MICHOACAN.validado is True


# ============================================================
# codigo_municipio_sacpi()
# ============================================================

def test_codigo_municipio_exacto():
    # Ciudad Hidalgo está como "HIDALGO" en SACPI
    codigo = codigo_municipio_sacpi("HIDALGO")
    assert codigo == "034"


def test_codigo_municipio_alias():
    # "Ciudad Hidalgo" debería mapear a "HIDALGO" → "034"
    codigo = codigo_municipio_sacpi("Ciudad Hidalgo")
    assert codigo == "034"


def test_codigo_municipio_apatzingan():
    codigo = codigo_municipio_sacpi("APATZINGAN")
    assert codigo == "006"


def test_codigo_municipio_no_existe():
    """Morelia tiene portal propio, NO está en SACPI."""
    codigo = codigo_municipio_sacpi("MORELIA")
    assert codigo is None


def test_codigo_municipio_uruapan_no_sacpi():
    codigo = codigo_municipio_sacpi("URUAPAN")
    assert codigo is None


# ============================================================
# plataforma_para_municipio()
# ============================================================

def test_plataforma_apatzingan_es_sacpi():
    plat = plataforma_para_municipio("mich", "APATZINGAN")
    assert plat is not None
    assert plat.nombre == "SACPI"


def test_plataforma_morelia_no_es_sacpi():
    """Morelia NO está en SACPI."""
    plat = plataforma_para_municipio("mich", "MORELIA")
    assert plat is None


def test_plataforma_municipio_otro_estado():
    """Municipio de otro estado no puede estar en SACPI MICH."""
    plat = plataforma_para_municipio("jal", "guadalajara")
    assert plat is None


# ============================================================
# Estructura de respuesta (con mock)
# ============================================================

def test_sacpi_municipios_tienen_codigo_y_nombre():
    for codigo, nombre in SACPI_MUNICIPIOS_MICH.items():
        assert len(codigo) == 3
        assert codigo.isdigit()
        assert len(nombre) > 0
        assert nombre == nombre.upper()  # todos en MAYÚSCULAS en SACPI
