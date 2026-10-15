---
name: actualizacion-renta-anual
description: Calcula y comunica la actualización anual de la renta de una propiedad residencial. Soporta dos mecanismos: (a) INPC anual variación del INEGI últimos 12 meses (default), (b) porcentaje fijo establecido en contrato. Verifica topes legales: en CDMX el incremento anual de casa habitación no puede exceder la inflación del año anterior (Art. 2448-D Código Civil CDMX, reforma Gaceta 28-08-2024, validada por la SCJN en feb-2026); en otros estados revisar el código civil local. Genera plantilla de notificación al inquilino con 30 días de anticipación. Usar cuando el usuario diga actualizar renta, incrementar renta, aniversario contrato, ajuste anual renta. NO usar para renovación de contrato completo (eso es contrato-arrendamiento-residencial).
allowed-tools: Read, Write
---

# Actualización anual de renta — INPC o porcentaje fijo

## Cuándo aplica

- Aniversario del contrato (fecha de firma + 12 meses)
- Cláusula del contrato establece actualización anual
- Aviso debe darse al inquilino 30 días antes de la aplicación

## Mecanismos

### A. INPC INEGI (recomendado)

**Fuente**: Índice Nacional de Precios al Consumidor del INEGI, vía tool `banxico_get_inpc` del MCP `mp_banxico` (API SIE real; requiere `BANXICO_TOKEN` gratuito; sin token devuelve mock).

**Cálculo**:
```
INPC_actual / INPC_hace_12_meses = factor_actualizacion
renta_nueva = renta_anterior * factor_actualizacion
```

**Ejemplo**:
- Renta actual: $12,000
- INPC junio 2025: 130.500
- INPC junio 2026: 135.200
- Factor: 135.200 / 130.500 = 1.036015
- Renta nueva: $12,000 × 1.036015 = **$12,432.18**

Incremento: 3.60%. (Índices ilustrativos: consulta los publicados.)

### B. Porcentaje fijo

Si el contrato establece % fijo (ej. 5% anual):
```
renta_nueva = renta_anterior * (1 + porcentaje_fijo)
```

⚠ En CDMX un % fijo pactado que supere la inflación del año anterior no es exigible en vivienda (Art. 2448-D CCDF): aplica el menor. CONDUSEF y PROFECO no conocen de rentas entre particulares; la controversia va a juzgado civil.

## Flujo

### Paso 1 — Identificar propiedades a actualizar

Buscar propiedades con `fecha_proxima_actualizacion <= 30 días`.

### Paso 2 — Consultar INPC

Si mecanismo == INPC:
- Invocar `banxico_get_inpc` para fechas:
  - Actual (último mes con dato publicado)
  - 12 meses atrás

Si el tool responde en modo mock (sin token): NO uses el dato para notificar; pide al usuario el INPC publicado por INEGI.

### Paso 3 — Calcular nuevo monto

Aplicar fórmula del mecanismo correspondiente.

### Paso 4 — Validaciones

- CDMX, casa habitación: si incremento > inflación anual del año anterior (INPC dic/dic) → 🔴 recortar al tope
- Otros estados: si incremento > 10% nominal → 🟡 revisar código civil local y confirmar con el inquilino
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
Renta a partir del [fecha aplicación]: $12,432.18

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
  "renta_nueva": "12432.18",
  "incremento_porcentaje": 3.6,
  "mecanismo": "INPC",
  "fecha_aplicacion": "2026-09-01",
  "fecha_notificacion": "2026-08-01",
  "inquilino_id_hash": "...",
  "vigencia_validada": false
}
```

### Paso 7 — Actualizar CFDIs futuros

A partir de `fecha_aplicacion`, los CFDIs mensuales se emiten con `monto_renta = 12432.18`.

## Casos edge

| Caso | Acción |
|---|---|
| Inquilino se opone (verbal o escrita) | Recordarle cláusula del contrato + sugerir mediación |
| INPC no publicado aún para mes objetivo | Usar último publicado + ajustar retroactivo (raro) |
| Contrato dice "5% fijo" pero la inflación fue 3.6% | Fuera de CDMX: aplica lo pactado. En CDMX vivienda: tope = inflación del año anterior |
| Inquilino paga renta menor "por costumbre" | Conversación necesaria — riesgo de tácita reconducción |
| Propiedad rentada hace < 12 meses | NO actualizar todavía |

## Dependencias

- `mp_banxico` → `banxico_get_inpc` (real con token; mock sin token)
- Tracker de propiedades

## ⚠ Compliance

- Notificación **escrita** con 30 días de anticipación (mejora posibilidad legal)
- Si la renta no se actualiza en un año, el derecho a ese incremento puede discutirse después: actualiza a tiempo
- Valida con abogado local; `vigencia_validada: false`
- Conservar comprobante de notificación (captura WhatsApp / correo)
