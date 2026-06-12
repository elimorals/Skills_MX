---
name: agenda-citas-notariales
description: Agenda de citas notariales con duración real por tipo de acto (compraventa 2-3h, testamento 1h, poder 30min, sociedad 3-5h, sucesión multiple sesiones). Pre-requisitos por tipo (documentos a llevar). Recordatorios al cliente 48h y 24h antes. Usar cuando el usuario diga cita notarial, agendar escritura, programar firma.
allowed-tools: Read, Write
---

# Agenda citas notariales

## Tipos + duración estimada

| Tipo escritura | Duración | Pre-requisitos cliente |
|---|---|---|
| Compraventa inmueble | 2-3h | ID, comprobante domicilio, certificado libertad gravamen, predial, escrituras anteriores |
| Testamento abierto | 1h | ID, 2 testigos |
| Poder general | 30-45min | ID poderdante + apoderado |
| Constitución S.A. | 3-5h | Aporte capital, denominación reservada SE, ID socios |
| Sucesión testamentaria | Múltiple | Testamento, acta defunción, ID herederos |
| Donación | 1-2h | ID donante + donatario, escrituras del bien |
| Hipoteca | 2-3h | Carta de no adeudo banco anterior, escrituras |

## Output

```json
{
  "cita_id": "NOT-001",
  "fecha_hora": "2026-06-15T10:00:00",
  "tipo_acto": "compraventa",
  "duracion_estimada_min": 150,
  "cliente_nombre": "...",
  "pre_requisitos_pendientes": ["certificado_libertad_gravamen"],
  "estado": "confirmada",
  "honorarios_estimados_mxn": "45000.00",
  "recordatorios_enviados": ["48h", "24h"]
}
```
