---
name: tracking-wallets-self-custody
description: Reconstruye historial de operaciones desde wallets self-custody (MetaMask, Ledger, Trust Wallet, Phantom) usando blockchain explorers (Etherscan, BscScan, Solscan, Polygonscan). Necesario porque no hay CSV de exchange para operaciones en wallets propias. Usar cuando el usuario diga "mi wallet", "self-custody", "MetaMask", "Ledger", "hardware wallet", "no usé exchange", "Etherscan", "Phantom", "address ETH", "transacciones on-chain".
allowed-tools: Read, Write, Bash
---

# Tracking de wallets self-custody

## Por qué importa

A diferencia de Bitso/Binance (que emiten CSV oficial), las wallets self-custody NO tienen historial preformateado. El contribuyente debe reconstruir cada operación desde el blockchain explorer:
- Entradas (recibos)
- Salidas (envíos)
- Swaps (DEX: Uniswap, PancakeSwap, Jupiter)
- Approvals (no tributables pero generan gas fees deducibles si la operación posterior sí lo es)
- Failed transactions (gas perdido — pérdida documentable)

## Explorers por cadena

| Cadena | Explorer | API |
|---|---|---|
| Ethereum | etherscan.io | api.etherscan.io (key gratis 5 req/s) |
| Polygon | polygonscan.com | api.polygonscan.com |
| BSC | bscscan.com | api.bscscan.com |
| Arbitrum | arbiscan.io | api.arbiscan.io |
| Optimism | optimistic.etherscan.io | api-optimistic.etherscan.io |
| Solana | solscan.io | api.solscan.io (público limitado) |
| Bitcoin | blockchain.com / mempool.space | mempool.space/api |

## Flujo de reconstrucción

```python
from decimal import Decimal
import requests

def reconstruir_historial_wallet(address: str, cadena: str, anio: int) -> list[OperacionCripto]:
    """
    Llama al explorer correspondiente, recupera todas las txs del año,
    clasifica cada una y mapea a OperacionCripto.
    """
    operaciones = []

    # 1. Transferencias nativas (ETH, BNB, MATIC, SOL nativo, BTC)
    txs_nativas = fetch_native_txs(address, cadena, anio)
    for tx in txs_nativas:
        op = clasificar_tx_nativa(tx, address, cadena)
        if op:
            operaciones.append(op)

    # 2. Token transfers (ERC-20, BEP-20, SPL)
    txs_tokens = fetch_token_transfers(address, cadena, anio)
    for tx in txs_tokens:
        op = clasificar_tx_token(tx, address, cadena)
        if op:
            operaciones.append(op)

    # 3. NFT transfers (ERC-721, ERC-1155)
    txs_nfts = fetch_nft_transfers(address, cadena, anio)
    for tx in txs_nfts:
        op = clasificar_tx_nft(tx, address, cadena)
        if op:
            operaciones.append(op)

    # 4. Detectar swaps (entrada + salida en misma tx)
    operaciones_consolidadas = detectar_swaps(operaciones)

    # 5. Enriquecer con precio MXN del día
    for op in operaciones_consolidadas:
        if op.valor_mxn_dia is None or op.valor_mxn_dia == 0:
            op.valor_mxn_dia = lookup_precio_mxn(op.activo_principal(), op.fecha_hora.date())

    return operaciones_consolidadas


def clasificar_tx_nativa(tx, my_address, cadena):
    if tx["to"].lower() == my_address.lower():
        return OperacionCripto(
            fecha_hora=tx["timeStamp"],
            exchange="self_wallet",
            tipo="transferencia_in",
            activo_recibido=moneda_nativa(cadena),
            cantidad_recibida=Decimal(tx["value"]) / Decimal("1e18"),
            fee_mxn=Decimal("0"),
            txid=tx["hash"],
        )
    elif tx["from"].lower() == my_address.lower():
        return OperacionCripto(
            fecha_hora=tx["timeStamp"],
            exchange="self_wallet",
            tipo="transferencia_out",
            activo_dado=moneda_nativa(cadena),
            cantidad_dada=Decimal(tx["value"]) / Decimal("1e18"),
            fee_mxn=Decimal(tx["gasUsed"]) * Decimal(tx["gasPrice"]) / Decimal("1e18") * tc_mxn_del_dia(),
            txid=tx["hash"],
        )
    return None
```

## Cómo distinguir tipos de operación

| Patrón on-chain | Tipo OperacionCripto |
|---|---|
| Entrada nativa desde Coinbase/Bitso/Binance | `transferencia_in` (no gravable hasta venta) |
| Salida nativa hacia exchange | `transferencia_out` |
| Entrada + salida en misma tx + Router conocido (Uniswap, 1inch) | `permuta` (gravable) |
| Entrada ERC-20 sin contraparte saliente | `airdrop` o `stake_recompensa` (clasificar) |
| Mint NFT (transfer from 0x0) | `nft_mint` |
| Token recibido de address de staking conocido | `stake_recompensa` |

## Routers DEX para detectar swaps

```python
ROUTERS_CONOCIDOS = {
    "ethereum": {
        "uniswap_v2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "uniswap_v3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "1inch": "0x1111111254EEB25477B68fb85Ed929f73A960582",
        "sushi": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
    },
    "polygon": {
        "quickswap": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
        "1inch": "0x1111111254EEB25477B68fb85Ed929f73A960582",
    },
    "bsc": {
        "pancakeswap_v2": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
    },
    "solana": {
        "jupiter": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
        "raydium": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    },
}
```

## Gas fees como gasto

Los gas fees pagados son **gasto deducible** asociado a la operación que se realizó:
- Swap con gas $40 MXN → suma a costo base del activo recibido
- Approval previo a swap → suma al gasto de ese swap
- Tx fallida → pérdida deducible (Cap IX si no es actividad empresarial)
- Send a otra wallet propia → NO deducible (es traslado, no enajenación)

## Output

```json
{
  "wallet_address": "0xABC...123",
  "cadena": "ethereum",
  "ejercicio": 2026,
  "txs_revisadas": 287,
  "operaciones_clasificadas": 134,
  "operaciones_dudosas": 12,
  "gas_total_pagado_mxn": "23500.00",
  "operaciones": [...],
  "advertencias": [
    "Tx 0xdef...567 — contrato no identificado, clasificar manualmente",
    "Token UNKNOWN sin precio en CoinGecko — valor MXN = $0 por defecto"
  ],
  "siguiente_paso": "Pasar a calcular-costo-base-fifo + permuta-cripto-cripto-gravable"
}
```

## Limitaciones

- **Privacy chains** (Monero, Zcash shielded): no rastreables públicamente.
- **L2s nuevas** (Base, Linea, zkSync): explorers en desarrollo.
- **Wallets con uso de mixers** (Tornado Cash, etc.): comprometen demostración del costo base.
- **Rate limits**: explorers gratis limitan a 5 req/s — wallets con >5,000 txs requieren múltiples ejecuciones.
