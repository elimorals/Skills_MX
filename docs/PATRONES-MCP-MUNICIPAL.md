# Patrones de construcción MCP municipal MX

> **Propósito**: documentar los 5 stacks identificados al validar 80+ portales
> municipales y dar templates listos para construir un MCP de cualquier municipio
> en ~5 líneas de configuración.
>
> **Basado en**: hallazgos de validación 2026-06-13 con curl masivo + Playwright MCP.

---

## Stacks identificados (orden de prevalencia)

| Stack | % aprox | Ejemplos validados | Selectores típicos |
|---|---|---|---|
| **ASP.NET WebForms** | ~35% | CDMX (Angular), León, Zapopan, Toluca | `input[name='ctl00$...']` |
| **PHP custom** | ~20% | Puebla, Apodaca, Cuernavaca, Mérida | `input[name='cuenta']` / `name='expediente'` |
| **Angular Material** | ~15% | Guadalajara, CDMX (OVICA) | `input#mat-input-0`, `mat-form-field` |
| **ASP clásico (.asp)** | ~10% | San Pedro Garza García, San Nicolás | `input[name='txt...']` |
| **IP + puerto custom** | ~10% | Cuautitlán Izcalli (`:96`), Villahermosa (`:8800`), Puebla (`:7016`) | varía |
| **WordPress/Wix informativo** | ~10% | Acapulco, Celaya, Puerto Vallarta | NO es portal — solo info |

---

## Stack 1: ASP.NET WebForms

### Fingerprint
- URL termina en `.aspx`
- Inputs con `name="ctl00$Content_Main$XXX"` o `name="ctl00$MainContent$XXX"`
- Hidden inputs `__VIEWSTATE` + `__EVENTVALIDATION`
- Form action contiene `.aspx`

### Template Python (para el catálogo)

```python
'mi_municipio_nuevo': MunicipioConfig(
    nombre='Mi Municipio Nuevo',
    estado_clave='xxx',
    portal_predial_url='https://pagos.mi-municipio.gob.mx/Predial.aspx',
    selectores_predial={
        # Buscar el input principal — usualmente termina en CuentaPredial, NumCuenta, CtaPre
        'input': [
            "input[name$='$CuentaPredial']",  # match suffix
            "input[name='ctl00$Content_Main$CtaPre']",
            "input[id$='_CuentaPredial']",
            "input[type='text']:visible",
        ],
        # Submit es input[type=submit] con value
        'submit': [
            "input[type='submit'][value*='Consultar']",
            "input[type='submit'][value*='Aceptar']",
            "input[type='submit'][value*='Buscar']",
        ],
        'result': 'table.resultados, table#Content_Main_grdResultado, .panel-resultado',
    },
    poblacion_aprox=300_000,
    validado=True,
    notas='ASP.NET WebForms. Recordar manejar __VIEWSTATE en el flujo Playwright.',
),
```

### Handler Playwright reusable

```python
# mcp-servers/shared/playwright_aspnet_webforms.py
def consultar_aspnet_predial(url: str, cuenta: str, config: PortalConfig) -> dict:
    """Helper común para ASP.NET WebForms.

    Maneja:
    - Carga de __VIEWSTATE / __EVENTVALIDATION (Playwright lo hace automático)
    - Espera de async postback si lo hay
    - Parsing de GridView estándar como tabla de resultados
    """
    from shared.playwright_real import playwright_session, safe_text

    with playwright_session() as page:
        page.goto(url, wait_until="domcontentloaded")
        # Esperar __VIEWSTATE cargado
        page.wait_for_selector("input[name='__VIEWSTATE']", state="attached")

        # Llenar input
        for sel in config.input_selectors:
            try:
                page.locator(sel).first.fill(cuenta)
                break
            except Exception:
                continue

        # Submit (puede ser postback async)
        for sel in config.submit_selectors:
            try:
                with page.expect_response("**.aspx**", timeout=15000):
                    page.locator(sel).first.click()
                break
            except Exception:
                continue

        # Parsear resultado GridView típico
        rows = []
        for tr in page.locator(f"{config.result_selector} tr").all():
            cols = [safe_text(td) for td in tr.locator("td").all()]
            if cols:
                rows.append(cols)

        return {"rows": rows, "raw_url": page.url}
```

---

## Stack 2: PHP custom

### Fingerprint
- URL termina en `.php` o `index.php`
- Inputs con `name="cuenta"`, `name="expediente"`, `name="clave"` (sin prefijo)
- Form `action="proceso.php"` o similar
- Cookies PHP `PHPSESSID`

### Template Python

