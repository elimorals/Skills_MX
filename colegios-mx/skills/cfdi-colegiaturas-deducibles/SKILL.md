---
name: cfdi-colegiaturas-deducibles
description: Emite CFDI de colegiaturas con los requisitos para que el padre o tutor aplique el estímulo fiscal por servicios educativos del Decreto DOF 26-12-2013 (arts. 1.8 a 1.10) en preescolar, primaria, secundaria, profesional técnico y bachillerato (NO universidad). Usa ClaveProdServ 86121501/86121503/86121601/86121602 según nivel, UsoCFDI D10, complemento concepto IEDU (iedu:instEducativas), IVA exento (Art. 15 fr. IV LIVA), forma de pago no efectivo (cheque nominativo, transferencia, tarjeta) y advierte los topes anuales por alumno (preescolar $14,200, primaria $12,900, secundaria $19,900, profesional técnico $17,100, bachillerato $24,500). Separa conceptos no deducibles (inscripción, reinscripción, cuotas, materiales). Usar cuando el usuario diga facturar colegiatura, CFDI colegio, factura escuela, deducible D10, comprobante deducible educación, complemento IEDU, school tuition CFDI. NO usar para extracurriculares de paga ni para universidad (no deducible).
allowed-tools: Read, Write, Edit
---

# CFDI de colegiaturas — deducibilidad correcta

Si el CFDI sale mal, el padre no puede deducir y el colegio queda mal con la familia.

## Fundamento

- **Decreto que compila diversos beneficios fiscales**, DOF 26-12-2013, arts. 1.8 a 1.10 (retoma el estímulo del decreto de 15-02-2011). No es una fracción del Art. 151 LISR.
- **Transporte escolar** es otra deducción: Art. 151 fr. VII LISR, solo si es obligatorio. Va en concepto separado.
- **IVA**: enseñanza de particulares con autorización o RVOE está exenta (Art. 15 fr. IV LIVA).

## Qué es deducible

- Colegiaturas de preescolar, primaria, secundaria, profesional técnico y bachillerato o equivalente, en escuelas privadas con autorización o RVOE.
- Beneficiarios: el propio contribuyente, cónyuge o concubino(a), y ascendientes o descendientes en línea recta, siempre que el beneficiario no tenga ingresos iguales o mayores a 1 UMA anual (2026: $117.31 × 365 = $42,818.15).

**No deducible**: universidad y posgrado; inscripción y reinscripción; cuotas distintas a la enseñanza (materiales, uniformes, exámenes, cursos extra) aunque se cobren junto con la colegiatura. Si van en el mismo CFDI, deben ir en conceptos separados y sin complemento IEDU.

## Topes anuales por alumno

| Nivel | Tope anual |
|---|---|
| Preescolar | $14,200 |
| Primaria | $12,900 |
| Secundaria | $19,900 |
| Profesional técnico | $17,100 |
| Bachillerato o su equivalente | $24,500 |

Sin cambios desde 2011 (confirmado como vigentes para la declaración de 2026 por Expansión, 12-03-2026; fuente secundaria, confianza media). Según fuentes secundarias, este estímulo no cuenta dentro del límite global de deducciones personales del Art. 151 LISR (verificar). El colegio puede facturar cualquier monto; el padre solo deduce hasta el tope.

## Estructura del CFDI

```
TipoDeComprobante: I
Emisor:
  Rfc, Nombre: del colegio
  RegimenFiscal: 603 si es AC/SC de enseñanza con RVOE (Título III, Art. 79 fr. X LISR); 601 si es SA/SC lucrativa; 626 si es RESICO
  LugarExpedicion: CP del colegio
Receptor:
  Rfc, Nombre, DomicilioFiscalReceptor, RegimenFiscalReceptor: del padre/madre/tutor que deduce, tal como en su constancia
  UsoCFDI: D10 (Pagos por servicios educativos (colegiaturas))
Moneda: MXN
MetodoPago: PUE (se emite al cobrar)
FormaPago: 02 cheque nominativo | 03 transferencia | 04 tarjeta de crédito | 28 tarjeta de débito | 29 tarjeta de servicios
  NO: 01 efectivo (no deducible)
Concepto colegiatura:
  ClaveProdServ:
    86121501 Servicios educativos preescolares
    86121503 Escuelas privadas de educación primaria o secundaria (86121502 si es escuela religiosa)
    86121601 Bachillerato o equivalente
    86121602 Profesional técnico
  Descripcion: "Colegiatura marzo 2026 — [alumno] — [grado] [grupo]"
  ClaveUnidad: E48
  Cantidad: 1
  ObjetoImp: 02, con traslado IVA TipoFactor Exento
  ComplementoConcepto: iedu:instEducativas (abajo)
```

