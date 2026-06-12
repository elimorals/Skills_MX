# mp_bancos_mx — activación del path Playwright real

> Spec: `docs/specs/03-bancos-mx-playwright-real.md`
> Esqueleto codificado: `playwright_drivers/`

## Estado del código

| Componente | Estado |
|---|---|
| Base class `BancoPlaywrightDriver` | ✅ |
| Driver `BbvaDriver` (estructura) | ✅ |
| Driver `BanamexDriver` (estructura) | ✅ |
| Driver `SantanderDriver` (estructura) | ✅ |
| Driver `BanorteDriver` (estructura + TOTP helper) | ✅ |
| Schema `Movimiento` común a los 4 bancos | ✅ |
| Tests (12) con mock | ✅ |
| `_real_login()` real (login flow) | ⏳ requiere humano |
| `_real_listar_movimientos()` (scraping tabla) | ⏳ requiere humano |
| `_real_descargar_estado_cuenta()` (descarga CSV/PDF) | ⏳ requiere humano |
| Session cache | ⏳ requiere humano |

## Pasos para activar uno de los 4 bancos

### 1. Setear credenciales (HUMANO)

```bash
# Ejemplo BBVA:
export BBVA_USUARIO=mi-usuario
export BBVA_PASSWORD='mi-password'
export PLUGINS_MX_PLAYWRIGHT_REAL=1

# Banamex:
export BANAMEX_USUARIO=...
export BANAMEX_PASSWORD=...
export BANAMEX_TOKEN_TYPE=fisico   # o "challenge"

# Banorte (TOTP opcional para evitar 2FA SMS):
export BANORTE_USUARIO=...
export BANORTE_PASSWORD=...
export BANORTE_SOFT_TOKEN_SEED=BASE32SEED...  # de la app autenticadora
```

⚠ **NUNCA** commitear `.env` con credenciales bancarias.

### 2. Instalar Playwright

```bash
cd mcp-servers
.venv/bin/pip install -e ".[sat-playwright]"   # mismo extra; incluye playwright
.venv/bin/playwright install chromium
.venv/bin/pip install pyotp  # opcional, solo Banorte con soft token
```

### 3. Implementar `_real_login()` por banco (HUMANO)

Cada banco tiene flujo de login distinto. Plantilla BBVA:

```python
# En playwright_drivers/bbva.py
def _real_login(self) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)  # headed para 2FA
        context = browser.new_context()
        self._page = context.new_page()
        self._page.goto(self.PORTAL_URL)

        # Selectores específicos BBVA (validar contra portal vigente):
        self._page.click("a[href*='banca-en-linea']")
        self._page.fill("input[name='userId']", self.config.usuario)
        self._page.fill("input[name='password']", self.config.password)
        self._page.click("button[type='submit']")

        # 2FA: usuario aprueba en app BBVA (espera asistida)
        try:
            self._page.wait_for_selector(".dashboard-container", timeout=90_000)
        except Exception:
            raise SesionExpiradaError("2FA no completado en 90s — reintentar")

        # Guardar cookies para reutilizar
        self._sesion_iniciada_en = datetime.now(timezone.utc)
        self._storage_state = context.storage_state()
```

### 4. Implementar `_real_listar_movimientos()` (HUMANO)

```python
def _real_listar_movimientos(self, params: dict[str, Any]) -> dict[str, Any]:
    if self._page is None:
        self._real_login()

    # Navegar a movimientos de la cuenta
    self._page.click(f"button[data-cuenta='{params['cuenta']}']")
    self._page.wait_for_selector("table.movimientos")

    movs = []
    for row in self._page.locator("table.movimientos tr").all():
        fecha_text = row.locator("td.fecha").inner_text()
        monto_text = row.locator("td.monto").inner_text()
        # ... parsing específico
        movs.append(Movimiento(...).to_dict())

    return {
        "operation": "listar_movimientos",
        "banco": self.BANCO_CODIGO,
        "data": {"cuenta_hash": Bitacora.hash_sensitive(params['cuenta']), "movimientos": movs, "total": len(movs)},
        "simulated": False,
    }
```

### 5. Detector breakage mensual (recomendado)

Crear cron que ejecute `_real_login` semanal en modo headless y alerte si falla.

## Recomendación de orden

1. **BBVA** primero (mayor share PyME MX, ~30%)
2. **Banamex** (token físico complica)
3. **Santander** (biométrico)
4. **Banorte** (TOTP simplifica si seed disponible)

Esfuerzo estimado: 60-100h por banco (ver spec).

## Mantenimiento ongoing

- ~4-8h por banco por mes (cambios de portal)
- Renovación token Banamex físico: cada 3-5 años
- Cambio password BBVA: cada 6 meses (política banco)
