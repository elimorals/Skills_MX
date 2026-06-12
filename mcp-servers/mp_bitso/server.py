"""mp_bitso — MCP para exchange Bitso (cripto-fiat MX).

10 tools:
- bitso_get_ticker (público, cache 30s)
- bitso_get_order_book (público)
- bitso_list_available_books (público)
- bitso_get_account_status (auth)
- bitso_get_balance (auth)
- bitso_get_fees (auth)
- bitso_get_ledger (auth, historial — útil reporte fiscal)
- bitso_list_fundings (auth, depósitos)
- bitso_list_withdrawals (auth, retiros)
- bitso_list_open_orders (auth)
- bitso_listar_catalogos (discovery)
- bitso_calcular_isr_cripto_mx (utility local — implicaciones fiscales)

Mock-first sin BITSO_API_KEY + BITSO_API_SECRET. Path sandbox vía
BITSO_ENV=sandbox.

⚠ Cripto en MX se acumula como "otros ingresos" Art. 142 LISR.
Bitso NO retiene ISR. El contribuyente declara.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_bitso.catalogos import (  # noqa: E402
    DEPOSIT_METHODS_MX,
    FISCAL_INFO_MX,
    FUNDING_STATUS,
    OPERATION_TYPES,
    ORDER_SIDE,
    ORDER_STATUS,
    ORDER_TYPE,
    TRADING_PAIRS,
)
from mp_bitso.client import BitsoClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("bitso_mcp")
_client = BitsoClient()


# ---------- input models ----------


class BookInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book: str = Field("btc_mxn", description="Trading pair (ej. btc_mxn, eth_mxn, usdt_mxn).")


class OrderBookInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book: str = Field("btc_mxn")
    aggregate: bool = Field(True, description="Agregar órdenes por precio.")


class LedgerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operations: Optional[str] = Field(
        None,
        description="Comma-separated: fundings,withdrawals,trades,fees,rewards",
    )
    marker: Optional[str] = None
    limit: int = Field(25, ge=1, le=100)


class LimitInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(25, ge=1, le=100)


class CalculoIsrInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ganancia_total_mxn: float = Field(..., ge=0, description="Ganancia neta del año por operaciones cripto.")
    otros_ingresos_anuales_mxn: float = Field(
        0.0, ge=0,
        description="Otros ingresos acumulables del ejercicio (sueldos, honorarios, etc.).",
    )
    regimen: Literal["RESICO_PF", "PFAE", "GENERAL"] = "PFAE"


# ---------- tools públicos ----------


@mcp.tool(
    annotations={
        "title": "Ticker (precio actual) de un par",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_get_ticker(args: BookInput) -> dict:
    """Precio actual de un trading pair (last, high, low, ask, bid, volume).

    Cache 30s. Útil para snapshot de mercado sin spam de API.
    """
    try:
        return await _client.get_ticker(args.book)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Order book (bids + asks)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_get_order_book(args: OrderBookInput) -> dict:
    """Profundidad del mercado: precios y volúmenes en bid/ask."""
    try:
        return await _client.get_order_book(args.book, args.aggregate)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Listar pares disponibles en Bitso",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_list_available_books() -> dict:
    """Todos los pares con min/max amounts."""
    try:
        return await _client.list_available_books()
    except McpError as exc:
        return exc.to_dict()


# ---------- tools con auth ----------


@mcp.tool(
    annotations={
        "title": "Status de la cuenta (límites, verificación, país)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_get_account_status() -> dict:
    """Status: límites diarios, nivel verificación, país. Sin auth → mock."""
    try:
        return await _client.get_account_status()
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Balances de todas las currencies (MXN, BTC, ETH, USDT, etc.)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_get_balance() -> dict:
    """Balance por currency: available, locked, total."""
    try:
        return await _client.get_balance()
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Comisiones por par",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_get_fees() -> dict:
    """Maker fee + taker fee por trading pair."""
    try:
        return await _client.get_fees()
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Ledger (historial movimientos) — útil para reporte fiscal",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_get_ledger(args: LedgerInput) -> dict:
    """Historial completo de movimientos.

    Filtros: operations=trades,fees,fundings,withdrawals,rewards.
    Para reporte fiscal anual: filtrar trades + fees.
    """
    try:
        return await _client.get_ledger(
            operations=args.operations or "",
            marker=args.marker,
            limit=args.limit,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Listar depósitos (fiat + crypto)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_list_fundings(args: LimitInput) -> dict:
    """Depósitos recibidos. Útil para conciliar SPEI entrante."""
    try:
        return await _client.list_fundings(args.limit)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Listar retiros",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_list_withdrawals(args: LimitInput) -> dict:
    """Retiros realizados (fiat o crypto)."""
    try:
        return await _client.list_withdrawals(args.limit)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Listar órdenes abiertas en el book",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bitso_list_open_orders() -> dict:
    """Órdenes limit aún abiertas (no ejecutadas)."""
    try:
        return await _client.list_open_orders()
    except McpError as exc:
        return exc.to_dict()


# ---------- utility local (sin red) ----------


@mcp.tool(
    annotations={
        "title": "Calcular ISR sobre ganancias cripto MX (Art. 142 LISR)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def bitso_calcular_isr_cripto_mx(args: CalculoIsrInput) -> dict:
    """Calcula ISR aproximado sobre ganancias cripto del año.

    ⚠ Tarifa Art. 96 LISR 2026 puede estar desactualizada. Validar con contador.

    Lógica básica:
    - RESICO_PF: tasa fija ladder (1.0%-2.5%)
    - PFAE / GENERAL: tarifa Art. 96 LISR progresiva
    - Cripto se acumula a otros ingresos del ejercicio
    """
    total_acumulable = args.ganancia_total_mxn + args.otros_ingresos_anuales_mxn

    if args.regimen == "RESICO_PF":
        # Tasas RESICO PF 2025 (validar 2026)
        if total_acumulable <= 25_000 * 12:
            tasa = 0.010
        elif total_acumulable <= 50_000 * 12:
            tasa = 0.011
        elif total_acumulable <= 83_333 * 12:
            tasa = 0.015
        elif total_acumulable <= 208_333 * 12:
            tasa = 0.020
        else:
            tasa = 0.025
        isr = args.ganancia_total_mxn * tasa
        razon = f"RESICO PF tasa {tasa*100:.1f}% sobre ganancia cripto"
    else:
        # Tarifa Art. 96 LISR — simplificada (rangos típicos 2025; validar 2026)
        # Esto es REFERENCIAL, no autoritativo
        if total_acumulable <= 8_952.49 * 12:
            tasa_marg = 0.0192
        elif total_acumulable <= 75_984.55 * 12:
            tasa_marg = 0.0640
        elif total_acumulable <= 133_536.07 * 12:
            tasa_marg = 0.1088
        elif total_acumulable <= 155_229.80 * 12:
            tasa_marg = 0.1600
        elif total_acumulable <= 185_852.57 * 12:
            tasa_marg = 0.1792
        elif total_acumulable <= 374_837.88 * 12:
            tasa_marg = 0.2136
        else:
            tasa_marg = 0.3500
        isr = args.ganancia_total_mxn * tasa_marg
        razon = f"Tarifa Art. 96 LISR — tasa marginal estimada {tasa_marg*100:.2f}%"

    return {
        "ganancia_cripto_mxn": args.ganancia_total_mxn,
        "otros_ingresos_acumulables_mxn": args.otros_ingresos_anuales_mxn,
        "total_acumulable_mxn": total_acumulable,
        "regimen": args.regimen,
        "isr_aproximado_mxn": round(isr, 2),
        "razon_calculo": razon,
        "fuente_legal": "Art. 142 LISR (otros ingresos) + Art. 96/Art. 113 LISR (tarifas)",
        "advertencia": (
            "Cálculo REFERENCIAL. Tarifas 2026 pueden haber cambiado por inflación. "
            "Bitso NO retiene ISR — debes declararlo. "
            "Validar con contador antes de pagar."
        ),
        "vigencia_validada": False,
    }


# ---------- catálogos ----------


@mcp.tool(
    annotations={
        "title": "Catálogos Bitso: pares, status, métodos depósito, info fiscal MX",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def bitso_listar_catalogos() -> dict:
    """Discovery offline de pares y info fiscal."""
    return {
        "trading_pairs": TRADING_PAIRS,
        "operation_types": OPERATION_TYPES,
        "funding_status": FUNDING_STATUS,
        "order_side": ORDER_SIDE,
        "order_type": ORDER_TYPE,
        "order_status": ORDER_STATUS,
        "deposit_methods_mx": DEPOSIT_METHODS_MX,
        "fiscal_info_mx": FISCAL_INFO_MX,
        "nota": (
            "Bitso opera ~30 pares cripto-fiat. Para reporte fiscal MX usar "
            "bitso_get_ledger filtrando operations=trades,fees. "
            "Cripto = otros ingresos Art. 142 LISR — Bitso NO retiene ISR."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
