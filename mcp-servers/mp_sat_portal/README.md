# mp_sat_portal — MCP para portal SAT (México)

Herramientas para verificación, descarga y consulta contra los portales del Servicio de Administración Tributaria (SAT) de México.

## Tools (11)

### Públicos — HTTP real con fallback a mock

| Tool | Propósito | Auth |
|---|---|---|
| `sat_consultar_padron` | Status RFC (ACTIVO/SUSPENDIDO/CANCELADO) | Pública (mock) |
| `sat_consultar_69b_efos` | Lista 69-B EFOS (definitivos + presuntos) | Pública (CSV) |
| `sat_consultar_69_incumplidos` | Lista 69 incumplidos Art. 69 CFF | Pública (CSV) |
| `sat_verificar_cfdi_uuid` | Status CFDI contra verificador SAT | Pública (HTML) |

### Local — sin red

| Tool | Propósito |
|---|---|
| `sat_validar_uuid_estructura` | Validar formato UUID CFDI (8-4-4-4-12 hex, v4) |

### Con autenticación — mock por default

Path real requiere Playwright + e.firma (.cer + .key + contraseña). No implementado todavía — siempre retorna `simulated: true`.

| Tool | Propósito | Auth |
|---|---|---|
| `sat_descargar_csf` | Constancia de Situación Fiscal | RFC+CIEC o e.firma |
| `sat_descargar_buzon_tributario` | Notificaciones pendientes | e.firma |
| `sat_descargar_cfdi_masivo` | Solicitud descarga masiva CFDIs | e.firma |
| `sat_agendar_cita` | Buscar disponibilidad de citas | RFC+CIEC |
| `sat_verificar_efirma_vigente` | Status e.firma | e.firma |
| `sat_descargar_acuse` | PDF de acuse | e.firma |

### Escritura — DOBLEMENTE bloqueada

| Tool | Propósito |
|---|---|
| `sat_actualizar_obligaciones` | Cambiar régimen / dar de alta-baja obligaciones |

**Comportamiento de seguridad**: incluso con credenciales reales esta tool retorna `simulated: true`. Para habilitar el path real se necesitan **DOS** flags: credenciales válidas + `PLUGINS_MX_SAT_PERMITIR_ESCRITURA=1`. Aún así el path real está marcado "no implementado" hasta tener doble revisión humana.

### Discovery

| Tool | Propósito |
|---|---|
| `sat_listar_catalogos` | Status RFC, motivos 69/69-B, tipos obligación, auth methods |

## Configuración

Variables de entorno reconocidas:

| Var | Propósito |
|---|---|
| `PLUGINS_MX_MOCK=1` | Forzar modo mock (override de credenciales) |
| `SAT_RFC` | RFC del contribuyente |
| `SAT_CIEC` | Contraseña CIEC |
| `SAT_EFIRMA_CERT` | Path al archivo .cer |
| `SAT_EFIRMA_KEY` | Path al archivo .key |
| `SAT_EFIRMA_PASSWORD` | Contraseña de la e.firma |
| `PLUGINS_MX_SAT_PERMITIR_ESCRITURA=1` | (peligroso) Permitir operaciones de escritura |

Sin credenciales setadas, **todos los tools con auth corren en modo mock** y devuelven respuestas plausibles marcadas `simulated: true`.

## Modo mock vs real

```
sin credenciales         → mock siempre
con credenciales         → tools públicos: HTTP real con fallback mock
                          → tools con auth: bloquea con error (Playwright no implementado)
PLUGINS_MX_MOCK=1        → mock siempre (override)
```

Los tools públicos (`consultar_69b_efos`, `consultar_69_incumplidos`) descargan los CSVs públicos del SAT y los parsean. Si la URL del SAT cambia o no responde, automaticamente caen a mock.

## Limitaciones conocidas

1. **Portal SAT cambia con frecuencia** (3-6 meses entre cambios importantes). Selectores Playwright pueden romper sin aviso.
2. **e.firma no soportada todavía** — Playwright runner para auth no incluido. PRs bienvenidas.
3. **`sat_actualizar_obligaciones`** intencionalmente no implementada — riesgo alto de cambios accidentales en padrón SAT.
4. **Parseo HTML del verificador CFDI** usa regex tolerante. Si SAT cambia su markup, los tools devuelven `parseo_fallido: true`.
5. **URLs públicas hardcodeadas** (`omawww.sat.gob.mx/cifras_sat/...`). Verificar vigencia cada 6-12 meses.

## Casos de uso típicos

### Due-diligence cliente nuevo
1. `sat_consultar_padron(rfc)` → status ACTIVO
2. `sat_consultar_69b_efos(rfc)` → no en lista
3. `sat_consultar_69_incumplidos(rfc)` → no en lista
4. `sat_descargar_csf(rfc)` → guardar para expediente

### Validación post-timbrado
1. `sat_validar_uuid_estructura(uuid)` → válido
2. `sat_verificar_cfdi_uuid(uuid, emisor, receptor, total)` → Vigente

### Cierre fiscal mensual
1. `sat_descargar_cfdi_masivo(rfc, ejercicio, mes, "emitidos")` → solicitud
2. `sat_descargar_cfdi_masivo(rfc, ejercicio, mes, "recibidos")` → solicitud
3. (esperar 1-4 horas)
4. `sat_descargar_buzon_tributario(rfc)` → revisar pendientes

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_sat_portal/tests/ -q
```
