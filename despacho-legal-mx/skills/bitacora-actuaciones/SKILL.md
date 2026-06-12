---
name: bitacora-actuaciones
description: Registra actuaciones procesales y trabajo realizado por el despacho en cada expediente con timestamp, abogado responsable, descripción del acto (presentación de promoción, asistencia a audiencia, redacción de escrito, llamada con autoridad, investigación, gestión, reunión con cliente), tiempo invertido en minutos para cálculo de honorarios por hora cuando aplica, archivos anexos (escritos PDF, fotos de comparecencia, audios de audiencia), y siguiente acción agendada con fecha límite legal cuando hay plazo procesal corriendo. Crítico para defensa por probable mala práctica profesional (debe demostrar diligencia debida) y para facturación detallada cuando cliente solicita desglose. Cumple con el requisito de Art. 2615 CCFm sobre rendición de cuentas. Usar cuando el usuario diga "registrar actuación", "anotar avance asunto", "bitácora despacho", "log de litigio", "minuta abogado", "ledger asunto legal". NO usar para bitácora bancaria ni para nota clínica.
allowed-tools: Read, Write, Edit
---

# Bitácora de actuaciones procesales

## Campos por entry

```yaml
fecha: 2026-06-12T10:30:00-06:00
expediente_id: EX-2026-042
abogado: Lic. Juan Pérez
tipo_actuacion: "presentación_promoción|audiencia|escrito|llamada|investigación|reunión_cliente|otro"
descripcion: "Presentación de contestación de demanda con 12 anexos"
tiempo_minutos: 240
archivos:
  - "expedientes/EX-2026-042/promociones/contestación-2026-06-12.pdf"
plazo_proximo:
  fecha_limite: 2026-06-25
  descripcion: "Audiencia de pruebas y alegatos"
  alerta_dias_antes: 7
costo_unitario: 1500   # $/hora si aplica
total_actuacion: 6000  # tiempo_minutos/60 * costo_unitario
```

## Por qué la bitácora

1. **Defensa por mala práctica**: requiere demostrar diligencia debida documentada
2. **Facturación detallada**: cliente puede solicitar desglose (Art. 2615 CCFm)
3. **Continuidad**: si cambia abogado, expediente debe ser tomable por otro
4. **Plazos procesales**: alertar antes de vencimientos
