---
name: urgencias-protocolo
description: Protocolo de triaje y manejo de urgencias veterinarias 24h. Clasificación nivel 1 (crítico, vida en juego), 2 (urgente, en horas), 3 (no urgente, agenda regular). Incluye instrucciones primeros auxilios al tutor por WhatsApp/teléfono (NO sustituye atención médica), decisión hospitalización vs casa, derivación a hospital 24h si la clínica no atiende noche, comunicación familia, autorización de procedimiento. Usar cuando el usuario diga urgencia mascota, accidente, atropellado, intoxicación, sangrado, dificultad respiratoria, convulsión, parto distócico, choque. NO usar para consulta no urgente (tarifario-servicios-vet).
allowed-tools: Read, Write, Edit
---

# Protocolo de urgencias veterinarias

## ⚠ Regla de oro

**NUNCA diagnosticar por teléfono/WhatsApp.** Siempre canalizar a atención presencial. El tutor puede subestimar gravedad o el caso requiere examen físico.

Los primeros auxilios por WA son SOLO para:
- Estabilizar mientras llega a clínica
- Indicar qué NO hacer (errores comunes)
- Evaluar nivel de urgencia para decidir clinica vs hospital 24h

## Triaje por nivel

### Nivel 1 — CRÍTICO (atender < 30 min)

Signos:
- Inconsciencia / no responde
- Dificultad respiratoria severa (lengua azul, jadeo extremo, gasping)
- Sangrado masivo no parable
- Convulsiones continuas > 5 min
- Atropellamiento confirmado (cualquier tamaño impacto)
- Trauma abierto (laceración profunda, hueso expuesto)
- Caída de altura > 1m con signos de dolor
- Quemadura > 10% superficie corporal
- Intoxicación confirmada (chocolate, xilitol, anticoagulante, etilenglicol)
- Distrocia (parto bloqueado) > 30 min sin progreso
- Shock evidente (encías pálidas, extremidades frías, taquipnea)
- Pinchamiento ojo / pérdida de visión aguda
- Quiebre de hueso visible
- Bote (gato) con uretra obstruida
- Vólvulo / torsión gástrica (perros grandes, abdomen distendido)

**Acción**: indicar al tutor venir AHORA. Si la clínica no abre, dirigir a hospital 24h más cercano. Llamar al teléfono mientras viene.

### Nivel 2 — URGENTE (atender < 4 horas)

Signos:
- Vómito persistente (> 3 episodios en 6h)
- Diarrea con sangre
- No comer ni beber > 24h
- Letargo extremo
- Cojera severa
- Sangrado interno sospechado (encías pálidas)
- Heridas pequeñas pero infectadas
- Picadura de insecto con inflamación masiva
- Mordedura de serpiente / perro
- Estreñimiento extremo > 48h
- Dificultad orinar/defecar
- Fiebre alta > 40°C
- Reacción alérgica medicamentosa (hinchazón cara, urticaria)

**Acción**: agendar misma tarde o noche. Indicar primeros auxilios mientras llega.

### Nivel 3 — NO URGENTE (agenda regular)

Signos:
- Comezón leve a moderada
- Pérdida apetito 1 comida
- Diarrea sin sangre 1-2 episodios
- Comportamiento "raro" sin signos físicos
- Cojera leve intermitente
- Mascota mayor con cambios graduales

**Acción**: agenda regular (24-72h).

## Primeros auxilios por WhatsApp/teléfono

⚠ Todo lo siguiente es solo para ESTABILIZAR mientras llegan a clínica. NO sustituye atención.

### Sangrado externo
> "Presiona con tela limpia o gasa SIN sacar. NO uses torniquete a menos que sea miembro y sangre arterial. Eleva la zona si es posible. Ven AHORA."

### Atropellamiento
> "NO la cargues sin tabla rígida. Tabla, cartón, sábana extendida. Inmoviliza. NO la fuerces a moverse. Llama al hospital 24h: {{tel}}."

