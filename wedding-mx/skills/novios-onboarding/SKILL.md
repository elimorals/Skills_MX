---
name: novios-onboarding
description: Onboarding inicial de novios para wedding planner — captura visión del evento, lista preliminar de invitados, presupuesto disponible, fecha tentativa, ubicación preferida, valores y prioridades (música > comida > deco), datos fiscales para CFDI. Sesión estructurada de 90 min en persona o video llamada. Genera documento "Brief de boda" que se referencia el resto del proyecto. Usar cuando el usuario diga novios nuevos, onboarding evento, primera reunión, brief boda, capturar visión. NO usar para contratos (contrato-boda-pf-pm) ni timeline (otro skill).
allowed-tools: Read, Write, Edit
---

# Onboarding de novios

La primera reunión define el éxito. Capturar todo lo necesario sin abrumar.

## Estructura de la sesión (90 minutos)

### Fase 1: Visión (20 min)
Preguntas abiertas:
- "Describan su boda ideal en 3 palabras"
- "¿Qué es lo que NO quieren en su boda?"
- "¿Tienen alguna referencia (Pinterest, Instagram, boda que vieron)?"
- "¿Religiosa, civil, o ambas? ¿Por qué?"

### Fase 2: Datos básicos (15 min)
- Nombres + apellidos
- Edades
- Profesiones (relevante para timeline)
- Cuántos años de relación
- ¿Hijos? (si sí, ¿participan?)
- ¿Familias bien? (si hay tensiones, planear con tacto)

### Fase 3: Presupuesto (15 min)
**Pregunta clave**: "¿Cuál es el rango cómodo y cuál es el techo absoluto?"

Sin esto no se puede planear. Si los novios no saben:
- "Una boda de 200 invitados en CDMX va de unos $630k a $1.3M antes de IVA en gama baja-media (referencia orientativa, ver `cotizacion-boda-mxn`). ¿Eso está en su rango?"
- Identificar si requieren financiamiento del banco / familia

### Fase 4: Invitados (15 min)
- Número aproximado (200-500 típico MX)
- ¿Quiénes son los más importantes? (que pueden mover fecha si no van)
- ¿Hay invitados internacionales? (visa, vuelo, hospedaje)
- ¿Niños? (afecta menú, deco, timeline)

### Fase 5: Locación + fecha (10 min)
- ¿Ciudad o destino? (CDMX, GDL, MTY, Tulum, San Miguel)
- Fecha preferida + 2 alternativas
- Estación del año (alergias, lluvia, frío)
- ¿Hacienda, jardín, salón, hotel?

### Fase 6: Prioridades (10 min)
Pedir que rankeen 1-12:
- Banquete + bebida
- Locación
- Decoración + flores
- Música / DJ
- Fotografía + video
- Vestido + maquillaje
- Traje novio
- Anillos
- Transporte
- Hospedaje
- Papelería
- Coordinación

Los top 3 reciben 60-70% del presupuesto. Los bottom 3 son donde se pueden hacer recortes.

### Fase 7: Logística + datos fiscales (5 min)
- Tutor de presupuesto (¿quién aprueba gastos?)
- Datos para CFDI 4.0 de quien va a recibir las facturas (novios o familia): RFC, nombre exacto como aparece en la Constancia de Situación Fiscal, régimen fiscal y CP del domicilio fiscal. Si no quieren factura con RFC, se usa público en general.
- Email para envío de invitaciones digitales

### Datos personales (LFPDPPP)
Entrega el aviso de privacidad antes de capturar datos (LFPDPPP vigente, DOF 20-03-2025; autoridad: Secretaría Anticorrupción y Buen Gobierno). Religión, salud (alergias, embarazo) y datos de menores son **datos sensibles**: captúralos solo si se necesitan para el evento y con consentimiento expreso. La lista de invitados también son datos personales de terceros: úsala solo para el evento. Ver `compliance-lfpdppp`.

