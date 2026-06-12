---
name: comparador-renta-zona-dinamica
description: Compara el precio de renta actual de un inmueble contra inmuebles equivalentes (mismas habitaciones, baños, m², cajones de auto, amenidades, antigüedad) en un radio de 1-3 km usando mp_inmuebles24 + mp_vivanuncios y portales adicionales scrapeables, para sugerir ajuste anual al arrendador con datos objetivos en lugar de subir solo por INPC inflación. Detecta el percentil de tu renta en la zona (estás en P25 → puedes subir agresivo, P75 → ya estás caro), proyecta tasa de ocupación post-ajuste (si subes 10% probablemente queda 1 mes vacío = pierdes lo que ganas), genera mensaje persuasivo al inquilino con datos comparativos (3-5 propiedades similares más caras) para justificar el ajuste sin sonar abusivo, y considera el costo emocional de cambiar inquilino bueno vs marginal de mantener (un mes vacío + tiempo búsqueda nuevo + riesgo malo cliente vs $X mensual extra). Usar cuando el usuario diga "ajustar renta", "comparador renta zona", "subir precio departamento", "renta vs mercado", "comparables renta", "precio mi depa". NO usar para tasación de venta (eso es distinto, valuador certificado).
allowed-tools: Read, Write, Edit
---

# Comparador dinámico de renta por zona

## Flujo

1. **Características del inmueble**: m², habitaciones, baños, cajones, planta, amenidades (alberca, gym, seguridad), antigüedad
2. **Búsqueda comparables**: mp_inmuebles24 + mp_vivanuncios en radio 1-3km
3. **Filtrado**: solo los con características ≥80% similares
4. **Análisis percentil**: tu precio actual está en qué percentil del mercado
5. **Proyección de impacto**: si subes X%, ¿probabilidad de quedar vacío?
6. **Generación de propuesta**: mensaje persuasivo al inquilino con datos

## Output ejemplo

```
🏠 Comparador — Depa Polanco 2/2/1 65m²

PRECIO ACTUAL: $14,500 MXN/mes
ZONA (1km radio):
  - Mínimo: $12,000 (P0)
  - P25: $13,800
  - Mediana: $15,400 ← tu inmueble está -6% bajo
  - P75: $17,200
  - Máximo: $24,500 (P100)

PERCENTIL ACTUAL: 35 → puedes subir 5-8% sin estar caro

5 COMPARABLES SIMILARES MÁS CAROS:
  1. Polanco Reforma 234 — 2/2/1 62m² — $15,800
  2. Polanco Anatole France — 2/2/1 66m² — $16,200
  3. Polanco Schiller — 2/2/1 65m² — $15,500
  4. Polanco Goethe — 2/2/1 63m² — $16,800
  5. Polanco Tennyson — 2/2/1 68m² — $17,200

SUGERENCIA AJUSTE: $15,400 (+6.2%) — quedas en mediana
INPC últimos 12m: +4.8% → tu ajuste sí supera inflación

PROYECCIÓN OCUPACIÓN si subes:
  - +6.2%: 95% probabilidad inquilino acepta (renta razonable mercado)
  - +10%: 70% probabilidad inquilino acepta
  - +15%: 40% probabilidad — riesgo 1-2 meses vacío

COSTO MES VACÍO: $14,500 (lo que pierdes si se va el inquilino)
GANANCIA por subir +6.2%: $900/mes × 12 = $10,800/año
GANANCIA por subir +10%: $1,450/mes × 12 = $17,400/año
RIESGO de subir +10%: 30% × $14,500 × 1.5 mes = $6,525 esperado

RECOMENDACIÓN ÓPTIMA: subir $900 (+6.2%) si tu inquilino es bueno
```

## Mensaje propuesto al inquilino

```
Hola [Nombre],

Como sabes, en mayo se cumple un año del contrato y toca renovación. Quería pasarte una propuesta de ajuste con datos objetivos:

Hice un comparativo con 5 propiedades similares a la tuya en la zona (mismos m², habitaciones, baños). Estoy adjuntando capturas.

Tu renta actual ($14,500) está 6% por debajo de la mediana de mercado ($15,400). El ajuste que estoy proponiendo es a $15,400 — exactamente la mediana — un incremento de $900 mensuales (6.2%).

Esto está acorde a:
- Inflación INPC últimos 12m: 4.8%
- Mediana de mercado actual

Para que te quedes tranquilo de que es justo, te paso las 5 propiedades comparables.

¿Cómo lo ves? Si te parece, formalizamos para el siguiente periodo.

Saludos
```

## Validación pendiente

⚠ Comparables se ven afectados por estacionalidad — siempre filtrar últimos 60 días.
⚠ Considerar incentivos no monetarios (no subir si paga puntual 12 meses, etc.).
