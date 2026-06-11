"""Tests para mp_sat_portal/uuid_validator.py."""

from __future__ import annotations

from mp_sat_portal.uuid_validator import (
    construir_url_verificacion,
    normalizar_uuid,
    validar_uuid,
)
from mp_sat_portal.tests.conftest import (
    DEMO_UUID_FORMATO_MAL,
    DEMO_UUID_LONGITUD_MAL,
    DEMO_UUID_VALIDO,
    DEMO_UUID_VALIDO_2,
)


def test_normalizar_uuid_quita_espacios_y_mayusculiza() -> None:
    assert normalizar_uuid("  a1b2c3d4-e5f6 ") == "A1B2C3D4-E5F6"


def test_validar_uuid_valido_v4() -> None:
    r = validar_uuid(DEMO_UUID_VALIDO)
    assert r["valido"] is True
    assert r["uuid_normalizado"] == DEMO_UUID_VALIDO
    assert r["es_v4_random"] is True
    assert r["version_uuid"] == 4
    assert r["razon"] is None


def test_validar_uuid_valido_v4_minusculas() -> None:
    r = validar_uuid(DEMO_UUID_VALIDO.lower())
    assert r["valido"] is True
    # Se normaliza a mayúsculas
    assert r["uuid_normalizado"] == DEMO_UUID_VALIDO


def test_validar_uuid_otro_v4() -> None:
    r = validar_uuid(DEMO_UUID_VALIDO_2)
    assert r["valido"] is True
    assert r["es_v4_random"] is True


def test_validar_uuid_vacio() -> None:
    r = validar_uuid("")
    assert r["valido"] is False
    assert "vacío" in r["razon"].lower()


def test_validar_uuid_no_str() -> None:
    r = validar_uuid(12345)  # type: ignore[arg-type]
    assert r["valido"] is False


def test_validar_uuid_formato_mal() -> None:
    r = validar_uuid(DEMO_UUID_FORMATO_MAL)
    assert r["valido"] is False
    assert "longitud" in r["razon"].lower() or "formato" in r["razon"].lower()


def test_validar_uuid_longitud_corta() -> None:
    r = validar_uuid(DEMO_UUID_LONGITUD_MAL)
    assert r["valido"] is False
    assert "longitud" in r["razon"].lower()


def test_validar_uuid_caracteres_no_hex() -> None:
    bad = "A1B2C3D4-E5F6-4789-9ABC-DEFGHIJKLMN0"  # G..N no son hex
    r = validar_uuid(bad)
    assert r["valido"] is False


def test_validar_uuid_con_espacios_intermedios() -> None:
    """Los espacios se quitan al normalizar — el UUID resultante puede ser corto."""
    r = validar_uuid("A1B2C3D4 E5F6 4789 9ABC DEF012345678")
    # Tras quitar espacios queda sin guiones → formato 8-4-4-4-12 falla
    assert r["valido"] is False


def test_construir_url_verificacion_normaliza_total() -> None:
    url = construir_url_verificacion(
        DEMO_UUID_VALIDO, "ABC010101AA1", "DEF020202BB2", "1500.50"
    )
    assert "id=A1B2C3D4-E5F6-4789-9ABC-DEF012345678" in url
    assert "re=ABC010101AA1" in url
    assert "rr=DEF020202BB2" in url
    assert "tt=1500.500000" in url


def test_construir_url_total_no_numerico() -> None:
    """Si total no es numérico, lo pasa como string sin formatear."""
    url = construir_url_verificacion(
        DEMO_UUID_VALIDO, "ABC010101AA1", "DEF020202BB2", "no-numero"
    )
    assert "tt=no-numero" in url