## Output: Brief de boda

```markdown
# Brief de Boda — {{novios}}

## Visión
- **Estilo**: {{estilo_3_palabras}}
- **Modalidad**: {{civil/religiosa/ambas}}
- **Sentido**: {{descripción_libre}}

## Detalles básicos
- **Novios**: {{nombres_completos}}
- **Edades**: {{edades}}
- **Fecha tentativa**: {{fecha}} (+ 2 alternativas)
- **Ciudad**: {{ciudad}}
- **Aniversario**: {{años_juntos}}

## Presupuesto
- **Rango cómodo**: ${{rango_low}} - ${{rango_high}}
- **Techo absoluto**: ${{techo}}
- **Fuente fondos**: {{ahorro_propio | familia | mixto | financiamiento}}

## Invitados
- **Número objetivo**: {{count}}
- **VIPs no negociables**: {{lista}}
- **Internacionales**: {{count_intl}}
- **Niños**: {{si/no, edades, cuántos}}

## Locación
- **Tipo preferido**: {{hacienda | hotel | jardín | salón}}
- **Distancia máxima del centro**: {{km}}
- **Locaciones específicas que les gustan**: {{lista}}

## Prioridades (ranking 1-12)
1. {{capitulo_top}}
2. {{capitulo_2}}
3. {{capitulo_3}}
... 

## Datos fiscales
- **RFC para CFDI**: {{rfc}}
- **Nombre / razón social**: {{nombre}}
- **CP domicilio fiscal**: {{cp}}
- **Régimen fiscal**: {{regimen}}
- **UsoCFDI sugerido**: S01 (sin efectos fiscales) o G03; una boda no es deducción personal

## Identificadores
- **WA principal**: {{tel_principal}}
- **Email**: {{email}}
- **Hashtag boda**: #{{hashtag}}

## Notas y caveats del planner
- {{tension_familia}}
- {{alergia_alimentaria}}
- {{religiosa_diversa}}
- {{cliente_tiene_amigo_que_es_dj_quiere_descuento}}
```

## Reglas para captar bien

1. **No vendan en la primera reunión** — solo captar. La cotización viene después con info digerida.
2. **Validar contra realidad** — si dicen "$300k para 500 invitados", honestidad: "Eso es $600/persona, en MX es difícil. Real ronda $4k-7k/persona."
3. **No prometer fecha sin confirmar locación** — saturada en alta temporada.
4. **Detectar red flags**:
   - Familia muy involucrada (puede generar conflictos)
   - Novios con presupuestos opuestos entre sí
   - Cambios de fecha probables por razones personales (no indagues datos de salud; si los novios los comparten, trátalos como sensibles)
   - Presión por fecha específica (a veces religiosa o cultural muy importante, a veces capricho que puede ajustarse)

## Output estructurado

```json
{
  "brief_boda_creado": {
    "fecha_creacion": "2026-06-18",
    "novios": "Ana M. + Carlos R.",
    "fecha_evento_objetivo": "2027-04-18",
    "invitados_objetivo": 200,
    "presupuesto_rango_mxn": [800000, 1300000],
    "ciudad": "CDMX",
    "modalidad": "civil_y_religiosa",
    "prioridades_top_3": ["banquete", "locacion", "fotografia"],
    "datos_fiscales_capturados": true,
    "alertas_planner": [
      "Mamá de la novia muy involucrada — alinear comunicación",
      "Padrino quiere participar como decorador (sin experiencia profesional)"
    ],
    "siguientes_pasos": [
      "Enviar 3 locaciones recomendadas en 5 días",
      "Cotización detallada en 10 días",
      "Firma de contrato planning en 14 días"
    ]
  }
}
```

## Validación pendiente

- Plantilla de brief en PDF profesional
- Cuestionario online previo para no perder tiempo en básicos
- Casos de éxito con bodas previas (referencias)
