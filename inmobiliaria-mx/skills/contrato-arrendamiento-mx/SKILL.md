---
name: contrato-arrendamiento-mx
description: Contrato de arrendamiento residencial o comercial conforme Código Civil Federal (Art. 2398-2496) y Código Civil CDMX (Art. 2398-2496) actualizado 2024 — fiador solidario o depósito mensual, vigencia mínima 1 año (residencial), aumentos anuales por inflación INPC, cláusulas anti-uso comercial en residencial, registro ante el RPP o no, gastos de mantenimiento, derecho de tanto. Personas físicas o morales (con o sin IVA). Usar cuando el usuario diga contrato renta, contrato arrendamiento, vamos a rentar, fiador, depósito, vigencia, aumento renta. NO usar para venta (otro skill comisiones-corredor) ni screening (otro skill).
allowed-tools: Read, Write, Edit
---

# Contrato de arrendamiento — MX

⚠ **Validar con abogado especializado en arrendamiento** antes de uso real.

## Marco legal

| Caso | Ley aplicable | Donde se rige |
|---|---|---|
| Residencial CDMX | Código Civil CDMX (Art. 2398-2496) | CDMX |
| Comercial CDMX | Código Civil CDMX + LGSC | CDMX |
| Residencial otros estados | Código Civil del Estado | Estado correspondiente |
| Comercial otros estados | Código Civil + Código de Comercio | Estado correspondiente |

## Estructura típica

### Modalidades
- **Residencial**: para vivienda (CCF/CCDF Art. 2398)
- **Comercial**: para giro mercantil (LGSC + Código Comercio)
- **Industrial**: para nave o fábrica
- **Mixto**: residencial + comercial (más complejo)

### Vigencia
- Mínimo residencial: **1 año** (CCDF Art. 2398). No se puede menos.
- Comercial: libre, típico 3-5 años.
- Renovaciones automáticas a menos que se notifique 30 días antes.

### Garantía
2 opciones (no ambas):

**A. Depósito mensual** (1-2 meses):
- Cantidad equivalente a 1-2 meses de renta
- Reembolsable al final si no hay daños/adeudos
- No produce intereses para el arrendatario

**B. Fiador solidario**:
- Tercero (familiar, amigo) responde solidariamente
- Debe acreditar capacidad económica
- Carta firmada ante notario o testigos

### Aumento anual
- Indexado al INPC del año anterior (típico)
- Aumento máximo legal: limitado por entidad (CDMX permite hasta 10% si no se vincula a INPC)
- Renta sube en aniversario del contrato

## Estructura del contrato