### Intoxicación por chocolate / xilitol / anticoagulante
> "Trae el empaque del producto. Si hace menos de 2h: NO induzcas vómito hasta que un MVZ te indique. NO le des leche. NO le des nada por boca. Ven AHORA."

### Convulsión
> "NO le metas la mano en la boca (te muerde sin querer). Aleja objetos. Cronometrea tiempo. Si dura > 3 min, ven URGENTE. Filma si puedes para mostrar al MVZ."

### Vólvulo gástrico (perro grande, abdomen distendido como tambor)
> "Esta es EMERGENCIA CRÍTICA. Cada minuto cuenta. Ven AHORA. No le des agua. No la fuerces a moverse."

### Distocia (parto bloqueado)
> "¿Cuántos cachorros han nacido? ¿Hace cuánto el último? Si > 30 min sin contracciones efectivas, ven YA. NO empujes manualmente."

### Quemadura
> "Enfría con agua fresca (NO hielo) 10-15 min. NO apliques pomadas, mantequilla, ni dentífrico. Ven."

## Decisión hospitalización vs casa

### Hospitalizar si:
- Necesita fluidos IV continuos
- Necesita monitoreo 24h
- Procedimiento postquirúrgico complicado
- Convulsiones recurrentes
- Shock estabilizado pero inestable
- Tutor no puede medicar correctamente

### Casa con manejo si:
- Estable con medicación oral
- Tutor capacitado y responsable
- Condición controlable ambulatoria
- Costos prohibitivos hospitalización Y caso no crítico
- Mascota más tranquila en su entorno

## Autorización de procedimiento

Antes de cualquier procedimiento mayor:

1. **Explicar el procedimiento** en términos comprensibles
2. **Pronóstico realista** (no falsamente optimista ni catastrofista)
3. **Costos estimados con rango** (no comprometer precio cerrado en urgencia)
4. **Riesgos comunicados** (anestesia, complicaciones, mortalidad)
5. **Autorización firmada** (digital o física)
6. **Datos del tutor de emergencia** (si tutor principal no localizable)

```
Yo {{tutor}} con RFC/INE {{id}} autorizo a la clínica {{clinica}}
representada por el MVZ {{mvz}} cédula {{cedula}} a realizar el procedimiento
{{procedimiento}} en mi mascota {{mascota}}. Se me explicaron riesgos y costos
estimados entre $X y $Y MXN. En caso de complicación grave la clínica intentará
contacto antes de proceder a cirugía adicional.
Firma: {{firma_digital}}
Fecha: {{timestamp}}
```

## Comunicación durante hospitalización

- Update cada 6-8 horas mínimo
- Foto si paciente está estable (humaniza)
- Llamada del MVZ cada 24h
- Cualquier cambio crítico: llamada INMEDIATA al tutor

## Output estructurado

```json
{
  "triaje_urgencia": {
    "mascota": "Luna",
    "tutor": "Ana M.",
    "signos_reportados": [
      "Vómito 5 veces en 4 horas",
      "Letargia",
      "No bebe agua"
    ],
    "nivel_urgencia": 2,
    "tiempo_atencion_recomendado": "< 4 horas (tarde-noche hoy)",
    "primeros_auxilios_indicados": [
      "No dar agua ni comida hasta evaluación",
      "Observar si hay sangre en vómito",
      "Si hay convulsión o pérdida conciencia → nivel 1"
    ],
    "derivacion_si_aplica": null,
    "hospital_24h_cercano": null,
    "telefono_alerta": "+5215512345678",
    "siguiente_paso": "Agendar cita esta tarde 18:00 o llegar walk-in"
  }
}
```

## Validación pendiente

- Protocolo NOM aplicable (NOM-007-SAG/SCFI-2014)
- Lista hospitales 24h MX por ciudad (CDMX, GDL, MTY, Querétaro)
- Convenios entre clínicas para referencia
- Capacitación del staff en triaje (curso recomendado AMMVEPE)
