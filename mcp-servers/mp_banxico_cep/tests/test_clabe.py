"""Tests para clabe.py — validación CLABE 18 dígitos + parseo clave rastreo."""

from __future__ import annotations

from mp_banxico_cep.clabe import (
    calcular_digito_control_clabe,
    parsear_clave_rastreo,
    validar_clabe,
)
from mp_banxico_cep.tests.conftest import make_valid_clabe


# ---------- dígito de control ----------


def test_digito_control_input_corto_es_menos_1() -> None:
    assert calcular_digito_control_clabe("12345") == -1


def test_digito_control_no_numerico_es_menos_1() -> None:
    assert calcular_digito_control_clabe("ABC" + "0" * 14) == -1


def test_digito_control_siempre_entre_0_y_9() -> None:
    for base in (
        "01218000123456789",
        "00200012345678901",
        "07212300012345678",
        "64600000000000000",  # STP
    ):
        d = calcular_digito_control_clabe(base)
        assert 0 <= d <= 9


def test_digito_control_es_determinístico() -> None:
    base = "01218000123456789"
    assert calcular_digito_control_clabe(base) == calcular_digito_control_clabe(base)


# ---------- validar_clabe ----------


def test_clabe_valida_bbva() -> None:
    clabe = make_valid_clabe("01218000123456789")
    r = validar_clabe(clabe)
    assert r["valida"] is True
    assert r["banco_codigo"] == "012"
    assert r["banco_nombre"] == "BBVA México"
    assert r["errores"] == []


def test_clabe_valida_normaliza_espacios_y_guiones() -> None:
    clabe = make_valid_clabe("01218000123456789")
    espaciada = " ".join(clabe[i : i + 4] for i in range(0, 18, 4))
    r = validar_clabe(espaciada)
    assert r["valida"] is True


def test_clabe_invalida_longitud() -> None:
    r = validar_clabe("1234")
    assert r["valida"] is False
    assert any("18 dígitos" in e for e in r["errores"])


def test_clabe_invalida_no_numerica() -> None:
    r = validar_clabe("ABCDEFGHIJKLMNOPQR")
    assert r["valida"] is False


def test_clabe_digito_control_incorrecto() -> None:
    clabe = make_valid_clabe("01218000123456789")
    # Corromper el dígito final
    clabe_mala = clabe[:-1] + str((int(clabe[-1]) + 1) % 10)
    r = validar_clabe(clabe_mala)
    assert r["valida"] is False
    assert any("Dígito de control" in e for e in r["errores"])


def test_clabe_banco_desconocido_es_alerta_no_error() -> None:
    """Si el dígito cuadra pero el banco no se reconoce, alerta sin invalidar."""
    clabe = make_valid_clabe("99988800000000000")
    r = validar_clabe(clabe)
    assert r["valida"] is True
    assert r["banco_nombre"] is None
    assert any("no está en el catálogo" in a for a in r["alertas"])


# ---------- parsear_clave_rastreo ----------


def test_clave_rastreo_bbva_se_identifica() -> None:
    r = parsear_clave_rastreo("MBAN0100123456789012")
    assert r["formato_valido"] is True
    assert r["prefijo_detectado"] == "MBAN"
    assert r["emisor_probable"] == "BBVA México"


def test_clave_rastreo_mercado_pago() -> None:
    r = parsear_clave_rastreo("MERPAGO20260315ABCDEF1234")
    assert r["formato_valido"] is True
    assert r["emisor_probable"] == "Mercado Pago"


def test_clave_rastreo_stp() -> None:
    r = parsear_clave_rastreo("STP20260315ABCDEF1234567890")
    assert r["emisor_probable"] == "STP / fintechs"


def test_clave_rastreo_sin_prefijo_conocido_alerta_pero_no_invalida() -> None:
    r = parsear_clave_rastreo("XYZNUEVAFINTECH123456789")
    assert r["formato_valido"] is True
    assert r["emisor_probable"] is None
    assert any("No se identificó" in a for a in r["alertas"])


def test_clave_rastreo_demasiado_corta() -> None:
    r = parsear_clave_rastreo("ABC")
    assert r["formato_valido"] is False
    assert len(r["alertas"]) > 0


def test_clave_rastreo_con_espacios_y_minusculas_se_normaliza() -> None:
    r = parsear_clave_rastreo(" mban0100123456789012 ")
    assert r["formato_valido"] is True
    assert r["clave_normalizada"] == "MBAN0100123456789012"
