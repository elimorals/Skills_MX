"""Tests para mp_sat_portal/catalogos.py."""

from __future__ import annotations

from mp_sat_portal.catalogos import (
    AUTH_METHODS,
    ESTADO_69B,
    MOTIVOS_69_INCUMPLIDOS,
    STATUS_EFIRMA,
    STATUS_RFC,
    TIPOS_OBLIGACION,
    es_riesgo_alto_69,
    es_riesgo_alto_69b,
)


def test_catalogos_contienen_claves_esperadas() -> None:
    assert "ACTIVO" in STATUS_RFC
    assert "DEFINITIVO" in ESTADO_69B
    assert "PRESUNTO" in ESTADO_69B
    assert "DOMICILIO_FALSO" in MOTIVOS_69_INCUMPLIDOS
    assert "VIGENTE" in STATUS_EFIRMA
    assert "ISR_PROVISIONAL" in TIPOS_OBLIGACION
    assert "EFIRMA" in AUTH_METHODS


def test_es_riesgo_alto_69b_definitivo_y_presunto() -> None:
    assert es_riesgo_alto_69b("DEFINITIVO") is True
    assert es_riesgo_alto_69b("PRESUNTO") is True
    assert es_riesgo_alto_69b("definitivo") is True  # case-insensitive
    assert es_riesgo_alto_69b("DESVIRTUADO") is False
    assert es_riesgo_alto_69b("SENTENCIA_FAVORABLE") is False


def test_es_riesgo_alto_69_motivos_criticos() -> None:
    assert es_riesgo_alto_69("DOMICILIO_FALSO") is True
    assert es_riesgo_alto_69("NO_LOCALIZADO") is True
    assert es_riesgo_alto_69("CREDITO_FIRME") is True
    assert es_riesgo_alto_69("SENTENCIA_FIRME") is True
    # Motivos menores no son riesgo alto
    assert es_riesgo_alto_69("CONDONACION") is False
    assert es_riesgo_alto_69("CANCELADO_FALTA_COBRO") is False
