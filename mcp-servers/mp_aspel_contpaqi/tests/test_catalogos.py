"""Tests para mp_aspel_contpaqi/catalogos.py."""

from __future__ import annotations

from mp_aspel_contpaqi.catalogos import (
    CODIGO_AGRUPADOR_SAT,
    NATURALEZA_CUENTA,
    TIPO_POLIZA,
    es_cuenta_balance,
    es_cuenta_resultado,
    get_codigo_sat,
)


def test_tipo_poliza_incluye_diario() -> None:
    assert "DIARIO" in TIPO_POLIZA
    assert "INGRESOS" in TIPO_POLIZA
    assert "EGRESOS" in TIPO_POLIZA


def test_naturaleza_completa() -> None:
    assert "DEUDORA" in NATURALEZA_CUENTA
    assert "ACREEDORA" in NATURALEZA_CUENTA


def test_codigo_agrupador_sat_incluye_principales() -> None:
    for codigo in ["100", "200", "300", "401", "500", "600"]:
        assert codigo in CODIGO_AGRUPADOR_SAT
        info = CODIGO_AGRUPADOR_SAT[codigo]
        assert "nombre" in info
        assert "naturaleza" in info
        assert "tipo" in info


def test_get_codigo_sat_existente() -> None:
    info = get_codigo_sat("102")
    assert info is not None
    assert info["nombre"] == "Bancos"


def test_get_codigo_sat_inexistente() -> None:
    assert get_codigo_sat("999") is None


def test_es_cuenta_resultado() -> None:
    assert es_cuenta_resultado("401") is True
    assert es_cuenta_resultado("500") is True
    assert es_cuenta_resultado("600") is True
    assert es_cuenta_resultado("102") is False
    assert es_cuenta_resultado("XXX") is False


def test_es_cuenta_balance() -> None:
    assert es_cuenta_balance("102") is True
    assert es_cuenta_balance("201") is True
    assert es_cuenta_balance("300") is True
    assert es_cuenta_balance("401") is False
