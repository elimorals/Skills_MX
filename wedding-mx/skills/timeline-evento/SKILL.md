---
name: timeline-evento
description: Timeline operativo para coordinación de boda — desde D-180 (cierre proveedores) hasta D+30 (cierre administrativo y agradecimientos). Hitos críticos con responsables, comunicaciones automatizadas por WhatsApp a novios y proveedores, alertas para deadlines (vencimiento contrato, último día reservar, prueba menú, prueba vestido). Genera Gantt visual. Usar cuando el usuario diga timeline boda, cronograma evento, plan de acción boda, organizar boda 6 meses, días previos, day-of, post-boda. NO usar para cotización (otro skill) ni contratos (otro skill).
allowed-tools: Read, Write, Edit
---

# Timeline operativo de boda

## Estructura del timeline

```
D-365 → Set fecha + presupuesto + locación
D-180 → Save the dates + proveedores principales firmados
D-120 → Pruebas iniciales + invitaciones impresas
D-90  → Confirmaciones (RSVP) + pagos anticipos
D-60  → Pruebas finales + ajustes
D-30  → Confirmaciones definitivas + pagos restantes
D-7   → Ensayo + briefing equipo
D-1   → Setup locación + día previo
D-0   → DÍA DEL EVENTO
D+1   → Post-evento + agradecimientos
D+30  → Cierre administrativo + álbum
```

## Hitos críticos por etapa

### D-365 a D-180: Decisiones estructurales

| Hito | Responsable | Días para realizar |
|---|---|---|
| Definir fecha tentativa | Novios | 0 |
| Set presupuesto total | Novios + planner | 7 |
| Definir invitados (lista preliminar) | Novios | 14 |
| Definir tipo (civil/religiosa/ambas) | Novios | 14 |
| Buscar locación + reservar | Planner | 30 |
| Firmar contrato locación | Novios | 60 |
| Anticipo locación (30-50%) | Novios | 60 |
| Save the dates enviados | Planner | 90 |

### D-180 a D-90: Proveedores principales

| Hito | Responsable | Notas |
|---|---|---|
| Cotizar 3 banquetes | Planner | Comparativo precio/calidad |
| Cerrar banquete (firmar contrato) | Novios | Anticipo 30% típico |
| Cotizar 3 DJ/banda | Planner | |
| Cerrar música | Novios | Anticipo 50% |
| Cotizar fotografía + video | Planner | |
| Cerrar foto+video | Novios | Anticipo 50% |
| Definir decoración + flores | Planner | |
| Cerrar decorador | Novios | |
| Definir transporte | Novios | |
| Comprar / mandar invitaciones impresas | Novios + planner | |

### D-90 a D-30: Confirmaciones y pruebas

| Hito | Responsable | Crítico si... |
|---|---|---|
| Lanzar RSVP (4 semanas) | Planner | Cualquier proveedor depende de número final |
| Prueba de menú | Novios + chef | Cambios sin costo si es 60+ días antes |
| Prueba vestido (1ra) | Novia | 2-3 meses para ajustes |
| Prueba peinado + maquillaje | Novia | |
| Prueba traje novio | Novio | |
| Lista de canciones DJ | Novios | |
| Confirmar honorarios juez/sacerdote | Novios | |
| Comprar/recoger anillos | Novios | |
| Definir orden ceremonia | Planner | |
| Definir layout mesa | Planner | |

### D-30 a D-7: Finalización

| Hito | Responsable | Notas |
|---|---|---|
| RSVP cierre (número final) | Planner | Comunicar a banquete |
| Pagar resto banquete | Novios | Típico D-7 |
| Pagar resto música | Novios | Típico D-7 |
| Pagar resto fotografía | Novios | Típico D-7 |
| Prueba vestido final | Novia | Última oportunidad ajustes |
| Confirmar transporte | Planner | |
| Lista de invitados con mesa asignada | Planner | |
| Briefing al equipo de servicio | Planner | |

### D-7 a D-1: Ensayo y setup

| Hito | Día | Responsable |
|---|---|---|
| Ensayo civil (si aplica) | D-3 | Juez + testigos + novios |
| Ensayo ceremonia religiosa | D-2 | Sacerdote + novios + cortejo |
| Briefing del equipo planner+proveedores | D-2 | Planner |
| Setup locación inicia | D-1 | Equipo locación |
| Decoración instala | D-1 | Decorador |
| Confirmar arribo equipo de servicio | D-1 | Planner |

### D-0: DÍA DEL EVENTO

```
07:00 — Novia arranca peinado/maquillaje
09:00 — Novio arranca preparación
11:00 — Llegada del equipo de coordinación a locación
13:00 — Llegada de proveedores (decoración final + montaje)
15:00 — Llegada del equipo de fotografía
16:30 — Inicio ceremonia
17:00 — Salida ceremonia + cocktail
18:30 — Banquete inicia
20:00 — Brindis novios
21:00 — Pista de baile abierta
23:00 — Mesa de dulces / postre
01:00 — Cierre formal
02:00 — Salida invitados / familia inmediata
03:00 — Equipo desmonta
```

### D+1 a D+30: Post-evento

| Hito | Responsable | Plazo |
|---|---|---|
| Agradecer proveedores | Planner | D+1 |
| Recoger objetos personales locación | Novios | D+1 |
| Aviso a familiares/invitados (gracias) | Novios | D+7 |
| Revisar fotos preview | Planner + novios | D+15 |
| Reclamaciones a proveedores (si aplica) | Novios | D+15 |
| Cierre fiscal del evento | Wedding planner | D+30 |
| Álbum + video entregados | Foto/video provider | D+60 (típico) |

## Recordatorios automatizados

WhatsApp templates por etapa:

**D-90 al novio/novia**:
> "Hola {{novios}} 💍 Estamos a 90 días! Esta semana hay que: ✅ lanzar RSVP a invitados, ✅ confirmar prueba de menú próxima semana, ✅ resto pago locación si aplica. Llamada esta tarde 5pm para revisar?"

**D-30**:
> "Hola {{novios}} 💍 Faltan 30 días! Esta semana cerramos número final de invitados, prueba vestido final, pago resto de banquete. Mensaje a todos los proveedores con confirmaciones."

**D-7**:
> "Hola {{novios}} 💍 Esta es la última semana! Ensayos {{fechas}}, briefing al equipo {{fecha}}. Pago final {{proveedores_pendientes}}. ¿Cómo se sienten? Llamada calmante 30 min hoy si quieren."

**D+1 a novios**:
> "{{novios}}! Felicidades 💕 Hoy descansen. Mañana coordinamos cierre, recoger objetos, agradecer a proveedores. Cuando estén listos me escriben."

## Output estructurado

```json
{
  "timeline_boda": {
    "fecha_evento": "2027-04-18",
    "dias_para_evento": 365,
    "etapa_actual": "D-365_a_D-180",
    "hitos_proximos_30d": [
      {
        "hito": "Set presupuesto total",
        "responsable": "Novios + planner",
        "deadline": "2026-06-18",
        "estado": "pendiente",
        "criticidad": "alta"
      },
      {
        "hito": "Definir invitados preliminar",
        "responsable": "Novios",
        "deadline": "2026-06-25",
        "estado": "pendiente",
        "criticidad": "alta"
      }
    ],
    "hitos_atrasados": [],
    "alertas": []
  }
}
```

## Validación pendiente

- Plazos típicos por proveedor MX (banquete cierra cuántos meses antes)
- Reglas civil/religiosa MX (papelería, registro civil, sacerdote)
- Variantes por boda de destino vs ciudad
- Casos edge (boda urgente < 3 meses, boda con embarazo, boda doble)