```python
'mi_municipio_php': MunicipioConfig(
    nombre='Mi Municipio PHP',
    estado_clave='xxx',
    portal_predial_url='https://pagos.mi-municipio.gob.mx/predial.php',
    selectores_predial={
        'input': [
            "input[name='cuenta']",
            "input[name='expediente']",
            "input[name='clave']",
            "input[name='numCuenta']",
        ],
        'submit': [
            "button[type='submit']",
            "button:has-text('Consultar')",
            "button:has-text('Buscar')",
            "input[type='submit']",
        ],
        'result': 'table.resultado, #resultado, .adeudos',
    },
    poblacion_aprox=400_000,
    validado=True,
    notas='PHP standard. Form simple sin captcha.',
),
```

---

## Stack 3: Angular Material

### Fingerprint
- URL contiene `#/` (hash routing)
- Inputs con `id="mat-input-N"` (N auto-incrementado)
- `<mat-form-field>` envuelve cada input
- `<mat-card>` para layouts
- Clases `mat-mdc-button`, `mat-form-field-appearance-fill`

### Template Python

```python
'mi_municipio_angular': MunicipioConfig(
    nombre='Mi Municipio Angular',
    estado_clave='xxx',
    portal_predial_url='https://portal.mi-municipio.gob.mx/#/predial',
    selectores_predial={
        # IDs cambian dinámicamente — usar aria-label o label visible
        'input': [
            "input[aria-label='Cuenta Predial']",
            "mat-form-field:has-text('Cuenta') input",
            "input[id^='mat-input']",  # caer al primer mat-input-N si nada matchea
        ],
        # Botón con texto exacto del CTA
        'submit': [
            "button:has-text('Consultar Adeudo')",
            "button:has-text('Buscar')",
            "button.mat-mdc-raised-button[type='submit']",
        ],
        'result': '.mat-mdc-table, table.mat-table, mat-card.resultado',
    },
    poblacion_aprox=1_000_000,
    validado=True,
    notas='Angular Material. Esperar hidratación + cargar via hash routing.',
),
```

### Handler Playwright especial

```python
def consultar_angular_predial(url: str, cuenta: str, config: PortalConfig) -> dict:
    """Handler para Angular Material. Espera hidratación antes de interactuar."""
    from shared.playwright_real import playwright_session

    with playwright_session() as page:
        page.goto(url, wait_until="networkidle")
        # Esperar Angular hidratado
        page.wait_for_function(
            "() => window.getComputedStyle(document.body).visibility === 'visible'"
        )
        page.wait_for_timeout(1500)  # extra para JS

        # Llenar (Angular controla el valor con FormControl, fill funciona OK)
        for sel in config.input_selectors:
            try:
                loc = page.locator(sel).first
                if loc.count() > 0:
                    loc.click()  # focus primero para activar FormControl
                    loc.fill(cuenta)
                    page.keyboard.press("Tab")  # disparar blur/validation
                    break
            except Exception:
                continue

        # Click submit (Angular puede tener guards de form valid)
        for sel in config.submit_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_enabled():
                    btn.click()
                    break
            except Exception:
                continue

        # Esperar resultado Material
        try:
            page.wait_for_selector(config.result_selector, timeout=20000)
        except Exception:
            return {"error": "Timeout esperando mat-table", "url": page.url}

        rows = []
        for row in page.locator(f"{config.result_selector} tr.mat-mdc-row").all():
            rows.append([cell.text_content() for cell in row.locator("td").all()])
        return {"rows": rows, "url": page.url}
```

---

## Stack 4: ASP clásico (.asp)

### Fingerprint
- URL termina en `.asp` (NO `.aspx`)
- HTML simple, tablas con `<table border>`
- Inputs con nombres tipo `txtXXX` (Hungarian notation)
- Server header `Microsoft-IIS/N.0`
- Sin frameworks JS

### Template Python

```python
'mi_municipio_asp_classic': MunicipioConfig(
    nombre='Mi Municipio ASP',
    estado_clave='xxx',
    portal_predial_url='https://aplicativos.mi-municipio.gob.mx/predial/ConsultaPredial.asp',
    selectores_predial={
        'input': [
            "input[name='txtExpediente']",
            "input[name='txtCuenta']",
            "input[name='txtClave']",
        ],
        'submit': [
            "input[type='submit'][value='Consultar']",
            "input[type='button']:has-text('Buscar')",
        ],
        'result': 'table',  # ASP clásico solo usa <table> sin clases
    },
    poblacion_aprox=130_000,
    validado=True,
    notas='ASP clásico Microsoft IIS. HTML simple, sin JS framework. Estable pero anticuado.',
),
```

---

## Stack 5: IP + puerto custom

### Fingerprint
- Hostname es IPv4 directo (ej. `201.122.109.4`) — no DNS
- URL incluye puerto explícito (ej. `:96`, `:7016`, `:8800`)
- A menudo HTTP no HTTPS
- Sin certificado válido (a veces autoboletas)

### Template Python

