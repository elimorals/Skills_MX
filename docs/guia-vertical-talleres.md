# Guía vertical: talleres-mx

**Propósito**: cómo usar el plugin para talleres mecánicos y servicios automotrices.

**Audiencia**: dueños y administradores de talleres mecánicos en México.

**Pre-lectura**: [guia-instalacion.md](guia-instalacion.md).

---

## Para quién es este plugin

- Taller mecánico independiente con 1-15 empleados
- Refaccionaria con servicio (mostrador + taller)
- Servicio electromecánico especializado
- Operación con clientes individuales (no flotillas grandes)

---

## Skills propios

| Skill | Propósito |
|---|---|
| `diagnostico-cotizacion` | Diagnóstico → cotización con desglose MO + refacciones |
| `autorizacion-cliente-wa` | Autorización por WhatsApp con bitácora auditada |
| `garantia-servicio` | Términos PROFECO + gestión reclamos |
| `orden-trabajo` | OT con firmas, inventario, check-out |

---

## Commands

- `/talleres:nuevo-diagnostico <cliente> <auto>` — abrir diagnóstico
- `/talleres:autorizacion <OT|DIAG>` — flujo autorización
- `/talleres:orden-trabajo <accion> <folio>` — abrir/modificar/cerrar OT
- `/talleres:garantia <accion> <OT>` — certificado o reclamo

---

## Flujo end-to-end del taller

```
1. Cliente llega con auto.
   ↓
2. /talleres:nuevo-diagnostico <cliente> <auto>
   - Captura datos vehículo (marca/modelo/año/VIN/placas/km)
   - Captura datos propietario
   - Captura síntomas verbatim del cliente
   - Mecánico revisa y documenta hallazgos
   - Sube fotos/video del problema
   - Genera cotización categorizada (urgente/recomendado/opcional)
   ↓
3. /talleres:autorizacion <DIAG-folio>
   - Envía mensaje WhatsApp al cliente con cotización + video
   - Cliente responde qué autoriza
   - Bitácora registra autorización con timestamp
   ↓
4. /talleres:orden-trabajo abrir <DIAG-folio>
   - Genera OT formal con trabajos autorizados
   - Cliente firma (tablet o impreso)
   - Mecánico inicia trabajo
   ↓
5. (Si descubre algo nuevo durante el trabajo)
   /talleres:autorizacion para trabajo adicional
   /talleres:orden-trabajo modificar <OT>
   ↓
6. Trabajo terminado.
   /talleres:orden-trabajo cerrar <OT>
   - Check-out con kilometraje, gasolina, inventario
   - Dispara CFDI (con datos fiscales del cliente)
   - Dispara certificado de garantía
   - WhatsApp al cliente: "auto listo"
   ↓
7. Cliente recoge, paga, firma check-out.
   Recibe CFDI + certificado de garantía + (opcional) refacciones reemplazadas.
   ↓
8. (Eventualmente, si reclama)
   /talleres:garantia reclamo <OT>
   - Valida vigencia
   - Diagnóstico de validación (Caso A/B/C/D)
   - Procede o no según corresponda
```

---

## Flujos típicos del día a día

### Mañana del taller

```
Usuario: "Necesito ver qué cotizaciones están sin respuesta hace más de 24h."

Claude → Lee bitácora-autorizaciones/
        Lista cotizaciones pendientes con días sin respuesta.
        Sugiere acción por cada una:
        - 1 día: recordatorio amable
        - 3 días: recordatorio con política de auto detenido
        - 5+ días: cargos por almacenamiento empiezan, aviso formal
```

### Diagnóstico nuevo común

```
Usuario: "Llegó un Jetta 2018 con ruido al frenar."

Claude → /talleres:nuevo-diagnostico
        Captura datos.
        
        Genera cotización:
        URGENTES:
        1. Cambio balatas delanteras (Brembo PD7589) - $1,650
        2. Cambio rotores delanteros (Brembo 08.5181) - $2,700
        
        RECOMENDADOS:
        3. Cambio filtro de aire - $250
        4. Cambio aceite (próximo a vencer por km) - $800
        
        OPCIONALES:
        5. Pulido de faros - $400
        
        Subtotal urgentes: $4,350
        + IVA: $696
        Total con todo: $6,720 incl IVA

        Genera mensaje WhatsApp con cotización + video del problema.
```

### Cierre de OT y CFDI

```
Usuario: "Terminamos el Jetta. Cliente paga con tarjeta."

Claude → /talleres:orden-trabajo cerrar OT-1234
        - Check-out automático: pide km final, nivel gasolina, inventario
        - Pregunta: ¿requiere CFDI? Si sí: datos fiscales del cliente
        - Aplica cfdi-emision para servicio (ClaveProdServ 78180100) + refacciones
        - Calcula IVA 16%
        - Genera CFDI mock (o real si Facturama está activo)
        - Genera certificado de garantía con plazos PROFECO
        - WhatsApp al cliente: "Tu Jetta está listo. Total $6,720 con IVA. 
                              Te esperamos en horario hábil."
```

