---
name: complemento-inseduc-cfdi-d10
description: Construye el complemento concepto IEDU de Instituciones Educativas Privadas (nodo iedu:instEducativas, versión 1.0) requerido en el CFDI con UsoCFDI D10 para que el padre aplique el estímulo por colegiaturas del Decreto DOF 26-12-2013 (arts. 1.8 a 1.10). Incluye los atributos del XSD del SAT: nombreAlumno, CURP del alumno, nivelEducativo (Preescolar, Primaria, Secundaria, Profesional técnico, Bachillerato o su equivalente), autRVOE (CCT o RVOE) y rfcPago opcional. Detecta errores que impiden deducir: pago en efectivo, CFDI a nombre del alumno, complemento ausente o a nivel comprobante, inscripción facturada con complemento, beneficiario con ingresos ≥ 1 UMA anual, escuela sin RVOE. Genera payload para facturama_timbrar_cfdi. Usar cuando el usuario diga "CFDI colegiatura", "factura colegio deducible", "complemento IEDU", "InsEduc", "complemento educativo", "factura escuela padre deduce". NO usar para inscripción ni para universidad.
allowed-tools: Read, Write, Edit
---

# Complemento IEDU para CFDI D10

Esquema oficial: namespace `http://www.sat.gob.mx/iedu`, XSD `http://www.sat.gob.mx/sitio_internet/cfd/iedu/iedu.xsd`. Es **complemento concepto**: va en `Concepto/ComplementoConcepto` del concepto de colegiatura.

## Estructura

```xml
<cfdi:Concepto ClaveProdServ="86121503" Cantidad="1" ClaveUnidad="E48"
    Descripcion="Colegiatura primaria — febrero 2026 — Sofía Pérez Hernández 3o A"
    ValorUnitario="1075.00" Importe="1075.00" ObjetoImp="02">
  <cfdi:Impuestos><cfdi:Traslados>
    <cfdi:Traslado Base="1075.00" Impuesto="002" TipoFactor="Exento"/>
  </cfdi:Traslados></cfdi:Impuestos>
  <cfdi:ComplementoConcepto>
    <iedu:instEducativas xmlns:iedu="http://www.sat.gob.mx/iedu"
        version="1.0"
        nombreAlumno="Sofía Pérez Hernández"
        CURP="PEHS150301MDFRRFA2"
        nivelEducativo="Primaria"
        autRVOE="09PPR1234A"/>
  </cfdi:ComplementoConcepto>
</cfdi:Concepto>
```

| Atributo | Uso | Regla |
|---|---|---|
| `version` | requerido | fijo "1.0" |
| `nombreAlumno` | requerido | como en el acta |
| `CURP` | requerido | del alumno |
| `nivelEducativo` | requerido | enumeración exacta (ver abajo) |
| `autRVOE` | requerido | CCT o número de RVOE de la escuela |
| `rfcPago` | opcional | RFC de quien paga, solo si es distinto de quien recibe el servicio |

## Niveles y topes anuales por alumno (Decreto DOF 26-12-2013)

| nivelEducativo (valor exacto) | Tope anual | ClaveProdServ |
|---|---|---|
| Preescolar | $14,200 | 86121501 |
| Primaria | $12,900 | 86121503 (86121502 religiosa) |
| Secundaria | $19,900 | 86121503 (86121502 religiosa) |
| Profesional técnico | $17,100 | 86121602 |
| Bachillerato o su equivalente | $24,500 | 86121601 |
| Universidad / posgrado | No aplica | — |

El bachillerato tecnológico entra como "Bachillerato o su equivalente". Topes sin cambio desde 2011 (fuente secundaria: Expansión 12-03-2026; verificar si se publica un nuevo decreto).

## Validaciones antes de timbrar

1. `nombreAlumno` completo (apellidos y nombres).
2. `CURP` de 18 caracteres: `curp_validar_estructura` (MCP `mp_curp_renapo`). La consulta a RENAPO queda en entrega a humano por captcha; si el tool devuelve `requiere_humano`, pide la constancia CURP al padre.
3. `nivelEducativo` con el texto exacto del XSD (acentos y mayúsculas incluidos).
4. `autRVOE` no vacío.
5. Receptor: RFC del padre/tutor (NO del alumno).
6. UsoCFDI D10.
7. FormaPago 02, 03, 04, 28 o 29. NO 01 efectivo. Evita 05 monedero: el decreto solo menciona cheque nominativo, transferencia y tarjetas.
8. El importe puede exceder el tope: el tope limita la deducción anual del padre, no el CFDI. Avisa si el acumulado anual lo rebasa.

## Casos edge

- **Varios hijos**: un concepto (o CFDI) por alumno, cada uno con su complemento; cada alumno tiene su propio tope.
- **Padres divorciados**: deduce quien paga; si ambos pagan, un CFDI a cada uno por su parte.
- **Pago en parcialidades o adelantado**: se emite CFDI al cobrar (PUE). No acumules un CFDI anual al cierre del ciclo: el CFDI debe emitirse cuando se recibe el pago.
- **Alumno mayor de edad**: el padre deduce si el alumno no tiene ingresos iguales o mayores a 1 UMA anual ($42,818.15 en 2026). Advierte, pero permite emitir.
- **Inscripción y reinscripción**: no deducibles; facturar en concepto aparte sin complemento.

## Output

```yaml
payload_facturama:
  TipoDeComprobante: I
  UsoCFDI: D10
  FormaPago: "03"
  MetodoPago: PUE
  Receptor:
    Rfc: PERA850115ABC
    Nombre: ALBERTO PEREZ RAMIREZ
    DomicilioFiscalReceptor: "06700"
    RegimenFiscalReceptor: "605"
  Conceptos:
    - ClaveProdServ: "86121503"
      Cantidad: 1
      ClaveUnidad: E48
      Descripcion: "Colegiatura primaria — febrero 2026 — Sofía Pérez Hernández 3o A"
      ValorUnitario: 1075.00
      Importe: 1075.00
      ObjetoImp: "02"
      Traslado: {Impuesto: "002", TipoFactor: "Exento"}
      ComplementoConcepto:
        iedu:
          version: "1.0"
          nombreAlumno: "Sofía Pérez Hernández"
          CURP: "PEHS150301MDFRRFA2"
          nivelEducativo: "Primaria"
          autRVOE: "09PPR1234A"
```

Valida con `facturama_validar_payload_local` y timbra con `facturama_timbrar_cfdi` (MCP `mp_facturama_extendido`, requiere credenciales; sin ellas, modo mock). Confirma con el PAC cómo recibe el complemento concepto IEDU en su API.

> Si el SAT publica una versión nueva del XSD, actualiza esta skill.
