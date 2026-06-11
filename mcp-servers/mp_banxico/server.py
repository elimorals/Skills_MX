"""mp-banxico — Tipos de cambio DOF y referencias económicas de Banxico.

Provee tipo de cambio FIX (USD/MXN, EUR/MXN, GBP/MXN, CAD/MXN, JPY/MXN),
TIIE 28, INPC, y UMA. Crítico para emitir CFDIs en moneda extranjera
(el SAT exige el TC del DOF del día hábil anterior).

Sin token funciona en modo simulado con valores plausibles fijos.
Para producción: BANXICO_TOKEN obtenido gratis en
https://www.banxico.org.mx/SieAPIRest/service/v1/token
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Local imports
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_banxico.client import BanxicoClient  # noqa: E402
from mp_banxico.holidays import is_business_day, previous_business_day  # noqa: E402
from mp_banxico.series import (  # noqa: E402
    INPC,
    TIIE_28,
    UMA_DIARIA,
    serie_for_par,
    supported_pares,
)
from shared.errors import McpError, ValidationError  # noqa: E402


# ---------- server init ----------

mcp = FastMCP("banxico_mcp")
_client = BanxicoClient()


# ---------- enums / shared models ----------

class Moneda(str, Enum):
    """Monedas soportadas para tipo de cambio contra MXN."""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    JPY = "JPY"


# ---------- input models ----------

class GetTcDofInput(BaseModel):
    """Input para get_tc_dof — TC oficial para una fecha específica."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    moneda: Moneda = Field(
        ...,
        description="Moneda origen (siempre se convierte contra MXN). Ej: 'USD', 'EUR'.",
    )
    fecha: str = Field(
        ...,
        description="Fecha objetivo en formato ISO 'YYYY-MM-DD'. Si cae en fin de semana o "
        "festivo bancario mexicano, el servidor automáticamente regresa el TC del "
        "último día hábil anterior y lo indica en 'fecha_ajustada'.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    @field_validator("fecha")
    @classmethod
    def fecha_parseable(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"Fecha inválida: {v}") from exc
        return v


class GetTcDiaHabilAnteriorInput(BaseModel):
    """Input para get_tc_dia_habil_anterior — el caso típico para CFDI."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    moneda: Moneda = Field(
        ...,
        description="Moneda origen contra MXN. Ej: 'USD'.",
    )
    fecha_referencia: Optional[str] = Field(
        default=None,
        description="Fecha de referencia ISO 'YYYY-MM-DD' (típicamente la fecha del CFDI). "
        "Por default es hoy. El TC retornado es el del último día hábil ESTRICTAMENTE "
        "anterior a esta fecha.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    @field_validator("fecha_referencia")
    @classmethod
    def fecha_parseable(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            date.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"Fecha inválida: {v}") from exc
        return v


class ConvertirMontoInput(BaseModel):
    """Input para convertir_monto — convierte entre MXN y otra moneda."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    monto: float = Field(
        ...,
        description="Monto a convertir (positivo). Ej: 10000.00.",
        gt=0,
    )
    de_moneda: Moneda | str = Field(
        ...,
        description="Moneda origen. Acepta cualquier código ISO 3 letras, pero solo "
        "{USD, EUR, GBP, CAD, JPY, MXN} están soportados.",
    )
    a_moneda: Moneda | str = Field(
        ...,
        description="Moneda destino. Mismas reglas que de_moneda.",
    )
    fecha: Optional[str] = Field(
        default=None,
        description="Fecha del TC a aplicar ('YYYY-MM-DD'). Por default usa el día hábil "
        "anterior a hoy (consistente con la regla SAT para CFDI).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    @field_validator("fecha")
    @classmethod
    def fecha_parseable(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            date.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"Fecha inválida: {v}") from exc
        return v


class GetReferenciaInput(BaseModel):
    """Input genérico para series no-FX (UMA, INPC, TIIE)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    fecha: Optional[str] = Field(
        default=None,
        description="Fecha de consulta ISO 'YYYY-MM-DD'. Si se omite, retorna el último "
        "valor publicado.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    @field_validator("fecha")
    @classmethod
    def fecha_parseable(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            date.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"Fecha inválida: {v}") from exc
        return v


# ---------- tool implementations ----------


@mcp.tool(
    name="banxico_get_tc_dof",
    annotations={
        "title": "TC oficial DOF para una fecha",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_get_tc_dof(params: GetTcDofInput) -> dict:
    """Obtiene el tipo de cambio FIX Banxico publicado en el DOF para una fecha específica.

    Útil para CFDIs en moneda extranjera y reportes históricos. Si la fecha
    solicitada no es día hábil mexicano (fin de semana o festivo bancario),
    el servidor regresa el TC del último día hábil anterior y lo indica en
    'fecha_ajustada' + 'fecha_consultada'.

    Args:
        params (GetTcDofInput):
            - moneda: USD | EUR | GBP | CAD | JPY
            - fecha: 'YYYY-MM-DD'

    Returns:
        dict con la siguiente estructura:
        {
            "moneda_origen": "USD",
            "moneda_destino": "MXN",
            "tipo_cambio": 18.5432,           # float
            "fecha_consultada": "YYYY-MM-DD",  # input original
            "fecha_aplicable": "YYYY-MM-DD",   # ajustada a día hábil si aplica
            "fecha_ajustada": false,           # true si se movió por feriado/fin de semana
            "razon_ajuste": null | "fin_de_semana" | "feriado_bancario",
            "serie": "SF63528",
            "fuente": "Banxico (DOF)" | "mock (...)",
            "simulated": false | true,
            "valido_para_cfdi": true,
            "advertencias": [...]
        }
    """
    try:
        fecha_solicitada = date.fromisoformat(params.fecha)
        fecha_aplicable, ajustada, razon = _resolve_business_day(fecha_solicitada)

        par = f"{params.moneda.value}/MXN"
        serie = serie_for_par(par)
        if serie is None:
            raise ValidationError(
                f"Par no soportado: {par}. Soportados: {', '.join(supported_pares())}",
                {"par": par},
            )

        obs = await _client.get_serie_value(serie.code, fecha_aplicable, cache_ttl_hours=24)

        return _format_tc_response(
            obs,
            moneda_origen=params.moneda.value,
            fecha_solicitada=fecha_solicitada,
            fecha_aplicable=fecha_aplicable,
            ajustada=ajustada,
            razon=razon,
            serie_code=serie.code,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="banxico_get_tc_dia_habil_anterior",
    annotations={
        "title": "TC del día hábil anterior (regla SAT para CFDI)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_get_tc_dia_habil_anterior(params: GetTcDiaHabilAnteriorInput) -> dict:
    """Retorna el TC oficial del día hábil INMEDIATAMENTE ANTERIOR a la fecha de referencia.

    Esta es la regla SAT para CFDIs en moneda extranjera (Anexo 20):
    se debe usar el TC publicado el día hábil previo al del comprobante.

    Args:
        params (GetTcDiaHabilAnteriorInput):
            - moneda: USD | EUR | GBP | CAD | JPY
            - fecha_referencia: 'YYYY-MM-DD' (default = hoy)

    Returns:
        Misma estructura que banxico_get_tc_dof, donde 'fecha_aplicable' es
        siempre el día hábil estricto anterior a 'fecha_consultada'.
    """
    try:
        if params.fecha_referencia:
            fecha_ref = date.fromisoformat(params.fecha_referencia)
        else:
            fecha_ref = datetime.now(timezone.utc).date()

        fecha_aplicable = previous_business_day(fecha_ref)

        par = f"{params.moneda.value}/MXN"
        serie = serie_for_par(par)
        if serie is None:
            raise ValidationError(
                f"Par no soportado: {par}",
                {"par": par},
            )

        obs = await _client.get_serie_value(serie.code, fecha_aplicable, cache_ttl_hours=24)
        return _format_tc_response(
            obs,
            moneda_origen=params.moneda.value,
            fecha_solicitada=fecha_ref,
            fecha_aplicable=fecha_aplicable,
            ajustada=True,
            razon="dia_habil_anterior",
            serie_code=serie.code,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="banxico_convertir_monto",
    annotations={
        "title": "Convertir monto entre MXN y otra moneda usando TC DOF",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_convertir_monto(params: ConvertirMontoInput) -> dict:
    """Convierte un monto entre MXN y otra moneda soportada usando el TC DOF aplicable.

    Acepta cualquier dirección (USD→MXN, MXN→USD, EUR→MXN, etc.) siempre que
    una de las monedas sea MXN. La conversión cross-currency (EUR→USD) NO
    está soportada — Banxico publica todos los TCs contra MXN.

    Args:
        params (ConvertirMontoInput):
            - monto: float positivo
            - de_moneda: código ISO 3 letras
            - a_moneda: código ISO 3 letras
            - fecha: ISO opcional (default = día hábil anterior a hoy)

    Returns:
        {
            "monto_original": 10000.00,
            "moneda_original": "USD",
            "monto_convertido": 185432.00,   # redondeado a 2 decimales
            "moneda_convertida": "MXN",
            "tipo_cambio": 18.5432,
            "fecha_tc": "YYYY-MM-DD",
            "direccion": "USD_to_MXN" | "MXN_to_USD",
            "fuente": "Banxico (DOF)" | "mock (...)",
            "simulated": false,
            "advertencias": [...]
        }
    """
    try:
        de = str(params.de_moneda).upper()
        a = str(params.a_moneda).upper()

        if de == a:
            raise ValidationError(
                f"de_moneda y a_moneda son iguales ({de}). Nada que convertir.",
                {"de_moneda": de, "a_moneda": a},
            )
        if de != "MXN" and a != "MXN":
            raise ValidationError(
                "Solo se soportan conversiones contra MXN. Para cross-currency, "
                "convierte primero a MXN y luego al destino.",
                {"de_moneda": de, "a_moneda": a},
            )

        # Resolve which non-MXN currency is involved
        moneda_extranjera = de if de != "MXN" else a
        try:
            Moneda(moneda_extranjera)
        except ValueError as exc:
            raise ValidationError(
                f"Moneda no soportada: {moneda_extranjera}. Soportadas: "
                f"{', '.join(m.value for m in Moneda)}, MXN.",
                {"moneda_no_soportada": moneda_extranjera},
            ) from exc

        # Resolve TC date
        if params.fecha:
            fecha_tc = date.fromisoformat(params.fecha)
        else:
            fecha_tc = previous_business_day(datetime.now(timezone.utc).date())

        # Ensure it's a business day (if user passed a non-business date, shift it)
        fecha_tc_aplicable, _, _ = _resolve_business_day(fecha_tc)

        par = f"{moneda_extranjera}/MXN"
        serie = serie_for_par(par)
        if serie is None:
            raise ValidationError(f"Par no soportado: {par}", {"par": par})

        obs = await _client.get_serie_value(serie.code, fecha_tc_aplicable, cache_ttl_hours=24)
        tc = obs["valor"]

        # Apply direction
        if de != "MXN" and a == "MXN":
            # foreign -> MXN: multiply
            monto_convertido = float(
                (Decimal(str(params.monto)) * Decimal(str(tc))).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            direccion = f"{de}_to_MXN"
        else:
            # MXN -> foreign: divide
            monto_convertido = float(
                (Decimal(str(params.monto)) / Decimal(str(tc))).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            direccion = f"MXN_to_{a}"

        return {
            "monto_original": params.monto,
            "moneda_original": de,
            "monto_convertido": monto_convertido,
            "moneda_convertida": a,
            "tipo_cambio": tc,
            "fecha_tc": obs["fecha"],
            "direccion": direccion,
            "serie": serie.code,
            "fuente": obs.get("fuente", "Banxico"),
            "simulated": obs.get("simulated", False),
            "advertencias": obs.get("advertencias", []),
        }
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="banxico_get_uma",
    annotations={
        "title": "Valor UMA diaria vigente",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_get_uma(params: GetReferenciaInput) -> dict:
    """Retorna el valor de la UMA (Unidad de Medida y Actualización) diaria.

    La UMA reemplaza al salario mínimo como referencia para multas, créditos,
    obligaciones, deducciones, etc. Se actualiza anualmente en febrero por INPC.

    Args:
        params (GetReferenciaInput):
            - fecha: ISO opcional (default = último valor publicado)

    Returns:
        {
            "valor_diario": 108.57,
            "valor_mensual": 3303.16,    # diario * 30.4
            "valor_anual": 39637.92,     # diario * 365
            "fecha_aplicable": "YYYY-MM-DD",
            "serie": "SP74660",
            "fuente": "...", "simulated": bool, "advertencias": [...]
        }
    """
    try:
        if params.fecha:
            fecha = date.fromisoformat(params.fecha)
            obs = await _client.get_serie_value(UMA_DIARIA.code, fecha, cache_ttl_hours=24 * 30)
        else:
            obs = await _client.get_serie_latest(UMA_DIARIA.code, cache_ttl_hours=24)

        diaria = obs["valor"]
        return {
            "valor_diario": diaria,
            "valor_mensual": round(diaria * 30.4, 2),
            "valor_anual": round(diaria * 365, 2),
            "fecha_aplicable": obs["fecha"],
            "serie": UMA_DIARIA.code,
            "fuente": obs.get("fuente", "Banxico"),
            "simulated": obs.get("simulated", False),
            "advertencias": obs.get("advertencias", []),
        }
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="banxico_get_inpc",
    annotations={
        "title": "INPC (Índice Nacional de Precios al Consumidor)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_get_inpc(params: GetReferenciaInput) -> dict:
    """Retorna el INPC vigente. Útil para indexación inflacionaria (rentas, contratos).

    El INPC se publica mensual. Si pasas una fecha intra-mes, retorna el INPC
    del mes correspondiente al primer dato disponible <= fecha.
    """
    try:
        if params.fecha:
            fecha = date.fromisoformat(params.fecha)
            obs = await _client.get_serie_value(INPC.code, fecha, cache_ttl_hours=24 * 30)
        else:
            obs = await _client.get_serie_latest(INPC.code, cache_ttl_hours=24)

        return {
            "inpc": obs["valor"],
            "fecha_aplicable": obs["fecha"],
            "serie": INPC.code,
            "fuente": obs.get("fuente", "Banxico"),
            "simulated": obs.get("simulated", False),
            "advertencias": obs.get("advertencias", []),
        }
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="banxico_get_tiie_28",
    annotations={
        "title": "TIIE a 28 días",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def banxico_get_tiie_28(params: GetReferenciaInput) -> dict:
    """Retorna la TIIE a 28 días vigente. Referencia para créditos comerciales en MXN."""
    try:
        if params.fecha:
            fecha = date.fromisoformat(params.fecha)
            obs = await _client.get_serie_value(TIIE_28.code, fecha, cache_ttl_hours=24)
        else:
            obs = await _client.get_serie_latest(TIIE_28.code, cache_ttl_hours=6)

        return {
            "tiie_28": obs["valor"],
            "fecha_aplicable": obs["fecha"],
            "serie": TIIE_28.code,
            "fuente": obs.get("fuente", "Banxico"),
            "simulated": obs.get("simulated", False),
            "advertencias": obs.get("advertencias", []),
        }
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="banxico_listar_monedas_soportadas",
    annotations={
        "title": "Lista de monedas soportadas para conversión MXN",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def banxico_listar_monedas_soportadas() -> dict:
    """Retorna la lista de pares de monedas para los que este MCP puede obtener TC.

    No requiere parámetros. No hace llamada a red. Útil para descubrir
    capacidades antes de invocar tools de conversión.
    """
    pares = []
    for par in supported_pares():
        serie = serie_for_par(par)
        if serie:
            pares.append(
                {
                    "par": par,
                    "moneda_origen": par.split("/")[0],
                    "moneda_destino": par.split("/")[1],
                    "serie": serie.code,
                    "descripcion": serie.label,
                }
            )
    return {
        "pares_soportados": pares,
        "fuente": "Banxico SIE",
        "advertencias": [
            "Solo soportamos conversiones contra MXN. Para cross-currency (ej. USD→EUR), "
            "convierte primero a MXN y luego a destino."
        ],
    }


# ---------- formatting helpers ----------


def _resolve_business_day(fecha: date) -> tuple[date, bool, str | None]:
    """Si `fecha` no es día hábil mexicano, retorna el anterior.

    Retorna: (fecha_aplicable, ajustada, razon)
    """
    if is_business_day(fecha):
        return fecha, False, None
    # Determine if weekend vs holiday for the razon label
    if fecha.weekday() >= 5:
        razon = "fin_de_semana"
    else:
        razon = "feriado_bancario"
    return previous_business_day(fecha + _one_day()), True, razon


def _one_day():
    """Construct timedelta(days=1) without polluting the top-level imports."""
    from datetime import timedelta

    return timedelta(days=1)


def _format_tc_response(
    obs: dict,
    *,
    moneda_origen: str,
    fecha_solicitada: date,
    fecha_aplicable: date,
    ajustada: bool,
    razon: str | None,
    serie_code: str,
) -> dict:
    """Build the consistent TC response envelope."""
    return {
        "moneda_origen": moneda_origen,
        "moneda_destino": "MXN",
        "tipo_cambio": obs["valor"],
        "fecha_consultada": fecha_solicitada.isoformat(),
        "fecha_aplicable": obs["fecha"],
        "fecha_ajustada": ajustada,
        "razon_ajuste": razon,
        "serie": serie_code,
        "fuente": obs.get("fuente", "Banxico (DOF)"),
        "simulated": obs.get("simulated", False),
        "valido_para_cfdi": not obs.get("simulated", False),
        "advertencias": obs.get("advertencias", []),
    }


# ---------- entry point ----------


def main() -> None:
    """Run the FastMCP server over stdio (default)."""
    mcp.run()


if __name__ == "__main__":
    main()
