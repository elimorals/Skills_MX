---
name: actualizacion-renta-anual
description: Calcula y comunica la actualización anual de la renta de una propiedad residencial. Soporta dos mecanismos: (a) INPC anual variación del INEGI últimos 12 meses (default), (b) porcentaje fijo establecido en contrato. Verifica que el incremento sea menor a topes legales (usualmente no hay tope formal en CDMX, pero > 10% nominal puede generar reclamos). Genera plantilla de notificación al inquilino con 30 días de anticipación. Usar cuando el usuario diga actualizar renta, incrementar renta, aniversario contrato, ajuste anual renta. NO usar para renovación de contrato completo (eso es contrato-arrendamiento-residencial).
allowed-tools: Read, Write
---

# Actualización anual de renta — INPC o porcentaje fijo

## Cuándo aplica

- Aniversario del contrato (fecha de firma + 12 meses)
- Cláusula del contrato establece actualización anual
- Aviso debe darse al inquilino 30 días antes de la aplicación

## Mecanismos

### A. INPC INEGI (recomendado)

**Fuente**: Índice Nacional de Precios al Consumidor del INEGI (`mp_banxico`).

**Cálculo**:
```
INPC_actual / INPC_hace_12_meses = factor_actualizacion
renta_nueva = renta_anterior * factor_actualizacion
```

**Ejemplo**:
- Renta actual: $12,000
- INPC junio 2025: 130.500
- INPC junio 2026: 135.200
- Factor: 135.200 / 130.500 = 1.0360
- Renta nueva: $12,000 * 1.0360 = **$12,432.00**

Incremento: ~3.6% (típico inflación México 2025).

### B. Porcentaje fijo

Si el contrato establece % fijo (ej. 5% anual):
```
renta_nueva = renta_anterior * (1 + porcentaje_fijo)
```

⚠ % fijos > 10% se consideran excesivos. Pueden ser reclamados ante CONDUSEF o reducirse judicialmente.

## Flujo

### Paso 1 — Identificar propiedades a actualizar

Buscar propiedades con `fecha_proxima_actualizacion <= 30 días`.

### Paso 2 — Consultar INPC

Si mecanismo == INPC:
- Invocar `mp_banxico.consultar_inpc` para fechas:
  - Actual (último mes con dato publicado)
  - 12 meses atrás

Si modo mock: simular con inflación 3.5% anual.

### Paso 3 — Calcular nuevo monto

Aplicar fórmula del mecanismo correspondiente.

### Paso 4 — Validaciones

- Si incremento > 15% nominal: 🔴 alerta (riesgo legal alto)
- Si incremento > 10% nominal: 🟡 confirmar con inquilino antes
- Si incremento < 0% (deflación rara): mantener renta actual o no aplicar

### Paso 5 — Generar notificación

Plantilla WhatsApp + email para enviar al inquilino:

```
Hola [Nombre],

Te escribo respecto al contrato de arrendamiento de [propiedad].

Conforme a la cláusula 4 del contrato firmado el [fecha contrato], la renta se
actualiza anualmente con el INPC del INEGI.

Renta actual: $12,000.00
INPC variación 12 meses: 3.6%
Renta a partir del [fecha aplicación]: $12,432.00

Esta actualización entra en vigor a partir del próximo pago del [fecha].

Cualquier duda o comentario, aquí estoy.

Saludos,
[Tu nombre]
```

### Paso 6 — Actualizar tracker

```json
{
  "propiedad_id": "RN-1A",
  "renta_anterior": "12000.00",
  "renta_nueva": "12432.00",
  "incremento_porcentaje": 3.6,
  "mecanismo": "INPC",
  "fecha_aplicacion": "2026-09-01",
  "fecha_notificacion": "2026-08-01",
  "inquilino_id_hash": "...",
  "vigencia_validada": false
}
```

### Paso 7 — Actualizar CFDIs futuros

A partir de `fecha_aplicacion`, los CFDIs mensuales se emiten con `monto_renta = 12432.00`.

## Casos edge

| Caso | Acción |
|---|---|
| Inquilino se opone (verbal o escrita) | Recordarle cláusula del contrato + sugerir mediación |
| INPC no publicado aún para mes objetivo | Usar último publicado + ajustar retroactivo (raro) |
| Contrato dice "5% fijo" pero INPC fue 3.6% | Aplicar 5% — contrato manda — pero advertir al usuario |
| Inquilino paga renta menor "por costumbre" | Conversación necesaria — riesgo de tácita reconducción |
| Propiedad rentada hace < 12 meses | NO actualizar todavía |

## Dependencias

- `mp_banxico.consultar_inpc` (mock o real)
- Tracker de propiedades

## ⚠ Compliance

- Notificación **escrita** con 30 días de anticipación (mejora posibilidad legal)
- Si renta no se actualiza por 2+ años seguidos: puede argumentarse renuncia tácita
- Conservar comprobante de notificación (captura WhatsApp / correo)
