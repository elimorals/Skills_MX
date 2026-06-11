"""End-to-end tests para los tools FastMCP de banxico_cep."""

from __future__ import annotations

from datetime import date

import pytest

from mp_banxico_cep.server import (
    ClabeInput,
    ClaveRastreoInput,
    CodigoBancoInput,
    GenerarCepInput,
    banxico_cep_consultar_pago_por_clave,
    banxico_cep_decodificar_clabe,
    banxico_cep_descargar_pdf,
    banxico_cep_generar_cep,
    banxico_cep_listar_bancos,
    banxico_cep_listar_catalogos,
    banxico_cep_lookup_banco,
    banxico_cep_parsear_clave_rastreo,
    banxico_cep_validar_cep,
    banxico_cep_validar_clabe,
)
from mp_banxico_cep.tests.conftest import make_valid_clabe


# ---------- locales ----------


@pytest.mark.asyncio
async def test_validar_clabe_ok() -> None:
    clabe = make_valid_clabe("01218000123456789")
    r = await banxico_cep_validar_clabe(ClabeInput(clabe=clabe))
    assert r["valida"] is True
    assert r["banco_nombre"] == "BBVA México"


@pytest.mark.asyncio
async def test_decodificar_clabe_componentes() -> None:
    clabe = make_valid_clabe("07240000012345678")  # Banorte, plaza 400
    r = await banxico_cep_decodificar_clabe(ClabeInput(clabe=clabe))
    assert r["banco_codigo"] == "072"
    assert r["banco_nombre"] == "Banorte"
    assert r["plaza_codigo"] == "400"


@pytest.mark.asyncio
async def test_parsear_clave_rastreo_bbva() -> None:
    r = await banxico_cep_parsear_clave_rastreo(
        ClaveRastreoInput(clave_rastreo="MBAN0100123456789012")
    )
    assert r["formato_valido"] is True
    assert r["emisor_probable"] == "BBVA México"


@pytest.mark.asyncio
async def test_lookup_banco_conocido() -> None:
    r = await banxico_cep_lookup_banco(CodigoBancoInput(codigo="012"))
    assert r["nombre"] == "BBVA México"


@pytest.mark.asyncio
async def test_lookup_banco_desconocido() -> None:
    r = await banxico_cep_lookup_banco(CodigoBancoInput(codigo="999"))
    assert "error" in r


# ---------- remotos (mock) ----------


@pytest.mark.asyncio
async def test_generar_cep_mock() -> None:
    r = await banxico_cep_generar_cep(
        GenerarCepInput(
            clave_rastreo="MBAN0100EJEMPLO",
            fecha_operacion=date(2026, 3, 15),
            banco_emisor="012",
            banco_receptor="002",
            monto=11600.00,
        )
    )
    assert r["simulated"] is True
    assert r["cep_disponible"] is True
    assert r["banco_emisor"]["clave"] == "012"


@pytest.mark.asyncio
async def test_generar_cep_banco_invalido_devuelve_error() -> None:
    r = await banxico_cep_generar_cep(
        GenerarCepInput(
            clave_rastreo="MBAN0100EJEMPLO",
            fecha_operacion=date(2026, 3, 15),
            banco_emisor="999",
            banco_receptor="002",
            monto=100.0,
        )
    )
    # ValidationError → to_dict() pone code=validation_error
    assert r.get("code") == "validation_error" or "error" in r


@pytest.mark.asyncio
async def test_validar_cep_mock() -> None:
    r = await banxico_cep_validar_cep(
        ClaveRastreoInput(clave_rastreo="MBAN0100VALIDARME")
    )
    assert r["simulated"] is True
    assert "existe_en_banxico" in r


@pytest.mark.asyncio
async def test_descargar_pdf_mock() -> None:
    r = await banxico_cep_descargar_pdf(
        GenerarCepInput(
            clave_rastreo="MBAN0100PDF",
            fecha_operacion=date(2026, 3, 15),
            banco_emisor="012",
            banco_receptor="002",
            monto=100.0,
        )
    )
    assert r["simulated"] is True
    assert "pdf_path" in r


@pytest.mark.asyncio
async def test_consultar_pago_por_clave_mock() -> None:
    r = await banxico_cep_consultar_pago_por_clave(
        ClaveRastreoInput(clave_rastreo="MBAN0100CONSULTA")
    )
    assert r["simulated"] is True


# ---------- catálogos ----------


@pytest.mark.asyncio
async def test_listar_bancos_completo() -> None:
    r = await banxico_cep_listar_bancos()
    assert r["total"] >= 80  # bancos + fintechs
    assert "002" in r["todos"]


@pytest.mark.asyncio
async def test_listar_catalogos_offline() -> None:
    r = await banxico_cep_listar_catalogos()
    assert "tipo_operacion_spei" in r
    assert "estado_cep" in r


# ---------- validation ----------


def test_clabe_input_min_length() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ClabeInput(clabe="")


def test_codigo_banco_max_3() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CodigoBancoInput(codigo="1234")


def test_generar_cep_monto_negativo_rechazado() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        GenerarCepInput(
            clave_rastreo="MBAN0100",
            fecha_operacion=date(2026, 1, 1),
            banco_emisor="012",
            banco_receptor="002",
            monto=-1.0,
        )
