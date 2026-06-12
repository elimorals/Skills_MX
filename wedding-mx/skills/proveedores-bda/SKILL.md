---
name: proveedores-bda
description: Gestión de proveedores de boda — directorio segmentado por capítulo (banquete, decoración, música, video, etc.), tracking de presupuesto vs gastado por proveedor, anticipos vs pagos restantes con fechas límite, evaluación post-evento (recomendable repetir o blacklist), comparativa de 3 cotizaciones por capítulo. Usar cuando el usuario diga proveedores boda, comparar cotizaciones, pago pendiente proveedor, presupuesto gastado, lista vendedores boda. NO usar para timeline (otro skill) ni contratos individuales (contrato-boda-pf-pm).
allowed-tools: Read, Write, Edit
---

# Gestión de proveedores — bodas MX

## Estructura del proveedor

```json
{
  "id_proveedor": "PROV-2026-0042",
  "nombre_comercial": "Banquetes Demo Premium",
  "razon_social": "Banquetes Demo SA de CV",
  "rfc": "BDP200101AB1",
  "capitulo": "banquete",
  "contacto_principal": {
    "nombre": "Carlos R.",
    "puesto": "Gerente de cuenta",
    "tel_wa": "+5215512345678",
    "email": "carlos@banquetesdemo.mx"
  },
  "datos_fiscales": {
    "regimen_fiscal": "601 — General PM",
    "cp_emision": "11000",
    "uso_cfdi_sugerido": "G03"
  },
  "rating_historico": 4.7,
  "eventos_realizados_propios": 8,
  "blacklisted": false,
  "razon_blacklist": null,
  "comentarios_internos": "Excelente servicio. Negociar tienen 10% descuento volumen > $200k."
}
```

## Comparativa de cotizaciones (3 mínimo por capítulo)

Para cada capítulo, evaluar 3 proveedores con criterios:

| Criterio | Peso |
|---|---|
| Precio | 30% |
| Calidad histórica + reviews | 25% |
| Flexibilidad (cambios sin costo) | 15% |
| Plazo entrega/disponibilidad | 10% |
| Forma de pago aceptada | 10% |
| Inclusiones extra (gratis) | 10% |

```json
{
  "capitulo": "banquete",
  "cotizaciones_comparadas": [
    {
      "proveedor": "Banquetes Demo Premium",
      "precio_persona_mxn": 1200,
      "incluye": ["menu 3 tiempos", "vajilla", "mesero c/15"],
      "no_incluye": ["bebidas alcoholicas", "vino mesa"],
      "rating": 4.7,
      "flexibilidad": "alta (cambios 60 días antes sin costo)",
      "score_total": 8.5
    },
    {
      "proveedor": "Banquetes Standard",
      "precio_persona_mxn": 950,
      "incluye": ["menu 2 tiempos básico"],
      "rating": 4.2,
      "score_total": 7.2
    },
    {
      "proveedor": "Banquetes Premium Plus",
      "precio_persona_mxn": 1800,
      "incluye": ["menu 4 tiempos chef estrella", "todo incluido"],
      "rating": 4.9,
      "score_total": 8.8
    }
  ],
  "recomendacion": "Banquetes Demo Premium — balance precio/calidad/flexibilidad"
}
```

## Tracking de pagos

Por proveedor, registrar:

```json
{
  "proveedor": "Banquetes Demo Premium",
  "contrato_total_mxn": 240000,
  "anticipo_pagado_mxn": 72000,
  "fecha_anticipo": "2026-12-15",
  "pago_intermedio_mxn": 96000,
  "fecha_pago_intermedio_planeado": "2027-02-15",
  "pago_intermedio_pagado": false,
  "pago_final_mxn": 72000,
  "fecha_pago_final_planeado": "2027-04-15",
  "pago_final_pagado": false,
  "ajustes_aplicados": 0,
  "saldo_pendiente_mxn": 168000,
  "alertas_proximos_pagos": [
    "Pago intermedio en 15 días"
  ]
}
```

## Presupuesto total vs gastado

Por capítulo de la boda:

```json
{
  "presupuesto_total_evento": {
    "presupuesto_planeado_mxn": 1200000,
    "gastado_acumulado_mxn": 285000,
    "comprometido_no_pagado_mxn": 580000,
    "disponible_libre_mxn": 335000,
    "buffer_imprevistos_mxn": 120000,
    "alerta_sobreejercicio": false
  },
  "por_capitulo": [
    {
      "capitulo": "banquete",
      "presupuestado_mxn": 480000,
      "comprometido_mxn": 240000,
      "pagado_mxn": 72000,
      "pendiente_pagar_mxn": 168000,
      "alerta": null
    },
    {
      "capitulo": "decoracion",
      "presupuestado_mxn": 100000,
      "comprometido_mxn": 0,
      "pagado_mxn": 0,
      "alerta": "Sin proveedor cerrado aún (D-180 = 6 meses)"
    }
  ]
}
```

## Evaluación post-evento

Por proveedor:

| Criterio | Calificación 1-5 |
|---|---|
| Puntualidad | __ |
| Calidad servicio | __ |
| Comunicación pre-evento | __ |
| Manejo de imprevistos | __ |
| Cumplimiento de contrato | __ |
| Trato con invitados | __ |

Score promedio:
- ≥ 4.5: recomendar fuertemente
- 3.5-4.4: recomendar con caveats
- 2.5-3.4: usar con cuidado
- < 2.5: **BLACKLIST** — no usar de nuevo

## CFDI de proveedores

Cada pago a proveedor debe estar respaldado con CFDI:
- Pago anticipo: CFDI tipo I con MetodoPago PUE
- Pago intermedio: CFDI tipo I PUE
- Pago final: CFDI tipo I PUE

Si el novio (cliente final) pide deducción del evento (no aplica en boda residencial pero sí si la empresa lo paga como evento corporativo): RFC, UsoCFDI G03 + retención si proveedor es PFAE.

## Output estructurado

```json
{
  "dashboard_proveedores": {
    "fecha_evento": "2027-04-18",
    "total_proveedores_cerrados": 8,
    "total_proveedores_pendientes_cerrar": 4,
    "presupuesto_comprometido_mxn": 580000,
    "presupuesto_pagado_mxn": 285000,
    "presupuesto_pendiente_pagar_mxn": 295000,
    "alertas_proximos_pagos_30d": [
      {
        "proveedor": "Banquetes Demo",
        "monto_mxn": 96000,
        "fecha_limite": "2027-02-15"
      }
    ],
    "capitulos_sin_proveedor_cerrado": ["decoracion", "transporte"],
    "advertencias": [
      "Capítulo decoración sin proveedor cerrado y faltan 6 meses",
      "Capítulo transporte sin proveedor (puede esperar pero no más de D-90)"
    ]
  }
}
```

## Validación pendiente

- Lista verificada de proveedores recomendados por ciudad MX
- Casos de fraude/incumplimiento típicos en industria bodas MX
- Cláusulas estándar para proteger al cliente final
