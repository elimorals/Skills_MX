---
name: cobranza-consultas-especialista
description: Cobranza de consultas para médico especialista, incluyendo casos B2C (paciente paga directo) y B2B (seguros médicos / GMM reembolsa al paciente o paga directo al médico). Cubre tarifa por especialidad y tipo consulta, validación coaseguro y deducible cuando paciente tiene seguro, emisión CFDI uso D01, recordatorios pago. Usar cuando el usuario diga cobrar consulta, factura medico, paciente con seguro, GMM reembolso.
allowed-tools: Read, Write
---

# Cobranza consultas especialista

## Modos de cobranza

### A. Paciente paga directo
- Tarifa lista médico (varía $500-$3,000 MXN según especialidad)
- Métodos: efectivo, tarjeta, transferencia
- CFDI uso D01 (deducible para paciente)
- 100% del importe al médico

### B. Paciente con seguro GMM (reembolso)
- Paciente paga 100% al médico
- Médico emite CFDI uso D01 + nota detallada para que aseguradora reembolse
- Médico se desentiende, paciente cobra del seguro

### C. Aseguradora paga directo (convenios)
- Médico está en panel de aseguradora (GNP, AXA, Banorte, etc.)
- Paciente solo paga coaseguro / deducible (~10-20% típico)
- Aseguradora paga el resto al médico en 30-60 días
- CFDI uso G03 a la aseguradora, no al paciente

## Tarifas referencia (validar local)

| Especialidad | Primera vez | Seguimiento |
|---|---|---|
| Médico general | $700 | $500 |
| Pediatría | $900 | $700 |
| Cardiología | $1,500 | $1,200 |
| Dermatología | $1,200 | $900 |
| Endocrinología | $1,500 | $1,200 |
| Psiquiatría | $1,800 | $1,500 |
| Ginecología | $1,200 | $900 |

## Output

```json
{
  "consulta_id": "...",
  "paciente_rfc_hash": "...",
  "tipo_pago": "paciente_con_seguro_gmm",
  "aseguradora": "GNP",
  "monto_total_consulta_mxn": "1500.00",
  "deducible_paciente_mxn": "200.00",
  "coaseguro_paciente_mxn": "260.00",
  "monto_paciente_a_pagar_mxn": "460.00",
  "monto_aseguradora_a_pagar_mxn": "1040.00",
  "cfdi_uuid": "abc-123",
  "estado_cobranza": "pendiente_aseguradora",
  "vigencia_validada": false
}
```
