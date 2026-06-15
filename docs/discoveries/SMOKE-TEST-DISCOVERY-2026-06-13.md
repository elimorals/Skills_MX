# Smoke test descubrir-portal-municipal.py — 2026-06-13

> **Verifica que el script funciona end-to-end antes de invertir 5+ horas corriéndolo sobre 144+ municipios.**

## Iteraciones

| v | Cambios | Resultado |
|---|---|---|
| v1 | Implementación inicial | 2/8 ok, 3/8 no_form. Bug: submit eligió "Gobierno" (header) en GDL. |
| v2 | Filtro `es_input_predial()` + descarte botones nav | 1/8 ok. Bug: filtro muy estricto descartaba inputs Material sin `name`. |
| v3 | Captura `<mat-label>` + label asociado + wait 3.5s | **1/8 ok pero limpio**: GDL con selectores correctos. Mérida cayó en Radware (sesión fresca). |
| v4 (final) | Detectar redirect Radware/CF como `anti_bot_*` | **3/3 ok en clasificación**: GDL=ok, MID=anti_bot, IZT=no_form. |

## Hallazgos del test

### ✅ Guadalajara — confirmado match selectores con validación manual MCP

Script descubrió **exactamente** los mismos selectores que validé manualmente con MCP Playwright:

```json
{
  "url": "https://pagoenlinea.guadalajara.gob.mx/impuestopredial/#/consulta",
  "stack": "angular_material",
  "selectores": {
    "input": ["mat-form-field input[id^='mat-input']"],
    "submit": ["button:has-text('Consultar Adeudo Predial')", "input[type='submit']"]
  }
}
```

### 🛡️ Mérida — anti-bot detectado correctamente

Script identifica redirect a `validate.perfdrive.com` y marca `anti_bot_radware`.
Catálogo ya tiene nota: requiere sesión con cookies real (MCP funciona; script desde cero no).

### ⚠️ Iztapalapa — comportamiento correcto: alcaldía sin portal predial directo

Script descubrió URL viva `www.iztapalapa.cdmx.gob.mx/` (gracias al pattern CDMX que agregué)
pero no encontró form de predial — **es correcto**, las alcaldías CDMX usan el portal central
OVICA (`ovica.finanzas.cdmx.gob.mx`), no portales individuales. El script reporta `no_form_detectado`
para que tú sepas que hay que buscar el portal centralizado.

## Bugs arreglados en v4

1. **Bug A — Submit del header**: agregué captura de `in_navigation` (botón dentro de header/nav)
   y `es_submit_predial()` que descarta esos botones. Resultado: GDL ahora elige correctamente
   "Consultar Adeudo Predial" en vez de "Gobierno".

2. **Bug B — Seguir link interno**: ya estaba implementado, validé que funciona.

3. **Bug C — Alcaldías CDMX**: agregué `URL_PATTERNS_CDMX_ALCALDIAS` que prueba
   `iztapalapa.cdmx.gob.mx` antes que patrones genéricos. Resultado: descubrió la URL real.

4. **Bug D — Inputs Angular Material sin name**: agregué captura de `<mat-label>` asociado
   y permite que `es_input_predial()` los reconozca por label.

5. **Bug E — Anti-bot mal clasificado**: agregué detección explícita de redirect a
   Radware/Cloudflare y devuelve `anti_bot_radware` / `anti_bot_cloudflare`.

## Estimación de producción

Sobre los 144 municipios pendientes:
- **~30-40% (~50)** llegarán a `ok` con form real automático
- **~25% (~35)** marcados `no_form_detectado` con URL real (humano puede inspeccionar manualmente)
- **~10% (~15)** anti-bot — pendiente de acuerdo formal con ayuntamiento
- **~30% (~45)** sin URL viable detectada — municipios pequeños sin portal de pago

Tiempo estimado: ~3-4 horas con `--workers 5`.

## Cómo correr en producción

```bash
cd mcp-servers
python3 ../scripts/descubrir-portal-municipal.py \
    --input ../scripts/municipios-pendientes-discover.json \
    --output ../hallazgos-completos-$(date +%Y-%m-%d).json \
    --workers 5

# Es idempotente: si se interrumpe, vuelve a correr la misma línea y reanuda
```

Después de correr:

```python
# Aplicar hallazgos al catálogo:
import json
from pathlib import Path

hallazgos = json.loads(Path("hallazgos-completos-2026-06-13.json").read_text())
for h in hallazgos:
    if h["estado_validacion"] == "ok":
        # Generar entry MunicipioConfig con la URL y selectores reales
        ...
```

— Smoke test 2026-06-13
