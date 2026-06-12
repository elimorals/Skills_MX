---
name: comunicacion-familiar-distribuida
description: Mantiene a la red familiar sincronizada sobre el estado del adulto mayor cuando los hijos viven en distintas ciudades o países (caso típico mexicano: 1 cuidador principal local + hermanos a distancia que aportan económicamente y emocionalmente) usando WhatsApp Business con templates aprobables Meta para tipos de mensaje (resumen diario corto, evento importante puntual, decisión pendiente que requiere consenso familiar, requerimiento urgente que necesita respuesta < 2 horas). Detecta y previene conflictos comunes: cuidador principal en burnout (sobrecarga emocional cuando solo 1 hijo soporta todo), hijo lejano que critica sin contribuir, decisiones unilaterales sin consultar (vender casa para pagar residencia, autorizar procedimiento médico riesgoso). Mantiene log de acuerdos familiares con timestamp + quién aceptó qué. Útil para herencia futura: la bitácora documenta quién contribuyó cuidado y cuánto. Usar cuando el usuario diga "comunicar familia", "grupo familiar WA", "decisión familiar", "consenso hermanos abuelita", "sincronizar familia". NO usar para comunicación con cuidadores (usar agenda-cuidadores) ni para grupos comerciales.
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

## Templates de mensajes (aprobables Meta)

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
