# mp_isn_mx

MCP multi-estado para **Impuesto sobre Nómina (ISN)** mexicano.

## Por qué importa

- ISN es obligación estatal para **TODA empresa formal MX con al menos 1 trabajador**.
- Universo: **~4 millones de empresas** (vs ~700k municipios consultables con `mp_predial_mx`). Mayor universo de cualquier MCP del monorepo.
- 32 entidades federativas, cada una con su propio portal y tasa (2.5% AGS → 4.25% BC; CDMX 4%).
- Vencimiento: día 10-17 del mes siguiente, según estado.

## Cobertura (tasas 2026)

| Estado | Tasa 2026 | Fuente |
|--------|-----------|--------|
| CDMX | 4.0% | Código Fiscal CDMX art. 158 (reforma 27-dic-2024) |
| Chihuahua | 4.0% | Guía oficial de pago ISN 2026 |
| Quintana Roo | 4.0% | BHR 2026 |
| Baja California | 4.25% única | Ley de Hacienda BC art. 151-16 |
| Yucatán | 3.75% | BHR 2026 |
| Zacatecas | 3.5% | BHR 2026 |
| Aguascalientes | 2.5% | BHR 2026 |
| Sinaloa | 2.4%–3.0% progresiva | no calculable: tramos 2026 no verificados |
| Tabasco | 3% o 3.5% | no calculable: criterio no verificado |
| Resto (23) | 3.0% | BHR 2026 |

Fuente base: https://www.bhrmx.com/wp-content/uploads/2026/01/CONTRIBUCIONES-LOCALES-CAMBIOS-RELEVANTES-2026-2.pdf
(confianza media; no se abrió el texto legal primario de cada estado).

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
# → {"isn_a_pagar": 4000, "tasa_pct": 4.0, "fuente_tasa": "Código Fiscal CDMX art. 158; ..."}

# Línea de captura: requiere sesión del contribuyente → config_error
# (con PLUGINS_MX_MOCK=1 devuelve una línea simulada).
```

## Modos

| Variable | Efecto |
|----------|--------|
| (ninguna) | `isn_calcular` real; línea de captura y declaración → `config_error` (requieren login, grupo G) |
| `PLUGINS_MX_MOCK=1` | Línea de captura y declaración simuladas (`simulated: true`) |

## Estado real (2026-10-14)

Cálculo local; no consulta portales. Tasas 2026 verificadas contra fuente
secundaria (tabla anterior). Cambios frente al catálogo previo: CDMX 3→4%,
BC 1.8%+sobretasas→4.25%, CHIH 3→4%, QROO 3→4%, YUC 2.5→3.75%, ZAC 3→3.5%,
y AGS, BCS, CAMP, CHIS, COAH, COL, DGO, GTO, GRO, MOR, NAY, SLP, SON a 3%.

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_isn_mx/tests/ -v
```
