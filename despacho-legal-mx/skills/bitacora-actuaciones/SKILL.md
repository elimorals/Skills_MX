---
name: bitacora-actuaciones
description: Registra actuaciones procesales y trabajo realizado por el despacho en cada expediente con timestamp, abogado responsable, descripción del acto (presentación de promoción, asistencia a audiencia, redacción de escrito, llamada con autoridad, investigación, gestión, reunión con cliente), tiempo invertido en minutos para cobrar honorarios por hora cuando aplica, archivos anexos (escritos PDF, fotos de comparecencia, audios de audiencia) y siguiente acción con fecha límite cuando hay plazo procesal corriendo. Sirve como evidencia de diligencia ante un reclamo por negligencia (Art. 2615 CCF) y como rendición de cuentas al cliente (Arts. 2569-2570 CCF, mandato). Usar cuando el usuario diga "registrar actuación", "anotar avance asunto", "bitácora despacho", "log de litigio", "minuta abogado", "time sheet abogado", "horas facturables", "ledger asunto legal". NO usar para bitácora bancaria ni para nota clínica.
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
  codigo_procesal: "CNPCF|código estatal|CNPP|Ley de Amparo|LFT|..."
  computo: "días hábiles del tribunal"   # confirmar contra el código aplicable
  alerta_dias_antes: 7
costo_hora: 1500       # $/hora, si el contrato cobra por hora
importe_actuacion: 6000  # 240 / 60 × 1,500 = 6,000 (antes de IVA)
```

## Por qué la bitácora

1. **Defensa por responsabilidad profesional**: el profesionista responde por negligencia, impericia o dolo (Art. 2615 CCF o su equivalente estatal); la bitácora documenta la diligencia.
2. **Rendición de cuentas**: el mandatario debe dar cuentas exactas al mandante (Art. 2569 CCF) y entregarle lo recibido por el poder (Art. 2570). Sirve también para el desglose que pida el cliente.
3. **Continuidad**: si cambia el abogado, otro debe poder tomar el expediente. Si el despacho deja el asunto, debe avisar con oportunidad (Art. 2614 CCF) y seguir el negocio mientras el cliente nombra a otro, si de lo contrario hay perjuicio (Art. 2603 CCF).
4. **Plazos procesales**: alertar antes de vencimientos.

## Plazos: qué código aplica

- **Civil y familiar**: el Código Nacional de Procedimientos Civiles y Familiares (DOF 07-06-2023) entra en vigor en cada estado por declaratoria de su congreso, con fecha límite del 1-abr-2027. Mientras no rija en la entidad, aplica el código procesal estatal. Antes de calcular un plazo, confirma qué código rige en ese juzgado y para asuntos iniciados en qué fecha (verificar la declaratoria del estado).
- **Federal**: desde el 1-sep-2025 la SCJN trabaja solo en Pleno y el Consejo de la Judicatura Federal fue sustituido por el Tribunal de Disciplina Judicial y el Órgano de Administración Judicial (reforma DOF 15-09-2024). Registra el nombre vigente del órgano que conoce del asunto.
- El skill no computa plazos procesales por sí solo: registra la fecha que fije el abogado y genera la alerta.

## Notas

- Los CCF citados son el Código Civil Federal. En asuntos locales aplica el código civil del estado, que suele tener artículos equivalentes con otra numeración.
- Los registros contienen información bajo secreto profesional: guárdalos con acceso restringido (ver `compliance-lfpdppp`).
