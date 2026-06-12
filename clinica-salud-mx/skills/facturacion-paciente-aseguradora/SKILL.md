---
name: facturacion-paciente-aseguradora
description: Facturación dual de la clínica: al paciente por coaseguro/deducible (CFDI uso D01) y a la aseguradora por convenio directo (CFDI uso G03). Maneja conciliación pagos aseguradora con 30-90 días de plazo, descuento por convenio, y consolidado mensual al admin de la clínica. Usar cuando el usuario diga facturar paciente, factura aseguradora, GMM clínica.
allowed-tools: Read, Write
---

# Facturación paciente + aseguradora

## Casos

### A. Sin seguro
- 100% al paciente
- CFDI D01

### B. Con seguro reembolso
- Paciente paga 100%
- Solicita reembolso a su aseguradora con CFDI D01

### C. Convenio directo aseguradora-clínica
- Paciente paga: deducible + coaseguro (10-20%)
- CFDI D01 a paciente por su parte
- Aseguradora paga el resto en 30-90d
- CFDI G03 a aseguradora con notas
- Descuento por convenio: aseguradora paga 20-30% menos que tarifa lista

## Output

```json
{
  "paciente_rfc_hash": "...",
  "aseguradora": "GNP",
  "monto_lista_mxn": "1500.00",
  "descuento_convenio_pct": 0.20,
  "monto_neto_aseguradora_mxn": "1200.00",
  "deducible_paciente_mxn": "200.00",
  "coaseguro_paciente_mxn": "200.00",
  "total_recaudado_mxn": "1600.00",
  "perdida_descuento_mxn": "300.00",
  "cfdi_paciente_uuid": "...",
  "cfdi_aseguradora_uuid": "...",
  "estado_cobro_aseguradora": "pendiente_45d"
}
```
