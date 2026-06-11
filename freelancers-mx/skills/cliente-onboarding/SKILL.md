---
name: cliente-onboarding
description: Captura completa y estructurada de datos fiscales, contacto y operativos de un nuevo cliente para freelancer/agencia en México. Recopila razón social, RFC, régimen fiscal, CP, uso CFDI preferido, datos de contacto del decisor y del operativo, esquema de pago acordado, datos para CFDI (forma de pago default), y opcionalmente constancia de situación fiscal. Genera ficha de cliente JSON estructurada, validación RFC inmediata, y plantilla de contrato marco de prestación de servicios profesionales en formato MX. Usar cuando el usuario diga onboarding, nuevo cliente, captura cliente, dar de alta cliente, ficha de cliente, client intake, KYC light, datos para facturar. NO usar para KYC bancario formal (eso es otra cosa, sigue circular CNBV).
allowed-tools: Read, Write, Edit
---

# Onboarding de cliente para freelancers

Captura ordenada de un cliente nuevo. Si te tardas 40 minutos en pedirle datos sueltos por WhatsApp, este skill te lleva los datos completos en una sola interacción.

## Estructura de la ficha de cliente

```json
{
  "ficha_cliente": {
    "id": "uuid-o-numero-secuencial",
    "fecha_creacion": "YYYY-MM-DD",

    "fiscal": {
      "razon_social": "string",
      "rfc": "AAAA000000XXX",
      "tipo": "PF | PM",
      "regimen_fiscal": "601 | 612 | 626 | ...",
      "uso_cfdi_preferido": "G03 | D01 | ...",
      "domicilio_fiscal": {
        "calle": "string",
        "numero_exterior": "string",
        "numero_interior": "string opcional",
        "colonia": "string",
        "municipio_alcaldia": "string",
        "estado": "string",
        "cp": "5 dígitos"
      },
      "constancia_situacion_fiscal_url": "opcional"
    },

    "contacto": {
      "decisor": {
        "nombre": "string",
        "cargo": "string",
        "email": "string",
        "telefono": "string con código país",
        "whatsapp_business": "boolean"
      },
      "operativo": {
        "nombre": "string",
        "cargo": "string",
        "email": "string",
        "telefono": "string"
      },
      "facturacion": {
        "email_envio_cfdi": "string",
        "requiere_orden_compra_previa": "boolean"
      }
    },

    "comercial": {
      "fuente": "referido | linkedin | web | evento | otro",
      "industria": "string",
      "tamano_empresa": "1-10 | 11-50 | 51-200 | 201-1000 | 1000+",
      "proyectos_iniciales": ["array de descripciones"],
      "esquema_pago_acordado": {
        "metodo": "PUE | PPD",
        "forma_pago_default": "03 | 04 | ...",
        "plazo_dias": 0,
        "anticipo_porcentaje": 30,
        "moneda": "MXN | USD | EUR"
      },
      "tipo_relacion": "proyecto_unico | retainer_mensual | hora_demanda"
    },

    "operativo": {
      "canal_comunicacion_preferido": "whatsapp | email | slack | otro",
      "tono_marca_cliente": "formal | informal | mixto",
      "stakeholders": ["lista de personas involucradas"],
      "notas_internas": "free text"
    },

    "compliance": {
      "aviso_privacidad_aceptado": "boolean",
      "fecha_aceptacion": "YYYY-MM-DD",
      "consentimiento_marketing": "boolean",
      "rfc_validado_estructura": "boolean",
      "rfc_validado_padron_sat": "boolean | null si no hay integración"
    }
  }
}
```

## Flujo de captura

Cuando el usuario invoca este skill para un cliente nuevo:

### Paso 1: Datos fiscales mínimos
"Para arrancar, necesito los datos fiscales del cliente para emitir CFDI cuando aplique:
- Razón social / nombre completo
- RFC
- Régimen fiscal (601 PM general, 612 PF act. empresarial, 626 RESICO, otro)
- Código postal del domicilio fiscal
- Uso CFDI preferido (por default sugerimos G03 para empresas)"

Mientras esperas respuesta, **valida cualquier RFC entregado con `rfc-validacion`** y avisa si hay problema estructural.

### Paso 2: Datos de contacto
"Ahora los contactos:
- ¿Quién es el contacto decisor (toma decisiones)? Nombre, cargo, email, teléfono.
- ¿Quién es el contacto operativo (con quien interactúas día a día)?
- ¿A qué correo se mandan los CFDIs?"

### Paso 3: Datos comerciales
"Para entender la relación:
- ¿Cómo llegaste a este cliente?
- ¿Qué industria? ¿Tamaño aproximado?
- ¿Qué proyectos vamos a hacer? (puedes describirlos a grandes rasgos)
- Esquema de pago: ¿PUE o PPD? ¿Hay anticipo? ¿En qué plazo paga?
- ¿Es proyecto único, retainer mensual o servicios bajo demanda?"

### Paso 4: Datos operativos
"Para la operación:
- ¿Canal de comunicación preferido?
- ¿Tono que usa la marca/empresa (te van a hablar formal o informal)?
- ¿Otros stakeholders del lado del cliente que debería tener en el radar?"

### Paso 5: Compliance
"Por LFPDPPP necesito confirmar:
- ¿Le envío el aviso de privacidad para que lo acepte?
- ¿Acepta recibir comunicaciones de marketing (newsletters, promociones)?"

### Paso 6: Generación de outputs

1. Ficha de cliente JSON estructurada (guardable en `clientes/[id-cliente].json`).
2. Resumen ejecutivo de 5 líneas en formato lectura.
3. **Contrato marco de prestación de servicios profesionales** pre-llenado (ver plantilla abajo).
4. Aviso de privacidad pre-llenado del lado del freelancer/agencia listo para mandar al cliente.

