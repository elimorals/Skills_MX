"""Tests para validacion.py — validación estructural + derivaciones + generación."""

from __future__ import annotations

from datetime import date

from mp_curp_renapo.tests.conftest import make_valid_curp
from mp_curp_renapo.validacion import (
    calcular_digito_verificador,
    derivar_estado,
    derivar_fecha_nacimiento,
    derivar_sexo,
    generar_curp_desde_datos,
    normalizar,
    validar_estructura,
    validar_lote,
)

# ---------- normalización ----------


def test_normalizar_quita_espacios_y_sube_a_mayusculas() -> None:
    assert normalizar("  perz821223hdfrrl09  ") == "PERZ821223HDFRRL09"


def test_normalizar_quita_acentos() -> None:
    assert normalizar("Pérez") == "PEREZ"
    assert normalizar("Núñez") == "NUNEZ"


def test_normalizar_vacio() -> None:
    assert normalizar("") == ""
    assert normalizar(None) == ""  # type: ignore[arg-type]


# ---------- dígito verificador ----------


def test_calcular_digito_curp_ejemplo_publico() -> None:
    """CURP pública documentada en tutoriales oficiales RENAPO."""
    # PERZ821223HDFRRL → debe dar dígito 9
    assert calcular_digito_verificador("PERZ821223HDFRRL0") == 9


def test_calcular_digito_devuelve_menos_1_para_input_corto() -> None:
    assert calcular_digito_verificador("ABC") == -1


def test_calcular_digito_devuelve_menos_1_si_char_invalido() -> None:
    base = "@" * 17
    assert calcular_digito_verificador(base) == -1


def test_calcular_digito_siempre_entre_0_y_9() -> None:
    # Probar varios patrones — el dígito final debe estar en 0..9 siempre
    for base in (
        "AAAA000101HASAAAA0",
        "ZZZZ991231MZSZZZZZ",
        "BCDF200315HJCBCDB1",
    ):
        d = calcular_digito_verificador(base[:17])
        assert 0 <= d <= 9


# ---------- validar_estructura: casos positivos ----------


def test_curp_publica_valida() -> None:
    r = validar_estructura("PERZ821223HDFRRL09")
    assert r["valido_estructura"] is True
    assert r["errores"] == []
    assert r["fecha_nacimiento"] == "1982-12-23"
    assert r["sexo"] == "H"
    assert r["estado_codigo"] == "DF"
    assert r["estado_nombre"] == "Ciudad de México"


def test_curp_sintetica_2010_es_valida() -> None:
    """Char homonimia letra → siglo 2000s."""
    curp = make_valid_curp("ROMA100315HJCMRRA")  # 2010-03-15, Jalisco, hombre, homonimia A
    r = validar_estructura(curp)
    assert r["valido_estructura"] is True, r["errores"]
    assert r["fecha_nacimiento"] == "2010-03-15"
    assert r["siglo_nacimiento"] == 2000
    assert r["sexo"] == "H"
    assert r["estado_codigo"] == "JC"


def test_curp_sintetica_1980_es_valida() -> None:
    """Char homonimia dígito → siglo 1900s."""
    curp = make_valid_curp("GOPL800701MNLNZS0")
    r = validar_estructura(curp)
    assert r["valido_estructura"] is True
    assert r["fecha_nacimiento"] == "1980-07-01"
    assert r["siglo_nacimiento"] == 1900
    assert r["sexo"] == "M"
    assert r["estado_codigo"] == "NL"


# ---------- validar_estructura: casos negativos ----------


def test_curp_corta_es_invalida() -> None:
    r = validar_estructura("ABC123")
    assert r["valido_estructura"] is False
    assert any("Longitud" in e for e in r["errores"])


def test_curp_formato_no_coincide() -> None:
    # 18 chars pero el patrón es basura
    r = validar_estructura("1234567890ABCDEFGH")
    assert r["valido_estructura"] is False
    assert any("Formato" in e for e in r["errores"])


def test_curp_estado_invalido() -> None:
    """El char[12-13] debe ser un código de estado RENAPO."""
    curp = make_valid_curp("PERZ821223HZZRRL0")  # ZZ no existe
    r = validar_estructura(curp)
    assert r["valido_estructura"] is False
    assert any("estado" in e.lower() for e in r["errores"])


def test_curp_fecha_invalida_31_feb() -> None:
    curp = make_valid_curp("PERZ820231HDFRRL0")  # 31 de febrero
    r = validar_estructura(curp)
    assert r["valido_estructura"] is False
    assert any("Fecha" in e for e in r["errores"])


