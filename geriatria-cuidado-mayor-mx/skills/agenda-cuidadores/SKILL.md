---
name: agenda-cuidadores
description: Organiza turnos rotativos de cuidadores formales (personas trabajadoras del hogar o de agencia, con alta obligatoria al IMSS) e informales (familiares) para cubrir atención 24/7 del adulto mayor. Calcula horas y pagos conforme a la LFT: jornada nocturna (20:00-06:00, máximo 7 h), prima dominical 25% (Art. 71), descanso obligatorio laborado con salario doble adicional (Arts. 74-75), tiempo extra (Arts. 66-68) y reglas del capítulo de personas trabajadoras del hogar. Gestiona el relevo entre turnos con bitácora (caídas, comidas, medicamentos, incidentes) y avisa al familiar principal cuando un turno queda descubierto. Usar cuando el usuario diga "turno cuidador", "agenda enfermera", "cuidador 24 horas", "rotación cuidadores", "guardia abuelita", "cuidadora de planta". NO usar para nómina general (nomina-pymes-mx) ni para pago a cuidador único.
allowed-tools: Read, Write, Edit
---

# Agenda de cuidadores en turnos

## Modalidades típicas

### Caso 1: Cuidadora 24h cama adentro

- 1 cuidadora vive en casa (persona trabajadora del hogar, LFT Título Sexto, Capítulo XIII, Arts. 331-343)
- Descanso semanal de **día y medio** ininterrumpido, preferentemente sábado y domingo (Art. 336); si vive en el domicilio, descanso nocturno mínimo de 9 h consecutivas y 3 h diarias entre actividades (Art. 333). Confianza media: verificar texto vigente
- Salario ≥ salario mínimo ($315.04 diarios en 2026; $440.87 en ZLFN)
- Alta obligatoria al IMSS como persona trabajadora del hogar (régimen obligatorio desde la reforma a la LSS de 2022)
- Contrato por escrito (Art. 331 Ter). CFDI de nómina: verificar la facilidad vigente del SAT/IMSS para patrones de trabajadoras del hogar

### Caso 2: Turnos 12x12

- 2 cuidadoras se alternan 12h cada una
- Ojo: 12 h exceden la jornada diurna (8 h) y la nocturna (7 h); las horas excedentes son tiempo extra salvo pacto válido de jornada. Revisar con contador laboral
- Sumar horas del mes por cuidadora

### Caso 3: Turnos 8h con familiares

- Hijos/nietos cubren turnos cuando pueden
- Profesional cubre gaps
- Calendario compartido

## Cálculo de plus salariales

| Concepto | Aplicación | Porcentaje |
|---|---|---|
| Jornada nocturna | 20:00-06:00 (Art. 60) | Máximo 7 h (Art. 61). La LFT **no** fija prima nocturna; un "plus nocturno" es pacto voluntario |
| Prima dominical | Trabajar en domingo (Art. 71) | +25% sobre salario de un día ordinario |
| Descanso obligatorio laborado | Días del Art. 74 LFT | Salario doble adicional al del día (triple en total, Art. 75) |
| Descanso semanal laborado | Art. 73 | Salario doble adicional |
| Tiempo extraordinario | Exceso de la jornada legal | Primeras 9 h/semana al 200% (Art. 67); excedente al 300% (Art. 68) |

**Reforma 40 horas**: decreto constitucional DOF 03-03-2026 y reforma a la LFT DOF 01-05-2026 reducen la jornada máxima semanal de 48 h a 40 h de forma escalonada (46 h en 2027 hasta 40 h en 2030, según fuentes secundarias). En 2026 sigue el límite de 48 h; verificar en el texto publicado las nuevas reglas de tiempo extra.

## Handoff (bitácora de turno)

```
fecha_turno: 2026-10-14
horario: 19:00 - 07:00
cuidador: María González
eventos:
  - 19:30: tomó cena completa
  - 20:00: medicamentos cumplidos (metformina + losartan)
  - 22:00: dormido sin problema
  - 02:00: despertó, fui al baño, regresó a dormir
  - 06:30: levantado, ánimo normal
incidencias_importantes:
  - Ninguna
medicamentos_pendientes_siguiente_turno:
  - Insulina basal 07:30
  - Multivitaminico desayuno
firma_entrega: María González
firma_recibe: (próximo turno)
```

## Validación pendiente

⚠ Cálculos orientativos: validar con contador laboral, sobre todo jornadas de 12/24 h y la transición a 40 horas.
⚠ Los familiares que cuidan sin pago no son trabajadores; no aplica la LFT.
