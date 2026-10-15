---
name: nft-enajenacion-bienes
description: Trata compra-venta de NFTs como enajenación de bienes (Cap. IV LISR, criterio usual de confianza media). Calcula ganancia, royalties retenidos al creador, gas fees deducibles, marketplaces (OpenSea, Magic Eden, MetaPlex). Usar cuando el usuario diga "NFT", "JPEG", "OpenSea", "venta NFT", "minteé un NFT", "royalty NFT", "ERC-721", "Bored Ape", "Solana NFT".
allowed-tools: Read, Write
---

# NFTs: tratamiento fiscal MX

## Marco aplicable

> Criterio usual, no regulado expresamente en LISR (confianza media). Validar con contador.

| Rol | Régimen | Observación |
|---|---|---|
| Coleccionista PF (compra-venta esporádica) | Cap. IV LISR — enajenación de bienes (Arts. 119-124) | Ganancia = precio venta − costo (precio compra + gas + comisión marketplace) |
| Creador PF que mintea para vender | Cap II — actividad empresarial | Ingreso por arte, ISR según régimen (RESICO si ≤$3.5M, 612 si más) |
| Holder con NFT como inversión | Cap. IV (al vender) | Tenencia ≠ tributable |
| Receptor de royalties por NFT propio | Cap IX — demás ingresos | El smart contract paga al creador en cada reventa |

## Algoritmo

```python
from decimal import Decimal

def calcular_nft_ops(operaciones_nft: list[OperacionNFT]) -> dict:
    """
    Cada operacion_nft tiene:
      - tipo: "mint" | "compra" | "venta" | "transferencia" | "royalty_recibido"
      - coleccion, token_id
      - precio_eth + precio_mxn_dia
      - gas_eth + gas_mxn
      - comision_marketplace_pct (la real cobrada en la operación)
      - royalty_pct (configurado por colección, típico 5-10%)
    """
    inventario = {}  # token_id → {costo_total_mxn, fecha_compra}
    ganancia_total = Decimal("0")
    perdida_total = Decimal("0")
    royalties_recibidos = Decimal("0")
    detalle = []

    for op in sorted(operaciones_nft, key=lambda o: o.fecha_hora):
        key = f"{op.coleccion}#{op.token_id}"

        if op.tipo == "mint":
            inventario[key] = {
                "costo_total_mxn": op.precio_mxn_dia + op.gas_mxn,
                "fecha": op.fecha_hora,
            }
        elif op.tipo == "compra":
            inventario[key] = {
                "costo_total_mxn": op.precio_mxn_dia + op.gas_mxn + (op.precio_mxn_dia * op.comision_marketplace_pct / 100),
                "fecha": op.fecha_hora,
            }
        elif op.tipo == "venta":
            lote = inventario.get(key)
            if not lote:
                detalle.append({"warning": f"Venta de {key} sin compra registrada — reconstruir costo base"})
                continue
            ingreso_neto = op.precio_mxn_dia - (op.precio_mxn_dia * op.comision_marketplace_pct / 100)
            ingreso_neto -= op.gas_mxn
            ingreso_neto -= (op.precio_mxn_dia * op.royalty_pct / 100)  # royalty al creador

            ganancia = ingreso_neto - lote["costo_total_mxn"]
            if ganancia > 0:
                ganancia_total += ganancia
            else:
                perdida_total += abs(ganancia)

            detalle.append({
                "token": key,
                "precio_venta_mxn": str(op.precio_mxn_dia),
                "comision_pagada_mxn": str(op.precio_mxn_dia * op.comision_marketplace_pct / 100),
                "royalty_pagado_mxn": str(op.precio_mxn_dia * op.royalty_pct / 100),
                "gas_pagado_mxn": str(op.gas_mxn),
                "costo_base_mxn": str(lote["costo_total_mxn"]),
                "ganancia_mxn": str(ganancia),
                "dias_tenencia": (op.fecha_hora - lote["fecha"]).days,
            })
            del inventario[key]
        elif op.tipo == "royalty_recibido":
            royalties_recibidos += op.precio_mxn_dia
            detalle.append({
                "tipo": "royalty",
                "token": key,
                "monto_mxn": str(op.precio_mxn_dia),
                "tratamiento": "Cap IX — demás ingresos",
            })

    return {
        "ganancia_total_mxn": str(ganancia_total),
        "perdida_total_mxn": str(perdida_total),
        "ganancia_gravable_conservadora_mxn": str(ganancia_total),  # pérdidas no restadas (Arts. 121-122)
        "royalties_acumulables_mxn": str(royalties_recibidos),
        "nfts_en_inventario": len(inventario),
        "valor_libros_inventario_mxn": str(sum(Decimal(str(v["costo_total_mxn"])) for v in inventario.values())),
        "detalle_operaciones": detalle,
    }
```

## Marketplaces relevantes MX

Las comisiones y la política de royalties cambian con frecuencia: tomar la comisión **real cobrada** de cada operación (on-chain o del recibo del marketplace), no un porcentaje de tabla.

| Marketplace | Cadenas |
|---|---|
| OpenSea | Ethereum, Polygon, Base y otras EVM |
| Magic Eden | Solana, Bitcoin Ordinals, EVM |
| Blur | Ethereum |

## Casos edge

| Caso | Tratamiento |
|---|---|
| Mint de colección propia que NO vende | No hay ingreso hasta primera venta |
| NFT recibido como pago de servicios | Ingreso por servicios al valor de mercado |
| NFT rugpull / colección abandonada | Documentar valor cero; la pérdida en bienes muebles no es disminuible (Arts. 121-122), criterio conservador |
| Wash trading entre wallets propias | NO genera ganancia ni pérdida (SAT podría desconocer) |
| NFT con utilidad (PFP + acceso DAO) | Solo el componente "bien mueble" es enajenación |

## Output

```json
{
  "ejercicio": 2026,
  "nfts_vendidos": 12,
  "ganancia_total_mxn": "85000.00",
  "perdida_total_mxn": "8000.00",
  "ganancia_gravable_conservadora_mxn": "85000.00",
  "neto_si_contador_acepta_compensar_mxn": "77000.00",
  "royalties_acumulables_mxn": "15000.00",
  "nfts_en_inventario": 4,
  "valor_libros_inventario_mxn": "240000.00",
  "advertencias": [
    "3 NFTs en inventario sin precio de mercado actual — valor libros usado."
  ]
}
```
