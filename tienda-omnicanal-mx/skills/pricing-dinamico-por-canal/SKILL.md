---
name: pricing-dinamico-por-canal
description: Calcula precio óptimo por canal considerando margen objetivo, comisión del canal (ML ~13%, Amazon ~15%, Shopify ~3%, tienda física 0%), IVA 16%, costo de envío al cliente (cuando aplique), y precio del competidor. Genera lista de precios por SKU × canal para que el operador apruebe o ajuste. Útil al hacer cambios de costos o entrar a nuevos canales. Usar cuando el usuario diga ajustar precios, pricing canal, comisión ML afecta precio, margen objetivo.
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
def calcular_precio_canal(costo, margen_obj, comision_canal, envio_canal, iva_pct=0.16):
    # Precio base con margen
    precio_sin_canal = costo / (1 - margen_obj)
    # Ajustar por comisión del canal
    precio_pre_iva = (precio_sin_canal + envio_canal) / (1 - comision_canal)
    # Aplicar IVA
    return precio_pre_iva * (1 + iva_pct)
```

## Output

```json
{
  "sku": "SKU-001",
  "costo_mxn": "120.00",
  "precios_sugeridos": {
    "mercadolibre": {"precio_publico": "289.00", "margen_neto_pct": 32.0, "vs_competidor_pct": -3.3},
    "amazon": {"precio_publico": "295.00", "margen_neto_pct": 31.5},
    "shopify": {"precio_publico": "245.00", "margen_neto_pct": 38.0, "ahorra_envio_dueño": true},
    "tienda_fisica": {"precio_publico": "225.00", "margen_neto_pct": 46.6}
  },
  "advertencias": ["Shopify margen 38% — más alto que canales con comisión"]
}
```

## Comisiones aproximadas (validar vigentes)

| Canal | Comisión |
|---|---|
| Mercado Libre clásico | 11-16% |
| Mercado Libre premium | 14-18% |
| Amazon MX | 8-15% según categoría |
| Shopify | 2.9% + $3 USD (Stripe MX) |
| Tienda física | 0% (sólo TPV ~2%) |
