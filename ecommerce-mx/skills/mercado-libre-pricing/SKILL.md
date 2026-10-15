---
name: mercado-libre-pricing
description: Cálculo de precio para publicaciones en Mercado Libre México considerando cargo por venta según tipo de publicación (Clásica / Premium) y categoría, cargo fijo por unidad en productos de bajo precio, IVA incluido en el precio publicado, costo logístico, retenciones de ISR e IVA que hace la plataforma (Art. 113-A LISR, LIF 2026 y 18-J LIVA), margen deseado y precio de competidores. Usar cuando el usuario diga precio mercado libre, pricing ML, qué precio pongo, comisión mercado libre, cuánto me cobra ML, margen ML, retención ML, competidores ML, optimizar precios. NO usar para crear publicaciones (skill mercado-libre-listings).
allowed-tools: Read, Write, Edit, Bash
---

# Mercado Libre — Pricing

El precio en ML se obtiene a la inversa: costo + cargos de ML + margen, todo sobre un precio publicado que **ya incluye IVA** (Art. 7 Bis LFPC: el proveedor debe mostrar el monto total con impuestos).

## Cargos de Mercado Libre — no uses tablas memorizadas

ML cobra, por cada venta:

1. **Cargo por venta**: porcentaje según **categoría** y **tipo de publicación**. Premium cuesta más que Clásica porque ofrece meses sin intereses al comprador.
2. **Cargo fijo por unidad** en productos por debajo de un umbral de precio (escalonado).
3. **Envío**: arriba de cierto precio el envío es gratis para el comprador y el vendedor absorbe parte del costo; Mercado Envíos Full cobra además almacenamiento y otros cargos propios. No es un "+5%" fijo.

Los porcentajes, umbrales y montos cambian varias veces al año. **Verificar siempre** antes de calcular:
- Página oficial: `https://www.mercadolibre.com.mx/ayuda/costos-de-vender-un-producto_870` (no se pudo consultar automáticamente el 2026-10-15; pide al usuario el dato o captura).
- Panel del vendedor: la simulación de "Cuánto recibes" al publicar.
- API pública de ML (fuera del MCP del repo): `GET /sites/MLM/listing_prices?price=<p>&category_id=<id>&listing_type_id=gold_special|gold_pro` devuelve el cargo exacto.

El MCP `mp_mercado_libre` **no** tiene tool de comisiones ni de búsqueda de competidores. Sus tools útiles aquí: `mercadolibre_get_item` (precio, tipo de publicación, categoría), `mercadolibre_update_price` y `mercadolibre_get_seller_reputation`. Su estado es "real sin validar (requiere credenciales OAuth)"; sin credenciales trabaja con datos que el usuario pegue.

## Retenciones que hace la plataforma (2026)

Mercado Libre, Amazon y cualquier plataforma que cobre por cuenta del vendedor retienen sobre el ingreso cobrado **sin IVA**:

| Vendedor | ISR | IVA | Fuente |
|---|---|---|---|
| PF con RFC (Art. 113-A fr. III) | **2.5%** (sustituye al 1% de la LISR durante 2026) | 50% del IVA cobrado | LIF 2026 Art. 25 fr. VI (DOF 07-11-2025); Art. 18-J fr. II a) LIVA |
| PF sin RFC | 20% | 100% del IVA | Art. 113-C fr. IV LISR; Art. 18-J fr. II a) LIVA |
| PM con RFC | **2.5%** sin deducción, acreditable en pagos provisionales/anual | 50% del IVA cobrado (18-J fr. II a) LIVA, extendido a PM) | LIF 2026 Art. 25 fr. VI (ISR) y fr. IX a) (IVA) |
| PM sin RFC | 20% | verificar (la LIF no fija 100% para PM sin RFC) | LIF 2026 Art. 25 fr. VI |

