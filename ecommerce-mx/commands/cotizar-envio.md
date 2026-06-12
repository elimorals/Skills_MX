---
description: Cotiza envío en las 4 paqueterías principales (Estafeta, DHL MX, FedEx MX, 99 Minutos) según peso, dimensiones, origen y destino. Recomienda la mejor opción según urgencia y costo.
argument-hint: "[origen CP, destino CP, peso kg, dimensiones cm]"
allowed-tools: Read, Write, Edit
---

# /ecommerce:cotizar-envio

Cotiza envío en paqueterías MX: $ARGUMENTS

## Lo que hace

1. Calcula peso volumétrico vs peso real (lo mayor cuenta).
2. Identifica zona (local, regional, nacional) según CPs.
3. Cotiza en paralelo en las 4 paqueterías principales.
4. Agrega seguro si valor declarado > $1,500 MXN.
5. Compara y recomienda según balance precio/tiempo.

## Cuándo usar

- Antes de fijar el costo de envío al cliente en checkout
- Decidir qué paquetería contratar para un pedido específico
- Comparar tarifas para optimización mensual

## Output esperado

```
✓ Cotización envío — CDMX 06700 → GDL 44100

Paquete: 3 kg real, 30×20×15 cm (vol: 1.8kg)
Peso facturable: 3 kg
Valor declarado: $2,500 MXN (seguro recomendado)

Opciones:
┌──────────────┬─────────────┬────────┬────────┬──────────┐
│ Paquetería   │ Servicio    │ Tiempo │ Precio │ Recomend │
├──────────────┼─────────────┼────────┼────────┼──────────┤
│ Estafeta     │ Día sig.    │ 1-2d   │ $215   │ ★★★      │
│ DHL MX       │ Same-day    │ 1d     │ $323   │ ★★       │
│ 99 Minutos   │ Next-day    │ 1d     │ $199*  │ ★★ (*sin seguro)│
│ paqueteX     │ Variable    │ 1-3d   │ $185   │ ★★       │
└──────────────┴─────────────┴────────┴────────┴──────────┘

★ Recomendación: Estafeta Día Siguiente
  Razón: mejor balance precio/tiempo con seguro incluido para esta ruta
```
