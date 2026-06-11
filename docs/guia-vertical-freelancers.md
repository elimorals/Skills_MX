# Guía vertical: freelancers-mx

**Propósito**: cómo usar el plugin `freelancers-mx` en operación diaria.

**Audiencia**: freelancers, consultores, agencias unipersonales en México.

**Pre-lectura**: [guia-instalacion.md](guia-instalacion.md).

---

## Para quién es este plugin

- Consultor tech (full-stack, DevOps, IA, seguridad)
- Diseñador, copywriter, fotógrafo, productor
- Agencia unipersonal o hasta 3 personas
- Régimen fiscal 612 (PFAE) o 626 (RESICO PF)
- Facturación entre $50k y $300k MXN/mes

Si encajas en 3+ de los anteriores, este plugin reduce tu carga administrativa entre 40-60%.

---

## Skills y commands disponibles

### Skills propios

| Skill | Propósito |
|---|---|
| `cotizacion-mxn` | Cotizaciones formato MX con IVA y retenciones |
| `propuesta-comercial` | Propuestas 3-15 páginas con SOW, T&Cs, PI, NDA |
| `cobranza-seguimiento` | Flujo 5 etapas escaladas |
| `cliente-onboarding` | Captura fiscal + contrato marco |
| `freelance-tax-mx` | Pago provisional ISR (RESICO/PFAE) + estimación anual |

### Skills heredados de core-mexico
`cfdi-emision`, `iva-retenciones-mx`, `rfc-validacion`, `whatsapp-business-mx`, `compliance-lfpdppp`, `mxn-formato`.

### Commands

- `/freelancers:cotizar <cliente> [scope]` — generar cotización
- `/freelancers:propuesta <cliente> [proyecto]` — propuesta comercial completa
- `/freelancers:cobranza <cliente>` — siguiente paso cobranza
- `/freelancers:onboarding <cliente>` — captura nuevo cliente
- `/freelancers:pago-provisional [mes año]` — cálculo del mes para SAT

---

## Flujos operativos típicos

### Flujo 1: Cliente nuevo de la a la z

```
Usuario: "Acabo de cerrar un nuevo cliente, Bimbo SA, para un proyecto de
        consultoría de migración a AWS por 3 meses."

Claude → (invoca cliente-onboarding)
        "Para registrarlos, necesito:
        - RFC y razón social exactos
        - Régimen fiscal (601 PM general probablemente)
        - Domicilio fiscal (al menos CP)
        - Uso CFDI preferido (G03 para empresas)
        - Contactos: ¿quién es decisor y quién operativo?"

Usuario: [provee datos]

Claude → Valida RFC, genera ficha JSON, contrato marco, aviso de privacidad.
        "Listo. Guardé ficha en clientes/bimbo/ficha.json.
         Contrato marco en clientes/bimbo/contrato-marco.md.
         ¿Procedo con la cotización del proyecto?"

Usuario: "Sí, scope: 3 entregables - assessment inicial, plan de migración,
         ejecución hands-on. Tarifa $250k MXN totales con 50% anticipo."

Claude → (invoca cotizacion-mxn)
        Aplica iva-retenciones-mx: PFAE→PM = 10% ISR + 10.6667% IVA ret.
        Genera cotización completa.

Usuario: "Conviértela a PDF y mándame el resumen para WhatsApp."

Claude → Genera PDF (skill pdf) + resumen breve.
```

### Flujo 2: Cobranza mensual

```
Usuario: "Bimbo no me ha pagado la factura del 15 de marzo, ya pasaron 12 días."

Claude → (invoca cobranza-seguimiento)
        Lee historial de cobranza (vacío → primer recordatorio? o etapa 2?).
        Detecta: 12 días = etapa 2 (recordatorio formal con recargo).

        "Generé recordatorio formal etapa 2 con cálculo de recargo:
        - Colegiatura: $150,000 MXN
        - Recargo 3% mensual × 12/30 días: $1,800
        - Total a la fecha: $151,800

        ¿Te paso el texto para WhatsApp o quieres email formal?"
```

### Flujo 3: Pago provisional mensual (día 15 del mes)

```
Usuario: "/freelancers:pago-provisional marzo 2026"

Claude → (invoca freelance-tax-mx)
        "Eres RESICO PF, ¿correcto? Para calcular necesito:
        - Total de CFDIs cobrados en marzo
        - Retenciones recibidas (de tus CFDIs a clientes PM)
        Puedo leer de tus CFDIs si me los pasas o capturarlos manualmente."

Usuario: [provee datos: $180,000 cobrados, $1,250 ISR retenido por PM]

Claude → Calcula:
        - Tasa aplicable: 1.5% (rango hasta $208,333)
        - ISR causado: $2,700
        - Retenciones acreditables: $1,250
        - ISR a pagar SAT: $1,450
        - Plazo: 17 abril 2026

        Alertas: "Detecté CFDI con FormaPago 99 marcado como cobrado.
        Posible inconsistencia. ¿Revisamos?"
```

### Flujo 4: Cierre anual

```
Usuario: "Necesito preparar declaración anual del ejercicio."

Claude → "Tengo registro de tus pagos provisionales y CFDIs del año.
        Estimación: ingreso anual $2.1M MXN, ISR pagado provisional $36k.
        
        Para deducción personal, ¿tienes:
        - CFDIs de honorarios médicos D01? (forma de pago electrónica)
        - CFDIs de colegiaturas D10 de tus hijos? (verificar topes)
        - Intereses hipotecarios?
        - Aportaciones SAR?
        
        Estimo saldo a favor probable: $X,XXX MXN.
        ¿Procedo a estructurar el detalle para que tu contador firme?"
```

