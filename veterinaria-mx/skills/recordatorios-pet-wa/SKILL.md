---
name: recordatorios-pet-wa
description: Templates de WhatsApp Business optimizados para clínicas veterinarias mexicanas — recordatorios de vacunas, citas, retiro de medicamento, resultado de exámenes, seguimiento post-cirugía, fecha de baño, control de peso, condolencias. Tono apropiado para tutores ansiosos (mascotas son familia). Considera diferencias entre tutor activo vs pasivo (timing y frecuencia). Usar cuando el usuario diga template wa veterinaria, mandar recordatorio mascota, mensaje dueño, comunicación clínica. NO usar para urgencias (urgencias-protocolo) ni vacunas standalone (vacunacion-calendario).
allowed-tools: Read, Write, Edit
---

# Recordatorios WhatsApp — veterinaria MX

Las mascotas son familia. El tono debe ser cálido pero profesional.

## Reglas de oro

1. **Nombre de la mascota** en cada mensaje (no "tu perro" sino "Luna")
2. **Emoji apropiado** (🐶 perro, 🐱 gato, no genéricos)
3. **Tutor (no propietario)** — implica responsabilidad afectiva
4. **No estresar** al tutor — evitar urgencias falsas
5. **Confirmación de lectura** — saber si el mensaje llegó
6. **No spam** — máximo 1 mensaje cada 3 días por cliente

## Templates por categoría

### Vacunación
Ver skill `vacunacion-calendario`. Templates listos para 30d/7d/24h.

### Cita médica programada

**Confirmación 24h antes**:
> "Hola {{tutor}} 🐶 Recordatorio: Luna tiene cita mañana {{fecha}} a las {{hora}} con MVZ {{mvz}}. Si no puedes asistir avísanos para reagendar."

**2h antes con dirección**:
> "Hola {{tutor}} 🐶 Te esperamos en 2 horas para la cita de Luna. {{direccion_consultorio}}. Mapa: {{link_maps}}"

### Retiro de medicamento

> "Hola {{tutor}} 💊 Ya está listo el medicamento de Luna: {{medicamento}}. Pásalo a recoger entre {{horario_apertura}}. Dosis: {{dosis_simplificada}}. Cualquier duda, escríbenos."

### Resultados de exámenes

**Resultados normales**:
> "Hola {{tutor}} ✅ Los resultados de Luna están listos y son normales 😊 Si tienes alguna pregunta, agenda llamada con el MVZ."

**Resultados que requieren consulta** (NUNCA dar diagnóstico por WA):
> "Hola {{tutor}} 📋 Ya tenemos los resultados de Luna. Para revisarlos juntos con el MVZ {{mvz}}, agenda una cita esta semana. Es importante que vengas para entender bien y planear los siguientes pasos."

### Seguimiento post-cirugía

**Día 1**:
> "Hola {{tutor}} 🐶 ¿Cómo amaneció Luna? Recuerda: collar isabelino puesto, no mojarla, dieta blanda primer día. Cualquier sangrado o vómito, llámanos {{tel_emergencia}} de inmediato."

**Día 3**:
> "Luna lleva 3 días post-cirugía 🩹 ¿Cómo va? Si todo bien: dieta normal a partir de hoy, sigue con antibiótico. Si tienes dudas, escríbenos."

**Día 10 (retiro de puntos)**:
> "Llegó el día del retiro de puntos de Luna 🐶 Agenda tu visita esta semana. Si no se han caído solos los puntos absorbibles, te ayudamos a verificar."

### Control de peso (en plan dietético)

> "Hola {{tutor}} 🐶 Recordatorio mensual: peso de Luna esta semana 📊 Si te conviene pasarla solo a la báscula sin consulta, sin cargo. Trae fotos de su comida actual."

### Baño y estética

> "Luna tiene cita de baño mañana 🛁 a las {{hora}}. Por favor llévala con la correa puesta. Si tiene parásitos visibles, avísanos para tratamiento adicional."

### Antiparasitario externo (pulgas/garrapatas)

> "Hola {{tutor}} 🐶 Hoy le toca a Luna su antiparasitario externo ({{producto}}). ¿Ya lo tienes en casa o quieres que te lo apartemos en clínica?"

### Antiparasitario interno (desparasitación)

> "Recordatorio: Luna debe desparasitarse este mes 🐛 (cada 3 meses recomendado). Si no tienes el medicamento, lo puedes recoger en clínica."

### Cita perdida (no-show)

> "Hola {{tutor}} 🐶 Luna no vino a su cita hoy. ¿Todo bien? Si todo OK, agendamos otro día. Si pasó algo, escríbenos para apoyarte."

### Condolencias (mascota fallecida)

⚠ Solo si el MVZ confirmó el fallecimiento. NO automatizar.

> "Querida {{tutor}}, lamentamos profundamente la partida de Luna 🌈 Fue un honor cuidarla en su camino. Si necesitas apoyo (tanatología, cremación, urna), aquí estamos. Te acompañamos en este momento."

### Cumpleaños mascota

> "🎂 Hoy Luna cumple {{años}} años! Felicidades {{tutor}}. Te invitamos a una visita de cortesía esta semana con baño gratis para festejar 🐶"

## Tipos de tutor (ajustar timing)

### Tutor super-activo
- Recordatorios 1 vez (24h antes)
- Sin necesidad de reforzar
- Responde rápido

### Tutor activo promedio
- Recordatorios 24h + 2h
- Confirmar con click en link

### Tutor pasivo / olvidadizo
- Recordatorios 30d + 7d + 24h + 2h
- Llamada del MVZ si > 60 días sin visitar
- Considerar cliente alto riesgo de churn

### Tutor con mascota crítica (cardiópata, diabético)
- Recordatorios semanales para medicación
- Tracking constante (no automatizable, semi-asistido)
- Mejor relación 1:1

## Validación pendiente

- Templates aprobados Meta WhatsApp Business para sector veterinario
- Tonos por región (CDMX más formal vs costas más casual)
- Casos de mascotas con tutores no responsables — protocolo legal
- Compliance LFPDPPP con datos de mascota (hay grises legales)
