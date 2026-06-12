---
name: integracion-medico-referente
description: Gestiona la red de médicos referentes del laboratorio (típicamente 30-200 médicos en lab PyME) con cálculo de comisiones por referencia que el lab paga al médico por cada paciente que envía (5-15% típico, variable por especialidad — más alto para ginecología y endocrinología que mandan más estudios), CFDI de honorarios del lab hacia el médico mensual con régimen 612 PFAE típicamente (10% ISR + 10.67% IVA retenido por el lab PM), tracking del volumen mensual por médico (top 10 que más refieren reciben atención preferencial y descuentos), envío automático de resultados de SUS pacientes vía WhatsApp/email con resumen ejecutivo + PDF completo, dashboard de productividad del médico (cuántos pacientes mandó este mes, monto, comisión generada), y prevención de comisiones por auto-referencia (el médico no puede ser él mismo el paciente — conflicto de interés). Cuidar: las comisiones por referencia están en zona gris en COFEPRIS — solo válidas si son por gestión administrativa, no por inducción a sobre-estudios. Usar cuando el usuario diga "comisiones médicos lab", "pagar al doctor que refirió", "facturar a médico", "red de médicos lab", "doctor referente". NO usar para facturar al paciente final.
allowed-tools: Read, Write, Edit
---

# Integración con médicos referentes

## Estructura del médico referente

```yaml
medico_id: MED-2026-042
nombre: Dr. Hernández García
especialidad: Endocrinología
cedula_profesional: 9876543
cedula_especialidad: 12345
rfc: HEGJ800101XYZ
regimen_fiscal: 612  # PFAE típico
contacto:
  consultorio: ...
  whatsapp: +52...
  email: ...
comision_acordada: 0.10  # 10%
fecha_alta: 2024-03-15
volumen_mensual_promedio: 25  # pacientes/mes
top_estudios_solicitados:
  - perfil_tiroideo
  - hba1c
  - perfil_lipidos
```

## Cálculo de comisión mensual

```
volumen_paciente_mes = 25
ingreso_lab_paciente_promedio = 850  # MXN
ingreso_total_mes = 25 * 850 = 21,250
comision_bruta = 21,250 * 0.10 = 2,125
ISR_retenido (10% del bruto Art. 113 LISR) = 212.50
IVA_trasladado = 2,125 * 0.16 = 340
IVA_retenido_lab (10.67%) = 226.67
comision_neta_medico = 2,125 + 340 - 212.50 - 226.67 = 2,025.83
```

## CFDI a emitir HACIA el médico

⚠ Nota: el médico es quien emite CFDI al lab, no al revés. El skill ayuda al médico a emitir esa factura, o el lab construye una factura pro-forma para que el médico la timbre.

Configuración pro-forma:
- TipoComprobante: I (Ingreso) emitido por el médico
- Emisor: médico
- Receptor: lab
- UsoCFDI: G03
- ClaveProdServ: 80101502 (servicios médicos profesionales)
- ImpuestosRetenidos: 10% ISR + 10.67% IVA (lab retiene)

## Dashboard del médico referente

```
TOP referentes del lab (mes actual):

1. Dr. Hernández (Endocrino)    | 28 pacientes | $2,200 comisión
2. Dr. Ramírez (Cardiólogo)     | 22 pacientes | $1,850 comisión
3. Dra. López (Ginecóloga)      | 19 pacientes | $1,615 comisión
4. Dr. Sánchez (Internista)     | 15 pacientes | $1,275 comisión
5. Dra. García (Pediatra)       | 12 pacientes | $1,020 comisión
...

Total: 156 pacientes | $13,260 comisiones netas
```

## Política de envío automático de resultados

Cuando se libera resultado de un paciente referido:
1. Resumen ejecutivo al médico vía WhatsApp (1 párrafo)
2. PDF completo adjunto
3. Si valor pánico: notificar inmediato por llamada
4. Médico puede solicitar comentario adicional del QFB

## Validación pendiente

⚠ COFEPRIS: la comisión por referencia médica debe ser por gestión administrativa, NO por inducir más estudios. Revisar con asesor legal sanitario.
⚠ Porcentajes y régimen fiscal varían por médico — confirmar individualmente.
