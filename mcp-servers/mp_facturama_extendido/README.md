# mp_facturama_extendido

Wrapper extendido sobre Facturama PAC API con **validación local previa al timbrado** y catálogos SAT incluidos.

## Por qué este wrapper

Facturama tiene un MCP oficial, pero limitado. Este wrapper agrega:

1. **Validación local que atrapa el 95% de errores comunes ANTES de gastar costo PAC**
   - MetodoPago ↔ FormaPago inconsistente (PUE+99, PPD+específico)
   - UsoCFDI incompatible con tipo de persona (D0X solo PF)
   - Totales que no cuadran (subtotal + IVA − retenciones)
   - Fechas fuera de ±72h
   - Falta Exportacion (obligatorio en 4.0)
   - RFC con formato inválido, CP faltante
   - Catálogos SAT (UsoCFDI, FormaPago, Régimen) verificados

2. **Cancelación con validación de motivos 01-04** y folio sustituto cuando aplica

3. **Modo mock plausible** que produce UUIDs y sellos sintéticos válidos sintácticamente — útil para desarrollo sin credenciales

4. **Bitácora estructurada** de cada timbrado/cancelación con RFCs hasheados (no fugas de PII)

5. **Cache de consultas** (estatus, búsquedas) con TTL apropiado

## Setup

### 1. Sandbox gratuito de Facturama

Registra cuenta sandbox en https://www.facturama.mx. Recibes credenciales en email.

### 2. Configurar credenciales

```bash
export FACTURAMA_USER="tu-usuario"
export FACTURAMA_PASSWORD="tu-password"
export FACTURAMA_ENV="sandbox"  # o "production"
```

Alternativa: `FACTURAMA_API_KEY="..."` reemplaza el usuario.

### 3. Probar sin credenciales (modo mock)

Sin `FACTURAMA_USER` el MCP corre en modo mock: UUIDs sintéticos, sello sha256 del payload (determinístico), `simulated: true` en todas las respuestas.

```bash
# Forzar mock incluso con credenciales (testing)
export PLUGINS_MX_MOCK=1
```

## Correr el servidor

```bash
cd mcp-servers
.venv/bin/python -m mp_facturama_extendido.server
```

## Configurar en Claude Code

```json
{
  "mcpServers": {
    "facturama": {
      "command": ".venv/bin/python",
      "args": ["-m", "mp_facturama_extendido.server"],
      "cwd": "/Users/elias/Documents/Trabajo/skills/mcp-servers",
      "env": {
        "FACTURAMA_USER": "${FACTURAMA_USER:-}",
        "FACTURAMA_PASSWORD": "${FACTURAMA_PASSWORD:-}",
        "FACTURAMA_ENV": "${FACTURAMA_ENV:-sandbox}",
        "PLUGINS_MX_MOCK": "${PLUGINS_MX_MOCK:-}"
      },
      "disabled": false
    }
  }
}
```

## Tools disponibles

### `facturama_validar_payload_local`
Valida un payload CFDI 4.0 **sin llamar al PAC**. Devuelve errores + warnings con códigos estables.

```python
{"payload": { ... CFDI 4.0 ... }}
# →
{
  "is_valid": false,
  "errors_count": 2,
  "warnings_count": 1,
  "errors": [
    {"severity": "error", "code": "metodo_forma_inconsistente_pue_99",
     "message": "MétodoPago = PUE no puede llevar FormaPago = 99...",
     "path": "comprobante.forma_pago"}
  ],
  "warnings": [...]
}
```

### `facturama_timbrar_cfdi`
Timbra un CFDI 4.0. Por default ejecuta validación local primero; si falla, NO llama al PAC.

```python
{
  "payload": { ... CFDI completo ... },
  "skip_local_validation": false
}
# Caso éxito →
{
  "ok": true,
  "uuid": "abc...",
  "fecha_timbrado": "...",
  "sello_sat": "...",
  "cadena_original_complemento": "||1.1|...",
  "simulated": true | false,
  "advertencias": [...]
}

# Caso validación local falla →
{
  "ok": false,
  "validacion_local_failed": true,
  "errors": [...],
  "warnings": [...]
}
```

### `facturama_cancelar_cfdi`
Cancela un CFDI con motivo SAT 01-04.

```python
{
  "uuid": "abc12345-6789-4567-89ab-cdef01234567",
  "motivo": "01",
  "folio_sustituto": "def67890-1234-4567-89ab-cdef01234567"  # solo para motivo 01
}
# →
{
  "ok": true,
  "uuid": "...",
  "motivo": "01",
  "estatus": "Solicitud de cancelación enviada",
  "requiere_aceptacion_receptor": true,
  "plazo_respuesta_receptor": "3 días hábiles",
  "simulated": true | false
}
```

