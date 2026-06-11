"""Tests para catalogos.py — tablas y enums RENAPO."""

from __future__ import annotations

from mp_curp_renapo.catalogos import (
    CHAR_A_NUMERO,
    ESTADOS_CURP,
    PALABRAS_INCONVENIENTES,
    SEXO_CURP,
)


def test_32_estados_mas_extranjero() -> None:
    # 32 entidades federativas + NE para extranjeros = 33
    assert len(ESTADOS_CURP) == 33
    assert "NE" in ESTADOS_CURP
    assert "DF" in ESTADOS_CURP  # CDMX histórico


def test_sexo_es_h_o_m() -> None:
    assert set(SEXO_CURP) == {"H", "M"}


def test_tabla_char_a_numero_valores_dígitos() -> None:
    # Dígitos: '0' → 0, '9' → 9
    assert CHAR_A_NUMERO["0"] == 0
    assert CHAR_A_NUMERO["9"] == 9


def test_tabla_char_a_numero_letras() -> None:
    # A=10, después de los 10 dígitos
    assert CHAR_A_NUMERO["A"] == 10
    # H=17 (esta es la trampa de varios docs antiguos: A=10 → H=17, no 18)
    assert CHAR_A_NUMERO["H"] == 17
    # N=23, Ñ=24, O=25 (Ñ va entre N y O)
    assert CHAR_A_NUMERO["N"] == 23
    assert CHAR_A_NUMERO["Ñ"] == 24
    assert CHAR_A_NUMERO["O"] == 25
    # Z queda como último
    assert CHAR_A_NUMERO["Z"] == 36


def test_palabras_inconvenientes_es_set() -> None:
    assert isinstance(PALABRAS_INCONVENIENTES, set)
    # Casos clásicos documentados por RENAPO
    assert "BUEY" in PALABRAS_INCONVENIENTES
    assert "PUTO" in PALABRAS_INCONVENIENTES
    assert "CACA" in PALABRAS_INCONVENIENTES
