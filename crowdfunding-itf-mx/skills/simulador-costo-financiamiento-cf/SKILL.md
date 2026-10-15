---
name: simulador-costo-financiamiento-cf
description: Para emprendedores y PyMEs - compara el costo total de financiarse vía crowdfunding (IFC de deuda o capital) contra un crédito bancario o de otra entidad, con tasa, comisiones de apertura y de la plataforma, IVA sobre intereses y comisiones, CAT y dilución en el caso de capital; incluye los montos máximos por solicitud de la CNBV (50,000 UDIS personales, 1,670,000 UDIS empresariales). Usar cuando el usuario diga simulador costo financiamiento cf, simulador_costo_financiamiento_cf, conviene crowdfunding o banco, cuánto me cuesta un préstamo por crowdfunding, levantar capital por crowdfunding, ayuda con simulador costo financiamiento cf.
allowed-tools: Read, Write
---

# Simulador costo de financiamiento: crowdfunding vs. banco

## Entradas (las da el usuario; no inventes tasas)

| Concepto | Crowdfunding deuda | Banco / otra entidad |
|---|---|---|
| Monto, plazo, periodicidad | sí | sí |
| Tasa anual | oferta de la IFC | oferta del banco |
| Comisión por apertura / éxito de la plataforma | % del monto | % del monto |
| Otras comisiones y seguros | sí | sí |
| IVA sobre intereses y comisiones | 16% salvo exención (Art. 15 LIVA; verificar caso) | ídem |
| Garantías / aval | según IFC | según banco |

Capital (equity crowdfunding): % de la empresa cedido, valuación pre-money, derechos de los inversionistas; el costo es la **dilución**, no una tasa.

## Cálculo

```python
def costo_total(monto, tasa_anual, meses, comision_pct, iva_intereses=True):
    i = tasa_anual / 12
    pago = monto * i / (1 - (1 + i) ** -meses)          # amortización francesa
    intereses = pago * meses - monto
    iva = intereses * D("0.16") if iva_intereses else D(0)
    comision = monto * comision_pct * D("1.16")
    return {"pago_mensual": pago, "intereses": intereses, "iva": iva,
            "comision_con_iva": comision, "costo_total": intereses + iva + comision}
```

El **CAT** oficial lo calcula y publica la entidad (metodología Banxico); pídelo y compáralo, no lo sustituyas con este cálculo.

## Límites CNBV (Arts. 47-48 de las Disposiciones ITF)

- Por IFC: 50,000 UDIS (préstamo personal); 1,670,000 UDIS (empresarial, inmobiliario, capital, copropiedad o regalías), hasta 6,700,000 UDIS con autorización de la CNBV.
- Total entre IFC por solicitante: 7,370,000 UDIS.

## Output esperado

```json
{
  "operation": "simulador-costo-financiamiento-cf",
  "data": {
    "monto_mxn": "500000.00",
    "escenarios": [
      {"fuente": "IFC", "tasa_anual": "<usuario>", "costo_total_mxn": "<calculado>", "cat_publicado": "<de la IFC>"},
      {"fuente": "banco", "tasa_anual": "<usuario>", "costo_total_mxn": "<calculado>", "cat_publicado": "<del banco>"}
    ],
    "dentro_limite_cnbv": true
  },
  "vigencia_validada": false
}
```

## Casos edge

- IFC no autorizada: no simular; remitir a `catalogo-ifc-autorizadas`.
- Deducibilidad de intereses para la empresa: requisitos del Art. 27 LISR y límites de capitalización delgada si hay partes relacionadas (verificar con contador).
- Datos incompletos → solicitar al usuario.

## Dependencias

- `core-mexico` (mxn-formato)

Comparativo orientativo, no asesoría financiera.
