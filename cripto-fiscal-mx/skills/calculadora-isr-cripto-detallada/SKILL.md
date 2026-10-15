---
name: calculadora-isr-cripto-detallada
description: Estima el ISR de una persona física en México por operaciones con criptomonedas y activos virtuales en la declaración anual (ejercicio 2025 en abril 2026, o 2026). Integra ventas y permutas (enajenación de bienes, Arts. 119-124 LISR), staking, airdrops y lending (demás ingresos o intereses) y NFTs; calcula el ISR incremental con la tarifa anual del Art. 152 sobre el total de ingresos del año. Usar cuando el usuario diga ISR cripto, impuestos bitcoin, declarar criptomonedas, cuánto pago por mis cripto, ganancia cripto SAT, enajenación de activos virtuales.
allowed-tools: Read, Write
---

# Calculadora ISR cripto detallada

> **Confianza media.** La LISR no tiene un capítulo para activos virtuales. El criterio usual (y el que aplica esta skill) trata ventas y permutas como **enajenación de bienes** (Cap. IV, Arts. 119-124 LISR; Art. 14 CFF) y los rendimientos como **demás ingresos** (Cap. IX) o **intereses** (Cap. VI). Otros contadores sostienen tratamientos distintos. Validar con contador antes de declarar.

## Categorías

| Concepto | Capítulo LISR (criterio usual) | Base |
|---|---|---|
| Venta cripto → MXN | IV enajenación de bienes | Precio − costo actualizado (FIFO, `calcular-costo-base-fifo`) − comisiones |
| Permuta cripto → cripto | IV enajenación de bienes | Valor de mercado de lo recibido − costo de lo entregado (`permuta-cripto-cripto-gravable`) |
| Staking, airdrops, LP fees | IX demás ingresos | Valor de mercado en MXN al recibir (`staking-y-airdrops-ingreso`) |
| Lending con CFDI/constancia de intereses | VI intereses | Interés real según constancia |
| NFTs | IV (coleccionista) o II (creador) | `nft-enajenacion-bienes` |

## Reglas de enajenación de bienes que cambian el resultado

1. **Costo actualizado (Art. 124)**: el costo se actualiza por INPC desde el mes de adquisición. Para bienes muebles el costo baja 10% por año de tenencia, salvo que se opte (Reglamento) por no disminuirlo en bienes que no pierden valor — documentar la opción.
2. **Ganancia por años de tenencia (Art. 120)**: la ganancia se divide entre los años transcurridos (máx. 20). Ese cociente se acumula a los demás ingresos; el resto paga a la tasa efectiva del año (o promedio de 5 años). Con tenencia < 1 año, toda la ganancia se acumula.
3. **Pérdidas**: los Arts. 121-122 solo permiten disminuir pérdidas de inmuebles, acciones, partes sociales y certificados de aportación. **Criterio conservador: la pérdida en cripto no se resta**; netear ganancias y pérdidas solo con criterio documentado del contador.
4. **Exención Art. 93 fr. XIX inc. b)**: enajenación de bienes muebles (no acciones ni títulos valor) exenta si en el año la diferencia entre el total de enajenaciones y el costo no excede 3 veces el salario mínimo anual. Con la desindexación se usa la UMA: 3 × 41,296.10 = **$123,888.30** (2025); 3 × 42,818.15 = **$128,454.45** (2026). Que los activos virtuales sean "bienes muebles" para esta exención es **discutible — verificar** con contador.
5. **Pago provisional (Art. 126)**: en "otros bienes" el adquirente PM residente retiene 20% del monto total. En exchanges normalmente no ocurre; si te retuvieron, acreditarlo.

## Algoritmo

```python
def calcular_isr_cripto(ops, otros_ingresos_acumulables, ejercicio, aplicar_exencion_93_xix=False):
    ganancia_enajenacion = sum_ganancias_por_operacion(ops)   # ventas + permutas + NFT, pérdidas NO restadas (conservador)
    if aplicar_exencion_93_xix:
        ganancia_enajenacion = max(0, ganancia_enajenacion - 3 * uma_anual(ejercicio))
    demas_ingresos = staking + airdrops + lp_fees               # Cap. IX
    intereses = lending_con_constancia                          # Cap. VI (interés real)

    base_con = otros_ingresos_acumulables + parte_acumulable(ganancia_enajenacion) + demas_ingresos + intereses
    isr_incremental = tarifa_152(base_con, ejercicio) - tarifa_152(otros_ingresos_acumulables, ejercicio)
    return isr_incremental  # + ISR de la parte no acumulable (Art. 120 fr. III) si tenencia > 1 año
```

Usa la tarifa anual del Art. 152 del ejercicio (tabla en `pf-anual-mx/skills/calculadora-isr-anual`). **No** apliques la tarifa mensual del Art. 96 ni una tasa fija: el ISR cripto es incremental sobre los demás ingresos.

`mp_bitso.bitso_calcular_isr_cripto_mx` existe pero es **referencial** (tarifa simplificada y trata RESICO): no usarlo como cálculo final. Las ganancias por enajenación de bienes **no** se pagan con tasas RESICO aunque el contribuyente esté en RESICO por otra actividad.

## Ejemplo (ejercicio 2025, sueldos $600,000, tenencias < 1 año)

```
Ganancia ventas 33,000 + permutas 8,500       = 41,500 (Cap. IV)
Staking 4,200 + airdrops 1,500                 =  5,700 (Cap. IX)
ISR tarifa 152 sobre 600,000                   = 113,603.94
ISR tarifa 152 sobre 647,200                   = 127,763.94
ISR incremental cripto (sin exención)          =  14,160.00
Si el contador acepta la exención 93-XIX-b:   base 605,700 → 115,313.94 → incremental 1,710.00
```

## Output

```json
{
  "rfc_hash": "...",
  "ejercicio": 2025,
  "ganancia_enajenacion_mxn": "41500.00",
  "perdidas_no_disminuidas_mxn": "12000.00",
  "demas_ingresos_cap_ix_mxn": "5700.00",
  "intereses_cap_vi_mxn": "0.00",
  "otros_ingresos_acumulables_mxn": "600000.00",
  "isr_incremental_mxn": "14160.00",
  "isr_incremental_con_exencion_93_xix_mxn": "1710.00",
  "tarifa": "Art_152_LISR_2025",
  "criterio": "Cap. IV enajenación + Cap. IX demás ingresos (confianza media)",
  "advertencias": [
    "Tratamiento fiscal de activos virtuales no expreso en LISR: validar criterio con contador",
    "Pérdidas en cripto no restadas (criterio conservador Arts. 121-122)"
  ],
  "vigencia_validada": false
}
```

## ⚠ Compliance

- Fuentes verificadas: LISR texto vigente (Cámara de Diputados, última reforma DOF 01-04-2024), Anexo 8 RMF 2026 (DOF 28-12-2025), UMA INEGI.
- Es una estimación, no asesoría fiscal. `vigencia_validada: false` siempre.
