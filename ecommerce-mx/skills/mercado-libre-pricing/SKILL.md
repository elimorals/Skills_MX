---
name: mercado-libre-pricing
description: Cálculo de precio óptimo para listings en Mercado Libre México considerando comisión por modalidad (13% clásica, 17% premium, +5% Mercado Envíos Full), costo IVA trasladado, costo logístico, margen mínimo deseado y precio competidores actuales. Detecta si subir/bajar precio según ratio precio-vs-competidores y reputación. Usar cuando el usuario diga precio mercado libre, pricing ML, qué precio pongo, comisión mercado libre, margen ML, competidores ML, optimizar precios. NO usar para crear listings (otro skill mercado-libre-listings).
allowed-tools: Read, Write, Edit, Bash
---

# Mercado Libre — Pricing dinámico

Calcular el precio en ML requiere ingeniería inversa de costo + comisión + márgen + posición competitiva.

## Fórmula base

```
precio_lista = (costo_articulo + costo_logistico) / (1 - comision_ml - margen_objetivo)
```

Para un producto con:
- Costo: $250 MXN
- Logística: $80 MXN (Mercado Envíos Full)
- Comisión: 17% (premium)
- Margen objetivo: 20%

```
precio_lista = ($250 + $80) / (1 - 0.17 - 0.20)
             = $330 / 0.63
             = $524 MXN
```

## Comisiones por categoría (referencia 2025 — verificar 2026)

| Categoría | Clásica | Premium |
|---|---|---|
| Celulares y telefonía | 13% | 16% |
| Computación | 13% | 16% |
| Electrónicos, Audio y Video | 13% | 17% |
| Hogar, Muebles y Jardín | 14% | 17% |
| Ropa, Bolsas y Calzado | 14% | 17% |
| Belleza y Cuidado Personal | 15% | 18% |
| Deportes y Fitness | 13% | 17% |
| Libros, Revistas y Comics | 8% | 11% |
| Juegos y Juguetes | 13% | 17% |
| Salud y Equipamiento Médico | 14% | 17% |
| **Mercado Envíos Full** (adicional) | +5% | +5% |

⚠ ML actualiza comisiones periódicamente. Validar con `mp_mercado_libre.get_category_fees(category_id)`.

## Análisis competitivo

Antes de fijar precio:

```
1. Buscar listings competidores: mp_mercado_libre.search_competitors(query)
2. Filtrar por:
   - Modalidad similar (premium vs clásica)
   - Reputación similar (MercadoLíder, Estándar)
   - Envío Full vs sin Full
3. Calcular percentiles: P25, mediana, P75
4. Decidir posición:
   - P25-P50: ranking alto, margen bajo (volumen)
   - P50-P75: equilibrio ranking/margen
   - >P75: margen alto, solo si tu reputación o calidad lo justifica
```

## IVA y CFDI implicaciones

ML maneja IVA dependiendo del tipo de venta:

| Tipo venta | Quien emite CFDI | Quien paga IVA |
|---|---|---|
| **B2C global** (sin RFC) | El seller (CFDI público general) | Seller traslada en su precio |
| **B2C con factura** | El seller a RFC del comprador | Seller traslada |
| **Cross-border** (Brasil/Argentina) | ML actúa como intermediario | Reglas IEPS/IVA específicas |

⚠ El precio publicado en ML **debe incluir IVA**. Si subes $500 y eliges "IVA incluido", el ingreso real para ti es $500 / 1.16 = $431.

## Ajuste por reputación

ML premia ranking si tienes mejor reputación:

| Reputación | Ranking boost | Precio máximo competitivo |
|---|---|---|
| MercadoLíder Platinum | +30% | P25-P50 |
| MercadoLíder Gold | +20% | P25-P50 |
| MercadoLíder | +10% | Mediana |
| Estándar | 0% | <P25 (única forma de competir) |
| Bajo desempeño | -50% | No competitivo |

## Estrategias de pricing

### 1. Anchor pricing
Listing premium con precio alto + listing clásica del mismo producto con precio bajo. El comprador percibe el clásico como "ganga".

### 2. Pricing por escala
Múltiples cantidades del mismo producto con descuento por volumen:
- 1 unidad: $500
- 3 unidades: $1,350 (-10%)
- 10 unidades: $4,000 (-20%)

### 3. Pricing competitivo agresivo
$1-5 MXN bajo el precio del competidor con mejor ranking. Útil cuando tu reputación es similar o mejor.

### 4. Pricing premium
$50-100 MXN sobre la mediana, justificado con:
- Envío Mercado Envíos Full (entrega 24h)
- Garantía extendida
- MercadoLíder Platinum badge

## Recargo o descuento por método de pago

| Método | Costo MercadoPago |
|---|---|
| TDC/TDD MX en una pago | 4.39% + IVA + $4 MXN/operación |
| 3 MSI (tarjeta Visa/Master) | +6.55% |
| 6 MSI | +9.55% |
| 9 MSI | +12.85% |
| 12 MSI | +15.85% |
| 18 MSI | +18.85% |

Si activas MSI, sube el precio para mantener margen — o ML lo descuenta de tus ganancias.

## Output estructurado

```json
{
  "analisis_precio": {
    "listing_id": "MLM1234567890",
    "costos": {
      "articulo": 250.00,
      "logistico": 80.00,
      "iva_acreditable": 40.00,
      "total_costo": 330.00
    },
    "comisiones": {
      "modalidad": "premium",
      "comision_categoria": 0.17,
      "envios_full": 0.05,
      "msi_si_activa": 0.0655,
      "total_comisiones": 0.2855
    },
    "competidores": {
      "p25": 459.00,
      "mediana": 549.00,
      "p75": 649.00,
      "mejor_ranking_precio": 519.00
    },
    "tu_reputacion": "MercadoLider Gold",
    "precios_sugeridos": {
      "agresivo_volumen": 515.00,
      "equilibrado": 549.00,
      "premium_margen": 619.00
    },
    "recomendacion": "equilibrado",
    "margen_real_estimado": "18-22%",
    "alertas": [
      "Tu costo está $20 sobre el mediano del mercado — revisa proveedor"
    ]
  }
}
```

## Validación pendiente

- Comisiones 2026 actualizadas
- Cargo MSI MercadoPago 2026
- Mercado Envíos Full pricing 2026
- Testimonios sellers MX con volumen ≥ $50k MXN/mes

## Ver también

- `mercado-libre-listings`
- `mxn-formato` para formato pesos
- `iva-retenciones-mx`
