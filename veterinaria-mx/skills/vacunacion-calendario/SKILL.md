---
name: vacunacion-calendario
description: Calendario de vacunación para perros, gatos y exóticos con esquemas estándar mexicanos (cachorro 6-16 semanas, adulto refuerzo anual, geriátricos especial), seguimiento por mascota con próxima dosis calculada, recordatorios WhatsApp 30d/7d/24h antes, registro de marca y lote para trazabilidad, validación de vencimiento de protección, alertas si el dueño se atrasa. Usar cuando el usuario diga vacunar mascota, calendario vacunas, refuerzo, cachorro plan, próxima vacuna, vacunación obligatoria. NO usar para expediente completo (expediente-clinico-mascota) ni urgencias.
allowed-tools: Read, Write, Edit
---

# Calendario de vacunación veterinaria

## Esquema cachorro perro (6-16 semanas)

| Edad | Vacuna | Notas |
|---|---|---|
| 6-8 semanas | Multivalente 1ra dosis (DAPP) | No salir todavía |
| 8-10 semanas | Multivalente 2da dosis + Leptospirosis | Aún en aislamiento |
| 12-14 semanas | Multivalente 3ra dosis + Antirrábica + Lepto 2da | Casi listo para salir |
| 16 semanas | Refuerzos finales | Salida segura calle |
| 6-12 meses | Bordetella (opcional) + Influenza canina | Si va a guardería |

**Refuerzo anual**: cada 12 meses todo el esquema.

## Esquema cachorro gato (8-16 semanas)

| Edad | Vacuna | Notas |
|---|---|---|
| 8-10 semanas | FVRCP 1ra dosis | Multivalente felino |
| 12-14 semanas | FVRCP 2da + Leucemia (FeLV) 1ra | |
| 16 semanas | FeLV 2da + Antirrábica | |

**Refuerzo anual** o bianual según riesgo (gato indoor vs outdoor).

## Esquema perro/gato adulto

- 1 vez al año: multivalente + antirrábica
- 1 vez cada 3 años: antirrábica (algunas marcas tienen efectividad triple)
- Bordetella: cada 6-12 meses si va a guardería/exposiciones
- Leptospirosis: anual si zona endémica (CDMX, Veracruz, regiones tropicales)

## Calendario sugerido por especie/edad

```json
{
  "perro_cachorro_calendario": [
    {"semana_vida": 7, "vacunas": ["DAPP-1"]},
    {"semana_vida": 10, "vacunas": ["DAPP-2", "Leptospirosis-1"]},
    {"semana_vida": 13, "vacunas": ["DAPP-3", "Antirrábica", "Leptospirosis-2"]},
    {"semana_vida": 16, "vacunas": ["DAPP-4", "Bordetella opcional"]}
  ],
  "perro_adulto_anual": [
    {"frecuencia": "anual", "vacunas": ["DAPP refuerzo", "Antirrábica"]},
    {"frecuencia": "semestral_si_riesgo", "vacunas": ["Bordetella"]}
  ]
}
```

## Recordatorios automáticos

### Lógica
```
para cada vacuna_aplicada:
  fecha_proxima_dosis = fecha_aplicacion + protección_meses
  enviar_recordatorio:
    - 30 días antes
    - 7 días antes
    - 1 día antes
  si pasó la fecha y no fue:
    - 1 día después: recordatorio amable
    - 7 días después: alerta urgencia (riesgo enfermedad)
    - 30 días después: marcar protección como "vencida"
```

### Templates WhatsApp

**30 días antes**:
> "Hola Ana 🐶 Luna tiene su próxima vacuna multivalente en 30 días (15-jul-2026). ¿Te agendamos? Llámanos o responde a este mensaje."

**7 días antes**:
> "Hola Ana 🐶 Recordatorio: Luna necesita su vacuna multivalente el martes 15-jul. Slot disponible 11am o 5pm — ¿cuál te conviene?"

**1 día antes**:
> "Mañana Luna tiene su vacuna 🐶 Te esperamos a las 11am. Si no puedes, avísanos para no perder el lote."

**1 día después si no fue**:
> "Ana, Luna no vino ayer a su vacuna. ¿Todo bien? Podemos reagendar esta semana — su protección expira pronto y queremos mantenerla protegida 🛡️"

## Registro post-aplicación

Cada vacuna debe registrar:
- Marca y lote (trazabilidad obligatoria por SAGARPA)
- Vencimiento del frasco (si vencido = revacunar)
- Vía de aplicación
- MVZ responsable + cédula profesional
- Reacción adversa si la hubo

⚠ Si reacción anafiláctica: **registrar permanentemente** en expediente. Próxima vacuna con premedicación + obs 4h.

## Trazabilidad SAGARPA

México exige trazabilidad de vacunas para campañas oficiales (rabia, brucelosis):
- Marca, lote, fecha aplicación
- Datos del aplicante (cédula MVZ)
- Datos del paciente y tutor
- Conservar 5 años (NOM-052)

## Output estructurado

```json
{
  "calendario_vacunacion": {
    "mascota": "Luna",
    "especie": "perro",
    "edad": "5 años 7 meses",
    "vacunas_vigentes": [
      {
        "vacuna": "Multivalente DAPP-L",
        "vence": "2026-06-15",
        "dias_para_vencer": 4,
        "estado": "VIGENTE_POR_RENOVAR"
      },
      {
        "vacuna": "Antirrábica",
        "vence": "2028-06-15",
        "dias_para_vencer": 730,
        "estado": "VIGENTE"
      }
    ],
    "vacunas_vencidas": [],
    "proximas_aplicaciones": [
      {
        "vacuna": "Multivalente refuerzo anual",
        "fecha_sugerida": "2026-06-15",
        "recordatorios_programados": ["2026-05-16", "2026-06-08", "2026-06-14"]
      }
    ],
    "alertas": [
      "Vacuna multivalente vence en 4 días — agendar antes"
    ]
  }
}
```

## Validación pendiente

- Esquemas vigentes CDMX vs estados (puede variar)
- Lista de marcas/lotes con vigencia 2026
- Reglas SAGARPA actualizadas trazabilidad
- Protocolo en caso de cachorro callejero adoptado (sin historial)
