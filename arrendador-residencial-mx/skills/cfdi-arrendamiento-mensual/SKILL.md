---
name: cfdi-arrendamiento-mensual
description: Emite el CFDI 4.0 mensual de arrendamiento residencial para arrendador persona física. Tipo I (Ingreso); régimen del emisor 606 (Arrendamiento) o 626 (RESICO PF); uso CFDI S01 (sin efectos fiscales) si el inquilino es PF que renta para vivir, G03 si es PM o PF con actividad que lo deduce. IVA exento en casa habitación (Art. 20 fr. II LIVA) salvo inmueble amueblado. Retenciones si el inquilino es PM: ISR 10% (606, Art. 116 LISR) o 1.25% (RESICO, Art. 113-J). Prepara el payload para Facturama (timbrado real solo con credenciales). Usar cuando el usuario diga emite CFDI renta, facturar mes, CFDI arrendamiento, factura inquilino, factura renta. NO usar para CFDI de comisión inmobiliaria (eso es inmobiliaria-mx).
allowed-tools: Read, Write
---

# CFDI mensual arrendamiento residencial

## Inputs requeridos

```json
{
  "propiedad_id": "RN-1A",
  "mes_facturado": "2026-06",
  "fecha_pago_recibido": "2026-06-05",
  "inquilino": {
    "rfc": "PEGJ900101ABC",
    "razon_social": "JUAN PEREZ GARCIA",
    "regimen_fiscal_receptor": "605",
    "uso_cfdi": "S01",
    "tipo_persona": "PF",
    "cp_fiscal": "06700"
  },
  "arrendador": {
    "rfc": "...",
    "regimen_fiscal": "606",
    "lugar_expedicion_cp": "06700"
  },
  "monto_renta_mxn": "12000.00",
  "amueblado": false
}
```

`regimen_fiscal_receptor` y `cp_fiscal` deben coincidir con la constancia de situación fiscal del inquilino (CFDI 4.0).

## Casos por régimen (casa habitación sin amueblar → IVA exento, Art. 20 fr. II LIVA)

| Caso | Emisor | Receptor | Uso CFDI | Retención ISR | Total |
|---|---|---|---|---|---|
| A | 606 | PF que vive ahí | S01 | 0 | $12,000.00 |
| B | 606 | PM (renta para un empleado) | G03 | 10% = $1,200.00 (Art. 116 LISR) | $10,800.00 |
| C | 626 RESICO | PF | S01 | 0 | $12,000.00 |
| D | 626 RESICO | PM | G03 | 1.25% = $150.00 (Art. 113-J LISR) | $11,850.00 |

En CFDI 4.0 el Total ya resta las retenciones. El IVA exento se reporta con `ObjetoImp = 02` y `TipoFactor = Exento` en el traslado.

### Inmueble amueblado

Si se renta amueblado, **todo** el arrendamiento causa IVA 16% (Art. 20 fr. II LIVA excluye los inmuebles amueblados de la exención). Si además el inquilino es PM, retiene 2/3 del IVA (10.6667% del subtotal, Art. 1-A fr. II a) LIVA) y el ISR que corresponda. Ejemplo 606 → PM, $12,000: IVA $1,920; ret. ISR $1,200; ret. IVA $1,280; Total $11,440.

## Forma y método de pago

- **Método PUE** si el CFDI se emite cuando el pago ya se recibió (o se recibirá en el mismo mes). **PPD** si se emite antes de cobrar o el pago llega en otro mes; en PPD hay que emitir complemento de pagos (REP) al cobrar, y el complemento siempre requiere aceptación para cancelarse.
- **Forma de pago**: 03 transferencia, 01 efectivo, etc. Con PPD la forma es 99 (por definir).

## Flujo

### Paso 1 — Validar inquilino
- Pedir su constancia de situación fiscal (nombre, régimen y CP exactos).
- `sat_consultar_padron` y `sat_consultar_69b_efos` (MCP `mp_sat_portal`): la consulta 69-B está validada; la de padrón requiere e.firma y no está validada. Si devuelve error o pide credenciales, usa la constancia.
- Sin RFC: `XAXX010101000`, régimen receptor 616, uso S01, CP = lugar de expedición.

### Paso 2 — Calcular montos
Aplica la tabla de casos. Detalle de retenciones: skill `iva-retenciones-mx` (si está instalado).

### Paso 3 — Validar y timbrar (MCP `mp_facturama_extendido`)
- `facturama_validar_payload_local` — valida el payload sin timbrar.
- `facturama_timbrar_cfdi` — solo con credenciales de Facturama del usuario (estado del MCP: real, sin validar con cuenta sandbox). Sin credenciales: entrega el payload validado y pide al usuario timbrarlo en su PAC.

### Paso 4 — Persistir y notificar
- Guardar UUID en el tracker de pagos.
- Enviar XML + PDF al inquilino por correo (no hay MCP de WhatsApp en el repo; el envío por WhatsApp es manual).

## Output

```json
{
  "operation": "cfdi_arrendamiento_mensual",
  "uuid": "...",
  "monto_facturado_mxn": "12000.00",
  "iva_mxn": "0.00",
  "retencion_isr_mxn": "0.00",
  "total_cfdi_mxn": "12000.00",
  "caso_aplicado": "A",
  "regimen_emisor": "606",
  "uso_cfdi": "S01",
  "metodo_pago": "PUE",
  "fecha_emision": "2026-06-06",
  "inquilino_rfc_hash": "...",
  "propiedad_id": "RN-1A",
  "timbrado_real": false,
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Inquilino sin RFC | `XAXX010101000`, régimen 616, uso `S01` |
| Cobro tardío (renta de junio pagada en julio) | La Fecha del CFDI es la de emisión; no se retrofecha. Indica el periodo en la descripción. Si emitiste en junio sin cobrar, debió ser PPD + REP al cobrar |
| Renta en USD | Moneda USD con TipoCambio DOF del día, o convertir a MXN según contrato |
| Varios inquilinos en el mismo contrato | Un CFDI al titular del contrato (o uno por persona si pagan por separado) |
| Pago parcial | PPD + REP por cada abono |
| Arrendamiento comercial (local, oficina) | IVA 16% y, si paga una PM, retención ISR 10% + IVA 2/3; fuera del alcance residencial de este skill |

## Dependencias

- `mp_facturama_extendido` (timbrado con credenciales del usuario)
- `mp_sat_portal` (69-B; padrón con e.firma)
- Tracker de propiedades y pagos

## ⚠ Compliance

- Hashear el RFC del inquilino en logs.
- XML+PDF en `~/.local/share/plugins-mx/cfdis/<rfc_emisor_hash>/<año>/<mes>/` (respaldo con el hook `scripts/hooks/backup-cfdi-automatico.sh` si está activado).
- Pagos provisionales de ISR (606: mensual o trimestral; RESICO: mensual): ver `gastos-deducibles-propiedad`.
- Valida con tu contador; `vigencia_validada: false`.
