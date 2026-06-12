---
name: retencion-clientes-loyalty
description: Programa de retención de clientes para salones mexicanos con sistema de puntos por consumo (1 punto = $1 MXN gastado, 100 puntos = $50 descuento), niveles (bronce/plata/oro/platino) con beneficios escalonados, descuentos por visita N (5ta visita 20%, 10ma free service), recordatorios automáticos al cliente que no regresa en N días, programa de referidos (refiero amigo → ambos ganan), análisis de churn. Usar cuando el usuario diga loyalty, puntos cliente, programa referidos, churn, retención, no me visitan, clientes inactivos. NO usar para paquetes prepago (paquetes-membresia) ni cita individual (agenda-citas-salon).
allowed-tools: Read, Write, Edit
---

# Retención y loyalty — salones MX

Adquirir clientes nuevos cuesta 5x más que retener. La retención es el mejor multiplicador.

## Sistema de puntos

### Acumulación
- 1 punto por cada $10 MXN gastado en servicios
- Productos retail: 1 punto por cada $20 MXN (margen menor)
- Bonos prepago: solo si el cliente USA el servicio (no al pagar)
- Referidos cerrados: 100 puntos extra

### Redención
- 100 puntos = $50 MXN descuento
- 250 puntos = $150 MXN descuento + corte gratis
- 500 puntos = servicio premium completo (tinte, mechas, facial)
- 1000 puntos = anualidad descuento 30%

### Vigencia
- Puntos NO expiran si el cliente visita cada 90 días
- Si pasa > 90 días sin visitar: puntos se reducen 10% mensualmente
- Si pasa > 180 días: puntos se cancelan

## Niveles (tiers)

### 🟫 Bronce (0-500 puntos acumulados YTD)
- Sin beneficios extra
- Cliente nuevo

### 🥈 Plata (501-1,500 YTD)
- 5% descuento permanente en productos
- Prioridad reservación 24h ventana
- Cumpleaños: corte gratis

### 🥇 Oro (1,501-3,000 YTD)
- 10% descuento permanente en servicios
- Prioridad reservación 48h
- Cumpleaños: paquete cumpleaños (corte + peinado + manicure)
- 1 servicio express al mes (no fila)

### 💎 Platino (3,001+ YTD)
- 15% descuento permanente
- Reservación prioritaria 1 semana ventana
- Estilista preferido garantizado
- 2 servicios premium gratis al año
- Acceso a eventos VIP del salón

Cliente sube de nivel automáticamente. Mantiene el nivel todo el año + reset enero.

## Recordatorios para retención

### Algoritmo
Track de "frecuencia esperada" por cliente:

```
frecuencia_promedio_personal = ventana_entre_ultimas_4_visitas
si dias_desde_ultima_visita > frecuencia_promedio_personal × 1.2:
  estado = "tarde_para_visitar"
  enviar WhatsApp con CTA
```

### Templates por tipo

**Cliente activo se atrasa** (ventana 7-15 días post-esperado):
> "Hola Ana 👋 ¿cómo va tu cabello? Nuestro estilista Carla preguntó por ti. Te apartamos un slot esta semana si quieres pasar."

**Cliente al borde de churn** (30+ días tarde):
> "Hola Ana 👋 hace 6 semanas que no te vemos. Tenemos algo nuevo: tratamiento {{producto_nuevo}} con 20% off para ti esta semana. ¿Te apartamos cita?"

**Cliente perdido** (90+ días):
> "Ana, te extrañamos! Estamos lanzando {{X}} y queremos que seas de las primeras. Cita gratis para reconectar."

⚠ No usar más de 1 recordatorio cada 2 semanas. Riesgo de spam → cliente bloquea WhatsApp.

## Programa de referidos

### Mecánica
- Cliente refiere a amigo con código personal
- Amigo va, completa primer servicio
- Ambos reciben beneficio

### Modelo de beneficio
- **Quien refiere**: 200 puntos (≈ $100 descuento) si amigo gasta > $500
- **Quien fue referido**: 20% descuento en primer servicio (nuevo cliente)

### Tracking
Código único por cliente actual: `REF-ANA-2026` (visible en su perfil + WhatsApp)

## Análisis de churn

### Métricas a monitorear

| Métrica | Cómo medir | Target |
|---|---|---|
| Tasa de retorno 90 días | % de clientes que vuelven en 90 días | > 70% |
| Frecuencia promedio | Días entre visitas | < 60 |
| LTV (Lifetime Value) | Suma promedio gastada por cliente / año | depende del salón |
| Churn rate | % clientes que no vuelven en 180 días | < 25% |
| CAC | Costo adquirir cliente nuevo | < 20% LTV |

### Identificar clientes en riesgo

Semanal: lista de clientes que:
- Tiempo desde última visita > frecuencia personal × 1.5
- Total gastado YTD > $X (vale la pena recuperar)
- NO han recibido recordatorio en últimas 2 semanas

Acción: WhatsApp personalizado, oferta retención, llamada del dueño.

## Costo del programa loyalty

| Item | Costo |
|---|---|
| Descuentos otorgados | 8-15% del revenue |
| Cumpleaños regalos | $50 por cliente activo / año |
| Referidos pagados | 5-10% revenue de clientes nuevos |
| Software de tracking | $300-800 MXN/mes (Loyverse, Vagaro, etc.) |

**ROI esperado**: tasa de retención sube 15-25% → LTV sube 30-50%.

## Output estructurado

```json
{
  "analisis_loyalty": {
    "periodo": "2026-Q1",
    "clientes_activos": 287,
    "tier_distribucion": {
      "bronce": 145,
      "plata": 92,
      "oro": 38,
      "platino": 12
    },
    "tasa_retencion_90d": 0.72,
    "tasa_churn_180d": 0.21,
    "frecuencia_promedio_dias": 52,
    "ltv_promedio_mxn": 4800,
    "cac_promedio_mxn": 320,
    "ratio_ltv_cac": 15.0,
    "referidos_cerrados": 18,
    "revenue_de_referidos": 12400.00
  },
  "clientes_riesgo_churn": [
    {
      "id_cliente": "C-1234",
      "ultima_visita": "2025-12-10",
      "frecuencia_personal_dias": 45,
      "dias_tarde": 60,
      "ltv_acumulado_mxn": 8400,
      "accion_recomendada": "WhatsApp con 25% off en próximo servicio + llamada del dueño"
    }
  ],
  "alertas": [
    "8% de Oro/Platino se atrasan más de 30 días — riesgo crítico",
    "Tasa de referidos cerrada cayó 30% mes anterior"
  ]
}
```

## Validación pendiente

- Tasa de churn típica salones MX (10-30% rango)
- LTV promedio por tipo de salón
- Comparativo software loyalty: Loyverse, Vagaro, Square, Wepoint
- Mejores prácticas en aceptación de programa (qué % se inscribe)
