---
name: registro-escrituras-tipos
description: Mantiene registro maestro de escrituras emitidas con folio + tipo + partes + bien + monto. Necesario para protocolo notarial. Incluye registro digital paralelo al físico (libro). Usar cuando el usuario diga registro escrituras, protocolo, folio notarial, libro escrituras.
allowed-tools: Read, Write
---

# Registro escrituras

## Folio notarial

Cada notaría tiene número único (asignado por estado) + folio secuencial.

Formato típico: `Notaría {número} {estado} — Esc. {folio} del libro {año}`

Ej: `Notaría 67 CDMX — Esc. 12,345 del libro 2026`

## Schema

```python
class EscrituraRegistrada(BaseModel):
    folio: int
    libro: int
    fecha_otorgamiento: date
    tipo_acto: str
    partes: list[Parte]
    bien_descripcion: str | None
    valor_operacion_mxn: Decimal | None
    impuestos_pagados: dict[str, Decimal]  # ISABI, IVA, etc.
    honorarios_notario_mxn: Decimal
    estado_registro_publico: Literal["pendiente", "presentado", "inscrito", "rechazado"]
    fecha_inscripcion_rpp: date | None
    folio_real_rpp: str | None
```

## Output

```json
{
  "folio": 12345,
  "libro": 2026,
  "tipo_acto": "compraventa",
  "partes": [
    {"rol": "vendedor", "rfc_hash": "..."},
    {"rol": "comprador", "rfc_hash": "..."}
  ],
  "bien_descripcion": "Inmueble Roma Norte CDMX",
  "valor_operacion_mxn": "5500000.00",
  "isabi_mxn": "165000.00",
  "honorarios_mxn": "48000.00",
  "estado_rpp": "inscrito",
  "folio_real": "12345-CDMX-2026"
}
```
