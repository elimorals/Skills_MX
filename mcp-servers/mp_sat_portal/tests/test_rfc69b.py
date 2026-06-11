"""Tests para mp_sat_portal/rfc69b.py — parseo CSVs públicos."""

from __future__ import annotations

from mp_sat_portal.rfc69b import (
    _clasificar_estado_69b,
    buscar_rfc_en_lista,
    parsear_csv_69_incumplidos,
    parsear_csv_69b,
)


CSV_69B_DEFINITIVOS = """RFC,Nombre del Contribuyente,Situación del Contribuyente,Número y Fecha del Oficio Global de Presunción
EFD850101001,FACTURADORA DEMO SA DE CV,Definitivo,500-05-2024-12345 del 10-Oct-2024
EFD850202002,FACTURAS FALSAS SA,Definitivo,500-05-2024-67890 del 15-Nov-2024
"""

CSV_69B_PRESUNTOS = """RFC,Nombre del Contribuyente,Situación del Contribuyente,Número y Fecha del Oficio Global de Presunción
EFD900301001,PRESUNTA SA DE CV,Presunto,500-05-2025-11111 del 01-Mar-2025
"""

CSV_69_INCUMPLIDOS = """RFC,Nombre,Supuesto,Entidad Federativa
INC900101001,INCUMPLIDO DOMICILIO,No localizado,CIUDAD DE MEXICO
INC910202002,INCUMPLIDO CREDITO,Crédito firme,JALISCO
"""


def test_parsear_csv_69b_definitivos_ok() -> None:
    regs = parsear_csv_69b(CSV_69B_DEFINITIVOS)
    assert len(regs) == 2
    assert regs[0]["rfc"] == "EFD850101001"
    assert regs[0]["estado_69b"] == "DEFINITIVO"
    assert regs[1]["rfc"] == "EFD850202002"


def test_parsear_csv_69b_presuntos_ok() -> None:
    regs = parsear_csv_69b(CSV_69B_PRESUNTOS)
    assert len(regs) == 1
    assert regs[0]["estado_69b"] == "PRESUNTO"


def test_parsear_csv_69b_vacio() -> None:
    assert parsear_csv_69b("") == []
    assert parsear_csv_69b("   \n   ") == []


def test_parsear_csv_69b_rfc_corto_se_ignora() -> None:
    csv = "RFC,Nombre,Situación del Contribuyente\nABC,Demo,Definitivo\n"
    regs = parsear_csv_69b(csv)
    assert regs == []


def test_parsear_csv_69_incumplidos_ok() -> None:
    regs = parsear_csv_69_incumplidos(CSV_69_INCUMPLIDOS)
    assert len(regs) == 2
    assert regs[0]["rfc"] == "INC900101001"
    assert "no localizado" in regs[0]["supuesto"].lower()
    assert regs[0]["entidad"] == "CIUDAD DE MEXICO"


def test_buscar_rfc_encontrado() -> None:
    regs = parsear_csv_69b(CSV_69B_DEFINITIVOS)
    found = buscar_rfc_en_lista("efd850101001", regs)
    assert found is not None
    assert found["rfc"] == "EFD850101001"


def test_buscar_rfc_no_encontrado() -> None:
    regs = parsear_csv_69b(CSV_69B_DEFINITIVOS)
    assert buscar_rfc_en_lista("ZZZ999999999", regs) is None


def test_clasificar_estado_69b_variantes() -> None:
    assert _clasificar_estado_69b("Definitivo") == "DEFINITIVO"
    assert _clasificar_estado_69b("PRESUNTO") == "PRESUNTO"
    assert _clasificar_estado_69b("Desvirtuado") == "DESVIRTUADO"
    assert _clasificar_estado_69b("Sentencia Favorable") == "SENTENCIA_FAVORABLE"
    assert _clasificar_estado_69b("texto raro") == "PRESUNTO"  # fallback conservador


def test_parsear_csv_69b_con_acentos_en_headers() -> None:
    csv = (
        "RFC,Nombre del Contribuyente,Situación del Contribuyente\n"
        "ACE850101001,ACENTOS SA,Definitivo\n"
    )
    regs = parsear_csv_69b(csv)
    assert len(regs) == 1
    assert regs[0]["rfc"] == "ACE850101001"


def test_parsear_csv_69b_tab_delimited() -> None:
    csv = (
        "RFC\tNombre del Contribuyente\tSituación del Contribuyente\n"
        "TAB850101001\tTAB DEMO SA\tDefinitivo\n"
    )
    regs = parsear_csv_69b(csv)
    assert len(regs) == 1
    assert regs[0]["estado_69b"] == "DEFINITIVO"
