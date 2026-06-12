---
name: cotizacion-boda-mxn
description: Cotización detallada de boda en MXN con desglose por capítulos (banquete, locación, decoración, música, fotografía, video, vestido, transporte, hospedaje, papelería, novios, otros). Considera invitados (típico 150-500 MX), tipo de evento (civil, religioso, ambos), día (sábado premium, jueves descuento), temporada (Nov-Feb alta, May-Ago baja), región (CDMX/GDL premium, ciudad interior media). Genera presupuesto realista con rangos low/mid/high. Usar cuando el usuario diga cotizar boda, presupuesto evento, cuánto cuesta una boda, paquete invitados, evento privado MX. NO usar para timeline (otro skill) ni contratos (contrato-boda-pf-pm).
allowed-tools: Read, Write, Edit
---

# Cotización de boda en MXN

## Estructura por capítulos

```json
{
  "capitulo": "banquete",
  "concepto": "Menú boda 3 tiempos",
  "invitados": 200,
  "precio_unitario_mxn": 1200,
  "subtotal_mxn": 240000,
  "incluye": [
    "Entrada (sopa o ensalada)",
    "Plato fuerte (a elegir 2 opciones: carne + pollo o pescado)",
    "Postre",
    "Mesero por cada 15 invitados",
    "Mantelería estándar"
  ],
  "no_incluye": [
    "Bebidas alcohólicas (cobertura aparte)",
    "Vino mesa",
    "Mesa de dulces"
  ]
}
```

## Capítulos típicos

### 1. Banquete + bebidas (40-50% del presupuesto total)
- Menú por persona (3 tiempos típico)
- Cobertura barra: open bar (8-12h) por invitado
- Vino mesa (1 botella por cada 3-4 personas)
- Mesa de dulces / candy bar
- Mesa de tequila / mezcal
- Pastel de boda

### 2. Locación (15-25%)
- Hacienda, jardín, salón, hotel
- Renta del lugar (varía mucho: $30k-300k)
- Incluye o no mobiliario, vajilla, valet

### 3. Decoración + flores (10-15%)
- Centros de mesa
- Camino al altar
- Arco floral
- Iluminación ambiente
- Mobiliario lounge

### 4. Música / DJ / banda (5-10%)
- DJ paquete básico
- Banda live
- Mariachis (mexicano clásico)
- Sonido ceremonia

### 5. Fotografía + video (5-10%)
- Fotógrafo (8-12h)
- Video (drone, cinematic)
- Cabina foto invitados
- Álbum impreso

### 6. Vestido + accesorios novia (3-7%)
- Vestido principal
- Velo + accesorios
- Vestido para fiesta (cambio)
- Maquillaje + peinado día del evento

### 7. Traje novio (1-3%)
- Traje a medida o renta
- Zapatos, mancuernillas, accesorios

### 8. Anillos / arras (1-3%)
- Anillos de boda
- Arras matrimoniales

### 9. Transporte + hospedaje (3-7%)
- Limousina / vehículo novios
- Hospedaje invitados destino
- Transporte invitados desde hotel

### 10. Papelería + ceremonia (2-4%)
- Invitaciones físicas
- Save-the-dates
- Programas ceremonia
- Souvenirs invitados
- Honorarios juez civil + sacerdote / pastor

### 11. Coordinación + planeación (8-15%)
- Wedding planner full
- Asistente day-of
- Coordinación con proveedores
- Manejo timeline

### 12. Otros / imprevistos (5-10%)
- Buffer obligatorio para imprevistos
- Propinas a equipo (10-15% propinable)

## Benchmark de costos en MX (2026 referencia)

⚠ Rangos amplios por región y tipo de evento. CDMX/GDL/MTY/destino-Cancún son premium.

### Boda 200 invitados — CDMX

| Capítulo | Low | Mid | High |
|---|---|---|---|
| Banquete + bebidas | $300k | $480k | $850k |
| Locación | $80k | $180k | $400k |
| Decoración + flores | $40k | $90k | $200k |
| Música DJ | $25k | $60k | $150k |
| Fotografía + video | $30k | $70k | $180k |
| Vestido + accesorios | $25k | $60k | $200k |
| Traje novio | $8k | $20k | $60k |
| Anillos | $20k | $50k | $150k |
| Transporte + hospedaje | $20k | $50k | $200k |
| Papelería | $10k | $25k | $60k |
| Coordinación | $40k | $100k | $250k |
| Otros / imprevistos | $30k | $70k | $200k |
| **TOTAL** | **$628k** | **$1.25M** | **$2.9M+** |

Per cápita: $3,140 - $14,500 MXN por invitado (rango común).

### Boda de destino (Tulum, San Miguel, Sayulita)
Premium +30-60% sobre CDMX equivalente. Logística internacional puede sumar $200k+.

## Factores de ajuste

### Día de la semana
- Sábado: precio base
- Viernes: -10%
- Jueves: -20%
- Domingo: -15%
- Lunes-Miércoles: -25-35%

### Temporada
- Alta (Nov-Feb, Mar-Abr): precio base
- Media (May, Sep-Oct): -10%
- Baja (Jun-Ago, lluvias): -20%

### Locación (tipo)
- Hotel 5 estrellas + paquete: premium
- Hacienda con todo: estándar
- Jardín particular: barato pero requiere logística (mobiliario, vajilla, generador)
- Salón social: medio
- Casa de los novios: muy barato pero requiere todo externo

## Output estructurado

```json
{
  "cotizacion_boda": {
    "fecha_evento": "2027-04-18",
    "invitados": 200,
    "ciudad": "CDMX",
    "dia_semana": "sábado",
    "temporada": "alta",
    "modalidad": "civil_y_religiosa",
    "tipo_evento": "estándar mid-premium",
    "capitulos": [
      {
        "capitulo": "banquete",
        "concepto": "Menú 3 tiempos + open bar + mesa dulces",
        "presupuesto_mxn": 480000,
        "porcentaje_del_total": 0.38
      },
      "..."
    ],
    "subtotal_mxn": 1100000,
    "iva_aplicable_mxn": 176000,
    "total_mxn": 1276000,
    "per_capita_mxn": 6380,
    "rango_comparativo": "mid-premium para CDMX 200 invitados",
    "buffer_imprevistos_recomendado_mxn": 100000,
    "presupuesto_recomendado_total_mxn": 1376000
  }
}
```

## Validación pendiente

- Tarifas reales 2026 por proveedor en CDMX, GDL, MTY
- Comparativo costo bodas de destino MX (Tulum, San Miguel, Sayulita)
- Listas de proveedores por región y rango de precios
- Tasas de inflación últimos 3 años en industria bodas

## Ver también

- `proveedores-bda` para gestión de presupuesto vs gastado
- `timeline-evento` para cronograma operativo
- `contrato-boda-pf-pm` para formalización legal
