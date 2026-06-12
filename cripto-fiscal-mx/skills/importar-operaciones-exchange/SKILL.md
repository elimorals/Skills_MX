---
name: importar-operaciones-exchange
description: Importa CSV oficial de cada exchange (Bitso, Binance, Coinbase, Kraken) y normaliza a schema común OperacionCripto. Detecta tipo (compra/venta/permuta/stake/airdrop/transferencia). Valoriza en MXN con TC histórico del día. Usar cuando el usuario diga importar bitso, csv binance, cargar operaciones, sincronizar exchange.
allowed-tools: Read, Write
---

# Importar operaciones exchange

## Formatos soportados

| Exchange | Formato | Cómo obtener |
|---|---|---|
| Bitso | CSV oficial | Cuenta → Reportes → Exportar |
| Binance | CSV oficial | Wallet → Transaction History → Export |
| Coinbase | CSV oficial | Profile → Reports → Generate |
| Kraken | CSV/Excel | History → Export |

## Schema normalizado

```python
class OperacionCripto(BaseModel):
    fecha_hora: datetime
    exchange: str
    tipo: Literal["compra", "venta", "permuta", "stake_recompensa", "airdrop", "transferencia_in", "transferencia_out", "lending_interes"]
    activo_dado: str | None
    cantidad_dada: Decimal
    activo_recibido: str
    cantidad_recibida: Decimal
    valor_mxn_dia: Decimal  # TC Banxico USD/MXN del día × precio en USD
    fee_mxn: Decimal
    txid: str | None
```

## Detección automática de tipo

- MXN → cripto = compra
- cripto → MXN = venta
- cripto A → cripto B (no MXN) = permuta gravable
- "REWARD" / "STAKING" = stake_recompensa
- "AIRDROP" = airdrop
- Wallet → exchange = transferencia_in

## Output

```json
{
  "exchange": "bitso",
  "archivo_origen": "bitso_2025_export.csv",
  "operaciones_importadas": 245,
  "compras": 89,
  "ventas": 67,
  "permutas": 45,
  "stakings": 32,
  "airdrops": 12,
  "valoradas_en_mxn": 245,
  "advertencias": []
}
```
