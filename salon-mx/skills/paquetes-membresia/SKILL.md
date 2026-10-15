---
name: paquetes-membresia
description: Diseño de paquetes y membresías para salones, estéticas y spas mexicanos (3-faciales, 6-cortes-niño, mensualidad spa ilimitado, anual VIP). Calcula descuento óptimo según churn, vigencia, días de uso, recargo por servicio no usado, condiciones de cancelación conforme a la LFPC (incluye la reforma de cobros recurrentes DOF 12-12-2025), y emisión de CFDI por suscripción mensual o cobro completo upfront. Usar cuando el usuario diga paquete servicios, membresía, suscripción salón, mensualidad spa, bono prepago, anualidad VIP. NO usar para servicios sueltos (servicios-tarifario) ni loyalty puntos (retencion-clientes-loyalty).
allowed-tools: Read, Write, Edit
---

# Paquetes y membresías

Aumentan ingresos predecibles + cierran al cliente por adelantado.

## Tipos de paquete

### A. Bono de servicios (prepago + descuento)

Cliente paga upfront 6 servicios con 25% de descuento (6 × $400 = $2,400 → $1,800):

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

La parte no reembolsable debe ser proporcional al costo real (agenda bloqueada, prueba ya hecha); retener el 100% sin servicio prestado puede considerarse cláusula abusiva (Art. 10 LFPC).

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
PROFECO atiende quejas por cancelación y cobros. Política clara, por escrito y entregada **antes** de cobrar:
- Hasta 7 días sin uso: reembolso 100% (política comercial sugerida)
- 8-30 días: prorrateo (servicios usados a precio carta)
- 30+ días: no reembolsable, pero crédito usable 90 días

Marco legal (LFPC, última reforma DOF 12-12-2025):
- **Art. 56 LFPC** (5 días hábiles para revocar sin responsabilidad) aplica solo a ventas **fuera del establecimiento** o a distancia (Art. 51), p. ej. un paquete vendido por teléfono o en un evento externo; no aplica si el servicio se presta dentro de 10 días hábiles. No es un derecho general para ventas en mostrador.
- **Art. 10 LFPC**: no se pueden hacer cargos sin consentimiento ni cláusulas abusivas; **Art. 90** invalida cláusulas que permitan al salón modificar el contrato o sustraerse de sus obligaciones unilateralmente.
- **Art. 7 BIS**: el precio exhibido debe ser el total (IVA incluido).
- Salones de belleza y spas **no** están en la lista de contratos de adhesión con registro obligatorio ante PROFECO (NOM-174-SCFI-2007 cubre, entre otros, eventos sociales y tintorerías; confianza media, fuente: IDC Online). El registro voluntario es posible.

### 4. Membresía sin renovar / cobro recurrente
Desde la reforma a la LFPC del **DOF 12-12-2025 (Art. 76 BIS fr. VIII y IX)**, cuando la membresía se contrata o cobra por medios electrónicos:
- Informar de forma clara y destacada que hay cobro automático recurrente, su periodicidad, monto y fecha.
- Obtener **consentimiento expreso e informado** para el cargo recurrente.
- Si hay renovación automática: avisar **al menos 5 días naturales antes** y permitir cancelar sin penalización (sugerido: aviso a 30 y a 5 días, por email + WhatsApp).
- Ofrecer un mecanismo para cancelar **de manera inmediata** (sin fricción intencional).

## Implicaciones fiscales (CFDI)

El IVA se causa y el ingreso se acumula cuando se **cobra** (Art. 17 LIVA), así que el CFDI se emite al cobro, no al consumo.

### Bonos prepago
- Si al cobrar ya están definidos los servicios y el precio (bono de 6 cortes por $1,800): CFDI de ingreso por la venta del paquete, PUE con la forma de pago real. No es "anticipo".
- El esquema de anticipo (CFDI de anticipo + CFDI de la operación con relación 07 + CFDI de egreso) solo aplica cuando al cobrar **no** se sabe qué servicio o precio se dará (p. ej. "saldo a favor" libre). Ver `cfdi-emision`.
- Al usar cada servicio: bitácora interna, no otro CFDI.
- UsoCFDI: G03 si el cliente lo pide; S01 si no tiene efectos fiscales. Ojo: los servicios de estética no son deducción personal de la PF y rara vez son deducibles para una empresa; no prometas deducibilidad.

### Membresía mensual
- Un CFDI por cada cobro mensual.
- Forma de pago: 04 (tarjeta de crédito), 28 (tarjeta de débito) o 03 (transferencia), según el medio real.

### Anualidad VIP pagada por adelantado
- Un CFDI por el total al cobrar (con leyenda "Membresía anual 12 meses"). No se puede "partir" en 12 CFDIs mensuales si el dinero ya se cobró completo.
- 12 CFDIs mensuales solo si el cobro también es mensual.

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
    "max_sobreuso_proyectado": "3 servicios/cliente (todo el paquete)",
    "valor_real_proyectado_mxn": 1200,
    "rentable_si_clientes_usan": "< 2.5 servicios promedio",
    "tasa_uso_target": 0.83
  },
  "implicaciones_cfdi": [
    "Emitir CFDI de ingreso PUE por el paquete completo al cobrar (servicios y precio definidos)",
    "UsoCFDI G03 o S01 según lo pida el cliente; no prometer deducibilidad",
    "Bitácora interna de servicios consumidos"
  ]
}
```

## Validación pendiente

- Tasas de uso real de paquetes en salones MX
- Si PROFECO emite lineamientos o NOM para aplicar el Art. 76 BIS fr. VIII-IX (reforma DOF 12-12-2025)

⚠ Validar los términos y condiciones con abogado y el tratamiento CFDI con contador antes de vender paquetes.
