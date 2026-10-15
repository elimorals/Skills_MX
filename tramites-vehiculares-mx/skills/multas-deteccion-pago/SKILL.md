---
name: multas-deteccion-pago
description: Guía la consulta de multas vehiculares pendientes por placa (CDMX, EdoMex, Jalisco, Nuevo León y San Pedro), estima el descuento por pronto pago según la regla de cada entidad y prepara los datos para pagar (portal, folio, monto, fecha límite del descuento). Los portales oficiales tienen CAPTCHA, así que la consulta normalmente se entrega al usuario con URL y pasos. NO ejecuta el pago. Usar cuando el usuario diga buscar multas, multas pendientes, infracciones, fotomultas, cuánto debo de multas, multas del auto, descuento en multas. NO usar para infracciones fiscales federales ni de PROFEPA.
allowed-tools: Read, Write
---

# Multas vehiculares — detección y preparación de pago

## Flujo

### 1. Consultar

`multas_consultar_por_placa(estado, placa)` (`mp_multas_vehiculares_mx`), con `estado` = `cdmx | edomex | jal | nl | nl_sanpedro`. `multas_listar_sistemas` muestra cuáles hay.

Estado real del MCP: **entrega a humano**. Los portales de CDMX, EdoMex, Jalisco y San Pedro tienen CAPTCHA; NL es consulta manual. Si la respuesta trae `requiere_humano: true`:
- Entrega al usuario `url` y `pasos` del handoff, tal cual.
- Pídele que pegue (o capture en foto) el resultado: folio, fecha, motivo y monto.
- No digas "no tienes multas": `consultado: false` significa que no se consultó.

Solo si el operador configuró el solver opt-in y la respuesta trae `multas`, úsalas directo. `multas_calcular_total` suma lo capturado.

Otros estados: no hay MCP. Da el portal de la secretaría de finanzas o tránsito del estado/municipio.

### 2. Descuento por pronto pago (verificar en cada caso)

No hay una regla nacional de "50% en 30 días". Cada entidad fija la suya:

| Entidad | Regla reportada 2026 | Confianza |
|---|---|---|
| EdoMex | 50% si se paga al momento o dentro de 15 días hábiles desde la emisión o notificación (Reglamento de Tránsito vigente desde 25-nov-2025). Monto mínimo/medio/máximo según infracciones acumuladas | media (El Financiero, N+) |
| CDMX | Descuentos en multa principal por Ley de Ingresos/Código Fiscal 2026; las fuentes no coinciden en porcentaje ni plazo; no aplica en carril confinado, ciclovía o con lesiones | baja: confirmar en finanzas.cdmx.gob.mx |
| Otras | Sin dato | confirmar en el portal |

Si no hay regla verificada, muestra el monto completo y marca `descuento: "verificar"`.

### 3. Preparar el pago

- CDMX: línea de captura en `finanzas.cdmx.gob.mx` (Secretaría de Administración y Finanzas).
- EdoMex: portal de pagos de la Secretaría de Finanzas o establecimientos autorizados.
- El usuario paga desde su banca. La skill no guarda datos de tarjeta.

### 4. Registrar

```json
{
  "placa_hash": "...",
  "multa_id": "M-12345",
  "entidad": "edomex",
  "fecha_notificacion": "2026-10-01",
  "motivo": "estacionar en lugar prohibido",
  "monto_original_mxn": "1500.00",
  "descuento_regla": "50% dentro de 15 días hábiles",
  "monto_con_descuento_mxn": "750.00",
  "fecha_limite_descuento": "2026-10-22",
  "fuente_dato": "captura del usuario desde portal oficial",
  "estado": "pendiente"
}
```

Fecha límite del ejemplo: 15 días hábiles desde el jueves 1-oct-2026, sin inhábiles oficiales intermedios = 22-oct-2026. Si hay días inhábiles oficiales en medio, recórrela.

## Casos edge

| Caso | Acción |
|---|---|
| Portal caído o CAPTCHA | Handoff: URL + pasos; reintentar más tarde |
| Mismo folio en dos consultas | Deduplicar por `multa_id` |
| Multa con más de un año | Puede haber recargos y bloquear trámites (refrendo, verificación); prioridad alta |
| Fotomulta no clara | Pedir al usuario revisarla antes de pagar; puede impugnarse en el plazo del reglamento |
| Fotocívica CDMX | Sanción por puntos/trabajo comunitario, no siempre monetaria; revisar en el portal |

## Compliance

- Hashear la placa en logs (`placa_hash`).
- No guardar datos de tarjeta.
- El pago se hace fuera del sistema.
- Montos y descuentos cambian por reglamento local: confirmar antes de pagar.