- La PF con ingresos ≤ $300,000 el año anterior (solo por plataformas) puede optar por que la retención de ISR sea **pago definitivo** (Art. 113-B LISR); IVA definitivo en el supuesto del Art. 18-M LIVA.
- Retención de IVA del 100% si el vendedor cobra en cuentas bancarias en el extranjero o es residente en el extranjero sin establecimiento (LIF 2026 Art. 25 fr. IX b-c).
- Las retenciones no son costo si se acreditan; sí afectan **flujo de efectivo**. Mostrarlas aparte del margen.
- Validar con contador antes de declarar: las tasas de la LIF son anuales y pueden cambiar en 2027.

## Fórmula

Con `P` = precio publicado con IVA, `c` = cargo por venta (decimal), `f` = cargo fijo por unidad, `m` = margen objetivo sobre ingreso sin IVA, costos sin IVA:

```
P = (costo_articulo + costo_logistico + f) / ((1 - m) / 1.16 - c)
```

Ejemplo ilustrativo (cargo por venta **hipotético** 17%, sin cargo fijo porque el precio queda arriba del umbral):

```
costo 250 + logística 80 = 330
denominador = (1 - 0.20) / 1.16 - 0.17 = 0.68966 - 0.17 = 0.51966
P = 330 / 0.51966 = $635.04  → publicar $635

Comprobación:
  ingreso sin IVA = 635.04 / 1.16 = 547.45
  cargo ML        = 0.17 × 635.04 = 107.96
  utilidad        = 547.45 - 107.96 - 330 = 109.49 → 20.0% de 547.45 ✓
  retención ISR PF 2.5% = 13.69 (anticipo) · retención IVA 50% = 43.80 (anticipo)
```

La IVA que ML traslada sobre su cargo es acreditable; por eso el cargo entra sin IVA.

## Análisis competitivo

Sin tool de búsqueda en el MCP, pide al usuario 5-20 precios de competidores (o la exportación de una herramienta de inteligencia de mercado) y:

1. Filtra por tipo de publicación, envío Full o no y reputación similar.
2. Calcula P25, mediana, P75.
3. Posición: P25-P50 = volumen; P50-P75 = equilibrio; >P75 solo con diferenciador (Full, garantía, marca).
4. Si tu `P` de equilibrio queda arriba de P75, el problema es costo o canal, no precio.

La reputación (`mercadolibre_get_seller_reputation`) influye en exposición, pero ML no publica un "boost" numérico: no lo inventes.

## Estrategias

- **Clásica vs Premium del mismo producto**: compara el ingreso neto de ambas con los cargos reales.
- **Kits / multipack**: subir el ticket por encima del umbral del cargo fijo puede bajar el costo por unidad. Ej.: 3 piezas a $450 en vez de 1 a $150.
- **Precio psicológico**: $1-5 bajo el competidor mejor posicionado, solo si tu margen lo soporta.
- **Meses sin intereses**: en Premium el costo ya está en el cargo; fuera de eso, el costo de MSI de Mercado Pago es variable — **verificar** en el panel antes de prometer MSI.

## IVA y CFDI

- El vendedor emite el CFDI de la venta: a RFC del comprador si lo pide, o en CFDI global a público en general (ver `cfdi-emision`).
- ML emite al vendedor CFDI por sus cargos y el **CFDI de retenciones** (ISR/IVA) que se usa para acreditar.
- Si vendes en región fronteriza con estímulo autorizado, la tasa puede ser 8% (ver `iva-retenciones-mx`).

## Output estructurado

```json
{
  "analisis_precio": {
    "listing_id": "MLM1234567890",
    "costos_sin_iva": {"articulo": 250.00, "logistico": 80.00, "cargo_fijo": 0.00},
    "cargos_ml": {"tipo_publicacion": "premium", "cargo_por_venta": 0.17, "fuente": "panel vendedor 2026-10-15"},
    "precio_equilibrio_margen_20": 635.04,
    "competidores": {"p25": 589.00, "mediana": 629.00, "p75": 679.00},
    "retenciones_estimadas": {"isr_2_5": 13.69, "iva_50": 43.80},
    "recomendacion": "publicar $635 (mediana)",
    "alertas": ["Cargo por venta tomado del panel; recalcular si cambia la categoría"]
  }
}
```

## Ver también

- `mercado-libre-listings` · `mxn-formato` · `iva-retenciones-mx` · `cfdi-emision`
