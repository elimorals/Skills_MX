---
name: refrendo-y-tenencia
description: Calcula el refrendo anual (placas) y la tenencia vehicular en estados que aún la cobran (EdoMex, NL, varios). El refrendo es obligatorio en TODOS los estados; la tenencia depende del estado (CDMX la subsidió desde 2011, EdoMex la cobra con subsidios condicionados). Genera resumen del costo total año, deadline (típico 31 marzo), y alertas si no se paga. Usar cuando el usuario diga refrendo, tenencia, cuánto pago de placas, pago anual auto. NO confundir con multas (esas son verificacion-vehicular o multas-deteccion-pago).
allowed-tools: Read, Write
---

# Refrendo y tenencia anual

## Conceptos

### Refrendo (obligatorio TODOS los estados)
- Pago anual de derechos por tener placas activas
- Plazo: deadline típicamente 31 marzo del año en curso
- Costo: $500-$1,500 MXN por estado

### Tenencia (depende del estado)
- Impuesto estatal sobre vehículos nuevos / usados según valor
- Estados que la cobran (2026 referencia, validar vigencia):
  - EdoMex (con subsidio si valor < $250k MXN aprox)
  - Nuevo León
  - Querétaro
  - Otros
- CDMX la subsidió permanentemente desde 2011

## Cálculo tenencia EdoMex (referencia 2026 — VALIDAR vigencia anual)

```python
def calcular_tenencia_edomex(valor_factura_mxn: Decimal, antiguedad_anos: int) -> Decimal:
    if antiguedad_anos > 9:
        return Decimal("0")  # exento
    # Tarifa progresiva
    base = valor_factura_mxn
    tasa = 0.03 if base <= 250_000 else 0.04 if base <= 500_000 else 0.05
    impuesto = base * Decimal(str(tasa))
    # Subsidio condicionado a placas EdoMex + sin multas
    return impuesto * Decimal("0.50")  # 50% subsidio estándar
```

⚠ Reglas pueden cambiar año a año — siempre consultar portal oficial:
- EdoMex: https://sfpya.edomexico.gob.mx
- NL: https://www.nl.gob.mx

## Output

```json
{
  "placa_hash": "...",
  "ejercicio": 2026,
  "entidad": "edomex",
  "refrendo": {
    "monto_mxn": "750.00",
    "deadline": "2026-03-31",
    "estado": "pagado",
    "fecha_pago": "2026-01-15"
  },
  "tenencia": {
    "aplica": true,
    "valor_factura_mxn": "300000.00",
    "antiguedad_anos": 3,
    "impuesto_calculado_mxn": "12000.00",
    "subsidio_50_pct": true,
    "monto_a_pagar_mxn": "6000.00",
    "deadline": "2026-03-31",
    "estado": "pendiente"
  },
  "total_anual_mxn": "6750.00",
  "advertencias": ["Tarifa tenencia EdoMex 2026 — confirmar con portal oficial"],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Vehículo > 10 años | Tenencia típicamente exenta |
| Vehículo eléctrico | Subsidios adicionales o exención |
| Placas de otra entidad federativa | Aplican reglas de esa entidad |
| Vehículo nuevo (factura del año) | Tenencia primera vez (valor factura sin depreciación) |
| Cambio de propietario | Refrendo se paga por propietario actual, no anterior |

## Dependencias

- Portales estatales (no MCP — info catálogo)
- `mp_cdmx_municipal`, `mp_edomex_municipal` (parcial — multas asociadas)

## ⚠ Compliance

- Tarifas se actualizan anualmente — confirmar antes de pagar
- `vigencia_validada: false` siempre — confirmar contra portal oficial