---

## Setup recomendado (primera vez)

### 1. Crear estructura de archivos local

```
~/freelancer-ops/
├── clientes/
│   ├── bimbo/
│   │   ├── ficha.json
│   │   ├── contrato-marco-firmado.pdf
│   │   └── notas/
│   └── coca-cola/
├── cotizaciones/
├── propuestas/
├── cobranza/
├── cfdi/
│   ├── 2026/
│   │   ├── 03-marzo/
│   │   └── 04-abril/
├── fiscal/
│   ├── 2026-03-pago-provisional.md
│   └── 2026-anual.md
└── briefs/
```

### 2. Configurar tu config personal

Crea `~/freelancer-ops/config.json`:
```json
{
  "emisor": {
    "razon_social": "Tu Nombre Completo / Razón Social",
    "rfc": "TU_RFC",
    "regimen_fiscal": "626",
    "domicilio_cp": "06700",
    "domicilio_completo": "...",
    "email": "...",
    "telefono": "...",
    "wa_business_number": "...",
    "datos_bancarios": {
      "banco": "BBVA",
      "clabe": "...",
      "cuenta": "..."
    }
  },
  "preferencias": {
    "moneda_default": "MXN",
    "vigencia_cotizacion_dias": 15,
    "anticipo_default_pct": 50,
    "tasa_moratoria_mensual_pct": 3,
    "honorarios_minimos_hora": 600
  }
}
```

Cuando Claude pregunte datos del emisor, podrá leer este config (si lo apuntas) sin volver a pedirlos.

### 3. Arrancar primera sesión

```bash
cd ~/freelancer-ops
claude --plugin-dir ~/plugins-mx/freelancers-mx
```

Y le dices a Claude:
```
"Acabo de instalar el plugin freelancers-mx. Léeme docs/guia-vertical-freelancers.md
para tener contexto, luego empezamos."
```

---

## KPIs sugeridos para medir

| KPI | Target | Cómo medir |
|---|---|---|
| Tiempo en cotización promedio | < 15 min | Cronometrar |
| Tiempo en cobranza al mes | < 2 horas | Tracking manual |
| % de cotizaciones cerradas | > 30% | Pipeline en JSON |
| Cartera vencida (cualquier monto) | < 15% | Sumar de cobranza |
| CFDIs con error vs total | < 2% | Bitácora de cancelaciones |
| Días promedio cobro post-factura | < 30 días | Promedio de facturas pagadas |

---

## Recursos adicionales del vertical

### Templates listos para usar

- Plantilla de cotización: `freelancers-mx/skills/cotizacion-mxn/SKILL.md`
- Plantilla de propuesta: `freelancers-mx/skills/propuesta-comercial/SKILL.md`
- Templates WhatsApp UTILITY para cobranza: `_shared/whatsapp-business-mx/references/templates-aprobados.md`
- Contrato marco: `freelancers-mx/skills/cliente-onboarding/SKILL.md`
- Cartas de cobranza por etapa: `freelancers-mx/skills/cobranza-seguimiento/SKILL.md`

### Casos edge cubiertos

- Cliente extranjero (exportación servicios tasa 0%)
- Cliente RESICO PF (retención 1.25% en lugar de 10%)
- Anticipo sin proyecto definido (3 CFDIs)
- Cobro a través de plataforma (Stripe, PayPal)
- Refacturación por error

---

## Riesgos y limitaciones

Ver [estado-real.md](estado-real.md) para detalle. Resumen:

- **`freelance-tax-mx` tiene RIESGO REGULATORIO ALTO**: las tarifas Art. 96 pueden estar desactualizadas. **No usar para declaraciones reales sin validar con contador**.
- **Contratos marco**: NO revisados por abogado mercantilista. Aceptables como punto de partida; valida con abogado antes de firmar contratos sustanciales.
- **Cartas formales de cobranza**: NO revisadas por abogado. Si vas a juicio mercantil ejecutivo, valida con despacho.

---

## FAQs específicos del vertical

### ¿Puedo usar este plugin si soy de Sueldos y Salarios (régimen 605)?

Parcialmente. La parte de cotizaciones, propuestas, cobranza sí. La parte fiscal (`freelance-tax-mx`) es para 612 o 626, no para 605. Para 605 los impuestos los retiene tu patrón.

### ¿Y si tengo ingresos mixtos (sueldos + actividad profesional)?

`freelance-tax-mx` no maneja eso a profundidad. Cubre el cálculo de la parte profesional pero la declaración anual con mixto es más compleja y requiere contador.

### ¿El contrato marco aplica a todos mis clientes?

Es genérico para servicios profesionales. Funciona bien para 80% de casos. Casos especiales (licencias de software, fee-share, equity, exclusividad geográfica) requieren ajuste.

### ¿Puedo facturar a clientes extranjeros con este plugin?

Sí. El skill `cfdi-emision` cubre el caso de exportación de servicios (tasa 0%, RFC genérico XEXX010101000, ResidenciaFiscal). `iva-retenciones-mx` no aplica retenciones (extranjero no retiene).

### ¿Maneja CFDI de pagos (REP)?

Sí. Cuando emites un CFDI con MétodoPago = PPD y luego recibes el cobro, `cfdi-emision` puede generar el complemento de pago. Ver caso edge en `references/casos-edge-cfdi.md`.

---

## Ver también

- [flujos-operativos.md](flujos-operativos.md) — workflows cross-vertical
- [estado-real.md](estado-real.md) — score honesto por skill
- [plan-afinacion.md](plan-afinacion.md) — roadmap para llevar a producción
- [glosario-fiscal-mx.md](glosario-fiscal-mx.md) — términos fiscales
