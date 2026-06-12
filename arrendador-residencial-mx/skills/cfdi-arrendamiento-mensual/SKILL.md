---
name: cfdi-arrendamiento-mensual
description: Emite el CFDI mensual de arrendamiento residencial para personas físicas. Tipo I (Ingreso), uso D04 (casa habitación) si el inquilino es PF que renta para vivir, o G03 (gastos en general) si es PM que renta habitación de oficina (caso raro residencial). Régimen del emisor: 612 (PFAE arrendamiento) o 626 (RESICO PF). Incluye retenciones de ISR aplicables (10% si pagador es PM, 0% si PF). Genera CFDI en Facturama con timbrado real o mock según credenciales. Usar cuando el usuario diga emite CFDI renta, facturar mes, CFDI arrendamiento, factura inquilino. NO usar para CFDI de comisión inmobiliaria (eso es inmobiliaria-mx).
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
    "regimen_fiscal_receptor": "612",  // o "601" si PM
    "uso_cfdi": "D04",  // o "G03" en raros casos
    "tipo_persona": "PF"  // o "PM"
  },
  "arrendador": {
    "rfc": "...",
    "regimen_fiscal": "612",  // o "626"
    "lugar_expedicion_cp": "06700"
  },
  "monto_renta_mxn": "12000.00",
  "incluir_iva": false  // casa habitación residencial = EXENTO IVA
}
```

## Casos por régimen

### Caso A — Arrendador PF en 612 (PFAE arrendamiento) renta a PF (612 o sin RFC)

- **IVA**: 0% (exento — casa habitación)
- **ISR retenido por inquilino**: 0% (PF no retiene a PF)
- **CFDI**:
  ```
  Tipo: I (Ingreso)
  Uso CFDI: D04 (casa habitación)
  Subtotal: $12,000.00
  IVA: $0 (exento)
  Total: $12,000.00
  Régimen emisor: 612
  ```

### Caso B — Arrendador PF en 612 renta a PM (601, 603, 626 PM)

- **IVA**: 0% (exento — casa habitación)
- **ISR retenido por PM**: **10% del subtotal** (Art. 145 LISR)
- **CFDI**:
  ```
  Tipo: I (Ingreso)
  Uso CFDI: G03 si para uso oficina (raro residencial), D04 si casa habitación
  Subtotal: $12,000.00
  IVA: $0
  Retención ISR: $1,200.00 (10%)
  Total a recibir: $10,800.00
  Régimen emisor: 612
  ```

### Caso C — Arrendador en RESICO PF (626) renta a PF

- **IVA**: 0% (exento)
- **ISR retenido**: 0% (RESICO no retiene en CFDI)
- **CFDI**:
  ```
  Tipo: I (Ingreso)
  Uso CFDI: D04
  Subtotal: $12,000.00
  IVA: $0
  Total: $12,000.00
  Régimen emisor: 626
  ```

### Caso D — Arrendador en RESICO PF (626) renta a PM

- **IVA**: 0% (exento)
- **ISR retenido por PM**: **1.25% del subtotal** (RESICO retiene menos)
- **CFDI**:
  ```
  Tipo: I (Ingreso)
  Uso CFDI: G03 / D04
  Subtotal: $12,000.00
  IVA: $0
  Retención ISR: $150.00 (1.25%)
  Total a recibir: $11,850.00
  Régimen emisor: 626
  ```

## Forma + método de pago

- **Forma pago**: 03 (Transferencia electrónica) si SPEI, 01 (efectivo) si efectivo en domicilio, etc.
- **Método pago**: PUE (Pago en una sola exhibición) — para arrendamiento típico mes a mes

⚠ NO usar PPD (Pago en parcialidades o diferido) salvo casos especiales. Si PPD, hay que emitir REP (Recibo Electrónico de Pago) al cobrar.

## Flujo

### Paso 1 — Validar inquilino
- Si `RFC == "XAXX010101000"` (público en general): permitido pero el inquilino no podrá deducir
- Validar RFC en padrón (`mp_sat_portal.consultar_padron`)
- Validar 69-B (excluir si en lista definitiva)

### Paso 2 — Calcular montos
- Aplicar tabla por régimen (caso A/B/C/D arriba)

### Paso 3 — Construir payload Facturama
- Use `mp_facturama_extendido.construir_payload_cfdi`
- Validar con `mp_facturama_extendido.validar_payload`

### Paso 4 — Timbrar
- `mp_facturama_extendido.timbrar_cfdi`
- Si exitoso: obtener UUID, XML, PDF

### Paso 5 — Persistir + notificar inquilino
- Guardar UUID en tracker de pagos
- Enviar XML+PDF al inquilino vía email
- Opcional: WhatsApp con "Tu CFDI del mes [mes] está listo"

## Output

```json
{
  "operation": "cfdi_arrendamiento_mensual",
  "uuid": "...",
  "xml_path": "...",
  "pdf_path": "...",
  "monto_facturado_mxn": "12000.00",
  "iva_mxn": "0.00",
  "retencion_isr_mxn": "0.00",
  "monto_a_recibir_mxn": "12000.00",
  "caso_aplicado": "A",
  "regimen_emisor": "612",
  "uso_cfdi": "D04",
  "fecha_emision": "2026-06-06",
  "inquilino_rfc_hash": "...",
  "propiedad_id": "RN-1A",
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Inquilino sin RFC | Usar XAXX010101000 (público en general) + uso `S01` |
| Cobro tardío (mes Y facturado en mes Y+1) | Mantener fecha del mes Y como `Fecha CFDI` |
| Renta en USD | Convertir a MXN con TC Banxico del día + cláusula |
| Múltiples inquilinos misma propiedad | Un CFDI por persona, prorrateado |
| Pago parcial | Si PPD: emitir REP en cada pago. Si PUE pero parcial: emitir CFDI por monto real cobrado |
| Cancelación inquilino mid-mes | CFDI por días pro-rata + cláusula de penalización |

## Dependencias

- `mp_facturama_extendido` (timbrado real o mock)
- `mp_sat_portal` (validación RFC inquilino)
- Tracker de propiedades + pagos

## ⚠ Compliance

- Hashear RFC del inquilino en logs
- XML+PDF guardados en `~/.local/share/plugins-mx/cfdis/<rfc_emisor_hash>/<año>/<mes>/`
- Backup automático vía hook `backup-cfdi-automatico.sh`
