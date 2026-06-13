---
name: staking-y-airdrops-ingreso
description: Trata staking rewards, lending interest y airdrops como ingreso acumulable al valor de mercado del día de recepción (Art. 90 LISR, ingresos diversos). Determina si tributa como intereses (Cap VI) o "demás ingresos" (Cap IX). Usar cuando el usuario diga "staking", "rewards", "airdrop", "lending crypto", "yield farming", "rendimiento DeFi", "stETH", "validador Ethereum", "delegación cripto".
allowed-tools: Read, Write
---

# Staking, rewards, airdrops como ingreso

## Marco fiscal MX

| Concepto | Régimen aplicable | Momento de causación |
|---|---|---|
| Staking nativo (ETH 2.0, SOL, ADA) | Demás ingresos (Cap IX LISR) o intereses si exchange custodia | Al recibir el reward, valuado a MXN del día |
| Lending centralizado (BlockFi-like, Bitso Lending) | Intereses (Cap VI LISR) — Bitso emite CFDI tipo Interés | Al devengar (CFDI mensual) |
| DeFi lending (Aave, Compound) | Demás ingresos | Al claim o devengado a discreción contribuyente |
| Liquidity pool fees | Demás ingresos | Al claim |
| Airdrop con liquidez inmediata | Demás ingresos | Día de recepción a precio de mercado |
| Airdrop sin liquidez (sin mercado) | Diferir hasta primera operación que lo valúe | Cuando se vuelve líquido |
| Hard fork (recibir nueva cadena) | Demás ingresos | Día de fork a precio de mercado de la nueva moneda |

## Algoritmo

```python
from decimal import Decimal
from datetime import datetime

def calcular_ingreso_rendimientos(operaciones: list[OperacionCripto]) -> dict:
    staking_total = Decimal("0")
    lending_total = Decimal("0")
    airdrops_total = Decimal("0")
    detalle = []

    for op in operaciones:
        if op.tipo not in ("stake_recompensa", "lending_interes", "airdrop"):
            continue

        valor_mxn = op.valor_mxn_dia  # importador debe haberlo capturado
        if valor_mxn is None:
            valor_mxn = lookup_precio_mxn(op.activo_recibido, op.fecha_hora.date())

        registro = {
            "fecha": op.fecha_hora.isoformat(),
            "tipo": op.tipo,
            "activo": op.activo_recibido,
            "cantidad": str(op.cantidad_recibida),
            "valor_mxn": str(valor_mxn),
            "fuente": op.exchange,
        }

        if op.tipo == "stake_recompensa":
            staking_total += valor_mxn
            registro["regimen_sugerido"] = "Cap IX — demás ingresos"
        elif op.tipo == "lending_interes":
            lending_total += valor_mxn
            registro["regimen_sugerido"] = "Cap VI — intereses (verificar CFDI)"
        elif op.tipo == "airdrop":
            if op.cantidad_recibida > 0 and valor_mxn == 0:
                registro["nota"] = "Airdrop sin precio de mercado — DIFERIR hasta liquidez"
                registro["estado"] = "diferido"
            else:
                airdrops_total += valor_mxn
                registro["regimen_sugerido"] = "Cap IX — demás ingresos"

        detalle.append(registro)

    # IMPORTANTE: el costo base para futura venta es el valor MXN al recibir
    # (regla general SAT: el ingreso reconocido se vuelve costo base)

    return {
        "staking_acumulable_mxn": str(staking_total),
        "lending_acumulable_mxn": str(lending_total),
        "airdrops_acumulable_mxn": str(airdrops_total),
        "total_acumulable_mxn": str(staking_total + lending_total + airdrops_total),
        "detalle": detalle,
        "advertencia_doble_tributacion": "Recuerda: cuando vendas estos tokens, el costo base es el valor MXN del día de recepción. NO causa doble pago."
    }
```

## Errores comunes (NO hacer)

- ❌ Esperar a vender el reward para tributar (genera intereses moratorios y multa)
- ❌ Usar el valor en USD sin convertir a MXN con TC DOF del día
- ❌ Sumar el reward al costo base original (genera doble tributación al vender)
- ❌ Ignorar airdrops "porque no los pedí" (sí son ingreso)

## Casos edge

| Situación | Acción |
|---|---|
| Validador ETH 2.0 con consensus reward diario | Sumar diario o promediar semanal. Documentar criterio. |
| Liquid staking (stETH, rETH) | El rebase (aumento de saldo) es reward al día. |
| Slashing penalty | Pérdida deducible si se documenta. Cap IX. |
| Airdrop a wallet abandonada | No tributable hasta que se reclame. |
| Hard fork no reclamado | No tributable hasta primera disposición. |

## Output

```json
{
  "ejercicio": 2026,
  "rendimientos_detectados": 412,
  "staking_mxn": "85000.00",
  "lending_mxn": "23000.00",
  "airdrops_mxn": "12000.00",
  "total_acumulable_cap_ix_mxn": "97000.00",
  "total_intereses_cap_vi_mxn": "23000.00",
  "advertencias": [
    "ARB airdrop de 2026-03-23 sin precio de mercado al día — diferido."
  ],
  "papel_trabajo_recomendado": [
    "TC DOF utilizado por fecha",
    "Fuente del precio de mercado (CoinGecko, exchange)",
    "Criterio de causación aplicado"
  ]
}
```
