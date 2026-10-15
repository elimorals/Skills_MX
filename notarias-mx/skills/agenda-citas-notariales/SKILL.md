---
name: agenda-citas-notariales
description: Agenda de citas notariales con duración real por tipo de acto (compraventa 2-3h, testamento 1h, poder 30min, sociedad 3-5h, sucesión multiple sesiones). Pre-requisitos por tipo (documentos a llevar). Recordatorios al cliente 48h y 24h antes. Usar cuando el usuario diga cita notarial, agendar escritura, programar firma.
allowed-tools: Read, Write
---

# Agenda citas notariales

## Tipos + duración estimada

| Tipo escritura | Duración | Pre-requisitos cliente |
|---|---|---|
| Compraventa inmueble | 2-3h | ID, CURP y constancia de situación fiscal de las partes, comprobante de domicilio (para exención casa habitación), certificado de libertad de gravámenes, predial y agua al corriente, avalúo, escritura anterior |
| Testamento público abierto | 1h | ID; testigos solo si el testador lo pide o no puede o no sabe firmar (CCDF Arts. 1513-1514; verificar código local) |
| Poder general | 30-45min | ID poderdante + apoderado |
| Constitución S.A. | 3-5h | Autorización de denominación (Secretaría de Economía), ID y RFC de socios, beneficiario controlador |
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
