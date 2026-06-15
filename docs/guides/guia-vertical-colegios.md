# Guía vertical: colegios-mx

**Propósito**: cómo usar el plugin para colegios privados K-12.

**Audiencia**: directores administrativos, dueños de colegio, equipo administrativo.

**Pre-lectura**: [guia-instalacion.md](guia-instalacion.md), advertencia de [estado-real.md](estado-real.md).

---

## ⚠ Advertencia crítica

**colegios-mx tiene RIESGO REGULATORIO ALTO**. Antes de usar en operación real:
1. Validar con contador especializado en educación
2. Validar formato de constancias con SEP del estado del colegio
3. Validar política de cobranza con abogado educativo
4. Conseguir partner del sector que opere el plugin 6-8 semanas antes de exponer a padres

Sin estos pasos: riesgo de multas SAT (CFDI mal emitido), conflicto con padres (cobranza mal hecha), y rechazo SEP (constancias mal formateadas).

---

## Para quién es este plugin

- Colegios privados K-12 con 50-1500 alumnos
- Kínders independientes
- Equipo administrativo de 2-8 personas
- Régimen 603 (PM no lucrativa), 601 (PM lucrativa), o 626 (RESICO PM)

---

## Skills propios

| Skill | Propósito |
|---|---|
| `cobranza-colegiaturas` | 5 etapas con tono empático para padres |
| `comunicacion-padres-wa` | Templates UTILITY académicos/administrativos/operativos |
| `constancias-academicas` | Inscripción, estudios, boleta, parcial |
| `cfdi-colegiaturas-deducibles` | UsoCFDI D10 + complemento InsEduc |

---

## Commands

- `/colegios:cobranza <familia>` — siguiente paso cobranza
- `/colegios:aviso-padres <tipo> [grupo]` — aviso masivo segmentado
- `/colegios:constancia <alumno> [tipo]` — generar documento
- `/colegios:facturar-colegiatura <familia> <mes>` — CFDI deducible

---

## Flujos operativos típicos

### Flujo 1: Día de cobro (día 1 del mes)

```
Usuario: "Necesito enviar recordatorios de colegiatura de abril a todos los
        padres con saldo pendiente."

Claude → Lee lista de familias con adeudo (de tu sistema o CSV).
        Para cada una:
        - Determina etapa (días de mora actual)
        - Genera template apropiado con datos del alumno
        - Marca cuáles requieren llamada vs WA vs carta formal
        
        Estadísticas:
        - 47 familias en etapa 1 (1-3 días)
        - 12 familias en etapa 2 (10-15 días) → con recargo
        - 3 familias en etapa 4 (carta formal)
        
        Estimado: 5-7 hrs ahorradas vs proceso manual.
```

### Flujo 2: Aviso masivo de suspensión

```
Usuario: "Mañana viernes 15 marzo no hay clases por consejo técnico SEP.
        Aviso a TODO el colegio."

Claude → /colegios:aviso-padres suspension todo-colegio
        
        Genera template UTILITY:
        "Hola {{nombre}}, les informamos que el viernes 15 de marzo
        *NO habrá clases* en todo el colegio por motivo de consejo técnico SEP.
        Las actividades se reanudan el lunes 18.
        Cualquier duda, llámenos al [tel]."
        
        Alerta de saturación: "Es el 3er mensaje a las familias esta semana.
        ¿Confirmar envío?"
        
        Output: lista de 480 destinatarios + CSV exportable.
```

### Flujo 3: Facturación mensual de colegiaturas

```
Usuario: "Facturar colegiaturas de abril a las 320 familias que ya pagaron."

Claude → Para cada familia:
        /colegios:facturar-colegiatura <familia> abril
        
        - Lee datos: alumno, CURP, padre receptor, RFC
        - Valida forma de pago electrónica (no efectivo)
        - Construye CFDI con UsoCFDI D10
        - Agrega complemento InsEduc
        - Timbra (mock o PAC real)
        - Genera XML + PDF
        - Manda WA al padre con link de descarga
        
        Alertas detectadas:
        - 2 familias con CURP inválido del alumno → no se factura, pedir corrección
        - 5 familias pagaron en efectivo → no podrán deducir, avisar
        - 1 familia con padres separados → confirmar a quién facturar
```

### Flujo 4: Constancia de inscripción (papá pide)

```
Usuario: "El papá de Diego (5to A) me pide constancia de inscripción
        para abrir cuenta bancaria del niño."

Claude → /colegios:constancia diego-perez inscripcion
        
        Lee config del colegio (razón social, CCT, RVOE, director).
        Genera constancia con datos correctos.
        Marca pendiente firma director + sello.
        Sugiere: "Imprimir en papel membretado, firmar, sellar, entregar."
```

### Flujo 5: Cierre de ciclo escolar

