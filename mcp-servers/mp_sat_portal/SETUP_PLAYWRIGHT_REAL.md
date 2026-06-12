# mp_sat_portal — activación del path Playwright real

> Spec: `docs/specs/02-sat-portal-playwright-real.md`
> Esqueleto codificado: `efirma_loader.py` + `playwright_client.py`

Este documento describe los pasos **humanos** necesarios para pasar del modo mock al path real con Playwright + e.firma. La estructura del cliente y validación de e.firma ya están codificadas. Falta solo lo que requiere intervención del operador.

## Estado del código

| Componente | Estado |
|---|---|
| `efirma_loader.py` — carga + valida .cer/.key | ✅ |
| Detección RFC + vencimiento del .cer | ✅ |
| Validación keypair (.cer ↔ .key emparejados) | ✅ |
| `playwright_client.py` — estructura cliente | ✅ |
| Detector mock/blocked/real | ✅ |
| Precheck e.firma vigente | ✅ |
| Detector de breakage de selectores (helper) | ✅ |
| Bitácora con RFC hasheado | ✅ |
| 20 tests con cert self-signed | ✅ |
| Stubs honestos de 6 tools (`_real_*` retornan flag explícito) | ✅ |
| **Browser automation real** (selectores + click + descarga) | ⏳ requiere humano |

## Pasos para activar el path real

### 1. Obtener e.firma vigente del SAT (HUMANO)

La e.firma se tramita en una oficina SAT con cita previa. Devuelve 3 cosas:
- `.cer` — certificado público
- `.key` — llave privada
- Contraseña — la define el contribuyente al tramitar

Si ya la tienes, solo necesitas los 3 archivos/datos.

### 2. Setear variables de entorno

```bash
export SAT_RFC=ABC010101AA1                       # tu RFC
export SAT_EFIRMA_CERT=/Users/tu/.efirma/cer.cer
export SAT_EFIRMA_KEY=/Users/tu/.efirma/key.key
export SAT_EFIRMA_PASSWORD='tu-password-efirma'   # ⚠ usa quotes simples si contiene $
export PLUGINS_MX_PLAYWRIGHT_REAL=1               # opt-in explícito
```

**Recomendado**: pon estas vars en `.env` y carga con `direnv` o equivalente. **NUNCA** las commitees.

### 3. Verificar la e.firma localmente (CODIFICADO, listo para correr)

```bash
cd mcp-servers
.venv/bin/python -c "
from mp_sat_portal.efirma_loader import EfirmaLoader
loader = EfirmaLoader.from_env()
print('RFC:', loader.metadata().rfc)
print('Vigencia:', loader.metadata().vigencia_hasta.date())
print('Dias para vencer:', loader.metadata().days_until_expiry)
print('Keypair válido:', loader.validate_key_pair())
"
```

Salida esperada:
```
RFC: ABC010101AA1
Vigencia: 2027-08-15
Dias para vencer: 425
Keypair válido: True
```

Si la salida es OK, la e.firma está lista para usar.

### 4. Instalar Playwright (HUMANO)

```bash
cd mcp-servers
.venv/bin/pip install -e ".[sat-playwright]"
.venv/bin/playwright install chromium
```

Esto descarga ~200MB del browser Chromium.

### 5. Implementar los `_real_*` (HUMANO — requiere portal SAT vigente)

En `playwright_client.py`, los 6 métodos `_real_descargar_csf`, `_real_descargar_buzon_tributario`, etc. son stubs que retornan mock. **Aquí es donde se implementa el scraping real**:

```python
def _real_descargar_csf(self, params: dict[str, Any]) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=self.headless)
        context = browser.new_context()
        page = context.new_page()

        # 1. Navegar al login con e.firma
        page.goto(f"{URL_PORTAL_SAT}/.../login_efirma")

        # 2. Subir .cer + .key (sus paths los tiene self.efirma)
        page.set_input_files("input[name='cert']", str(self.efirma.cert_path))
        page.set_input_files("input[name='key']",  str(self.efirma.key_path))
        page.fill("input[name='password']", self.efirma._password)
        page.click("button[type='submit']")

        # 3. Esperar load del dashboard
        page.wait_for_selector(".sat-dashboard", timeout=30_000)

        # 4. Navegar a CSF y descargar
        page.click("a[href*='constancia']")
        with page.expect_download() as dl_info:
            page.click("button.descargar-csf")
        download = dl_info.value
        pdf_path = Path("~/.local/share/plugins-mx/sat-pdfs/").expanduser()
        pdf_path.mkdir(parents=True, exist_ok=True)
        final = pdf_path / f"csf-{params['rfc']}-{datetime.now():%Y%m%d}.pdf"
        download.save_as(final)

        browser.close()

        return {
            "operation": "descargar_csf",
            "data": {
                "rfc": params["rfc"],
                "pdf_path": str(final),
                "fecha_descarga": datetime.now(timezone.utc).isoformat(),
            },
            "simulated": False,
        }
```

⚠ Los selectores arriba son **ilustrativos**. Los reales hay que extraerlos navegando el portal SAT actual con devtools.

### 6. Sesión cache (recomendado para evitar re-login cada call)

En `_dispatch`, antes de cada call real, intentar cargar cookies de `~/.cache/plugins-mx/sat_portal/session.json`. Si vigentes, omitir paso de login (5min ahorrados/call).

### 7. Mantenimiento ongoing

El portal SAT cambia cada 3-6 meses. Estrategia:
- Ejecutar `detector_breakage()` mensualmente (cron)
- Si detecta selector roto: alertar + caer a mock
- Re-extraer selectores y actualizar el código

## Costos estimados (referencia)

- Implementación inicial (6 tools): ~150-210h
- Mantenimiento mensual: ~4-8h (selectores)
- Mantenimiento anual e.firma: 1h (renovación)

Ver spec `docs/specs/02-sat-portal-playwright-real.md` para roadmap detallado.

## Seguridad

- e.firma vale acceso fiscal completo — protegerla como contraseña bancaria
- `.env` con la password NUNCA commit
- En servidores compartidos: considerar HSM o vault tipo HashiCorp Vault
- Auditar bitácora regularmente: `~/.local/share/plugins-mx/audit-log/sat_portal_pw/`
- Si la e.firma se compromete: tramita nueva en SAT (~1 semana)