## Plantilla de contrato marco

```markdown
# Contrato Marco de Prestación de Servicios Profesionales

En la ciudad de [Ciudad], a los [DD] días del mes de [mes] de [AAAA], las partes que se identifican al pie suscriben el presente contrato marco bajo los siguientes:

## Antecedentes

I. [Nombre del Prestador], con RFC [RFC], domiciliado en [domicilio], en lo sucesivo "El Prestador", manifiesta contar con la capacidad técnica y profesional para prestar servicios de [naturaleza del servicio].

II. [Razón Social del Cliente], con RFC [RFC], domiciliado en [domicilio], representado por [representante legal] en su carácter de [cargo], en lo sucesivo "El Cliente", manifiesta requerir los servicios del Prestador.

## Cláusulas

### PRIMERA. Objeto

El Prestador prestará al Cliente servicios profesionales de [descripción general] bajo el esquema descrito en este contrato y en cada Cotización o Propuesta específica aceptada por ambas partes.

### SEGUNDA. Cotizaciones

Cada servicio específico requerirá una Cotización o Propuesta firmada por ambas partes que detalle alcance, entregables, plazo y monto. Las cotizaciones se incorporan a este contrato por referencia.

### TERCERA. Contraprestación

El Cliente pagará al Prestador los montos pactados en cada Cotización, en los plazos y condiciones ahí establecidos. El IVA y retenciones se calculan conforme a la legislación vigente.

### CUARTA. Forma de pago

Mediante transferencia electrónica SPEI a la cuenta señalada por el Prestador, en moneda mexicana o moneda extranjera según se pacte, contra emisión del CFDI correspondiente.

### QUINTA. Plazo

El presente contrato tiene vigencia indefinida hasta que cualquiera de las partes lo dé por terminado con aviso previo de 30 días naturales. Los servicios en curso al momento del aviso se concluyen conforme a las cotizaciones aceptadas.

### SEXTA. Propiedad intelectual

Los entregables son propiedad del Cliente al pago final de cada cotización. El Prestador conserva derechos sobre metodologías, frameworks, herramientas propias y componentes reutilizables no específicos al Cliente.

El Prestador podrá usar los proyectos como caso referencia con autorización previa del Cliente.

### SÉPTIMA. Confidencialidad

Ambas partes mantienen confidencial la información intercambiada por 3 años posteriores a la terminación del contrato. Excepciones: información ya pública, requerida por autoridad, o con autorización por escrito.

### OCTAVA. Protección de datos personales

Las partes tratarán los datos personales conforme a la LFPDPPP. El aviso de privacidad del Prestador está disponible en [URL/anexo]. El Cliente declara haberlo conocido y aceptado.

### NOVENA. No-solicitud de personal

Durante la vigencia del contrato y los 12 meses posteriores, el Cliente se compromete a no contratar directamente personal del Prestador sin compensación previa acordada.

### DÉCIMA. Limitación de responsabilidad

La responsabilidad del Prestador por cualquier reclamación, en agregado, se limita al monto pagado por el Cliente bajo la cotización específica que dio origen a la reclamación.

### DÉCIMA PRIMERA. Cancelación

Cualquiera de las partes puede dar por terminado este contrato con aviso de 30 días. Los servicios en curso se liquidan conforme a las cotizaciones; el anticipo aplicado no es reembolsable salvo causa imputable al Prestador.

### DÉCIMA SEGUNDA. Jurisdicción

Para la interpretación y cumplimiento de este contrato, las partes se someten a los tribunales competentes de la Ciudad de México, renunciando a cualquier otro fuero.

---

Leído y de acuerdo, las partes firman este contrato en dos tantos.

**Por el Prestador**
[Nombre]
[Firma]

**Por el Cliente**
[Nombre y cargo del representante]
[Firma]
[Sello de la empresa, si aplica]
```

## Datos críticos vs opcionales

**Críticos** (sin estos no puede facturarse):
- Razón social, RFC, régimen, CP, uso CFDI preferido
- Email para envío de CFDI
- Esquema de pago básico

**Opcionales** (pueden completarse después):
- Constancia de situación fiscal (útil tenerla)
- Datos de operativo si solo hay un contacto
- Detalles de la industria/tamaño (vienen con la conversación)

## Validaciones en captura

Mientras se captura, el skill aplica:
- RFC con `rfc-validacion` (estructura).
- CP con `cfdi-emision` (existencia en catálogo).
- Régimen consistente con tipo PF/PM.
- Uso CFDI compatible con régimen del receptor.

Si algo falla: avisar suavemente y pedir corrección antes de cerrar la ficha.

## Almacenamiento sugerido

```
clientes/
  [id-cliente]/
    ficha.json
    contrato-marco-firmado.pdf
    aviso-privacidad-aceptado.pdf
    constancia-situacion-fiscal.pdf (opcional)
    notas/
      [fecha]-[asunto].md
```

## Salida esperada

1. Ficha JSON guardada en `clientes/[id-cliente]/ficha.json`.
2. Contrato marco pre-llenado en `clientes/[id-cliente]/contrato-marco.md` listo para firmar.
3. Aviso de privacidad para enviarle al cliente.
4. Mensaje breve para enviar al cliente: "Hola [Nombre], registré tus datos. Te dejo [aquí el contrato/aviso] para firmar. Cuando esté de regreso seguimos."

## Integración con otros skills

- `rfc-validacion` para validar RFC.
- `cfdi-emision` para validar CP y régimen.
- `compliance-lfpdppp` para generar aviso de privacidad.
- `cotizacion-mxn` o `propuesta-comercial` como siguiente paso típico después de onboarding.
- `cobranza-seguimiento` consume la ficha para datos de contacto al momento de cobrar.
