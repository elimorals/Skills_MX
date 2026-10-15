---
name: cfdi-mensualidad-curso
description: Arma el CFDI de la mensualidad o pago de un curso de una academia particular (idiomas, regularización, música, programación, cursos en línea). Decide IVA (16% si no hay RVOE; exento con RVOE, Art. 15 fr. IV LIVA), UsoCFDI (G03 o S01; D10 con complemento IEDU solo para preescolar a bachillerato con RVOE), ClaveProdServ (enseñanza a distancia, idiomas, capacitación) y retenciones cuando se vende a través de plataformas digitales (Arts. 113-A LISR y 18-J LIVA). Pago no efectivo solo importa para colegiaturas deducibles. Usar cuando el usuario diga CFDI mensualidad curso, factura curso en línea, facturar clases, factura academia, IVA curso online, ¿mi curso es deducible?
allowed-tools: Read, Write
---

# CFDI de mensualidad de curso

## 1. Decide el caso

| Curso | IVA | UsoCFDI típico | ¿Deducible para el alumno? |
|---|---|---|---|
| Sin RVOE (idiomas, regularización, talleres, cursos online) | 16% (`ObjetoImp` 02, traslado 0.16) | G03 si lo paga una empresa; S01 si es PF que no lo deduce | No como colegiatura. Para una empresa puede ser gasto (capacitación) |
| Preescolar a bachillerato con RVOE | Exento (Art. 15 fr. IV LIVA) | D10 + complemento IEDU | Sí, con topes: usa la skill `cfdi-colegiaturas-deducibles` del plugin colegios-mx |
| Licenciatura o posgrado con RVOE | Exento | G03 / S01 | No (el estímulo no cubre educación superior) |

Si no hay RVOE, NO uses D10 ni complemento IEDU: el SAT rechazaría la deducción del alumno y el CFDI quedaría mal.

## 2. ClaveProdServ (catálogo c_ClaveProdServ)

- `86111502` Servicios de enseñanza a distancia (cursos en línea)
- `86111700` Educación de idiomas (`86111701` conversación, `86111702` inmersión)
- `86111604` Educación para empleados · `86111601` cursos nocturnos
- `86131601` Escuelas de música · `86131602` baile
- `86132000` Capacitación en administración

Elige la más cercana al curso; si dudas, confirma en el buscador del SAT.

## 3. Venta por plataforma digital

Si el curso se vende a través de una plataforma de intermediación (marketplace de cursos) y el instructor es persona física:
- La plataforma retiene ISR (2.5% en 2026: la LIF 2026 Art. 25 fr. VI, DOF 07-11-2025, sustituye el 1% del Art. 113-A fr. III LISR; 20% si no das tu RFC) y 50% del IVA cobrado (Art. 18-J fr. II inciso b) LIVA); 100% si no das tu RFC.
- La plataforma emite el CFDI de retenciones; tú facturas según sus reglas. Ver `iva-retenciones-mx`.
- Si una plataforma extranjera vende directamente al alumno, ella cobra el IVA de servicios digitales (Art. 18-B fr. IV LIVA, enseñanza a distancia); no es tu CFDI.

## 4. Datos del CFDI

```
TipoDeComprobante: I · Moneda: MXN · MetodoPago: PUE (si ya se cobró)
FormaPago: la real (03 SPEI, 04/28 tarjeta, 01 efectivo…)
Receptor: RFC, nombre, CP y régimen de la constancia del alumno o empresa
  (público en general: XAXX010101000 con reglas de factura global)
Concepto: "Mensualidad curso [nombre] — [mes 2026] — [alumno]"
  ClaveUnidad: E48 · Cantidad: 1
```

Ejemplo sin RVOE: mensualidad $1,500.00 + IVA 16% $240.00 = **$1,740.00**. Si el precio publicado ya incluye IVA ($1,500 IVA incluido): base $1,293.10 + IVA $206.90.

## 5. Timbrado

Payload para `facturama_validar_payload_local` y `facturama_timbrar_cfdi` (MCP `mp_facturama_extendido`). Requiere credenciales; sin ellas, modo mock. Base técnica: `cfdi-emision`; formato de montos: `mxn-formato`.

## Output esperado

```json
{
  "operation": "cfdi-mensualidad-curso",
  "data": {
    "tiene_rvoe": false,
    "iva": "16%",
    "uso_cfdi": "S01",
    "clave_prod_serv": "86111502",
    "subtotal": "1500.00",
    "iva_trasladado": "240.00",
    "total": "1740.00"
  },
  "vigencia_validada": true
}
```

> Revisión profesional: confirma el régimen de la academia y el tratamiento de plataformas con su contador.