**Motivos SAT**:
- `01`: Comprobante con errores con relación → requiere `folio_sustituto`
- `02`: Comprobante con errores sin relación
- `03`: No se llevó a cabo la operación
- `04`: Operación nominativa en factura global

### `facturama_consultar_estatus`
Consulta estatus actual (Vigente / Cancelado / En proceso). Cache 15 min.

```python
{"uuid": "abc..."}
# → {"uuid": "...", "estatus": "Vigente", "consultado_en": "..."}
```

### `facturama_descargar_xml`
Descarga el XML completo del CFDI timbrado.

### `facturama_descargar_pdf`
Descarga la representación impresa PDF (base64).

### `facturama_buscar_cfdis`
Búsqueda con filtros: RFC receptor/emisor, folio, rango fechas, tipo.

```python
{
  "rfc_receptor": "IBM970131DRA",
  "fecha_desde": "2026-03-01",
  "fecha_hasta": "2026-03-31",
  "tipo": "I",
  "limit": 50
}
```

### `facturama_listar_catalogos`
Discovery sin red — devuelve los catálogos SAT que el MCP conoce:
UsoCFDI, FormaPago, MetodoPago, RegimenFiscal, Exportacion, MotivosCancelacion, TipoComprobante.

## Validaciones locales (detalle)

El validador atrapa estos errores **antes** de llamar al PAC:

| Código | Detecta |
|---|---|
| `emisor_rfc_invalido` | RFC del emisor con formato inválido |
| `emisor_cp_invalido` | CP del lugar de expedición no es 5 dígitos |
| `emisor_regimen_invalido` | Régimen fiscal no existe en catálogo |
| `receptor_cp_faltante` | CP del receptor obligatorio en CFDI 4.0 |
| `receptor_regimen_faltante` | Régimen fiscal del receptor obligatorio en 4.0 |
| `uso_cfdi_invalido` | UsoCFDI no existe en catálogo |
| `rfc_generico_requiere_s01` | XAXX010101000 requiere UsoCFDI=S01 |
| `extranjero_falta_residencia_fiscal` | XEXX010101000 requiere ResidenciaFiscal |
| `metodo_forma_inconsistente_pue_99` | PUE+FormaPago99 (el bug clásico) |
| `metodo_forma_inconsistente_ppd_no_99` | PPD requiere FormaPago=99 |
| `exportacion_faltante` | Falta campo Exportacion (obligatorio 4.0) |
| `tipo_cambio_requerido` | Moneda ≠ MXN requiere TipoCambio positivo |
| `fecha_futura` | Fecha en el futuro |
| `fecha_demasiado_antigua` | Fecha > 72h en el pasado |
| `concepto_objeto_imp_faltante` | Falta ObjetoImp por concepto (obligatorio 4.0) |
| `concepto_importe_no_cuadra` | Importe ≠ cantidad × valor_unitario |
| `subtotal_no_cuadra` | Subtotal declarado ≠ suma conceptos |
| `total_no_cuadra` | Total ≠ subtotal + trasladados − retenidos |
| `uso_cfdi_incompatible_persona` | D0X enviado a receptor PM (solo aplica PF) |
| `uso_cfdi_obligatorio_no_cumplido` | Tipo P requiere CP01, Tipo N requiere CN01 |

**Warnings (no bloquean timbrado)**:
- `ppd_requiere_rep_posterior`: recordatorio de emitir REP al cobrar
- `concepto_clave_prod_serv_formato`: ClaveProdServ no es 8 dígitos
- `extranjero_sin_num_reg_id_trib`: extranjero típicamente requiere NumRegIdTrib

## Bitácora

Cada timbrado/cancelación se registra en `~/.local/share/plugins-mx/audit-log/facturama_mcp/YYYY-MM.jsonl`.

**RFCs y UUIDs se hashean** con sha256 truncado a 12 chars antes de loguear, para preservar capacidad de análisis ("¿cuántos timbrados al mismo emisor?") sin filtrar PII.

## ⚠ Datos a verificar vigentes

- **Catálogos SAT** (`catalogos.py`) reflejan Anexo 20 vigente al momento del training. Validar contra https://www.sat.gob.mx antes de producción.
- **Reglas de cancelación SAT**: las versiones de motivos 01-04 son estables desde 2022, pero verificar RMF vigente.
- **Endpoints Facturama**: el cliente usa rutas estables, pero cambios a la API requerirán ajuste.

## Tests

```bash
cd mcp-servers
.venv/bin/python -m pytest mp_facturama_extendido/tests -v
```

Cobertura actual: **88 tests** cubriendo:
- 47 tests del validador (cada regla, RFC genéricos, fechas, totales, UsoCFDI×régimen, cancelación)
- 26 tests del cliente (mock determinístico, bitácora con hashing, cache, modo real sin creds)
- 15 tests end-to-end de los 8 tools del server