```
Usuario: "Cerramos el ciclo, necesito constancia anual de servicios educativos
        para los 320 padres + boletas finales de los alumnos."

Claude → Para cada padre:
        - Suma todos los CFDIs de colegiatura del año
        - Genera constancia anual con detalle mes a mes
        - Indica si deducción anual proyectada cabe en tope (Art. 151 LISR)
        
        Para cada alumno:
        - Lee calificaciones del ciclo
        - Genera boleta final
        - Marca aprobado/reprobado por materia
        - Promedio general
```

---

## Setup recomendado

### Config del colegio

`config/colegio.json`:
```json
{
  "razon_social": "Colegio Aurora SC",
  "rfc": "CAU010101ABC",
  "regimen_fiscal": "603",
  "cct": "09PPR1234A",
  "rvoe": {
    "numero": "20060123",
    "fecha": "DD/MM/AAAA",
    "nivel": "primaria"
  },
  "domicilio": {
    "calle": "...",
    "numero": "...",
    "colonia": "...",
    "ciudad": "CDMX",
    "estado": "Ciudad de México",
    "cp": "06700"
  },
  "telefono": "55-1234-5678",
  "email": "admin@colegioaurora.mx",
  "director": {
    "nombre_completo": "...",
    "cargo": "Director General"
  },
  "datos_bancarios": {
    "banco": "BBVA",
    "clabe": "..."
  },
  "preferencias_cobranza": {
    "recargo_mensual_pct": 3,
    "dias_etapa_2": 10,
    "dias_etapa_3": 20,
    "dias_etapa_4": 35,
    "dias_etapa_5": 50
  }
}
```

### Estructura de familias

`familias/<id-familia>/ficha.json`:
```json
{
  "id": "001234",
  "padres": [
    {"nombre": "...", "rfc": "...", "regimen": "...", "es_receptor_cfdi": true},
    {"nombre": "...", "rfc": "...", "regimen": "..."}
  ],
  "alumnos": [
    {
      "nombre_completo": "Diego Perez Rodriguez",
      "curp": "PERD150301HDFRZG02",
      "matricula": "MAT-1234",
      "grado": "5to",
      "grupo": "A",
      "ciclo": "2025-2026"
    }
  ],
  "esquema_pago": {
    "metodo_pago_default": "PUE",
    "forma_pago_default": "03",
    "moneda": "MXN"
  },
  "consentimientos": {
    "aviso_privacidad": true,
    "marketing_eventos": true,
    "comunicacion_operativa": true,
    "fotos_publicacion": false
  }
}
```

---

## KPIs sugeridos

| KPI | Target nacional | Target con plugin |
|---|---|---|
| Cartera vencida | ~18% promedio MX | < 8% |
| Tiempo en cobranza al mes (admin) | 25-40 hrs | < 10 hrs |
| % CFDIs deducibles emitidos correctamente | desconocido | > 99% |
| Tasa de respuesta a WhatsApp masivo | 60-75% | > 85% |
| Reclamos PROFECO por cobranza | ocasionales | 0 |

---

## Compliance crítico

| Marco | Cobertura del plugin | Acción requerida |
|---|---|---|
| Art. 151 LISR fracción VIII (colegiaturas deducibles) | Estructura correcta | Validar topes vigentes |
| Complemento InsEduc | Estructura incluida | Verificar versión vigente |
| NOM-024 (expediente clínico — si hay servicio médico escolar) | No cubierto | Skill aparte requerido |
| LFPDPPP (datos de menores) | Aviso de privacidad base | Validar con abogado |
| SEP/CCT/RVOE | Estructura general | Verificar formato del estado |
| Reglamento interno del colegio | No cubierto | El colegio lo redacta separado |

---

## Riesgos específicos

### Riesgo legal: retención académica
**NO retener boletas/certificados de ciclos pasados por adeudo**. SEP ha emitido pronunciamientos. El skill `cobranza-colegiaturas` te recuerda esto explícitamente, pero la decisión la toma el director.

### Riesgo fiscal: pago efectivo
Si el padre paga colegiatura en efectivo, el CFDI no le sirve para deducir. El skill alerta esto, pero requiere que el colegio:
- Pida formas de pago electrónicas como default
- O explique al padre que el CFDI sirve para contabilidad del colegio pero no para su deducción personal

### Riesgo reputacional: cobranza pública
Publicar listas de morosos, exponer al padre frente a otros padres, daño moral. El skill nunca lo sugiere, pero hay que capacitar al equipo administrativo.

---

## Ver también

- [estado-real.md](estado-real.md) — colegios-mx tiene score 4.2/9 (más bajo)
- [plan-afinacion.md](plan-afinacion.md) — semanas 25-36 para llevar a producción
- [compliance-checklist.md](compliance-checklist.md) — checklist educativo
