---
name: registro-escrituras-tipos
description: Mantiene el registro maestro de escrituras de la notaría (número de escritura, volumen/libro, tipo de acto, partes, bien, monto) en paralelo al protocolo físico, con los impuestos que el notario calcula y entera (ISAI/ISABI, ISR por enajenación Art. 126 LISR, pago estatal Art. 127, exención de casa habitación Art. 93 fr. XIX) y el estado de los avisos antilavado (LFPIORPI). Usar cuando el usuario diga registro escrituras, protocolo, folio notarial, libro escrituras, control de escrituras, ISR enajenación notario.
allowed-tools: Read, Write
---

# Registro de escrituras

## Numeración

Cada notaría tiene un número asignado por la entidad; las escrituras llevan número consecutivo y se asientan en volúmenes/libros del protocolo según la ley del notariado local (CDMX: protocolo abierto en folios).

Formato de referencia: `Notaría {número} {entidad} — Esc. {número} Vol. {volumen}`

## Schema

```python
class EscrituraRegistrada(BaseModel):
    numero_escritura: int
    volumen: int
    fecha_otorgamiento: date
    tipo_acto: str
    partes: list[Parte]
    bien_descripcion: str | None
    valor_operacion_mxn: Decimal | None
    impuestos: dict[str, Decimal]  # isai, isr_enajenacion_126, isr_estatal_127, iva
    exencion_casa_habitacion_93_xix: bool | None
    honorarios_notario_mxn: Decimal
    aviso_lfpiorpi: Literal["no_aplica", "pendiente", "presentado"]
    estado_registro_publico: Literal["pendiente", "presentado", "inscrito", "rechazado"]
    fecha_inscripcion_rpp: date | None
    folio_real_rpp: str | None
```

## Obligaciones fiscales del notario en enajenación de inmuebles

| Obligación | Base legal | Qué hace el notario |
|---|---|---|
| Pago provisional de ISR del vendedor PF | Art. 126 LISR | Lo calcula y lo entera dentro de los 15 días siguientes a la firma de la escritura; entrega comprobante al enajenante |
| Pago a la entidad federativa | Art. 127 LISR | 5% sobre la ganancia; acreditable contra el pago provisional federal; mismo plazo |
| Exención de casa habitación | Art. 93 fr. XIX a) LISR | Exento hasta 700,000 UDIs del ingreso si el vendedor no exentó otra casa habitación en los 3 años previos; el notario verifica con el SAT y grava el excedente. Valor UDI del día: Banxico (SIE) |
| Declaración informativa | DeclaraNOT (SAT) | Informar la operación y el pago (verificar plazos en RMF 2026) |
| Antilavado | LFPIORPI Art. 17 | Identificar siempre a las partes y al beneficiario controlador; aviso a la UIF por el portal del SAT cuando se alcance el umbral (reforma DOF 16-07-2025: **verificar** umbral vigente; fuentes secundarias no coinciden) |
| Efectivo | LFPIORPI Art. 32 fr. I | No se puede pagar en efectivo la transmisión de inmuebles de 8,025 UMA o más ($941,412.75 con UMA 2026) |

## Output

```json
{
  "numero_escritura": 12345,
  "volumen": 410,
  "tipo_acto": "compraventa",
  "partes": [
    {"rol": "vendedor", "rfc_hash": "..."},
    {"rol": "comprador", "rfc_hash": "..."}
  ],
  "bien_descripcion": "Inmueble Roma Norte CDMX",
  "valor_operacion_mxn": "5500000.00",
  "impuestos": {
    "isai_mxn": "calcular con calculo-isabi-por-estado (tarifa CDMX vigente)",
    "isr_enajenacion_126_mxn": "0.00",
    "isr_estatal_127_mxn": "0.00"
  },
  "exencion_casa_habitacion_93_xix": true,
  "honorarios_mxn": "57500.00",
  "iva_honorarios_mxn": "9200.00",
  "aviso_lfpiorpi": "pendiente",
  "estado_rpp": "inscrito",
  "folio_real": "12345-CDMX-2026"
}
```

En el ejemplo el vendedor acredita la exención total: $5,500,000 / 700,000 = 7.857, así que el ingreso queda exento mientras la UDI del día de la escritura valga más de 7.857 (la UDI supera ese nivel desde 2023; confirma el valor exacto en Banxico SIE). Si no aplicara, se calcula el ISR con el procedimiento del Art. 126.

## ⚠ Compliance

Validar cálculos de ISR, exenciones y avisos con el notario titular; las cifras y umbrales cambian por reforma y RMF.