Claves verificadas contra el catálogo c_ClaveProdServ (copia pública del catálogo SAT) y Expansión 12-03-2026. Ojo: la tabla de `cfdi-emision/references/catalogos-sat.md` lista 86111600-86111800 para educación básica; en el catálogo esas claves son educación de adultos, idiomas e intercambios. Usa las de aquí.

## Complemento IEDU (complemento concepto)

Sin él, el CFDI no sustenta el estímulo. Va dentro del concepto de la colegiatura, no a nivel comprobante. Esquema oficial: `http://www.sat.gob.mx/sitio_internet/cfd/iedu/iedu.xsd`, versión 1.0.

```xml
<cfdi:ComplementoConcepto>
  <iedu:instEducativas xmlns:iedu="http://www.sat.gob.mx/iedu"
    version="1.0"
    nombreAlumno="Diego Pérez Rodríguez"
    CURP="PERD150301HDFRDGA1"
    nivelEducativo="Primaria"
    autRVOE="09PPR1234A"
    rfcPago="PERA800101ABC"/>
</cfdi:ComplementoConcepto>
```

- `nombreAlumno`: como aparece en el acta de nacimiento.
- `CURP`: del alumno (no del padre).
- `nivelEducativo`: exactamente uno de "Preescolar", "Primaria", "Secundaria", "Profesional técnico", "Bachillerato o su equivalente".
- `autRVOE`: clave del centro de trabajo (CCT) o número de RVOE de la escuela.
- `rfcPago`: opcional; RFC de quien paga cuando es distinto de quien recibe el servicio.

## Validaciones antes de timbrar

1. **Forma de pago**: si el padre pagó en efectivo, avísale que esa colegiatura no será deducible y ofrécele transferencia para las siguientes.
2. **Receptor = quien paga y deduce**. Si pagan ambos padres, un CFDI a cada uno por lo que pagó.
3. **Nombre y CURP del alumno**: `curp_validar_estructura` (MCP `mp_curp_renapo`) valida el formato localmente. La consulta a RENAPO (`curp_consultar_renapo`) suele quedar en entrega a humano por captcha: si devuelve `requiere_humano`, pide al padre la constancia CURP de gob.mx/curp.
4. **RVOE vigente** para el nivel facturado.
5. **Concepto descriptivo**: mes, alumno y grado. Un CFDI por alumno.
6. **Conceptos no deducibles** separados del de colegiatura.

## Constancia anual de pagos (opcional)

No es requisito legal para deducir: el CFDI con complemento basta. Muchos colegios la entregan como resumen para el padre:

```markdown
# CONSTANCIA DE PAGOS DE COLEGIATURAS — Ejercicio [Año]
[Membrete del colegio]
Se hace constar que el C. [Nombre], RFC [RFC], pagó colegiaturas del alumno [Nombre], CURP [CURP], inscrito en [grado] de [nivel]:

| Mes | Folio fiscal (UUID) | Monto |
|---|---|---|
| Enero | abc-1234-... | $X,XXX |

Total pagado en el ejercicio: $XX,XXX MXN
Documento informativo; el comprobante fiscal es cada CFDI.
[Director] · [Razón social] · RVOE [número y fecha] · CCT [CCT] · [Fecha] · [Sello]
```

## Casos edge

- **Padres divorciados**: CFDI a cada uno por lo que efectivamente pagó, o todo a uno según su acuerdo.
- **Beca parcial**: se factura solo lo cobrado.
- **Pagan los abuelos**: pueden deducir como ascendientes si pagan y el CFDI va a su RFC (el alumno es su descendiente en línea recta).
- **Pago atrasado de varios meses**: un CFDI al cobrar, con un concepto por mes (o un CFDI por mes) para que el detalle cuadre.
- **Cambio de colegio**: cada colegio factura lo que cobró; el padre deduce hasta un solo tope por alumno y nivel.

## Salida esperada

1. Lee datos del alumno y padre desde `clientes/[familia]/ficha.json`.
2. Valida RFC del receptor con `rfc-validacion`.
3. Confirma exención de IVA con `iva-retenciones-mx`.
4. Arma el payload con `cfdi-emision` + complemento IEDU y valida con `facturama_validar_payload_local`.
5. Timbra con `facturama_timbrar_cfdi` (MCP `mp_facturama_extendido`; requiere credenciales, sin ellas queda en mock) y guarda XML + PDF.
6. Alerta si la forma de pago es efectivo o si el acumulado anual ya pasó el tope.
7. Al cierre del ejercicio, ofrece la constancia anual opcional.

## Integración

- `complemento-inseduc-cfdi-d10`: detalle del complemento.
- `validador-requisitos-deducibilidad-colegiaturas`: revisión de CFDI emitidos.
- `cobranza-colegiaturas`: el CFDI se emite contra cobro efectivo.
- `comunicacion-padres-wa`: aviso de CFDI listo.

> Revisión profesional: valida el flujo con el contador del colegio y prueba un timbrado en sandbox del PAC antes de producción.
