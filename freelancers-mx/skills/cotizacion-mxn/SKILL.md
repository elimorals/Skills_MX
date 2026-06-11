---
name: cotizacion-mxn
description: Genera cotizaciones profesionales en formato mexicano para servicios de consultoría, desarrollo, diseño, contenido o cualquier servicio profesional facturable por freelancer/agencia. Incluye IVA 16%, retenciones (ISR 10% + IVA 10.6667% para PFAE 612 → PM; ISR 1.25% para RESICO 626 PF → PM), términos de pago parcializados (anticipo + entregas), vigencia, scope con deliverables, y cláusula de aceptación. Salida en markdown estructurado convertible a PDF o documento. Usar siempre que el usuario diga cotización, cotizar, presupuesto, propuesta económica, quote, budget, generar cotización, o esté preparando una respuesta económica a un cliente para servicios profesionales. NO usar para CFDI (esa es facturación real, no cotización) ni para licitación pública (esa tiene formato gubernamental específico).
allowed-tools: Read, Write, Edit
---

# Cotización MXN para freelancers

Genera cotizaciones que **se ven profesionales** y **calculan bien las retenciones**. Una cotización con cálculos correctos cierra negocio; una con cálculos mal genera disputa en pago.

## Estructura obligatoria

```markdown
# Cotización [NÚMERO]

**Fecha de emisión**: [DD de mes de AAAA]
**Vigencia**: [15 días naturales por default — ajustable]

---

## Datos del emisor

[Nombre o Razón Social]
RFC: [RFC]
Régimen Fiscal: [612 PFAE / 626 RESICO PF / 601 PM]
Domicilio: [completo o solo CP]
Contacto: [email / WhatsApp]

## Datos del cliente

[Razón Social o nombre]
RFC: [RFC del cliente]
Uso CFDI propuesto: [G03 lo más común]

---

## Alcance del servicio

[Descripción clara y específica del trabajo a realizar]

### Entregables
1. [Entregable 1]
2. [Entregable 2]
...

### Fuera de alcance
- [Lista de cosas que NO incluye, para evitar disputa después]

---

## Cronograma

| Hito | Fecha estimada | % del proyecto |
|---|---|---|
| Inicio del proyecto | [fecha] | 0% |
| [Hito 1] | [fecha] | 30% |
| [Hito 2] | [fecha] | 70% |
| Entrega final | [fecha] | 100% |

---

## Cálculo económico

| Concepto | Cantidad | Unidad | Precio unit. | Subtotal |
|---|---|---|---|---|
| [Servicio 1] | [n] | [unidad] | $X,XXX.XX | $X,XXX.XX |
| [Servicio 2] | [n] | [unidad] | $X,XXX.XX | $X,XXX.XX |

**Subtotal**: $X,XXX.XX MXN
**IVA 16%**: $X,XXX.XX MXN
[Si aplica:] **Retención ISR (10% PFAE / 1.25% RESICO)**: −$X,XXX.XX MXN
[Si aplica:] **Retención IVA (10.6667% PFAE)**: −$X,XXX.XX MXN

**Total del CFDI**: $X,XXX.XX MXN
**Neto a transferir al emisor**: $X,XXX.XX MXN

> Las retenciones las paga el cliente al SAT directamente. El emisor recibe el neto.

---

## Términos de pago

**Esquema sugerido**: [Anticipo 50% + 50% contra entrega] (ajustable)

- Forma de pago: Transferencia electrónica SPEI a la siguiente CLABE:
  - Banco: [BANCO]
  - CLABE: [XXX XXX XXX XXX XXX XX]
  - Beneficiario: [Nombre]
  - Referencia sugerida: [identificador]

- Plazo de pago: el anticipo a partir de la aceptación; el resto contra entrega.
- CFDI: se emite contra cada pago recibido. Si el cliente requiere CFDI antes (PPD), se emite previamente con complemento de pago al cobrar.

---

## Términos generales

1. **Propiedad intelectual**: [definir — típico: cliente recibe derechos sobre entregables al pago final; emisor conserva metodología y herramientas].
2. **Confidencialidad**: ambas partes mantienen confidencial la información intercambiada.
3. **Cambios de alcance**: cualquier modificación significativa requiere addendum por escrito y puede ajustar el precio.
4. **Cancelación**: si el cliente cancela después del anticipo, este no es reembolsable salvo causa imputable al emisor.
5. **Jurisdicción**: tribunales de [Ciudad de México / domicilio del emisor].

---

## Aceptación

Para aceptar esta cotización, responda a este correo/WhatsApp con la palabra **"ACEPTO"** indicando los datos fiscales finales para CFDI y confirmando el esquema de pago, o firme y devuelva esta cotización.

[Nombre del emisor]
```

