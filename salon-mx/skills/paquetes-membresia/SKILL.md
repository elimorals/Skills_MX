---
name: paquetes-membresia
description: Diseño de paquetes y membresías para salones, estéticas y spas mexicanos (3-faciales, 6-cortes-niño, mensualidad spa ilimitado, anual VIP). Calcula descuento óptimo según churn, vigencia, días de uso, recargo por servicio no usado, condiciones de cancelación PROFECO-friendly, y emisión de CFDI por suscripción mensual o cobro completo upfront. Usar cuando el usuario diga paquete servicios, membresía, suscripción salón, mensualidad spa, bono prepago, anualidad VIP. NO usar para servicios sueltos (servicios-tarifario) ni loyalty puntos (retencion-clientes-loyalty).
allowed-tools: Read, Write, Edit
---

# Paquetes y membresías

Aumentan ingresos predecibles + cierran al cliente por adelantado.

## Tipos de paquete

### A. Bono de servicios (prepago + descuento)

Cliente paga upfront 5 servicios al precio de 4:

```
{
  "tipo": "bono_corte_x6",
  "servicios_incluidos": 6,
  "vigencia_dias": 180,
  "precio_total_mxn": 1800,  # vs 6 × $400 = $2400 → ahorro 25%
  "descuento_porcentaje": 0.25,
  "cancelable": "después del 3er servicio usado",
  "extension_posible": "30 días con $200 MXN"
}
```

### B. Membresía mensual (todo incluido)

Cliente paga $X al mes y consume servicios ilimitados:

```
{
  "tipo": "membresia_spa_completa",
  "precio_mensual_mxn": 1500,
  "vigencia": "mensual con renovación automática",
  "incluye": ["1 facial/mes", "2 masajes/mes", "uso ilimitado área húmeda"],
  "no_incluye": ["tratamientos láser", "productos retail"],
  "limites_uso_anti_abuso": "máx 4 servicios/mes por categoría",
  "cancelacion_30_dias_aviso": true
}
```

### C. Membresía VIP anual

Cliente paga anualmente y obtiene mejores precios + extras:

```
{
  "tipo": "vip_anual",
  "precio_anual_mxn": 18000,
  "descuento_servicios_carta": 0.15,
  "incluye_extras": [
    "12 cortes/año gratis",
    "4 tratamientos hidratación gratis",
    "Prioridad en agenda",
    "Acceso a eventos exclusivos"
  ],
  "cancelacion": "reembolso prorrateado solo en mes 1"
}
```

### D. Paquete novia / quinceañera

```
{
  "tipo": "paquete_novia",
  "precio_total_mxn": 5500,
  "servicios": [
    "Prueba peinado (1 sesión)",
    "Día evento: maquillaje + peinado",
    "Tratamiento previo (1 hidratación)",
    "Manicure pre-evento"
  ],
  "no_reembolsable_24_dias_antes": true
}
```

### E. Paquete corporativo (servicio para grupo)

Para empresas que reservan para varios empleados:

```
{
  "tipo": "corporate_express",
  "min_servicios": 5,
  "descuento_volumen": 0.20,
  "factura_unica": true,
  "uso_cfdi": "G03 — Gastos en general"
}
```

## Cálculo del descuento óptimo

### Para bonos prepago
Punto de equilibrio: el descuento debe ser menor que el costo de adquirir un cliente nuevo.

```
descuento_max = (CAC + costo_oportunidad_silla) / servicios_promedio
```

Si CAC = $300 y servicios promedio por cliente = 4:
- Descuento máximo = $300 / 4 = $75 por servicio (≈18% de un servicio $400)
- **Conclusión**: bono 6×$400 con 25% descuento sale del rango ideal — ajustar a 18-20%

### Para membresías mensuales
Punto de equilibrio: ingreso debe cubrir costo variable + asegurar margen.

```
ingreso_mensual_minimo = costo_servicios_promedio_mes + margen_objetivo
```

## Riesgos a manejar

### 1. Sobreuso (abuso)
Cliente consume todo el límite en primera semana. Configurar:
- Máximo 1 servicio por semana
- Reserva con 48h anticipación obligatoria
- Saltar reservas: pierde el servicio

### 2. Cliente fantasma
Paga pero no usa. Bueno para flujo pero malo para reputación:
- Reminders WhatsApp mes 1 y 3
- Si no usa en 60 días, ofrecer credit transferible

### 3. Cancelación prematura
PROFECO permite reclamo. Política clara:
- Hasta 7 días: reembolso 100% (Art. 56 LFPC)
- 8-30 días: prorrateo (servicios usados a precio carta)
- 30+ días: no reembolsable, pero credit usable 90 días

### 4. Membresía sin renovar
Auto-renueva por default con consentimiento previo (Art. 76 bis LFPC):
- Pre-aviso 30 días antes
- Email + WhatsApp
- Opt-out fácil (no fricción intencional)

## Implicaciones fiscales (CFDI)

### Bonos prepago
- CFDI emitido al cobrar (anticipo)
- UsoCFDI: G03 (gastos generales) si cliente quiere deducir
- Al usar el servicio: emitir CFDI relacionado o nota interna

### Membresía mensual
- CFDI mensual recurrente
- Forma de pago: 28 (Tarjeta de débito) o 03 (Transferencia)
- Si pago anual upfront: emitir CFDI completo con leyenda "Membresía anual 12 meses"

### Anualidad VIP
- Opción A: CFDI total al cobrar (más simple, cliente lo deduce 100% en el año)
- Opción B: 12 CFDIs mensuales (mejor flujo contable pero más operativo)

## Output estructurado

```json
{
  "paquete_creado": {
    "tipo": "membresia_facial_x3_mes",
    "precio_total_mxn": 1500,
    "precio_individual_equivalente": 600,
    "descuento_efectivo": 0.17,
    "vigencia_dias": 90,
    "punto_equilibrio_servicios": 2.5,
    "margen_proyectado": 0.62,
    "cancelable": true,
    "auto_renueva": false
  },
  "analisis_riesgo": {
    "max_sobreuso_proyectado": "12 servicios/cliente",
    "valor_real_proyectado_mxn": 1200,
    "rentable_si_clientes_usan": "< 2.5 servicios promedio",
    "tasa_uso_target": 0.83
  },
  "implicaciones_cfdi": [
    "Emitir CFDI al cobrar (anticipo) si pago upfront",
    "UsoCFDI G03 para deducibilidad cliente",
    "Bitácora interna de servicios consumidos"
  ]
}
```

## Validación pendiente

- Tasas de uso real de paquetes en salones MX
- Cláusulas legales válidas según Art. 56-76 LFPC
- Mejores prácticas de auto-renovación post-reforma Art. 76 bis