### Reclamo de garantía

```
Usuario: "El cliente del Jetta regresa, dice que sigue chillando."

Claude → /talleres:garantia reclamo OT-1234
        Valida: hace 15 días del cierre → dentro de garantía MO (30d).
        
        Mecánico inspecciona y reporta:
        - Caso A: misma falla del trabajo original → CUBIERTA
          → Comunica al cliente, repara sin costo
        - Caso B: falla nueva (otro componente) → NO CUBIERTA
          → Genera nueva cotización
        - Caso C: uso indebido (cliente puso balatas de otro lado) → NO CUBIERTA
          → Comunica + cobra diagnóstico revisión
        
        Documenta el caso para defensa PROFECO si llegara queja.
```

---

## Setup recomendado

### Config del taller

```json
{
  "taller": {
    "razon_social": "Taller Aurora SA de CV",
    "rfc": "...",
    "regimen_fiscal": "601",
    "domicilio_completo": "...",
    "cp": "06700",
    "telefono": "...",
    "wa_business": "...",
    "horario": "Lun-Vie 8:00-18:00, Sab 8:00-14:00"
  },
  "tarifas": {
    "mano_obra_hora": 500,
    "diagnostico_minimo": 300
  },
  "garantia": {
    "mano_obra_dias": 30,
    "refacciones_nuevas_dias": 90,
    "refacciones_usadas_dias": 30
  },
  "politicas": {
    "almacenamiento_dias_gratis": 5,
    "almacenamiento_costo_dia": 100,
    "auto_abandono_dias": 90
  }
}
```

### Estructura de archivos

```
~/taller-ops/
├── config/taller.json
├── diagnosticos/
│   └── 2026-03-15-jetta-ABC1234/
│       ├── diagnostico.md
│       ├── fotos/
│       └── video.mp4
├── bitacora-autorizaciones/
│   └── DIAG-1234.json
├── ordenes-trabajo/
│   └── OT-1234/
│       ├── ot-inicial.md
│       ├── ot-modificacion-01.md
│       └── check-out.md
├── garantias/
│   ├── OT-1234.md       # Certificado
│   └── OT-1234-reclamo-2026-04-20.md
└── cfdi/
    └── 2026/03/F-1234.xml
```

---

## KPIs sugeridos

| KPI | Target |
|---|---|
| % cotizaciones cerradas (autorizadas) | > 60% |
| Tiempo promedio cotización → autorización | < 4h hábiles |
| Días promedio auto en taller (sin autorización) | < 2 |
| Reclamos de garantía / total OTs | < 5% |
| Reclamos PROFECO al año | 0 |
| CFDIs emitidos sin error | > 99% |
| Tasa de CFDI emitido al cierre | > 80% |

---

## Marco legal aplicable

| Marco | Cobertura del plugin |
|---|---|
| Ley Federal de Protección al Consumidor (LFPC) | Garantías mínimas |
| NMX-D-003-IMNC (talleres automotrices) | Estándar referenciado |
| PROFECO procedimiento de queja | Estructura de defensa con bitácora |
| LFPDPPP (datos del cliente) | Aviso de privacidad base |
| CFDI 4.0 (ClaveProdServ 78180100) | Emisión correcta |
| Ley antilavado (pagos efectivo > $645k MXN) | Alerta si se rebasa |

---

## Riesgos específicos

### Riesgo PROFECO
Cliente queja → PROFECO citatorio → audiencia → multa potencial.

**Mitigación con el plugin**:
- Bitácora WhatsApp con autorización explícita timestamped
- Diagnóstico con foto/video documentado
- OT firmada (digital o física)
- Certificado de garantía entregado

Con estos 4 documentos, defensa PROFECO es muy sólida.

### Riesgo de objeción al cobro
Cliente dice "no autoricé eso", "me cobraron más de lo que dijeron".

**Mitigación**:
- Cotización tiene desglose claro firmado/autorizado
- Cambios al alcance requieren nueva autorización registrada
- Check-out con firma del cliente al entregar

### Riesgo de auto en abandono
Cliente deja el auto y nunca lo recoge. Espacio ocupado, almacenamiento.

**Mitigación**:
- Política de almacenamiento declarada en cotización inicial
- Aviso formal al día 30, 60
- Procedimiento legal para abandono al día 90+
- (Requiere asesoría legal específica del despacho)

---

## Ver también

- [estado-real.md](estado-real.md) — talleres-mx score 4.4/9
- [plan-afinacion.md](plan-afinacion.md) — semanas 17-24 para producción
- [integracion-whatsapp.md](integracion-whatsapp.md) — para autorizaciones
