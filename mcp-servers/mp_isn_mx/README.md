# mp_isn_mx

MCP multi-estado para **Impuesto sobre Nómina (ISN)** mexicano.

## Por qué importa

- ISN es obligación estatal para **TODA empresa formal MX con al menos 1 trabajador**.
- Universo: **~4 millones de empresas** (vs ~700k municipios consultables con `mp_predial_mx`). Mayor universo de cualquier MCP del monorepo.
- 32 entidades federativas, cada una con su propio portal y tasa (1.8% BC → 3% CDMX/JAL/EdoMex).
- Vencimiento: día 10-17 del mes siguiente, según estado.

## Cobertura

| Estado | Tasa | Portal | Validado |
|--------|------|--------|----------|
| CDMX | 3.0% | dgtc.finanzas.cdmx.gob.mx | ✅ |
| Jalisco | 3.0% | gobiernoenlinea1.jalisco.gob.mx | ✅ |
| Nuevo León | 3.0% | egobierno.nl.gob.mx | ✅ |
| EdoMex | 3.0% | sfpya.edomexico.gob.mx | ✅ |
| Querétaro | 3.0% | asistenciaspf.queretaro.gob.mx | ✅ |
| Puebla | 3.0% | haciendapuebla.gob.mx | ⚠ captcha |
| Guanajuato | 2.0% | guanajuato.gob.mx/finanzas | ✅ |
| Yucatán | 2.5% | sefinyucatan.gob.mx | ✅ |
| Baja California | 1.8-3.0% | www4.ebajacalifornia.gob.mx | ✅ |
| ...(24 estados más con catálogo básico) | | | — |

Total: **32 estados en catálogo**, **8 validados** Playwright MCP.

## Tools expuestas

| Tool | Para qué |
|------|----------|
| `isn_calcular` | Cálculo offline desde catálogo (no toca portal) |
| `isn_listar_estados` | Lista del catálogo completo |
| `isn_info_estado` | Detalle de un estado (URL, tasa, selectores DOM) |
| `isn_generar_linea_captura` | Línea de captura para pago referenciado |
| `isn_descargar_declaracion` | PDF de declaración desde bóveda estatal |

## Ejemplo de uso

```python
# Calcular cuánto debe pagar empresa CDMX con $100k de nómina
calc = isn_calcular(nomina_gravable=100_000, estado="CDMX")
# → {"isn_a_pagar": 3000, "tasa_pct": 3.0, "vencimiento_dia": 17}

# Línea de captura para mayo 2026
linea = isn_generar_linea_captura(
    estado="CDMX", periodo="2026-05",
    rfc="ABC120101AB1", nomina_gravable=100_000,
)
# → {"linea_captura": "...", "monto_a_pagar": 3000, "portal_pago": "..."}
```

## Modos

| Variable | Default | Efecto |
|----------|---------|--------|
| `PLUGINS_MX_MOCK=1` | ✅ | Datos simulados |
| `MP_PLAYWRIGHT_PUBLIC=1` | — | Playwright real (requiere credenciales por estado) |

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_isn_mx/tests/ -v
```
