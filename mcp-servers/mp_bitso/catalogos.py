"""Catálogos Bitso (exchange cripto-fiat México).

Notas:
- Bitso es el exchange dominante en MX para fiat MXN ↔ crypto.
- API REST pública: https://api.bitso.com/v3/
- API REST privada (auth HMAC): https://api.bitso.com/v3/
- Sandbox: https://stage.bitso.com/api/v3/ (testnet)
"""

from __future__ import annotations


# ---------- Order Books / Trading pairs ----------

# Pares spot disponibles (parcial — Bitso opera ~30 pares)
TRADING_PAIRS: dict[str, str] = {
    "btc_mxn": "Bitcoin / Peso Mexicano",
    "eth_mxn": "Ethereum / Peso Mexicano",
    "xrp_mxn": "Ripple / Peso Mexicano",
    "usdt_mxn": "Tether USD / Peso Mexicano",
    "usdc_mxn": "USD Coin / Peso Mexicano",
    "mxn_dai": "DAI / Peso Mexicano",
    "ada_mxn": "Cardano / Peso Mexicano",
    "sol_mxn": "Solana / Peso Mexicano",
    "matic_mxn": "Polygon / Peso Mexicano",
    "ltc_mxn": "Litecoin / Peso Mexicano",
    "bch_mxn": "Bitcoin Cash / Peso Mexicano",
    "btc_usd": "Bitcoin / USD",
    "eth_usd": "Ethereum / USD",
    "btc_ars": "Bitcoin / Peso Argentino",
    "btc_brl": "Bitcoin / Real Brasileño",
}


# ---------- Tipos de operación ----------

OPERATION_TYPES: dict[str, str] = {
    "trade": "Compraventa spot (mercado o limit)",
    "fee": "Comisión cobrada por Bitso",
    "deposit_fiat": "Depósito fiat (SPEI, etc.)",
    "deposit_crypto": "Depósito cripto on-chain",
    "withdrawal_fiat": "Retiro fiat (SPEI)",
    "withdrawal_crypto": "Retiro cripto on-chain",
    "rewards": "Recompensa/staking",
    "referral": "Bono por referido",
}


# ---------- Status de funding (depósitos/retiros) ----------

FUNDING_STATUS: dict[str, str] = {
    "pending": "En proceso — esperando confirmaciones",
    "in_progress": "Confirmaciones parciales",
    "complete": "Completado",
    "failed": "Fallido",
    "cancelled": "Cancelado",
}


# ---------- Side de orden ----------

ORDER_SIDE: dict[str, str] = {
    "buy": "Compra (gastar quote currency, recibir base)",
    "sell": "Venta (gastar base currency, recibir quote)",
}


# ---------- Order Type ----------

ORDER_TYPE: dict[str, str] = {
    "market": "Orden a precio de mercado (inmediata)",
    "limit": "Orden con precio límite (queda en book)",
}


# ---------- Order Status ----------

ORDER_STATUS: dict[str, str] = {
    "open": "Abierta en el book",
    "partial-fill": "Parcialmente ejecutada",
    "completed": "Ejecutada completamente",
    "cancelled": "Cancelada por el usuario",
}


# ---------- Métodos de depósito fiat MX ----------

DEPOSIT_METHODS_MX: dict[str, str] = {
    "spei": "Transferencia SPEI desde banco MX (gratis)",
    "oxxo": "Depósito en efectivo OXXO (comisión variable)",
    "international_wire": "Transferencia internacional SWIFT (USD)",
}


# ---------- Implicaciones fiscales MX (referencia rápida) ----------

FISCAL_INFO_MX: dict[str, str] = {
    "ganancia_capital_isr": "Ganancia por venta de cripto se acumula a ingresos del ejercicio (Art. 142 LISR — otros ingresos)",
    "obligacion_informativa": "Bitso reporta operaciones a UIF si > $56,000 USD/mes (Ley Antilavado)",
    "iva": "Compra/venta de cripto NO causa IVA (Art. 14 LIVA)",
    "isr_retencion_bitso": "Bitso NO retiene ISR — el contribuyente debe declarar",
    "regimen_sugerido": "RESICO PF / PFAE — cripto = ingresos otros (Art. 17 LISR)",
}


# ---------- helpers ----------


def is_trading_pair(pair: str) -> bool:
    return pair in TRADING_PAIRS


def is_terminal_status(status: str) -> bool:
    return status in {"complete", "failed", "cancelled"}
