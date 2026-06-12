---
name: agenda-cuidadores
description: Organiza turnos rotativos de cuidadores formales (con vínculo laboral CFDI nómina + IMSS si residencia o agencia formal) e informales (familiares sin vínculo laboral, sin CFDI) cubriendo 24/7 cuando se requiere atención continua. Calcula horas trabajadas por cuidador con plus por trabajo nocturno (Art. 67 LFT — 25% de prima por horario nocturno 8pm-6am), domingos (25% prima dominical Art. 71 LFT), días festivos oficiales (Art. 75 LFT — pago triple si labora). Gestiona handoff entre turnos con bitácora de eventos (qué pasó en mi turno: caída a las 14:30, no quiso comer, vomitó medicamento) para continuidad de cuidados. Diferencia entre cuidador profesional certificado (mejor pagado, con seguro de responsabilidad civil) y cuidador básico. Notifica al familiar principal cuando un turno está descubierto. Usar cuando el usuario diga "turno cuidador", "agenda enfermera", "cuidador 24 horas", "rotación cuidadores", "guardia abuelita". NO usar para nómina general (usar nomina-pymes-mx) ni para pago a cuidador único.
allowed-tools: Read, Write, Edit
---

# Agenda de cuidadores en turnos

## Modalidades típicas

### Caso 1: Cuidadora 24h cama adentro

- 1 cuidadora vive en casa
- Descanso 1 día/semana (cubre relevo)
- Salario mensual cerrado + comida + hospedaje
- Tener CFDI Nómina como empleada doméstica (LFT capítulo XIII)

### Caso 2: Turnos 12x12

- 2 cuidadoras se alternan 12h cada una
- Pagos por turno
- Sumar horas mes + plus nocturno

### Caso 3: Turnos 8h con familiares

- Hijos/nietos cubren turnos cuando pueden
- Profesional cubre gaps
- Calendario compartido

## Cálculo de plus salariales

| Concepto | Aplicación | Porcentaje |
|---|---|---|
| Nocturno | 8pm-6am | +25% sobre tarifa hora |
| Dominical | Domingo de descanso | +25% |
| Festivo oficial laborado | Art. 74 LFT (8 días) | Pago triple |
| Tiempo extraordinario | >48 hrs/sem | +100% primeras 9 hrs, +200% siguientes |

## Handoff (bitácora de turno)

```
fecha_turno: 2026-06-12
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

⚠ Tarifas plus deben validarse contra LFT vigente. Cláusulas IMSS para empleadas del hogar tienen régimen especial.
