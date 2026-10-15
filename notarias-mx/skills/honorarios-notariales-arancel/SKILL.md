---
name: honorarios-notariales-arancel
description: Calcula honorarios notariales según el arancel de notarios publicado por cada entidad (en CDMX, el Arancel de Notarios publicado en la Gaceta Oficial). Cada estado tiene su propio arancel y reglas sobre descuentos. Útil para cotización inicial al cliente. Usar cuando el usuario diga honorarios notario, arancel notarial, cuanto cobra notario, cotizar escritura.
allowed-tools: Read, Write
---

# Honorarios notariales — arancel

## Estructura arancel típica

Por tipo de acto:
- **Compraventa**: % escalonado sobre valor operación + fijo base
- **Testamento**: monto fijo ($500-$3,500 según estado)
- **Poder general**: $1,500-$5,000
- **Constitución sociedad**: % capital social + fijo
- **Sucesión**: varia por complejidad
- **Hipoteca**: % monto crédito

## Tabla ilustrativa (NO es el arancel oficial)

Esta tabla solo muestra la mecánica de cálculo por tramos. No se verificó contra el Arancel de Notarios de la CDMX vigente: antes de cotizar, carga los tramos del arancel publicado en la Gaceta Oficial de la entidad (**verificar**).

| Valor operación | % aplicable |
|---|---|
| Hasta $500k | 1.5% (mínimo $5,000) |
| $500k - $1M | 1.2% sobre el exceso de $500k + $7,500 |
| $1M - $5M | 1.0% sobre exceso de $1M + $13,500 |
| Más de $5M | 0.8% sobre exceso de $5M + $53,500 |

## Output

Cálculo: 500,000 × 1.5% = 7,500; 500,000 × 1.2% = 6,000; 4,000,000 × 1% = 40,000; 500,000 × 0.8% = 4,000; subtotal 57,500; IVA 9,200; total 66,700.

```json
{
  "tipo_acto": "compraventa",
  "estado": "cdmx",
  "valor_operacion_mxn": "5500000.00",
  "calculo_arancel": {
    "tramo_1_hasta_500k": "7500.00",
    "tramo_2_500k_1m": "6000.00",
    "tramo_3_1m_5m": "40000.00",
    "tramo_4_exceso_5m": "4000.00",
    "subtotal": "57500.00"
  },
  "iva_16_pct_mxn": "9200.00",
  "honorarios_totales_mxn": "66700.00",
  "puede_descontar_notario": "verificar ley local",
  "descuento_aplicado_mxn": "0",
  "honorarios_finales_mxn": "66700.00",
  "vigencia_validada": false
}
```

## ⚠ Compliance

- Aranceles cambian por estado y se actualizan periódicamente
- Si el notario puede cobrar menos del arancel depende de la ley del notariado local (**verificar**); nunca más
- IVA 16% sobre los honorarios (8% si la notaría está en el padrón del estímulo fronterizo)
- Los honorarios no incluyen impuestos (ISAI, ISR del vendedor) ni derechos del RPP