```markdown
CONTRATO DE ARRENDAMIENTO {{residencial/comercial}}

ENTRE:
EL ARRENDADOR: {{nombre_arrendador}}, con RFC {{rfc_arrendador}},
  con domicilio en {{domicilio_arrendador}}.

EL ARRENDATARIO: {{nombre_arrendatario}}, con RFC {{rfc_arrendatario}},
  con domicilio en {{domicilio_arrendatario}}.

{{si aplica fiador:}}
EL FIADOR SOLIDARIO: {{nombre_fiador}}, con RFC {{rfc_fiador}}, con
  domicilio en {{domicilio_fiador}}, que se obliga solidariamente.

OBJETO DEL CONTRATO:
{{descripcion_inmueble}} ubicado en {{direccion_completa}}, identificado
con cuenta predial {{cuenta_predial}}, escritura {{numero_escritura}}
del Notario {{numero_notario}}.

CLÁUSULAS:

PRIMERA — RENTA
El ARRENDATARIO pagará la cantidad de ${{renta_mensual}} MXN (más IVA si aplica)
mensuales, pagaderos los primeros 5 días de cada mes.

SEGUNDA — DEPÓSITO / FIANZA
{{si depósito:}}
EL ARRENDATARIO entrega a la firma ${{deposito_mxn}} como depósito en garantía,
equivalente a {{meses}} mes(es) de renta. Reembolsable al término sin daños.

{{si fiador:}}
EL FIADOR SOLIDARIO se obliga solidariamente al cumplimiento de TODAS las
obligaciones del ARRENDATARIO.

TERCERA — VIGENCIA
El contrato inicia el {{fecha_inicio}} y termina el {{fecha_fin}}.
Vigencia: {{meses}} meses.

CUARTA — RENOVACIÓN
Se renueva automáticamente por igual periodo si ninguna parte notifica
por escrito su intención de no renovar con 30 días de anticipación al
vencimiento.

QUINTA — AUMENTO ANUAL
La renta se incrementará anualmente conforme al INPC del año anterior
o {{porcentaje_fijo}}% (lo que sea mayor o lo que se pacte).

SEXTA — USO DEL INMUEBLE
El inmueble se destinará exclusivamente para {{uso_residencial/comercial}}.
{{si residencial:}} NO se permite uso comercial, industrial, ni para fines
contrarios a la moral o las buenas costumbres.

SÉPTIMA — GASTOS
EL ARRENDATARIO se compromete a pagar puntualmente:
- Luz eléctrica
- Agua
- Gas
- Internet / cable (si lo desea)
- Servicio de basura (si aplica)

Quedan a cargo del ARRENDADOR:
- Impuesto predial
- Aseguramiento del inmueble
- Mantenimiento estructural

OCTAVA — MANTENIMIENTO
EL ARRENDATARIO se compromete a:
- Mantener el inmueble en condiciones de habitabilidad
- Notificar inmediatamente cualquier desperfecto mayor
- Realizar reparaciones menores (cambio de focos, pintura interior)
- NO modificar estructura sin consentimiento por escrito

NOVENA — INCUMPLIMIENTO POR ARRENDATARIO
Si el ARRENDATARIO incumple en el pago por más de 1 mes:
- Mora del 6% mensual (Art. 362 CCom adapted)
- EL ARRENDADOR puede rescindir con previo requerimiento por escrito (30 días)
- Si rescinde, el ARRENDATARIO debe devolver el inmueble en 30 días naturales

DÉCIMA — DERECHO DE TANTO
Si el ARRENDADOR decide vender el inmueble, debe ofrecerlo primero al
ARRENDATARIO en igualdad de condiciones (Art. 2447 CCF).

DÉCIMA PRIMERA — REGISTRO
{{si CDMX y vigencia >= 1 año:}}
El presente contrato se inscribirá en el RPP de la CDMX dentro de los
30 días siguientes a su firma para que sea oponible a terceros.

{{si solo para protocolización:}}
El contrato deberá ser ratificado ante notario público.

DÉCIMA SEGUNDA — JURISDICCIÓN
LAS PARTES se someten a los Tribunales Civiles de {{ciudad}}, renunciando
a cualquier otra jurisdicción.

DÉCIMA TERCERA — INVENTARIO
Anexo 1: Inventario del inmueble con fotos del estado inicial. Firmado por
ambas partes.

FIRMAS:

{{Arrendador}}                        {{Arrendatario}}
{{nombre_completo}}                    {{nombre_completo}}
{{firma}}                              {{firma}}
{{rfc}}                                {{rfc}}

{{si aplica:}}
{{Fiador Solidario}}
{{nombre_completo}}
{{firma}}
{{rfc}}

{{ciudad}}, {{fecha_firma}}
```

## CFDI por arrendamiento

### Si arrendador es Persona Física
- Régimen: 612 (Arrendamiento) o 626 (RESICO PF)
- CFDI tipo I por cada pago mensual
- Retención del 10% ISR + 2/3 IVA (Art. 1-A LIVA) si arrendatario es PM

### Si arrendador es Persona Moral
- CFDI tipo I por cada pago mensual
- No hay retenciones (Art. 1-A LIVA)

### IVA arrendamiento
- Residencial: **exento** (Art. 9-XII LIVA)
- Comercial: **16% IVA**
- Frontera norte comercial: **8% IVA**

## Output estructurado

```json
{
  "contrato_arrendamiento_generado": {
    "modalidad": "residencial",
    "ciudad": "CDMX",
    "marco_legal": "CCDF Art. 2398-2496",
    "vigencia_meses": 12,
    "renta_mensual_mxn": 18500,
    "garantia": {
      "tipo": "fiador_solidario",
      "datos_capturados": true
    },
    "iva_aplicable": false,
    "iva_razon": "Residencial exento Art. 9-XII LIVA",
    "registro_rpp_requerido": true,
    "fecha_inicio": "2026-04-01",
    "fecha_fin": "2027-03-31",
    "aumento_anual_referencia": "INPC marzo 2026 publicado por INEGI",
    "clausulas_personalizadas": [],
    "requiere_revisar_abogado_antes_firma": true
  }
}
```

## Validación pendiente

- Revisión por abogado especializado en arrendamiento (CRÍTICO)
- Códigos Civiles vigentes 2026 por estado (CDMX, EdoMex, Jalisco, NL diferentes)
- Casos típicos en disputas (devolución depósito, daños, abandono)
