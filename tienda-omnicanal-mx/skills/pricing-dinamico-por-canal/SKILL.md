---
name: pricing-dinamico-por-canal
description: Calcula precio óptimo por canal considerando margen objetivo, cargos de cada canal (Mercado Libre, Amazon, pasarela de Shopify, terminal en tienda física; siempre con la tarifa vigente que dé el usuario), IVA 16% incluido en el precio, costo de envío al cliente (cuando aplique), y precio del competidor. Genera lista de precios por SKU × canal para que el operador apruebe o ajuste. Útil al hacer cambios de costos o entrar a nuevos canales. Usar cuando el usuario diga ajustar precios, pricing canal, comisión ML afecta precio, margen objetivo.
allowed-tools: Read, Write
---

# Pricing dinámico por canal

## Inputs

```json
{
  "sku": "SKU-001",
  "costo_unitario_mxn": "120.00",
  "margen_objetivo_pct": 0.35,
  "competidor_precio_mxn": {"mercadolibre": "299", "amazon": "289", "shopify": "279"}
}
```

## Cálculo por canal

```python
def calcular_precio_canal(costo, margen_obj, comision_canal, envio_canal=0, cargo_fijo=0, iva=0.16):
    # P = precio publicado con IVA (Art. 7 Bis LFPC). La comisión se cobra sobre P;
    # su IVA es acreditable, así que entra sin IVA. Margen sobre ingreso sin IVA.
    return (costo + envio_canal + cargo_fijo) / ((1 - margen_obj) / (1 + iva) - comision_canal)
```

Las retenciones de ISR/IVA de ML y Amazon (ver `mercado-libre-pricing`) son anticipo de impuestos, no costo: van al flujo, no a esta fórmula.

## Output

```json
{
  "sku": "SKU-001",
  "costo_mxn": "120.00",
  "precios_sugeridos": {
    "mercadolibre": {"comision_supuesta": 0.15, "precio_publico": "292.44", "vs_competidor_pct": -2.2},
    "amazon": {"comision_supuesta": 0.15, "precio_publico": "292.44", "vs_competidor_pct": 1.2},
    "shopify": {"comision_supuesta": 0.036, "precio_publico": "228.86", "vs_competidor_pct": -18.0},
    "tienda_fisica": {"comision_supuesta": 0.025, "precio_publico": "224.15"}
  },
  "advertencias": [
    "Comisiones del ejemplo son supuestas; sustituir por las vigentes de cada canal",
    "ML: precio < umbral de cargo fijo; sumar cargo fijo por unidad vigente"
  ]
}
```

Comprobación ML: 292.44 / 1.16 = 252.10 sin IVA; comisión 0.15 × 292.44 = 43.87; utilidad 252.10 − 43.87 − 120 = 88.23 = 35.0% ✓ (envío 0 en todos para simplificar).

## De dónde sacar los cargos vigentes

No hay tabla confiable memorizada: los cargos cambian y dependen de categoría, tipo de publicación y plan.

| Canal | Fuente |
|---|---|
| Mercado Libre | Ayuda oficial "costos de vender" o simulador del panel (cargo % + cargo fijo en bajo precio) |
| Amazon MX | `amazon_mx_get_fees_estimate` (MCP `mp_amazon_mx_seller`, requiere credenciales SP-API) o la calculadora de Seller Central |
| Shopify | Tarifa de tu pasarela + comisión de transacción de tu plan si usas pasarela externa |
| Tienda física | Tarifa de tu terminal (Clip, Mercado Pago Point, banco), sobre ventas con tarjeta |
