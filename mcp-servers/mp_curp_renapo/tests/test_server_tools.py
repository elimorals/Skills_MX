"""End-to-end tests para los tools FastMCP del MCP curp_renapo."""

from __future__ import annotations

from datetime import date

import pytest

from mp_curp_renapo.server import (
    CurpInput,
    CurpListInput,
    GenerarCurpInput,
    Sexo,
    curp_consultar_renapo,
    curp_derivar_estado,
    curp_derivar_fecha_nacimiento,
    curp_derivar_sexo,
    curp_descargar_constancia_renapo,
    curp_generar_desde_datos,
    curp_listar_catalogos,
    curp_validar_estructura,
    curp_validar_lote,
)


@pytest.mark.asyncio
async def test_validar_estructura_ok() -> None:
    r = await curp_validar_estructura(CurpInput(curp="PERZ821223HDFRRL09"))
    assert r["valido_estructura"] is True


@pytest.mark.asyncio
async def test_validar_estructura_normaliza_input() -> None:
    """Espacios y minúsculas deben normalizarse antes de validar."""
    r = await curp_validar_estructura(CurpInput(curp="  perz821223hdfrrl09  "))
    assert r["valido_estructura"] is True


@pytest.mark.asyncio
async def test_derivar_fecha_returns_iso_string() -> None:
    r = await curp_derivar_fecha_nacimiento(CurpInput(curp="PERZ821223HDFRRL09"))
    assert r["fecha_nacimiento"] == "1982-12-23"
    assert r["siglo"] == 1900


@pytest.mark.asyncio
async def test_derivar_sexo_h() -> None:
    r = await curp_derivar_sexo(CurpInput(curp="PERZ821223HDFRRL09"))
    assert r["sexo"] == "H"
    assert r["descripcion"] == "Hombre"


@pytest.mark.asyncio
async def test_derivar_estado_df() -> None:
    r = await curp_derivar_estado(CurpInput(curp="PERZ821223HDFRRL09"))
    assert r["estado_codigo"] == "DF"
    assert r["estado_nombre"] == "Ciudad de México"


@pytest.mark.asyncio
async def test_validar_lote_separa_buenas_y_malas() -> None:
    r = await curp_validar_lote(
        CurpListInput(curps=["PERZ821223HDFRRL09", "BASURA"])
    )
    assert r["total"] == 2
    assert r["validos"] == 1
    assert r["invalidos"] == 1


@pytest.mark.asyncio
async def test_generar_curp_desde_datos_redondea_a_curp_valida() -> None:
    r = await curp_generar_desde_datos(
        GenerarCurpInput(
            primer_apellido="Pérez",
            segundo_apellido="Ramírez",
            nombre="Luis",
            fecha_nacimiento=date(1982, 12, 23),
            sexo=Sexo.H,
            estado_codigo="DF",
            char_homonimia="0",
        )
    )
    assert r["valido"] is True
    # Auto-validar la CURP generada
    rv = await curp_validar_estructura(CurpInput(curp=r["curp_generada"]))
    assert rv["valido_estructura"] is True


@pytest.mark.asyncio
async def test_consultar_renapo_mock() -> None:
    r = await curp_consultar_renapo(CurpInput(curp="PERZ821223HDFRRL09"))
    assert r["simulated"] is True
    assert r["estado_renapo"] == "VIGENTE"


@pytest.mark.asyncio
async def test_consultar_renapo_curp_invalida_devuelve_error() -> None:
    r = await curp_consultar_renapo(CurpInput(curp="BASURA"))
    # ValidationError → to_dict() pone code=validation_error
    assert "error" in r or "code" in r


@pytest.mark.asyncio
async def test_descargar_constancia_mock() -> None:
    r = await curp_descargar_constancia_renapo(CurpInput(curp="PERZ821223HDFRRL09"))
    assert r["simulated"] is True
    assert "PERZ821223HDFRRL09" in r["constancia_pdf_path"]


@pytest.mark.asyncio
async def test_listar_catalogos_offline() -> None:
    r = await curp_listar_catalogos()
    assert "estados" in r
    assert "sexo" in r
    assert "DF" in r["estados"]
    assert "NE" in r["estados"]  # extranjeros


# ---------- validation errors ----------


def test_curp_input_min_length() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CurpInput(curp="")


def test_lote_min_un_curp() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CurpListInput(curps=[])


def test_lote_max_500() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CurpListInput(curps=["A"] * 501)


def test_estado_codigo_2_chars() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        GenerarCurpInput(
            primer_apellido="X",
            nombre="Y",
            fecha_nacimiento=date(2000, 1, 1),
            sexo=Sexo.H,
            estado_codigo="DFG",
        )
