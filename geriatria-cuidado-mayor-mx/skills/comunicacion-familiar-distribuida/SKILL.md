---
name: comunicacion-familiar-distribuida
description: Mantiene a la red familiar sincronizada sobre el estado del adulto mayor cuando los hijos viven en distintas ciudades o países (caso típico: un cuidador principal local + hermanos a distancia que aportan dinero o visitas). Redacta mensajes para WhatsApp (resumen diario, evento médico, decisión que requiere consenso, aviso urgente) y, si la familia usa WhatsApp Business API, los prepara como templates aprobables por Meta. Detecta señales de conflicto: cuidador principal en burnout, críticas sin aporte, decisiones unilaterales (vender la casa, autorizar un procedimiento riesgoso). Lleva bitácora de acuerdos con fecha y quién aceptó qué, útil como registro de aportaciones. Usar cuando el usuario diga "comunicar familia", "grupo familiar WA", "decisión familiar", "consenso hermanos abuelita", "sincronizar familia", "quién paga la residencia". NO usar para comunicación con cuidadores (agenda-cuidadores) ni para grupos comerciales.
allowed-tools: Read, Write, Edit
---

# Comunicación familiar distribuida

## Estructura del grupo familiar

```yaml
adulto_mayor_id: ABC123
cuidador_principal:
  nombre: María (hija mayor)
  ubicacion: CDMX
  rol: decide + cuida
familiares_distantes:
  - nombre: Carlos (hijo)
    ubicacion: Monterrey
    rol: aporta económicamente
    contacto: +52...
  - nombre: Patricia (hija menor)
    ubicacion: Texas USA
    rol: contribuye con visitas trimestrales
    contacto: +1...
medico_familiar:
  nombre: Dr. Hernández
  cedula: 9876543
  contacto: +52...
```

## Mensajes

En un grupo familiar de WhatsApp normal se envían como texto libre. Solo si la familia usa WhatsApp Business API se registran como templates (categoría UTILITY); Meta cobra por mensaje entregado desde el 01-07-2025 (ver skill `whatsapp-business-mx`).

### "utility_estado_diario"
> "Resumen del día de Mamá ($DIA): se levantó bien, comió 80% de las comidas, tomó todos los medicamentos. Sin incidencias."

### "utility_evento_medico"
> "Mamá tuvo cita con Dr. Hernández hoy. Cambió la dosis de metformina de 850mg a 500mg porque está más sensible. Próxima cita: $FECHA."

### "decision_familiar"
> "Necesitamos decidir juntos: la residencia subió la mensualidad de \$25k a \$30k. Opciones: A) seguir pagando, B) buscar otra, C) cuidar en casa rotativo. Reaccionen con A/B/C."

### "urgente_2h"
> "🚨 URGENTE - Mamá tuvo una caída pero está consciente. Estoy con ella en el ER. ¿Pueden llamarme en los próximos 30 min?"

## Detección de patrones

- **Cuidador principal en burnout**: si > 80% del esfuerzo recae en 1 persona → alertar redistribución
- **Hermano lejano crítico**: si > 50% de sus mensajes son críticos sin propuesta → flagear
- **Decisión unilateral**: si decisión importante (>$10k MXN o riesgo médico) se toma sin consulta → log + alerta a otros

## Bitácora de acuerdos

```
2026-04-15: Acuerdo: rotar visita semanal entre hermanos
  - María: aceptado
  - Carlos: aceptado (vendrá CDMX 2do fin de mes)
  - Patricia: aceptado (videollamada diaria)
2026-05-22: Acuerdo: cambiar a residencia "El Cardenal"
  - María: aceptado
  - Carlos: aceptado (aporta 60% mensualidad)
  - Patricia: aceptado (aporta 40%)
  Costo mensual: $28,500 MXN
```

> La bitácora es un registro de acuerdos, no un documento legal: no sustituye testamento, convenio ante notario ni designación de apoyos. Contiene datos de salud (sensibles, LFPDPPP): compártela solo con la familia involucrada.
