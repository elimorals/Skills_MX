---
name: cobranza-terapia-recurrente-tele
description: Cobranza recurrente para pacientes en seguimiento o terapia psicológica remota (sesiones semanales). Pre-pago obligatorio típico, descuentos por paquete (4 sesiones = mes), cobranza escalada empática si paquete no se completa. Diferencia con consulta puntual: relación continua que requiere preservar. Usar cuando el usuario diga cobranza terapia tele, mensualidad paciente online, recurrente telemedicina.
allowed-tools: Read, Write
---

# Cobranza recurrente terapia / telemedicina

## Modelos típicos

### A. Por sesión (pre-pago)
- $X por sesión, pagado antes
- Mayor flexibilidad pero menos compromiso
- Más cancelaciones

### B. Paquete mensual (4 sesiones)
- Descuento 10-15% vs sesión individual
- Pago a inicio de mes
- Mejor adherencia
- Si paciente cancela mid-mes: política clara

### C. Paquete trimestral (12 sesiones)
- Descuento 15-20%
- Para pacientes comprometidos largo plazo
- Reembolso pro-rateado si cancela

## Cobranza escalada

| Días | Nivel | Tono |
|---|---|---|
| D-2 | Recordatorio | Cordial: "Recordatorio renovación paquete" |
| D+1 | Sin pago | Amable: "¿pasa algo? te quiero apoyar" |
| D+3 | Insistencia | Firme pero empática |
| D+7 | Pausa | "Pausa temporal hasta regularizar — entiendo si necesitas espacio" |

⚠ Más de 2 sesiones impagas → conversación EN SESIÓN, no por mensaje.

## Plantillas

### Nivel 1 (D-2 renovación)
```
Hola [Nombre], pasando a recordarte que el [día] empieza el nuevo
ciclo. Como acordamos: 4 sesiones mensuales × $[X] = $[Total].

Puedes hacer el depósito a la cuenta de siempre. Aquí estoy si
necesitas algo. 💙
```

### Nivel 2 (D+1 sin pago)
```
Hola [Nombre], aún no he visto el pago del ciclo de este mes. 
¿Pasa algo? Si necesitas posponer o platicar de algún ajuste,
aquí estoy.
```

### Nivel 3 (D+3 con pausa)
```
[Nombre], como no ha sido posible regularizar el pago de este 
mes, vamos a pausar las sesiones hasta que estés listo/a para
retomarlas. Sin presión. Cuando quieras retomar, sólo escríbeme.
Te mando un abrazo.
```

## Output

```json
{
  "paciente_id_hash": "...",
  "modalidad_pago": "paquete_mensual_4_sesiones",
  "monto_paquete_mxn": "3000.00",
  "descuento_pct": 12,
  "estado_pago": "pendiente_renovacion",
  "dias_desde_vencimiento": 1,
  "nivel_cobranza_recomendado": 2,
  "plantilla_renderizada": "...",
  "sugerencia_pausa": false
}
```

## ⚠ Tono empático crítico

Pacientes de salud mental son extra-sensibles. Cobranza agresiva = ruptura terapéutica + queja CONDUSEF/PROFECO + reseñas negativas.
