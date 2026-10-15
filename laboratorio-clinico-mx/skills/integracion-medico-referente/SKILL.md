---
name: integracion-medico-referente
description: Gestiona la red de médicos referentes del laboratorio - comisiones por referencia (porcentaje pactado por médico), CFDI que el médico emite al laboratorio con retenciones (régimen 612 - ISR 10% + IVA 10.6667%; RESICO - ISR 1.25% + IVA 10.6667%), volumen mensual por médico, envío de resultados de sus pacientes por WhatsApp/email y prevención de auto-referencia. Advierte el riesgo ético-legal de pagar por referir pacientes. Usar cuando el usuario diga comisiones médicos lab, pagar al doctor que refirió, factura del médico al laboratorio, red de médicos lab, doctor referente. NO usar para facturar al paciente final.
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
IVA_trasladado = 2,125 * 0.16 = 340      # la comisión NO es servicio médico → no aplica la exención del Art. 15 fr. XIV LIVA

# Médico régimen 612 (PFAE)
ISR_retenido (10%, Art. 106 LISR) = 212.50
IVA_retenido_lab (2/3 del IVA = 10.6667%) = 226.67
deposito_al_medico = 2,125 + 340 - 212.50 - 226.67 = 2,025.83

# Médico RESICO PF (626)
ISR_retenido (1.25%, Art. 113-J LISR) = 26.56
IVA_retenido_lab (2/3 del IVA) = 226.67
deposito_al_medico = 2,125 + 340 - 26.56 - 226.67 = 2,211.77
```

## CFDI que emite el médico al laboratorio

⚠ El médico emite el CFDI al lab, no al revés. El lab puede armar un borrador para que el médico lo timbre.

- TipoComprobante: I, emisor = médico, receptor = lab (persona moral)
- UsoCFDI: G03
- ClaveProdServ: de comisiones/intermediación, **no** de servicios médicos (8512xxxx); confirmar la clave exacta en c_ClaveProdServ con el contador
- Traslado IVA 16%; retenciones según la tabla de arriba
- Total del CFDI = subtotal + IVA − retenciones (= depósito al médico)

El laboratorio persona moral también cobra **IVA 16%** a sus pacientes: la exención de estudios clínicos (Art. 15 fr. XV LIVA) solo cubre organismos públicos descentralizados.

## Dashboard del médico referente

```
TOP referentes del lab (mes actual):

1. Dr. Hernández (Endocrino)    | 28 pacientes | $2,380 comisión
2. Dr. Ramírez (Cardiólogo)     | 22 pacientes | $1,870 comisión
3. Dra. López (Ginecóloga)      | 19 pacientes | $1,615 comisión
4. Dr. Sánchez (Internista)     | 15 pacientes | $1,275 comisión
5. Dra. García (Pediatra)       | 12 pacientes | $1,020 comisión
...

Total: 156 pacientes | $13,260 comisiones brutas (antes de IVA y retenciones)
```

Supuesto del ejemplo: ticket promedio $850 sin IVA y comisión 10% para todos (pacientes × 850 × 0.10).

## Política de envío automático de resultados

Cuando se libera resultado de un paciente referido:
1. Resumen ejecutivo al médico (1 párrafo) por canal autenticado; resultados = datos sensibles: el paciente debe haber consentido el envío a su médico (Art. 8 LFPDPPP 2025)
2. PDF completo firmado por el responsable sanitario o personal autorizado (NOM-007 5.1.8)
3. Si valor de pánico: llamada inmediata, no solo mensaje
4. Médico puede solicitar comentario adicional del químico responsable

## Validación pendiente

⚠ Pagar al médico por cada paciente referido ("dicotomía") es cuestionado por la ética médica y puede generar conflicto de interés. No se localizó (2026-10-15) una prohibición expresa en la LGS; documentar la comisión como pago por servicios reales (gestión, toma de muestra, logística), nunca por volumen de estudios, y revisarlo con asesor legal sanitario.
⚠ Porcentajes y régimen fiscal varían por médico — confirmar individualmente.
