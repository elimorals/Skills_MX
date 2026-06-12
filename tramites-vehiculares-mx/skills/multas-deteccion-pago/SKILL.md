---
name: multas-deteccion-pago
description: Detecta multas vehiculares pendientes consultando portales municipales (CDMX, EdoMex, Monterrey y otros disponibles) por placa, calcula el descuento por pronto pago (típico 50% en primeros 30 días), y prepara los datos para pago (línea de captura, monto, deadline). NO ejecuta el pago en sí (ese paso es manual o vía banca digital del usuario). Usar cuando el usuario diga buscar multas, multas pendientes, cuánto debo de multas, multas auto. NO usar para infracciones de Hacienda federal o de PROFEPA.
allowed-tools: Read, Write
---

# Multas vehiculares — detección y preparación de pago

## Trigger

- "¿tengo multas?"
- "buscar multas placa ABC-1234"
- Cron diario `check-multas-vehiculares.sh` detecta y alerta

## Flujo

### 1. Consultar por entidad

Por cada placa registrada con su entidad:
- CDMX → `mp_cdmx_municipal.consultar_multas(placa)`
- EdoMex → `mp_edomex_municipal.consultar_multas(placa)`
- MTY/NL → `mp_monterrey_municipal.consultar_multas(placa)`
- Otros estados → mock (pendiente MCPs específicos)

### 2. Calcular descuentos

Típico en MX: pago dentro de 30 días → descuento 50%.

```python
def calcular_monto_pago(multa):
    if (today - multa.fecha_infraccion).days <= 30:
        return multa.monto * 0.50  # 50% descuento
    return multa.monto
```

### 3. Generar línea de captura

CDMX: vía https://www.finanzas.cdmx.gob.mx
EdoMex: vía https://sfpya.edomexico.gob.mx
NL: vía portales municipales por municipio

Output: URL + folio para que usuario pague en banca digital.

### 4. Persistir en tracker

```json
{
  "placa": "ABC-1234",
  "multa_id": "M-12345",
  "entidad": "edomex",
  "fecha_infraccion": "2026-04-12",
  "tipo": "estacionar_zona_prohibida",
  "monto_original_mxn": "1500.00",
  "monto_con_descuento_mxn": "750.00",
  "deadline_descuento": "2026-05-12",
  "linea_captura": "...",
  "estado": "pendiente"
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Portal banco down | Reintentar; si persiste, alertar |
| Multa duplicada (mismo folio en distintas consultas) | Deduplicate por `multa_id` |
| Multa > 1 año sin pagar | Riesgo embargo placa → 🔴 prioridad alta |
| Foto multa no clara | Pedir al usuario validar antes de pagar |

## ⚠ Compliance

- Hashear placa en logs (`placa_hash`)
- NO almacenar datos de tarjeta del usuario para pago
- El pago se hace fuera del sistema (banca digital del usuario)
