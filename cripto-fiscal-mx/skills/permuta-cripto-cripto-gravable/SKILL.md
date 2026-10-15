---
name: permuta-cripto-cripto-gravable
description: Detecta y valúa permutas cripto-cripto como enajenación del activo entregado (Art. 14 CFF y Art. 119 LISR, criterio usual de confianza media). Cualquier intercambio de un cripto por otro (ej. BTC → USDC, ETH → SOL) realiza la ganancia o pérdida del activo entregado aunque no toques pesos. Usar cuando el usuario diga "swap", "intercambio cripto", "permuta cripto-cripto", "convertir BTC a USDC", "DEX swap", "Uniswap operación".
allowed-tools: Read, Write
---

# Permuta cripto-cripto gravable

## Por qué importa

El criterio usual trata la permuta cripto-cripto como **enajenación** del activo entregado: el Art. 14 fr. I CFF considera enajenación "toda transmisión de propiedad" y el Art. 119 LISR remite a ese concepto. No hay criterio normativo del SAT específico para cripto (confianza media; validar con contador). Esto significa:

- Cambiar 1 BTC (comprado a $1.2M MXN) por 50,000 USDC cuando 1 BTC vale $1.5M MXN = **realiza ganancia de $300k MXN gravable**, aunque no convirtieras a fiat.
- DEX swaps (Uniswap, PancakeSwap, Curve, 1inch) son también permutas.
- Stablecoin swaps (USDT → USDC) son permutas — pero la ganancia normalmente es ~0 si el peg se mantuvo.

**Errores comunes**:
- Asumir "no toqué fiat → no gravable" ❌
- Reportar solo cuando llega a MXN bancarizado ❌

## Algoritmo de detección

```python
from decimal import Decimal
from typing import Literal

def detectar_permutas(operaciones: list[OperacionCripto]) -> list[PermutaGravable]:
    """
    Una permuta gravable es una operacion tipo="permuta" donde activo_dado != "MXN"
    Y activo_recibido != "MXN" (ambos lados son cripto).
    """
    permutas = []
    for op in operaciones:
        if op.tipo != "permuta":
            continue
        if op.activo_dado == "MXN" or op.activo_recibido == "MXN":
            continue  # esto es compra o venta, no permuta

        # Determinar valor MXN del lado entregado (es el monto "vendido")
        valor_mxn_entregado = op.valor_mxn_dia  # se asume capturado por importador

        # Costo base del lado entregado se calcula via FIFO en skill calcular-costo-base-fifo
        permutas.append(PermutaGravable(
            fecha=op.fecha_hora,
            exchange=op.exchange,
            activo_entregado=op.activo_dado,
            cantidad_entregada=op.cantidad_dada,
            activo_recibido=op.activo_recibido,
            cantidad_recibida=op.cantidad_recibida,
            valor_mxn_realizado=valor_mxn_entregado,
            requiere_calculo_costo_base=True,
            txid=op.txid,
        ))

    return permutas
```

## Casos edge importantes

| Caso | Tratamiento fiscal |
|---|---|
| Wrap/unwrap (BTC ↔ WBTC) | Discutible — el SAT no se ha pronunciado. Conservador: tratar como permuta. Agresivo: argumentar misma economía. |
| Bridge entre cadenas (USDC Ethereum → USDC Polygon) | Conservador: permuta. Agresivo: no enajenación (mismo token). |
| Stablecoin USDT → USDC | Permuta. Ganancia/pérdida ~$0 si peg estable. Reportar de todos modos. |
| Liquidity Pool deposit | LP token recibido = permuta del par entregado (gravable). |
| Yield/Lending: depositar USDC → recibir aUSDC | Discutible. Argumentar custodia ≠ enajenación. |

## Output schema

```json
{
  "ejercicio": 2026,
  "permutas_detectadas": 47,
  "valor_mxn_total_realizado": "2450000.00",
  "ganancia_acumulada_permutas_mxn": "385000.00",
  "perdida_acumulada_permutas_mxn": "42000.00",
  "ganancia_gravable_conservadora_mxn": "385000.00",
  "neto_si_contador_acepta_compensar_mxn": "343000.00",
  "permutas": [
    {
      "fecha": "2026-03-15T14:22:00Z",
      "exchange": "uniswap-v3",
      "entregado": {"activo": "ETH", "cantidad": "5.0", "valor_mxn_realizado": "275000.00"},
      "recibido": {"activo": "USDC", "cantidad": "13750"},
      "costo_base_mxn": "200000.00",
      "ganancia_mxn": "75000.00",
      "tratamiento_fiscal": "Cap. IV LISR — enajenación de bienes (Art. 14 CFF)"
    }
  ],
  "notas_papel_trabajo": "Permutas calculadas con TC Banxico publicado en DOF (Art. 20 CFF). FIFO aplicado para costo base."
}
```

## Cuándo NO usar este skill

- Compras con MXN (usa skill `importar-operaciones-exchange`).
- Ventas a MXN (cálculo principal en `calcular-costo-base-fifo`).
- Recibir staking rewards (usa `staking-y-airdrops-ingreso`).
- Compra/venta de NFTs (usa `nft-enajenacion-bienes`).
