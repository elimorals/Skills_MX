---
name: calculo-isabi-por-estado
description: Calcula el ISABI / ISAI (Impuesto Sobre Adquisición de Bienes Inmuebles) que fija cada estado o municipio. Algunos usan tasa fija (típicamente 2% a 4.5%) y otros, como CDMX, una tarifa progresiva por rangos con cuota fija más factor sobre el excedente. Lo paga el adquirente; en la mayoría de entidades el notario lo calcula y lo entera. Determina la base (el mayor entre valor de operación, catastral y avalúo, según la ley local). Usar cuando el usuario diga ISABI, ISAI, impuesto adquisicion inmuebles, impuesto de traslado de dominio, calcular impuesto compraventa.
allowed-tools: Read, Write
---

# Cálculo ISABI / ISAI por estado o municipio

## Regla de oro

Las tasas y tarifas cambian cada año con la ley de ingresos o el código fiscal local. **No uses una tasa sin confirmarla** con la tesorería municipal/estatal o el código vigente. Este skill no trae un catálogo verificado de tasas 2026.

## CDMX: tarifa progresiva (Art. 113 Código Fiscal CDMX)

- No varía por alcaldía: es una tarifa única por rangos (A, B, C…) con cuota fija + factor aplicado al excedente del límite inferior.
- Los rangos se actualizan cada año. No se encontró la tabla oficial 2026 (solo copias parciales de 2024 y una cifra 2025: cuota fija del rango A $314.97). Obtén la tabla vigente del Código Fiscal CDMX publicado en la Gaceta Oficial o del portal de la Secretaría de Administración y Finanzas.
- Hay litigios sobre la proporcionalidad de la tarifa (tribunales del Primer Circuito, 2022; SCJN, Acuerdo General 9/2026 para los ejercicios 2022-2024). Si el cliente pregunta por amparo, derivar a abogado fiscal.

```python
def isai_cdmx(base, tabla):  # tabla vigente: [(limite_inferior, limite_superior, cuota_fija, factor), ...]
    for li, ls, cuota, factor in tabla:
        if li <= base <= ls:
            return cuota + (base - li) * factor
    raise ValueError("base fuera de la tabla")
```

## Entidades con tasa fija

`isabi = base × tasa`. Pide al usuario la tasa vigente del municipio o consúltala en su ley de ingresos 2026. Las tasas que traía la versión anterior de este skill (Monterrey 2%, Guadalajara 2.5%, Querétaro 2%, Mérida 2%, Toluca 3%, Naucalpan 3.5%) no están verificadas: trátalas como **verificar**.

## Base gravable

Generalmente el mayor entre:
- Valor de operación (precio pactado)
- Valor catastral
- Valor de avalúo (perito autorizado por la autoridad local)

## Output (ejemplo con tasa fija ilustrativa de 2% aportada por el usuario)

```json
{
  "operacion": "compraventa",
  "valor_operacion_mxn": "5500000.00",
  "valor_catastral_mxn": "4800000.00",
  "valor_avaluo_mxn": "5650000.00",
  "base_gravable_mxn": "5650000.00",
  "entidad": "yucatan",
  "municipio": "merida",
  "tipo_calculo": "tasa_fija",
  "tasa_isabi": 0.02,
  "tasa_fuente": "proporcionada por el usuario — verificar",
  "isabi_a_pagar_mxn": "113000.00",
  "quien_paga": "adquirente",
  "plazo_pago": "según ley local — verificar",
  "vigencia_validada": false
}
```

Cálculo: base = max(5,500,000; 4,800,000; 5,650,000) = 5,650,000; 5,650,000 × 2% = 113,000.

## ⚠ Compliance

- `vigencia_validada: false`: confirma tasa/tarifa y plazo con la tesorería antes de cotizar.
- Exenciones o reducciones (vivienda de interés social, herencias, donación entre familiares) dependen de cada ley local.
