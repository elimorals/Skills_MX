---
name: manejo-resenas-hosts
description: Gestiona reseñas de huéspedes Airbnb/Booking/Vrbo del anfitrión generando respuestas a reseñas positivas y negativas según playbook validado (la respuesta a una mala reseña la VEN futuros huéspedes — vale más que la propia reseña), borradores que el host puede aprobar antes de publicar, detección de patrones críticos (varias reseñas mencionan ruido del aire acondicionado → comprar nuevo, varias reseñas mencionan internet lento → cambiar plan), estrategia para mejorar score promedio (próximo huésped feliz puede ser el que rompe inercia), y manejo de reseñas tóxicas con peso desproporcionado (un huésped enojado que escribe novela vs varios contentos en 1 línea — la matemática del review average castiga). Cubre solicitud activa de reseñas a huéspedes contentos (D+1 post checkout WhatsApp) y respuesta a reseñas del anfitrión hacia huésped (Airbnb permite responder y el huésped lo ve). Detecta reseñas con mentiras objetivas que ameriten reporte formal a Airbnb para revisión. Usar cuando el usuario diga "responder reseña", "mala calificación huésped", "manejo reviews", "mejorar puntuación airbnb", "reseña negativa". NO usar para reportes del huésped al anfitrión (eso es bidireccional pero requiere otra perspectiva).
allowed-tools: Read, Write, Edit
---

# Manejo de reseñas Airbnb

## Tipos de respuesta a reseña

### Reseña 5 estrellas — Respuesta de agradecimiento

> "¡Gracias [Nombre]! Fue un placer recibirte. Estaremos felices de hospedarte de nuevo cuando regreses a [ciudad]. Saludos."

### Reseña 4 estrellas — Reconocer + indagar

> "Gracias [Nombre] por tu reseña. Si hay algo específico en lo que podamos mejorar para tu próxima visita, nos encantaría saberlo. ¡Te esperamos pronto!"

### Reseña 3 estrellas — Tomar responsabilidad + acción

> "Hola [Nombre], gracias por tomarte el tiempo de dejarnos tu reseña. Lamentamos que tu experiencia no haya sido al 100%. Hemos tomado nota de [problema específico] y ya estamos trabajando en [acción concreta]. Esperamos darte una mejor experiencia próximamente."

### Reseña 1-2 estrellas — Manejo cuidadoso (clave para futuros huéspedes)

> "Hola [Nombre], lamentamos profundamente que tu estancia no haya cumplido tus expectativas. Recibimos tu retroalimentación sobre [problema] y queremos compartir el contexto: [explicación factual sin atacar al huésped]. Hemos implementado [acción correctiva concreta]. Apreciamos tu retroalimentación porque nos ayuda a mejorar."

## Reglas para mala reseña

🚫 **NUNCA**:
- Atacar al huésped ("tú fuiste el problema")
- Defenderse excesivamente
- Discutir en público
- Pedir que la retiren
- Sonar pasivo-agresivo

✅ **SIEMPRE**:
- Reconocer la queja específicamente
- Dar contexto factual sin culpar
- Mostrar acción correctiva concreta
- Mantener tono profesional
- Recordar que los futuros huéspedes LEEN la respuesta

## Detección de patrones críticos

Si en últimas 10 reseñas aparece N+ veces el mismo problema:

| Patrón mencionado | Umbral | Acción |
|---|---|---|
| Aire acondicionado | 3+ | Servicio o reemplazo |
| Internet lento | 3+ | Cambiar plan |
| Limpieza | 2+ | Cambiar limpiador/contrato |
| Check-in confuso | 3+ | Mejorar instrucciones |
| Ruido externo | 4+ | Aislar acústicamente o ajustar marketing |

## Solicitud activa de reseñas

Día post-checkout (a través de mensaje WhatsApp template):

> "Hola [Nombre], esperamos hayas tenido un excelente regreso a casa. Si te sentiste como en familia con nosotros, nos ayudaría mucho que dejes una breve reseña en Airbnb. Es lo que mantiene nuestro pequeño negocio en pie 🏡 [link directo]. ¡Gracias!"

## Reportar mentiras objetivas a Airbnb

Si huésped escribe falsedades demostrables (ej. "la cama estaba sucia" cuando hay foto de cama recién hecha tomada esa mañana):

1. Recolectar evidencia: fotos timestamp, conversaciones WhatsApp
2. Reportar vía panel de Airbnb: Help Center → Disputar reseña
3. Plazo: 14 días tras publicación
4. Airbnb evalúa y puede remover si claramente falso

## Métricas del host

```
Score promedio: 4.78/5 (últimas 50 reseñas)
Distribución:
  5 estrellas: 78%
  4 estrellas: 18%
  3 estrellas: 3%
  1-2 estrellas: 1%

Tasa de respuesta a reseñas: 100%
Tiempo promedio respuesta: 4.2 horas
```

## Validación pendiente

⚠ Tono de respuestas templates puede afinarse con datos reales del host.
