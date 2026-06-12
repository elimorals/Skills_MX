---
name: tarifario-servicios-vet
description: Tarifario completo de servicios veterinarios mexicanos — consulta general, consulta especialidad, vacunación, esterilización, cirugía mayor/menor, hospitalización, hospedaje, estética canina/felina, exámenes laboratorio, radiografía, ecografía, eutanasia, cremación. Incluye costos directos del medicamento/insumos, márgenes target, urgencia/sábado/domingo recargo. Usar cuando el usuario diga tarifario veterinario, cuánto cobrar, precios vet, costo cirugía, precio esterilización, hospitalización mascota. NO usar para urgencias (urgencias-protocolo) ni cotizaciones individuales (otro skill).
allowed-tools: Read, Write, Edit
---

# Tarifario servicios veterinarios

## Estructura del tarifario

```json
{
  "categoria": "consulta",
  "servicio": "Consulta general primera vez",
  "precio_mxn": 450,
  "duracion_estimada_min": 30,
  "incluye": [
    "Exploración física completa",
    "Revisión expediente clínico",
    "Indicaciones diagnósticas iniciales",
    "Receta si necesaria"
  ],
  "no_incluye": [
    "Exámenes laboratorio",
    "Radiografías",
    "Medicamentos administrados",
    "Procedimientos en cita"
  ],
  "costo_insumos_directo_mxn": 30,
  "margen_estimado": 0.93
}
```

## Categorías y precios típicos (referencia CDMX 2026)

⚠ Rangos variables. Clínicas barrio cobran ~30-50% menos, premium 50-100% más.

### Consultas
| Servicio | Precio |
|---|---|
| Consulta general primera vez | $450-650 |
| Consulta seguimiento | $300-450 |
| Consulta especialidad (dermatología, neuro) | $700-1,200 |
| Consulta a domicilio | $800-1,500 (+ traslado) |

### Vacunación
| Vacuna | Precio |
|---|---|
| Multivalente (DAPP perro / FVRCP gato) | $250-380 |
| Antirrábica | $180-280 |
| Leptospirosis | $200-300 |
| Bordetella | $250-380 |
| Leucemia felina (FeLV) | $300-450 |
| Paquete cachorro completo (3-4 dosis) | $1,500-2,200 |

### Esterilización
| Servicio | Precio |
|---|---|
| Castración macho perro pequeño | $1,500-2,800 |
| Castración macho perro grande | $2,200-3,800 |
| Ovariohisterectomía hembra perro pequeño | $2,500-4,200 |
| Ovariohisterectomía hembra perro grande | $3,500-5,500 |
| Castración macho gato | $850-1,400 |
| Ovariohisterectomía hembra gata | $1,500-2,400 |

### Cirugías menores
| Servicio | Precio |
|---|---|
| Limpieza dental con anestesia | $1,800-3,500 |
| Extracción molar | $800-1,500 |
| Sutura de herida | $400-1,200 |
| Drenaje absceso | $500-1,000 |
| Cirugía oftalmológica menor | $1,500-3,000 |

### Cirugías mayores
| Servicio | Precio |
|---|---|
| Tumor pequeño (extirpación) | $2,500-5,500 |
| Cesárea | $4,000-8,000 |
| Fractura sin osteosíntesis | $3,000-6,500 |
| Fractura con clavo/placa | $8,000-25,000 |
| Cirugía abdominal mayor | $6,000-15,000 |

### Hospitalización
| Servicio | Precio/día |
|---|---|
| Hospitalización general | $800-1,500 |
| Cuidados intensivos | $1,500-3,500 |
| Aislamiento (infeccioso) | $1,200-2,200 |

Incluye: alimentación + medicación administrada + monitoreo. NO incluye exámenes adicionales.

