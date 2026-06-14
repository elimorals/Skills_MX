# mp_repse_stps

MCP standalone para consulta REPSE STPS (Registro Público de empresas de Subcontratación).

**Portal**: https://repse.stps.gob.mx/app/ — **reCAPTCHA v1beta1 deprecated**, automatizable 100%.

## Por qué importa

- Reforma laboral 2021 (Art. 15 LFT) obligó a TODO proveedor de servicios especializados a registrarse en REPSE.
- Si contratas a un proveedor SIN REPSE vigente, **te vuelves responsable solidario laboral y fiscal** de sus trabajadores. Esto incluye salarios caídos, finiquitos, IMSS, INFONAVIT y créditos fiscales.
- Universo afectado: **TODA empresa B2B mexicana** que terceriza nómina, IT, limpieza, seguridad, contabilidad, marketing, etc.

## Tools expuestas

| Tool | Para qué |
|------|----------|
| `repse_consultar_por_razon_social` | Búsqueda fuzzy por nombre o razón social |
| `repse_consultar_por_numero_registro` | Detalle completo de registro (vigencia, servicios) |
| `repse_verificar_proveedor` | Compliance B2B: ¿puedo contratar a este proveedor? |

## Flujo `repse_verificar_proveedor` (compliance Art. 15 LFT)

```
input: razon_social="MANPOWER CORPORATIVO"
   │
   ├─→ ¿Aparece en REPSE?
   │    NO → puede_contratar=False, advertencia "responsable solidario"
   │    SÍ → continuar
   │
   ├─→ ¿Vigencia >= hoy?
   │    NO → puede_contratar=False, advertencia "debe renovar"
   │    SÍ → puede_contratar=True
   │
   └─→ Return detalle + decision
```

## Tipos de datos REPSE

- **Número de registro**: 4-7 dígitos (ej. `669356`)
- **Folio**: número interno padrón
- **AR (Aviso de Registro)**: ej. `AR6169`
- **Vigencia**: 3 años desde la fecha de aviso de registro

## Modos

| Variable | Default | Efecto |
|----------|---------|--------|
| `PLUGINS_MX_MOCK=1` | ✅ | Datos simulados, no toca STPS |
| `MP_PLAYWRIGHT_PUBLIC=1` | — | Playwright real contra `repse.stps.gob.mx/app/` |

## Cache

30 días por consulta. El padrón cambia raramente (altas/bajas/renovaciones).

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_repse_stps/tests/ -v
```

## Selectores DOM validados Playwright MCP 2026-06-14

```python
SELECTORES_REPSE = {
    "input_razon_social": "input[placeholder*='Razón social']",
    "boton_buscar": "button:has-text('Buscar')",
    "tabla_resultados": "table tbody tr",
    "boton_seleccionar": "tr button:has-text('Seleccionar')",
    "detalle_folio_heading": "h3:has-text('REGISTRO LOCALIZADO FOLIO')",
    # más en shared/repse_stps.py
}
```