## Reglas fiscales aplicadas

**Caso 1 — Freelancer PFAE 612 facturando a PM 601** (el más común):
```
Subtotal: $10,000.00
IVA 16%: $1,600.00
Retención ISR 10%: −$1,000.00
Retención IVA 10.6667%: −$1,066.67
Total CFDI: $11,600.00
Neto a recibir: $9,533.33
```

**Caso 2 — RESICO PF 626 facturando a PM 601**:
```
Subtotal: $10,000.00
IVA 16%: $1,600.00
Retención ISR 1.25%: −$125.00
Retención IVA: 0 (RESICO PF no genera retención IVA)
Total CFDI: $11,600.00
Neto a recibir: $11,475.00
```

**Caso 3 — Freelancer facturando a PF (cliente persona física)**:
```
Subtotal: $10,000.00
IVA 16%: $1,600.00
Total CFDI: $11,600.00
Neto a recibir: $11,600.00
(No hay retenciones; PF no retiene a PF)
```

**Caso 4 — Servicios al extranjero (exportación)**:
```
Subtotal: $10,000.00 (o en USD/EUR con TipoCambio DOF)
IVA 0%: $0.00
Total CFDI: $10,000.00
Neto a recibir: $10,000.00
(Tasa 0% por exportación, sin retenciones)
```

Para el cálculo correcto, invocar `iva-retenciones-mx` que tiene la matriz completa.

## Vigencia default y cuándo ajustar

- **Default**: 15 días naturales. Razonable para que cliente decida sin presionar.
- **30 días**: proyectos grandes (>$100k MXN) donde el cliente requiere aprobaciones internas.
- **7 días**: cuando hay capacidad limitada del emisor y necesita confirmar agenda rápido.

## Cronograma — buenas prácticas

- Definir "Inicio" como **fecha de recepción del anticipo**, no fecha de aceptación verbal.
- Reservar buffer en cada hito (no comprometer 100% del cronograma sin margen).
- Si el cliente puede retrasar entregables (ej. requiere su input para avanzar), incluir cláusula de "tiempo del cliente" que paraliza el cronograma sin penalizar al emisor.

## Datos que debes recopilar antes de generar

Si falta algo, **pregúntalo antes de redactar**:

1. **Del cliente**:
   - Razón social y RFC (para calcular retenciones correctas)
   - ¿Es PF o PM? (afecta retención)
   - Uso CFDI esperado (típicamente G03)

2. **Del scope**:
   - ¿Qué se entregará exactamente? Sé específico.
   - ¿Cuánto tiempo te llevará?
   - ¿Cuál es el costo de oportunidad / tarifa horaria implícita?

3. **Del esquema**:
   - ¿Pago en una sola exhibición o por hitos?
   - ¿Anticipo? % típico: 30-50%
   - ¿Moneda? MXN default; USD si cliente extranjero

## Salida esperada

1. Cotización completa en markdown (estructura anterior).
2. Resumen ejecutivo de 3 líneas para enviar por WhatsApp/email junto con el PDF.
3. Cálculos verificados con `iva-retenciones-mx`.
4. Alerta si:
   - Cliente PM y emisor RESICO PF: aclarar retención 1.25% (no el tradicional 10%)
   - Cliente extranjero: confirmar exportación de servicios y tasa 0%
   - Anticipo declarado pero ambiguo (¿anticipo de CFDI o solo enganche de proyecto?)

## Conversión a PDF

Si el usuario lo pide, puede usar:
- `pdf` skill del sistema para convertir markdown a PDF
- `docx` skill si prefiere Word
- Plantilla LaTeX si quiere algo más editorial

## Tono

Profesional pero no acartonado. Mexicano neutro. Sin tecnicismos fiscales en los apartados que el cliente lee (resumen, entregables). Los tecnicismos van en cálculo económico (sí necesarios) con nota breve para no-contadores.