def test_curp_digito_verificador_incorrecto() -> None:
    """Si tomamos una CURP válida y le cambiamos el dígito final, debe fallar."""
    curp_ok = "PERZ821223HDFRRL09"
    # Forzar dígito 0 (incorrecto, debería ser 9)
    curp_mal = curp_ok[:-1] + "0"
    r = validar_estructura(curp_mal)
    assert r["valido_estructura"] is False
    assert any("verificador" in e.lower() for e in r["errores"])


def test_curp_fecha_en_futuro_es_invalida() -> None:
    # 99 99 99 con homonimia letra → 2099
    curp = make_valid_curp("PERZ991231HDFRRLA")
    r = validar_estructura(curp)
    # 2099 todavía es futuro hoy → error
    assert r["valido_estructura"] is False
    assert any("futuro" in e.lower() for e in r["errores"])


# ---------- pseudo-CURP ----------


def test_pseudo_curp_xexx_marca_alerta() -> None:
    curp = make_valid_curp("XEXX010101HNEXXXA")
    r = validar_estructura(curp)
    assert r["valido_estructura"] is True
    assert r["es_pseudo_curp"] is True
    assert any("Pseudo-CURP" in a for a in r["alertas"])


# ---------- derivaciones ----------


def test_derivar_fecha_devuelve_date() -> None:
    f = derivar_fecha_nacimiento("PERZ821223HDFRRL09")
    assert f == date(1982, 12, 23)


def test_derivar_fecha_2000s_via_homonimia_letra() -> None:
    curp = make_valid_curp("AAAA100101HASAAAA")
    f = derivar_fecha_nacimiento(curp)
    assert f is not None
    assert f.year == 2010


def test_derivar_sexo() -> None:
    assert derivar_sexo("PERZ821223HDFRRL09") == "H"
    assert derivar_sexo("XYZ") is None


def test_derivar_estado() -> None:
    estado = derivar_estado("PERZ821223HDFRRL09")
    assert estado == ("DF", "Ciudad de México")


# ---------- batch ----------


def test_validar_lote_resumen_correcto() -> None:
    curps = [
        "PERZ821223HDFRRL09",  # válida
        "ABC",  # inválida (corta)
        make_valid_curp("ROMA100315HJCMRRA"),  # válida
    ]
    r = validar_lote(curps)
    assert r["total"] == 3
    assert r["validos"] == 2
    assert r["invalidos"] == 1
    assert len(r["detalle"]) == 3


# ---------- generación ----------


def test_generar_curp_basico() -> None:
    r = generar_curp_desde_datos(
        primer_apellido="Pérez",
        segundo_apellido="Ramírez",
        nombre="Luis",
        fecha_nacimiento=date(1982, 12, 23),
        sexo="H",
        estado_codigo="DF",
        char_homonimia="0",
    )
    assert r["valido"] is True
    assert r["curp_generada"] is not None
    # La CURP generada debe pasar validación estructural completa
    rv = validar_estructura(r["curp_generada"])
    assert rv["valido_estructura"] is True


def test_generar_curp_2000s_auto_letra_homonimia() -> None:
    r = generar_curp_desde_datos(
        primer_apellido="Robles",
        segundo_apellido="Martínez",
        nombre="Ana",
        fecha_nacimiento=date(2010, 3, 15),
        sexo="M",
        estado_codigo="JC",
    )
    assert r["valido"] is True
    # El char homonimia auto-asignado debe ser una letra (2000s)
    assert r["componentes"]["char_homonimia"].isalpha()


def test_generar_curp_rechaza_sexo_invalido() -> None:
    r = generar_curp_desde_datos(
        primer_apellido="X",
        segundo_apellido="Y",
        nombre="Z",
        fecha_nacimiento=date(2000, 1, 1),
        sexo="OTRO",
        estado_codigo="DF",
    )
    assert r["valido"] is False
    assert any("Sexo" in e for e in r["errores"])


def test_generar_curp_rechaza_estado_invalido() -> None:
    r = generar_curp_desde_datos(
        primer_apellido="X",
        segundo_apellido="Y",
        nombre="Z",
        fecha_nacimiento=date(2000, 1, 1),
        sexo="H",
        estado_codigo="ZZ",
    )
    assert r["valido"] is False


def test_generar_curp_extranjero_sin_segundo_apellido() -> None:
    """Extranjeros suelen no tener apellido materno — RENAPO pone X."""
    r = generar_curp_desde_datos(
        primer_apellido="Smith",
        segundo_apellido="",
        nombre="John",
        fecha_nacimiento=date(1990, 5, 5),
        sexo="H",
        estado_codigo="NE",
    )
    assert r["valido"] is True
    # La 3ra letra de la CURP (1ra del 2do apellido) debe ser X
    assert r["curp_generada"][2] == "X"