### Estética canina
| Servicio | Precio |
|---|---|
| Baño raza chica | $200-350 |
| Baño raza grande | $350-600 |
| Corte estético raza chica | $350-550 |
| Corte estético raza grande | $500-900 |
| Corte uñas | $80-150 |
| Limpieza oídos | $100-200 |

### Estética felina (más cara — manejo difícil)
| Servicio | Precio |
|---|---|
| Baño gato | $400-700 |
| Corte higiénico gato | $500-900 |
| Sedación leve para baño difícil | +$300-500 |

### Exámenes laboratorio
| Examen | Precio |
|---|---|
| Hemograma completo | $250-450 |
| Química sanguínea básica | $400-700 |
| Química sanguínea completa | $700-1,200 |
| Examen general orina | $200-350 |
| Cuádruple felino (FeLV+FIV) | $500-800 |
| Heces (parásitos) | $150-250 |
| Citología | $400-700 |
| Biopsia (envío laboratorio externo) | $800-2,500 |

### Radiografía + Ecografía
| Servicio | Precio |
|---|---|
| Rayos X 1 placa | $400-700 |
| Rayos X 2 placas | $700-1,200 |
| Rayos X serie completa | $1,200-2,200 |
| Ecografía abdominal | $800-1,500 |
| Ecocardiograma | $1,500-3,000 |
| Endoscopia | $2,500-5,000 |

### Fin de vida
| Servicio | Precio |
|---|---|
| Eutanasia (procedimiento) | $1,200-2,500 |
| Cremación individual | $1,500-4,500 |
| Cremación grupal | $600-1,200 |
| Urna estándar | $400-1,500 |
| Urna premium | $2,000-8,000 |

⚠ Eutanasia debe ofrecerse como SERVICIO COMPLETO (con sedación previa, ambiente tranquilo, sin prisa). Tutores en duelo necesitan tiempo, no proceso comercial frío.

## Reglas de tarificación

### Recargo nocturno/festivo
- Lun-Vie 8pm-8am: +30%
- Sábado todo el día: +20%
- Domingo y festivos: +40%
- Urgencias 24h reales: +50%

### Pacientes grandes vs pequeños
Cirugías y vacunas: ajustar por peso
- Hasta 10 kg: precio base
- 10-25 kg: +20%
- 25-40 kg: +40%
- > 40 kg: +60% (rotweiler, mastín, etc.)

### Exóticos (premium)
Aves, reptiles, hurones requieren conocimiento especializado:
- Recargo +40-80% vs equivalente en perro/gato

### Convenios (refugios, ONGs)
Descuentos 20-40% para casos sociales con documentación.

## Output estructurado

```json
{
  "cotizacion_servicio": {
    "mascota": "Luna",
    "peso_kg": 28.5,
    "servicios_solicitados": [
      {
        "servicio": "Esterilización ovariohisterectomía",
        "precio_base_mxn": 3500,
        "ajuste_peso": "+20% (10-25 kg)",
        "precio_ajustado_mxn": 4200,
        "incluye": ["Cirugía", "Anestesia", "Hospitalización 1 día", "Antibiótico post"],
        "no_incluye": ["Collar isabelino ($150)", "Visita retiro puntos ($300)"]
      }
    ],
    "examenes_pre_quirurgicos_sugeridos": [
      {"examen": "Hemograma completo", "precio_mxn": 350},
      {"examen": "Química sanguínea básica", "precio_mxn": 550}
    ],
    "total_estimado_mxn": 5100,
    "recargo_aplicable": "ninguno",
    "fecha_recomendada": "antes del primer celo (8-10 meses)",
    "advertencias": [
      "Ayuno 12h antes de la cirugía",
      "Llevar collar isabelino post-cirugía"
    ]
  }
}
```

## Validación pendiente

- Comparativa de precios CDMX vs GDL vs MTY (2026)
- Costos reales de medicamentos veterinarios actuales
- Tarifas hospitalarias por especialidad
- Lista de equipamiento por nivel de clínica (general / especialidad / hospital)
