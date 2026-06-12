---
name: calculo-isabi-por-estado
description: Calcula ISABI (Impuesto Sobre Adquisición de Bienes Inmuebles) que varía por estado y municipio (1.5% a 6% del valor de operación). El comprador paga ISABI; el notario lo retiene en la escritura y entera al fisco local. Catálogo con tasas vigentes top municipios. Usar cuando el usuario diga ISABI, impuesto adquisicion inmuebles, calcular impuesto compraventa.
allowed-tools: Read, Write
---

# Cálculo ISABI por estado/municipio

## Tasas referencia (validar vigentes anual)

| Entidad | Municipio | Tasa ISABI |
|---|---|---|
| CDMX | Cuauhtémoc | 4.0% |
| CDMX | Miguel Hidalgo | 4.5% |
| CDMX | Otros | 4.0-4.5% |
| EdoMex | Naucalpan | 3.5% |
| EdoMex | Toluca | 3.0% |
| NL | Monterrey | 2.0% |
| NL | San Pedro | 2.0% |
| Jalisco | Guadalajara | 2.5% |
| Querétaro | Querétaro | 2.0% |
| Yucatán | Mérida | 2.0% |

## Base gravable

Mayor entre:
- Valor de operación (lo declarado)
- Valor catastral (lo que dice el municipio)
- Valor de avalúo (perito certificado)

## Output

```json
{
  "operacion": "compraventa",
  "valor_operacion_mxn": "5500000.00",
  "valor_catastral_mxn": "4800000.00",
  "valor_avaluo_mxn": "5650000.00",
  "base_gravable_mxn": "5650000.00",
  "entidad": "cdmx",
  "municipio": "cuauhtemoc",
  "tasa_isabi": 0.04,
  "isabi_a_pagar_mxn": "226000.00",
  "quien_paga": "comprador",
  "deadline_pago": "30 días post escrituración",
  "vigencia_validada": false
}
```

## ⚠ Compliance

- Tasas cambian anualmente en algunos municipios
- `vigencia_validada: false` — confirmar con tesorería municipal antes
- Compraventa entre familiares: puede aplicar exención (consultar)
