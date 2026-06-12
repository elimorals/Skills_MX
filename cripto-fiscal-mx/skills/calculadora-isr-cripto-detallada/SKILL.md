---
name: calculadora-isr-cripto-detallada
description: Cálculo ISR detallado de operaciones cripto integrando permutas gravables, staking/airdrops/lending como ingresos, NFTs como enajenación de bienes. Aplica tarifa Art. 96 LISR sobre el neto gravable + reporta dónde encaja en la declaración anual PF. Usar cuando el usuario diga ISR cripto, declarar criptomonedas, cuanto pago de impuestos cripto.
allowed-tools: Read, Write
---

# Calculadora ISR cripto detallada

## Categorías gravables

```python
def calcular_isr_cripto(ops: list[OperacionCripto]) -> dict:
    # 1. Ventas (FIFO ya calculado)
    ganancia_ventas = ganancia_ventas_fifo

    # 2. Permutas (cripto A → cripto B)
    # Gravable como enajenación de bienes
    ganancia_permutas = sum_ganancia_permutas

    # 3. Staking + lending interés
    # Acumulables como interés Cap. IX LISR
    ingreso_staking = sum_recompensas_al_valor_mxn

    # 4. Airdrops
    # Ingreso al valor de mercado del día recepción
    ingreso_airdrops = sum_airdrops_valor

    # 5. NFTs (enajenación bienes)
    ganancia_nfts = sum_ganancia_nfts

    total_acumulable = (
        ganancia_ventas + ganancia_permutas
        + ingreso_staking + ingreso_airdrops + ganancia_nfts
    )

    # Aplicar tarifa Art. 96 LISR
    isr_estimado = aplicar_tarifa_art96(total_acumulable)

    return {
        "ganancia_ventas_mxn": str(ganancia_ventas),
        "ganancia_permutas_mxn": str(ganancia_permutas),
        "ingreso_staking_mxn": str(ingreso_staking),
        "ingreso_airdrops_mxn": str(ingreso_airdrops),
        "ganancia_nfts_mxn": str(ganancia_nfts),
        "total_acumulable_mxn": str(total_acumulable),
        "isr_estimado_mxn": str(isr_estimado),
        "categoria_declaracion": "Cap. IV ingresos por enajenación de bienes + Cap. IX intereses",
        "vigencia_validada": False
    }
```

## Output completo

```json
{
  "rfc_hash": "...",
  "ejercicio": 2025,
  "ganancia_ventas_mxn": "33000.00",
  "ganancia_permutas_mxn": "8500.00",
  "ingreso_staking_mxn": "4200.00",
  "ingreso_airdrops_mxn": "1500.00",
  "ganancia_nfts_mxn": "0.00",
  "total_acumulable_mxn": "47200.00",
  "isr_estimado_mxn": "9912.00",
  "categoria_declaracion_anual": "Cap. IV + Cap. IX",
  "advertencias": [
    "Tarifa Art. 96 LISR — confirmar vigencia anual",
    "Si recibiste devolución en años anteriores: declarar este año aunque sea pequeño"
  ],
  "vigencia_validada": false
}
```
