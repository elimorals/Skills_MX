---
name: validacion-factura-cfe
description: Revisa un recibo o factura CFE de una PyME o usuario con paneles solares y detecta errores comunes - lecturas que no cuadran, kWh entregados a la red no compensados, saldo a favor que desapareció, DAP cobrado dos veces, cargo por factor de potencia mal aplicado, cambio de tarifa sin aviso, IVA mal calculado o lectura estimada. Prepara la reclamación ante CFE y, si no se resuelve, la queja ante PROFECO. Usar cuando el usuario diga validacion factura cfe, recibo CFE mal cobrado, error en recibo de luz, cobro indebido CFE, no me compensaron los kWh, reclamar a CFE.
allowed-tools: Read, Write
---

# Validación de factura CFE

## Entrada

JSON de `lectura-factura-cfe-pdf` del periodo actual y, si existe, del anterior (para continuidad de lecturas y saldo).

## Revisiones

| # | Revisión | Regla | Severidad si falla |
|---|---|---|---|
| 1 | Continuidad de lecturas | Lectura anterior de este recibo = lectura actual del recibo previo | alta |
| 2 | kWh del periodo | Lectura actual − anterior = kWh facturados (por canal y periodo horario) | alta |
| 3 | Inyección compensada | En medición neta, kWh entregados se restan o pasan a saldo | alta |
| 4 | Saldo a favor | Saldo anterior + inyectados − compensados = saldo actual (ver `credito-kwh-tracking`) | alta |
| 5 | Lectura estimada | El recibo indica "estimada" o no hay lectura real | media: pedir lectura real |
| 6 | DAP | Un solo cargo de DAP por periodo | media |
| 7 | Factor de potencia | Cargo solo si FP < 90%; bonificación si > 90% (tarifas de media tensión) | media |
| 8 | Tarifa | Igual a la del contrato; si cambió (p. ej. a DAC), revisar promedio de 12 meses | media |
| 9 | IVA | 16% del subtotal de energía y demanda (8% en región fronteriza con estímulo) | baja |
| 10 | Aritmética | Subtotal + IVA + DAP = total (± $1) | baja |

Solo marca error lo que el recibo muestra. Si falta un dato para revisar, la revisión queda `"no_verificable"`, no `"ok"`.

## Ejemplo

Recibo previo: lectura actual de entrega 18,400. Recibo actual: lectura anterior de entrega 18,100 → la continuidad falla por 300 kWh. Saldo anterior 200 + inyectados 950 − compensados 1,000 = 150; el recibo muestra 0 → saldo faltante de 150 kWh.

## Reclamación

1. Reporte a CFE (centro de atención, 071 o portal) con número de servicio, periodo y la tabla de diferencias. Pide folio.
2. Si no hay respuesta o es negativa: queja ante PROFECO (CFE como proveedor del suministro básico). `concilianet_consultar_proveedor` (`mp_concilianet_profeco`) dice si CFE está en Concilianet; el registro de la queja lo hace el usuario.
3. Paga lo no disputado para evitar suspensión mientras se resuelve, salvo que CFE indique otra cosa.

## Output

```json
{
  "periodo": "2026-09",
  "revisiones": [
    {"id": 1, "nombre": "continuidad_lecturas", "resultado": "error", "diferencia_kwh": 300},
    {"id": 4, "nombre": "saldo_a_favor", "resultado": "error", "esperado_kwh": 150, "recibo_kwh": 0},
    {"id": 7, "nombre": "factor_potencia", "resultado": "no_verificable"}
  ],
  "monto_en_disputa_mxn": "calcular con el precio por kWh del recibo",
  "siguiente_paso": "reclamación CFE con folio"
}
```

## Advertencias

- Revisión de consistencia del recibo, no peritaje del medidor. Un medidor dañado lo revisa CFE.
- Las reglas de compensación dependen del contrato de interconexión (ver `credito-kwh-tracking`).
