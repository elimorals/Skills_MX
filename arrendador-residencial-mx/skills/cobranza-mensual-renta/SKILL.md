---
name: cobranza-mensual-renta
description: Cobranza escalada de renta mensual para arrendador residencial con tono adaptado a la relación continua dueño-inquilino. A diferencia de cobranza B2B (más directa), aquí el objetivo es cobrar SIN quemar la relación porque el inquilino sigue ocupando el inmueble. Implementa 5 niveles de escalamiento (D-3 recordatorio cordial, D+3 amable, D+7 firme, D+15 formal, D+30 protocolo desalojo) cada uno con plantilla WhatsApp y email específica. Considera historial del inquilino (puntual histórico vs reincidente). Usar cuando el usuario diga cobranza renta, cobrar inquilino, recordar pago, inquilino no paga, ya me debe X días. NO usar para cobranza B2B (eso es freelancers-mx/cobranza-seguimiento).
allowed-tools: Read, Write
---

# Cobranza renta mensual — 5 niveles

## Filosofía

El inquilino **sigue viviendo** en tu propiedad. Cobranza agresiva = inquilino se va o se queja con CONDUSEF / inmobiliaria pública. Mantener la relación es valioso a largo plazo si el inquilino es bueno (rotación = vacancia + costos de screening).

## 5 niveles de escalamiento

### Nivel 1 — D-3 (recordatorio cordial pre-vencimiento)

**Cuándo**: 3 días antes del día de pago.

**Canal**: WhatsApp + email.

**Tono**: amable, recordatorio sin presión.

**Plantilla WA**:
```
Hola [Nombre], buenos días.
Solo un recordatorio que el [día N] vence el pago de la renta de [propiedad].
CLABE: XXXX XXXX XXXX XXXX 02 (BBVA).
Cualquier duda, aquí estoy.
Saludos!
```

### Nivel 2 — D+3 (recordatorio post-vencimiento, amable)

**Cuándo**: 3 días después del día de pago si no se recibió.

**Tono**: cordial, asume olvido.

**Plantilla WA**:
```
Hola [Nombre], paso a recordarte que el pago de la renta de [propiedad] correspondiente a [mes] aún no aparece en mi cuenta.
Si ya lo hiciste, ¿podrías compartirme el comprobante por aquí?
CLABE: XXXX XXXX XXXX XXXX 02.
Gracias!
```

### Nivel 3 — D+7 (firme)

**Cuándo**: 7 días después.

**Tono**: firme pero respetuoso. Mencionar mora.

**Plantilla WA**:
```
Hola [Nombre], aún no he visto el pago de la renta de [propiedad] del mes de [mes].
Te recuerdo que el contrato contempla recargo del 5% mensual por mora.
¿Pasa algo? Si necesitas, podemos platicar para ver opciones.
Por favor confírmame cuándo podrás hacer el pago.
```

### Nivel 4 — D+15 (formal — primer aviso documentado)

**Cuándo**: 15 días después.

**Canal**: WhatsApp + email + posiblemente llamada.

**Tono**: formal. Mencionar contrato y consecuencias.

**Plantilla email**:
```
Estimado/a [Nombre]:

Por este medio le notifico que la renta correspondiente al mes de [mes] del inmueble ubicado en [dirección] no ha sido pagada al día de hoy [fecha].

Conforme a la cláusula 9 del contrato firmado el [fecha contrato], la falta de pago de dos mensualidades consecutivas constituye causal de rescisión del contrato (Art. 2489 fr. I CCDF).

Le solicito regularizar el pago a más tardar el [fecha límite +5 días], incluyendo el recargo del 5% por mora.

Quedo atento a su respuesta.

Atentamente,
[Nombre del arrendador]
```

### Nivel 5 — D+30 (protocolo desalojo)

**Cuándo**: 30 días después + sin respuesta o sin pago.

**Acción**:
1. Burofax o notificación notarial (deja constancia para juicio)
2. Iniciar consulta con abogado especializado en arrendamiento
3. Documentar TODO (capturas, mensajes, llamadas)
4. NO ejecutar desalojo por cuenta propia (es ilegal y delito) — requiere orden judicial

**Plantilla notificación notarial** (sugerir buscar notario):
```
Sirva la presente para hacer del conocimiento del C. [Nombre], en su carácter de
arrendatario del inmueble ubicado en [dirección], que al día de hoy [fecha], y
habiendo transcurrido 30 días naturales desde el vencimiento del pago correspondiente
al mes de [mes], y no obstante los requerimientos previos del [fecha nivel 4],
NO HA SIDO REALIZADO el pago de la renta convenida.

Por lo anterior, en virtud de la causal contemplada en el Art. 2489 fr. I del CCDF,
se inicia el procedimiento de rescisión del contrato de arrendamiento celebrado el
[fecha contrato].

Se otorga un último plazo de 10 días hábiles para regularizar la situación.
De no atender, se procederá a entablar la acción judicial correspondiente.
```

## Algoritmo de selección de nivel

```python
def determinar_nivel(dias_mora: int, historial_puntualidad: str) -> int:
    """
    historial_puntualidad: "puntual_siempre" | "mixto" | "reincidente"
    """
    if dias_mora <= -3:
        return 0  # no action
    if dias_mora == -3:
        return 1  # recordatorio cordial
    if 0 < dias_mora <= 6:
        return 2  # amable
    if 7 <= dias_mora <= 14:
        return 3  # firme
    if 15 <= dias_mora <= 29:
        return 4  # formal
    if dias_mora >= 30:
        return 5  # protocolo desalojo

    # ajuste si reincidente: subir un nivel desde D+0
    if historial_puntualidad == "reincidente" and dias_mora > 0:
        return min(5, base_nivel + 1)
```

## Output

```json
{
  "operation": "cobranza_mensual_renta",
  "propiedad_id": "RN-1A",
  "inquilino_id_hash": "...",
  "mes_periodo": "2026-06",
  "fecha_vencimiento": "2026-06-05",
  "dias_mora": 15,
  "historial_puntualidad": "mixto",
  "nivel_recomendado": 4,
  "plantilla_canal": "email",
  "plantilla_renderizada": "Estimado/a Juan: ...",
  "monto_total_adeudado_mxn": "12000.00",
  "monto_con_recargo_mxn": "12600.00",
  "siguiente_escalamiento_si_no_paga": "2026-06-30 → nivel 5"
}
```

## Casos edge

| Caso | Tono |
|---|---|
| Inquilino con familia vulnerable (niños / discapacidad) | Extra cuidadoso. Más empatía. Buscar plan de pagos antes de desalojo. |
| Inquilino perdió empleo | Plan de pago + grace period (mes vacío) + revisión a 30 días |
| Inquilino dejó de contestar mensajes | Subir nivel + considerar visita en persona |
| Inquilino paga parcial | Aceptar como abono + nivel actual de cobranza por restante |
| Múltiples meses de mora acumulados | Saltar a nivel 4-5, no quedarse en nivel 2 |

## Dependencias

- `mp_meta_whatsapp` (envío WA)
- `mp_facturama_extendido` (verificar si CFDI ya emitido)
- Tracker de pagos
- Tracker de historial inquilino

## ⚠ Compliance + ética

- NUNCA amenazas falsas (decir "te denuncio penalmente" sin base)
- NO compartir deuda con vecinos / familiares (LFPDPPP)
- Burofax o notarial requiere costos — pasar al usuario después de aprobación
- En CDMX, desalojo judicial puede tardar 6-12 meses — preparar al arrendador