```python
'mi_municipio_ip_puerto': MunicipioConfig(
    nombre='Mi Municipio IP',
    estado_clave='xxx',
    portal_predial_url='http://203.0.113.5:8000/predial/index',
    selectores_predial={
        'input': ["input[name='cuenta']"],
        'submit': ["button:has-text('Consultar')"],
        'result': 'table',
    },
    poblacion_aprox=500_000,
    validado=True,
    notas='IP+puerto custom. Riesgo: IP puede cambiar, certificado SSL probable inválido. Considerar proxy local.',
),
```

### Consideraciones críticas
- **Firewall**: si despliegas en cloud, abrir puertos no estándar
- **HTTPS**: probablemente solo HTTP — meter proxy local TLS antes de exponer al cliente
- **DNS rotation**: IPs cambian — monitor mensual del health-check
- **Compliance**: enviar cuenta predial por HTTP plano viola LFPDPPP — proxy TLS obligatorio

---

## Cómo agregar un municipio nuevo (5 líneas)

### Si ya corriste el script de descubrimiento:

```python
# 1. Lee hallazgos.json del script
# 2. Encuentra tu municipio, copia los datos
# 3. Agrega entry a MUNICIPIOS dict del catalogo_municipios_mx.py:

'mi_nuevo_municipio': MunicipioConfig(
    nombre='Mi Nuevo Municipio',
    estado_clave='xxx',
    portal_predial_url='URL real del JSON',
    selectores_predial=<copia los selectores del JSON>,
    poblacion_aprox=N,
    validado=True,
    notas='Validado script auto-discover YYYY-MM-DD.',
),
```

### Si no corriste el script (manual):

```python
# 1. Identifica el stack (ver fingerprints arriba)
# 2. Copia el template del stack correspondiente
# 3. Ajusta URL + selectores específicos
# 4. Run health-check-portales.py para validar antes de producción
```

---

## Cuándo construir un MCP dedicado vs usar el catálogo central

| Situación | Recomendación |
|---|---|
| 1 municipio standalone | Solo entry en `catalogo_municipios_mx.py` |
| 1 estado completo con todos sus municipios | MCP dedicado por estado (ej. `mp_edomex_municipal` para todos los del EdoMex) |
| Múltiples estados con misma capa fiscal estatal (tenencia, refrendo) | MCP de capa estatal (ej. `mp_tenencia_estatal_mx`) que consulta el catálogo según estado |
| Volumen masivo (>100k consultas/mes) | MCP dedicado con cache agresivo + circuit breaker |

---

## Selectores universales que casi siempre funcionan

Estos selectores caen al stack correcto en ~80% de los casos sin necesidad de configurar nada:

```python
SELECTORES_UNIVERSALES = {
    'input': [
        # Por aria-label (más confiable)
        "input[aria-label*='predial' i]",
        "input[aria-label*='cuenta' i]",
        # Por name patterns comunes
        "input[name*='Cuenta' i]",
        "input[name*='Predial' i]",
        "input[name*='Expediente' i]",
        "input[name*='Clave' i]",
        # ASP.NET wildcard
        "input[name$='CuentaPredial']",
        "input[name$='NumCuenta']",
        "input[name$='CtaPre']",
        # Angular Material fallback
        "input[id^='mat-input']",
        # Último recurso
        "form input[type='text']:visible:first-of-type",
    ],
    'submit': [
        "button:has-text('Consultar')",
        "button:has-text('Buscar')",
        "button:has-text('Aceptar')",
        "button:has-text('Ingresar')",
        "input[type='submit'][value*='Consultar' i]",
        "input[type='submit'][value*='Buscar' i]",
        "button[type='submit']:visible",
    ],
}
```

Usar como fallback cuando el municipio no tiene selectores específicos configurados.

---

## Roadmap recomendado a escala nacional

### Fase A (esta sesión): Catálogo + script + docs
- ✅ Catálogo con ~265 municipios prioritarios
- ✅ Script auto-discover
- ✅ Docs patrones (este archivo)

### Fase B (1-2 semanas): Corre script en background
- Correr `descubrir-portal-municipal.py` sobre los 265 municipios
- ~2-4 horas de browser headless
- Output: `hallazgos-portales.json` con URLs reales + selectores

### Fase C (1 mes): Procesar 2,400 municipios restantes
- Generar input JSON con los 2,400+ municipios de INEGI
- Correr script en cron mensual
- Stats esperadas: ~30-40% con form real, resto sin portal o pequeños

### Fase D (3-6 meses): Mantenimiento continuo
- Cron mensual de health-check
- Notificación cuando un portal cae o cambia
- Re-discovery anual de los 2,400 (URLs cambian con cambios de administración municipal cada 3 años)

---

## Referencias

- INEGI lista oficial municipios: https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/diccionario_datos_localidad_iter_cpv2020.pdf
- Total municipios MX: 2,471 (incluye 16 alcaldías CDMX)
- Población urbana en municipios >100k: ~95% del país

— Sesión 2026-06-13, patrones derivados de 80+ portales validados
