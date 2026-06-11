"""Tests para catalogos.py — bancos CLABE + tipos operación SPEI."""

from __future__ import annotations

from mp_banxico_cep.catalogos import (
    BANCOS_CLABE,
    BANCOS_TODOS,
    ESTADO_CEP,
    OTROS_PARTICIPANTES_CLABE,
    TIPO_OPERACION_SPEI,
    lookup_banco,
)


def test_bancos_principales_presentes() -> None:
    # Top 6 sí o sí
    assert BANCOS_CLABE["002"] == "Banamex"
    assert BANCOS_CLABE["012"] == "BBVA México"
    assert BANCOS_CLABE["014"] == "Santander"
    assert BANCOS_CLABE["021"] == "HSBC"
    assert BANCOS_CLABE["044"] == "Scotiabank"
    assert BANCOS_CLABE["072"] == "Banorte"


def test_fintechs_relevantes_presentes() -> None:
    # Códigos altos (600+) son fintechs / casas bolsa
    assert "Mercado Pago" in OTROS_PARTICIPANTES_CLABE.values()
    assert "STP" in OTROS_PARTICIPANTES_CLABE["646"]
    assert "Stori" in OTROS_PARTICIPANTES_CLABE["728"]


def test_bancos_todos_es_union() -> None:
    assert len(BANCOS_TODOS) == len(BANCOS_CLABE) + len(OTROS_PARTICIPANTES_CLABE)


def test_lookup_banco_normaliza_padding() -> None:
    """Códigos pueden venir sin padding ('12' por '012')."""
    assert lookup_banco("12") == "BBVA México"
    assert lookup_banco("012") == "BBVA México"


def test_lookup_banco_devuelve_none_si_desconocido() -> None:
    assert lookup_banco("999") is None


def test_tipo_operacion_spei_tiene_basicos() -> None:
    assert "1" in TIPO_OPERACION_SPEI  # tercero a tercero
    assert "19" in TIPO_OPERACION_SPEI  # devolución acreditada


def test_estado_cep_cubre_4_estados() -> None:
    assert set(ESTADO_CEP) == {"disponible", "no_encontrado", "pendiente", "rechazado"}
