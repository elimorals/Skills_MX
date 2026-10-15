---
name: credito-kwh-tracking
description: Lleva el registro mes a mes (o bimestre a bimestre) de los kWh que un sistema solar interconectado a CFE inyecta a la red, los que compensa y el saldo a favor acumulado, según el esquema de contraprestación del contrato (medición neta, facturación neta o venta total). En medición neta CFE no paga en efectivo: el excedente queda como crédito en kWh. Usar cuando el usuario diga credito kwh tracking, crédito de kWh, saldo a favor CFE, energía inyectada, excedentes solares, cuántos kWh tengo a favor, medición neta.
allowed-tools: Read, Write
---

# Crédito kWh — seguimiento

## Marco (verificado 2026-10-14)

- Ley del Sector Eléctrico (LSE, DOF 18-03-2025): centrales de **menos de 0.7 MW** son generación distribuida / generadora exenta y no requieren permiso (Arts. 3 fr. XXII, 19 y 25). Venden excedentes a la Suministradora de Servicios Básicos (CFE); los modelos de contrato y contraprestación los emite la **Comisión Nacional de Energía (CNE)**, que sustituyó a la CRE (Art. 27).
- Esquemas de contraprestación: medición neta, facturación neta y venta total. Vienen de las disposiciones de generación distribuida de la extinta CRE; siguen en uso mientras la CNE no emita las nuevas. **Verificar** en el contrato de interconexión cuál firmó el usuario y las reglas de vigencia del saldo.

| Esquema | Qué pasa con el excedente |
|---|---|
| Medición neta | Se compensa contra consumo; el sobrante queda como saldo en kWh, sin pago en efectivo |
| Facturación neta | Lo inyectado se paga a un precio (abono en $), lo consumido se cobra a tarifa |
| Venta total | Toda la generación se vende; el consumo se factura aparte |

Vigencia del saldo en medición neta: las fuentes reportan que los kWh a favor se pueden usar durante 12 meses y después se pierden (confianza media; confirmar en el contrato).

## Flujo

1. Pide esquema del contrato, fecha de interconexión y los recibos desde entonces (ver `lectura-factura-cfe-pdf`).
2. Por periodo registra: kWh consumidos de la red, kWh inyectados, kWh compensados, saldo final.
3. Saldo = saldo anterior + inyectados − compensados. Cuadra contra el saldo impreso en el recibo; si no cuadra, márcalo y sugiere `validacion-factura-cfe`.
4. Alerta cuando haya saldo por vencer (si el contrato fija vigencia).
5. Si sobra crédito de forma constante, el sistema está sobredimensionado para el consumo: dilo.

## Ejemplo (medición neta)

| Periodo | Consumo red | Inyectado | Compensado | Saldo |
|---|---|---|---|---|
| saldo inicial | | | | 0 |
| mar–abr 2026 | 900 | 1,200 | 900 | 300 |
| may–jun 2026 | 1,100 | 1,000 | 1,100 | 200 |
| jul–ago 2026 | 1,000 | 950 | 1,000 | 150 |

En may–jun: 300 + 1,000 = 1,300 disponibles; se compensan 1,100; quedan 200. En jul–ago: 200 + 950 = 1,150; se compensan 1,000; quedan 150.

## Output

```json
{
  "rpu_hash": "...",
  "esquema": "medicion_neta",
  "periodos": [{"periodo": "2026-07/08", "kwh_consumo_red": 1000, "kwh_inyectados": 950, "kwh_compensados": 1000, "kwh_saldo": 150, "cuadra_con_recibo": true}],
  "kwh_saldo_actual": 150,
  "vigencia_saldo": "verificar en contrato",
  "fuente": "recibos CFE capturados por el usuario"
}
```

## Dependencias

- `lectura-factura-cfe-pdf` para extraer los datos.
- `mp_cfe_interconexion_solar.cfe_solar_simular_ahorro` (esquemas `medicion_neta` / `facturacion_neta`) para proyectar.
- No hay consulta pública del saldo en CFE: el dato sale del recibo.
