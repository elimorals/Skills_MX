"""Tests para mp_aspel_contpaqi/export_parser.py."""

from __future__ import annotations

from decimal import Decimal

from mp_aspel_contpaqi.export_parser import (
    _to_decimal,
    parsear_csv_balanza,
    parsear_csv_catalogo_cuentas,
    parsear_csv_polizas,
)
from mp_aspel_contpaqi.tests.conftest import (
    CSV_BALANZA_DEMO,
    CSV_CATALOGO_DEMO,
    CSV_POLIZAS_DEMO,
)


# ---------- _to_decimal ----------


def test_to_decimal_simple() -> None:
    assert _to_decimal("1234.56") == Decimal("1234.56")


def test_to_decimal_con_signo_dolar() -> None:
    assert _to_decimal("$1,234.56") == Decimal("1234.56")


def test_to_decimal_vacio() -> None:
    assert _to_decimal("") == Decimal("0")
    assert _to_decimal(None) == Decimal("0")


def test_to_decimal_separador_miles() -> None:
    assert _to_decimal("1,234,567.89") == Decimal("1234567.89")


def test_to_decimal_coma_decimal_europeo() -> None:
    """Coma con max 2 dígitos a la derecha = decimal estilo europeo."""
    assert _to_decimal("1234,56") == Decimal("1234.56")


def test_to_decimal_invalido_devuelve_cero() -> None:
    assert _to_decimal("texto") == Decimal("0")


# ---------- parsear_csv_polizas ----------


def test_parsear_polizas_agrupa_por_numero() -> None:
    polizas = parsear_csv_polizas(CSV_POLIZAS_DEMO)
    assert len(polizas) == 2
    nums = {p["numero"] for p in polizas}
    assert nums == {"D-001", "I-002"}


def test_parsear_polizas_lineas_correctas() -> None:
    polizas = parsear_csv_polizas(CSV_POLIZAS_DEMO)
    d001 = next(p for p in polizas if p["numero"] == "D-001")
    assert len(d001["lineas"]) == 3
    # Debe estar balanceada
    assert d001["balanceada"] is True
    assert d001["total_cargos"] == "34800.00"
    assert d001["total_abonos"] == "34800.00"


def test_parsear_polizas_tipo_y_concepto() -> None:
    polizas = parsear_csv_polizas(CSV_POLIZAS_DEMO)
    i002 = next(p for p in polizas if p["numero"] == "I-002")
    assert i002["tipo"] == "INGRESOS"
    assert "Tech Demo" in i002["concepto"]


def test_parsear_polizas_vacio() -> None:
    assert parsear_csv_polizas("") == []
    assert parsear_csv_polizas("   ") == []


def test_parsear_polizas_punto_y_coma_delimiter() -> None:
    """Algunos exports usan ';' como delimitador."""
    csv = """Numero;Fecha;Tipo;Concepto;Cuenta;Debe;Haber
A-001;2026-03-01;DIARIO;Demo;102-001;1000;0
A-001;2026-03-01;DIARIO;Demo;401-001;0;1000
"""
    polizas = parsear_csv_polizas(csv)
    assert len(polizas) == 1
    assert polizas[0]["balanceada"] is True


def test_parsear_polizas_acepta_columnas_extra() -> None:
    csv = """Numero,Fecha,Tipo,Concepto,Cuenta,Debe,Haber,Extra,Notas
A-001,2026-03-01,DIARIO,Demo,102-001,1000,0,ignorar,esto
A-001,2026-03-01,DIARIO,Demo,401-001,0,1000,ignorar,esto
"""
    polizas = parsear_csv_polizas(csv)
    assert len(polizas) == 1


# ---------- parsear_csv_balanza ----------


def test_parsear_balanza_ok() -> None:
    cuentas = parsear_csv_balanza(CSV_BALANZA_DEMO)
    assert len(cuentas) == 3
    bancos = next(c for c in cuentas if c["cuenta"] == "102-001")
    assert bancos["nombre"] == "Bancos BBVA"
    assert bancos["saldo_inicial"] == "350000.00"
    assert bancos["saldo_final"] == "373200.00"


def test_parsear_balanza_vacio() -> None:
    assert parsear_csv_balanza("") == []


def test_parsear_balanza_acentos_en_headers() -> None:
    csv = """Cuenta,Descripción,Saldo Inicial,Cargos,Abonos,Saldo Final
102-001,Bancos,100,50,30,120
"""
    cuentas = parsear_csv_balanza(csv)
    assert len(cuentas) == 1
    assert cuentas[0]["nombre"] == "Bancos"


# ---------- parsear_csv_catalogo_cuentas ----------


def test_parsear_catalogo_ok() -> None:
    cuentas = parsear_csv_catalogo_cuentas(CSV_CATALOGO_DEMO)
    assert len(cuentas) == 3
    bancos = next(c for c in cuentas if c["cuenta"] == "102-001")
    assert bancos["codigo_sat"] == "102"
    assert bancos["naturaleza"] == "DEUDORA"


def test_parsear_catalogo_vacio() -> None:
    assert parsear_csv_catalogo_cuentas("") == []
