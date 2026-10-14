# mp_sat_portal — MCP para portal SAT (México)

Herramientas para verificación, descarga y consulta contra los portales del Servicio de Administración Tributaria (SAT) de México.

## Estado real (2026-10-14)

Login con e.firma **por HTTP puro** (`shared/sat_portal_fiel.py`, httpx), port
mínimo del módulo `portal` de [satcfdi](https://pypi.org/project/satcfdi/) (MIT,
v26.8.0). No se usa satcfdi como dependencia: va sobre `requests` (no se prueba
con respx) y arrastra weasyprint, lxml y pyOpenSSL. Playwright ya no es el path
real (`playwright_client.py` queda como legado y nunca devuelve mock con
credenciales). Los hosts `*.siat.sat.gob.mx` negocian DH de 1024 bits: se
excluyen suites DH (igual que satcfdi), si no, `DH_KEY_TOO_SMALL`.

| Tool | Estado | Validación en vivo |
|---|---|---|
| `sat_verificar_efirma_vigente` | **Real.** Local: .cer (RFC, no. de certificado, vigencia) + .key abre y corresponde. Portal: login FIEL; detecta "Certificado Revocado/Caduco". | Handshake FIEL completo contra `loginda.siat.sat.gob.mx` con un certificado autofirmado (2026-10-14): el SAT respondió el rechazo `"El certificado no se encuentra disponible o no fue posible validarlo"` y el cliente lo detectó. **Falta** el caso aceptado (e.firma real). |
| `sat_descargar_csf` | **Real, sin validar con e.firma.** Flujo `login.siat` → SAML → `rfcampc.siat` (JSF) → PDF. Guarda el PDF (600) y devuelve ruta + sha256; no extrae datos del PDF (oleada 3). | Entradas `login.siat.sat.gob.mx/nidp/idff/sso?id=fiel_Aviso` (200) y `rfcampc.siat.sat.gob.mx` (302 al NIDP) vivas 2026-10-14. |
| `sat_consultar_padron` | **Real con e.firma propia, sin validar.** Login FIEL a `portal.facturaelectronica.sat.gob.mx` → `Clientes/ExisteLrfc` + `Clientes/ValidaLco`. Sin e.firma: error con `handoff_url` a ValidaRFC (tiene CAPTCHA, no se automatiza). | Cadena WS-Fed hasta el reto `certform` en `cfdiau.sat.gob.mx` viva 2026-10-14. ValidaRFC 200 con CAPTCHA. |
| `sat_consultar_69b_efos` | **Real** por default (sin mock salvo `PLUGINS_MX_MOCK=1`). Falla → `UpstreamError`. | 2026-10-14: `Documents_AGAFF/Definitivos.csv` 200 (3.8 MB, mod. 2026-09-15), `Presuntos.csv` 200; 12,742 registros parseados. |
| `sat_consultar_69_incumplidos` | **Real** por default (solo `Firmes.csv`). Falla → `UpstreamError`. | 2026-10-14: `Documents_AGR/Firmes.csv` 200 (20 MB, mod. 2026-10-08); 264,240 registros. |
| `sat_descargar_buzon_tributario` | **No implementado.** Con credenciales → `UpstreamError` con `handoff_url`. | — |
| `sat_descargar_acuse` | **No implementado.** Igual que buzón. | — |
| `sat_actualizar_obligaciones`, `sat_agendar_cita` | **No se automatizan** (escritura). Sin cambios. | — |

Prueba live con e.firma (la corre el coordinador; nunca con la e.firma en el repo):

```bash
cd mcp-servers && uv pip install -e ".[dev,sat-portal]"
PLUGINS_MX_LIVE=1 SAT_RFC=<RFC> SAT_EFIRMA_CERT=<ruta.cer> SAT_EFIRMA_KEY=<ruta.key> \
  SAT_EFIRMA_PASSWORD=<pwd> .venv/bin/pytest -q -m live \
  mp_sat_portal/tests/test_efirma_real.py mp_sat_opinion_32d/tests/test_real.py
```

## Tools (11)

### Públicos — HTTP real (sin fallback a mock en 69/69-B)

| Tool | Propósito | Auth |
|---|---|---|
| `sat_consultar_padron` | ¿RFC en la LCO? + datos LCO | e.firma propia (sin ella: handoff CAPTCHA) |
| `sat_consultar_69b_efos` | Lista 69-B EFOS (definitivos + presuntos) | Pública (CSV) |
| `sat_consultar_69_incumplidos` | Lista 69 incumplidos Art. 69 CFF | Pública (CSV) |
| `sat_verificar_cfdi_uuid` | Status CFDI contra verificador SAT | Pública (HTML) |

### Local — sin red

| Tool | Propósito |
|---|---|
| `sat_validar_uuid_estructura` | Validar formato UUID CFDI (8-4-4-4-12 hex, v4) |

### Con autenticación — mock solo sin credenciales

Path real: login e.firma por httpx (ver "Estado real"). Buzón y acuses aún no tienen path real: con credenciales devuelven error explícito.

| Tool | Propósito | Auth |
|---|---|---|
| `sat_descargar_csf` | Constancia de Situación Fiscal (PDF) | e.firma |
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
listas 69 / 69-B         → HTTP real siempre; si falla, UpstreamError
sin credenciales SAT     → tools con auth en mock (simulated: true)
con e.firma (SAT_EFIRMA_*) → CSF, padrón, vigencia: login FIEL real
con credenciales sin path real (buzón, acuse) → error explícito con handoff
PLUGINS_MX_MOCK=1        → mock siempre (override)
```

## Limitaciones conocidas

1. **Portal SAT cambia con frecuencia.** El login FIEL por httpx depende del NIDP del SAT (`certform` + `guid`); si cambia, el error dice en qué paso (`details.paso`).
2. **CSF y padrón con e.firma no validados todavía con una e.firma real** (ver "Estado real").
3. **`sat_actualizar_obligaciones`** intencionalmente no implementada — riesgo alto de cambios accidentales en padrón SAT.
4. **Parseo HTML del verificador CFDI** usa regex tolerante. Si SAT cambia su markup, los tools devuelven `parseo_fallido: true`.
5. **URLs públicas hardcodeadas** (Azure Blob `wu1agsprosta001.blob.core.windows.net`). Verificadas 2026-10-14.

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
