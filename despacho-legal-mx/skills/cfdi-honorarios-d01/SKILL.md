---
name: cfdi-honorarios-d01
description: Emite CFDI 4.0 tipo Ingreso por honorarios profesionales legales. UsoCFDI G03 cuando el cliente es empresa o PF con actividad que lo deduce, S01 si el cliente PF no lo deduce; D01 NO aplica a servicios legales (es para honorarios médicos). ClaveProdServ según materia (familia 801215-801219 del catálogo SAT), IVA 16% trasladado, retenciones cuando el receptor es persona moral (PF 612: 10% ISR + 2/3 del IVA; PF RESICO 626: 1.25% ISR + 2/3 del IVA), MetodoPago PUE si se cobró al emitir o PPD si se cobra después (con complemento de pagos), y FormaPago coherente con el medio (03 SPEI, 04 TDC, 01 efectivo, 99 si es PPD). Diferencia iguala mensual vs honorarios por etapa. Usar cuando el usuario diga "factura abogado", "CFDI honorarios legales", "facturar iguala", "facturar honorarios despacho", "factura por servicios legales", "retenciones honorarios abogado". NO usar para CFDI de retenciones del despacho hacia subagentes ni para el CFDI tipo P (REP).
allowed-tools: Read, Write, Edit
---

# CFDI de honorarios legales

> El nombre del skill conserva "d01" por compatibilidad; los servicios legales NO usan D01.

## Configuración

- **TipoDeComprobante**: I (Ingreso)
- **UsoCFDI**: G03 (gastos en general) si el receptor lo deduce; S01 (sin efectos fiscales) si es PF sin actividad. D01 es solo para honorarios médicos, dentales y hospitalarios.
- **ClaveProdServ** (catálogo c_ClaveProdServ), elige por materia:
  - `80121704` contratos · `80121603` derecho societario · `80121607` derecho tributario
  - `80121706` derecho laboral · `80121503` defensa penal · `80121502` apelación
  - `80121801` divorcio · `80121804` custodia · `80121803` migratorio
  - `80121610` cobro de cartera · `80121604` propiedad intelectual · `80121606` inmobiliario
  - No uses `80101502` (es asesoría sobre fusiones de empresas, no servicios legales).
- **ClaveUnidad**: `E48` (unidad de servicio)
- **ObjetoImp**: `02` (sí objeto de impuesto), IVA 16% trasladado.

## Retenciones por escenario

Fuente: Art. 106 último párrafo y Art. 113-J LISR; Art. 1-A fr. II inciso a) LIVA y Art. 3 fr. I RLIVA. Debe coincidir con `iva-retenciones-mx`.

| Receptor | Emisor | Retiene ISR | Retiene IVA |
|---|---|---|---|
| Persona moral | PF régimen 612 | 10% | 10.6667% (2/3 del IVA) |
| Persona moral | PF RESICO 626 | 1.25% | 10.6667% (2/3 del IVA) |
| Persona física | cualquiera | 0 | 0 |
| cualquiera | Despacho persona moral (601) | 0 | 0 |

### Ejemplo (honorarios $10,000.00 a una PM)

| Concepto | Emisor 612 | Emisor 626 |
|---|---|---|
| Subtotal | 10,000.00 | 10,000.00 |
| IVA trasladado 16% | 1,600.00 | 1,600.00 |
| ISR retenido | −1,000.00 | −125.00 |
| IVA retenido (2/3) | −1,066.67 | −1,066.67 |
| **Total** | **9,533.33** | **10,408.33** |

## Validación previa al timbrado

1. RFC, nombre y CP del receptor tal como están en su constancia de situación fiscal (ver `rfc-validacion`).
2. Si hay retenciones, que estén en Impuestos.Retenciones del concepto y del comprobante.
3. Total = Subtotal + IVA trasladado − ISR retenido − IVA retenido.
4. MetodoPago/FormaPago: PUE con forma específica (03, 04, 01…); PPD con FormaPago 99 y complemento de pagos al cobrar.
5. Iguala: un CFDI por mes con el periodo en la descripción. Honorarios por etapa: un CFDI por hito, cuando se cobra.

## Output

Payload listo para `facturama_timbrar_cfdi` del MCP `mp_facturama_extendido` (valídalo antes con `facturama_validar_payload_local`). El MCP requiere credenciales; sin ellas, deja el payload en modo mock y avisa al usuario. Registra la emisión en la bitácora del expediente.

> Revisión profesional: confirma el régimen del emisor y del receptor con el contador del despacho antes de timbrar.
